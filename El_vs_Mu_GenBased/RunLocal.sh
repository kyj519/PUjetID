#!/bin/bash


ERALIST=(
UL18
UL17
UL16
UL16APV
)
inDirList=(
	"/gv0/Users/yeonjoon/ntuples_JMENano/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim_MuonLooseIso/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim_MuonNoIso/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim_MuonNoIso_EleNoIso/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim_MuonTightIso_EleTightIso/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim_Muon_Electron_TightIDwithTightMiniIso/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
	"/gv0/Users/yeonjoon/ntuples_JMENano_SingleLeptonTrigger/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/"
)
outDirList=(
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim_MuonLooseIso/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim_MuonNoIso/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim_MuonNoIso_EleNoIso/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim_MuonVeryTightIso_EleVeryTightIso/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLepton_Reskim_Muon_El_TightIDwithTightminiIso/"
	"/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_SingleLeptonTrigger/"
)
i=`expr $1 / 8`
j=`expr $1 % 8`
echo $1
echo $i
echo $j
python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/MakePlot.py --era ${ERALIST[$i]} --ncores 32 --path_inDir ${inDirList[$j]} --outDir=${outDirList[$j]} --doLogY &
python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/MakePlot.py --era ${ERALIST[$i]} --ncores 32 --path_inDir ${inDirList[$j]} --outDir=${outDirList[$j]}

