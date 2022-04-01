import os, sys, subprocess
import htcondor
import shutil

class sample_setting:
	def __init__(self, sample_name, sample_era, njobs, dcap_file_location = "",dasdataset = "", fromXROOTD = False, isMC = True, dataStream = ""):
		self.file_location =  dcap_file_location
		self.sample_name = sample_name
		self.sample_era = sample_era
		self.isMC = isMC
		self.dasdataset = dasdataset
		self.filelist = []
		self.splitted_filelist = {}
		self.dataStream = dataStream
		self.outDir = "gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/outtree/%s"%sample_name
		if not os.path.isdir(self.outDir): os.mkdir(self.outDir)

		if fromXROOTD and dasdataset == "":
			print("error: das dataset is needed for xrootd")
			exit()
		
		if dataStream is not "" and isMC:
			print("no dataStream for MC")
			exit()

		if fromXROOTD: self.getFileFromXROOTD()
		else: self.getFileFromDCAP()
		self.splitFile(njobs)
	
	def getFileFromXROOTD(self):
		xrootd_prefix_knu = "root://cluster142.knu.ac.kr//store/user/yeonjoon/"
		xrootd_prefix_cms = "root://cms-xrd-global.cern.ch///"
		query = '--query  "file dataset=%s"' % self.dasdataset
		stream = os.popen('/cvmfs/cms.cern.ch/common/dasgoclient %s' % query)
		xrootdsample_without_prefix = stream.read().splitlines()

		for sample in xrootdsample_without_prefix:
			self.filelist.append(xrootd_prefix_cms+sample)

		

	def getFileFromDCAP(self):
		gsidprefix = "gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/"
		filelist_without_abspath = os.listdir(self.file_location)
		for file in filelist_without_abspath:
	 		self.filelist.append(self.file_location+"/"+file)	
	
	def splitFile(self,njobs):
		
		if njobs > len(self.filelist): njobs = len(self.filelist)
		
		for i in range(njobs):
			self.splitted_filelist[i] = []
		for i in range(len(self.filelist)):
			self.splitted_filelist[i % njobs].append(self.filelist[i])

		
def jobmaker(sample):
	n = 0
	current_dir = os.path.realpath("./")
	condor_dir = current_dir + "/condor"
	for i, lists in sample.splitted_filelist.items():
		n+=len(lists)
	print("%s, total number of input NanoAODs %d" % (sample.sample_name,n))
	os.mkdir(condor_dir+"/job/%s"%sample.sample_name)
	for i, files in sample.splitted_filelist.items():	
		f = open(condor_dir+"/job/%s/job_%d.sh" % (sample.sample_name,i),"w+")
		f.write("#!/bin/bash\n")
		for file in files:
			if sample.isMC:
				f.write('python /u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Skimmer/RunSkimmerCondor.py --era %s --outDir %s --isMC 1 --inputNanoAOD %s'%(sample.sample_era, sample.outDir, file))
			else:
				f.write('python /u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Skimmer/RunSkimmerCondor.py --era %s --outDir %s --inputNanoAOD %s'%(sample.sample_era, sample.outDir, file))
		os.system('chmod 755 %s' % (condor_dir+"/job/%s/job_%d.sh" % (sample.sample_name,i)))
		f.close()

def condor_submitter(sample):
	current_dir = os.path.realpath("./")
	joblist_wo_abs = os.listdir(current_dir+"/condor/job/%s/" % sample.sample_name)
	joblist = [(current_dir+"/condor/job/%s/" % sample.sample_name)+job for job in joblist_wo_abs]
	os.mkdir(condor_dir+"/log/%s"%sample.sample_name)
	for i in range(len(joblist)):

		submit_dic = {"executable": joblist[i],
		"jobbatchname": sample.sample_name+"_job_%d" % i,
		"universe":"vanilla",
		"request_cpus":1,
		"RequestMemory":4096,
		"log":current_dir+"/condor/condor_log/%s/job_%d.log"%(sample.sample_name,i),
		"getenv":"True",
		"should_transfer_files":"YES",
		"when_to_transfer_output" : "ON_EXIT",
		"output": current_dir+"/condor/log/%s/job_%d.log"%(sample.sample_name,i),
		"error" : current_dir+"/condor/log/%s/job_%d.err"%(sample.sample_name,i)}
		sub = htcondor.Submit(submit_dic)
		schedd = htcondor.Schedd()         
		submit_result = schedd.submit(sub)
		

if __name__ =="__main__":
	current_dir = os.path.realpath("./")
	if os.path.isdir(current_dir+"/condor"): shutil.rmtree(current_dir+"/condor")
	os.mkdir(current_dir+"/condor")
	os.mkdir(current_dir+"/condor/job")
	os.mkdir(current_dir+"/condor/log")
	os.mkdir(current_dir+"/condor/condor_log")
	condor_dir = current_dir + "/condor"

	MC_2018_1j = sample_setting(
							sample_name="DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8",
							sample_era="UL2018",
							njobs = 100,
							dasdataset = '/DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM',
							fromXROOTD=True)
	
	jobmaker(MC_2018_1j)
	condor_submitter(MC_2018_1j)

