"""
##/usr/bin/python
mct codec evalution tools
"""

import sys
import subprocess
import os
import re
import math
import time
import datetime

conf_file = './conf/config.conf'
config_max_lines = 10000



def is_operation(oper):
    if oper == '+' or oper == '-' or oper == '*' or oper == '/':
        return True
    else:
        return False

#def is_encoder(SRC_NAME)
	
	
	
	
class VbvVal(object):
    vbv_bufsize = 0
    vbv_maxrate = 0
    bitrate_unit = 0

def is_equal(oper):
    if oper == '=':
        return True
    else:
        return False


def is_comma(oper):
    if oper == ',':
        return True
    else:
        return False

def mixed_operation (exp):
    exp_list = list(exp)
    print "exp_list", exp_list
    val = ''
    behavor_list = []
    i = 0
    length = len(exp_list)
    for item in exp_list:
        if is_equal(item):
            val += item
            behavor_list.append(val)
            val = ''
            i += 1
            continue
        if is_operation(item) or is_comma(item):
            behavor_list.append(val)
            behavor_list.append(item)
            val = ''
        else:
            val += item
        if (i == length - 1):
            behavor_list.append(val)
        i += 1
    print behavor_list
    return behavor_list


def parse_conf(str_char):
    """
    @ parse_conf() used parse "./conf/config.conf'
    """
    confFp = open(conf_file, "r")
    i_count = 0
    val = ''
    while(i_count < config_max_lines):
        conf_line = confFp.readline()
        if not conf_line:
            break
        iscommon = re.search('##', conf_line)
        if (iscommon):
            continue
        str_char = str_char + '.*'
        isstr_char = re.search(str_char, conf_line)
        if (isstr_char):
            isstr_char = isstr_char.group(0)
            val = re.split('\:  ', isstr_char)
            val = ''.join(val[1])
            val = val.lstrip()
	    ##print "val", val
        i_count += 1
    val = val.strip()
    return val
    confFp.close()


def calcul_vbv_val(exp_list, vbv_val):
    length = len(exp_list)
    ax = 0
    bx = 0
    cx = 0
    i = 0
    while (i < len(exp_list)):
        if (exp_list[i] == 'UNIT='):
            cx = float(exp_list[i+1])
        if (exp_list[i] == 'VBV_BUFSIZE='):
            ax = float(exp_list[i+1])
        if (exp_list[i] == 'VBV_MAXRATE='):
            bx = float(exp_list[i+1])
        i += 1
#    if (ax == 0 or bx == 0):
#        print "may errror!"
#    else:
        vbv_val.vbv_bufsize = float(ax )
        vbv_val.vbv_maxrate = float(bx )
        vbv_val.bitrate_unit = float(cx )
