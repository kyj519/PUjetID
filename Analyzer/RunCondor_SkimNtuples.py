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

Samplelist.extend(["DataUL18A_EGamma",
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
"DataUL16APVF_DoubleEG"])

Samplelist = [
    "MCUL18_TTTo2L2Nu",
    "MCUL18_WW",
    "MCUL18_WZ",
    "MCUL18_ZZ",
    "MCUL17_TTTo2L2Nu",
    "MCUL17_WW",
    "MCUL17_WZ",
	"MCUL17_ZZ",
    "MCUL16APV_TTTo2L2Nu",
    "MCUL16APV_WW",
    "MCUL16APV_WZ",
    "MCUL16APV_ZZ",
    "MCUL16_TTTo2L2Nu",
    "MCUL16_WW",
    "MCUL16_WZ",
    "MCUL16_ZZ"
    ]

condor_dir = os.path.realpath("./")
condor_dir = condor_dir + "/condor_skim/"
if not os.path.isdir(condor_dir):
    os.makedirs(condor_dir+"job")
    os.makedirs(condor_dir+"log")
njobs = 0
os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')
ncores = 4
for sample in Samplelist:
	f = open(condor_dir+"job/job_"+sample+".sh","w+")
	f.write("#!/bin/bash\n")
	f.write('source %s../RunCondor_SkimNtuples.sh %s %d' % (condor_dir,sample,ncores))
	mem = 8192

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
	"RequestMemory": mem,
	"output": condor_dir+"log/"+sample+".log",
	"error" : condor_dir+"log/"+sample+".err",
 	"concurrency_limits" : 'n200.yeonjoon'}
	sub = htcondor.Submit(submit_dic)
	schedd = htcondor.Schedd()         
	submit_result = schedd.submit(sub)  

	


