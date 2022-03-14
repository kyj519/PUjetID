from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *
import math
import array
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


class LeptonCleanPreselector(Module):
    def __init__(self, isMC, era, isDoubleElecData=False, isDoubleMuonData=False):
        self.era = era
        self.isMC = isMC
        self.isDoubleElecData = isDoubleElecData
        self.isDoubleMuonData = isDoubleMuonData
        self.muonPtDef = "corrected_pt"  # using muon rochester corrected muon pt

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
        if not (event.passPreselNMuon or event.passPreselNElectron):
            return False

        #######################
        #
        # Muon selection
        #
        #######################
        event.muonsAll = Collection(event, "Muon")

        #
        # Veto muon selection
        #
        event.muonsVeto = [x for x in event.muonsAll
                           if getattr(x, self.muonPtDef) > 10. and abs(x.eta) < 2.4
                           and x.looseId and x.pfIsoId >= 1 and x.isPFcand
                           ]
        event.muonsVeto.sort(key=lambda x: getattr(
            x, self.muonPtDef), reverse=True)

        #
        # Tight muon selection
        #
        event.muonsTight = [x for x in event.muonsVeto
                            if getattr(x, self.muonPtDef) > 20.
                            and x.mediumPromptId and x.pfIsoId >= 4
                            ]
        event.pass0VetoMuons = len(event.muonsVeto) == 0
        event.pass2VetoMuons = len(event.muonsVeto) == 2
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
        event.electronsVeto = [x for x in event.electronsAll
                               if x.pt > 10. and x.cutBased >= 1 and abs(x.deltaEtaSC+x.eta) < 2.5
                               ]
        event.electronsVeto.sort(key=lambda x: x.pt, reverse=True)

        #
        # Tight electron selection
        #
        event.electronsTight = [x for x in event.electronsVeto
                                if x.pt > 20. and x.mvaFall17V2Iso_WP90
                                and abs(x.deltaEtaSC+x.eta) < 2.5
                                # ignore electrons in gap region
                                and not(abs(x.deltaEtaSC+x.eta) >= 1.4442) and (abs(x.deltaEtaSC+x.eta) < 1.566)
                                ]

        event.pass0VetoElectrons = len(event.electronsVeto) == 0
        event.pass2VetoElectrons = len(event.electronsVeto) == 2
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
        event.lep0_pdgId = None
        event.lep1_pdgId = None
        event.lep0_charge = None
        event.lep1_charge = None
        # ============================================
        #
        # Check if pass dimuon selection
        #
        # ============================================
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
            if getattr(event.muonsTight[0], self.muonPtDef) > 20:
                event.passLep0TrigThreshold = True
            if getattr(event.muonsTight[1], self.muonPtDef) > 10:
                event.passLep1TrigThreshold = True
            #
            # Assign lepton p4
            #
            event.lep0_p4 = event.muonsTight[0].p4(
                getattr(event.muonsTight[0], self.muonPtDef))
            event.lep1_p4 = event.muonsTight[1].p4(
                getattr(event.muonsTight[1], self.muonPtDef))
            event.lep0_charge = event.muonsTight[0].charge
            event.lep1_charge = event.muonsTight[1].charge
            event.lep0_pdgId = event.muonsTight[0].pdgId
            event.lep1_pdgId = event.muonsTight[1].pdgId
        # ============================================
        #
        # Check if pass dielectron selection
        #
        # ============================================
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
            if event.electronsTight[0].pt > 25:
                event.passLep0TrigThreshold = True
            if event.electronsTight[1].pt > 15:
                event.passLep1TrigThreshold = True
            #
            # Assign lepton p4
            #
            event.lep0_p4 = event.electronsTight[0].p4()
            event.lep1_p4 = event.electronsTight[1].p4()
            event.lep0_charge = event.electronsTight[0].charge
            event.lep1_charge = event.electronsTight[1].charge
            event.lep0_pdgId = event.electronsTight[0].pdgId
            event.lep1_pdgId = event.electronsTight[1].pdgId
        # ============================================
        #
        # Fail both channels
        #
        # ============================================
        else:
            return False

        # ============================================
        #
        # Apply trigger selection based on channel
        #
        # ============================================
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

        if not event.passLepTrigSel:
            return False

        #
        # Each selected offline lepton should be matched to HLT-level object
        #
        if not(event.passLep0TrigMatch and event.passLep1TrigMatch):
            return False

        #
        # Offline pt cut should be higher than online pt threshold
        #
        if not(event.passLep0TrigThreshold and event.passLep1TrigThreshold):
            return False

        # =====================================================================================
        #
        # Reconstruct di-lepton p4 and select events wit di-lepton mass in Z-boson mass window
        #
        # ======================================================================================
        event.dilep_p4 = event.lep0_p4 + event.lep1_p4
        return True if event.dilep_p4.M() > 70. and event.dilep_p4.M() < 110. else False

    def beignJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def passJetSelection(self, event, jetSyst=""):
        #######################
        #
        # Jets selection
        #
        #######################
        event.jetsAll = Collection(event, "Jet")
        #
        # Get the name of the jet pt and jet mass branches
        # for nominal and systematic shifts
        #
        jetPtName, jetMassName = self.getJetPtAndMassForSyst(jetSyst)

        jetPtCutMin = 20
        # jetPtCutMin=10 # JMENano can go as low as 10 GeV

        event.jetsSel = [x for x in event.jetsAll
                         if abs(x.eta) < 5. and getattr(x, jetPtName) > jetPtCutMin
                         and (x.jetId & (1 << 1))  # 'Tight' WP for jet ID
                         and x.DeltaR(event.lep0_p4) > 0.4 and x.DeltaR(event.lep1_p4) > 0.4
                         ]
        event.jetsSel.sort(key=lambda x: getattr(x, jetPtName), reverse=True)
        event.nJetSel = len(event.jetsSel)
        #
        # The event must at least have 1 jet anywhere for us to do the analysis
        #
        event.passAtLeast1Jet = event.nJetSel >= 1
        if not event.passAtLeast1Jet:
            return False
        #
        # Match genjets to the selected reco jets
        #
        #
        return True

    def passEventPreselection(self, event):

        ######trigger######
        passElTrig = self.passElectronTriggerSelection(event)
        passMuTrig = self.passMuonTriggerSelection(event)

        if passElTrig is False and passMuTrig is False:
            return False

        ######Z reco fail######
        if self.passZBosonSelection(event) is False:
            return False

		######Jet Selection#####
        event.passJetSelNomSyst = False

        for jetSyst in self.jetSystsList:
            self.resetJetBranches(event, jetSyst)
            if self.passJetSelection(event, jetSyst):
                event.passJetSelNomSyst |= True

        if event.passJetSelNomSyst:
            return True
        else:
            return False

LeptonCleanPreselector_UL2016APV_muon_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2016APV", isDoubleMuonData=True) 
LeptonCleanPreselector_UL2016_muon_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2016", isDoubleMuonData=True) 
LeptonCleanPreselector_UL2017_muon_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2017", isDoubleMuonData=True) 
LeptonCleanPreselector_UL2018_muon_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2018", isDoubleMuonData=True) 


LeptonCleanPreselector_UL2016APV_elec_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2016APV", isDoubleElecData=True) 
LeptonCleanPreselector_UL2016_elec_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2016", isDoubleElecData=True) 
LeptonCleanPreselector_UL2017_elec_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2017", isDoubleElecData=True) 
LeptonCleanPreselector_UL2018_elec_data = lambda : LeptonCleanPreselector(isMC=False, era="UL2018", isDoubleElecData=True) 

LeptonCleanPreselector_UL2016APV_mc = lambda : LeptonCleanPreselector(isMC=True, era="UL2016APV") 
LeptonCleanPreselector_UL2016_mc = lambda : LeptonCleanPreselector(isMC=True, era="UL2016") 
LeptonCleanPreselector_UL2017_mc = lambda : LeptonCleanPreselector(isMC=True, era="UL2017") 
LeptonCleanPreselector_UL2018_mc = lambda : LeptonCleanPreselector(isMC=True, era="UL2018") 