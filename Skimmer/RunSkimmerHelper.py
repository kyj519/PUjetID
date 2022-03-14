#!/usr/bin/env python

def GetSelection(era):
  #
  # Define object preselection. Need to do "Sum$" rather than take the first element because
  # the first element is not necessarily the leading in pt. 
  #
  objectSel = "((nMuon>=2 && Sum$(Muon_pt>15.)>=1) || (nElectron>=2 && Sum$(Electron_pt>20.)>=1)) && (nJet>=1)"

  #
  # Define trigger selection. Need to do "Alt$(trigBranchName,0)" because some trigger paths are not available throughout a given year.
  # If it doesn't exist in a period or a run, the branch will not exist in nanoAOD.
  #
  trigSel2016 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ,0) ||Alt$(HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ,0))"
  trigSel2017 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"
  trigSel2018 = "(Alt$(HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8,0) || Alt$(HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL,0))"

  selection = ""

  if (era == "2016" or era == "UL2016APV" or era == "UL2016"):
    selection = " && ".join((objectSel,trigSel2016))
  elif (era == "2017" or era == "UL2017"):
    selection = " && ".join((objectSel,trigSel2017))
  elif (era == "2018" or era == "UL2018"):
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
  elif (era == "UL2016APV" or era == "UL2016"):
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"
  elif era == "UL2017":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"
  elif era == "UL2018":
    jsonInput="/src/PUjetID/Skimmer/data/lumi/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"

  return jsonInput

from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCor2016 
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCor2017 
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCor2018 

from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2016APV
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2016
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2017
from PUjetID.Skimmer.MuonRocCorrProducer import muonRocCorUL2018

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
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2018_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2018_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2018_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016APV_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016APV_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016APV_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_UL2016_data_dimuon 

from PUjetID.Skimmer.PUIDCalculator import PUIDCalculator_UL2017 

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import * 
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2016
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2018
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2018
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_UL2016

from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016APV_muon_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016_muon_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2017_muon_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2018_muon_data


from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016APV_elec_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016_elec_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2017_elec_data
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2018_elec_data

from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016APV_mc
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2016_mc
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2017_mc
from PUjetID.Skimmer.LeptonCleanPreselector import LeptonCleanPreselector_UL2018_mc
def GetModules(era, isMC, dataStream):
  modules = []
  #
  # Modules for jet pt resolution smearing on MC and also to retrieve JEC and JER uncertainties
  #
  applyJetPtSmearing=True
  if era == "2016":
    if isMC: 
      jetCorr_AK4_2016_mc = createJMECorrector(isMC=True, dataYear="2016", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "2017":
    if isMC: 
      jetCorr_AK4_2017_mc = createJMECorrector(isMC=True, dataYear="2017", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "2018":
    if isMC: 
      jetCorr_AK4_2018_mc = createJMECorrector(isMC=True, dataYear="2018", runPeriod="", jesUncert="Total", jetType="AK4PFchs", applySmearing=applyJetPtSmearing)
  elif era == "UL2017":
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
  # PreUL 2016
  #
  if era == "2016":
    if isMC: 
      modules=[puWeight_2016(), muonRocCor2016(), jetCorr_AK4_2016_mc(), SkimmerDiLepton_2016_mc()]
    else:
      if "DoubleMuon" in dataStream:
        modules=[muonRocCor2016(), SkimmerDiLepton_2016_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCor2016(), SkimmerDiLepton_2016_data_dielectron()]
  #
  # PreUL 2017
  #
  elif era == "2017":
    if isMC: 
      modules=[puWeight_2017(), muonRocCor2017(), jetCorr_AK4_2017_mc(), SkimmerDiLepton_2017_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCor2017(), SkimmerDiLepton_2017_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCor2017(), SkimmerDiLepton_2017_data_dielectron()]
  #
  # PreUL 2018
  #
  elif era == "2018":
    if isMC: 
      modules=[puWeight_2018(), muonRocCor2018(), jetCorr_AK4_2018_mc(), SkimmerDiLepton_2018_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCor2018(), SkimmerDiLepton_2018_data_dimuon()]
      elif "EGamma" in dataStream:
        modules=[muonRocCor2018(), SkimmerDiLepton_2018_data_dielectron()]
  #
  # UL 2017
  #
  elif era == "UL2017":
    if isMC: 
      modules=[puWeight_UL2017(), muonRocCorUL2017(), LeptonCleanPreselector_UL2017_mc(),jetCorr_AK4_UL2017_mc(), SkimmerDiLepton_UL2017_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2017(),LeptonCleanPreselector_UL2017_muon_data() ,SkimmerDiLepton_UL2017_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2017(), SkimmerDiLepton_UL2017_data_dielectron()]
  #
  # UL 2018
  #
  elif era == "UL2018":
    if isMC: 
      modules=[puWeight_UL2018(), muonRocCorUL2018(), jetCorr_AK4_UL2018_mc(), SkimmerDiLepton_UL2018_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2018(), SkimmerDiLepton_UL2018_data_dimuon()]
      elif "EGamma" in dataStream:
        modules=[muonRocCorUL2018(), SkimmerDiLepton_UL2018_data_dielectron()]
  #
  # UL 2016APV
  #
  elif era == "UL2016APV":
    if isMC: 
      modules=[puWeight_UL2016(), muonRocCorUL2016APV(), jetCorr_AK4_UL2016APV_mc(), SkimmerDiLepton_UL2016APV_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2016APV(), SkimmerDiLepton_UL2016APV_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2016APV(), SkimmerDiLepton_UL2016APV_data_dielectron()]
  #
  # UL 2016
  #
  elif era == "UL2016":
    if isMC: 
      modules=[puWeight_UL2016(), muonRocCorUL2016(), jetCorr_AK4_UL2016_mc(), SkimmerDiLepton_UL2016_mc()]
    else:              
      if "DoubleMuon" in dataStream:
        modules=[muonRocCorUL2016(), SkimmerDiLepton_UL2016_data_dimuon()]
      elif "DoubleEG" in dataStream:
        modules=[muonRocCorUL2016(), SkimmerDiLepton_UL2016_data_dielectron()]

  return modules


