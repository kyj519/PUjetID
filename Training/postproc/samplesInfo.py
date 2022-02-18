EOSURL      = "root://eoscms.cern.ch/"
prod_tag    = "DiLepSkim_JMENanoV9_v1p2"
path_inDir  = "/eos/cms/store/group/phys_jetmet/nbinnorj/JetPUIdTrain_"+prod_tag+"/CRABOUTPUT/"
path_outDir = "/eos/cms/store/group/phys_jetmet/nbinnorj/JetPUIdTrain_"+prod_tag+"/MERGED/"

samplesInfoDict = dict()

#
# Define cross-sections and path for all eras
#
eraListForMC = [
  "UL17",
  "UL18",

]
for era in eraListForMC:
  samplesInfoDict["MC"+era+"_DY_MG"] = {
    "path": [
      "DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUIdTrain_MC"+era+"JMENanoAODv9_"+prod_tag+"*/*/*/tree_*.root"
    ],
    "xsec": 5347.0,
  }
  samplesInfoDict["MC"+era+"_TTTo2L2Nu"] = {
    "path": [
      "TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/JetPUIdTrain_MC"+era+"JMENanoAODv9_"+prod_tag+"*/*/*/tree_*.root"
    ],
    "xsec": 88.29, #pb
  }

#
# UL2017 Lumi: 41479.68 picobarns
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#SummaryTable
#
samplesInfoDict["DataUL17_DoubleMuon"] = { 
  "path" : [
    "DoubleMuon/JetPUIdTrain_Run2017B-DataUL17JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2017C-DataUL17JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2017D-DataUL17JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2017E-DataUL17JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2017F-DataUL17JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
  ],
  "xsec":1.0,
}
#
# UL2018 Lumi: 59832.47 picobarns
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#SummaryTable
#
samplesInfoDict["DataUL18_DoubleMuon"] = { 
  "path" : [
    "DoubleMuon/JetPUIdTrain_Run2018A-DataUL18JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2018B-DataUL18JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2018C-DataUL18JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
    "DoubleMuon/JetPUIdTrain_Run2018D-DataUL18JMENanoAODv9_"+prod_tag+"/*/*/tree_*.root",
  ],
  "xsec":1.0,
}


