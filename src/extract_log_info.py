# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sys
import csv
import string
import platform
# index, seq_name, rate, psnr_y, psnr_u, psnr_v, fps
MAX_INDEX = 1000
ENTRY_ONLY_PSNR = 8
ENTRY_SSIM_VMAF = 12
def find_frms_kbps_index(split_line):
    for i in range(len(split_line)-1, -1, -1):
        if split_line[i] == "Avg":
            frame_index = i - 1
            bits_index = i + 4
            break
    return frame_index, bits_index

def extract_t265_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        FoundLine = False
        FoundPrevLine = False
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = (line.split(' ')[1]).replace("\n", "")
            if FoundLine == True and FoundPrevLine == True:
                out_list[index][2] = line.split(' ')[-20]
                out_list[index][3] = line.split(' ')[-17]
                out_list[index][4] = line.split(' ')[-14]
                out_list[index][5] = line.split(' ')[-11]
            if "Bitrate" in line:
                FoundLine = True
            else:
                FoundLine = False
                FoundPrevLine = False
            if "Preset" in line:
                FoundPrevLine = True

            if "time" in line and  "cost" in line:
                out_list[index][6] = line.split(' ')[-2]
                index = index + 1
    return out_list

def extract_x265_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        frameI_info = [0] * 5
        frameP_info = [0] * 5
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = line.split(" ")[1]                
            if "frame P" in line and "Avg QP" in line:
                split_line = line.split(" ")
                frame_index, bits_index = find_frms_kbps_index(split_line)
                frameP_info[0] = split_line[frame_index].replace(",", "")
                frameP_info[1] = split_line[bits_index]
                frameP_info[2] = split_line[-3].replace("Y:", "")
                frameP_info[3] = split_line[-2].replace("U:", "")
                frameP_info[4] = (split_line[-1].replace("V:", "")).replace("\n", "")
                total_frm = int(frameI_info[0]) + int(frameP_info[0])
                out_list[index][2] = round((float(frameI_info[1]) * int(frameI_info[0]) + float(frameP_info[1]) * int(frameP_info[0])) / total_frm, 3)
                out_list[index][3] = round((float(frameI_info[2]) * int(frameI_info[0]) + float(frameP_info[2]) * int(frameP_info[0])) / total_frm, 3)
                out_list[index][4] = round((float(frameI_info[3]) * int(frameI_info[0]) + float(frameP_info[3]) * int(frameP_info[0])) / total_frm, 3)
                out_list[index][5] = round((float(frameI_info[4]) * int(frameI_info[0]) + float(frameP_info[4]) * int(frameP_info[0])) / total_frm, 3)              
            if "frame I" in line and "Avg QP" in line:
                split_line = line.split(" ")
                frame_index, bits_index = find_frms_kbps_index(split_line)
                frameI_info[0] = split_line[frame_index].replace(",", "")
                frameI_info[1] = split_line[bits_index]
                frameI_info[2] = split_line[-3].replace("Y:", "")
                frameI_info[3] = split_line[-2].replace("U:", "")
                frameI_info[4] = (split_line[-1].replace("V:", "")).replace("\n", "")
            if "encoded" in line:
                out_list[index][6] = line.split(' ')[5].replace("(", "")
                index = index + 1
    return out_list

def extract_h265_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            internal_list = line.split(' ')
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = (internal_list[1]).replace("\n", "")
            if (line.find('FPS:') != -1):
                out_list[index][6] = internal_list[-1].replace("\n", "")
            if (line.find('bitrate, psnr :') != -1):
                out_list[index][3] = internal_list[-1].split('\t')[1]
                out_list[index][4] = internal_list[-1].split('\t')[2]
                out_list[index][5] = internal_list[-1].split('\t')[3].replace("\n", "")
                out_list[index][2] = internal_list[-1].split('\t')[0]
                index = index + 1
    return out_list

def extract_265old_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            internal_list = line.split(' ')
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = (internal_list[1]).replace("\n", "")
            if ('FPS:' in line):
                out_list[index][6] = internal_list[-1].replace("\n", "")
            if ('bitrate, psnr' in line):
                out_list[index][3] = internal_list[-1].split('\t')[1]
                out_list[index][4] = internal_list[-1].split('\t')[2]
                out_list[index][5] = internal_list[-1].split('\t')[3]
                out_list[index][2] = internal_list[-1].split('\t')[0]
                index = index + 1
    return out_list
def extract_x264_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = line.split(" ")[1]
            if "PSNR Mean" in line:
                split_line = line.split(" ")
                if split_line[2] == "PSNR":
                    out_list[index][2] = (split_line[-1].replace("kb/s:", "")).replace("\n", "")
                    out_list[index][3] = split_line[4].replace("Y:", "")
                    out_list[index][4] = split_line[5].replace("U:", "")
                    out_list[index][5] = split_line[6].replace("V:", "")
            if "encoded" in line:
                out_list[index][6] = line.split(' ')[3]
                index = index + 1
    return out_list

def extract_mvpx_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    frame_num = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            split_line = line.split()
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = (line.split(" ")[1]).replace("\n", "")
            if "global mean psnr" in line:
                str(split_line[6]).replace("\r", "")
                str(split_line[6]).replace("\n", "")
                out_list[index][3] = split_line[4][5:]
                out_list[index][4] = split_line[5][3:]
                out_list[index][5] = split_line[6][3:]
                index = index+1
            if "bitrate in bps" in line:
                str(split_line[2]).replace("\r", "")
                str(split_line[2]).replace("\n", "")
                bitrate = int(split_line[2][4:])/1000.00
                out_list[index][2] = bitrate
            if "frame num:" in line:
                frame_num = frame_num+1
            if "EncodeFrame:" in line:
                encode_time = float(split_line[1])
                encode_fps = round(frame_num / encode_time,2)
                frame_num = 0
                out_list[index][6] = encode_fps
    return out_list

def extract_h264_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                out_list[index][0] = index + 1
                out_list[index][1] = (line.split(" ")[1]).replace("\n", "")
            if "PSNR Mean" in line:
                split_line = line.split(" ")
                if (split_line[0] == "PSNR"):
                    out_list[index][2] = (split_line[-1].replace("kb/s:", "")).replace("\n", "")
                    out_list[index][3] = split_line[2].replace("Y:", "")
                    out_list[index][4] = split_line[3].replace("U:", "")
                    out_list[index][5] = split_line[4].replace("V:", "")
                    index = index + 1
            if "FPS:" in line:
                out_list[index][6] = (line.split(" ")[-1]).replace("\n", "")
    return out_list

def extract_netint_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    encoder_flag = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                encoder_flag = 0
                out_list[index][0] = index + 1
                out_list[index][1] = (line.split(" ")[1]).replace("\n", "")
            if "frame=" in line:
                if encoder_flag == 0 or encoder_flag == 1:
                    split_line = line.split()
                    encoder_flag = 1
                    for split in split_line:
                        if "kbits/s" in split:
                            out_list[index][2] = (split.replace("bitrate=","")).replace("kbits/s","")
                        if "fps=" in split:
                            out_list[index][6] = split.replace("fps=", "")
            else:
                if encoder_flag == 1:
                    encoder_flag = 2
                    index = index + 1
    return out_list

def extract_videocore_info(in_file):
    out_list = [[-1 for i in range(ENTRY_ONLY_PSNR)] for j in range(MAX_INDEX)]
    index = 0
    frames_num = 0
    fps = 0
    file_size = 0
    hardware = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                encoder_flag = 0
                out_list[index][0] = index + 1
                out_list[index][1] = (line.split(" ")[1]).replace("\n", "")
            if "Total frames number" in line:
                split_line = line.split()
                frames_num = split_line[3]
                fps = split_line[6]
            if "encfps:" in line:
                hardware = 1
                split_line = line.split(':')
                out_list[index][6] = split_line[1][:-1]
            if "Total Codec Time" in line and hardware == 0:
                split_line = line.split()
                out_list[index][6] = str(int(frames_num)/(int(split_line[3])/1000.0))
            if "File size" in line:
                split_line = line.split()
                file_size = split_line[2]
                out_list[index][2] = str(int(file_size) / (int(frames_num)/int(fps)))
                index = index + 1
            
    return out_list

def extract_ssim_psnr_info(in_file, first_out_list, ssim_psnr=True, vmaf=False):
    out_list = [[-1 for i in range(ENTRY_SSIM_VMAF)] for j in range(MAX_INDEX)]
    index = 0
    with open(in_file, 'r', encoding='UTF-8') as f:
        for line in f:
            internal_list = line.split(' ')
            out_list[index][0] = first_out_list[index][0]
            out_list[index][1] = first_out_list[index][1]
            out_list[index][2] = first_out_list[index][2]
            out_list[index][ENTRY_SSIM_VMAF-2] = first_out_list[index][ENTRY_ONLY_PSNR-2]
            if ssim_psnr == False:
                out_list[index][3] = first_out_list[index][3]
                out_list[index][4] = first_out_list[index][4]
                out_list[index][5] = first_out_list[index][5]
            if "Parsed_ssim_0" in line:
                out_list[index][6] = (internal_list[4]).replace("Y:", "")
                out_list[index][7] = (internal_list[6]).replace("U:", "")
                out_list[index][8] = (internal_list[8]).replace("V:", "")
            if (ssim_psnr == True and line.find('Parsed_psnr_1') != -1):
                out_list[index][3] = (internal_list[4]).replace("y:", "")
                out_list[index][4] = (internal_list[5]).replace("u:", "")
                out_list[index][5] = (internal_list[6]).replace("v:", "")
                if vmaf == False:
                  index = index + 1
            if (vmaf and line.find('VMAF_SCORE') != -1):
                out_list[index][9] = internal_list[-1].replace("\n", "")
                index = index + 1
    return out_list

def extract_api_stability_info(in_file):
    out_list = []
    with open(in_file, 'r') as f:
        stability_ok = False
        seq_prev = ""
        for row_index, line in enumerate(f):
            if "Seq_name" in line:
                seq_cur = (line.split(" ")[1]).replace("\n", "")
                if seq_prev == "":
                    seq_prev = seq_cur
                else:
                    out_list.append([seq_prev, stability_ok])
                    stability_ok = False
                    seq_prev = seq_cur
            if "Stability test is ok" in line:
                stability_ok = True
        # For last seq in the test
        out_list.append([seq_prev, stability_ok])
    return out_list

def collect_info(in_file, codecname, ssim_psnr=False, vmaf=False, api_test=False):
    #print "in_file_path:", in_file
    if api_test == True:
        out_list = extract_api_stability_info(in_file)
        return out_list

    if codecname == "vp9":
        codecname = "mvpx"
    funcname = "extract_" + codecname + "_info"
    print(funcname)
    out_list = eval(funcname)(in_file)
    if ssim_psnr == True or vmaf == True:
        out_list = extract_ssim_psnr_info(in_file, out_list, ssim_psnr, vmaf)
    return out_list

def print_out_result(out_file_name, out_list, ssim=False, vmaf=False, class_list=None):
    #print "out_file_path:", out_file_name
    if platform.python_version() < "3.0.0":
        out_file = open(out_file_name, "wb")
    else:
        out_file = open(out_file_name, 'w', newline='')

    # Write CSV header
    csv_writer = csv.writer(out_file)
    if ssim == False and vmaf == False:
        csv_header = ['NO', 'SEQ', 'BR', 'PSNR_Y', 'PSNR_U', 'PSNR_V', 'FPS', 'CLASS']
        class_index = ENTRY_ONLY_PSNR - 1
    else:
        csv_header = ['NO', 'SEQ', 'BR', 'PSNR_Y', 'PSNR_U', 'PSNR_V', 'SSIM_Y', 'SSIM_U', 'SSIM_V', 'VMAF', 'FPS', 'CLASS']
        class_index = ENTRY_SSIM_VMAF - 1
    csv_writer.writerow(csv_header)
    
    # Write each result item
    for index in range(MAX_INDEX):
        if(out_list[index][0] == -1):
            return
        out_list[index][class_index] = "None" if class_list == None else class_list[index]
        print(out_list[index])
        csv_writer.writerow(out_list[index])
        index = index + 1
    
    out_file.close()

#out_list = collect_info("d:\\Streams\\videocore_python\\videocore\\h264-hardware-encoder-normal\\ippp_cbr\\TASK_RESULT.log", "videocore", True, False)
#print_out_result("d:\\Streams\\videocore_python\\videocore\\h264-hardware-encoder-normal\\ippp_cbr\\FORMAT_RESULT.csv", out_list, True, False)