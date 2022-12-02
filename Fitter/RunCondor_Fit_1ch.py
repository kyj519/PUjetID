import os, htcondor
from datetime import datetime
def make_not_exist_dir(path):
    if os.path.isdir(path):
        return
    else:
        os.makedirs(path)
Eras = ['UL2018','UL2017','UL2016','UL2016APV']
orders = ['NLO']
workingPoints = ['Loose','Medium',"Tight"]
systs = ['central', 'jesTotalUp', 'jesTotalDown', 'noJER', 'jerUp', 'jerDown']
runkeys = [era+" "+order+" "+wp+" "+syst for syst in systs for wp in workingPoints for order in orders for era in Eras]

condor_dir = "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Fitter/condor/"
make_not_exist_dir(condor_dir)
make_not_exist_dir(os.path.join(condor_dir,'job'))
make_not_exist_dir(os.path.join(condor_dir,'log'))
njobs = 0
os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')

now = datetime.now()
nowstr_mu = now.strftime("%d%m%Y_%H%M%S")+"_mu"
nowstr_el = now.strftime("%d%m%Y_%H%M%S")+"_el"
balanceN = os.listdir('/gv0/Users/yeonjoon/ntuples/result_his_hadd')

for runkey in runkeys:
	for n in balanceN:
		f = open(condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_mu.sh","w+")
		f.write("#!/bin/bash\n")
		f.write("source "+condor_dir+"../RunCondor_Fit_1ch_mu.sh "+runkey+" "+nowstr_mu+" %s" % n)
		os.system("chmod 755 "+condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_mu.sh")
		f.close()
		submit_dic = {"executable": condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_mu.sh",
		"jobbatchname": "PUJets_"+runkey.replace(" ","_"),
		"universe":"vanilla",
		"request_cpus":1,
		"log":condor_dir+"condorlog/"+runkey.replace(" ","_")+"_"+n+".log",
		"getenv":"True",
		"should_transfer_files":"YES",
		"when_to_transfer_output" : "ON_EXIT",
		"output": condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+"_mu.log",
		"error" : condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+"_mu.err",
  		"concurrency_limits" : "n500.yeonjoon"}

		sub = htcondor.Submit(submit_dic)
		schedd = htcondor.Schedd()         
		submit_result = schedd.submit(sub)  
		
for runkey in runkeys:
	for n in balanceN:
		f = open(condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_el.sh","w+")
		f.write("#!/bin/bash\n")
		f.write("source "+condor_dir+"../RunCondor_Fit_1ch_el.sh "+runkey+" "+nowstr_el+" %s" % n)
		os.system("chmod 755 "+condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_el.sh")
		f.close()
		submit_dic = {"executable": condor_dir+"job/job_"+runkey.replace(" ","_")+"_"+n+"_el.sh",
		"jobbatchname": "PUJets_"+runkey.replace(" ","_"),
		"universe":"vanilla",
		"request_cpus":1,
		"log":condor_dir+"condorlog/"+runkey.replace(" ","_")+"_"+n+".log",
		"getenv":"True",
		"should_transfer_files":"YES",
		"when_to_transfer_output" : "ON_EXIT",
		"output": condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+"_el.log",
		"error" : condor_dir+"log/"+runkey.replace(" ","_")+"_"+n+"_el.err",
  		"concurrency_limits" : "n500.yeonjoon"}

		sub = htcondor.Submit(submit_dic)
		schedd = htcondor.Schedd()         
		submit_result = schedd.submit(sub)  

