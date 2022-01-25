#
# Shamelessly copied from nanoAOD-tools with minor modifications
# https://github.com/cms-nanoAOD/nanoAOD-tools/blob/555b3075892c38b63a98f84527685fa042ffcf59/python/postprocessing/modules/common/muonScaleResProducer.py
#
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
import ROOT
import os
import random
ROOT.PyConfig.IgnoreCommandLineOptions = True

def mk_safe(fct, *args):
    try:
        return fct(*args)
    except Exception as e:
        if any('Error in function boost::math::erf_inv' in arg
               for arg in e.args):
            print(
                'WARNING: catching exception and returning -1. Exception arguments: %s'
                % e.args)
            return -1.
        else:
            raise e

class MuonRocCorrProducer(Module):
    def __init__(self, rc_dir, rc_corrections):
        p_skimmer = '%s/src/PUjetID/Skimmer' % os.environ['CMSSW_BASE']
        p_roccor = p_skimmer + '/data/muon/' + rc_dir
        if "/RoccoR_cc.so" not in ROOT.gSystem.GetLibraries():
            p_helper = '%s/RoccoR.cc' % p_roccor
            print('Loading C++ helper from ' + p_helper)
            ROOT.gROOT.ProcessLine('.L ' + p_helper)
        self._roccor = ROOT.RoccoR(p_roccor + '/' + rc_corrections)

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Muon_corrected_pt", "F", lenVar="nMuon")
        self.out.branch("Muon_correctedUp_pt", "F", lenVar="nMuon")
        self.out.branch("Muon_correctedDown_pt", "F", lenVar="nMuon")
        self.is_mc = bool(inputTree.GetBranch("GenJet_pt"))

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        muons = Collection(event, "Muon")
        if self.is_mc:
            genparticles = Collection(event, "GenPart")
        roccor = self._roccor
        if self.is_mc:
            pt_corr = []
            pt_err = []
            for mu in muons:
                genIdx = mu.genPartIdx
                if genIdx >= 0 and genIdx < len(genparticles):
                    genMu = genparticles[genIdx]
                    pt_corr.append(mu.pt *
                                   mk_safe(roccor.kSpreadMC, mu.charge, mu.pt,
                                           mu.eta, mu.phi, genMu.pt))
                    pt_err.append(mu.pt *
                                  mk_safe(roccor.kSpreadMCerror, mu.charge,
                                          mu.pt, mu.eta, mu.phi, genMu.pt))
                else:
                    u1 = random.uniform(0.0, 1.0)
                    pt_corr.append(
                        mu.pt * mk_safe(roccor.kSmearMC, mu.charge, mu.pt,
                                        mu.eta, mu.phi, mu.nTrackerLayers, u1))
                    pt_err.append(
                        mu.pt * mk_safe(roccor.kSmearMCerror, mu.charge, mu.pt,
                                        mu.eta, mu.phi, mu.nTrackerLayers, u1))
        else:
            pt_corr = list(
                mu.pt *
                mk_safe(roccor.kScaleDT, mu.charge, mu.pt, mu.eta, mu.phi)
                for mu in muons)
            pt_err = list(
                mu.pt *
                mk_safe(roccor.kScaleDTerror, mu.charge, mu.pt, mu.eta, mu.phi)
                for mu in muons)

        self.out.fillBranch("Muon_corrected_pt", pt_corr)
        pt_corr_up = list(
            max(pt_corr[imu] + pt_err[imu], 0.0)
            for imu, mu in enumerate(muons))
        pt_corr_down = list(
            max(pt_corr[imu] - pt_err[imu], 0.0)
            for imu, mu in enumerate(muons))
        self.out.fillBranch("Muon_correctedUp_pt", pt_corr_up)
        self.out.fillBranch("Muon_correctedDown_pt", pt_corr_down)
        return True

#
# UL
#
muonRocCorUL2016APV = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2016aUL.txt')
muonRocCorUL2016 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2016bUL.txt')
muonRocCorUL2017 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2017UL.txt')
muonRocCorUL2018 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2018UL.txt')
#
# EOY
#
muonRocCor2016 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2016.txt')
muonRocCor2017 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2017.txt')
muonRocCor2018 = lambda: MuonRocCorrProducer('roccor.Run2.v5','RoccoR2018.txt')
