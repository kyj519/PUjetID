import os, shutil
os.system("export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert")
os.system("export LD_PRELOAD=/usr/lib64/libpdcap.so")
os.system("export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/dcap")

#
# combine all data histos into one root file
#
# export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert
# export LD_PRELOAD="/usr/lib64/libpdcap.so"
# export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib64/dcap"
# HISTODIR="gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his"

# python haddhisto.py --histdir $HISTODIR

# mkdir ./temp
# ls $HISTODIR | xargs -I{} cp $HISTODIR/{} ./temp/ &
# wait
# hadd -f ./temp/Histo_DataUL17.root ./temp/Histo_DataUL17*_*.root
# hadd -f ./temp/Histo_DataUL18.root ./temp/Histo_DataUL18*_*.root
# hadd -f ./temp/Histo_DataUL16APV.root ./temp/Histo_DataUL16APV*_*.root
# hadd -f ./temp/Histo_DataUL16.root ./temp/Histo_DataUL16[FGH]_*.root
# hadd -f ./temp/Histo_MCUL16_DY_AMCNLO_JetBinned.root ./temp/Histo_MCUL16[FGH]_*.root
# hadd -f ./temp/Histo_DataUL16APV_DY_AMCNLO_JetBinned.root ./temp/Histo_DataUL16[FGH]_*.root
# hadd -f ./temp/Histo_DataUL17_DY_AMCNLO_JetBinned.root ./temp/Histo_DataUL16[FGH]_*.root
# hadd -f ./temp/Histo_DataUL18_DY_AMCNLO_JetBinned.root ./temp/Histo_DataUL16[FGH]_*.root

# cp ./temp/Histo_DataUL17.root ${HISTODIR}
# cp ./temp/Histo_DataUL18.root ${HISTODIR}
# cp ./temp/Histo_DataUL16APV.root ${HISTODIR}
# cp ./temp/Histo_DataUL16.root ${HISTODIR}
# rm -rf ./temp
histodir= "gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his/"
tempdir = "./temp/"
shutil.copytree(histodir,tempdir)
histlist = os.listdir(tempdir)
datalist_by_era = {}
eraList = ["17","16","16APV"]
for era in eraList:
	targetfilename = "Histo_DataUL%s.root" % era 
	datalist_by_era[targetfilename]=[]
	for file in histlist:
		if "DataUL" + era in file:
			datalist_by_era[targetfilename].append(file)

AK4Syst = ["","_jerDown","_jerUp","_jesTotalDown","_jesTotalUp","_noJER"]
mclist_by_era_and_syst = {}
for era in eraList:
	for syst in AK4Syst:
		targetfilename = "Histo_MCUL%s_DY_AMCNLO%s.root" % (era,syst)
		mclist_by_era_and_syst[targetfilename]=[]
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_0J%s.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_1J%s.root" % (era,syst))
		mclist_by_era_and_syst[targetfilename].append("Histo_MCUL%s_DY_AMCNLO_2J%s.root" % (era,syst))

print("Hadd start for data")
for targetname, hist in datalist_by_era.items():
	command_str = "hadd -f %s%s" % (tempdir,targetname)
	for file in hist:
		command_str = command_str + " " +tempdir + file
	print(command_str)
	os.system(command_str)
	os.system("dccp -H %s%s %s"%(tempdir,targetname,histodir))

for targetname, hist in mclist_by_era_and_syst.items():
	command_str = "hadd -f %s%s" % (tempdir, targetname)
	for file in hist:
		command_str = command_str + " " +tempdir + file
	print(command_str)
	os.system(command_str)
	os.system("dccp -H %s%s %s"%(tempdir,targetname,histodir))

shutil.rmtree(tempdir)