import os, htcondor

Samplelist = ["DataUL17B_DoubleMuon",
"DataUL17C_DoubleMuon",
"DataUL17D_DoubleMuon",
"DataUL17E_DoubleMuon",
"DataUL17F_DoubleMuon",
"DataUL18A_DoubleMuon",
"DataUL18B_DoubleMuon",
"DataUL18C_DoubleMuon",
"DataUL18D_DoubleMuon",
"DataUL16APVB_DoubleMuon",
"DataUL16APVC_DoubleMuon",
"DataUL16APVD_DoubleMuon",
"DataUL16APVE_DoubleMuon",
"DataUL16APVF_DoubleMuon",
"DataUL16F_DoubleMuon",
"DataUL16G_DoubleMuon",
"DataUL16H_DoubleMuon",
"MCUL18_DY_AMCNLO_0J","MCUL16_DY_AMCNLO_0J","MCUL17_DY_AMCNLO_0J","MCUL16APV_DY_AMCNLO_0J",
 "MCUL18_DY_AMCNLO_1J","MCUL16_DY_AMCNLO_1J","MCUL17_DY_AMCNLO_1J","MCUL16APV_DY_AMCNLO_1J",
 "MCUL18_DY_AMCNLO_2J","MCUL16_DY_AMCNLO_2J","MCUL17_DY_AMCNLO_2J","MCUL16APV_DY_AMCNLO_2J"]

Samplelist = ["DataUL18A_EGamma",
"DataUL18B_EGamma",
"DataUL18C_EGamma",
"DataUL18D_EGamma",
"DataUL17B_DoubleEG",
"DataUL17C_DoubleEG",
"DataUL17D_DoubleEG",
"DataUL17E_DoubleEG",
"DataUL17F_DoubleEG",
"DataUL16F_DoubleEG",
"DataUL16G_DoubleEG",
"DataUL16H_DoubleEG",
"DataUL16APVB_DoubleEG",
"DataUL16APVC_DoubleEG",
"DataUL16APVD_DoubleEG",
"DataUL16APVE_DoubleEG",
"DataUL16APVF_DoubleEG"]
#Samplelist = ["MCUL18_DY_AMCNLO_INCL","MCUL17_DY_AMCNLO_INCL","MCUL16APV_DY_AMCNLO_INCL","MCUL16_DY_AMCNLO_INCL"]
condor_dir = "/u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Analyzer/condor/"
njobs = 0
os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')
ncores = 40
for sample in Samplelist:
	f = open(condor_dir+"job/job_"+sample+".sh","w+")
	f.write("#!/bin/bash\n")
	f.write('source %s../RunCondor_SkimNtuples.sh %s %d' % (condor_dir,sample,ncores))

	os.system("chmod 755 "+condor_dir+"job/job_"+sample+".sh")
	f.close()
	submit_dic = {"executable": condor_dir+"job/job_"+sample+".sh",
	"jobbatchname": "PUJets_"+sample,
	"universe":"vanilla",
	"request_cpus":ncores,
	"log":condor_dir+sample+".log",
	"getenv":"True",
	"should_transfer_files":"YES",
	"when_to_transfer_output" : "ON_EXIT",
	"RequestMemory":8192*2,
	"output": condor_dir+"log/"+sample+".log",
	"error" : condor_dir+"log/"+sample+".err"}
	sub = htcondor.Submit(submit_dic)
	schedd = htcondor.Schedd()         
	submit_result = schedd.submit(sub)  

	


