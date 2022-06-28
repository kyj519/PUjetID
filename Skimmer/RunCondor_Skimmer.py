import os, sys, subprocess
import htcondor
import shutil

class sample_setting:
    def __init__(self, sample_name, sample_era, njobs,dasdataset, isMC = True, dataStream = ""):
        self.sample_name = sample_name
        self.sample_era = sample_era
        self.isMC = isMC
        self.dasdataset = dasdataset
        self.filelist = []
        self.splitted_filelist = {}
        self.dataStream = dataStream
        
        if isMC:
            self.requestName = self.getOutDIR_MC() 
        else:
            self.requestName = self.getOutDIR_Data() 
            
        self.outDir = "/gv0/Users/yeonjoon/outtree/CRABOUTPUT/%s/%s"%(sample_name,self.requestName)
        if not os.path.isdir(self.outDir): os.makedirs(self.outDir)
        
        if dataStream is not "" and isMC:
            print("no dataStream for MC")
            exit()
        self.getFileFromXROOTD()
        self.splitFile(njobs)
    
    def getFileFromXROOTD(self):
        xrootd_prefix_cms = "root://cms-xrd-global.cern.ch//"
        query = '--query  "file dataset=%s"' % self.dasdataset.replace("\n","")
        stream = os.popen('/cvmfs/cms.cern.ch/common/dasgoclient %s' % query)
        xrootdsample_without_prefix = stream.read().splitlines()

        for sample in xrootdsample_without_prefix:
            self.filelist.append(xrootd_prefix_cms+sample)

        

    def splitFile(self,njobs):
        
        if njobs > len(self.filelist): njobs = len(self.filelist)
        
        for i in range(njobs):
            self.splitted_filelist[i] = []
        for i in range(len(self.filelist)):
            self.splitted_filelist[i % njobs].append(self.filelist[i])
   
    def getOutDIR_MC(self):
        reqNamePrefix="JetPUId"
        version = "DiLeptonSkim_ULNanoV9_v1p4"
        dataset = self.dasdataset
        primaryName   = dataset.split('/')[1].split("_")[0:4]
        primaryName   = "_".join(primaryName)
        primaryName   = primaryName.replace("_13TeV","")
        primaryName   = primaryName.replace("pythia","py")
        primaryName   = primaryName.replace("herwig","hw")
        primaryName   = primaryName.replace("powhegMiNNLO","pwhg")
        primaryName   = primaryName.replace("-photos","")
        
        secondaryName = dataset.split('/')[2]
        if self.sample_era == 'UL2018':
            secondaryName = secondaryName.replace("RunIISummer20UL18NanoAODv9-","MCUL18NanoAODv9")#RENAME CAMPAIGN. CHECK ITS UPDATED
            secondaryName = secondaryName.replace("106X_upgrade2018_realistic_v16_L1v1","") #REMOVE GT. CHECK ITS UPDATED
        elif self.sample_era == 'UL2017':
            secondaryName = secondaryName.replace("RunIISummer20UL17NanoAODv9-","MCUL17NanoAODv9")#RENAME CAMPAIGN. CHECK ITS UPDATED
            secondaryName = secondaryName.replace("106X_mc2017_realistic_v9","") #REMOVE GT. CHECK ITS UPDATED
        elif self.sample_era == 'UL2016APV':
            secondaryName = secondaryName.replace("RunIISummer20UL16NanoAODAPVv9-","MCUL16APVNanoAODv9")#RENAME CAMPAIGN. CHECK ITS UPDATED
            secondaryName = secondaryName.replace("106X_mcRun2_asymptotic_preVFP_v11","") #REMOVE GT. CHECK ITS UPDATED
        elif self.sample_era == 'UL2016':
            secondaryName = secondaryName.replace("RunIISummer20UL16NanoAODv9-","MCUL16NanoAODv9")#RENAME CAMPAIGN. CHECK ITS UPDATED
            secondaryName = secondaryName.replace("106X_mcRun2_asymptotic_v17","") #REMOVE GT. CHECK ITS UPDATED
        
        secondaryName = secondaryName.replace("-v1","")# 
        secondaryName = secondaryName.replace("-v2","")# 
        secondaryName = secondaryName.replace("-v3","")#
        secondaryName = secondaryName.replace("-v4","")

        requestName = primaryName + "_" + secondaryName
        requestName = reqNamePrefix +"_" + requestName + "_" + version
        
        return requestName
    
    def getOutDIR_Data(self):               
        reqNamePrefix="JetPUId"
        version = "DiLeptonSkim_ULNanoV9_v1p4" 
        dataset = self.dasdataset
 
        primaryName   = dataset.split('/')[1]
        #
        # TO DO: Fix This
        #
        secondaryName = dataset.split('/')[2]
        if self.sample_era == 'UL2018':
            secondaryName = secondaryName.replace("UL2018_MiniAODv2_NanoAODv9","DataUL18NanoAODv9") #CHECK
        elif self.sample_era == 'UL2017':
            secondaryName = secondaryName.replace("UL2017_MiniAODv2_NanoAODv9","DataUL17NanoAODv9") #CHECK
        elif self.sample_era == 'UL2016APV':
            secondaryName = secondaryName.replace("HIPM_UL2016_MiniAODv2_NanoAODv9","DataUL16APVNanoAODv9") #CHECK
        elif self.sample_era == 'UL2016':
            secondaryName = secondaryName.replace("UL2016_MiniAODv2_NanoAODv9","DataUL16NanoAODv9") #CHECK
            
         
        secondaryName = secondaryName.replace("-v1","") #CHECK
        secondaryName = secondaryName.replace("-v2","") #CHECK
        secondaryName = secondaryName.replace("-v3","") #CHECK
        #
        requestName = primaryName + "_" + secondaryName
        requestName = reqNamePrefix + "_" + requestName + "_" + version
        
        return requestName

        

        
def jobmaker(sample):
    n = 0
    current_dir = os.path.realpath("./")
    condor_dir = current_dir + "/condor"
    os.makedirs(condor_dir+"/"+sample.requestName+"/job")
    os.makedirs(condor_dir+"/"+sample.requestName+"/out")
    os.makedirs(condor_dir+"/"+sample.requestName+"/err")
    os.makedirs(condor_dir+"/"+sample.requestName+"/condor_log")
    
    for i, lists in sample.splitted_filelist.items():
        n+=len(lists)
    print("%s, total number of input NanoAODs %d" % (sample.sample_name,n))
    for i, files in sample.splitted_filelist.items():	
        f = open(condor_dir+"/"+sample.requestName+"/job/job_%s.sh" % (i),"w+")
        f.write("#!/bin/bash\n")
        f.write("export X509_USER_PROXY=/data6/Users/yeonjoon/proxy.cert\n")
        for file in files:
            if sample.isMC:
                f.write('python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/RunSkimmerCondor.py --era %s --outDir %s --isMC 1 --inputNanoAOD %s --outputFname %s'%(sample.sample_era, sample.outDir, file, "tree_%s.root" % i))
            else:
                f.write('python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/RunSkimmerCondor.py --era %s --outDir %s --inputNanoAOD %s --dataStream %s --outputFname %s'%(sample.sample_era, sample.outDir, file, sample.sample_name, "tree_%s.root" % i))
        os.system("chmod 755 "+condor_dir+"/"+sample.requestName+"/job/job_%s.sh" % (i))
        f.close()
        
def jobmaker_prefetcher(sample):
    n = 0
    current_dir = os.path.realpath("./")
    condor_dir = current_dir + "/condor"
    os.makedirs(condor_dir+"/"+sample.requestName+"/job")
    os.makedirs(condor_dir+"/"+sample.requestName+"/out")
    os.makedirs(condor_dir+"/"+sample.requestName+"/err")
    os.makedirs(condor_dir+"/"+sample.requestName+"/condor_log")
    
    for i, lists in sample.splitted_filelist.items():
        n+=len(lists)
    print("%s, total number of input NanoAODs %d" % (sample.sample_name,n))
    # for i, files in sample.splitted_filelist.items():	
    #     f = open(condor_dir+"/"+sample.requestName+"/job/job_%s.sh" % (i),"w+")
    #     f.write("#!/bin/bash\n")
    #     f.write("export X509_USER_PROXY=/data6/Users/yeonjoon/proxy.cert\n")
    #     for file in files:
    #         f.write('python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/filePrefetcher.py --file %s' % file)
    #     os.system("chmod 755 "+condor_dir+"/"+sample.requestName+"/job/job_%s.sh" % (i))
    #     f.close()
    for i, files in sample.splitted_filelist.items():
        f = open("xrootdlist.txt","a")
        for file in files:
            f.write(file+"\n")
        f.close()
        
def condor_submitter(sample):
    current_dir = os.path.realpath("./")
    condor_dir = current_dir + "/condor"
    joblist_wo_abs = os.listdir(condor_dir+"/"+sample.requestName+"/job/")
    joblist = [condor_dir+"/"+sample.requestName+"/job/"+job for job in joblist_wo_abs]
    mem = 2*1024
    if "MC" in sample.sample_name: mem = 2*1024
    if "2018" in sample.sample_name: mem= 2*1024
    
    defectKey = ['4732FDDD-C1CE-E246-8A76']

    
    
    for i in range(len(joblist)):
        isDefectedFile = False
        f = open(joblist[i], "r")
        lines = f.readlines()
        for key in defectKey:
            if key in lines[2]:
                isDefectedFile = isDefectedFile or True
        #if not isDefectedFile: continue
        submit_dic = {"executable": joblist[i],
        "jobbatchname": sample.requestName,
        "universe":"vanilla",
        "request_cpus":1,
        "RequestMemory":mem,
        "log":condor_dir+"/"+sample.requestName+"/condor_log/log_%s.log"%i,
        "getenv":"True",
        "should_transfer_files":"YES",
        "when_to_transfer_output" : "ON_EXIT",
        "output": condor_dir+"/"+sample.requestName+"/out/job_%s.out"%(i),
        "error" : condor_dir+"/"+sample.requestName+"/err/job_%s.err"%(i),
        "concurrency_limits" : "n200.yeonjoon"}
        sub = htcondor.Submit(submit_dic)
        schedd = htcondor.Schedd()         
        submit_result = schedd.submit(sub)
        

if __name__ =="__main__":
    current_dir = os.path.realpath("./")
    
    if os.path.isdir(current_dir+"/condor"): shutil.rmtree(current_dir+"/condor")

    condor_dir = current_dir + "/condor"
    eras = ['2016', '2016APV','2017','2018']
    channels = ['Electron', 'Muon', 'MC']

    for era in eras:
        for ch in channels:
            path = '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Skimmer/samples/ULNanoAODv9'
            prefix = 'ULNanoAODv9'
            if ch == 'MC':
                text_file = '%s/%s_%s_MC_amcnlo_jetBinned.txt' % (path,prefix,era)
            elif ch == 'Muon':
                text_file = '%s/%s_%s_Data_DoubleMuon.txt' % (path,prefix,era) 
            elif ch == 'Electron':
                text_file = '%s/%s_%s_Data_DoubleEG.txt' % (path,prefix,era)
            f = open(text_file)
            for line in f.readlines():
                if not '#' in line and not line == '':
                    print(line)
                    if ch == 'MC': sample_to_submit = sample_setting(sample_name=line.split('/')[1],sample_era='UL%s'%era,njobs=1000,dasdataset=line,isMC=True)
                    else: sample_to_submit = sample_setting(sample_name=line.split('/')[1],sample_era='UL%s'%era,njobs=1000,dasdataset=line,isMC=False)
                    jobmaker_prefetcher(sample_to_submit)
                    condor_submitter(sample_to_submit)
 


