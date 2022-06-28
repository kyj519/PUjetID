import os,sys
import ROOT

condor_dir = '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/condor/'
samplelist = [condor_dir + sample for sample in os.listdir(condor_dir)]
outlist = [folder + '/out' for folder in samplelist]
errlist = []
notEndinglist = []
for folder in outlist:
    filelist = [folder + "/" + file for file in os.listdir(folder)]
    for file in filelist:
        f = open(file, 'r')
        lines = f.readlines()
        isNoneerr = False
        isEnded = False
        for line in lines:
            if 'None' in line: isNoneerr = False
            if '100' in line: isEnded = False
        if isEnded: notEndinglist.append(file)
        if isNoneerr: errlist.append(file)
        f.close()

print(errlist)
print(notEndinglist)
    
    
