#!/usr/bin/env python
import os,sys
import ROOT
import hashlib
import signal
import argparse
import shutil
from io import StringIO 
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

def nocondorRun(jobN):
    import htcondor
    if os.path.isdir('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck'): shutil.rmtree('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck')
    os.mkdir('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck')
    os.mkdir('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job')
    
    for i in range(jobN):
        fromindex = int((FileNumber-1)/(jobN-1))*i
        toindex = int((FileNumber-1)/(jobN-1))*(i+1)-1
        if i == jobN-1: toindex = FileNumber-1
        f = open('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job/job_%s.sh'%i,"w+")
        f.write("#!/bin/bash\n")
        f.write("python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/validfileCheck.py --fromidx %d --toidx %d --condorRun 1" % (fromindex, toindex))
        f.close
        os.system('chmod 755 %s' % '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job/job_%s.sh' % i)
        
        submit_dic = {"executable": '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job/job_%s.sh' % i,
        "universe":"vanilla",
        "request_cpus":1,
        "output": '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job%s.out' % i,
        "error": '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/job%s.err' % i,
        "getenv":"True",
        "should_transfer_files":"YES",
        "when_to_transfer_output" : "ON_EXIT",
        "concurrency_limits" : "n1000.yeonjoon"}
        sub = htcondor.Submit(submit_dic)
        schedd = htcondor.Schedd()
        submit_result = schedd.submit(sub)
        
def condorRun(fromidx,toidx):
    corrfile = []

    for i in range(fromidx,toidx+1):
        file = filelist[i].strip('\n')
        isZombie = False
        f = ROOT.TFile.Open(file,'r')
        print(file)
        if f:
            if f.IsZombie(): corrfile.append(file)
            if not f.GetListOfKeys().Contains("Events"): corrfile.append(file)
            evt = f.Get("Events")
            if not str(evt.Draw("((nMuon>=2 && Sum$(Muon_pt>15.)>=1) || (nElectron>=2 && Sum$(Electron_pt>20.)>=1)) && (nJet>=1)")) == 'None': corrfile.append(file)

            f.Close()
        else:
            corrfile.append(file)


        if i % 3 == 0:
            print("%s file checked, %.2f percent proceed" % (i, float(i)/float(FileNumber)*100.0))
    
    rst = open('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filecheck/result.txt','a')
    for file in corrfile:
        rst.write(file)
        rst.write('\n')
    rst.close()
    
        
  
parser = argparse.ArgumentParser("")
parser.add_argument('--fromidx',default=0,	type=int)
parser.add_argument('--toidx',default=0,	type=int)
parser.add_argument('--condorRun',type = int, default = 0)
args        = parser.parse_args()
fromidx = args.fromidx
toidx = args.toidx
isCondor = args.condorRun
nanoPath = '/gv0/Users/yeonjoon/tmp2'

filelist = open('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/Nanolist.txt','r').readlines()
FileNumber = len(filelist)
print(isCondor)
if isCondor:
    condorRun(fromidx, toidx)
else:
    nocondorRun(200)
