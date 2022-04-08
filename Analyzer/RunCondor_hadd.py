import os, htcondor

histdir = "/gv0/Users/yeonjoon/ntuples/result_his"

condor_dir = "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Analyzer/condor_hadd/"
python_hadd_path = "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Analyzer/haddhisto_condor.py"
subfolder_list = os.listdir(histdir)
os.system('rm -rf %s/job/*' % condor_dir)
os.system('rm -rf %s/condor_log/*' % condor_dir)
os.system('rm -rf %s/log/*' % condor_dir)
for subfolder in subfolder_list:
	jobname = condor_dir+"job/"+subfolder+".sh"
	f = open(jobname,"w+")
	f.write("#!/bin/bash\n")
	f.write("export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert\n")
	f.write("export LD_PRELOAD=/usr/lib64/libpdcap.so\n")
	f.write("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/dcap\n")
	f.write('python %s --subfolder %s' % (python_hadd_path, subfolder))
	f.close()
	os.system('chmod 755 %s' % jobname)
	submit_dic = {"executable": jobname,
	"jobbatchname": "hadd_%s" % subfolder,
	"universe":"vanilla",
	"log":condor_dir+"condor_log/"+subfolder+".log",
	"getenv":"True",
	"should_transfer_files":"YES",
	"when_to_transfer_output" : "ON_EXIT",
	"output": condor_dir+"log/"+subfolder+".out",
	"error" : condor_dir+"log/"+subfolder+".err"}
	sub = htcondor.Submit(submit_dic)
	schedd = htcondor.Schedd()         
	submit_result = schedd.submit(sub)