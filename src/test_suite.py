# This test project is for various encoder's compression efficiency,
# coding time performance as well as consistency evaluation
# H264/x264/H265/x265/t265 are supported now
# ================================================================
"""
Example usage:
  python test_suite.py scene [optional:codecname] [optional:config.json] [optional:encoder_exe_name]
"""

import os
import sys
import json
import platform
import filecmp
import hashlib

from util.extract_log_info import *
from util.generate_command import *
from util.execute_command import *
from util.log import Log
from util.qci import QCI

prj_path='/Users/chenhuiduan/Documents/ppcodec/O264rt'

def call_help():
  """Print help information"""
  
  print(
        "python test_suite.py --scene=<scene_type> [optional] \n\n" +
        "Required input includes: \n" +
        "--scene=<scene> : [camera, desktop] : default camera\n" +
        "Optional input includes: \n" +
        "--codec=<codecname> : : default value h265\n" +
        "--config=<config_path> : : default value config.json\n"+
        "--enc=<encoder_exe_name> : : default value None\n"+
        "--test-type=<test_type> : [0-3] 0-bdrate, 1-consistency, 2-sde, 3-API : default value 0\n"+
        "--ssim=<ssim> : [0-1] 0-disable, 1-enable : default value 0\n" +
        "--vmaf=<vmaf> : [0-1] 0-disable, 1-enable : default value 1\n" +
        "--consistency-level=<consis_level> : [0-2] : default value 0\n"+
        "--sde-priority=<sde_priority> : [0-2] : default value 0\n"+
        "--gaia-path=<gaia_config_path> : : default value None\n\n"+
        "Example usage:\n"+
        "python test_suite.py camera --codec=h265 --config=config-h265.json --enc=TcHevcEncTest --test-type=0\n"
    )

def parse_options(args):
  """Parse input options and initialize the basic information of test suite

  Arg:
    args: list

  Return:
    params: dict, contain settings of scene, config, codec, encoder, sde test level, consistency
      test level and default prefix of path.
  """
  if "--help" in args:
    call_help()
    exit(1)
  
  if len(args) < 2:
    print("Invalid input parameters!!")
    call_help()
    exit(1)
  
  params = {
    "scene" : None,
    "codec" : "h264",
    "config" : "config.json",
    "enc" : None,
    "test-type" : "0",
    "ssim" : "1",
    "vmaf" : "0",
    "consistency-level" : "0",
    "sde-priority" : "0",
    "gaia-path" : None
    }

  # Parse options and set into params dict
  for arg in args[1:]:
    key_value = arg.split("=")

    if len(key_value) != 2:
      print("wrong setting parameter form: {}!!".format(arg))
      exit(1)
    
    key = key_value[0].replace("--", "")
    val = key_value[1]
    if key not in params.keys():
      print("wrong input param: {}!!".format(key))
      exit(1)
    
    params[key] = val
  
  # Validate required params
  if params["scene"] == None:
    print("Must set scene type!!")
    call_help()
    exit(1)

  # Validate platform for SDE test
  if params["test-type"] == "2":
    if platform.system() != "Windows":
      print("SDE test does not support on Mac/Linux!!")
      exit(1)

  return params


def load_json(input_json, scene, encoder_exe, configuration, prefix_path, ssim=False, vmaf=False):
  """Load input json file and extract platform info

  Arg:
    input_json: an opened json file, with encoding param sets and
    current test options

  Return:
    params: a dict, containing task's basic information
  """
  input_dicts = json.load(input_json)
  params = dict()
  
  # Extract params depended on system
  cur_sys = platform.system()
  cur_folder = prj_path
  info_sys = input_dicts['env_conf']
  if cur_sys == 'Windows':
    params["exe_folder"] = os.path.join(str(cur_folder), "output", "win")
    if encoder_exe != None:
      info_sys['encoder'] = encoder_exe
    info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'] + ".exe")
    info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "win",  info_sys['decoder'] + ".exe")
    info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'] + ".exe")
    info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'] + ".exe")   
  elif cur_sys == 'Darwin':
    params["exe_folder"] = os.path.join(str(cur_folder), "output", "mac")
    if encoder_exe != None:
      info_sys['encoder'] = encoder_exe
    info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'])
    info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "mac",  info_sys['decoder'])
    info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'])
    info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'])
  elif cur_sys == 'Linux':
    params["exe_folder"] = os.path.join(str(cur_folder), "output", "linux")
    if encoder_exe != None:
      info_sys['encoder'] = encoder_exe
    info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'])
    info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "linux", info_sys['decoder'])
    info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'])
    info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'])
  if info_sys == None:
    print("Invalid platform")
    exit(1)

  params['enc'] = info_sys['encoder']
  params['dec'] = info_sys['decoder']
  params['ffmpeg'] = info_sys['ffmpeg']
  params['vmaf'] = info_sys['vmaf']
  # load other info
  params['gop'] = input_dicts['gop_param_set']
  params['rc'] = input_dicts['rc_param_set']
  params['ext'] = input_dicts['additional_param_set']
  params['enc_cmd'] = input_dicts['encode_task_template']
  params['dec_cmd'] = input_dicts['decode_task_template']
  params['opt'] = input_dicts[scene + '_test_option']
  params['qps'] = input_dicts['eval_qp_set']

  if configuration != None:
    params['opt'] = configuration

  seq_json = os.path.join(str(cur_folder), "qci_test", info_sys['seq_json'])
  print(seq_json)
  with open(seq_json, 'r') as seqs_json_file:
    seq_dict = json.load(seqs_json_file)
    if cur_sys == 'Windows':
      seq_info_sys = seq_dict['win']
    elif cur_sys == 'Darwin':
      seq_info_sys = seq_dict['mac']
    elif cur_sys == 'Linux':
      seq_info_sys = seq_dict['linux']
    if seq_info_sys == None:
      print("Invalid platform")
      exit(1)
    params['out_path'] = os.path.join(prj_path, "encode_test_res")
    params['seq_path'] = os.path.join(prj_path, "sequence")
    params['seq'] = seq_dict[scene + '_seqs_info']
    params['run_seq'] = seq_dict[scene + '_run_seq']

  # Detect if the encoder or decoder is existed.
  # If not existed, exit the program.
  # If existed, give permission to both encoder and decoder on Linux and Mac.
  if not os.path.exists(params['enc']):
    print("Encoder does not exist:" + params['enc'])
    sys.exit(1)
  
  if params['opt']['test_type'] == 1 and not os.path.exists(params['dec']):
    print("Decoder does not exist")
    sys.exit(1)
  
  if ssim == True or vmaf == True:
    if not os.path.exists(params['dec']):
      print("Decoder does not exist: " + params['dec'])
      exit(1)
    if not os.path.exists(params['ffmpeg']):
      print("FFMPEG does not exist:" + params['ffmpeg'])
      exit(1)
    if vmaf == True and not os.path.exists(info_sys['vmaf']):
      print("VMAF does not exist:" + params['vmaf'])
      exit(1)

  if cur_sys == 'Darwin' or cur_sys == 'Linux':
    os.system('chmod +x ' + params['enc'])
    os.system('chmod +x ' + params['dec'])
    if ssim == True or vmaf == True:
      os.system('chmod +x ' + params['dec'])
      os.system('chmod +x ' + params['ffmpeg'])
      if vmaf == True:
        os.system('chmod +x ' + params['vmaf'])

  return params

def execute_task(params, codecname, sde_priority=0, consist_level=0, skiptask=False, ssim=False, vmaf=False, desc=None):
  """Generate command by loaded option and execute each command

  Arg:
    params: a dict, contain all tasks' information
    codecname: string, specify encoder to be tested
    sde_priority: int, specify test level of sde evaluation
    consist_level: int, specify test level of consistency evaluation
    skiptask: bool, specify if current task will be skipped
    ssimvmaf: bool, specify if ssim and vmaf need to be evaluated

  Return:
    out_path: a string, the output path
    config_list: a list, the name of each test configurations
    format_result_list: a list, the collection of documenting results
  """
  # Output file list
  format_result_list = []
  config_list = []
  command_dict_list = []
  isSuccess = True
  out_path = prj_path
  seq_path = prj_path
  if not os.path.exists(out_path):
    os.mkdir(str(out_path))
  if not os.path.exists(seq_path):
    print("Incorrect sequences path")
    sys.exit(1)
  
  test_conf = {
    "codec" : codecname,
    "sde_priority" : sde_priority,
    "consistency_level" : consist_level,
    "ssim" : ssim,
    "vmaf" : vmaf,
    "test_type" : params["opt"]["test_type"],
    "rc_conf" : params["opt"]["rc"],
    "gop_conf" : params["opt"]["gop"],
    "extend_params" : params["opt"]["additional"],
    "desc" : desc
  }

  test_type = params["opt"]["test_type"]

  # Obtain commands to be executed
  cmd_maker = cmd_generator(params, test_conf)
  if test_type == "0":
    command_dict_list = cmd_maker.get_bdrate_test_commands()
  elif test_type == "1":
    command_dict_list = cmd_maker.get_consistency_test_commands()
  elif test_type == "2":
    command_dict_list = cmd_maker.get_sde_test_commands()
  elif test_type == "3":
    command_dict_list = cmd_maker.get_API_test_commands()

  overview_log = os.path.join(out_path, "RUNTEST{}_OVERVIEW.log".format(test_type))
  overview_logger = Log()
  for cmd_dict in command_dict_list:
    config_list.append(cmd_dict["config"])
    sub_path = cmd_dict["sub_path"]
    cmd_list = cmd_dict["cmd_list"]
    out_name_list = cmd_dict["out_name_list"]
    class_list = cmd_dict["class_list"]
    quark_arch_bin = None

    run_log = os.path.join(sub_path, "TASK_RESULT.log")
    overview_logger.info("=============================")
    overview_logger.info("TEST CONFIG: {} SUB_PATH: {}".format(config_list[-1], sub_path))
    overview_logger.info("=============================")

    # Check if task results are available when skiptask is true
    if skiptask == True:
      if not os.path.exists(run_log):
        print("Task results are unavailable. Start current task.")
        skiptask = False
    
    # Execute commands
    if skiptask == False:
      for (i, cmd) in enumerate(cmd_list):
        Log().instance().info("Seq_name {}".format(out_name_list[i]))
        Log().instance().info(cmd)
        res = execute_cmd(cmd)
        if res == False:
          print("Execution error!")
          Log().instance().save_to(run_log)
          overview_logger.error("{}\n Execution error!".format(cmd))
          overview_logger.save_to(overview_log)
          sys.exit(1)

        # post process generated products
        if test_type == "0":
          if ssim == True or vmaf == True:
            dec_yuv = os.path.join(sub_path, "Dec_" + out_name_list[i] + ".yuv")
            os.remove(dec_yuv)
        elif test_type == "1":
          # Compare rec yuv and dec yuv
          rec_yuv = os.path.join(sub_path, "Rec_" + out_name_list[i] + ".yuv")
          dec_yuv = os.path.join(sub_path, "Dec_" + out_name_list[i] + ".yuv")
          if not os.path.exists(rec_yuv):
            overview_logger.error("{} does not exist".format(rec_yuv))
            sys.exit(1)
          elif not os.path.exists(dec_yuv):
            overview_logger.error("{} does not exist".format(dec_yuv))
            sys.exit(1)
          else:
            consist = filecmp.cmp(rec_yuv, dec_yuv)
            os.remove(rec_yuv)
            os.remove(dec_yuv)
            if consist == False:
              overview_logger.error("{}: False".format(os.path.join(sub_path, out_name_list[i])))
              overview_logger.error(cmd)
              isSuccess = False
        elif test_type == "2":
          cmd_split = cmd.split(' ')
          arch = cmd_split[1][1:]
          if arch == "quark":
            overview_logger.info("Seq name: {}".format(out_name_list[i]))
          bin_name = os.path.join(sub_path, "{}.bin".format(out_name_list[i]))
          bin_existed = True if os.path.exists(bin_name) else False
          log_line = "-%-6s  \tBIN_EXIST: %-5s  " % (arch, bin_existed)
          
          # Generate md5 # to be eval
          if bin_existed:
            with open(bin_name, "rb") as bin_file:
              md5_hash = hashlib.md5()
              md5_hash.update(bin_file.read())
              md5_val = md5_hash.hexdigest()
              if arch == "quark":
                quark_arch_md5 = md5_val
                log_line += " %-17s" % (" ")
              else:
                consis = (quark_arch_md5 == md5_val)
                log_line += " ASM_C_SAME: %-5s" % (consis)
              log_line += "  md5:{}".format(md5_val)

          overview_logger.info(log_line)
  
    # Extract log info
    Log().instance().save_to(run_log)
    Log().instance().clear()
    if test_type == "0":
      # Extract bitrate, psnr, ssim/vmaf (if available) log
      format_result_path = os.path.join(sub_path, 'FORMAT_RESULT.csv')
      if skiptask == False:
        out_list = collect_info(run_log, codecname, ssim, vmaf)
        print_out_result(format_result_path, out_list, ssim, vmaf, class_list)
      format_result_list.append(format_result_path)
    elif test_type == "3":
      out_list = collect_info(run_log, codecname, api_test=True)
      for line in out_list:
        overview_logger.info("{} {}".format(line[0], line[1]))

  overview_logger.save_to(overview_log) 
  return isSuccess, out_path, config_list, format_result_list

def single_codec_tasks(argv, configuration=None, prefix_path='.', run_seq=None, skip_task=False, ssim=False, vmaf=False, desc=""):
  """Run single encoder evaluation

  Args:
    param_dict: dict, contain settings of scene, config, codec, encoder, sde test level, consistency
      test level and default prefix of path.
    configuration: , specify test options.
    run_seq: list, specify sequence class to be tested.
    skip_task: bool, specify if current test task to be skipped.
    ssim_vmaf: bool, specify if the ssim and vmaf metrics will be evaluated.
  """
  print(argv)
  scene = argv["scene"]
  codecname = argv["codec"]
  encoder_exe = argv["enc"]
  sde_priority = argv["sde-priority"]
  consist_level = argv["consistency-level"]
  test_type = argv["test-type"]
  json_file = os.path.join(prj_path, "qci_test", "config.json")
  print("Current json file: " + json_file)

  with open(json_file, 'r') as input_json:
    params = load_json(input_json, scene, encoder_exe, configuration, prefix_path, ssim, vmaf)
  
  # Update test type if specified in command line
  if test_type != None:
    params["opt"]["test_type"] = test_type

  if run_seq != None:
    print("Current tested classes: {}".format(params['run_seq']))
    params['run_seq'] = run_seq

  return execute_task(params, codecname, sde_priority, consist_level, skip_task, ssim, vmaf, desc)


if __name__ == '__main__':
  param_dict = parse_options(sys.argv)

  default_prefix = os.path.join("json-samples", "encoder_evaluation")
  if param_dict["gaia-path"] != None:
    default_prefix = os.path.join("json-samples", param_dict["gaia-path"])
  if param_dict["test-type"] > "0":
    default_prefix = "."
  
  ssim = False if param_dict["ssim"] == "0" else True
  vmaf = False if param_dict["vmaf"] == "0" else True

  isSuccess, out_path, config_list, format_result_list = \
    single_codec_tasks(param_dict, prefix_path=default_prefix, ssim=ssim, vmaf=vmaf)
  if isSuccess == False:
    sys.exit(1)
