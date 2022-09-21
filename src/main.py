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

  params['enc'] = info_sys['encoder'] #待测试编码器名字
  params['ffmpeg'] = info_sys['ffmpeg'] #依赖ffmpeg工具
  # load other info
  params['gop'] = input_dicts['gop_param_set'] #gop设置
  params['rc'] = input_dicts['rc_param_set'] #码率控制参数设置cqp和cbr
  params['ext'] = input_dicts['additional_param_set'] #额外编码器设置，编码速度/预处理等
  params['enc_cmd'] = input_dicts['encode_task_template'] #编码器命令行模版
  params['dec_cmd'] = input_dicts['decode_task_template'] #解码器命令行模版，目前忽略用ffmpeg
  params['opt'] = input_dicts[scene + '_test_option'] #具体测试选取哪些参数组合
  params['qps'] = input_dicts['eval_qp_set'] #量化参数qp设置，适应cqp

  if configuration != None:
    params['opt'] = configuration

  seq_json = os.path.join(str(cur_folder), "rule", info_sys['seq_json']) #序列目录
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
    params['out_path'] = os.path.join(cur_folder, "output") #输出路径
    params['seq_path'] = os.path.join(cur_folder, "sequence")
    params['seq'] = seq_dict[scene + '_seqs_info'] #具体待测试序列信息
    params['run_seq'] = seq_dict[scene + '_run_seq']

  # Detect if the encoder or decoder is existed.
  # If not existed, exit the program.
  # If existed, give permission to both encoder and decoder on Linux and Mac.
  codec_path = os.path.join(cur_folder, "bin", params['enc'])#待测试codec路径和文件名
  print (codec_path)
  if not os.path.exists(codec_path):
    print("Encoder does not exist:" + params['enc'])
    sys.exit(1)
  
#   if params['opt']['test_type'] == 1 and not os.path.exists(params['dec']):
#     print("Decoder does not exist")
#     sys.exit(1)
  ffmpeg_path = os.path.join(cur_folder, params['ffmpeg'])

  if cur_sys == 'Darwin' or cur_sys == 'Linux':
    os.system('chmod +x ' + codec_path)
#   print(params)
  return params

def run_codec_task(param):
    # prj_path=os.getcwd()
    prj_path=os.path.abspath(os.path.join(os.getcwd(), ".."))
    print (os.getcwd(),param)
    json_file=os.path.join(prj_path, "rule", param['config'])
    with open(json_file, 'r') as input_json:
        params = load_json(input_json, param['scene']) #成功解析命令和测试文件源信息

  

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




