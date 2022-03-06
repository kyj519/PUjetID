import os, htcondor
'''
Samplelist = ["DataUL17B_DoubleMuon",
"DataUL17C_DoubleMuon",
"DataUL17D_DoubleMuon",
"DataUL17E_DoubleMuon",
"DataUL17F_DoubleMuon",
"MCUL17_DY_MG",
"DataUL18A_DoubleMuon",
"DataUL18B_DoubleMuon",
"DataUL18C_DoubleMuon",
"DataUL18D_DoubleMuon",
"MCUL18_DY_MG",
"DataUL16APVB_DoubleMuon",
"DataUL16APVC_DoubleMuon",
"DataUL16APVD_DoubleMuon",
"DataUL16APVE_DoubleMuon",
"DataUL16APVF_DoubleMuon",
"MCUL16APV_DY_MG",
"DataUL16F_DoubleMuon",
"DataUL16G_DoubleMuon",
"DataUL16H_DoubleMuon",
'MCUL16_DY_MG']
'''
Samplelist = ["MCUL18_DY_AMCNLO","MCUL16_DY_AMCNLO","MCUL17_DY_AMCNLO","MCUL16APV_DY_AMCNLO"]

condor_dir = "/u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Analyzer/condor/"
njobs = 0
os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')

for sample in Samplelist:
	f = open(condor_dir+"job/job_"+sample+".sh","w+")
	f.write("#!/bin/bash\n")
	f.write("source "+condor_dir+"../RunCondor_SkimNtuples.sh "+sample)
	os.system("chmod 755 "+condor_dir+"job/job_"+sample+".sh")
	f.close()
	submit_dic = {"executable": condor_dir+"job/job_"+sample+".sh",
	"jobbatchname": "PUJets_"+sample,
	"universe":"vanilla",
	"request_cpus":20,
	"log":condor_dir+sample+".log",
	"getenv":"True",
	"should_transfer_files":"YES",
	"when_to_transfer_output" : "ON_EXIT",
	"output": condor_dir+"log/"+sample+".log",
	"error" : condor_dir+"log/"+sample+".err"}
	print(submit_dic)
	sub = htcondor.Submit(submit_dic)
	schedd = htcondor.Schedd()         
	submit_result = schedd.submit(sub)  
	print(submit_result.cluster())  
	


