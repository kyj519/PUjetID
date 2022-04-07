import os, htcondor
from datetime import datetime
Eras = ['UL2018','UL2017','UL2016','UL2016APV']
orders = ['NLO']
workingPoints = ['Loose','Medium',"Tight"]
systs = ['central', 'jesTotalUp', 'jesTotalDown', 'noJER', 'jerUp', 'jerDown']
systs = ['central']
runkeys = [era+" "+order+" "+wp+" "+syst for syst in systs for wp in workingPoints for order in orders for era in Eras]
condor_dir = "/u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Fitter/condor/"
njobs = 0
os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')

now = datetime.now()
nowstr = now.strftime("%d%m%Y_%H%M%S")
balanceN = os.listdir('gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his_hadd/')

for runkey in runkeys:
	for n in balanceN:
		f = open(condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+".sh","w+")
		f.write("#!/bin/bash\n")
		f.write("source "+condor_dir+"../RunCondor_Fit.sh "+runkey+" "+nowstr+" %s" % n)
		os.system("chmod 755 "+condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+".sh")
		f.close()
		submit_dic = {"executable": condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+".sh",
		"jobbatchname": "PUJets_"+runkey.replace(" ","_"),
		"universe":"vanilla",
		"request_cpus":1,
		"log":condor_dir+"condorlog/"+runkey.replace(" ","_")+"_"+n+".log",
		"getenv":"True",
		"should_transfer_files":"YES",
		"when_to_transfer_output" : "ON_EXIT",
		"output": condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+".log",
		"error" : condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+".err"}
		sub = htcondor.Submit(submit_dic)
		schedd = htcondor.Schedd()         
		submit_result = schedd.submit(sub)  
		


