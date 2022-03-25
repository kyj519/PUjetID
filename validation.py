import os, ROOT
path1 = "/u/user/yeonjoon/SE_UserHome/ntuples/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
path2 = "/u/user/yeonjoon/SE_UserHome/ntuples_no_jer_branch/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
dir1 = os.listdir(path1)
dir2 = os.listdir(path2)

entrydict1 = {}
entrydict2 = {}
for i in dir1:
	f = ROOT.TFile(path1+i,"READ")
	evt = f.Get("Events")
	entrydict1[i] = evt.GetEntries()

for i in dir2:
	f = ROOT.TFile(path2+i,"READ")
	evt = f.Get("Events")
	entrydict2[i] = evt.GetEntries()

for key, vals in entrydict1.items():
	print("Entry of %s" % key)
	print("jer ntuple : %s " % entrydict1[key])
	print("no jer ntuple : %s " % entrydict2[key])
