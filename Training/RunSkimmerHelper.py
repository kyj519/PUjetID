#!/usr/bin/env python

def GetSelection(era):
  #
  # Define object preselection. Need to do "Sum$" rather than take the first element because
  # the first element is not necessarily the leading in pt. 
  #
  objectSel = "((nMuon>=2 && Sum$(Muon_pt>15.)>=1) || (nElectron>=2 && Sum$(Electron_pt>20.)>=1)) && (nJet>=1 || nJetPuppi>=1)"

  #
  # Define trigger selection. Need to do "Alt$(trigBranchName,0)" because some trigger paths are not available throughout a given year.
  # If it doesn't exist in a period or a run, the branch will not exist in nanoAOD.
  #
  trigSel2016 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,0) ||Alt$(HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,0))"
  trigSel2017 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"
  trigSel2018 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"

  selection = ""

  if (era == "UL2016APV" or era == "UL2016"):
    selection = " && ".join((objectSel,trigSel2016))
  elif (era == "UL2017"):
    selection = " && ".join((objectSel,trigSel2017))
  elif (era == "UL2018"):
    selection = " && ".join((objectSel,trigSel2018))

  return selection
 
def GetJSON(era):
  jsonInput=""
  if (era == "UL2016APV" or era == "UL2016"):
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
  elif era == "UL2017":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
  elif era == "UL2018":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"

  return jsonInput

from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2016APV
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2016
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2017
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2018

from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016APV_mc
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016_mc
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2017_mc
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2018_mc

from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016APV_data_dielectron
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016_data_dielectron
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2017_data_dielectron
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2018_data_dielectron

from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016APV_data_dimuon 
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2016_data_dimuon 
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2017_data_dimuon 
from PUjetID.Training.SkimmerDiLeptonForTraining import SkimmerDiLeptonForTraining_UL2018_data_dimuon 

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import * 
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2018
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2016

def GetModules(era, isMC, dataStream):
  modules = []
  #
  # Modules for jet pt resolution smearing on MC and also to retrieve JEC and JER uncertainties
  #
  applyJetPtSmearing=False
  if era == "UL2017":
    if isMC: 
      jetCorr_AK4_UL2017_mc = createJMECorrector(isMC=True, dataYear="UL2017", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "UL2018":
    if isMC: 
      jetCorr_AK4_UL2018_mc = createJMECorrector(isMC=True, dataYear="UL2018", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "UL2016APV":
    if isMC: 
      jetCorr_AK4_UL2016APV_mc = createJMECorrector(isMC=True, dataYear="UL2016_preVFP", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "UL2016":
    if isMC: 
      jetCorr_AK4_UL2016_mc = createJMECorrector(isMC=True, dataYear="UL2016", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)

  #===========================================
  #
  # Make list of modules
  #
  #============================================
  #
  # UL 2017
  #
  if era == "UL2017":
    if isMC: 
      modules=[puWeight_UL2017(), muonRocCorUL2017(), jetCorr_AK4_UL2017_mc(), SkimmerDiLeptonForTraining_UL2017_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2017(), SkimmerDiLeptonForTraining_UL2017_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2017(), SkimmerDiLeptonForTraining_UL2017_data_dielectron()]
  #
  # UL 2018
  #
  elif era == "UL2018":
    if isMC: 
      modules=[puWeight_UL2018(), muonRocCorUL2018(), jetCorr_AK4_UL2018_mc(), SkimmerDiLeptonForTraining_UL2018_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2018(), SkimmerDiLeptonForTraining_UL2018_data_dimuon()]
      elif "EGamma" in dataStream:
        modules=[muonRocCorUL2018(), SkimmerDiLeptonForTraining_UL2018_data_dielectron()]
  #
  # UL 2016APV
  #
  elif era == "UL2016APV":
    if isMC: 
      modules=[puWeight_UL2016(), muonRocCorUL2016APV(), jetCorr_AK4_UL2016APV_mc(), SkimmerDiLeptonForTraining_UL2016APV_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2016APV(), SkimmerDiLeptonForTraining_UL2016APV_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2016APV(), SkimmerDiLeptonForTraining_UL2016APV_data_dielectron()]
  #
  # UL 2016
  #
  elif era == "UL2016":
    if isMC: 
      modules=[puWeight_UL2016(), muonRocCorUL2016(), jetCorr_AK4_UL2016_mc(), SkimmerDiLeptonForTraining_UL2016_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2016(), SkimmerDiLeptonForTraining_UL2016_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2016(), SkimmerDiLeptonForTrainingUL2016_data_dielectron()]

  return modules
