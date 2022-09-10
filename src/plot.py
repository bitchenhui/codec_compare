"""
#!/usr/bin/python
"""
import os
import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import copy
import bjontegaard_metric
import parse_conf
## global val
Result_Bdrate = './output/' + 'bd_rate.txt'
result_data = './output/' + 'result.txt'
class PlotAttr(object):
    """
    polt attr for curve
    """
    X_label = ''
    Y_lable = ''
    Title = ''
    Text = ''
    Savefig = ''
    min_xlim = 0
    max_xlim = 0
    min_ylim = 0
    max_ylim = 0
#
#    color map set
#    'b'         blue   -----   slateblue  ----  o 
#    'g'         green  -----   springgreen ---- >
#    'r'         red    -----   darkred     ---- <
#    'c'         cyan   -----   teal       ----  s  
#    'm'         magenta-----   purple     ----  *
#    'y'         yellow ----    gold      -----  x
#    'k'         black  ----    grey      -----  D
#
    
c1_line_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'deeppink', 'slateblue',\
                  'springgreen', 'darkred', 'teal', 'purple', 'gold', 'grey', 'hotpink']
c2_line_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'deeppink', 'slateblue',\
                  'springgreen', 'darkred', 'teal', 'purple', 'gold', 'grey', 'hotpink']
marker_colors = ['g', 'r', 'c', 'm', 'y', 'k', 'deeppink', 'b', 'g', 'r', 'c', 'm', 'y', 'k', 'deeppink', 'b']
marker_skyles = ['o', '>', '<', 's', '*', 'x', 'D', 'p', 'o', '>', '<', 's', '*', 'x', 'D', 'p']
class ColorAttr(object):
    """
    color attr for compare two curves
    """
    c1_line_color = ''
    c2_line_color = ''
    marker_color = ''
    marker_skyle = ''
class CurveAttr(object):
    """
    a curve attr member
    """
    list_x = []
    list_y = []
    curve_name = ''
def select_colors(i, colors_attr):
    """
    select_colors
    """
    colors_attr.c1_line_color = c1_line_colors[i]
    colors_attr.c2_line_color = c2_line_colors[i]
    colors_attr.marker_color = marker_colors[i]
    colors_attr.marker_skyle = marker_skyles[i]
curve_vmaf_list = []
curve_psnr_list = []
curve_ssim_list = []
curve_speed_list = []
def print_curve_list(list_bitrate, list_vmafscore, list_psnr, list_speed):
    """
    print_curve_list
    """
    if (len(list_bitrate)>0):
        print "list_bitrate:", list_bitrate
    if (len(list_vmafscore)>0):
        print "list_vmafscore:", list_vmafscore
    if (len(list_psnr)>0):
        print "list_psnr", list_psnr
    if (len(list_speed)):
        print "list_speed", list_speed
def push_curve_list(curve_name, list_bitrate, list_vmafscore, list_psnr, list_ssim, list_speed):
    """
    push_curve_list
    """
    vmaf_curve_attr = CurveAttr()
    if (len(list_bitrate)>0 and len(list_vmafscore)>0):
        vmaf_curve_attr.list_x = copy.copy(list_bitrate)
        vmaf_curve_attr.list_y = copy.copy(list_vmafscore)
        vmaf_curve_attr.curve_name = curve_name
        curve_vmaf_list.append(vmaf_curve_attr)
    psnr_curve_attr = CurveAttr()
    if(len(list_bitrate)>0 and len(list_psnr)>0):
        psnr_curve_attr.list_x = copy.copy(list_bitrate)
        psnr_curve_attr.list_y = copy.copy(list_psnr)
        psnr_curve_attr.curve_name = curve_name
        curve_psnr_list.append(psnr_curve_attr)
    ssim_curve_attr = CurveAttr()
    if(len(list_bitrate)>0 and len(list_ssim)>0):
        ssim_curve_attr.list_x = copy.copy(list_bitrate)
        ssim_curve_attr.list_y = copy.copy(list_ssim)
        ssim_curve_attr.curve_name = curve_name
        curve_ssim_list.append(ssim_curve_attr)
    speed_curve_attr = CurveAttr()
    if(len(list_bitrate)>0 and len(list_speed)>0):
        speed_curve_attr.list_x = copy.copy(list_bitrate)
        speed_curve_attr.list_y = copy.copy(list_speed)
        speed_curve_attr.curve_name = curve_name
        curve_speed_list.append(speed_curve_attr)
def set_plt_attr(plot_attrs):
    """
    set_plt_attr
    """
    plt.title("%s" % plot_attrs.Title)
    plt.xlabel("%s" % plot_attrs.X_label)
    plt.ylabel("%s" % plot_attrs.Y_label)
    plt.ylim(plot_attrs.min_ylim, plot_attrs.max_ylim)
    plt.xlim(plot_attrs.min_xlim, plot_attrs.max_xlim)
def excute_drow(x_t, y_t, plot_attrs):
    """
    @drow the plot
    """
    plt.legend(loc = 'best')
    ax = plt.gca()
    y_ticks = np.arange(plot_attrs.min_ylim, plot_attrs.max_ylim, y_t)
    ax.yaxis.grid()
    ax.set_yticks(y_ticks)
    x_ticks = np.arange(plot_attrs.min_xlim, plot_attrs.max_xlim, x_t)
    ax.xaxis.grid()
    ax.set_xticks(x_ticks)
    plt.savefig(plot_attrs.Savefig, dpi=200)
    plt.show()
   
def plot_curves_figures():
    """
    draw vmaf curve
    """
    sizex = 24
    sizey = 15
    plot_attrs = PlotAttr()
    plot_attrs.Title = 'BitRate--VamfScore &Curves'
    plot_attrs.X_label = 'Bitrate(kbps)'
    plot_attrs.Y_label = 'VamfScore'
    plot_attrs.max_ylim = 100
    plot_attrs.max_xlim = 6000
    plot_attrs.Savefig = './output/BitRate--VamfScore.png'
    plt.figure(figsize = (sizex, sizey))
    set_plt_attr(plot_attrs)
    tmp_colors_attr = ColorAttr()
    i = 0
    while(i < len(curve_vmaf_list)):
        select_colors(i, tmp_colors_attr)
        print "vmaf", i, "list:", curve_vmaf_list[i].list_y
        if(i < len(curve_vmaf_list)/2):
            plt.plot(curve_vmaf_list[i].list_x, curve_vmaf_list[i].list_y, 
                label=curve_vmaf_list[i].curve_name, linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        else:
            plt.plot(curve_vmaf_list[i].list_x, curve_vmaf_list[i].list_y, 
                label=curve_vmaf_list[i].curve_name, linestyle='--', linewidth=4, 
                color=tmp_colors_attr.c2_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        i += 1
    excute_drow(500, 10, plot_attrs)
    ## draw psnr curve
    plot_attrs.Title = 'BitRate--PSNR &Curves'
    plot_attrs.X_label = 'Bitrate(kbps)'
    plot_attrs.Y_label = 'PSNR/dB'
    plot_attrs.max_ylim = 50
    plot_attrs.min_ylim = 20
    plot_attrs.max_xlim = 6000
    plot_attrs.Savefig = './output/BitRate--PSNR.png'
    plt.figure(figsize = (sizex, sizey))
    set_plt_attr(plot_attrs)
    tmp_colors_attr = ColorAttr()
    i = 0
    while(i < len(curve_psnr_list)):
        select_colors(i, tmp_colors_attr)
        print "psnr:", i, "list:", curve_psnr_list[i].list_y, curve_psnr_list[i].curve_name
        if(i < len(curve_psnr_list)/2):
            plt.plot(curve_psnr_list[i].list_x, curve_psnr_list[i].list_y, 
                label=curve_psnr_list[i].curve_name, linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        else:
            plt.plot(curve_psnr_list[i].list_x, curve_psnr_list[i].list_y, 
                label=curve_psnr_list[i].curve_name, linestyle='--', linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        i += 1
    excute_drow(500, 5, plot_attrs)
    ## draw ssim curve    
    plot_attrs.Title = 'BitRate--SSIM &Curves'
    plot_attrs.X_label = 'Bitrate(kbps)'
    plot_attrs.Y_label = 'SSIM'
    plot_attrs.max_ylim = 1
    plot_attrs.min_ylim = 0
    plot_attrs.max_xlim = 6000
    plot_attrs.Savefig = './output/BitRate--SSIM.png'
    plt.figure(figsize = (sizex, sizey))
    set_plt_attr(plot_attrs)
    tmp_colors_attr = ColorAttr()
    i = 0
    while(i < len(curve_ssim_list)):
        select_colors(i, tmp_colors_attr)
        print "ssim:", i, "list:", curve_ssim_list[i].list_y, curve_ssim_list[i].curve_name
        #print curve_ssim_list[i].list_x
        if(i < len(curve_ssim_list)/2):
            plt.plot(curve_ssim_list[i].list_x, curve_ssim_list[i].list_y, 
                label=curve_ssim_list[i].curve_name, linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        else:
            plt.plot(curve_ssim_list[i].list_x, curve_ssim_list[i].list_y, 
                label=curve_ssim_list[i].curve_name, linestyle='--', linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        i += 1
    excute_drow(500, 0.1, plot_attrs)
    
    ## draw speed curve
    plot_attrs.Title = 'BitRate--speed &Curves'
    plot_attrs.X_label = 'Bitrate(kbps)'
    plot_attrs.Y_label = 'Speed'
    plot_attrs.min_ylim = 0
    plot_attrs.max_ylim = 100
    plot_attrs.Savefig = './output/BitRate--Speed.png'
    plt.figure(figsize = (sizex, sizey))
    set_plt_attr(plot_attrs)
    tmp_colors_attr = ColorAttr()
    i = 0
    while(i < len(curve_speed_list)):
        select_colors(i, tmp_colors_attr)
        print "speed:", i, "list:", curve_speed_list[i].list_y
        if(i < len(curve_speed_list)/2):
            plt.plot(curve_speed_list[i].list_x, curve_speed_list[i].list_y, 
                label=curve_speed_list[i].curve_name, linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        else:
            plt.plot(curve_speed_list[i].list_x, curve_speed_list[i].list_y, 
                label=curve_speed_list[i].curve_name, linestyle='--', linewidth=4, 
                color=tmp_colors_attr.c1_line_color, marker=tmp_colors_attr.marker_skyle, 
                markerfacecolor=tmp_colors_attr.marker_color, markersize=5)
        i += 1
    excute_drow(500, 20, plot_attrs)
def calculate_bd_rate(resultFp):
    """
    calculate_bd_rate
    """
    print_char = ''
    print_char0 = 'vidoe_name'
    print_char1 = 'BD-rate'
    print_char = 'Description'
    resultFp.write("| %15s | %15s | %80s |" % (print_char0, print_char1, print_char))
    resultFp.write("\n")
    conf_str = 'Enable_Vmaf'
    Enable_Vmaf = parse_conf.parse_conf(conf_str)
    print "Enable_Vmaf", Enable_Vmaf
    conf_str = 'Enable_Psnr'
    Enable_Psnr = parse_conf.parse_conf(conf_str)
    print "Enable_Psnr", Enable_Psnr
    codec_strA = 'codecA_name'
    Codec_name_A = parse_conf.parse_conf(codec_strA)
    codec_strB = 'codecB_name'
    Codec_name_B = parse_conf.parse_conf(codec_strB)
    print Codec_name_A
    print Codec_name_B
    i = 0
    while(i < len(curve_vmaf_list)/2):
        if (Enable_Psnr != '1'):
            i = len(curve_psnr_list)/2
            i += 1
            continue
        curve_name_a = curve_psnr_list[i].curve_name
        bitrate_list_a = np.array(curve_psnr_list[i].list_x)
        psnr_list_a = np.array(curve_psnr_list[i].list_y)
        curve_name_b = curve_psnr_list[i + len(curve_psnr_list) / 2].curve_name
        bitrate_list_b = np.array(curve_psnr_list[i + len(curve_psnr_list) / 2].list_x)
        psnr_list_b = np.array(curve_psnr_list[i + len(curve_psnr_list) / 2].list_y)
        curve_name = re.sub('_[0-9].*', "", curve_name_a)
        video_name_a = curve_name
        #video_name_a = re.sub('_' + Codec_name_A, "", video_name_a)
        curve_name = re.sub('_[0-9].*', "", curve_name_b)
        video_name_b = curve_name
        #video_name_b = re.sub('_' + Codec_name_B, "", video_name_b)
        print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", video_name_b
        if (Enable_Psnr != '1'):
            i = len(curve_psnr_list)/2
            print_char = '**'
            resultFp.write("| %20s | %15s |" % (print_char, print_char))
            i += 1
            continue 
        if (video_name_a != video_name_b):
            print "curves compare with \n", "A=", video_name_a, " && B=", video_name_b
        else:
            print "video name :", video_name_a
            print "psnr_list_a", psnr_list_a
            print "psnr_list_b", psnr_list_b
        print "curves maybe", "A=", video_name_a, " && B=", video_name_b
        bd_data = bjontegaard_metric.BD_RATE(bitrate_list_a, 
            psnr_list_a, bitrate_list_b, psnr_list_b)
        if (bd_data > 0):
            bd_data = str(bd_data)
            print_char = Codec_name_A + ' is better,which could save ' + bd_data + '% bitrate when PSNR is equal '   
        else:
            bd_data = abs(bd_data)
            bd_data = str(bd_data)
            print_char = Codec_name_B + ' is better,which could save ' + bd_data + '% bitrate when PSNR is equal '
        str_bd_data = str(bd_data)
        video_name_a = re.sub('_' + Codec_name_A, "", video_name_a)
        resultFp.write("| %15s | %15s | %80s |" % (video_name_a, str_bd_data, print_char))
        resultFp.write("\n")
        i += 1
    print_char0 = 'vidoe_name'
    print_char1 = 'BD-PSNR'
    print_char = 'Description'
    resultFp.write("| %15s | %15s | %80s |" % (print_char0, print_char1, print_char))
    resultFp.write("\n")
    i = 0
    while(i < len(curve_psnr_list) / 2):
        if (Enable_Psnr == '0'):
            i = len(curve_psnr_list) / 2
            i += 1
            continue
        curve_name_a = curve_psnr_list[i].curve_name
        bitrate_list_a = np.array(curve_psnr_list[i].list_x)
        psnr_list_a = np.array(curve_psnr_list[i].list_y)
        curve_name_b = curve_psnr_list[i + len(curve_psnr_list)/2].curve_name
        bitrate_list_b = np.array(curve_psnr_list[i + len(curve_psnr_list)/2].list_x)
        psnr_list_b = np.array(curve_psnr_list[i + len(curve_psnr_list) / 2].list_y)
        curve_name = re.sub('_[0-9].*', "", curve_name_a)
        video_name_a = curve_name
        curve_name = re.sub('_[0-9].*', "", curve_name_b)
        video_name_b = curve_name
        print "curves compare with \n", "A=", video_name_a, " && B=", video_name_b
        print "psnr_list_a", psnr_list_a
        print "psnr_list_b", psnr_list_b
        bd_data = bjontegaard_metric.BD_PSNR(bitrate_list_a,
            psnr_list_a, bitrate_list_b, psnr_list_b)
        if (bd_data > 0):
            bd_data = str(bd_data)
            print_char = Codec_name_B + ' is better, whose PSNR is ' + bd_data + 'dB higher than ' + Codec_name_A + ' when bitrate is equal'    
        else:
            bd_data = abs(bd_data)
            bd_data = str(bd_data)
            print_char = Codec_name_A + ' is better, whose PSNR is ' + bd_data + 'dB higher than ' + Codec_name_B + ' when bitrate is equal'
        str_bd_data = str(bd_data)
        ##print("| %20s | %15s | %40s |" % (video_name_a, str_bd_data, print_char))
        video_name_b = re.sub('_' + Codec_name_B, "", video_name_b)
        resultFp.write("| %15s | %15s | %80s |" % (video_name_b, str_bd_data, print_char))
        resultFp.write("\n")
        i += 1
    print "calculate_bd_rate end!"
def parse_result():
    """
    parse_result
    """
    resultInfoFp = open(result_data, "r")
    count = 0
    list_bitrate = []
    list_vmafscore = []
    list_psnr = []
    list_ssim = []
    list_speed = []
    curve_title = ''
    while(count < 10000):
        srcline = resultInfoFp.readline()
        if not srcline:
            #print_curve_list(list_bitrate, list_vmafscore, list_psnr, list_speed)
            push_curve_list(curve_title, list_bitrate, list_vmafscore, list_psnr, list_ssim, list_speed)
            break
        flag_title = re.search('Codec:', srcline)
        if(flag_title):
            srcline = re.split('\|', srcline)
            print "title_line:", srcline
            #print_curve_list(list_bitrate, list_vmafscore, list_psnr, list_speed)
            push_curve_list(curve_title, list_bitrate, list_vmafscore, list_psnr, list_ssim, list_speed)
            video_name = srcline[2]
            video_name = re.split('-', video_name)
            video_name = video_name[1]
            video_name = re.sub("\s+", "", video_name)
            video_name = re.sub('_[0-9].*', "", video_name)
            print video_name
            codec_type = srcline[1]
            codec_type = re.split(':', codec_type)
            codec_type = codec_type[1]
            codec_type = re.sub("\s+", "", codec_type)
            curve_title = video_name + '_' + codec_type
            print curve_title
            list_bitrate = []
            list_vmafscore = []
            list_psnr = []
            list_ssim = []
            list_speed = []
        else:
            srcline = re.split('\|', srcline)
            print "normal_line:", srcline
            list_bitrate.append(float(re.sub("\s+", "", srcline[1])))
            list_vmafscore.append(float(re.sub("\s+", "", srcline[2])))
            list_ssim.append(float(re.sub("\s+", "", srcline[3])))
            list_psnr.append(float(re.sub("\s+", "", srcline[4])))
            list_speed.append(float(re.sub("\s+", "", srcline[5])))    
        count += 1
    resultInfoFp.close()
def init_plot():
    """
    init_plot
    """
    os.system(":>%s" % Result_Bdrate)
    bdrateFp = open(Result_Bdrate, "w")
    return bdrateFp
def close_plot(bdrateFp):
    """
    close_plot
    """
    bdrateFp.close()
 
#for test code
if __name__ == '__main__':
    bdrateFp = init_plot()
    parse_result()
    plot_curves_figures()
    calculate_bd_rate(bdrateFp)
    close_plot(bdrateFp)
