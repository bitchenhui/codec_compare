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
import plot
import parse_conf
import argparse
import tempfile

parser=argparse.ArgumentParser(
    description='''The tool is used with evalute the speed
        and quality of two video codecs, such as 264/265 and so on. ''',
    epilog="""the end of help.""")
parser.add_argument('--video_list', type=str, 
    default='./src/src_video.list', help='the source video list in ./src/ ')
parser.add_argument("-o", "--Output_options", type=str, 
    help='three steps of the program', default='all', choices=['video', 'result', 'figure', 'all'])
parser.add_argument("-c", "--codec_options", type=str, 
    help='h264 or h265', default='h265', choices=['h265', 'h264'])
args=parser.parse_args()

class MediaInfo(object):
    """
    struct of media information
    """
    width = ''
    height = ''
    framerate = ''
    duration_s = ''
    bitrate = ''


class CurveScore(object):
    """
    Curve Score
    """
    vmaf_score = ''
    psnr_score = ''
    ssim_score = ''
    speed = ''


def decode_duration_hms2s(duration):
    """
    hh:mm:ss to 000.000s
    return float s
    """
    str_time = duration
    time = re.split(':', str_time)
    time_h = ''.join(time[0])
    time_min = ''.join(time[1])
    time_sec = ''.join(time[2])
    duration_s = float(time_h)*3600 + float(time_min)*60 + float(time_sec)
    return duration_s


def modify_transform_cmd(SRC_NAME, DST_NAME, BITRATE, VBV_BUFSIZE, VBV_MAXRATE, transform_cmd):
    """
    modify conf_transform_cmd in ./conf/config.conf to transform_cmd
    """
    mid_transform_cmd = ''
    val = int(BITRATE)
    vb = str(val)
    print transform_cmd
    if (VBV_BUFSIZE == 0 and VBV_MAXRATE == 0):
        VBV_MAXRATE = str(int(VBV_MAXRATE))
        VBV_BUFSIZE = str(int(VBV_BUFSIZE))
        if (transform_cmd):
            mid_transform_cmd = re.sub('SRC_NAME', SRC_NAME, transform_cmd)
            mid_transform_cmd = re.sub('DST_NAME', DST_NAME, mid_transform_cmd)
            mid_transform_cmd = re.sub('BITRATE', vb, mid_transform_cmd)	
    elif(VBV_BUFSIZE == 0 and VBV_MAXRATE != 0):
        VBV_MAXRATE = str(int(VBV_MAXRATE))
        VBV_BUFSIZE = str(int(VBV_BUFSIZE))	
        if (transform_cmd):
            mid_transform_cmd = re.sub('SRC_NAME', SRC_NAME, transform_cmd)
            mid_transform_cmd = re.sub('DST_NAME', DST_NAME, mid_transform_cmd)
            mid_transform_cmd = re.sub('BITRATE', vb, mid_transform_cmd)
            mid_transform_cmd = re.sub('VBV_MAXRATE', VBV_MAXRATE, mid_transform_cmd)	
    elif(VBV_BUFSIZE != 0 and VBV_MAXRATE == 0):
        VBV_MAXRATE = str(int(VBV_MAXRATE))
        VBV_BUFSIZE = str(int(VBV_BUFSIZE))	
        if (transform_cmd):
            mid_transform_cmd = re.sub('SRC_NAME', SRC_NAME, transform_cmd)
            mid_transform_cmd = re.sub('DST_NAME', DST_NAME, mid_transform_cmd)
            mid_transform_cmd = re.sub('BITRATE', vb, mid_transform_cmd)
            mid_transform_cmd = re.sub('VBV_BUFSIZE', VBV_BUFSIZE, mid_transform_cmd)	
    else:
        VBV_MAXRATE = str(int(VBV_MAXRATE))
        VBV_BUFSIZE = str(int(VBV_BUFSIZE))	
        if (transform_cmd):
            mid_transform_cmd = re.sub('SRC_NAME', SRC_NAME, transform_cmd)
            mid_transform_cmd = re.sub('DST_NAME', DST_NAME, mid_transform_cmd)
            mid_transform_cmd = re.sub('BITRATE', vb, mid_transform_cmd)
            mid_transform_cmd = re.sub('VBV_MAXRATE', VBV_MAXRATE, mid_transform_cmd)
            mid_transform_cmd = re.sub('VBV_BUFSIZE', VBV_BUFSIZE, mid_transform_cmd)
    return mid_transform_cmd


def resultInfo_write_header(codec_name, SRC_NAME):
    """
    resultInfo_write_header
    """
    codec_lib = parse_conf.parse_conf(codec_name)
    codec_type_str = 'Codec:' + codec_lib
    resultInfoFp.write("|%15s |%35s |" % (codec_type_str, SRC_NAME))
    print_char = 'bitrate/bit'
    resultInfoFp.write(" %11s |" % print_char)
    print_char = 'vmaf_score'
    resultInfoFp.write(" %11s |" % print_char)
    print_char = 'ssim'
    resultInfoFp.write(" %11s |" % print_char)
    print_char = 'psnr/dB'
    resultInfoFp.write(" %11s |" % print_char)
    print_char = 'speed/fps'
    resultInfoFp.write(" %11s |" % print_char)
    resultInfoFp.write("\n")
   

def generate_conf_transcmd(SRC_NAME, BITRATE, codec_name):
    """
    generate transcode cmd And filename
    """
    conf_transform_cmd = ''
    if (codec_name == 'codecB_name'):
        codec_lib = parse_conf.parse_conf(codec_name)
        conf_str = 'codecB_cmd'
        conf_transform_cmd = parse_conf.parse_conf(conf_str)
    if (codec_name == 'codecA_name'):
        codec_lib = parse_conf.parse_conf(codec_name)
        conf_str = 'codecA_cmd'
        conf_transform_cmd = parse_conf.parse_conf(conf_str) 
    return conf_transform_cmd


def generate_dstfilename(SRC_NAME, BITRATE, codec_name, codec_format):
    """
    generate transcode cmd And filename
    """
    DST_NAME = ''
    src = re.sub('_[0-9].*$', "", SRC_NAME)
    src = re.sub('.yuv', "", src)
    src = src.strip()
    print src
    if (codec_name == 'codecB_name'):
        codec_lib = parse_conf.parse_conf(codec_name)
        DST_NAME = src + '_' + codec_lib + '_' + str(BITRATE) + codec_format
    if (codec_name == 'codecA_name'):
        codec_lib = parse_conf.parse_conf(codec_name)
        DST_NAME = src + '_' + codec_lib + '_' + str(BITRATE) + codec_format
    return DST_NAME


def get_mediainfo(DST_NAME, media_info, codec_format):
    """
    get dst_name media information
    """
    print codec_format
    MP4_NAME = re.sub( codec_format + '$', '.mp4', DST_NAME)
    print 'mp4_video:', MP4_NAME
    package_cmd = 'mediainfo/mediainfo_ffmpeg -i ./dst/' + DST_NAME + ' -c copy -f mp4 -y ./dst/' + MP4_NAME
    print package_cmd
    handle_excute_bin = subprocess.Popen(package_cmd, shell=True)
    handle_excute_bin.wait()
    out_temp = tempfile.SpooledTemporaryFile(bufsize=100*4096)#filehandle
    fileno = out_temp.fileno()#filename
    mediainfo_cmd = 'mediainfo/mediainfo_ffmpeg -i ./dst/' + MP4_NAME    
    print mediainfo_cmd
    handle_excute_bin = subprocess.Popen(mediainfo_cmd, shell=True, \
          stdout = fileno, stderr= fileno)
    handle_excute_bin.wait()
    out_temp.seek(0)
    for media_info_msg in out_temp.readlines():
        reback_duration = re.search('Duration:.*', media_info_msg)
        if(reback_duration):
            duration = reback_duration.group(0)
            duration_time = re.split(',', duration)
            duration_time = ''.join(duration_time[0])
            duration_time = re.sub(r'Duration: ', "", duration_time)
            duration_s = decode_duration_hms2s(duration_time)
            media_info.duration_s = duration_s
            print 'duration_s:', duration_s
        reback_videoinfo = re.search('Video:.*', media_info_msg)
        if(reback_videoinfo):
            index = 2
            videoinfo = reback_videoinfo.group(0)
            videoinfo = re.split(',', videoinfo)
            print videoinfo
            wxh =''.join(videoinfo[index])
            print wxh
            wxh = re.sub('\s+', "", wxh)
            guess = wxh[0:2]
            print "guess", guess
            flag = guess.isdigit()
            if not flag:
                index += 1
                wxh =''.join(videoinfo[index])
            wxh = wxh.lstrip()
            print wxh
            wxh = re.split('\s+', wxh)
            wxh =''.join(wxh[0])
            wxh = re.split('x', wxh)
            print "wxh",  wxh
            width = ''.join(wxh[0])
            width = re.sub('\[.*', "", width)
            height = ''.join(wxh[1])
            height = re.sub('\[.*', "", height)
            print "height:", height
            index += 1
            bitrate = ''.join(videoinfo[index])
            print bitrate
            bitrate = re.sub('\s+', "", bitrate)
            print bitrate
            bitrate = re.sub('kb/s', "", bitrate)
            print bitrate
            index += 1
            framerate = ''.join(videoinfo[index])
            framerate = re.sub('\s+', "", framerate)
            framerate = re.sub('fps', "", framerate)
            media_info.width = width
            media_info.height = height
            media_info.bitrate = bitrate
            media_info.framerate = framerate 
    out_temp.close()

def calculate_vmaf(media_info, curve_scores):
    """
    calculate_vmaf
    """
    out_temp = tempfile.SpooledTemporaryFile(bufsize=100*4096)#filehandle
    fileno = out_temp.fileno()#filename	
    calculate_vmaf_cmd = ('vmaf/vmafossexec yuv420p ' + media_info.width + ' ' + media_info.height + 
        ' ./tmp/dst.yuv ./tmp/src.yuv vmaf/model/vmaf_v0.6.1.pkl --log ./tmp/vmaf_result.log')
    conf_str = 'Enable_Vmaf'
    Enable_Vmaf = parse_conf.parse_conf(conf_str)
    if (Enable_Vmaf == '0'):
        calculate_vmaf_cmd = ''
    print "calculate_vmaf_cmd:", calculate_vmaf_cmd
    handle_video_client = subprocess.Popen(calculate_vmaf_cmd, shell=True, \
        stdout = fileno, stderr= fileno)
    handle_video_client.wait()
    out_temp.seek(0)
    vmaf_score = ''
    for media_info_msg in out_temp.readlines():
        reback = re.search('VMAF score =.*[a-zA-Z0-9]', media_info_msg)
        if(reback):
            vmaf_score = reback.group(0)
            vmaf_score = re.sub('VMAF score =', "", vmaf_score)
            vmaf_score = re.sub('\s+', "", vmaf_score)
            print 'vmaf_score=', vmaf_score
    curve_scores.vmaf_score = vmaf_score
    out_temp.close()
    

def calculate_psnr_ssim(media_info, curve_scores):
    """
    calculate psnr and ssim score
    """
    calculate_psnr_ssim_cmd = ('mediainfo/mediainfo_ffmpeg -pix_fmt yuv420p ' + '-s ' + 
        media_info.width + 'x' + media_info.height + 
        ' -i tmp/dst.yuv -pix_fmt yuv420p ' + '-s ' + media_info.width + 'x' + media_info.height + 
        ' -i ./tmp/src.yuv ' + '-lavfi  "ssim;[0:v][1:v]psnr" -f null -') 
    conf_str = 'Enable_Psnr'
    Enable_Psnr = parse_conf.parse_conf(conf_str)
    if (Enable_Psnr == '0'):
        calculate_vmaf_cmd = ''
    out_temp = tempfile.SpooledTemporaryFile(bufsize=100*4096)#filehandle
    fileno = out_temp.fileno()#filename
    print "calculate_psnr_ssim_cmd:", calculate_psnr_ssim_cmd
    handle_video_client = subprocess.Popen(calculate_psnr_ssim_cmd, shell=True, \
        stdout = fileno, stderr= fileno)
    handle_video_client.wait()
    ssim_score = ''
    psnr_score = ''
    out_temp.seek(0)
    for media_info_msg in out_temp.readlines():
        reback_ssim = re.search('All:.*[ ]', media_info_msg)
        reback_psnr = re.search('average:.* ', media_info_msg)    
        if(reback_ssim):
            ssim_score = reback_ssim.group(0)
            ssim_score = re.sub('All:', "", ssim_score)
            ssim_score = re.sub('\s+', "", ssim_score)
            print 'ssim_score', ssim_score
        if(reback_psnr):
            psnr_score = reback_psnr.group(0)
            psnr_score = re.sub('average:', "", psnr_score)
            psnr_score = re.sub('min:.*', "", psnr_score)
            psnr_score = re.sub('\s+', "", psnr_score)
            print 'psnr_score', psnr_score
    curve_scores.ssim_score = ssim_score
    curve_scores.psnr_score = psnr_score
    out_temp.close()

 
def evl_codecs_func(media_list, resultInfoFp, v_count, codec_name, codec_format):
    """
    main function for evalute the two codecs
    """
    srcFp = open(media_list, "r")
    	
    excute_data = './dst/' + 'excute_time_' + codec_name + '.list'
    print excute_data
    #os.system(":>%s" % excute_data)
    excuteFp = open(excute_data, "r")
    print excuteFp
    #dst_data = './dst/' + 'mp4_list.list'
    #os.system(":>%s" % dst_data)
    #dstInfoFp = open(dst_data, "r")
	
    i_count = 0
    while(i_count < v_count):
        srcline = srcFp.readline()
        if not srcline:
            break
        srcline = srcline.split(' ', 1)
        ## If you want to filter out some video
        if(i_count < jump_num):
            i_count += 1
            print "%s skip" % (srcline[0])
            continue
        SRC_NAME = ''.join(srcline[0])
        SRC_NAME = SRC_NAME.strip()
        print SRC_NAME
        i_bitrate = 0
        decode_yuv_cmd = 'mediainfo/mediainfo_ffmpeg -i src/' + SRC_NAME + ' -pix_fmt yuv420p -y ./tmp/src.yuv'
        print "##decode_src_yuv:"
        print decode_yuv_cmd
        ##decode_yuv_cmd = ''
        print "codec_name:", codec_name
        resultInfo_write_header(codec_name, SRC_NAME) 
        handle_excute_bin = subprocess.Popen(decode_yuv_cmd, shell=True)
        handle_excute_bin.wait()
        num_bitrate_levels = 12
        while (i_bitrate < num_bitrate_levels):
            BITRATE = 500 + i_bitrate * 500
            print_char = ''
            resultInfoFp.write("%53s |" % print_char)
            print "i_bitrate:", i_bitrate
            DST_NAME = ''
            if (codec_name == 'codecA_name'):
                str_char = 'codecA_rldes'
            if (codec_name == 'codecB_name'):
                str_char = 'codecB_rldes'
            ret_val = parse_conf.parse_conf(str_char)
            vbv_val = parse_conf.VbvVal()
            exp_list = parse_conf.mixed_operation(ret_val)
            parse_conf.calcul_vbv_val(exp_list, vbv_val)
            if(vbv_val.bitrate_unit == 1):
                BITRATE = BITRATE * 1000
            #VBV_BUFSIZE = vbv_val.vbv_bufsize * BITRATE
            #VBV_MAXRATE = vbv_val.vbv_maxrate * BITRATE
            DST_NAME = generate_dstfilename(SRC_NAME, BITRATE, codec_name, codec_format)
            excute_time = ''
            print DST_NAME
            excuteline = excuteFp.readline()
            print excuteline
            #if not excuteline:
            #    break
            excuteline = excuteline.split(' ', 1)
            excute_time = ''.join(excuteline[0])
            excute_time = excute_time.strip()
            excute_time = float(excute_time)
            print "excute_time:", excute_time
			
            curve_scores = CurveScore()
            media_info = MediaInfo()
            get_mediainfo(DST_NAME, media_info, codec_format)
            print media_info.bitrate
            print media_info.framerate
            resultInfoFp.write(" %11s |" % media_info.bitrate)
            nframes = media_info.duration_s * float(media_info.framerate)
            print "nframes:", nframes
            curve_scores.speed = float(nframes / excute_time)
            curve_scores.speed = str(curve_scores.speed)[0:9]
            if(curve_scores.speed == ''):
               print "transform_cmd maybe error!"
            else:
               print "speed:", curve_scores.speed
            decode_yuv_cmd = ('mediainfo/mediainfo_ffmpeg -i ./dst/' + 
               DST_NAME + ' -pix_fmt yuv420p -y tmp/dst.yuv')
            print decode_yuv_cmd
            handle_video_client = subprocess.Popen(decode_yuv_cmd, shell=True)
            handle_video_client.wait()
            calculate_vmaf(media_info, curve_scores)
            if (curve_scores.vmaf_score == ''):
               curve_scores.vmaf_score = '0'
            resultInfoFp.write(" %11s |" % curve_scores.vmaf_score)
            calculate_psnr_ssim(media_info, curve_scores) 
            if(curve_scores.ssim_score == '' or curve_scores.psnr_score == ''):
               print 'calculate_psnr_ssim_cmd error!'
               curve_scores.ssim_score = '0'
               curve_scores.psnr_score = '0'
            resultInfoFp.write(" %11s |" % curve_scores.ssim_score)
            resultInfoFp.write(" %11s |" % curve_scores.psnr_score)
            resultInfoFp.write(" %11s |" % curve_scores.speed)
            resultInfoFp.write("\n")
            resultInfoFp.flush()
            i_bitrate += 1
        print 'cal No:', i_count
        i_count += 1
        t = 1
        if(i_count % 20 == 0):
            time.sleep(t)
            print 'sleep', t, 's'
    #dstInfoFp.close()
    excuteFp.close()
    srcFp.close()

def trans_codecs_func(media_list, v_count, codec_name, codec_format):
    """
    main function for evalute the two codecs
    """
    srcFp = open(media_list, "r")
	
    excute_data = './dst/' + 'excute_time_' + codec_name + '.list'
    os.system(":>%s" % excute_data)
    excuteFp = open(excute_data, "w")

    i_count = 0
    while(i_count < v_count):
        srcline = srcFp.readline()
        if not srcline:
            break
        srcline = srcline.split(' ', 1)
        ## If you want to filter out some video
        if(i_count < jump_num):
            i_count += 1
            print "%s skip" % (srcline[0])
            continue
        SRC_NAME = ''.join(srcline[0])
        SRC_NAME = SRC_NAME.strip()
        print SRC_NAME
        i_bitrate = 0
        print "codec_name:", codec_name
        VBV_BUFSIZE = 0
        VBV_MAXRATE = 0

        vbv_val = parse_conf.VbvVal()
        num_bitrate_levels = 12
        while (i_bitrate < num_bitrate_levels):
            BITRATE = 500 + i_bitrate * 500
            ## BITRATE levels = [500000, 1000000, 1500000, 2000000, 2500000, 3000000,\
            ##                   3500000, 4000000, 4500000, 5000000, 5500000, 6000000]
            print "bitrate:", BITRATE
            str_char = ''
            if (codec_name == 'codecA_name'):
                str_char = 'codecA_rldes'
            if (codec_name == 'codecB_name'):
                str_char = 'codecB_rldes'
            ret_val = parse_conf.parse_conf(str_char)
            exp_list = parse_conf.mixed_operation(ret_val)
            parse_conf.calcul_vbv_val(exp_list, vbv_val)
            if(vbv_val.bitrate_unit == 1):
                BITRATE = BITRATE * 1000
            VBV_BUFSIZE = vbv_val.vbv_bufsize * BITRATE
            VBV_MAXRATE = vbv_val.vbv_maxrate * BITRATE
            print_char = ''

            DST_NAME = ''
            conf_transform_cmd = ''
            conf_transform_cmd = generate_conf_transcmd(SRC_NAME, BITRATE, codec_name)
            print conf_transform_cmd
            DST_NAME = generate_dstfilename(SRC_NAME, BITRATE, codec_name, codec_format)
            print DST_NAME
            #dstInfoFp.write(str(DST_NAME))
            #dstInfoFp.write("\n")
			
            transform_cmd = modify_transform_cmd(SRC_NAME, 
                DST_NAME, BITRATE, VBV_BUFSIZE, VBV_MAXRATE, conf_transform_cmd)
            start_time = datetime.datetime.now()
            print 'transform_cmd:', transform_cmd
            ##transform_cmd = ''
            handle_excute_bin = subprocess.Popen(transform_cmd, shell=True)
            handle_excute_bin.wait()
            end_time = datetime.datetime.now()
            excute_time = (end_time - start_time).total_seconds()
            print "excute_time:", excute_time
            excuteFp.write(str(excute_time))
            excuteFp.write("\n")
			
            i_bitrate += 1
        print 'transcode media No:', i_count
        i_count += 1
        t = 1
        if(i_count % 20 == 0):
            time.sleep(t)
            print 'sleep', t, 's'
    #dstInfoFp.close()
    srcFp.close()


tmpdata = './tmp'
#src_video_list = sys.argv[1]
video_count_for_evl = 10
jump_num = 0


try:
    media_list = ''
    ### input 0 mediaID list
    if (args.video_list):
        media_list = args.video_list
    else:
        print "please input the video_list.list file!"
    print media_list
	
    options_choice = ''
    if (args.Output_options):
        options_choice = args.Output_options
    else:
        print "please input the Output_options!"
    print options_choice


    codec_choice = ''
    if (args.codec_options):
        codec_choice = args.codec_options
    else:
        print "please input the codec type!"    
    print codec_choice
    if (codec_choice == 'h265'):
        codec_format = '.265'
    else:
        codec_format = '.264'
 
    if (options_choice == 'video'):

        #dst_data = './dst/' + 'mp4_list.list'
        #os.system(":>%s" % dst_data)
        #dstInfoFp = open(dst_data, "w")
        ##run codecs A && B
        codec_name = 'codecA_name'
        trans_codecs_func(media_list, video_count_for_evl, codec_name, codec_format)
        codec_name = 'codecB_name'
        trans_codecs_func(media_list, video_count_for_evl, codec_name, codec_format)
        #dstInfoFp.close()
    elif(options_choice == 'result'):
    #result		
        os.system("mkdir %s" % tmpdata)
        result_data = './output/' + 'result.txt'
        os.system(":>%s" % result_data)
        resultInfoFp = open(result_data, "w")
        
        ##run codecs A && B
        codec_name = 'codecA_name'
        evl_codecs_func(media_list, resultInfoFp, video_count_for_evl, codec_name, codec_format)
        codec_name = 'codecB_name'
        evl_codecs_func(media_list, resultInfoFp, video_count_for_evl, codec_name, codec_format)  
        resultInfoFp.close()
    elif(options_choice == 'figure'):
        ##plot the drow
        bdrateFp = plot.init_plot()
        plot.parse_result()
        plot.plot_curves_figures()
        plot.calculate_bd_rate(bdrateFp)
        plot.close_plot(bdrateFp)   
    else :
        #dst_data = './dst/' + 'mp4_list.list'
        #os.system(":>%s" % dst_data)
        #dstInfoFp = open(dst_data, "w")
        ##run codecs A && B
        codec_name = 'codecA_name'
        trans_codecs_func(media_list, video_count_for_evl, codec_name, codec_format)
        codec_name = 'codecB_name'
        trans_codecs_func(media_list, video_count_for_evl, codec_name, codec_format)
        #dstInfoFp.close()
        os.system("mkdir %s" % tmpdata)
        result_data = './output/' + 'result.txt'
        os.system(":>%s" % result_data)
        resultInfoFp = open(result_data, "w")
        
        ##run codecs A && B
        codec_name = 'codecA_name'
        evl_codecs_func(media_list, resultInfoFp, video_count_for_evl, codec_name, codec_format)
        codec_name = 'codecB_name'
        evl_codecs_func(media_list, resultInfoFp, video_count_for_evl, codec_name, codec_format)  
        resultInfoFp.close()
        ##plot the drow
        bdrateFp = plot.init_plot()
        plot.parse_result()
        plot.plot_curves_figures()
        plot.calculate_bd_rate(bdrateFp)
        plot.close_plot(bdrateFp)
finally:
    print 'the shell is over!'





