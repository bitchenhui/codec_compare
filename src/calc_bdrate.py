#!/usr/bin/env python
# -*- coding: utf-8 -*-
# calculate bdrate and speed-up ratio
# calc_all_bdrate(anchor_log, test_log, dst_path, scene):
# inputs: anchor_log path, test_log path , dst_path and scene
# (anchor_log and test_log should be csv file)
# outputs: formatted csv file, dst_path/scene.csv
# ================================================================
import os
import math
import csv
import sys
import collections

def pchipend(h1, h2, del1, del2):
    d = ((2 * h1 + h2) * del1 - h1 * del2) / (h1 + h2)
    if (d * del1 < 0):
        d = 0
    elif ((del1 * del2 < 0)  and (abs(d) > abs(3 * del1))):
        d = 3 * del1
    return d

def bdrint(rate, dist, low, high):
    log_rate = [0,0,0,0]
    log_dist = [0,0,0,0]
    for i in range(0, 4):
        log_rate[i] = math.log(rate[3-i], 10)
        log_dist[i] = dist[3 - i]
    H = [0,0,0]
    delta = [0,0,0]
    for i in range(0,3):
        H[i] = log_dist[i + 1] - log_dist[i]
        delta[i] = (log_rate[i + 1] - log_rate[i]) / H[i]

    d = [0,0,0,0]
    
    d[0] = pchipend(H[0], H[1], delta[0], delta[1])
    
    for i in range(1,3):
        d[i] = (3 * H[i - 1] + 3 * H[i]) / ((2 * H[i] + H[i - 1]) / delta[i - 1] + (H[i] + 2 * H[i - 1]) / delta[i])
    d[3] = pchipend(H[2], H[1], delta[2], delta[1])
    c = [0,0,0]
    b = [0,0,0]
    for i in range(0,3):
        c[i] = (3 * delta[i] - 2 * d[i] - d[i + 1]) / H[i]
        b[i] = (d[i] - 2 * delta[i] + d[i + 1]) / (H[i] * H[i])
    result = 0
    
    for i in range(0,3):
        s0 = log_dist[i]
        s1 = log_dist[i + 1]
        
        s0 = max(s0, low)
        s0 = min(s0, high)
        
        s1 = max(s1, low)
        s1 = min(s1, high)

        s0 = s0 - log_dist[i]
        s1 = s1 - log_dist[i]
        
        if (s1 > s0):
            result = result + (s1 - s0) * log_rate[i]
            result = result + (s1 * s1 - s0 * s0) * d[i] / 2
            result = result + (s1 * s1 * s1 - s0 * s0 * s0) * c[i] / 3
            result = result + (s1 * s1 * s1 * s1 - s0 * s0 * s0 * s0) * b[i] / 4
    bdrint = result
    return bdrint

def c_psnr(input,label):
    return (6 * float(input[label['Y-PSNR']]) + float(input[label['U-PSNR']]) + float(input[label['V-PSNR']])) / 8

def c_ssim(input,label):
    return (6 * float(input[label['Y-SSIM']]) + float(input[label['U-SSIM']]) + float(input[label['V-SSIM']])) / 8

def bdrate(rateA, distA, rateB, distB):
    minPSNR = max(min(distA), min(distB))
    maxPSNR = min(max(distA), max(distB))
    vA = bdrint(rateA, distA, minPSNR, maxPSNR)
    vB = bdrint(rateB, distB, minPSNR, maxPSNR)
    avg = (vB - vA) / (maxPSNR - minPSNR)
    bdrate = math.pow(10, avg) - 1
    return bdrate

def get_index(type="psnr"):
    index = dict()
    index["SEQ"] = 1
    index["BR"] = 2
    index["Y-PSNR"] = 3
    index["U-PSNR"] = 4
    index["V-PSNR"] = 5
    if type == "all":
        index["Y-SSIM"] = 6
        index["U-SSIM"] = 7
        index["V-SSIM"] = 8
        index["VMAF"] = 9
        index["FPS"] = 10
        index["CLASS"] = 11
        index["COLNUM"] = 36
    elif type == "psnr":
        index["FPS"] = 6
        index["CLASS"] = 7
        index["COLNUM"] = 20
    return index

def calc_all_bdrate(anchor_log, test_log, dst_path, scene):
    print("--------------------START calc_all_bitrate-----------------------------")
    print("anchor_log:" + anchor_log)
    print("test_log:" + test_log)

    anchor_csv = open(anchor_log, "r")
    test_csv = open(test_log, "r")

    anchor_data = list(csv.reader(anchor_csv))
    test_data = list(csv.reader(test_csv))
    f_res = os.path.join(dst_path, scene + ".csv")
    print("dst_file:" + f_res)
    rate_anchor = rate_test = dist_anchor = dist_test = [0, 0, 0, 0]
    if (os.path.exists(f_res)):
        try:
            os.remove(str(f_res))
        except:
            print("failed to remove {}, please close this file and run scripts again!".format(f_res))
            return

    if (len(anchor_data) != len(test_data)):
        print("anchor and test log mismatch!")
        return

    if (len(anchor_data) % 4 != 1 or len(anchor_data) < 2):
        print("attention, the data may be incomplete!")

    type = "psnr" if len(anchor_data[0]) == 8 else "all"
    print("type=" + type)
    entries = (len(anchor_data) - 1)
    label = get_index(type)

    csv_line = [""] * label["COLNUM"]
    class_dict = collections.OrderedDict()  
    with open(f_res, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        if type == "all":
            writer.writerow(["Class", "Sequences", "kbps", "Y-PSNR", "U-PSNR", "V-PSNR","C-PSNR","Y-SSIM", "U-SSIM", "V-SSIM","C-SSIM", "VMAF","EncFps", "",\
                "kbps", "Y-PSNR", "U-PSNR", "V-PSNR","C-PSNR","Y-SSIM", "U-SSIM", "V-SSIM","C-SSIM", "VMAF","EncFps", "",\
                "Y-BDPSNR", "U-BDPSNR", "V-BDPSNR", "C-BDPSNR", "Y-BDSSIM", "U-BDSSIM" , "V-BDSSIM", "C-BDSSIM", "VMAF", "SPEED-UP"])
        elif type == "psnr":
            writer.writerow(["Class","Sequences", "kbps", "Y-PSNR", "U-PSNR", "V-PSNR","C-PSNR","EncFps", "", \
                "kbps", "Y-PSNR", "U-PSNR", "V-PSNR","C-PSNR", "EncFps","", \
                "Y-BDPSNR", "U-BDPSNR", "V-BDPSNR", "C-BDPSNR", "SPEED-UP"])

        YBDPSNR_SUM = UBDPSNR_SUM = VBDPSNR_SUM = CBDPSNR_SUM = SPEEDUP_SUM = 0
        YBDSSIM_SUM = UBDSSIM_SUM = VBDSSIM_SUM = CBDSSIM_SUM = VMAF_SUM = 0
        for index in range(1, len(anchor_data), 4):
            rate_anchor = [float(anchor_data[index][label['BR']]), float(anchor_data[index+1][label['BR']]), float(anchor_data[index+2][label['BR']]), float(anchor_data[index+3][label['BR']])]
            rate_test = [float(test_data[index][label['BR']]), float(test_data[index+1][label['BR']]), float(test_data[index+2][label['BR']]), float(test_data[index+3][label['BR']])]
            # calculate Y-BD-PSNR
            dist_anchor = [float(anchor_data[index][label['Y-PSNR']]), float(anchor_data[index+1][label['Y-PSNR']]), float(anchor_data[index+2][label['Y-PSNR']]), float(anchor_data[index+3][label['Y-PSNR']])]
            dist_test = [float(test_data[index][label['Y-PSNR']]), float(test_data[index+1][label['Y-PSNR']]), float(test_data[index+2][label['Y-PSNR']]), float(test_data[index+3][label['Y-PSNR']])]
            tmpbdrate_y = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
            Y_BDPSNR = format(tmpbdrate_y,".2%")
            YBDPSNR_SUM += tmpbdrate_y
                
            # calculate U-BD-PSNR
            dist_anchor = [float(anchor_data[index][label['U-PSNR']]), float(anchor_data[index+1][label['U-PSNR']]), float(anchor_data[index+2][label['U-PSNR']]), float(anchor_data[index+3][label['U-PSNR']])]
            dist_test = [float(test_data[index][label['U-PSNR']]), float(test_data[index+1][label['U-PSNR']]), float(test_data[index+2][label['U-PSNR']]), float(test_data[index+3][label['U-PSNR']])]
            tmpbdrate_u = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
            U_BDPSNR = format(tmpbdrate_u, ".2%")
            UBDPSNR_SUM += tmpbdrate_u

            # calculate U-BD-PSNR
            dist_anchor = [float(anchor_data[index][label['V-PSNR']]), float(anchor_data[index+1][label['V-PSNR']]), float(anchor_data[index+2][label['V-PSNR']]), float(anchor_data[index+3][label['V-PSNR']])]
            dist_test = [float(test_data[index][label['V-PSNR']]), float(test_data[index+1][label['V-PSNR']]), float(test_data[index+2][label['V-PSNR']]), float(test_data[index+3][label['V-PSNR']])]
            tmpbdrate_v = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
            V_BDPSNR = format(tmpbdrate_v,".2%")
            VBDPSNR_SUM += tmpbdrate_v

            #calculate combined BD-PSNR
            dist_anchor = [c_psnr(anchor_data[index],label), c_psnr(anchor_data[index+1],label), c_psnr(anchor_data[index+2],label), c_psnr(anchor_data[index+3],label)]
            dist_test = [c_psnr(test_data[index],label), c_psnr(test_data[index+1],label), c_psnr(test_data[index+2],label), c_psnr(test_data[index+3],label)]
            tmpbdrate_c = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
            C_BDPSNR = format(tmpbdrate_c,".2%")
            CBDPSNR_SUM += tmpbdrate_c

            cur_class = anchor_data[index][label['CLASS']]
            if  not (cur_class in class_dict):
                class_dict[cur_class] = [0 for i in range(11)]
            #y-psnr, u-psnr, v-psnr, c-psnr, y-ssim, u-ssim, v-ssim, c-ssim, vmaf, speed-sum, entries
            class_dict[cur_class][0] += tmpbdrate_y
            class_dict[cur_class][1] += tmpbdrate_u
            class_dict[cur_class][2] += tmpbdrate_v
            class_dict[cur_class][3] += tmpbdrate_c


            if type == "all":
                # calculate Y-BD-PSNR
                dist_anchor = [float(anchor_data[index][label['Y-SSIM']]), float(anchor_data[index+1][label['Y-SSIM']]), float(anchor_data[index+2][label['Y-SSIM']]), float(anchor_data[index+3][label['Y-SSIM']])]
                dist_test = [float(test_data[index][label['Y-SSIM']]), float(test_data[index+1][label['Y-SSIM']]), float(test_data[index+2][label['Y-SSIM']]), float(test_data[index+3][label['Y-SSIM']])]
                tmpbdrate_y = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
                Y_BDSSIM = format(tmpbdrate_y,".2%")
                YBDSSIM_SUM += tmpbdrate_y

                # calculate U-BD-SSIM
                dist_anchor = [float(anchor_data[index][label['U-SSIM']]), float(anchor_data[index+1][label['U-SSIM']]), float(anchor_data[index+2][label['U-SSIM']]), float(anchor_data[index+3][label['U-SSIM']])]
                dist_test = [float(test_data[index][label['U-SSIM']]), float(test_data[index+1][label['U-SSIM']]), float(test_data[index+2][label['U-SSIM']]), float(test_data[index+3][label['U-SSIM']])]
                tmpbdrate_u = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
                U_BDSSIM = format(tmpbdrate_u, ".2%")
                UBDSSIM_SUM += tmpbdrate_u

                # calculate U-BD-SSIM
                dist_anchor = [float(anchor_data[index][label['V-SSIM']]), float(anchor_data[index+1][label['V-SSIM']]), float(anchor_data[index+2][label['V-SSIM']]), float(anchor_data[index+3][label['V-SSIM']])]
                dist_test = [float(test_data[index][label['V-SSIM']]), float(test_data[index+1][label['V-SSIM']]), float(test_data[index+2][label['V-SSIM']]), float(test_data[index+3][label['V-SSIM']])]
                tmpbdrate_v = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
                V_BDSSIM = format(tmpbdrate_v,".2%")
                VBDSSIM_SUM += tmpbdrate_v

                #calculate combined BD-SSIM
                dist_anchor = [c_ssim(anchor_data[index],label), c_ssim(anchor_data[index+1],label), c_ssim(anchor_data[index+2],label), c_ssim(anchor_data[index+3],label)]
                dist_test = [c_ssim(test_data[index],label), c_ssim(test_data[index+1],label), c_ssim(test_data[index+2],label), c_ssim(test_data[index+3],label)]
                tmpbdrate_c = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
                C_BDSSIM = format(tmpbdrate_c,".2%")
                CBDSSIM_SUM += tmpbdrate_c

                # calculate VMAF
                dist_anchor = [float(anchor_data[index][label['VMAF']]), float(anchor_data[index+1][label['VMAF']]), float(anchor_data[index+2][label['VMAF']]), float(anchor_data[index+3][label['VMAF']])]
                dist_test = [float(test_data[index][label['VMAF']]), float(test_data[index+1][label['VMAF']]), float(test_data[index+2][label['VMAF']]), float(test_data[index+3][label['VMAF']])]
                tmpbdrate_vmaf = bdrate(rate_anchor, dist_anchor, rate_test, dist_test)
                BDVMAF = format(tmpbdrate_vmaf,".2%")
                VMAF_SUM += tmpbdrate_vmaf

                class_dict[cur_class][4] += tmpbdrate_y
                class_dict[cur_class][5] += tmpbdrate_u
                class_dict[cur_class][6] += tmpbdrate_v
                class_dict[cur_class][7] += tmpbdrate_c
                class_dict[cur_class][8] += tmpbdrate_vmaf

            for i in range(4):
                line = i + index
                tmpspeedup = float(test_data[line][label["FPS"]])/float(anchor_data[line][label["FPS"]])
                SPEEDUP_SUM += tmpspeedup
                tmpspeedup = round(tmpspeedup, 2)
                class_dict[cur_class][9] += tmpspeedup
                class_dict[cur_class][10] += 1 
                if type == "all":
                    if i == 0:
                        csv_line = [anchor_data[line][label["CLASS"]], anchor_data[line][label["SEQ"]], round(float(anchor_data[line][label["BR"]]), 2), \
                            round(float(anchor_data[line][label["Y-PSNR"]]), 2), round(float(anchor_data[line][label["U-PSNR"]]), 2), round(float(anchor_data[line][label["V-PSNR"]]), 2), round(c_psnr(anchor_data[line],label), 2), \
                            round(float(anchor_data[line][label["Y-SSIM"]]), 2), round(float(anchor_data[line][label["U-SSIM"]]), 2), round(float(anchor_data[line][label["V-SSIM"]]), 2), round(c_ssim(anchor_data[line],label), 2), \
                            round(float(anchor_data[line][label["VMAF"]]), 2), round(float(anchor_data[line][label["FPS"]]), 2),'', \
                            round(float(test_data[line][label["BR"]]), 2),\
                            round(float(test_data[line][label["Y-PSNR"]]), 2), round(float(test_data[line][label["U-PSNR"]]), 2), round(float(test_data[line][label["V-PSNR"]]), 2), round(c_psnr(test_data[line],label), 2), \
                            round(float(test_data[line][label["Y-SSIM"]]), 2), round(float(test_data[line][label["U-SSIM"]]), 2), round(float(test_data[line][label["V-SSIM"]]), 2), round(c_ssim(test_data[line],label), 2), \
                            round(float(test_data[line][label["VMAF"]]), 2), round(float(test_data[line][label["FPS"]]), 2),'', \
                            Y_BDPSNR, U_BDPSNR, V_BDPSNR, C_BDPSNR, Y_BDSSIM, U_BDSSIM, V_BDSSIM, C_BDSSIM, BDVMAF, tmpspeedup]
                    else:
                        csv_line = [anchor_data[line][label["CLASS"]], anchor_data[line][label["SEQ"]], round(float(anchor_data[line][label["BR"]]), 2), \
                            round(float(anchor_data[line][label["Y-PSNR"]]), 2), round(float(anchor_data[line][label["U-PSNR"]]), 2), round(float(anchor_data[line][label["V-PSNR"]]), 2), round(c_psnr(anchor_data[line],label), 2), \
                            round(float(anchor_data[line][label["Y-SSIM"]]), 2), round(float(anchor_data[line][label["U-SSIM"]]), 2), round(float(anchor_data[line][label["V-SSIM"]]), 2), round(c_ssim(anchor_data[line],label), 2), \
                            round(float(anchor_data[line][label["VMAF"]]), 2), round(float(anchor_data[line][label["FPS"]]), 2),'', \
                            round(float(test_data[line][label["BR"]]), 2), \
                            round(float(test_data[line][label["Y-PSNR"]]), 2), round(float(test_data[line][label["U-PSNR"]]), 2), round(float(test_data[line][label["V-PSNR"]]), 2), round(c_psnr(test_data[line],label), 2), \
                            round(float(test_data[line][label["Y-SSIM"]]), 2), round(float(test_data[line][label["U-SSIM"]]), 2), round(float(test_data[line][label["V-SSIM"]]), 2), round(c_ssim(test_data[line],label), 2), \
                            round(float(test_data[line][label["VMAF"]]), 2), round(float(test_data[line][label["FPS"]]), 2),'', \
                            '', '', '', '', '', '', '', '', '', tmpspeedup]
                else:
                    if i == 0:
                        csv_line = [anchor_data[line][label["CLASS"]], anchor_data[line][label["SEQ"]], round(float(anchor_data[line][label["BR"]]), 2), \
                            round(float(anchor_data[line][label["Y-PSNR"]]), 2), round(float(anchor_data[line][label["U-PSNR"]]), 2), round(float(anchor_data[line][label["V-PSNR"]]), 2), \
                            round(c_psnr(anchor_data[line],label), 2), round(float(anchor_data[line][label["FPS"]]), 2),'', \
                            round(float(test_data[line][label["BR"]]), 2), \
                            round(float(test_data[line][label["Y-PSNR"]]), 2), round(float(test_data[line][label["U-PSNR"]]), 2), round(float(test_data[line][label["V-PSNR"]]), 2), \
                            round(c_psnr(test_data[line],label), 2), round(float(test_data[line][label["FPS"]]), 2),'', \
                            Y_BDPSNR, U_BDPSNR, V_BDPSNR, C_BDPSNR, tmpspeedup]
                    else:
                        csv_line = [anchor_data[line][label["CLASS"]], anchor_data[line][label["SEQ"]], round(float(anchor_data[line][label["BR"]]), 2), \
                            round(float(anchor_data[line][label["Y-PSNR"]]), 2), round(float(anchor_data[line][label["U-PSNR"]]), 2), round(float(anchor_data[line][label["V-PSNR"]]), 2), \
                            round(c_psnr(anchor_data[line],label), 2), round(float(anchor_data[line][label["FPS"]]), 2),'', \
                            round(float(test_data[line][label["BR"]]), 2), \
                            round(float(test_data[line][label["Y-PSNR"]]), 2), round(float(test_data[line][label["U-PSNR"]]), 2), round(float(test_data[line][label["V-PSNR"]]), 2), \
                            round(c_psnr(test_data[line],label), 2), round(float(test_data[line][label["FPS"]]), 2),'', \
                            '', '', '', '', tmpspeedup]
                writer.writerow(csv_line)
        #write class average info
        for key, value in class_dict.items():
            if type == "all":
                csv_line = ['Average', key, '', '', '', '', '', '', '', '', '','', '', '','','', '', '', '', '', '','', '', '','','', \
                    format((value[0] * 4 / value[10]), '.2%'), format((value[1] * 4 / value[10]), '.2%'), format((value[2] * 4 / value[10]), '.2%'),format((value[3] * 4 / value[10]), '.2%'), \
                    format((value[4] * 4 / value[10]), '.2%'), format((value[5] * 4 / value[10]), '.2%'), format((value[6] * 4 / value[10]), '.2%'),format((value[7] * 4 / value[10]), '.2%'), \
                    format((value[8] * 4 / value[10]), '.2%'), round(value[9] / value[10], 2)]
            else:
                csv_line = ['Average', key, '', '', '', '', '', '', '', '', '','', '', '','','',format((value[0] * 4 / value[10]), '.2%'), \
                    format((value[1] * 4 / value[10]), '.2%'), format((value[2] * 4 / value[10]), '.2%'),format((value[3] * 4 / value[10]), '.2%'),round(value[9] / value[10], 2)]
            writer.writerow(csv_line)

        #write average info
        if type == "all":
            csv_line = ['Average', 'ALL', '', '', '', '', '', '', '', '', '','', '', '','','', '', '', '', '', '','', '', '','','', \
                format((YBDPSNR_SUM * 4 / entries), '.2%'), format((UBDPSNR_SUM * 4 / entries), '.2%'), format((VBDPSNR_SUM * 4 / entries), '.2%'),format((CBDPSNR_SUM * 4 / entries), '.2%'), \
                format((YBDSSIM_SUM * 4 / entries), '.2%'), format((UBDSSIM_SUM * 4 / entries), '.2%'), format((VBDSSIM_SUM * 4 / entries), '.2%'),format((CBDSSIM_SUM * 4 / entries), '.2%'), \
                format((VMAF_SUM * 4 / entries), '.2%'), round(SPEEDUP_SUM / entries, 2)]
        else:
            csv_line = ['Average', 'ALL', '', '', '', '', '', '', '', '', '','', '', '','','',format((YBDPSNR_SUM * 4 / entries), '.2%'), \
                format((UBDPSNR_SUM * 4 / entries), '.2%'), format((VBDPSNR_SUM * 4 / entries), '.2%'),format((CBDPSNR_SUM * 4 / entries), '.2%'),round(SPEEDUP_SUM / entries, 2)]
        writer.writerow(csv_line)
    print("------------------------FINISHED---------------------------------------")
    return f_res, type

if __name__ == '__main__':
    calc_all_bdrate(sys.argv[1], sys.argv[2], "F:\\camera_test", "camera")