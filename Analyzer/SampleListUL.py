import collections
from SampleList import Sample

version="DiLeptonSkim_ULNanoV9_v1p1"

EOSURL="root://eoscms.cern.ch/"
EOSDIR="/eos/cms/store/group/phys_jetmet/nbinnorj/"
CRABDIR="JetPUId_"+version+"/CRABOUTPUT/"
NTUPDIR="JetPUId_"+version+"/ntuples_skim/"
Samples = collections.OrderedDict()

################################################
#
# UL2017
#
################################################
#
# DY MG5 LO
#
Samples["MCUL17_DY_MG"] = Sample(
  name="MCUL17_DY_MG",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUId_MCUL17NanoAODv9_"+version+"/*/*/tree_*.root",
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUId_MCUL17NanoAODv9_ext1_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL17_DY_MG.root"
  ]
)
#
# DY MG5 NLO
#
Samples["MCUL17_DY_AMCNLO"] = Sample(
  name="MCUL17_DY_AMCNLO",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/JetPUId_MCUL17NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL17_DY_AMCNLO.root"
  ]
)
#
# Data DoubleMuon
#
Samples["DataUL17B_DoubleMuon"] = Sample(
  name="DataUL17B_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2017B-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17B_DoubleMuon.root"
  ]
)
Samples["DataUL17C_DoubleMuon"] = Sample(
  name="DataUL17C_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2017C-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17C_DoubleMuon.root"
  ]
)
Samples["DataUL17D_DoubleMuon"] = Sample(
  name="DataUL17D_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2017D-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17D_DoubleMuon.root"
  ]
)
Samples["DataUL17E_DoubleMuon"] = Sample(
  name="DataUL17E_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2017E-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17E_DoubleMuon.root"
  ]
)
Samples["DataUL17F_DoubleMuon"] = Sample(
  name="DataUL17F_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2017F-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17F_DoubleMuon.root"
  ]
)
#
# Data DoubleEG
#
Samples["DataUL17B_DoubleEG"] = Sample(
  name="DataUL17B_DoubleEG",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2017B-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17B_DoubleEG.root"
  ]
)
Samples["DataUL17C_DoubleEG"] = Sample(
  name="DataUL17C_DoubleEG",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2017C-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17C_DoubleEG.root"
  ]
)
Samples["DataUL17D_DoubleEG"] = Sample(
  name="DataUL17D_DoubleEG",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2017D-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17D_DoubleEG.root"
  ]
)
Samples["DataUL17E_DoubleEG"] = Sample(
  name="DataUL17E_DoubleEG",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2017E-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17E_DoubleEG.root"
  ]
)
Samples["DataUL17F_DoubleEG"] = Sample(
  name="DataUL17F_DoubleEG",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2017F-DataUL17NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL17F_DoubleEG.root"
  ]
)
################################################
#
# UL2018
#
################################################
#
# DY MG5 LO
#
Samples["MCUL18_DY_MG"] = Sample(
  name="MCUL18_DY_MG",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUId_MCUL18NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL18_DY_MG.root"
  ]
)
#
# DY MG5 NLO
#
Samples["MCUL18_DY_AMCNLO"] = Sample(
  name="MCUL18_DY_AMCNLO",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/JetPUId_MCUL18NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL18_DY_AMCNLO.root"
  ]
)
#
# Data DoubleMuon
#
Samples["DataUL18A_DoubleMuon"] = Sample(
  name="DataUL18A_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2018A-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18A_DoubleMuon.root"
  ]
)
Samples["DataUL18B_DoubleMuon"] = Sample(
  name="DataUL18B_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2018B-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18B_DoubleMuon.root"
  ]
)
Samples["DataUL18C_DoubleMuon"] = Sample(
  name="DataUL18C_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2018C-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18C_DoubleMuon.root"
  ]
)
Samples["DataUL18D_DoubleMuon"] = Sample(
  name="DataUL18D_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2018D-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18D_DoubleMuon.root"
  ]
)
#
# Data EGamma
#
Samples["DataUL18A_EGamma"] = Sample(
  name="DataUL18A_EGamma",
  crabFiles=[
    EOSDIR+CRABDIR+"EGamma/JetPUId_Run2018A-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18A_EGamma.root"
  ]
)
Samples["DataUL18B_EGamma"] = Sample(
  name="DataUL18B_EGamma",
  crabFiles=[
    EOSDIR+CRABDIR+"EGamma/JetPUId_Run2018B-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18B_EGamma.root"
  ]
)
Samples["DataUL18C_EGamma"] = Sample(
  name="DataUL18C_EGamma",
  crabFiles=[
    EOSDIR+CRABDIR+"EGamma/JetPUId_Run2018C-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18C_EGamma.root"
  ]
)
Samples["DataUL18D_EGamma"] = Sample(
  name="DataUL18D_EGamma",
  crabFiles=[
    EOSDIR+CRABDIR+"EGamma/JetPUId_Run2018D-DataUL18NanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL18D_EGamma.root"
  ]
)
################################################
#
# UL2016APV
#
################################################
#
# DY MG5 LO
#
Samples["MCUL16APV_DY_MG"] = Sample(
  name="MCUL16APV_DY_MG",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUId_MCUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL16APV_DY_MG.root"
  ]
)
#
# DY MG5 NLO
#
Samples["MCUL16APV_DY_AMCNLO"] = Sample(
  name="MCUL16APV_DY_AMCNLO",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/JetPUId_MCUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL16APV_DY_AMCNLO.root"
  ]
)
#
# DYToMumu Powheg
#
Samples["MCUL16APV_DYToMuMu_PHG"] = Sample(
  name="MCUL16APV_DYToMuMu_PHG",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToMuMu_M-50_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/JetPUId_MCUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL16APV_DYToMuMu_PHG.root"
  ]
)
#
# Data DoubleMuon
#
Samples["DataUL16APVB_DoubleMuon"] = Sample(
  name="DataUL16APVB_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016B-ver1_DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016B-ver2_DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root"
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16APVB_DoubleMuon.root"
  ]
)
Samples["DataUL16APVC_DoubleMuon"] = Sample(
  name="DataUL16APVC_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016C-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16APVC_DoubleMuon.root"
  ]
)
Samples["DataUL16APVD_DoubleMuon"] = Sample(
  name="DataUL16APVD_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016D-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16APVD_DoubleMuon.root"
  ]
)
Samples["DataUL16APVE_DoubleMuon"] = Sample(
  name="DataUL16APVE_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016E-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16APVE_DoubleMuon.root"
  ]
)
Samples["DataUL16APVF_DoubleMuon"] = Sample(
  name="DataUL16APVF_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016F-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16APVF_DoubleMuon.root"
  ]
)
#
# Data DoubleEG
#
# Samples["DataUL16APVB_DoubleEG"] = Sample(
#   name="DataUL16APVB_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016B-ver1_DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016B-ver2_DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root"
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16APVB_DoubleEG.root"
#   ]
# )
# Samples["DataUL16APVC_DoubleEG"] = Sample(
#   name="DataUL16APVC_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016C-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16APVC_DoubleEG.root"
#   ]
# )
# Samples["DataUL16APVD_DoubleEG"] = Sample(
#   name="DataUL16APVD_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016D-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16APVD_DoubleEG.root"
#   ]
# )
# Samples["DataUL16APVE_DoubleEG"] = Sample(
#   name="DataUL16APVE_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016E-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16APVE_DoubleEG.root"
#   ]
# )
# Samples["DataUL16APVF_DoubleEG"] = Sample(
#   name="DataUL16APVF_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016F-DataUL16APVNanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16APVF_DoubleEG.root"
#   ]
# )
################################################
#
# UL2016
#
################################################
#
# DY MG5 LO
#
# Samples["MCUL16_DY_MG"] = Sample(
#   name="MCUL16_DY_MG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/JetPUId_MCUL16NanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_MCUL16_DY_MG.root"
#   ]
# )
#
# DY MG5 NLO
#
# Samples["MCUL16_DY_AMCNLO"] = Sample(
#   name="MCUL16_DY_AMCNLO",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/JetPUId_MCUL16NanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_MC16_DY_AMCNLO.root"
#   ]
# )
#
# DYToMumu Powheg
#
Samples["MCUL16_DYToMuMu_PHG"] = Sample(
  name="MCUL16_DYToMuMu_PHG",
  crabFiles=[
    EOSDIR+CRABDIR+"DYJetsToMuMu_M-50_TuneCP5_13TeV-powhegMiNNLO-pythia8-photos/JetPUId_MCUL16NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_MCUL16_DYToMuMu_PHG.root"
  ]
)
#
# Data DoubleMuon
#
Samples["DataUL16F_DoubleMuon"] = Sample(
  name="DataUL16F_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016F-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16F_DoubleMuon.root"
  ]
)
Samples["DataUL16G_DoubleMuon"] = Sample(
  name="DataUL16G_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016G-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16G_DoubleMuon.root"
  ]
)
Samples["DataUL16H_DoubleMuon"] = Sample(
  name="DataUL16H_DoubleMuon",
  crabFiles=[
    EOSDIR+CRABDIR+"DoubleMuon/JetPUId_Run2016H-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
  ],
  ntupleFiles=[
    EOSDIR+NTUPDIR+"ntuple_DataUL16H_DoubleMuon.root"
  ]
)
#
# Data DoubleEG
#
# Samples["DataUL16F_DoubleEG"] = Sample(
#   name="DataUL16F_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016F-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16F_DoubleEG.root"
#   ]
# )
# Samples["DataUL16G_DoubleEG"] = Sample(
#   name="DataUL16G_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016G-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16G_DoubleEG.root"
#   ]
# )
# Samples["DataUL16H_DoubleEG"] = Sample(
#   name="DataUL16H_DoubleEG",
#   crabFiles=[
#     EOSDIR+CRABDIR+"DoubleEG/JetPUId_Run2016H-DataUL16NanoAODv9_"+version+"/*/*/tree_*.root",
#   ],
#   ntupleFiles=[
#     EOSDIR+NTUPDIR+"ntuple_DataUL16H_DoubleEG.root"
#   ]
# )

