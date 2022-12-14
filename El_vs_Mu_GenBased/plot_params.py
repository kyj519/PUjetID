import collections
import ROOT
class MyDict(collections.OrderedDict):
    def __missing__(self, key):
        val = self[key] = MyDict()
        return val
    
colorsDict = {
    "DY": ROOT.kGreen+1,
    "DY_REAL": ROOT.kGreen+1,
    "DY_PU": ROOT.kGreen+4,
    "TT": ROOT.kOrange+1,
    "VV": ROOT.kBlue+1,
    "Data": ROOT.kBlack
}

colorsDict_2 = {
    "DY": ROOT.kGreen+1,
    "DY_REAL": ROOT.kOrange+1,
    "DY_PU": ROOT.kOrange+4,
    "TT": ROOT.kOrange+1,
    "VV": ROOT.kBlue+1,
    "Data": ROOT.kBlack
}
def getSamples(era,path_inDir):
  samples = MyDict()
  samples["DY"] = {
    "files": [
      path_inDir+"ntuple_MC"+era+"_DY_MG.root",
    ],
    'subsamples': {
      "DY_REAL": {
        "selection": "probeJet_passGenMatch",
      },
      "DY_PU": {
        "selection": "!probeJet_passGenMatch",
      },
    }
  }
  return samples

histoInfos = MyDict()
doLogY=True ##useless line
histoInfos["npv"] = {
  "branch": "PV_npvs",
  "model": ROOT.RDF.TH1DModel("h_npv", "", 80, 0, 80),
  "doLogy": doLogY,
  "xaxistitle": "NPV",
}
histoInfos["closestgen_dR"] = {
  "branch": "probeJet_closestgen_dR",
  "model": ROOT.RDF.TH1DModel("h_probeJet_closestgen_dR", "", 60, 0.0, 1.0),
  "doLogy": doLogY,
  "xaxistitle": "Closest \Delta R(gen,reco)",
}
histoInfos["beta"] = {
  "branch": "probeJet_puId_beta",
  "model": ROOT.RDF.TH1DModel("beta", "", 30, 0, 0.1),
  "doLogy": doLogY,
  "xaxistitle": "#beta",
}
histoInfos["beta_2"] = {
  "branch": "probeJet_puId_beta",
  "model": ROOT.RDF.TH1DModel("beta_2", "", 30, 0.7, 1.0),
  "doLogy": doLogY,
  "xaxistitle": "#beta",
}
histoInfos["dR2Mean"] = {
  "branch": "probeJet_puId_dR2Mean",
  "model": ROOT.RDF.TH1DModel("beta", "", 60, 0, 0.15),
  "doLogy": doLogY,
  "xaxistitle": "mean of jet \Delta R^2 (p_T^2 weighted) ",
}
histoInfos["frac01"] = {
  "branch": "probeJet_puId_frac01",
  "model": ROOT.RDF.TH1DModel("frac01", "", 50, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "frac01",
}
histoInfos["frac02"] = {
  "branch": "probeJet_puId_frac02",
  "model": ROOT.RDF.TH1DModel("frac02", "", 50, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "frac02",
}
histoInfos["frac03"] = {
  "branch": "probeJet_puId_frac03",
  "model": ROOT.RDF.TH1DModel("frac03", "", 50, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "frac03",
}
histoInfos["frac04"] = {
  "branch": "probeJet_puId_frac04",
  "model": ROOT.RDF.TH1DModel("frac04", "", 50, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "frac04",
}
histoInfos["jetR"] = {
  "branch": "probeJet_puId_jetR",
  "model": ROOT.RDF.TH1DModel("jetR", "", 50, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "leading con. p_T fraction",
}
histoInfos["jetRchg"] = {
  "branch": "probeJet_puId_jetRchg",
  "model": ROOT.RDF.TH1DModel("jetRchg", "", 100, 0, 0.1),
  "doLogy": doLogY,
  "xaxistitle": "leading chrged con. p_T fraction",
}
histoInfos["majW"] = {
  "branch": "probeJet_puId_majW",
  "model": ROOT.RDF.TH1DModel("majW", "", 50, 0, 0.4),
  "doLogy": doLogY,
  "xaxistitle": "jet ellipsoid maj. Axis",
}
histoInfos["minW"] = {
  "branch": "probeJet_puId_minW",
  "model": ROOT.RDF.TH1DModel("minW", "", 50, 0, 0.3),
  "doLogy": doLogY,
  "xaxistitle": "jet ellipsoid min. Axis",
}
histoInfos["nCharged"] = {
  "branch": "probeJet_puId_nCharged",
  "model": ROOT.RDF.TH1DModel("nCharged", "", 40, 0, 40),
  "doLogy": doLogY,
  "xaxistitle": "n. of Charged con.",
}
histoInfos["nConstituents"] = {
  "branch": "probeJet_nConstituents",
  "model": ROOT.RDF.TH1DModel("nConstituents", "", 40, 0, 40),
  "doLogy": doLogY,
  "xaxistitle": "n. of con.",
}
histoInfos["ptD"] = {
  "branch": "probeJet_puId_ptD",
  "model": ROOT.RDF.TH1DModel("ptD", "", 30, 0, 2),
  "doLogy": doLogY,
  "xaxistitle": "p_T average p_T of con.",
}
histoInfos["pull"] = {
  "branch": "probeJet_puId_pull",
  "model": ROOT.RDF.TH1DModel("pull", "", 30, 0, 0.1),
  "doLogy": doLogY,
  "xaxistitle": "pull vector mag.",
}
histoInfos["chEmEF"] = {
  "branch": "probeJet_chEmEF",
  "model": ROOT.RDF.TH1DModel("nCharged", "", 100, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "Charge Em EF",
}
histoInfos["neEmEF"] = {
  "branch": "probeJet_neEmEF",
  "model": ROOT.RDF.TH1DModel("neEmEF", "", 100, 0, 0.6),
  "doLogy": doLogY,
  "xaxistitle": "Neutral Em EF",
}
histoInfos["chHEF"] = {
  "branch": "probeJet_chHEF",
  "model": ROOT.RDF.TH1DModel("chHEF", "", 100, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "Charge Hadron EF",
}
histoInfos["neHEF"] = {
  "branch": "probeJet_neHEF",
  "model": ROOT.RDF.TH1DModel("neHEF", "", 100, 0, 1),
  "doLogy": doLogY,
  "xaxistitle": "neutral Hadron EF",
}
histoInfos["puIdDiscOTF"] = {
  "branch": "probeJet_puIdDiscOTF",
  "model": ROOT.RDF.TH1DModel("puIdDiscOTF", "", 100, 0.5, 1),
  "doLogy": doLogY,
  "xaxistitle": "puId score on the fly",
}
histoInfos["puIdDisc"] = {
  "branch": "probeJet_puIdDisc",
  "model": ROOT.RDF.TH1DModel("puIdDisc", "", 100, 0.5, 1),
  "doLogy": doLogY,
  "xaxistitle": "puId score",
}
histoInfos["puIdDiscOTF_2"] = {
  "branch": "probeJet_puIdDiscOTF",
  "model": ROOT.RDF.TH1DModel("puIdDiscOTF", "", 100, 0, 0.5),
  "doLogy": doLogY,
  "xaxistitle": "puId score on the fly",
}
histoInfos["puIdDisc_2"] = {
  "branch": "probeJet_puIdDisc",
  "model": ROOT.RDF.TH1DModel("puIdDisc", "", 100, 0, 0.5),
  "doLogy": doLogY,
  "xaxistitle": "puId score",
}
histoInfos["pt"] = {
  "branch": "probeJet_pt",
  "model": ROOT.RDF.TH1DModel("pt", "", 100, 20, 50),
  "doLogy": doLogY,
  "xaxistitle": "p_T",
}
histoInfos["eta"] = {
  "branch": "probeJet_eta",
  "model": ROOT.RDF.TH1DModel("eta", "", 50, -5, 5),
  "doLogy": doLogY,
  "xaxistitle": "\eta",
}
histoInfos["rho"] = {
  "branch": "fixedGridRhoFastjetAll",
  "model": ROOT.RDF.TH1DModel("rho", "", 100, 0, 80),
  "doLogy": doLogY,
  "xaxistitle": "#rho",
}
# histoInfos["puIdDisc_vs_otf"] = {
#   "branch": "probeJet_puIdDisc",
#   "model": ROOT.RDF.TH1DModel("puIdDisc_vs_otf", "", 100, 0.6, 1),
#   "doLogy": doLogY,
#   "xaxistitle": "puId score",
# }