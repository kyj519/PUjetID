#!/usr/bin/env python
import os
import glob
import collections
import copy
import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gROOT.LoadMacro("tdrstyle.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
from helpers import *

class MyDict(collections.OrderedDict):
  def __missing__(self, key):
    val = self[key] = MyDict()
    return val

prod_tag   = "DiLeptonSkim_ULNanoV9_v1p4"

EOSURL     = "root://eoscms.cern.ch/"
path_inDir = "/eos/cms/store/group/phys_jetmet/nbinnorj/JetPUId_"+prod_tag+"/ntuples_skim/"

ncores=4
ROOT.ROOT.EnableImplicitMT(ncores)

####################################################
#
#
#
######################################################
# era  = "UL17"
# yearStr = "UL2017" 
# lumiStr = "41.5"

era  = "UL18"
yearStr = "UL2018" 
lumiStr = "59.8"

samples = MyDict()
samples["DY"] = {
  "files" : [
    path_inDir+"ntuple_MC"+era+"_DY_AMCNLO.root",
  ],
  'subsamples':{
    "DY_REAL" : {
      "selection": "probeJet_passGenMatch",
    },
    "DY_PU" : {
      "selection": "!probeJet_passGenMatch",
    },
  }
}
samples["TT"] = {
  "files" : [
    path_inDir+"ntuple_MC"+era+"_TTTo2L2Nu.root",
  ],
}
samples["VV"] = {
  "files" : [
    path_inDir+"ntuple_MC"+era+"_WW.root",
    path_inDir+"ntuple_MC"+era+"_WZ.root",
    # path_inDir+"ntuple_MC"+era+"_ZZ.root"
  ],
}
samples["Data"] = {
  "files": [f for f in glob.glob(path_inDir+"ntuple_Data"+era+"*_DoubleMuon.root")],
}

colorsDict = {
  "DY": ROOT.kGreen+1,
  "DY_REAL": ROOT.kGreen+1,
  "DY_PU": ROOT.kGreen+2,
  "TT": ROOT.kOrange+1,
  "VV": ROOT.kBlue+1,
  "Data": ROOT.kBlack
}

sampleNames = samples.keys()

mcList = ["TT","VV","DY"]
mcListFinal = ["TT","VV","DY_PU","DY_REAL"]
####################################################
#
#
#
######################################################
histoInfos = MyDict()
histoInfos["dilep_pt"] = {
  "branch": "dilep_pt",
  "model": ROOT.RDF.TH1DModel("h_dilep_pt", "", 20, 0., 100.),
  "doLogy": True,
  "xaxistitle": "Dilep p_{T} [GeV]",
}
histoInfos["dilep_mass"] = {
  "branch": "dilep_mass",
  "model": ROOT.RDF.TH1DModel("h_dilep_mass", "", 80, 70., 110.),
  "doLogy": True,
  "xaxistitle": "Dilep mass [GeV]",
}
histoInfos["lep0_pt"] = {
  "branch": "lep0_pt",
  "model": ROOT.RDF.TH1DModel("h_lep0_pt", "", 50, 20., 120.),
  "doLogy": True,
  "xaxistitle": "lep0 p_{T} [GeV]",
}
histoInfos["lep0_eta"] = {
  "branch": "lep0_eta",
  "model": ROOT.RDF.TH1DModel("h_lep0_eta", "", 60, -3.0, 3.0),
  "doLogy": False,
  "xaxistitle": "lep0 #eta",
}
histoInfos["lep0_phi"] = {
  "branch": "lep0_phi",
  "model": ROOT.RDF.TH1DModel("h_lep0_phi", "",  80, -4.0, 4.0),
  "doLogy": False,
  "xaxistitle": "lep0 #phi",
}
histoInfos["lep1_pt"] = {
  "branch": "lep1_pt",
  "model": ROOT.RDF.TH1DModel("h_lep1_pt", "", 50, 20., 120.),
  "doLogy": True,
  "xaxistitle": "lep1 p_{T} [GeV]",
}
histoInfos["lep1_eta"] = {
  "branch": "lep1_eta",
  "model": ROOT.RDF.TH1DModel("h_lep1_eta", "", 60, -3.0, 3.0),
  "doLogy": False,
  "xaxistitle": "lep1 #eta",
}
histoInfos["lep1_phi"] = {
  "branch": "lep1_phi",
  "model": ROOT.RDF.TH1DModel("h_lep1_phi", "",  80, -4.0, 4.0),
  "doLogy": False,
  "xaxistitle": "lep1 #phi",
}
histoInfos["probeJet_pt"] = {
  "branch": "probeJet_pt",
  "model": ROOT.RDF.TH1DModel("h_probeJet_pt", "", 16, 20., 100.),
  "doLogy": True,
  "xaxistitle": "Probe jet p_{T} [GeV]",
}
histoInfos["probeJet_eta"] = {
  "branch": "probeJet_eta",
  "model": ROOT.RDF.TH1DModel("h_probeJet_eta", "", 50, -5.0, 5.0),
  "doLogy": False,
  "xaxistitle": "Probe jet #eta",
}
histoInfos["probeJet_phi"] = {
  "branch": "probeJet_phi",
  "model": ROOT.RDF.TH1DModel("h_probeJet_phi", "", 80, -4.0, 4.0),
  "doLogy": False,
  "xaxistitle": "Probe jet #phi",
}
histoInfos["probeJet_dilep_dphi"] = {
  "branch": "probeJet_dilep_dphi",
  "model": ROOT.RDF.TH1DModel("h_probeJet_dilep_dphi", "", 64, 0., 6.4),
  "doLogy": False,
  "xaxistitle": "#Delta#phi(dilep,probeJet)",
}
histoInfos["probeJet_dilep_ptbalance"] = {
  "branch": "probeJet_dilep_ptbalance",
  "model": ROOT.RDF.TH1DModel("h_probeJet_dilep_ptbalance", "", 60, 0.0, 3.0),
  "doLogy": False,
  "xaxistitle": "Probe jet p_{T} / Dilep p_{T}",
}


####################################################
#
# 
#
######################################################
inTrees = MyDict()
for sample in samples:
  inTrees[sample] = ROOT.TChain("Events")
  for file in samples[sample]["files"]:
    print file
    inTrees[sample].Add(EOSURL+file)

inTrees["TotalMC"] = ROOT.TChain("Events")
for mc in mcList:
  inTrees["TotalMC"].Add(inTrees[mc])


####################################################
#
#
#
######################################################
ROOT.gROOT.LoadMacro("./modules/Helpers.h")
ROOT.gROOT.LoadMacro("./modules/SFProducerPUJetId.h")

# ROOT.gSystem.Load("modules/Helpers_h.so")
# ROOT.gSystem.Load("modules/SFProducerPUJetId_h.so")

def SetupSFProducerPUJetId(fileSF, era):
  eraName = ""
  if era == "UL18": eraName = "UL2018"
  elif era == "UL17":eraName = "UL2017"
  elif era == "UL16":eraName = "UL2016"
  elif era == "UL16APV": eraName = "UL2016APV"

  ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> PUIdSF_Loose(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"L\"));')
  ROOT.gInterpreter.ProcessLine('PUIdSF_Loose->LoadSF();')

  ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> PUIdSF_Medium(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"M\"));')
  ROOT.gInterpreter.ProcessLine('PUIdSF_Medium->LoadSF();')

  ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> PUIdSF_Tight(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"T\"));')
  ROOT.gInterpreter.ProcessLine('PUIdSF_Tight->LoadSF();')

SetupSFProducerPUJetId("data/PUID_SFAndEff_ULNanoV9_v1p4.root",era)

def ApplyBaselineSelection(df, era, isMC=True):
  #
  # Event-level flags or
  #
  df = df.Define("isMuMu","(abs(lep0_pdgId)==13)&&(abs(lep1_pdgId)==13)")
  #
  # Baseline
  #
  df = df.Filter("passOS").Filter("passNJetSel").Filter("isMuMu") #Only muon channel at the moment

  #
  # Define the probeJet
  #
  probeJetStr="jetSel0"
  df = df.Define("probeJet_pt",     probeJetStr+"_pt")
  df = df.Define("probeJet_eta",    probeJetStr+"_eta")
  df = df.Define("probeJet_abseta", "fabs("+probeJetStr+"_eta)")
  df = df.Define("probeJet_phi",    probeJetStr+"_phi")
  df = df.Define("probeJet_dilep_dphi",     "DeltaPhi("+probeJetStr+"_dilep_dphi)")
  df = df.Define("probeJet_dilep_ptbalance","dilep_pt/probeJet_pt")
  if isMC:
    df = df.Define("probeJet_passGenMatch", probeJetStr+"_gen_match")
  if "UL16" in era:
    df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 0)")
    df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
    df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 2)")
  else:
    df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 2)")
    df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
    df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 0)")
  df = df.Define("probeJet_puIdLoose_pass",  "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Loose)")
  df = df.Define("probeJet_puIdMedium_pass", "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Medium)")
  df = df.Define("probeJet_puIdTight_pass",  "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Tight)")
  
  return df

def ApplyEtaSelection(df, isMC=True, etaCut="EtaInc"):
  if etaCut == "EtaCentral":
    df = df.Filter("probeJet_abseta<2.4")
  elif etaCut == "EtaForward":
    df = df.Filter("probeJet_abseta>=2.4")

  return df

def ApplyPUIdSelection(df, isMC=True, applyPUId=True, PUIdWP="Loose", applyPUIdEffSF=False, applyPUIdMistagSF=False):

  if applyPUId:
    df = df.Filter("probeJet_puId"+PUIdWP+"_pass")
    if isMC:
      if applyPUIdEffSF:
        df = df.Define("probeJet_puId_effSF",    "PUIdSF_"+PUIdWP+"->Get_EffSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch)")
      else:
        df = df.Define("probeJet_puId_effSF",    "1.f")
      if applyPUIdMistagSF:
        df = df.Define("probeJet_puId_mistagSF", "PUIdSF_"+PUIdWP+"->Get_MistagSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch)")
      else:
        df = df.Define("probeJet_puId_mistagSF", "1.f")
  else:
    df = df.Define("probeJet_puId_effSF", "1.f")
    df = df.Define("probeJet_puId_mistagSF", "1.f")

  return df

def ApplyWeights(df, selLevel="Baseline", weightDef="", isMC=True, normFactor="1.f"):
  if isMC:
    if "Baseline" in selLevel:
      df = df.Define("evtWeight_Baseline", "genWeight * eventWeightScale * puWeight * L1PreFiringWeight_Nom * " + normFactor)
    elif "prePuId" in selLevel:
      df = df.Define("evtWeight_prePuId",  "evtWeight_Baseline")
    elif "passPuIdLoose" in selLevel:
      df = df.Define("evtWeight_passPuIdLoose", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
    elif "passPuIdMedium" in selLevel:
      df = df.Define("evtWeight_passPuIdMedium", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
    elif "passPuIdTight" in selLevel:
      df = df.Define("evtWeight_passPuIdTight", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
  else:
    df = df.Define("evtWeight", "1.")

  return df

####################################################
#
#
#
######################################################

df_pre = MyDict()
#
# Data
#
df_pre["Data"]["Initial"]  = ROOT.RDataFrame(inTrees["Data"])
df_pre["Data"]["Baseline"] = ApplyBaselineSelection(df_pre["Data"]["Initial"], era, isMC=False)
df_pre["Data"]["Baseline"] = ApplyWeights(df_pre["Data"]["Baseline"], "Baseline", isMC=False)
df_count_Data = df_pre["Data"]["Baseline"].Count()

#
# Total MC
#
df_pre["TotalMC"]["Initial"]  = ROOT.RDataFrame(inTrees["TotalMC"])
df_pre["TotalMC"]["Baseline"] = ApplyBaselineSelection(df_pre["TotalMC"]["Initial"], era, isMC=True)
df_pre["TotalMC"]["Baseline"] = ApplyWeights(df_pre["TotalMC"]["Baseline"], "Baseline", isMC=True)
df_count_totalMC = df_pre["TotalMC"]["Baseline"].Sum("evtWeight_Baseline")
#
# Get the number of events in data and MC
#
nevents_data  = df_count_Data.GetValue()
nevents_mc    = df_count_totalMC.GetValue()
#
# Use this number to normalize MC to number of events in data
#
scalemc2data = nevents_data/nevents_mc
# scalemc2data=1.0
print("data = %d"  %nevents_data)
print("mc   = %.2f" %nevents_mc)
print("scalemc2data = %.3f" %scalemc2data)

####################################################
#
#
#
######################################################
df = MyDict()
df_counts = MyDict()

#====================================
#
# Data
#
#====================================
df["Data"]["Initial"]        = ROOT.RDataFrame(inTrees["Data"])

df["Data"]["Baseline"]        = ApplyBaselineSelection(df["Data"]["Initial"], era, isMC=False)
df_counts["Data"]["Baseline"] = df["Data"]["Baseline"].Count()

df["Data"]["prePuId"]        = df["Data"]["Baseline"]
df_counts["Data"]["prePuId"] = df["Data"]["prePuId"].Count()

df["Data"]["passPuIdLoose"]  = ApplyPUIdSelection(df["Data"]["prePuId"], isMC=False, applyPUId=True,  PUIdWP="Loose")
df_counts["Data"]["passPuIdLoose"]  = df["Data"]["passPuIdLoose"].Count()

df["Data"]["passPuIdMedium"] = ApplyPUIdSelection(df["Data"]["prePuId"], isMC=False, applyPUId=True,  PUIdWP="Medium")
df_counts["Data"]["passPuIdMedium"] = df["Data"]["passPuIdMedium"].Count()

df["Data"]["passPuIdTight"]  = ApplyPUIdSelection(df["Data"]["prePuId"], isMC=False, applyPUId=True,  PUIdWP="Tight")
df_counts["Data"]["passPuIdTight"]  = df["Data"]["passPuIdTight"].Count()
#====================================
#
# MC
#
#====================================
applyPUIdEffSF=True
applyPUIdMistagSF=True

for sample in mcList:
  df[sample]["Initial"]        = ROOT.RDataFrame(inTrees[sample])
  #
  df[sample]["Baseline"] = ApplyBaselineSelection(df[sample]["Initial"], era, isMC=True)
  df[sample]["Baseline"] = ApplyWeights(df[sample]["Baseline"], selLevel="Baseline", isMC=True, normFactor=str(scalemc2data))
  df_counts[sample]["Baseline"] = df[sample]["Baseline"].Sum("evtWeight_Baseline")
  #
  #
  #
  df[sample]["prePuId"] = df[sample]["Baseline"]
  df[sample]["prePuId"] = ApplyWeights(df[sample]["prePuId"], selLevel="prePuId", isMC=True, normFactor=str(scalemc2data))
  df_counts[sample]["prePuId"] = df[sample]["prePuId"].Sum("evtWeight_prePuId")

  #
  #
  #
  df[sample]["passPuIdLoose"] = ApplyPUIdSelection(df[sample]["prePuId"], isMC=True, applyPUId=True,  PUIdWP="Loose",  applyPUIdEffSF=applyPUIdEffSF, applyPUIdMistagSF=applyPUIdMistagSF)
  df[sample]["passPuIdLoose"] = ApplyWeights(df[sample]["passPuIdLoose"],  selLevel="passPuIdLoose",  isMC=True, normFactor=str(scalemc2data))
  df_counts[sample]["passPuIdLoose"]  = df[sample]["passPuIdLoose"].Sum("evtWeight_passPuIdLoose")

  #
  #
  #
  df[sample]["passPuIdMedium"] = ApplyPUIdSelection(df[sample]["prePuId"], isMC=True, applyPUId=True,  PUIdWP="Medium", applyPUIdEffSF=applyPUIdEffSF, applyPUIdMistagSF=applyPUIdMistagSF)
  df[sample]["passPuIdMedium"] = ApplyWeights(df[sample]["passPuIdMedium"], selLevel="passPuIdMedium", isMC=True, normFactor=str(scalemc2data))
  df_counts[sample]["passPuIdMedium"] = df[sample]["passPuIdMedium"].Sum("evtWeight_passPuIdMedium")

  #
  #
  #
  df[sample]["passPuIdTight"] = ApplyPUIdSelection(df[sample]["prePuId"], isMC=True, applyPUId=True,  PUIdWP="Tight",  applyPUIdEffSF=applyPUIdEffSF, applyPUIdMistagSF=applyPUIdMistagSF)
  df[sample]["passPuIdTight"] = ApplyWeights(df[sample]["passPuIdTight"],  selLevel="passPuIdTight",  isMC=True, normFactor=str(scalemc2data))
  df_counts[sample]["passPuIdTight"] = df[sample]["passPuIdTight"].Sum("evtWeight_passPuIdTight")

  if "subsamples" in samples[sample]:
    for subsample in samples[sample]["subsamples"]:
      df[subsample]["Baseline"] = df[sample]["Baseline"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts[subsample]["Baseline"] = df[subsample]["Baseline"].Sum("evtWeight_Baseline")

      df[subsample]["prePuId"] = df[sample]["prePuId"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts[subsample]["prePuId"] = df[subsample]["prePuId"].Sum("evtWeight_prePuId")

      df[subsample]["passPuIdLoose"] = df[sample]["passPuIdLoose"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts[subsample]["passPuIdLoose"] = df[subsample]["passPuIdLoose"].Sum("evtWeight_passPuIdLoose")

      df[subsample]["passPuIdMedium"] = df[sample]["passPuIdMedium"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts[subsample]["passPuIdMedium"] = df[subsample]["passPuIdMedium"].Sum("evtWeight_passPuIdMedium")

      df[subsample]["passPuIdTight"] = df[sample]["passPuIdTight"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts[subsample]["passPuIdTight"] = df[subsample]["passPuIdTight"].Sum("evtWeight_passPuIdTight")

cutNames = [
  "Baseline",
  "prePuId",
  "passPuIdLoose",
  "passPuIdMedium",
  "passPuIdTight",
]

weightName = "evtWeight"

histograms = MyDict()
histo1D = MyDict()
for sample in mcListFinal+["Data"]:
  for cut in cutNames:
    for hist in histoInfos:
      hModelTemp = copy.copy(histoInfos[hist]["model"])
      hModelTemp.fName = sample+"_"+cut+"_"+histoInfos[hist]["model"].fName
      if "Data" in sample:
        histo1D[sample][cut][hist] = df[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"])
      else:
        histo1D[sample][cut][hist] = df[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName+"_"+cut)

#
# Print out Baseline yields
#
print("Baseline")
for sample in mcListFinal+["Data"]:
  nevts = df_counts[sample]["Baseline"].GetValue()
  print(sample+":"+str(nevts))

#
# Get histograms
#
for sample in mcListFinal+["Data"]:
  for cut in cutNames:
    for hist in histoInfos:
      histograms[sample][cut][hist] = histo1D[sample][cut][hist].GetValue()

####################################################
#
#
#
######################################################
outDir="./plots_pujetid_datamc/"


def MakePlot(histograms, histoInfos, cutName="", histoName="", dataName="", mcList=[], year="", lumi="", outDir=""):
  mcListTemp = list(mcList)
  
  #
  #
  xLat,yLat = 0.25, 0.91
  xLeg,yLeg = xLat + 0.30, yLat
  leg_h =  0.03 * len(mcListTemp)
  leg = ROOT.TLegend( xLeg, yLeg - leg_h, xLeg + 0.35, yLeg )
  leg.SetNColumns( 2 )
  leg.SetFillStyle( 0 )
  leg.SetBorderSize( 0 )
  leg.SetTextFont( 43 )
  leg.SetTextSize( 18 )
  #
  #
  #
  h_data  = histograms[dataName][cutName][histoName]
  h_dataC = h_data.Clone(dataName+"_"+cutName+"_"+h_data.GetName())
  h_dataC.SetMarkerColor(ROOT.kBlack)
  h_dataC.SetBinErrorOption(ROOT.TH1.kPoisson)
  #
  #
  #
  histosTemp = {}
  stack_mc = ROOT.THStack("stack_"+histoName+"_"+cutName, histoName+"_"+cutName)
  for mc in mcListTemp:
    h  = histograms[mc][cutName][histoName]
    hC = h.Clone(mc+"_"+cutName+"_"+h.GetName())
    hC.SetLineColor(ROOT.kBlack)
    hC.SetLineWidth(2)
    hC.SetFillColor(colorsDict[mc])
    stack_mc.Add(hC)
    histosTemp[mc] = hC
  h_mc_totalC = stack_mc.GetStack().Last().Clone(histoName+"_"+cutName+"_TotalMC")
  #
  #
  #
  leg.AddEntry(h_dataC,"Data","p")
  mcListTemp.reverse()
  for mc in mcListTemp:
    leg.AddEntry(histosTemp[mc],mc,"f")

  xaxistitle = histoInfos[histoName]["xaxistitle"]
  yaxistitle = "Events"

  if not os.path.exists(outDir):
    os.makedirs(outDir)
  pdfName= "%sh_%s_%s_%s"%(outDir,year,cutName,histoName)
  PlotDataMC("h_"+cutName+"_"+histoName, stack_mc, h_dataC, h_mc_totalC, leg, xaxistitle, yaxistitle, year, lumi, histoInfos[histoName]["doLogy"],pdfName)

#
#
#
for cutName in cutNames:
  for hInfo in histoInfos:
    MakePlot(histograms, histoInfos, cutName, hInfo, "Data", mcListFinal, yearStr, lumiStr, outDir)


