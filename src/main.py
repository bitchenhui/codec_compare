"""
#!/root/.jumbo/bin/python 
"""
import sys
import subprocess
import xml.dom.minidom
import xml.etree.ElementTree as ET
import json
import os
import re
import math 
import time
import datetime
import platform
# import plot
# import parse_conf
import argparse
import tempfile

parser=argparse.ArgumentParser(
    description='''The tool is used to evalute the quality of video codec, such as h264/h265 and so on. ''',
    epilog="""the end of help.""")
parser.add_argument("-m", "--mode_option", type=str,
    help='4 steps of the program', default='all', choices=['psnr&ssim', 'vmaf', 'bdrate', 'all'])
parser.add_argument("-c", "--codec_name", type=str, 
    help='specific the codec', default='O264rtEncTest')
args=parser.parse_args()

def parse_options(arg1, arg2):
    print(args)
    params = {
    "scene" : "camera",
    "codec" : arg1,
    "level" : arg2,
    "config" : arg1+".json"
    }
    return params


def load_json(input_json, scene, configuration=None, ssim=False, vmaf=False):
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
  # cur_folder = os.getcwd()
  cur_folder = os.path.abspath(os.path.join(os.getcwd(), ".."))
  info_sys = input_dicts['env_conf']
#   if cur_sys == 'Windows':
#     params["exe_folder"] = os.path.join(str(cur_folder), "output", "win")
#     if encoder_exe != None:
#       info_sys['encoder'] = encoder_exe
#     info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'] + ".exe")
#     info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "win",  info_sys['decoder'] + ".exe")
#     info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'] + ".exe")
#     info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'] + ".exe")   
#   elif cur_sys == 'Darwin':
#     params["exe_folder"] = os.path.join(str(cur_folder), "output", "mac")
#     if encoder_exe != None:
#       info_sys['encoder'] = encoder_exe
#     info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'])
#     info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "mac",  info_sys['decoder'])
#     info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'])
#     info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'])
#   elif cur_sys == 'Linux':
#     params["exe_folder"] = os.path.join(str(cur_folder), "output", "linux")
#     if encoder_exe != None:
#       info_sys['encoder'] = encoder_exe
#     info_sys['encoder'] = os.path.join(params["exe_folder"], info_sys['encoder'])
#     info_sys['decoder'] = os.path.join(cur_folder, "qci_test", "bin", "linux", info_sys['decoder'])
#     info_sys['ffmpeg'] = os.path.join(params["exe_folder"], info_sys['ffmpeg'])
#     info_sys['vmaf'] = os.path.join(params["exe_folder"], info_sys['vmaf'])
#   if info_sys == None:
#     print("Invalid platform")
#     exit(1)

  params['enc'] = info_sys['encoder']
  params['ffmpeg'] = info_sys['ffmpeg']
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

  seq_json = os.path.join(str(cur_folder), "rule", info_sys['seq_json'])
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
    params['out_path'] = os.path.join(cur_folder, "output")
    params['seq_path'] = os.path.join(cur_folder, "sequence")
    params['seq'] = seq_dict[scene + '_seqs_info']
    params['run_seq'] = seq_dict[scene + '_run_seq']

  # Detect if the encoder or decoder is existed.
  # If not existed, exit the program.
  # If existed, give permission to both encoder and decoder on Linux and Mac.
  codec_path = os.path.join(cur_folder, "bin", params['enc'])
  print (codec_path)
  if not os.path.exists(codec_path):
    print("Encoder does not exist:" + params['enc'])
    sys.exit(1)
  
#   if params['opt']['test_type'] == 1 and not os.path.exists(params['dec']):
#     print("Decoder does not exist")
#     sys.exit(1)
  ffmpeg_path = os.path.join(cur_folder, params['ffmpeg'])
  if ssim == True or vmaf == True:
    # if not os.path.exists(params['dec']):
    #   print("Decoder does not exist: " + params['dec'])
    #   exit(1)
    if not os.path.exists(params['ffmpeg']):
      print("FFMPEG does not exist:" + params['ffmpeg'])
      exit(1)
    # if vmaf == True and not os.path.exists(info_sys['vmaf']):
    #   print("VMAF does not exist:" + params['vmaf'])
    #   exit(1)

  if cur_sys == 'Darwin' or cur_sys == 'Linux':
    os.system('chmod +x ' + codec_path)
    if ssim == True or vmaf == True:
      os.system('chmod +x ' + params['ffmpeg'])
#   print(params)
  return params

def run_codec_task(param):
    # prj_path=os.getcwd()
    prj_path=os.path.abspath(os.path.join(os.getcwd(), ".."))
    print (os.getcwd(),param)
    json_file=os.path.join(prj_path, "rule", param['config'])
    with open(json_file, 'r') as input_json:
        params = load_json(input_json, param['scene'])

  

if __name__ == '__main__':
    codec_evl = ''
    codec_evl_level= ''
    if (args.codec_name):
        codec_evl = args.codec_name
    else:
        print ("please input the codec name!")
        exit(1)
    if (args.mode_option):
        codec_evl_level = args.mode_option
    else:
        print ("please input the codec evl mode!")
        exit(1)
    param_dict = parse_options(codec_evl, codec_evl_level)
    
    run_codec_task(param_dict)




