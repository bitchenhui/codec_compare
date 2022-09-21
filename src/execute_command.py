# -*- coding: utf-8 -*-
# ================================================================

import os
import subprocess

from util.log import Log

def execute_cmd(cmd):
  """Start a process to execute input command.

  Arg:
    cmd: string
  
  Return:
    bool
  """
  try:
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p != None and p.stdout != None:
      for line in p.stdout.readlines():
        print(line)
        if type(line) is bytes:
          line = line.decode("utf-8")
        Log.instance().info(line.replace("\n", ""))
    if p != None and p.stderr != None:
      for line in p.stderr.readlines():
        if type(line) is bytes:
          line = line.decode("utf-8")
        Log.instance().error(Line)
    rt = p.wait()
    if rt < 0:
      print(rt)
      return False
  except IOError:
    Log.instance().error("Failed execution: {}".format(cmd))
    return False
    
  return True