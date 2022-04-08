import os, htcondor

Samplelist = [
"DataUL17B_DoubleMuon",
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
condor_dir = "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Analyzer/condor_hist/"
njobs = 0

os.system('rm -rf '+condor_dir+'job/*')
os.system('rm -rf '+condor_dir+'log/*')

def submitter(ncores, memory, fname, channel, N):
	submit_dic = {"executable": fname,
	"jobbatchname": "PUJets_"+sample,
	#"jobbatchname": "PUJets_histo",	
	"universe":"vanilla",
	"request_cpus":ncores,
	"log":condor_dir+"condor_log/"+sample+str(N).replace(".","p")+".log",
	"RequestMemory": memory,
	"getenv":"True",
	"should_transfer_files":"YES",
	"when_to_transfer_output" : "ON_EXIT",
	"output": condor_dir+"log/"+sample+str(N).replace(".","p")+".log",
	"error" : condor_dir+"log/"+sample+str(N).replace(".","p")+".err",
 	"concurrency_limits" : 'n200.yeonjoon'
   }
	sub = htcondor.Submit(submit_dic)
	schedd = htcondor.Schedd()         
	submit_result = schedd.submit(sub)
nlist=[0.5+0.5*i for i in range(0,4)]
nlist=[1.5]
for n in nlist:
	for sample in Samplelist:
		fname = condor_dir+"job/job_"+sample+"_N"+str(n).replace(".","p")+".sh"
		if 'DoubleMuon' in sample:
			ncores = 4
			memory = 4*1024
			f = open(fname ,"w+")
			f.write("#!/bin/bash\n")
			f.write('source %s../RunCondor_MakeHistograms.sh %s %d %.1f %s' % (condor_dir,sample,ncores,n, 'Mu'))
			os.system("chmod 755 "+fname)
			f.close()
			submitter(ncores,memory,fname,"Mu",n)
		elif 'DoubleEG' in sample or 'EGamma' in sample:
			ncores = 4
			memory = 4*1024	
			f = open(fname ,"w+")
			f.write("#!/bin/bash\n")
			f.write('source %s../RunCondor_MakeHistograms.sh %s %d %.1f %s' % (condor_dir,sample,ncores, n,'El'))
			os.system("chmod 755 "+fname)
			f.close()
			submitter(ncores,memory,fname,"El",n)

		elif 'MCUL' in sample:
			f = open(fname.replace(".sh","_El.sh") ,"w+")
			f.write("#!/bin/bash\n")
			ncores = 8
			memory = 8*1024
			f.write('source %s../RunCondor_MakeHistograms.sh %s %d %.1f %s' % (condor_dir,sample,ncores, n,'El'))
			os.system("chmod 755 "+fname.replace(".sh","_El.sh"))
			f.close()
			submitter(ncores,memory,fname.replace(".sh","_El.sh"),"El",n)

			f = open(fname.replace(".sh","_Mu.sh") ,"w+")
			f.write("#!/bin/bash\n")
			ncores = 8
			memory = 8*1024
			f.write('source %s../RunCondor_MakeHistograms.sh %s %d %.1f %s' % (condor_dir,sample,ncores, n, 'Mu'))
			os.system("chmod 755 "+fname.replace(".sh","_Mu.sh"))
			f.close()
			submitter(ncores,memory,fname.replace(".sh","_Mu.sh"),"Mu",n)

  
	


