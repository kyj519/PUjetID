#!/usr/bin/env python

def GetSelection(era):
  #
  # Define object preselection. Need to do "Sum$" rather than take the first element because
  # the first element is not necessarily the leading in pt. 
  #
  objectSel = "((nMuon>=2 && Sum$(Muon_pt>20.)>=1) || (nElectron>=2 && Sum$(Electron_pt>20.)>=1)) && (nJet>=1)"

  #
  # Define trigger selection. Need to do "Alt$(trigBranchName,0)" because some trigger paths are not available throughout a given year.
  # If it doesn't exist in a period or a run, the branch will not exist in nanoAOD.
  #
  trigSel2016 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,0) ||Alt$(HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,0))"
  trigSel2017 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"
  trigSel2018 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"

  selection = ""

  #
  # preUL
  #
  if era == "2016":
    selection = " && ".join((objectSel,trigSel2016))
  elif era == "2017":
    selection = " && ".join((objectSel,trigSel2017))
  elif era == "2018":
    selection = " && ".join((objectSel,trigSel2018))
  #
  # UL
  #
  elif era == "UL2016preVFP":
    selection = " && ".join((objectSel,trigSel2016))
  elif era == "UL2016postVFP":
    selection = " && ".join((objectSel,trigSel2016))
  elif era == "UL2017":
    selection = " && ".join((objectSel,trigSel2017))
  elif era == "UL2018":
    selection = " && ".join((objectSel,trigSel2018))

  return selection
 
def GetJSON(era):
  jsonInput=""
  #
  # preUL
  #
  if era == "2016":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt"
  elif era == "2017":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt"
  elif era == "2018":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt"
  #
  # UL
  #
  elif era == "UL2016preVFP":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
  elif era == "UL2016postVFP":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
  elif era == "UL2017":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
  elif era == "UL2018":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"

  return jsonInput

from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_data_dimuon 

from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2017_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2017_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2017_data_dimuon 

from PUjetID.Skimmer.PUIDCalculator import PUIDCalculator_UL2017 

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import * 
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2016
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2018

def GetModules(era, isMC, dataStream):
  modules = []
  #
  # Modules for jet pt resolution smearing on MC and also to retrieve JEC and JER uncertainties
  #
  applyJetPtSmearing=True
  if era == "2016":
    if isMC: 
      jetCorr_AK4_MC16 = createJMECorrector(isMC=True, dataYear="2016", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "2017":
    if isMC: 
      jetCorr_AK4_MC17 = createJMECorrector(isMC=True, dataYear="2017", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "2018":
    if isMC: 
      jetCorr_AK4_MC18 = createJMECorrector(isMC=True, dataYear="2018", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "UL2017":
    if isMC: 
      jetCorr_AK4_MCUL17 = createJMECorrector(isMC=True, dataYear="UL2017", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)

  #===========================================
  #
  # Make list of modules
  #
  #============================================
  #
  # PreUL 2016
  #
  if era == "2016":
    if isMC: 
      modules=[puWeight_2016(), jetCorr_AK4_MC16(), SkimmerDiLepton_2016_mc()]
    else:
      if "DoubleMuon" in dataStream:
        modules=[SkimmerDiLepton_2016_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[SkimmerDiLepton_2016_data_dielectron()]
  #
  # PreUL 2017
  #
  elif era == "2017":
    if isMC: 
      modules=[puWeight_2017(), jetCorr_AK4_MC17(), SkimmerDiLepton_2017_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[SkimmerDiLepton_2017_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[SkimmerDiLepton_2017_data_dielectron()]
  #
  # PreUL 2018
  #
  elif era == "2018":
    if isMC: 
      modules=[puWeight_2018(), jetCorr_AK4_MC18(), SkimmerDiLepton_2018_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[SkimmerDiLepton_2018_data_dimuon()]
      elif "EGamma" in dataStream:
        modules=[SkimmerDiLepton_2018_data_dielectron()]
  #
  # UL 2017
  #
  elif era == "UL2017":
    if isMC: 
      modules=[jetCorr_AK4_MCUL17(), SkimmerDiLepton_UL2017_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[SkimmerDiLepton_UL2017_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[SkimmerDiLepton_UL2017_data_dielectron()]

  return modules


