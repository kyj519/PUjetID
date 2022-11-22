from distutils import filelist
import os, shutil
import argparse
import tempfile


parser = argparse.ArgumentParser("")
parser.add_argument('--subfolder',         dest='subfolder',         type=str,  default="")
args = parser.parse_args()
subfolder = args.subfolder+"/"
print(subfolder)
histodir= "gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his/"+subfolder
histodir_xrootd="root://cluster142.knu.ac.kr//store/user/yeonjoon/ntuples/result_his/"+subfolder
histodir_result= "gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his_hadd/"+subfolder
tempdir = "/d0/scratch/yeonjoon/temp/"+subfolder
tempdir_result = "/d0/scratch/yeonjoon/temp_hadd/"+subfolder

if os.path.isdir(tempdir):
	shutil.rmtree(tempdir)
if os.path.isdir(tempdir_result):
	shutil.rmtree(tempdir_result)
if os.path.isdir(histodir_result):
	shutil.rmtree(histodir_result)


os.makedirs(tempdir)
os.makedirs(tempdir_result)
os.makedirs(histodir_result)

os.system("xrdcp -r %s %s --parallel 4" % (histodir_xrootd, tempdir.replace(subfolder,"")))
os.system("mv %s%s* %s" % (tempdir, subfolder,tempdir))

histlist = os.listdir(tempdir)
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
for file in histlist:
	print("copy inclusive MC")
	if "AMCNLO_INCL" in file:
		os.system("dccp -H %s%s %s &"%(tempdir,file,histodir_result))	

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

print("Hadd start for data")
for targetname, hist in datalist_by_era.items():
	command_str = "hadd -f %s%s" % (tempdir_result,targetname)
	for file in hist:
		command_str = command_str + " " +tempdir + file
	print(command_str)
	os.system(command_str)
	os.system("dccp -H %s%s %s &"%(tempdir_result,targetname,histodir_result))

for targetname, hist in mclist_by_era_and_syst.items():
	command_str = "hadd -f %s%s" % (tempdir_result, targetname)
	for file in hist:
		command_str = command_str + " " +tempdir + file
	print(command_str)
	os.system(command_str)
	os.system("dccp -H %s%s %s &"%(tempdir_result,targetname,histodir_result))


