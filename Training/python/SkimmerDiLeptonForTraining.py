from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection,Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *
import math
import array
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class SkimmerDiLeptonForTraining(Module):
  def __init__(self, isMC, era, isDoubleElecData=False, isDoubleMuonData=False,):
    self.era = era
    self.isMC = isMC
    self.isDoubleElecData=False
    self.isDoubleMuonData=False
    if not(self.isMC):
      self.isDoubleElecData=isDoubleElecData
      self.isDoubleMuonData=isDoubleMuonData
    #
    #
    #
    self.useMuonRocCor = True
    self.muonPtDef = "pt"
    if self.useMuonRocCor:
      self.muonPtDef = "corrected_pt"
      print("Use muon pt with rochester corrections applied. Branch:"+self.muonPtDef)

  def beginJob(self,histFile=None,histDirName=None):
    Module.beginJob(self)

  def endJob(self):
    Module.endJob(self)
    print("SkimmerDiLeptonForTraining module ended successfully")
    pass

  def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    print("File closed successfully")
    pass

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree
    self.out.branch("dilep_pt",     "F")
    self.out.branch("dilep_eta",    "F")
    self.out.branch("dilep_phi",    "F")
    self.out.branch("dilep_mass",   "F")
    self.out.branch("lep0_pt",      "F")
    self.out.branch("lep0_eta",     "F")
    self.out.branch("lep0_phi",     "F")
    self.out.branch("lep0_mass",    "F")
    self.out.branch("lep0_charge",  "I")
    self.out.branch("lep0_pdgId",   "I")
    self.out.branch("lep1_pt",      "F")
    self.out.branch("lep1_eta",     "F")
    self.out.branch("lep1_phi",     "F")
    self.out.branch("lep1_mass",    "F")
    self.out.branch("lep1_charge",  "I")
    self.out.branch("lep1_pdgId",   "I")

    ########################################
    #
    #
    #
    ########################################
    #
    # AK4 CHS jets
    #
    lenVarJet="nJetSel"
    self.out.branch(lenVarJet,               "I")
    self.out.branch("JetSel_pt",             "F", lenVar=lenVarJet)
    self.out.branch("JetSel_eta",            "F", lenVar=lenVarJet)
    self.out.branch("JetSel_phi",            "F", lenVar=lenVarJet)
    self.out.branch("JetSel_mass",           "F", lenVar=lenVarJet)
    self.out.branch("JetSel_jetId",          "I", lenVar=lenVarJet)
    self.out.branch("JetSel_puId",           "I", lenVar=lenVarJet)
    self.out.branch("JetSel_puIdDisc",       "F", lenVar=lenVarJet)
    self.out.branch("JetSel_qgl",            "F", lenVar=lenVarJet)
    self.out.branch("JetSel_nConst",         "I", lenVar=lenVarJet)
    self.out.branch("JetSel_chEmEF",         "F", lenVar=lenVarJet)
    self.out.branch("JetSel_chHEF",          "F", lenVar=lenVarJet)
    self.out.branch("JetSel_neEmEF",         "F", lenVar=lenVarJet)
    self.out.branch("JetSel_neHEF",          "F", lenVar=lenVarJet)
    self.out.branch("JetSel_muEF",           "F", lenVar=lenVarJet)
    self.out.branch("JetSel_hfHEF",          "F", lenVar=lenVarJet)
    self.out.branch("JetSel_hfEmEF",         "F", lenVar=lenVarJet)
    self.out.branch("JetSel_dilep_dphi",     "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_beta",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_dR2Mean",   "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_frac01",    "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_frac02",    "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_frac03",    "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_frac04",    "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_majW",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_minW",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_jetR",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_jetRchg",   "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_nParticles","I", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_nCharged",  "I", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_ptD",       "F", lenVar=lenVarJet)
    self.out.branch("JetSel_puId_pull",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_qgl_axis2",      "F", lenVar=lenVarJet)
    self.out.branch("JetSel_qgl_ptD",        "F", lenVar=lenVarJet)
    self.out.branch("JetSel_qgl_mult",       "F", lenVar=lenVarJet)
    self.out.branch("JetSel_btagDeepFlavQG",            "F", lenVar=lenVarJet)
    self.out.branch("JetSel_btagDeepFlavUDS",           "F", lenVar=lenVarJet)
    self.out.branch("JetSel_particleNetAK4_QvsG",       "F", lenVar=lenVarJet)
    self.out.branch("JetSel_particleNetAK4_puIdDisc",   "F", lenVar=lenVarJet)
    if(self.isMC):
      self.out.branch("JetSel_partflav",     "I", lenVar=lenVarJet)
      self.out.branch("JetSel_hadflav",      "I", lenVar=lenVarJet)
      self.out.branch("JetSel_closestgen_dR","F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_match",    "B", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_pt",       "F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_eta",      "F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_phi",      "F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_mass",     "F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_dR",       "F", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_partflav", "I", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_hadflav",  "I", lenVar=lenVarJet)
      self.out.branch("JetSel_gen_idx",      "I", lenVar=lenVarJet)
    #
    # AK4 Puppi jets
    #
    lenVarJetPuppi="nJetPuppiSel"
    self.out.branch(lenVarJetPuppi,               "I")
    self.out.branch("JetPuppiSel_pt",             "F", lenVar=lenVarJetPuppi) 
    self.out.branch("JetPuppiSel_eta",            "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_phi",            "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_mass",           "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_jetId",          "I", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_nConst",         "I", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_chEmEF",         "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_chHEF",          "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_neEmEF",         "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_neHEF",          "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_muEF",           "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_hfHEF",          "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_hfEmEF",         "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_dilep_dphi",     "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_beta",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_dR2Mean",   "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_frac01",    "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_frac02",    "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_frac03",    "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_frac04",    "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_majW",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_minW",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_jetR",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_jetRchg",   "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_nParticles","I", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_nCharged",  "I", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_ptD",       "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_puId_pull",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_qgl_axis2",      "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_qgl_ptD",        "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_qgl_mult",       "F", lenVar=lenVarJetPuppi)
    self.out.branch("JetPuppiSel_btagDeepFlavQG",            "F", lenVar=lenVarJet)
    self.out.branch("JetPuppiSel_btagDeepFlavUDS",           "F", lenVar=lenVarJet)
    self.out.branch("JetPuppiSel_particleNetAK4_QvsG",       "F", lenVar=lenVarJet)
    self.out.branch("JetPuppiSel_particleNetAK4_puIdDisc",   "F", lenVar=lenVarJet)

    if(self.isMC):
      self.out.branch("JetPuppiSel_partflav",     "I", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_hadflav",      "I", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_closestgen_dR","F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_match",    "B", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_pt",       "F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_eta",      "F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_phi",      "F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_mass",     "F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_dR",       "F", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_partflav", "I", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_hadflav",  "I", lenVar=lenVarJetPuppi)
      self.out.branch("JetPuppiSel_gen_idx",      "I", lenVar=lenVarJetPuppi)

  def analyze(self, event):
    """process event, return True (go to next module) or False (fail, go to next event)"""
    
    if self.passEventPreselection(event) is False:
      return False
    
    #
    # Check for trigger selection. Skip event if it doesn't
    # even pass any one of them
    #
    passElTrig = self.passElectronTriggerSelection(event)
    passMuTrig = self.passMuonTriggerSelection(event)

    if passElTrig is False and passMuTrig is False:
      return False
  
    #
    # Reconstruct Z->ll and apply selection
    #
    if self.passZBosonSelection(event) is False:
      return False 
    self.fillZBosonBranches(event)
    
    #
    # Get AK4 jets. 
    #
    self.resetJetBranches(event,"JetSel")
    self.resetJetBranches(event,"JetPuppiSel")
 
    passAK4CHSJetSel   = self.passAK4CHSJetSelection(event)
    passAK4PuppiJetSel = self.passAK4PuppiJetSelection(event)

    if passAK4CHSJetSel or passAK4PuppiJetSel:
      if passAK4CHSJetSel:   self.fillJetBranches(event,"JetSel")
      if passAK4PuppiJetSel: self.fillJetBranches(event,"JetPuppiSel")
      return True
    else:
      return False

  def passEventPreselection(self, event):
    #######################
    #
    # Pre-selection
    #
    #######################
    if event.PV_npvsGood < 1:
      return False

    event.evtWeight = 1.0
    if self.isMC:
      event.evtWeight = event.genWeight

    # Event pass selection
    return True

  def passElectronTriggerSelection(self, event):
    ##############################
    #
    # Di-electron trigger selection
    #
    #############################
    event.passElectronTrig = False

    if (self.era == "2016" or self.era == "UL2016APV" or self.era == "UL2016"):
      if hasattr(event, 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ'):
        event.passElectronTrig |= event.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ
    elif (self.era == "2017" or self.era == "UL2017"):
      if hasattr(event, 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL'):
        event.passElectronTrig |= event.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL
    elif (self.era == "2018" or self.era == "UL2018"):
      if hasattr(event, 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL'):
        event.passElectronTrig |= event.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL
    
    return event.passElectronTrig
      
  def passMuonTriggerSelection(self, event):
    #############################
    #
    # Di-muon trigger selection
    #
    ############################
    event.passMuonTrig = False

    if (self.era == "2016" or self.era == "UL2016APV" or self.era == "UL2016"):
      if hasattr(event, 'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ'):
        event.passMuonTrig |= event.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ
      if hasattr(event, 'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL'):
        event.passMuonTrig |= event.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL
      if hasattr(event, 'HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL'):
        event.passMuonTrig |= event.HLT_TkMu17_TrkIsoVVL_TkMu8_TrkIsoVVL
    elif (self.era == "2017" or self.era == "UL2017"):
      if hasattr(event, 'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8'):
        event.passMuonTrig |= event.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8
    elif (self.era == "2018" or self.era == "UL2018"):
      if hasattr(event, 'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8'):
        event.passMuonTrig |= event.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8

    return event.passMuonTrig
 
  def passZBosonSelection(self, event):
    #######################
    #
    # Leptons pre-selection
    #
    #######################

    event.passPreselNMuon = event.nMuon >= 2
    event.passPreselNElectron = event.nElectron >= 2
    if not (event.passPreselNMuon or event.passPreselNElectron): return False

    #######################
    #
    # Muon selection
    #
    #######################
    event.muonsAll = Collection(event, "Muon")

    #
    # Veto muon selection
    #
    event.muonsVeto  = [x for x in event.muonsAll
      if getattr(x, self.muonPtDef) > 10. and abs(x.eta) < 2.4
      and x.looseId and x.pfIsoId >= 1 and x.isPFcand
    ]
    event.muonsVeto.sort(key=lambda x: getattr(x, self.muonPtDef), reverse=True)

    #
    # Tight muon selection
    #
    event.muonsTight  = [x for x in event.muonsVeto
      if getattr(x, self.muonPtDef) > 20. 
      and x.mediumPromptId and x.pfIsoId >= 4 
    ] 
    event.pass0VetoMuons  = len(event.muonsVeto)  == 0
    event.pass2VetoMuons  = len(event.muonsVeto)  == 2
    event.pass2TightMuons = len(event.muonsTight) == 2

    #######################
    #
    # Electron selection
    #
    #######################
    event.electronsAll = Collection(event, "Electron")

    #
    # Veto electron selection
    #
    event.electronsVeto  = [x for x in event.electronsAll
      if x.pt > 10. and x.cutBased>=1 and abs(x.deltaEtaSC+x.eta) < 2.5
    ]
    event.electronsVeto.sort(key=lambda x:x.pt,reverse=True)

    #
    # Tight electron selection
    #
    event.electronsTight  = [x for x in event.electronsVeto
      if x.pt > 20. and x.mvaFall17V2Iso_WP90
      and abs(x.deltaEtaSC+x.eta) < 2.5
      and not(abs(x.deltaEtaSC+x.eta)>=1.4442) and (abs(x.deltaEtaSC+x.eta)<1.566) # ignore electrons in gap region
    ]

    event.pass0VetoElectrons  = len(event.electronsVeto)  == 0
    event.pass2VetoElectrons  = len(event.electronsVeto)  == 2
    event.pass2TightElectrons = len(event.electronsTight) == 2
    #####################################################
    #
    # Di-lepton (Z-boson) reconstruction and selection
    #
    ####################################################
    event.passLep0TrigMatch = False
    event.passLep1TrigMatch = False
    event.passLep0TrigThreshold = False
    event.passLep1TrigThreshold = False

    event.lep0_p4 = None
    event.lep1_p4 = None
    event.dilep_p4 = None
    event.lep0_pdgId  = None
    event.lep1_pdgId  = None
    event.lep0_charge = None
    event.lep1_charge = None
    #============================================
    #
    # Check if pass dimuon selection
    #
    #============================================
    if event.pass2TightMuons and event.pass2VetoMuons and event.pass0VetoElectrons: 
      # 
      # Trigger matching
      #
      event.trigObjsAll = Collection(event, "TrigObj")
      for obj in event.trigObjsAll:
        if not(obj.id == 13):
          continue
        # if not(obj.filterBits&16): 
        #   continue    
        if(event.muonsTight[0].DeltaR(obj) < 0.1): 
          event.passLep0TrigMatch = True
        if(event.muonsTight[1].DeltaR(obj) < 0.1): 
          event.passLep1TrigMatch = True
      # 
      # Offline cuts should be tighter than trigger thresholds.
      # Could probably already be tighter than it is stated here 
      # but just check it again just to be safe.
      #
      if getattr(event.muonsTight[0], self.muonPtDef) > 20: event.passLep0TrigThreshold = True
      if getattr(event.muonsTight[1], self.muonPtDef) > 10: event.passLep1TrigThreshold = True
      # 
      # Assign lepton p4
      #
      event.lep0_p4 = event.muonsTight[0].p4(getattr(event.muonsTight[0], self.muonPtDef))
      event.lep1_p4 = event.muonsTight[1].p4(getattr(event.muonsTight[1], self.muonPtDef))
      event.lep0_charge = event.muonsTight[0].charge
      event.lep1_charge = event.muonsTight[1].charge
      event.lep0_pdgId = event.muonsTight[0].pdgId
      event.lep1_pdgId = event.muonsTight[1].pdgId
    #============================================
    #
    # Check if pass dielectron selection
    #
    #============================================
    elif event.pass2TightElectrons and event.pass2VetoElectrons and event.pass0VetoMuons: 
      # 
      # Trigger matching
      #
      event.trigObjsAll = Collection(event, "TrigObj")
      for obj in event.trigObjsAll:
        if not(obj.id == 11):
          continue
        # if not(obj.filterBits&16): 
        #   continue  
        if(event.electronsTight[0].DeltaR(obj) < 0.1): 
          event.passLep0TrigMatch = True
        if(event.electronsTight[1].DeltaR(obj) < 0.1): 
          event.passLep1TrigMatch = True
      # 
      # Offline cuts should be tighter than trigger thresholds.
      # Could probably already be tighter than it is stated here 
      # but just check it again just to be safe.
      #
      if event.electronsTight[0].pt > 25: event.passLep0TrigThreshold = True
      if event.electronsTight[1].pt > 15: event.passLep1TrigThreshold = True
      # 
      # Assign lepton p4
      #
      event.lep0_p4 = event.electronsTight[0].p4()
      event.lep1_p4 = event.electronsTight[1].p4()
      event.lep0_charge = event.electronsTight[0].charge
      event.lep1_charge = event.electronsTight[1].charge
      event.lep0_pdgId = event.electronsTight[0].pdgId
      event.lep1_pdgId = event.electronsTight[1].pdgId
    #============================================
    #
    # Fail both channels
    #
    #============================================
    else:
      return False

    #============================================
    #
    # Apply trigger selection based on channel
    #
    #============================================
    event.passLepTrigSel = False
    #
    # Check trigger by channel
    #
    if abs(event.lep0_pdgId) == 13 and abs(event.lep1_pdgId) == 13:
      # For MC
      if self.isMC:
        event.passLepTrigSel = event.passMuonTrig 
      # For Data
      else:
        event.passLepTrigSel = event.passMuonTrig if self.isDoubleMuonData else False
    elif abs(event.lep0_pdgId) == 11 and abs(event.lep1_pdgId) == 11:
      # For MC
      if self.isMC:
        event.passLepTrigSel = event.passElectronTrig
      # For Data
      else:
        event.passLepTrigSel = event.passElectronTrig if self.isDoubleElecData else False

    if not event.passLepTrigSel: return False

    #
    # Each selected offline lepton should be matched to HLT-level object
    #
    if not(event.passLep0TrigMatch and event.passLep1TrigMatch): return False
      
    #
    # Offline pt cut should be higher than online pt threshold
    #
    if not(event.passLep0TrigThreshold and event.passLep1TrigThreshold): return False

    #=====================================================================================
    #
    # Reconstruct di-lepton p4 and select events wit di-lepton mass in Z-boson mass window
    #
    #======================================================================================
    event.dilep_p4 =  event.lep0_p4 + event.lep1_p4
    return True if event.dilep_p4.M() > 70. and event.dilep_p4.M() < 110. else False

  def passAK4CHSJetSelection(self, event):
    #######################
    #
    # AK4 CHS Jets selection
    #
    #######################
    event.jetsAll = Collection(event, "Jet")

    event.jetsSel = [x for x in event.jetsAll 
      if abs(x.eta) < 5. and x.pt > 10.
      and (x.jetId & (1<<1)) # 'Tight' WP for jet ID
      and x.DeltaR(event.lep0_p4) > 0.4 and x.DeltaR(event.lep1_p4) > 0.4 
    ]
    event.jetsSel.sort(key=lambda x: x.pt, reverse=True)
    event.nJetSel=len(event.jetsSel)
    #
    # The event must at least have 1 jet anywhere for us to do the analysis
    #
    event.passAtLeast1Jet = event.nJetSel >= 1
    if not event.passAtLeast1Jet: return False
    #
    # Match genjets to the selected reco jets
    #
    # if self.isMC:
    #   event.genJetsAll = Collection(event, "GenJet")
    #   event.pairForJets = matchObjectCollection(event.jetsSel, event.genJetsAll, dRmax=0.4)
    #
    # The event pass selection
    #
    return True

  def passAK4PuppiJetSelection(self, event):
    #######################
    #
    # AK4 Puppi Jets selection
    #
    #######################
    event.jetsPuppiAll = Collection(event, "JetPuppi")

    event.jetsPuppiSel = [x for x in event.jetsPuppiAll 
      if abs(x.eta) < 5. and x.pt > 10. 
      and (x.jetId & (1<<1)) # 'Tight' WP for jet ID
      and x.DeltaR(event.lep0_p4) > 0.4 and x.DeltaR(event.lep1_p4) > 0.4 
    ]
    event.jetsPuppiSel.sort(key=lambda x:x.pt , reverse=True)
    event.nJetPuppiSel=len(event.jetsPuppiSel)
    #
    # The event must at least have 1 jet anywhere for us to do the analysis
    #
    event.passAtLeast1JetPuppi = event.nJetPuppiSel >= 1
    if not event.passAtLeast1JetPuppi: return False
    #
    # Match genjets to the selected reco jets
    #
    # if self.isMC:
    #   event.genJetsAll = Collection(event, "GenJet")
    #   event.pairForJetsPuppi = matchObjectCollection(event.jetsPuppiSel, event.genJetsAll, dRmax=0.4)
    #
    # The event pass selection
    #
    return True

  def fillZBosonBranches(self, event):
    self.out.fillBranch("dilep_pt",      event.dilep_p4.Pt())
    self.out.fillBranch("dilep_eta",     event.dilep_p4.Eta())
    self.out.fillBranch("dilep_phi",     event.dilep_p4.Phi())
    self.out.fillBranch("dilep_mass",    event.dilep_p4.M())
    self.out.fillBranch("lep0_pt",       event.lep0_p4.Pt())
    self.out.fillBranch("lep0_eta",      event.lep0_p4.Eta())
    self.out.fillBranch("lep0_phi",      event.lep0_p4.Phi())
    self.out.fillBranch("lep0_mass",     event.lep0_p4.M())
    self.out.fillBranch("lep0_charge",   event.lep0_charge)
    self.out.fillBranch("lep0_pdgId",    event.lep0_pdgId)
    self.out.fillBranch("lep1_pt",       event.lep1_p4.Pt())
    self.out.fillBranch("lep1_eta",      event.lep1_p4.Eta())
    self.out.fillBranch("lep1_phi",      event.lep1_p4.Phi())
    self.out.fillBranch("lep1_mass",     event.lep1_p4.M())
    self.out.fillBranch("lep1_charge",   event.lep1_charge)
    self.out.fillBranch("lep1_pdgId",    event.lep1_pdgId)

  def resetJetBranches(self, event, jetColl="JetSel"):
    self.out.fillBranch("n"+jetColl+"",             0)
    self.out.fillBranch(jetColl+"_pt",              [])
    self.out.fillBranch(jetColl+"_eta",             [])
    self.out.fillBranch(jetColl+"_phi",             [])
    self.out.fillBranch(jetColl+"_mass",            [])
    self.out.fillBranch(jetColl+"_jetId",           [])
    if jetColl == "JetSel":
      self.out.fillBranch(jetColl+"_puId",          [])
      self.out.fillBranch(jetColl+"_puIdDisc",      []) 
      self.out.fillBranch(jetColl+"_qgl",           []) 
    self.out.fillBranch(jetColl+"_nConst",          [])
    self.out.fillBranch(jetColl+"_chEmEF",          [])
    self.out.fillBranch(jetColl+"_chHEF",           [])
    self.out.fillBranch(jetColl+"_neEmEF",          [])
    self.out.fillBranch(jetColl+"_neHEF",           [])
    self.out.fillBranch(jetColl+"_muEF",            [])
    self.out.fillBranch(jetColl+"_hfHEF",           [])
    self.out.fillBranch(jetColl+"_hfEmEF",          [])
    self.out.fillBranch(jetColl+"_dilep_dphi",      [])
    self.out.fillBranch(jetColl+"_puId_beta",       [])
    self.out.fillBranch(jetColl+"_puId_dR2Mean",    [])
    self.out.fillBranch(jetColl+"_puId_frac01",     [])
    self.out.fillBranch(jetColl+"_puId_frac02",     [])
    self.out.fillBranch(jetColl+"_puId_frac03",     [])
    self.out.fillBranch(jetColl+"_puId_frac04",     [])
    self.out.fillBranch(jetColl+"_puId_majW",       [])
    self.out.fillBranch(jetColl+"_puId_minW",       [])
    self.out.fillBranch(jetColl+"_puId_jetR",       [])
    self.out.fillBranch(jetColl+"_puId_jetRchg",    [])
    self.out.fillBranch(jetColl+"_puId_nParticles", [])
    self.out.fillBranch(jetColl+"_puId_nCharged",   [])
    self.out.fillBranch(jetColl+"_puId_ptD",        [])
    self.out.fillBranch(jetColl+"_puId_pull",       [])
    self.out.fillBranch(jetColl+"_qgl_axis2",       [])
    self.out.fillBranch(jetColl+"_qgl_ptD",         [])
    self.out.fillBranch(jetColl+"_qgl_mult",        [])
    self.out.fillBranch(jetColl+"_btagDeepFlavQG",          [])
    self.out.fillBranch(jetColl+"_btagDeepFlavUDS",         [])
    self.out.fillBranch(jetColl+"_particleNetAK4_QvsG",     [])
    self.out.fillBranch(jetColl+"_particleNetAK4_puIdDisc", [])
    if self.isMC:
      self.out.fillBranch(jetColl+"_partflav",      [])
      self.out.fillBranch(jetColl+"_hadflav",       [])
      self.out.fillBranch(jetColl+"_closestgen_dR", [])
      self.out.fillBranch(jetColl+"_gen_match",     [])
      self.out.fillBranch(jetColl+"_gen_pt",        [])
      self.out.fillBranch(jetColl+"_gen_eta",       [])
      self.out.fillBranch(jetColl+"_gen_phi",       [])
      self.out.fillBranch(jetColl+"_gen_mass",      [])
      self.out.fillBranch(jetColl+"_gen_dR",        [])
      self.out.fillBranch(jetColl+"_gen_partflav",  [])
      self.out.fillBranch(jetColl+"_gen_hadflav",   [])
      self.out.fillBranch(jetColl+"_gen_idx",       [])

  def fillJetBranches(self, event, jetColl="JetSel"):

    jet_pt = []
    jet_eta = []
    jet_phi = []
    jet_mass = []

    jet_jetId = []
    jet_puId = []
    jet_puIdDisc = []
    jet_qgl = []

    jet_nConstituents = []
    jet_chEmEF = []
    jet_chHEF = []
    jet_neEmEF = []
    jet_neHEF = []
    jet_muEF = []
    jet_hfHEF = []
    jet_hfEmEF = []

    jet_dilep_dphi = []

    jet_puId_beta = []
    jet_puId_dR2Mean = []
    jet_puId_frac01 = []
    jet_puId_frac02 = []
    jet_puId_frac03 = []
    jet_puId_frac04 = []
    jet_puId_majW = []
    jet_puId_minW = []
    jet_puId_jetR = []
    jet_puId_jetRchg = []
    jet_puId_nParticles = []
    jet_puId_nCharged = []
    jet_puId_ptD = []
    jet_puId_pull = []

    jet_qgl_axis2 = []
    jet_qgl_ptD = []
    jet_qgl_mult = []

    jet_btagDeepFlavQG = []
    jet_btagDeepFlavUDS = []
    jet_particleNetAK4_QvsG = []
    jet_particleNetAK4_puIdDisc = []

    jet_partonFlavour = []
    jet_hadronFlavour = []
    jet_closestgen_dR = []
    jet_gen_match = []
    jet_gen_pt = []
    jet_gen_eta = []
    jet_gen_phi = []
    jet_gen_mass = []
    jet_gen_dR = []
    jet_gen_partflav = []
    jet_gen_hadflav = []
    jet_gen_idx = []
 
    jetSelColl = None
    if jetColl == "JetSel":
      jetSelColl = event.jetsSel
    else: 
      jetSelColl = event.jetsPuppiSel
    
    event.genJetsAll = None
    if self.isMC:
      event.genJetsAll = Collection(event, "GenJet")

    for i, jet in enumerate(jetSelColl):
      jet_pt.append(jet.pt)
      jet_eta.append(jet.eta)
      jet_phi.append(jet.phi)
      jet_mass.append(jet.mass)
      jet_jetId.append(jet.jetId)
      if jetColl == "JetSel":
        jet_puId.append(jet.puId)
        jet_puIdDisc.append(jet.puIdDisc)
        jet_qgl.append(jet.qgl)
      jet_nConstituents.append(jet.nConstituents)
      jet_chEmEF.append(jet.chEmEF)
      jet_chHEF.append(jet.chHEF)
      jet_neEmEF.append(jet.neEmEF)
      jet_neHEF.append(jet.neHEF)
      jet_muEF.append(jet.muEF)
      jet_hfHEF.append(jet.hfHEF)
      jet_hfEmEF.append(jet.hfEmEF)
      jet_dilep_dphi.append(event.dilep_p4.DeltaPhi(jet.p4()))
      jet_puId_beta.append(jet.puId_beta)
      jet_puId_dR2Mean.append(jet.puId_dR2Mean)
      jet_puId_frac01.append(jet.puId_frac01)
      jet_puId_frac02.append(jet.puId_frac02)
      jet_puId_frac03.append(jet.puId_frac03)
      jet_puId_frac04.append(jet.puId_frac04)
      jet_puId_majW.append(jet.puId_majW)
      jet_puId_minW.append(jet.puId_minW)
      jet_puId_jetR.append(jet.puId_jetR)
      jet_puId_jetRchg.append(jet.puId_jetRchg)
      jet_puId_nParticles.append(jet.nConstituents)
      jet_puId_nCharged.append(jet.puId_nCharged)
      jet_puId_ptD.append(jet.puId_ptD)
      jet_puId_pull.append(jet.puId_pull)
      jet_qgl_axis2.append(jet.qgl_axis2)
      jet_qgl_ptD.append(jet.qgl_ptD)
      jet_qgl_mult.append(jet.qgl_mult)
      jet_btagDeepFlavQG.append(jet.btagDeepFlavQG)
      jet_btagDeepFlavUDS.append(jet.btagDeepFlavUDS)
      jet_particleNetAK4_QvsG.append(jet.particleNetAK4_QvsG)
      jet_particleNetAK4_puIdDisc.append(jet.particleNetAK4_puIdDisc)
      
      if self.isMC:
        jet_partonFlavour.append(jet.partonFlavour)
        jet_hadronFlavour.append(jet.hadronFlavour)

        closestgen_dR = 999.
        for gj in event.genJetsAll:
          thisjet_gen_dR = jet.p4().DeltaR(gj.p4())
          if thisjet_gen_dR < closestgen_dR: closestgen_dR = thisjet_gen_dR
        jet_closestgen_dR.append(closestgen_dR)
         
        # genJet = None
        # if jetColl == "JetSel":
        #   genJet = event.pairForJets[jet]
        # elif jetColl == "JetPuppiSel":
        #   genJet = event.pairForJetsPuppi[jet]
        
        genJet = None
        if jet.genJetIdx >= 0 and jet.genJetIdx < len(event.genJetsAll):
          genJet = event.genJetsAll[jet.genJetIdx]

        if genJet:
          jet_gen_match.append(True)
          jet_gen_pt.append(genJet.pt)
          jet_gen_eta.append(genJet.eta)
          jet_gen_phi.append(genJet.phi)
          jet_gen_mass.append(genJet.mass)
          jet_gen_dR.append(jet.p4().DeltaR(genJet.p4()))
          jet_gen_partflav.append(genJet.partonFlavour)
          jet_gen_hadflav.append(genJet.hadronFlavour)
        else:
          jet_gen_match.append(False)
          jet_gen_pt.append(-1.)
          jet_gen_eta.append(-9.)
          jet_gen_phi.append(-9.)
          jet_gen_mass.append(-1.)
          jet_gen_dR.append(-9)
          jet_gen_partflav.append(-99)
          jet_gen_hadflav.append(-99)
        jet_gen_idx.append(jet.genJetIdx)
    
    self.out.fillBranch("n"+jetColl,                getattr(event,"n"+jetColl))
    self.out.fillBranch(jetColl+"_pt",              jet_pt)
    self.out.fillBranch(jetColl+"_eta",             jet_eta)
    self.out.fillBranch(jetColl+"_phi",             jet_phi)
    self.out.fillBranch(jetColl+"_mass",            jet_mass)
    self.out.fillBranch(jetColl+"_jetId",           jet_jetId)
    if jetColl == "JetSel":
      self.out.fillBranch(jetColl+"_puId",          jet_puId)
      self.out.fillBranch(jetColl+"_puIdDisc",        jet_puIdDisc)
      self.out.fillBranch(jetColl+"_qgl",           jet_qgl)
    self.out.fillBranch(jetColl+"_nConst",          jet_nConstituents)
    self.out.fillBranch(jetColl+"_chEmEF",          jet_chEmEF)
    self.out.fillBranch(jetColl+"_chHEF",           jet_chHEF)
    self.out.fillBranch(jetColl+"_neEmEF",          jet_neEmEF)
    self.out.fillBranch(jetColl+"_neHEF",           jet_neHEF)
    self.out.fillBranch(jetColl+"_muEF",            jet_muEF)
    self.out.fillBranch(jetColl+"_hfHEF",           jet_hfHEF)
    self.out.fillBranch(jetColl+"_hfEmEF",          jet_hfEmEF)
    self.out.fillBranch(jetColl+"_dilep_dphi",      jet_dilep_dphi)
    self.out.fillBranch(jetColl+"_puId_beta",       jet_puId_beta)
    self.out.fillBranch(jetColl+"_puId_dR2Mean",    jet_puId_dR2Mean)
    self.out.fillBranch(jetColl+"_puId_frac01",     jet_puId_frac01)
    self.out.fillBranch(jetColl+"_puId_frac02",     jet_puId_frac02)
    self.out.fillBranch(jetColl+"_puId_frac03",     jet_puId_frac03)
    self.out.fillBranch(jetColl+"_puId_frac04",     jet_puId_frac04)
    self.out.fillBranch(jetColl+"_puId_majW",       jet_puId_majW)
    self.out.fillBranch(jetColl+"_puId_minW",       jet_puId_minW)
    self.out.fillBranch(jetColl+"_puId_jetR",       jet_puId_jetR)
    self.out.fillBranch(jetColl+"_puId_jetRchg",    jet_puId_jetRchg)
    self.out.fillBranch(jetColl+"_puId_nParticles", jet_puId_nParticles)
    self.out.fillBranch(jetColl+"_puId_nCharged",   jet_puId_nCharged)
    self.out.fillBranch(jetColl+"_puId_ptD",        jet_puId_ptD)
    self.out.fillBranch(jetColl+"_puId_pull",       jet_puId_pull)
    self.out.fillBranch(jetColl+"_qgl_axis2",       jet_qgl_axis2)
    self.out.fillBranch(jetColl+"_qgl_ptD",         jet_qgl_ptD)
    self.out.fillBranch(jetColl+"_qgl_mult",        jet_qgl_mult)
    self.out.fillBranch(jetColl+"_btagDeepFlavQG",          jet_btagDeepFlavQG)
    self.out.fillBranch(jetColl+"_btagDeepFlavUDS",         jet_btagDeepFlavUDS)
    self.out.fillBranch(jetColl+"_particleNetAK4_QvsG",     jet_particleNetAK4_QvsG)
    self.out.fillBranch(jetColl+"_particleNetAK4_puIdDisc", jet_particleNetAK4_puIdDisc)
    if self.isMC:
      self.out.fillBranch(jetColl+"_partflav",      jet_partonFlavour)
      self.out.fillBranch(jetColl+"_hadflav",       jet_hadronFlavour)
      self.out.fillBranch(jetColl+"_closestgen_dR", jet_closestgen_dR)
      self.out.fillBranch(jetColl+"_gen_match",     jet_gen_match)
      self.out.fillBranch(jetColl+"_gen_pt",        jet_gen_pt)
      self.out.fillBranch(jetColl+"_gen_eta",       jet_gen_eta)
      self.out.fillBranch(jetColl+"_gen_phi",       jet_gen_phi)
      self.out.fillBranch(jetColl+"_gen_mass",      jet_gen_mass)
      self.out.fillBranch(jetColl+"_gen_dR",        jet_gen_dR)
      self.out.fillBranch(jetColl+"_gen_partflav",  jet_gen_partflav)
      self.out.fillBranch(jetColl+"_gen_hadflav",   jet_gen_hadflav)
      self.out.fillBranch(jetColl+"_gen_idx",       jet_gen_idx)

#
# Ultra-Legacy 2016 APV (Compatible with JMENanoV9)
#
SkimmerDiLeptonForTraining_UL2016APV_data_dielectron = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2016APV", isDoubleElecData=True)
SkimmerDiLeptonForTraining_UL2016APV_data_dimuon = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2016APV", isDoubleMuonData=True) 
SkimmerDiLeptonForTraining_UL2016APV_mc = lambda : SkimmerDiLeptonForTraining(isMC=True,  era="UL2016APV") 

#
# Ultra-Legacy 2016 (Compatible with JMENanoV9)
#
SkimmerDiLeptonForTraining_UL2016_data_dielectron = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2016", isDoubleElecData=True)
SkimmerDiLeptonForTraining_UL2016_data_dimuon = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2016", isDoubleMuonData=True) 
SkimmerDiLeptonForTraining_UL2016_mc = lambda : SkimmerDiLeptonForTraining(isMC=True,  era="UL2016") 

#
# Ultra-Legacy 2017 (Compatible with JMENanoV9)
#
SkimmerDiLeptonForTraining_UL2017_data_dielectron = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2017", isDoubleElecData=True)
SkimmerDiLeptonForTraining_UL2017_data_dimuon = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2017", isDoubleMuonData=True) 
SkimmerDiLeptonForTraining_UL2017_mc = lambda : SkimmerDiLeptonForTraining(isMC=True,  era="UL2017") 

#
# Ultra-Legacy 2018 (Compatible with JMENanoV9)
#
SkimmerDiLeptonForTraining_UL2018_data_dielectron = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2018", isDoubleElecData=True)
SkimmerDiLeptonForTraining_UL2018_data_dimuon = lambda : SkimmerDiLeptonForTraining(isMC=False, era="UL2018", isDoubleMuonData=True) 
SkimmerDiLeptonForTraining_UL2018_mc = lambda : SkimmerDiLeptonForTraining(isMC=True,  era="UL2018") 
