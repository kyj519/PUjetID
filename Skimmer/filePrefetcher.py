#!/usr/bin/env python
import os,sys
import ROOT
import hashlib
import argparse
import subprocess

parser = argparse.ArgumentParser("")
parser.add_argument('--file',             type=str)
parser.add_argument('--targetFolder',       type=str ,default="/gv0/Users/yeonjoon/tmp2")

args = parser.parse_args()
fname = args.file
targetFolder = args.targetFolder
rndchars =  "long_cache-id%d-%s" % (os.getuid(), hashlib.sha1(fname).hexdigest())
localfile = "%s/%s-%s.root" % (targetFolder, os.path.basename(fname).replace(".root", ""), rndchars)
os.system("xrdcp -f %s %s" % (fname, localfile))
out = subprocess.Popen(['xrdcp', '-f', fname, localfile], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout,stderr = out.communicate()
print("----STDOUT----\n")
print(stdout)
print("----STDERR----\n")
print(stderr)