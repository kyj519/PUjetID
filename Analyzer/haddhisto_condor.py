import os, shutil
import argparse
import tempfile


parser = argparse.ArgumentParser("")
parser.add_argument('--subfolder',         dest='subfolder',         type=str,  default="")
args = parser.parse_args()
subfolder = args.subfolder+"/"
print(subfolder)
histodir= "/gv0/Users/yeonjoon/ntuples/result_his/"+subfolder
histodir_result= "/gv0/Users/yeonjoon/ntuples/result_his_hadd/"+subfolder
if os.path.isdir(histodir_result):
	shutil.rmtree(histodir_result)


os.makedirs(histodir_result)


histlist = os.listdir(histodir)
print(histlist)
datalist_by_era = {}
eraList = ["17","16","16APV","18"]
for era in eraList:
	targetfilename_Mu = "Histo_DataUL%s_Mu.root" % era 
	datalist_by_era[targetfilename_Mu]=[]
	for file in histlist:
		if "DataUL" + era in file and "_Mu" in file:
			datalist_by_era[targetfilename_Mu].append(file)
for era in eraList:
	targetfilename_El ="Histo_DataUL%s_El.root" % era 
	datalist_by_era[targetfilename_El]=[]
	for file in histlist:
		if "DataUL" + era in file and "_El" in file:
			datalist_by_era[targetfilename_El].append(file)

AK4Syst = ["","_jerDown","_jerUp","_jesTotalUp","_jesTotalDown","_noJER"]
mclist_by_era_and_syst = {}
for era in eraList:
	for syst in AK4Syst:
		targetfilename = "Histo_MCUL%s_DY_AMCNLO%s_Mu.root" % (era,syst)
		mclist_by_era_and_syst[targetfilename]=[]
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_0J%s_Mu.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_1J%s_Mu.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_2J%s_Mu.root" % (era,syst))
for era in eraList:
	for syst in AK4Syst:
		targetfilename = "Histo_MCUL%s_DY_AMCNLO%s_El.root" % (era,syst)
		mclist_by_era_and_syst[targetfilename]=[]
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_0J%s_El.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_1J%s_El.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_2J%s_El.root" % (era,syst))
for file in histlist:
    if "_INCL" in file:
        shutil.copy2(histodir+file,histodir_result)
        
print("Hadd start for data")
for targetname, hist in datalist_by_era.items():
	command_str = "hadd -f %s%s" % (histodir_result,targetname)
	for file in hist:
		command_str = command_str + " " +histodir + file
	print(command_str)
	os.system(command_str)

for targetname, hist in mclist_by_era_and_syst.items():
	command_str = "hadd -f %s%s" % (histodir_result, targetname)
	for file in hist:
		command_str = command_str + " " +histodir + file
	print(command_str)
	os.system(command_str)


