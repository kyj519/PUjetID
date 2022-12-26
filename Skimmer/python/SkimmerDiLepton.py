from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *
import math
import array
import os
import ROOT
import shutil
ROOT.PyConfig.IgnoreCommandLineOptions = True
import JERLoader

import tarfile, tempfile

from PhysicsTools.NanoAODTools.postprocessing.tools import matchObjectCollection, matchObjectCollectionMultiple
class SkimmerDiLepton(Module):
    def __init__(self, isMC, era, isDoubleElecData=False, isDoubleMuonData=False, doOTFPUJetIDBDT=False):
        
        self.era = era
        self.isULNano = True if "UL" in self.era else False
        self.isMC = isMC
        self.maxNSelJetsSaved = 1
        self.isDoubleElecData = False
        self.isDoubleMuonData = False
        if not(self.isMC):
            self.isDoubleElecData = isDoubleElecData
            self.isDoubleMuonData = isDoubleMuonData
        #
        #
        #
        self.useMuonRocCor = True
        self.muonPtDef = "pt"
        if self.useMuonRocCor:
            self.muonPtDef = "corrected_pt"
            print(
                "Use muon pt with rochester corrections applied. Branch:"+self.muonPtDef)

        #
        # Calculate PU ID BDT on-the-fly (OTF). Can only be done with for JMENano as inputs.
        #
        self.doOTFPUJetIDBDT = doOTFPUJetIDBDT
        #
        # List jet systematics
        #
        ak4Systematics = [
            "noJER",
            "jesTotalUp",
            "jesTotalDown",
            "jerUp",
            "jerDown"
        ]
        #
        #
        #
        self.jetSystsList = [""]
        if self.isMC:
            self.jetSystsList.extend(ak4Systematics)
        #
        #
        #
        self.calcBDTDiscOTF = False
        if self.doOTFPUJetIDBDT:
            if self.era == "UL2017" or self.era == "UL2018" or self.era == "UL2016APV" or self.era == "UL2016":
                self.setupTMVAReader()
                self.calcBDTDiscOTF = True 

        ########Loading Jet res file#######
        self.isDATA = not self.isMC
        isDATA = self.isDATA
        
        eraCode={"UL2016":"Summer20UL16","UL2016APV":"Summer20UL16APV","UL2017":"Summer19UL17","UL2018":"Summer19UL18"}
        verCode={"UL2016":"JRV3","UL2016APV":"JRV3","UL2017":"JRV2","UL2018":"JRV2"}
        DataOrMCCode={True:"MC",False:"MC"}
        isWhat={"Eta":"EtaResolution","Pt":"PtResolution","Phi":"PhiResolution"}
        jerInputFileName_pt = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Pt"])
        #self.jerInputFileName_eta = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Eta"])
        #self.jerInputFileName_phi = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Phi"])
        jerUncertaintyInputFileName = "%s_%s_%s_SF_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA])

        jerInputArchivePath = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/"
        if not isDATA:
            jerTag = jerInputFileName_pt[:jerInputFileName_pt.find('_MC_')+len('_MC')]
        else:
            jerTag = jerInputFileName_pt[:jerInputFileName_pt.find('_MC_')+len('_MC')]
        jerArchive = tarfile.open(jerInputArchivePath+jerTag+".tgz", "r:gz")
        jerInputFilePath = tempfile.mkdtemp()
        self.jerInputFilePath = jerInputFilePath
        jerArchive.extractall(jerInputFilePath)

        self.params_sf_and_uncertainty = ROOT.PyJetParametersWrapper()
        self.params_resolution = ROOT.PyJetParametersWrapper()

        # load libraries for accessing JER scale factors and uncertainties from txt files
        for library in ["libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools"]:
            if library not in ROOT.gSystem.GetLibraries():
                print("Load Library '%s'" % library.replace("lib", ""))
                ROOT.gSystem.Load(library)
        
        self.jer_pt  = ROOT.PyJetResolutionWrapper(os.path.join(jerInputFilePath, jerInputFileName_pt ))
        #self.jer_eta = ROOT.PyJetResolutionWrapper(os.path.join(self.jerInputFilePath, self.jerInputFileName_eta))
        #self.jer_phi = ROOT.PyJetResolutionWrapper(os.path.join(self.jerInputFilePath, self.jerInputFileName_phi))
        self.jerSF_and_Uncertainty = ROOT.PyJetResolutionScaleFactorWrapper(os.path.join(jerInputFilePath,jerUncertaintyInputFileName))


    def getJetPtResolution(self,Pt, Eta, rho):

        self.params_resolution.setJetPt(Pt)
        self.params_resolution.setJetEta(Eta)
        self.params_resolution.setRho(rho)
        self.params_sf_and_uncertainty.setJetPt(Pt)
        self.params_sf_and_uncertainty.setJetEta(Eta)
        jet_pt_resolution  = self.jer_pt.getResolution(self.params_resolution)
        jet_pt_resolution_SF = self.jerSF_and_Uncertainty.getScaleFactor(self.params_sf_and_uncertainty, 0)
        #jet_eta_resolution = self.jer_eta.getResolution(self.params_resolution)
        #jet_phi_resolution = sel_phi.getResolution(self.params_resolution)


        # debug
        #print_msg = "MC jer : {0:.4f} \t\t   MC jer SF : {1:.4f}".format(jet_pt_resolution,jet_pt_resolution_SF)
        #print(print_msg)
        return  jet_pt_resolution*jet_pt_resolution_SF

    def setupTMVAReader(self):
        self.tmvaWeightsPath = os.environ['CMSSW_BASE'] + \
            "/src/PUjetID/Skimmer/data/mvaWeights/"
        #
        # TMVA BDT weights
        #
        self.tmvaWeightFilenames = []
        # UL 2017 training weights
        if self.era == "UL2017":
            self.tmvaWeightFilenames = [
                self.tmvaWeightsPath+"pileupJetId_UL17_Eta0p0To2p5_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL17_Eta2p5To2p75_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL17_Eta2p75To3p0_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL17_Eta3p0To5p0_chs_BDT.weights.xml",
            ]
        # UL 2018 training weights
        elif self.era == "UL2018":
            self.tmvaWeightFilenames = [
                self.tmvaWeightsPath+"pileupJetId_UL18_Eta0p0To2p5_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL18_Eta2p5To2p75_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL18_Eta2p75To3p0_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL18_Eta3p0To5p0_chs_BDT.weights.xml",
            ]
        # UL 2016APV training weights
        elif self.era == "UL2016APV":
            self.tmvaWeightFilenames = [
                self.tmvaWeightsPath+"pileupJetId_UL16APV_Eta0p0To2p5_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16APV_Eta2p5To2p75_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16APV_Eta2p75To3p0_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16APV_Eta3p0To5p0_chs_BDT.weights.xml",
            ]
        # UL 2016 training weights
        elif self.era == "UL2016":
            self.tmvaWeightFilenames = [
                self.tmvaWeightsPath+"pileupJetId_UL16_Eta0p0To2p5_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16_Eta2p5To2p75_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16_Eta2p75To3p0_chs_BDT.weights.xml",
                self.tmvaWeightsPath+"pileupJetId_UL16_Eta3p0To5p0_chs_BDT.weights.xml",
            ]
        #
        # Eta bins
        #
        self.eta_bins = [
            "Eta0p0To2p5",
            "Eta2p5To2p75",
            "Eta2p75To3p0",
            "Eta3p0To5p0"
        ]
        #
        # Define variables to be provided to TMVA::Reader
        #
        self.tmva_v_nvtx = array.array("f", [-999.])
        self.tmva_v_beta = array.array("f", [-999.])
        self.tmva_v_dR2Mean = array.array("f", [-999.])
        self.tmva_v_frac01 = array.array("f", [-999.])
        self.tmva_v_frac02 = array.array("f", [-999.])
        self.tmva_v_frac03 = array.array("f", [-999.])
        self.tmva_v_frac04 = array.array("f", [-999.])
        self.tmva_v_majW = array.array("f", [-999.])
        self.tmva_v_minW = array.array("f", [-999.])
        self.tmva_v_jetR = array.array("f", [-999.])
        self.tmva_v_jetRchg = array.array("f", [-999.])
        self.tmva_v_nParticles = array.array("f", [-999.])
        self.tmva_v_nCharged = array.array("f", [-999.])
        self.tmva_v_ptD = array.array("f", [-999.])
        self.tmva_v_pull = array.array("f", [-999.])
        # NOTE: It is important that this list follows
        # the order of the variables as in the tmva weights
        # files
        self.tmva_variables = [
            ("nvtx",       self.tmva_v_nvtx),
            ("beta",        self.tmva_v_beta),
            ("dR2Mean",     self.tmva_v_dR2Mean),
            ("frac01",      self.tmva_v_frac01),
            ("frac02",      self.tmva_v_frac02),
            ("frac03",      self.tmva_v_frac03),
            ("frac04",      self.tmva_v_frac04),
            ("majW",        self.tmva_v_majW),
            ("minW",        self.tmva_v_minW),
            ("jetR",        self.tmva_v_jetR),
            ("jetRchg",     self.tmva_v_jetRchg),
            ("nParticles",  self.tmva_v_nParticles),
            ("nCharged",    self.tmva_v_nCharged),
            ("ptD",         self.tmva_v_ptD),
            ("pull",        self.tmva_v_pull),
        ]
        self.tmva_s_jetPt = array.array("f", [-999])
        self.tmva_s_jetEta = array.array("f", [-999])
        self.tmva_spectators = [
            ("jetPt",  self.tmva_s_jetPt),
            ("jetEta", self.tmva_s_jetEta),
        ]
        self.tmva_readers = []
        if len(self.eta_bins) == len(self.tmvaWeightFilenames):
            #
            # For each eta bin, setup a TMVA::Reader
            #
            for i, eta_bin in enumerate(self.eta_bins):
                #
                # Initialize TMVA::Reader
                #
                self.tmva_readers.append(ROOT.TMVA.Reader("!Color:!Silent"))
                #
                # Add spectator variables
                #
                for spec_name, spec_address in self.tmva_spectators:
                    self.tmva_readers[i].AddSpectator(spec_name, spec_address)
                #
                # Add training variables
                #
                for var_name, var_address in self.tmva_variables:
                    # For the last eta bin, we don't use the following
                    # variables in training.
                    if eta_bin == "Eta3p0To5p0":
                        if var_name == "beta":
                            continue
                        if var_name == "jetRchg":
                            continue
                        if var_name == "nCharged":
                            continue
                    self.tmva_readers[i].AddVariable(var_name, var_address)
                #
                # Book BDT
                #
                print("Setup BDT with weight file: " +
                      self.tmvaWeightFilenames[i])
                self.tmva_readers[i].BookMVA(
                    "BDT", self.tmvaWeightFilenames[i])
        else:
            raise ValueError(
                "ERROR: eta_bins length not the same as tmvaWeightFilenames length. Please check!")

    def calcPUIDBDTDisc(self, event, jet):
        #
        jet_pt = jet.pt
        jet_eta = jet.eta
        #
        self.tmva_s_jetPt[0] = jet_pt
        self.tmva_s_jetEta[0] = jet_eta
        #
        self.tmva_v_nvtx[0] = event.PV_npvsGood
        self.tmva_v_beta[0] = jet.puId_beta
        self.tmva_v_dR2Mean[0] = jet.puId_dR2Mean
        self.tmva_v_frac01[0] = jet.puId_frac01
        self.tmva_v_frac02[0] = jet.puId_frac02
        self.tmva_v_frac03[0] = jet.puId_frac03
        self.tmva_v_frac04[0] = jet.puId_frac04
        self.tmva_v_majW[0] = jet.puId_majW
        self.tmva_v_minW[0] = jet.puId_minW
        self.tmva_v_jetR[0] = jet.puId_jetR
        self.tmva_v_jetRchg[0] = jet.puId_jetRchg
        self.tmva_v_nParticles[0] = jet.nConstituents
        self.tmva_v_nCharged[0] = jet.puId_nCharged
        self.tmva_v_ptD[0] = jet.puId_ptD
        self.tmva_v_pull[0] = jet.puId_pull
        #
        # Determine which etaBin this jet is in
        #
        etaBinIdx = -1
        if abs(jet_eta) > 0.00 and abs(jet_eta) <= 2.50:
            etaBinIdx = 0
        elif abs(jet_eta) > 2.50 and abs(jet_eta) <= 2.75:
            etaBinIdx = 1
        elif abs(jet_eta) > 2.75 and abs(jet_eta) <= 3.00:
            etaBinIdx = 2
        elif abs(jet_eta) > 3.00 and abs(jet_eta) <= 5.00:
            etaBinIdx = 3
        #
        return self.tmva_readers[etaBinIdx].EvaluateMVA("BDT")

    def beginJob(self, histFile=None, histDirName=None):
        Module.beginJob(self)

    def endJob(self):
        Module.endJob(self)
        shutil.rmtree(self.jerInputFilePath)
        print("SkimmerDiLepton module ended successfully")
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
        #
        # Jet branches
        #
        for jetSyst in self.jetSystsList:
            jetSystPreFix = self.getJetSystBranchPrefix(jetSyst)
            self.out.branch(jetSystPreFix+"nJetSel", "I")
            self.out.branch(jetSystPreFix+"nJetSelPt30Eta5p0", "I")
            self.out.branch(jetSystPreFix+"nJetSelPt20Eta2p4", "I")
            # self.out.branch(jetSystPreFix+"nJetSelPt20Eta5p0", "I")#JMENano
            # self.out.branch(jetSystPreFix+"nJetSelPt10Eta2p4", "I")#JMENano
            for i in xrange(0, self.maxNSelJetsSaved):
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_jer_from_pt",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_jer_from_pt_nom",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_jer_from_pt_nano",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_bestN",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_bestN_up",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_bestN_down",         "F")				
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_bestN_up_const",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_bestN_down_const",         "F")
                self.out.branch(jetSystPreFix+"jetSel"+str(i)+"_pt_undoJER","F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_jer_CORR",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_pt",         "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_pt_nom",     "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_pt_nano",    "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_eta",        "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_phi",        "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass",       "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass_nom",   "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass_nano",  "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_jetId",      "I")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId",       "I")
                self.out.branch(jetSystPreFix+"jetSel"+str(i) +
                                "_puIdDisc",   "F")  # Starting from NanoAODv7
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puIdDiscOTF", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_qgl",        "F")
                # Starting from (UL)NanoAODv9
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_btagDeepFlavQG", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_nConst",     "I")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_chEmEF",     "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_chHEF",      "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_neEmEF",     "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_neHEF",      "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_muEF",       "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_dilep_dphi", "F")
                ########PUID Training variable#######
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_PV_npvsGood", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_beta", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_dR2Mean", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac01", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac02", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac03", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac04", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_majW", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_minW", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_jetR", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_jetRchg", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_nConstituents", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_nCharged", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_ptD", "F")
                self.out.branch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_pull", "F")
       
                if(self.isMC):
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_partflav",     "I")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_hadflav",      "I")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_closestgen_dR", "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_match",    "B")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_pt",       "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_eta",      "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_phi",      "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_mass",     "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_dR",       "F")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_partflav", "I")
                    self.out.branch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_hadflav",  "I")

    def getJetSystBranchPrefix(self, jetSyst):
        jetSystPreFix = "" if jetSyst == "" else jetSyst+"_"
        return jetSystPreFix

    def getJetPtAndMassForSyst(self, jetSyst):
        if self.isMC:
            # NOTE: For MC, we use the value from nanoAOD-tools.
            # The pt and mass systematic variation branches are saved by nanoAOD-tools.
            jetPt = "pt_nom" if jetSyst == "" else "pt_"+jetSyst
            jetMass = "mass_nom" if jetSyst == "" else "mass_"+jetSyst
            if jetSyst == "noJER":
                jetPt = "pt"
                jetMass = "mass"

        else:
            # NOTE: For data, just use the value from nanoAODs.
            # The JECs has been applied at the NanoAOD production level.
            jetPt = "pt"
            jetMass = "mass"

        return jetPt, jetMass

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
        # Get jets.
        # Skip event and don't store in tree if this selection
        # doesn't pass nominal and any systematic variations
        #
        event.passJetSelNomSyst = False

        for jetSyst in self.jetSystsList:
            self.resetJetBranches(event, jetSyst)
            if self.passJetSelection(event, jetSyst):
                event.passJetSelNomSyst |= True
            self.fillJetBranches(event, jetSyst)

        if event.passJetSelNomSyst:
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
        # event.muonsVeto = [x for x in event.muonsAll
        #                    if getattr(x, self.muonPtDef) > 10. and abs(x.eta) < 2.4
        #                    and x.looseId and x.pfIsoId >= 1 and x.isPFcand
        #                    ]
        #muons with miniisoloose
        event.muonsVeto = [x for x in event.muonsAll
                           if getattr(x, self.muonPtDef) > 10. and abs(x.eta) < 2.4
                           and x.looseId 
                           #and x.miniPFRelIso_all <= 0.4 
                           and x.isPFcand
                           ]
        event.muonsVeto.sort(key=lambda x: getattr(
            x, self.muonPtDef), reverse=True)

        #
        # Tight muon selection
        #
        # event.muonsTight = [x for x in event.muonsVeto
        #                     if getattr(x, self.muonPtDef) > 20.
        #                     and x.mediumPromptId and x.pfIsoId >= 4
        #                     ]
        #muons with minisio tight
        event.muonsTight = [x for x in event.muonsVeto
                             if getattr(x, self.muonPtDef) > 10.
                            and x.mediumPromptId 
                            #and x.miniPFRelIso_all <= 0.1
                             ]
        event.pass0VetoMuons = len(event.muonsVeto) == 0
        event.pass2VetoMuons = len(event.muonsVeto) == 2
        event.pass2TightMuons = len(event.muonsTight) == 2
        if event.pass2TightMuons and getattr(event.muonsTight[0], self.muonPtDef) <= 20.:
            event.pass2TightMuons = False
        

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
        # event.electronsTight = [x for x in event.electronsVeto
        #                         if x.pt > 20. and x.mvaFall17V2Iso_WP90
        #                         and abs(x.deltaEtaSC+x.eta) < 2.5
        #                         # ignore electrons in gap region
        #                         and not((abs(x.deltaEtaSC+x.eta) >= 1.4442) and (abs(x.deltaEtaSC+x.eta) < 1.566))
        #                         ]
        
        event.electronsTight = [x for x in event.electronsVeto
                                if x.pt > 15. and x.mvaFall17V2noIso_WP90
                                and abs(x.deltaEtaSC+x.eta) < 2.5
                                # ignore electrons in gap region
                                and not((abs(x.deltaEtaSC+x.eta) >= 1.4442) and (abs(x.deltaEtaSC+x.eta) < 1.566))
                                ]

        event.pass0VetoElectrons = len(event.electronsVeto) == 0
        event.pass2VetoElectrons = len(event.electronsVeto) == 2
        event.pass2TightElectrons = len(event.electronsTight) == 2
        if event.pass2TightElectrons and event.electronsTight[0].pt <= 25.:
            event.pass2TightElectrons = False 
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

    def getUndoJERandCORR(self,jetSyst,this_jet,return_CORR = False):
        ## note for jes and jer systematic##
        # 1.pt_nom: jer_nomVal+jes_nomVal
        # 2.pt:jes_nom
        # 3.pt_jerUp:jer_upVal+jes_NomVal
        # 4.pt_jerDown:jer_upVal+jes_NomVal
        # 5.pt_jesTotalDown: jer_nomVal+jes_downVal
        # 6.pt_jesTotalup: jer_nomVal+jes_upVal
        jetPtName, jetMassName = self.getJetPtAndMassForSyst(jetSyst)
        pt_undoJER = getattr(this_jet,'pt')
        corr = getattr(this_jet,jetPtName)/pt_undoJER
        if jetSyst=="noJER":
            pt_undoJER = getattr(this_jet,jetPtName) 
            corr = 1.
        elif 'jer' in jetSyst:
            pt_undoJER = getattr(this_jet,'pt')
            corr = getattr(this_jet,jetPtName)/pt_undoJER
        
        if 'jes' in jetSyst:
            corr = getattr(this_jet,'pt_nom')/getattr(this_jet,'pt')
            pt_undoJER = getattr(this_jet, jetPtName)/corr
        if return_CORR:
            return pt_undoJER, corr
        else:
            return pt_undoJER

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
                         if abs(x.eta) < 5. and self.getUndoJERandCORR(jetSyst,x) > jetPtCutMin
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
        if self.isMC:
            event.genJetsAll = Collection(event, "GenJet")
            event.pair = matchObjectCollection(
                event.jetsSel, event.genJetsAll, dRmax=0.4)
        #
        # Check if event passes
        # 1. <= 1 jet with pt > 30. GeV, |eta| < 5.0
        # AND
        # 2. <= 1 jet with pt > 20. GeV, |eta| < 2.4
        # NOTE: Apply this at analysis level. Save flag
        #
        event.jetsSelPt30Eta5p0 = [x for x in event.jetsSel
                                   if abs(x.eta) < 5. and self.getUndoJERandCORR(jetSyst,x) > 30.
                                   ]
        event.nJetSelPt30Eta5p0 = len(event.jetsSelPt30Eta5p0)

        event.jetsSelPt20Eta2p4 = [x for x in event.jetsSel
                                   if abs(x.eta) < 2.4 and self.getUndoJERandCORR(jetSyst,x) > 20.
                                   ]
        event.nJetSelPt20Eta2p4 = len(event.jetsSelPt20Eta2p4)

        #
        # Like above, but lower threshold. For JMENano
        #
        # event.jetsSelPt20Eta5p0 = [x for x in event.jetsSel
        #   if abs(x.eta) < 5. and getattr(x, jetPtName) > 20.
        # ]
        # event.nJetSelPt20Eta5p0=len(event.jetsSelPt20Eta5p0)

        # event.jetsSelPt10Eta2p4 = [x for x in event.jetsSel
        #   if abs(x.eta) < 2.4 and getattr(x, jetPtName) > 10.
        # ]
        # event.nJetSelPt10Eta2p4=len(event.jetsSelPt10Eta2p4)

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

    def resetJetBranches(self, event, jetSyst):
        #  reset jet branches
        jetSystPreFix = self.getJetSystBranchPrefix(jetSyst)

        self.out.fillBranch(jetSystPreFix+"nJetSel", -1)
        self.out.fillBranch(jetSystPreFix+"nJetSelPt30Eta5p0", -1)
        self.out.fillBranch(jetSystPreFix+"nJetSelPt20Eta2p4", -1)
        # self.out.fillBranch(jetSystPreFix+"nJetSelPt20Eta5p0", -1) #JMENano
        # self.out.fillBranch(jetSystPreFix+"nJetSelPt10Eta2p4", -1) #JMENano
        for i in xrange(0, self.maxNSelJetsSaved):
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt",      -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt_nom",      -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt_nano",      -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_bestN",         -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_bestN_up",         -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_bestN_down",         -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_bestN_up_const",         -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_bestN_down_const",         -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_CORR",      -9.)	
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt_undoJER", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt",      -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt_nom",  -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt_nano", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_eta",     -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_phi",     -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_mass",    -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_mass_nom", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass_nano", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jetId",  -9)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_puId",   -9)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_puIdDisc", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_qgl",    -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_nConst", -9)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_chEmEF", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_chHEF",  -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_neEmEF", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_neHEF",  -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_muEF",   -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_dilep_dphi", -9.)
            ##########PUID training var#########
            self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_PV_npvsGood", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_beta", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_dR2Mean", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_frac01", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_frac02", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_frac03", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_frac04", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_majW", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_minW", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_jetR", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_jetRchg", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_nConstituents", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_nCharged", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_ptD", -9.)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                            str(i)+"_puId_pull", -9.)
            if self.isMC:
                self.out.fillBranch(
                    jetSystPreFix+"jetSel"+str(i)+"_partflav", -9)
                self.out.fillBranch(
                    jetSystPreFix+"jetSel"+str(i)+"_hadflav", -9)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_closestgen_dR", -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_match", False)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_pt",      -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_eta",     -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_phi",     -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_mass",    -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_dR",      -9.)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_partflav", -9)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_gen_hadflav",  -9)

    def etaTruncator(self, eta):
        jeteta = eta
        if jeteta <= -4.7: jeteta = -4.69
        if jeteta >= 4.7: jeteta = 4.69

        return jeteta

    def getBestN(self,jet_pt,jet_eta):
        import os
        print(os.getcwd())
        f = ROOT.TFile('/srv/CMSSW_10_6_30/python/PUjetID/Skimmer/balanceHist.root','READ')
        histkey = '%s_best_N' % (self.era)
        hist = f.Get(histkey)
        binXn = hist.GetXaxis().FindBin(jet_pt)
        binYn = hist.GetYaxis().FindBin(jet_eta)
        binN = hist.GetBin(binXn,binYn,0)
        N = hist.GetBinContent(binN)

        return N
        
    def getBestN_asym(self,jet_pt,jet_eta):
        import os
        print(os.getcwd())
        f = ROOT.TFile('/srv/CMSSW_10_6_30/python/PUjetID/Skimmer/balanceHist_asym.root','READ')
        histkey_up = '%s_best_N_up' % (self.era)
        histkey_low = '%s_best_N_low' % (self.era)
        hist_up = f.Get(histkey_up)
        hist_low = f.Get(histkey_low)
        binXn = hist_up.GetXaxis().FindBin(jet_pt)
        binYn = hist_up.GetYaxis().FindBin(jet_eta)
        binN = hist_up.GetBin(binXn,binYn,0)
        N_up = hist_up.GetBinContent(binN)
        N_low = hist_low.GetBinContent(binN)

        return N_up, N_low

    def getBestN_asym_const(self,jet_pt,jet_eta):
        import os
        print(os.getcwd())
        f = ROOT.TFile('/srv/CMSSW_10_6_30/python/PUjetID/Skimmer/balanceHist_asym_const.root','READ')
        histkey_up = '%s_best_N_up' % (self.era)
        histkey_low = '%s_best_N_low' % (self.era)
        hist_up = f.Get(histkey_up)
        hist_low = f.Get(histkey_low)
        binXn = hist_up.GetXaxis().FindBin(jet_pt)
        binYn = hist_up.GetYaxis().FindBin(jet_eta)
        binN = hist_up.GetBin(binXn,binYn,0)
        N_up = hist_up.GetBinContent(binN)
        N_low = hist_low.GetBinContent(binN)

        return N_up, N_low
        
    
    def fillJetBranches(self, event, jetSyst):
        # fill jet branches
        jetSystPreFix = self.getJetSystBranchPrefix(jetSyst)

        # Get the name of the jet pt and jet mass branches
        # for nominal and systematic shifts
        jetPtName, jetMassName = self.getJetPtAndMassForSyst(jetSyst)

        self.out.fillBranch(jetSystPreFix+"nJetSel", event.nJetSel)
        self.out.fillBranch(jetSystPreFix+"nJetSelPt30Eta5p0",
                            event.nJetSelPt30Eta5p0)
        self.out.fillBranch(jetSystPreFix+"nJetSelPt20Eta2p4",
                            event.nJetSelPt20Eta2p4)
        # self.out.fillBranch(jetSystPreFix+"nJetSelPt20Eta5p0", event.nJetSelPt20Eta5p0) #JMENano
        # self.out.fillBranch(jetSystPreFix+"nJetSelPt10Eta2p4", event.nJetSelPt10Eta2p4) #JMENano
        for i, jet in enumerate(event.jetsSel):
            if i >= self.maxNSelJetsSaved:
                break
            rho = getattr(event,"fixedGridRhoFastjetAll")
            jer_from_pt = self.getJetPtResolution(getattr(jet,jetPtName), self.etaTruncator(jet.eta), rho)
            jer_from_pt_nom = self.getJetPtResolution(getattr(jet, "pt_nom") if self.isMC and hasattr(jet, "pt_nom") else jet.pt, self.etaTruncator(jet.eta), rho)
            jer_from_pt_nano = self.getJetPtResolution(jet.pt, self.etaTruncator(jet.eta), rho)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt",jer_from_pt)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt_nom",jer_from_pt_nom)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_from_pt_nano",jer_from_pt_nano) 
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_pt",      getattr(jet, jetPtName))
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt_nom",  getattr(
                jet, "pt_nom") if self.isMC and hasattr(jet, "pt_nom") else jet.pt)  # Fix this

            if self.isDATA:
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN",self.getBestN(jet.pt,jet.eta))
                n_up, n_down = self.getBestN_asym(jet.pt,jet.eta)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_up",n_up)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_down",n_down)
                n_up_const, n_down_const = self.getBestN_asym_const(jet.pt,jet.eta)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_up_const",n_up_const)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_down_const",n_down_const)
            else:
                pt_jerUndo, corr =  self.getUndoJERandCORR(jetSyst,jet,return_CORR = True) 
                self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_jer_CORR",  corr)  # Fix this
                self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_pt_undoJER",pt_jerUndo)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN",self.getBestN(pt_jerUndo,jet.eta))
                n_up, n_down = self.getBestN_asym(pt_jerUndo,jet.eta)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_up",n_up)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_down",n_down)
                n_up_const, n_down_const = self.getBestN_asym_const(pt_jerUndo,jet.eta)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_up_const",n_up_const)
                self.out.fillBranch(jetSystPreFix+"jetSel" + str(i)+"_bestN_down_const",n_down_const)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_pt_nano", jet.pt)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_eta",     jet.eta)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_phi",     jet.phi)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass",    getattr(jet, jetMassName))
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i)+"_mass_nom", getattr(
                jet, "mass_nom") if self.isMC and hasattr(jet, "mass_nom") else jet.mass)  # Fix this
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_mass_nano", jet.mass)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_jetId",   jet.jetId)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId",    jet.puId)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puIdDisc", jet.puIdDisc)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_qgl",     jet.qgl)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_nConst",  jet.nConstituents)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_chEmEF",  jet.chEmEF)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_chHEF",   jet.chHEF)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_neEmEF",  jet.neEmEF)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_neHEF",   jet.neHEF)
            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_muEF",    jet.muEF)
            self.out.fillBranch(jetSystPreFix+"jetSel"+str(i) +
                                "_dilep_dphi", event.dilep_p4.DeltaPhi(jet.p4()))
            if self.isULNano:
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_btagDeepFlavQG", jet.btagDeepFlavQG)
            #
            # This is where we calculate the PU BDT discriminant
            #
            jetPuIdDiscOTF = -9.
            if self.calcBDTDiscOTF:
                jetPuIdDiscOTF = self.calcPUIDBDTDisc(event, jet)
                ##########PUID training var#########
                self.out.fillBranch(jetSystPreFix+"jetSel" +str(i)+"_PV_npvsGood", event.PV_npvsGood)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_beta", jet.puId_beta)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_dR2Mean", jet.puId_dR2Mean)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac01", jet.puId_frac01)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac02", jet.puId_frac02)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac03", jet.puId_frac03)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_frac04", jet.puId_frac04)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_majW", jet.puId_majW)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_minW", jet.puId_minW)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_jetR", jet.puId_jetR)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_jetRchg", jet.puId_jetRchg)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_nConstituents", jet.nConstituents)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_nCharged", jet.puId_nCharged)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_ptD", jet.puId_ptD)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puId_pull", jet.puId_pull)

            self.out.fillBranch(jetSystPreFix+"jetSel" +
                                str(i)+"_puIdDiscOTF", jetPuIdDiscOTF)
            #
            if self.isMC:
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_partflav", jet.partonFlavour)
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_hadflav", jet.hadronFlavour)
                #
                #
                #
                closestgen_dR = 999.
                for gj in event.genJetsAll:
                    jet_gen_dR = jet.p4().DeltaR(gj.p4())
                    if jet_gen_dR < closestgen_dR:
                        closestgen_dR = jet_gen_dR
                self.out.fillBranch(jetSystPreFix+"jetSel" +
                                    str(i)+"_closestgen_dR", closestgen_dR)
                #
                #
                #
                genJet = None
                genJet = event.pair[jet]
                if not (genJet == None):
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_match", True)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_pt",   genJet.pt)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_eta",  genJet.eta)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_phi",  genJet.phi)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_mass", genJet.mass)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_dR",   jet.p4().DeltaR(genJet.p4()))
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_partflav", genJet.partonFlavour)
                    self.out.fillBranch(
                        jetSystPreFix+"jetSel"+str(i)+"_gen_hadflav",  genJet.hadronFlavour)
#
# Pre Ultra-Legacy 2016 (Compatible with NanoAODv7)
#


def SkimmerDiLepton_2016_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="2016", isDoubleElecData=True)
def SkimmerDiLepton_2016_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="2016", isDoubleMuonData=True)


def SkimmerDiLepton_2016_mc(): return SkimmerDiLepton(isMC=True,  era="2016")
#
# Pre Ultra-Legacy 2017 (Compatible with NanoAODv7)
#


def SkimmerDiLepton_2017_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="2017", isDoubleElecData=True)
def SkimmerDiLepton_2017_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="2017", isDoubleMuonData=True)


def SkimmerDiLepton_2017_mc(): return SkimmerDiLepton(isMC=True,  era="2017")
#
# Pre Ultra-Legacy 2018 (Compatible with NanoAODv7)
#


def SkimmerDiLepton_2018_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="2018", isDoubleElecData=True)


def SkimmerDiLepton_2018_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="2018", isDoubleMuonData=True)


def SkimmerDiLepton_2018_mc(): return SkimmerDiLepton(isMC=True,  era="2018")

#
# Ultra-Legacy 2017 (Compatible with ULNanoAODv9)
#


def SkimmerDiLepton_UL2017_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2017", isDoubleElecData=True)


def SkimmerDiLepton_UL2017_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2017", isDoubleMuonData=True)


def SkimmerDiLepton_UL2017_mc(): return SkimmerDiLepton(isMC=True,  era="UL2017")
#
# Ultra-Legacy 2018 (Compatible with ULNanoAODv9)
#


def SkimmerDiLepton_UL2018_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2018", isDoubleElecData=True)


def SkimmerDiLepton_UL2018_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2018", isDoubleMuonData=True)


def SkimmerDiLepton_UL2018_mc(): return SkimmerDiLepton(isMC=True,  era="UL2018")
#
# Ultra-Legacy 2016APV (Compatible with ULNanoAODv9)
#


def SkimmerDiLepton_UL2016APV_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2016APV", isDoubleElecData=True)


def SkimmerDiLepton_UL2016APV_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2016APV", isDoubleMuonData=True)


def SkimmerDiLepton_UL2016APV_mc(): return SkimmerDiLepton(
    isMC=True,  era="UL2016APV")
#
# Ultra-Legacy 2016 (Compatible with ULNanoAODv9)
#


def SkimmerDiLepton_UL2016_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2016", isDoubleElecData=True)


def SkimmerDiLepton_UL2016_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2016", isDoubleMuonData=True)


def SkimmerDiLepton_UL2016_mc(): return SkimmerDiLepton(isMC=True,  era="UL2016")

#
# Ultra-Legacy 2017 (Compatible with JMENanoV1)
#


def SkimmerDiLepton_UL2017_JMENanoV1_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2017", isDoubleElecData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2017_JMENanoV1_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2017", isDoubleMuonData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2017_JMENanoV1_mc(): return SkimmerDiLepton(
    isMC=True,  era="UL2017", doOTFPUJetIDBDT=True)


#
# Ultra-Legacy 2018 (Compatible with JMENanoV1)
#


def SkimmerDiLepton_UL2018_JMENanoV1_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2018", isDoubleElecData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2018_JMENanoV1_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2018", isDoubleMuonData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2018_JMENanoV1_mc(): return SkimmerDiLepton(
    isMC=True,  era="UL2018", doOTFPUJetIDBDT=True)


#
# Ultra-Legacy 2016 (Compatible with JMENanoV1)
#


def SkimmerDiLepton_UL2016_JMENanoV1_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2016", isDoubleElecData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2016_JMENanoV1_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2016", isDoubleMuonData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2016_JMENanoV1_mc(): return SkimmerDiLepton(
    isMC=True,  era="UL2016", doOTFPUJetIDBDT=True)


#
# Ultra-Legacy 2016APV (Compatible with JMENanoV1)
#


def SkimmerDiLepton_UL2016APV_JMENanoV1_data_dielectron(): return SkimmerDiLepton(
    isMC=False, era="UL2016APV", isDoubleElecData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2016APV_JMENanoV1_data_dimuon(): return SkimmerDiLepton(
    isMC=False, era="UL2016APV", isDoubleMuonData=True, doOTFPUJetIDBDT=True)


def SkimmerDiLepton_UL2016APV_JMENanoV1_mc(): return SkimmerDiLepton(
    isMC=True,  era="UL2016APV", doOTFPUJetIDBDT=True)