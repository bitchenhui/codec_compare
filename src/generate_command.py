# -*- coding: utf-8 -*-
# This file generates command according to configurations
# ================================================================
import os
import platform

class cmd_generator():
  """Command generator class.

  This generator can read the encoder params and test configurations,
  and generate test commands according to different test needs.
  """
  def __init__(self, params, test_conf):
    self._command_list = []
    self._run_seqs = []

    # Set params
    self._out_path = params['out_path']
    self._seq_path = params['seq_path']
    self._exe_path = params['exe_folder']
    self._seqs = params['seq']
    self._enc = params['enc']
    self._dec = params["dec"]
    self._ffmpeg = params["ffmpeg"]
    self._vmaf_exe = params["vmaf"]
    self._gops = params['gop']
    self._rcs = params['rc']
    self._eval_qps = params['qps']
    self._extended_cmds = params['ext']
    self._enc_template_cmd = params['enc_cmd']
    self._dec_template_cmd = params['dec_cmd']
    self._run_classes = params['run_seq']

    # Set test config
    self._codec = test_conf['codec']
    self._rc_conf = test_conf['rc_conf']
    self._gop_conf = test_conf['gop_conf']
    self._extend_params_conf = test_conf['extend_params']
    self._test_type = test_conf["test_type"]
    self._sde_priority = test_conf["sde_priority"]
    self._consist_level = test_conf["consistency_level"]
    self._ssim = test_conf["ssim"]
    self._vmaf = test_conf["vmaf"]
    self._desc = test_conf["desc"]

  def generate_template_commands(self):
    """ Generate encoder command list according to needs. """
    # Parse tested seqs info
    for seq in self._seqs:
      if seq['class'] in self._run_classes:
        seq_name = os.path.join(self._seq_path, seq['sub_path'], seq['seq_name'] + ".yuv")
        if not os.path.exists(seq_name):
          print(seq_name + " not exist")
          sys.exit(1)
        self._run_seqs.append(seq)

    # Determine the number of tasks by gop and rate-control method
    # to be tested, and generate corresponding command for each task.
    # The results will be written into a log file
    self._enc_template_cmd = self._enc_template_cmd.replace('{encoder}', self._enc)
    for ext_opt in self._extend_params_conf:
      cur_extended_command = self._extended_cmds[ext_opt]
      conf_name = str(cur_extended_command['name'])

      # For each gop and rc-mode
      for gop_opt in self._gop_conf:
        for rc_opt in self._rc_conf:
          command_dict = {}
          out_name_list = []
          cmd_list = []
          class_list = []
          cur_gop = self._gops[gop_opt]
          cur_rc = self._rcs[rc_opt]

          # Set bitstream filepath and log file
          gop_name = str(cur_gop['gop_type'])
          rc_mode = str(cur_rc['mode'])
          if self._desc != None:
            sub_path = os.path.join(self._out_path, self._desc, conf_name, gop_name + '_' + rc_mode)
          else:
            sub_path = os.path.join(self._out_path, self._codec, conf_name, gop_name + '_' + rc_mode)
          if not os.path.exists(sub_path):
            os.makedirs(sub_path)
            print("mkdir: {}".format(sub_path))

          for seq in self._run_seqs:
            cmd = self._enc_template_cmd
            seq_name = os.path.join(self._seq_path, seq['sub_path'], seq['seq_name'])

            # Write seq info into command
            cmd = cmd.replace('{seq_name}', seq_name)
            cmd = cmd.replace('{seq_ext}',  str(seq['seq_ext']))
            cmd = cmd.replace('{wdt}', str(seq['wdt']))
            cmd = cmd.replace('{hgt}', str(seq['hgt']))
            cmd = cmd.replace('{fps}', str(seq['fps']))
            cmd = cmd.replace('{frm}', str(seq['frm']))
            cmd = cmd.replace('{csp}', str(seq['csp']))

            # Complete gop and additional params
            cmd += str(cur_gop['params'])
            cmd += str(cur_extended_command['params'])

            # Complete command according to rate-control method
            cmd += str(cur_rc['params'])
            eval_points = seq['bitrate']
            if  rc_mode == 'cqp':
              eval_points = self._eval_qps

            for eval_point in eval_points:
              # Set output file and recon file if needed
              out_name = '_'.join([seq['seq_name'], rc_mode, gop_name, str(eval_point)])
              bs_name = out_name + '.bin'
              bs_path = os.path.join(sub_path, bs_name)
              cmd_final = cmd.replace('{output_name}', bs_path)

              # Set qp point or bitrate point
              if rc_mode == 'cqp':
                cmd_final = cmd_final.replace('{q}', str(eval_point))
              elif rc_mode == 'abr':
                cmd_final = cmd_final.replace('{b}', str(eval_point))
                cmd_final = cmd_final.replace('{maxb}', str(eval_point * 3 / 2))
              else:
                cmd_final = cmd_final.replace('{b}', str(eval_point))
                cmd_final = cmd_final.replace('{0.3b}', str(eval_point * 3 / 10))

              out_name_list.append(out_name)
              cmd_list.append(cmd_final)
              class_list.append(seq['class'])

          command_dict['config'] = rc_mode + '_' + gop_name.replace("xcast_", "")
          command_dict['sub_path'] = sub_path
          command_dict['out_name_list'] = out_name_list
          command_dict['cmd_list'] = cmd_list
          command_dict['class_list'] = class_list
          self._command_list.append(command_dict)

  def get_bdrate_test_commands(self):
    """ Generate commands for encoder's quality evaluation

    Return:
      command_list: list, consist of several dict representing various configs.
    """
    self.generate_template_commands()

    # Customize command
    for cmd_dict in self._command_list:
      sub_path = cmd_dict["sub_path"]
      eval_point_num = len(cmd_dict["cmd_list"]) / len(self._run_seqs)
      for i in range(len(cmd_dict["cmd_list"])):
        out_name = cmd_dict["out_name_list"][i]
        seq = self._run_seqs[int(i / eval_point_num)]
        seq_name = os.path.join(self._seq_path, seq['sub_path'], seq['seq_name'])
        bs_path = os.path.join(sub_path, out_name + ".bin")
        dec_yuv = os.path.join(sub_path, "Dec_" + out_name + seq['seq_ext'])
        ref_yuv = seq_name + seq['seq_ext']

        if self._ssim == True or self._vmaf == True:
          # Generate decoding command
          dec_cmd = self._dec_template_cmd
          dec_cmd = dec_cmd.replace('{decoder}', self._dec)
          dec_cmd = dec_cmd.replace('{output_name}', bs_path)
          dec_cmd = dec_cmd.replace('{dec_name}', dec_yuv)
          dec_cmd = dec_cmd.replace('{csp}', str(seq['csp']))
          cmd_dict["cmd_list"][i] += " && "
          cmd_dict["cmd_list"][i] += dec_cmd
        
        if self._ssim == True:          
          # Generate command for psnr/ssim calculation
          pix_fmt = "yuv420p" if seq['csp'] == 1 else "yuv444p"
          psnr_ssim_cmd = '{ffmpeg} -s {wdt}x{hgt} -r 1 -ss 0 -t {frms} -pix_fmt {fmt} -i {dec} -s {wdt}x{hgt} -r 1 -ss 0 -t {frms} -pix_fmt {fmt} -i {ref}.yuv -lavfi "ssim={ssim_log};[0:v][1:v]psnr={psnr_log}" -f null -'.format(
                ffmpeg=self._ffmpeg,
                wdt=seq['wdt'],
                hgt=seq['hgt'],
                frms=seq['frm'],
                dec=dec_yuv,
                ref=seq_name, 
                fmt=pix_fmt,
                ssim_log="score_ssim",
                psnr_log="score_psnr")

          cmd_dict["cmd_list"][i] += " && "
          cmd_dict["cmd_list"][i] += psnr_ssim_cmd

        if self._vmaf == True:
        # Generate command for vmaf calculation
          if platform.system() == 'Windows':
            model_path = os.path.join(self._exe_path, "vmaf_v0.6.1.pkl")
            vmaf_cmd = '{vmaf} {fmt} {wdt} {hgt} {ref}.yuv {dis} {model}'.format(
                  vmaf=self._vmaf_exe,
                  ref=seq_name,
                  dis=dec_yuv,
                  wdt=seq['wdt'],
                  hgt=seq['hgt'],
                  fmt=pix_fmt,
                  model=model_path)
          else:
            pix_fmt = "420" if seq['csp'] == 1 else "444"
            vmaf_cmd = '{vmaf} -r {ref}.yuv -d {dis} -w {wdt} -h {hgt} -p {fmt} -b 8'.format(
                  vmaf=self._vmaf_exe,
                  ref=seq_name,
                  dis=dec_yuv,
                  wdt=seq['wdt'],
                  hgt=seq['hgt'],
                  fmt=pix_fmt)
          cmd_dict["cmd_list"][i] += " && "
          cmd_dict["cmd_list"][i] += vmaf_cmd

    return self._command_list 

  def get_consistency_test_commands(self):
    """ Generate commands for consistency evaluation

    Return:
      command_list: list, consist of several dict representing various configs.
    """
    self.generate_template_commands()

    # Customize command
    for cmd_dict in self._command_list:
      sub_path = cmd_dict["sub_path"]
      eval_point_num = len(cmd_dict["cmd_list"]) / len(self._run_seqs)
      for idx in range(len(cmd_dict["cmd_list"])):
        seq = self._run_seqs[int(idx / eval_point_num)]
        out_name = cmd_dict["out_name_list"][idx]
        class_name = cmd_dict["class_list"][idx]

        bs_path = os.path.join(sub_path, out_name + ".bin")
        rec_yuv = os.path.join(sub_path, "Rec_" + out_name + ".yuv")
        dec_yuv = os.path.join(sub_path, "Dec_" + out_name + ".yuv")

        # Complete encoding command to generate rec yuv
        cmd_dict["cmd_list"][idx] += "-enrec 1 -drec 0 " + rec_yuv

        # Generate decoding command
        dec_cmd = self._dec_template_cmd
        dec_cmd = dec_cmd.replace('{decoder}', self._dec)
        dec_cmd = dec_cmd.replace('{output_name}', bs_path)
        dec_cmd = dec_cmd.replace('{dec_name}', dec_yuv)
        dec_cmd = dec_cmd.replace('{csp}', str(seq['csp']))
        cmd_dict["cmd_list"][idx] += " && "
        cmd_dict["cmd_list"][idx] += dec_cmd

    return self._command_list

  def get_sde_test_commands(self):
    """ Generate commands for assembly stability

    Return:
      command_list: list, consist of several dict representing various configs.
    """
    sde_p0_archs = ["p4", "wsm", "snb", "bdw", "skl", "icl"]
    sde_p1_archs = ["p4", "p4p", "mrm", "pnr", "nhm", "wsm", "snb", "ivb", "hsw", "bdw", "skl", "cnl", "skx"]
    sde_p2_archs = ["p4", "p4p", "mrm", "pnr", "nhm", "wsm", "snb", "ivb", "hsw", "bdw", "slt", "slm", "glm",
                    "glp", "tnt", "snr", "skl", "cnl", "icl", "skx", "clx", "cpx", "icx", "knl", "knm", "tgl",
                    "adl", "spr", "future"]
    self.generate_template_commands()
    
    # Customize command
    sde_exe = os.path.join(self._exe_path, "sde", "sde.exe")
    sde_exe = self._ffmpeg
    for cmd_dict in self._command_list:
      sde_cmds = []
      sde_outnames = []
      sde_classes = []
      eval_point_num = len(cmd_dict["cmd_list"]) / len(self._run_seqs)
      for i in range(len(cmd_dict["cmd_list"])):
        seq = self._run_seqs[int(i / eval_point_num)]
        out_name = cmd_dict["out_name_list"][i]
        bin_name = out_name + ".bin"
        quark_outname = out_name + "_quark"

        # Must run on quark
        quark_cmd = "{} -quark -- {}".format(sde_exe, cmd_dict["cmd_list"][i])
        quark_cmd = quark_cmd.replace(bin_name, quark_outname + ".bin")
        sde_cmds.append(quark_cmd)
        sde_outnames.append(quark_outname)
        sde_classes.append(seq["class"])
        
        # Run specific sde priority test set
        sde_archs = sde_p0_archs
        if self._sde_priority == "1":
          sde_archs = sde_p1_archs
        elif self._sde_priority == "2":
          sde_archs = sde_p2_archs
        for sde_arch in sde_archs:
          sde_arch_outname = out_name + "_" + sde_arch
          sde_arch_cmd = "{} -{} --{}".format(
            sde_exe,
            sde_arch,
            cmd_dict["cmd_list"][i]
          )
          sde_arch_cmd = sde_arch_cmd.replace(bin_name, sde_arch_outname + ".bin")
          sde_cmds.append(sde_arch_cmd)
          sde_outnames.append(sde_arch_outname)
          sde_classes.append(seq["class"])
      cmd_dict["cmd_list"] = sde_cmds
      cmd_dict["class_list"] = sde_classes
      cmd_dict["out_name_list"] = sde_outnames
    
    return self._command_list
  
  def get_API_test_commands(self):
    """ Generate commands for API stability evaluation

    Return:
      command_list: list, consist of several dict representing various configs.
    """
    self.generate_template_commands()

    # Customize command
    for cmd_dict in self._command_list:
      eval_point_num = len(cmd_dict["cmd_list"]) / len(self._run_seqs)
      for i in range(len(cmd_dict["cmd_list"]) - 1, -1, -1):
        if i % eval_point_num == eval_point_num - 2:
          if self._codec == "h265":
            cmd_dict["cmd_list"][i] += "-testtype 2 -resloops 3 "
          elif self._codec == "h264":
            cmd_dict["cmd_list"][i] += "-testtype 2 -resloop 3 "
        else:
          cmd_dict["cmd_list"].pop(i)

    return self._command_list
