import sys
import os
import glob

import array
import ROOT
import tarfile, tempfile

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import matchObjectCollection, matchObjectCollectionMultiple

class JERLoader(Module):
	def __init__(self, era, isDATA):
		self.maxNSelJetsSaved = 1
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
		if not isDATA:
			self.jetSystsList.extend(ak4Systematics)

		eraCode={"UL2016":"Summer20UL16","UL2016APV":"Summer20UL16APV","UL2017":"Summer19UL17","UL2018":"Summer19UL18"}
		verCode={"UL2016":"JRV3","UL2016APV":"JRV3","UL2017":"JRV2","UL2018":"JRV2"}
		DataOrMCCode={True:"MC",False:"MC"}
		isWhat={"Eta":"EtaResolution","Pt":"PtResolution","Phi":"PhiResolution"}
		self.jerInputFileName_pt = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Pt"])
		#self.jerInputFileName_eta = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Eta"])
		#self.jerInputFileName_phi = "%s_%s_%s_%s_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA],isWhat["Phi"])
		self.jerUncertaintyInputFileName = "%s_%s_%s_SF_AK4PFchs.txt" % (eraCode[era],verCode[era],DataOrMCCode[isDATA])

		for library in [ "libCondFormatsJetMETObjects", "libPhysicsToolsNanoAODTools"]:
			if library not in ROOT.gSystem.GetLibraries():
				print("Load Library '%s'" % library.replace("lib", ""))
				ROOT.gSystem.Load(library)

		self.jerInputArchivePath = os.environ['CMSSW_BASE'] + "/src/PUJetID/Analyzer/data/JRDatabase/tarballs/"
		if not isDATA:
			self.jerTag = self.jerInputFileName_pt[:self.jerInputFileName_pt.find('_MC_')+len('_MC')]
		else:
			self.jerTag = self.jerInputFileName_pt[:self.jerInputFileName_pt.find('_DATA_')+len('_DATA')]
		self.jerArchive = tarfile.open(self.jerInputArchivePath+self.jerTag+".tgz", "r:gz")
		self.jerInputFilePath = tempfile.mkdtemp()
		self.jerArchive.extractall(self.jerInputFilePath)

		self.params_sf_and_uncertainty = ROOT.PyJetParametersWrapper()
		self.params_resolution = ROOT.PyJetParametersWrapper()

		self.jer_pt  = ROOT.PyJetResolutionWrapper(os.path.join(self.jerInputFilePath, self.jerInputFileName_pt ))
		#self.jer_eta = ROOT.PyJetResolutionWrapper(os.path.join(self.jerInputFilePath, self.jerInputFileName_eta))
		#self.jer_phi = ROOT.PyJetResolutionWrapper(os.path.join(self.jerInputFilePath, self.jerInputFileName_phi))
		self.jerSF_and_Uncertainty = ROOT.PyJetResolutionScaleFactorWrapper(os.path.join(self.jerInputFilePath, self.jerUncertaintyInputFileName))

	def getJetPtResolution(self, Pt, Eta, rho):

		self.params_resolution.setJetPt(Pt)
		self.params_resolution.setJetEta(Eta)
		self.params_resolution.setRho(rho)
		jet_pt_resolution  = self.jer_pt.getResolution(self.params_resolution)
		#jet_eta_resolution = self.jer_eta.getResolution(self.params_resolution)
		#jet_phi_resolution = self.jer_phi.getResolution(self.params_resolution)


		# debug
		#print_msg = "MC jer : {0:.4f} \t\t   MC jer SF : {1:.4f}".format(jet_pt_resolution,jet_pt_resolution_SF)
		#print(print_msg)
		return  jet_pt_resolution
	def beginJob(self):
		pass

	def endJob(self):
		pass
	def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
		self.out = wrappedOutputTree
		for jetsyst in self.jetSystsList:
			self.out.