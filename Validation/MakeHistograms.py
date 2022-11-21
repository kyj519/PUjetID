#!/usr/bin/env python
import os
import glob
import collections
import copy
import itertools
import argparse
import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gROOT.LoadMacro("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/tdrstyle.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")
from helpers import *

class MyDict(collections.OrderedDict):
  def __missing__(self, key):
    val = self[key] = MyDict()
    return val
colorsDict = {
    "DY": ROOT.kGreen+1,
    "DY_REAL": ROOT.kGreen+1,
    "DY_PU": ROOT.kGreen+2,
    "TT": ROOT.kOrange+1,
    "VV": ROOT.kBlue+1,
    "Data": ROOT.kBlack
  }

prod_tag   = "DiLeptonSkim_ULNanoV9_v1p4"

EOSURL     = ""
path_inDir = "/gv0/Users/yeonjoon/ntuples_HEMFix/JetPUId_"+prod_tag+"/ntuples_skim/"



####################################################
#
#
#
######################################################
def SetupSFProducerPUJetId(fileSF, era):
    eraName = ""
    if era == "UL18": eraName = "UL2018"
    elif era == "UL17": eraName = "UL2017"
    elif era == "UL16": eraName = "UL2016"
    elif era == "UL16APV": eraName = "UL2016APV"

    ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> puIdSF_Loose(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"L\"));')
    ROOT.gInterpreter.ProcessLine('puIdSF_Loose->LoadSF();')

    ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> puIdSF_Medium(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"M\"));')
    ROOT.gInterpreter.ProcessLine('puIdSF_Medium->LoadSF();')

    ROOT.gInterpreter.Declare('std::unique_ptr<SFProducerPUJetId> puIdSF_Tight(new SFProducerPUJetId(\"'+eraName+'\",\"'+fileSF+'\",\"T\"));')
    ROOT.gInterpreter.ProcessLine('puIdSF_Tight->LoadSF();')
def ApplyBaselineSelection(df, era,syst,isMC=True):
    #
    # Event-level flags or
    #
    if syst == "central" or ('SF' in syst):
      syst_str_pre = ""
    else:
      syst_str_pre = syst+"_"
    df = df.Define("isMuMu","(abs(lep0_pdgId)==13)&&(abs(lep1_pdgId)==13)")
    df = df.Define("isElEl","(abs(lep0_pdgId)==11)&&(abs(lep1_pdgId)==11)")
  
    #
    # Baseline
    #
    df = df.Filter("passOS").Filter(syst_str_pre+"passNJetSel").Filter("isElEl") #Only muon channel at the moment

    #
    # Define the probeJet
    #
    probeJetStr=syst_str_pre+"jetSel0"
    df = df.Define("probeJet_pt",     probeJetStr+"_pt")
    df = df.Define("probeJet_eta",    probeJetStr+"_eta")
    df = df.Define("probeJet_abseta", "fabs("+probeJetStr+"_eta)")
    df = df.Define("probeJet_phi",    probeJetStr+"_phi")
    df = df.Define("probeJet_dilep_dphi", "DeltaPhi("+probeJetStr+"_dilep_dphi)")
    df = df.Define("probeJet_dilep_ptbalance", "dilep_pt/probeJet_pt")
    df = df.Define("probeJet_goodBalance", "probeJet_dilep_dphi>2.5 && probeJet_dilep_dphi<3.78")
    df = df.Define("probeJet_etaCentral", "probeJet_abseta<2.5f")
    df = df.Define("probeJet_etaForward", "probeJet_abseta>=2.5f")
    # df = df.Define("probeJet_eta2p5To3p0","probeJet_abseta>=2.5f && probeJet_abseta<3.0f")
    # df = df.Define("probeJet_eta2p5To3p0_goodBal", "probeJet_eta2p5To3p0 && probeJet_goodBalance")

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

  # def ApplyEtaSelection(df, isMC=True, etaCut="EtaInc"):
  #   if etaCut == "EtaCentral":
  #     df = df.Filter("probeJet_abseta<2.4")
  #   elif etaCut == "EtaForward":
  #     df = df.Filter("probeJet_abseta>=2.4")
  #   elif etaCut == "EtaInc":
  #     df = df.Filter("probeJet_abseta>=0.0")
  #   return df
def ApplyPUIdSelection(df, isMC=True, applyPUId=True, puIdWP="Loose", applyPUIdEffSF=False, applyPUIdMistagSF=False):

    if applyPUId:
      df = df.Filter("probeJet_puId"+puIdWP+"_pass")
      if isMC:
        if applyPUIdEffSF:
          df = df.Define("probeJet_puId_effSF",    "puIdSF_"+puIdWP+"->Get_EffSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,0)")
          df = df.Define("probeJet_puId_effSF_SF_up",    "puIdSF_"+puIdWP+"->Get_EffSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,1)")
          df = df.Define("probeJet_puId_effSF_SF_down",    "puIdSF_"+puIdWP+"->Get_EffSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,-1)")
        else:
          df = df.Define("probeJet_puId_effSF",    "1.f")
          df = df.Define("probeJet_puId_effSF_SF_up",    "1.f")
          df = df.Define("probeJet_puId_effSF_SF_down",    "1.f")
        if applyPUIdMistagSF:
          df = df.Define("probeJet_puId_mistagSF", "puIdSF_"+puIdWP+"->Get_MistagSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,0)")
          df = df.Define("probeJet_puId_mistagSF_SF_up", "puIdSF_"+puIdWP+"->Get_MistagSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,1)")
          df = df.Define("probeJet_puId_mistagSF_SF_down", "puIdSF_"+puIdWP+"->Get_MistagSF_PUID(probeJet_pt,probeJet_eta,probeJet_passGenMatch,-1)")
        else:
          df = df.Define("probeJet_puId_mistagSF", "1.f")
          df = df.Define("probeJet_puId_mistagSF_SF_up", "1.f")
          df = df.Define("probeJet_puId_mistagSF_SF_down", "1.f")
    else:
      df = df.Define("probeJet_puId_effSF", "1.f")
      df = df.Define("probeJet_puId_mistagSF", "1.f")
      df = df.Define("probeJet_puId_effSF_SF_up", "1.f")
      df = df.Define("probeJet_puId_mistagSF_SF_up", "1.f")
      df = df.Define("probeJet_puId_effSF_SF_down", "1.f")
      df = df.Define("probeJet_puId_mistagSF_SF_down", "1.f")

    return df
def ApplySelections(df, df_counts, sample, isMC, etaCutList, puIdWPList, applyPUIdEffSF=False ,applyPUIdMistagSF=False):

       
    cutCombinations =  ['_'.join(cuts) for cuts in list(itertools.product(etaCutList, puIdWPList))]
    itersyst = ['central','SF_up','SF_down','jesTotalDown','jesTotalUp']
    if sample == 'data':
      itersyst = ['central'] 
    #
    #
    #
    for syst in itersyst:
      df[sample][syst]["prePuId"] = df[sample][syst]["Baseline"]
      df_counts[sample][syst]["prePuId"] = df[sample][syst]["prePuId"].Count()
      df[sample][syst]["prePuId"] = ApplyWeights(df[sample][syst]["prePuId"], selLevel="prePuId", isMC=isMC)

      for etaCut in etaCutList:
        preCutStr="prePuId"
        cutStr=etaCut+"_prePuId"
        df[sample][syst][cutStr] = df[sample][syst][preCutStr].Filter("probeJet_"+etaCut)
        df[sample][syst][cutStr] = ApplyWeights(df[sample][syst][cutStr], selLevel="prePuId", isMC=isMC)
        df_counts[sample][syst][cutStr] = df[sample][syst][cutStr].Count()

      #
      #
      #
      for puIdWP in puIdWPList:
        preCutStr="prePuId"
        cutStr="passPuId"+puIdWP
        df[sample][syst][cutStr]  = ApplyPUIdSelection(df[sample][syst][preCutStr], isMC=isMC, applyPUId=True,  puIdWP=puIdWP, applyPUIdEffSF=applyPUIdEffSF, applyPUIdMistagSF=applyPUIdMistagSF)
        df[sample][syst][cutStr]  = ApplyWeights(df[sample][syst][cutStr], selLevel="passPuId"+puIdWP, isMC=isMC)
        df_counts[sample][syst][cutStr]  = df[sample][syst][cutStr].Count()

        for etaCut in etaCutList:
          preCutStr=etaCut+"_prePuId"
          cutStr=etaCut+"_passPuId"+puIdWP
          df[sample][syst][cutStr]  = ApplyPUIdSelection(df[sample][syst][preCutStr], isMC=isMC, applyPUId=True,  puIdWP=puIdWP,applyPUIdEffSF=applyPUIdEffSF, applyPUIdMistagSF=applyPUIdMistagSF)
          df[sample][syst][cutStr]  = ApplyWeights(df[sample][syst][cutStr], selLevel="passPuId"+puIdWP, isMC=isMC)
          df_counts[sample][syst][cutStr] = df[sample][syst][cutStr].Count()

    return df, df_counts
def ApplyWeights(df, selLevel="Baseline", isMC=True, normFactor="1.f"):
  if isMC:
    if "Baseline" in selLevel and not(df.HasColumn("evtWeight_Baseline")):
      df = df.Define("evtWeight_Baseline", "genWeight * eventWeightScale * puWeight * L1PreFiringWeight_Nom * " + normFactor)
    elif "prePuId" in selLevel and not(df.HasColumn("evtWeight_prePuId")):
      df = df.Define("evtWeight_prePuId",  "evtWeight_Baseline")
    elif "passPuIdLoose" in selLevel and not(df.HasColumn("evtWeight_passPuIdLoose")):
      df = df.Define("evtWeight_passPuIdLoose", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
      df = df.Define("evtWeight_passPuIdLoose_systUp", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systUp")
      df = df.Define("evtWeight_passPuIdLoose_systDown", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systDown")
    elif "passPuIdMedium" in selLevel and not(df.HasColumn("evtWeight_passPuIdMedium")):
      df = df.Define("evtWeight_passPuIdMedium", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
      df = df.Define("evtWeight_passPuIdMedium_systUp", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systUp")
      df = df.Define("evtWeight_passPuIdMedium_systDown", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systDown")
    elif "passPuIdTight" in selLevel and not(df.HasColumn("evtWeight_passPuIdTight")):
      df = df.Define("evtWeight_passPuIdTight", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF")
      df = df.Define("evtWeight_passPuIdTight_systUp", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systUp")
      df = df.Define("evtWeight_passPuIdTight_systDown", "evtWeight_Baseline * probeJet_puId_effSF * probeJet_puId_mistagSF_systDown")
  elif not(isMC) and not(df.HasColumn("evtWeight")):
    df = df.Define("evtWeight", "1.")

  return df

def MakePlot(histograms, histoInfos, cutName="", histoName="", dataName="", mcList=[], year="", lumi="", outDir="", extratext = '',noSF=True):
    mcListTemp = list(mcList)
    syst_list = ['central','SF_up','SF_down','jesTotalDown','jesTotalUp'] 
    syst_list_woCentral = ['SF_up','SF_down','jesTotalDown','jesTotalUp'] 
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
    h_data  = histograms[dataName]['central'][cutName][histoName]
    h_dataC = h_data.Clone(dataName+"_"+cutName+"_"+h_data.GetName())
    h_dataC.SetMarkerColor(ROOT.kBlack)
    h_dataC.SetBinErrorOption(ROOT.TH1.kPoisson)
    #
    #
    #
    histosTemp = {}
    stack_mc = {}
    h_mc_totalC = {}
    for syst in syst_list:
      stack_mc[syst] = ROOT.THStack("stack_"+histoName+"_"+cutName, histoName+"_"+cutName)
    for mc in mcListTemp:
      for syst in syst_list:
        h  = histograms[mc][syst][cutName][histoName]
        hC = h.Clone(mc+"_"+cutName+"_"+h.GetName()+"_"+syst)
        hC.SetLineColor(ROOT.kBlack)
        hC.SetLineWidth(2)
        hC.SetFillColor(colorsDict[mc])
        stack_mc[syst].Add(hC)
        
        
        histosTemp[mc][syst] = hC
    
    h_mc_totalC[syst] = stack_mc[syst].GetStack().Last().Clone(histoName+"_"+cutName+"_TotalMC"+"_"+syst)
   
    #
    #
    #
    leg.AddEntry(h_dataC,"Data","p")
    mcListTemp.reverse()
    for mc in mcListTemp:
      leg.AddEntry(histosTemp[mc]['central'],mc,"f")

    xaxistitle = histoInfos[histoName]["xaxistitle"]
    yaxistitle = "Events"

    if not os.path.exists(outDir):
      os.makedirs(outDir)
    pdfName= "%sh_%s_%s_%s"%(outDir,year,cutName,histoName)
    if noSF:
      pdfName = pdfName+'_noSF'
    syst_mc_hist = [h_mc_totalC[syst] for syst in syst_list_woCentral]
    PlotDataMC("h_"+cutName+"_"+histoName, stack_mc, h_dataC, h_mc_totalC['central'],syst_mc_hist, leg, xaxistitle, yaxistitle, year, lumi, histoInfos[histoName]["doLogy"],pdfName,extratxt=extratext)
    
def main():

  parser = argparse.ArgumentParser("")
  parser.add_argument('--era', dest='era', type=str, required=True)
  parser.add_argument('--ncores', dest='ncores', type=int)
  args = parser.parse_args()
  ncores = args.ncores
  ROOT.ROOT.EnableImplicitMT(ncores)
  era = args.era
  if era  == "UL17":
    yearStr = "UL2017" 
    lumiStr = "41.5"
  elif era  == "UL18":
    yearStr = "UL2018" 
    lumiStr = "59.8"
  elif era  == "UL16":
    yearStr = "UL2016late" 
    lumiStr = "16.8"
  elif era  == "UL16APV":
    yearStr = "UL2016early" 
    lumiStr = "19.5"
  else:
    raise Exception("Unrecognized era: "+era+". Please check!")

  MakeValidation(era,yearStr,lumiStr)

def MakeValidation(era,yearStr,lumiStr):

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
      path_inDir+"ntuple_MC"+era+"_ZZ.root"
    ],
  }

  # if era == "UL16":
  #   samples["Data"] = {
  #     "files": [
  #       path_inDir+"ntuple_DataUL16F_DoubleMuon.root",
  #       path_inDir+"ntuple_DataUL16G_DoubleMuon.root",
  #       path_inDir+"ntuple_DataUL16H_DoubleMuon.root",
  #     ],
  #   }
  #else:
  if era == "UL18":
    samples["Data"] = {
    "files": [f for f in glob.glob(path_inDir+"ntuple_Data"+era+"?_EGamma.root")]
    }
  else:
    samples["Data"] = {
      #"files": [f for f in glob.glob(path_inDir+"ntuple_Data"+era+"*_DoubleMuon.root")],
      "files": [f for f in glob.glob(path_inDir+"ntuple_Data"+era+"?_DoubleEG.root")]
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
  histoInfos["npv"] = {
    "branch": "PV_npvs",
    "model": ROOT.RDF.TH1DModel("h_npv", "", 80, 0, 80),
    "doLogy": False,
    "xaxistitle": "NPV",
  }
  histoInfos["dilep_pt"] = {
    "branch": "dilep_pt",
    "model": ROOT.RDF.TH1DModel("h_dilep_pt", "", 50, 0., 100.),
    "doLogy": False,
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
      print(file)
      inTrees[sample].Add(EOSURL+file)

  inTrees["TotalMC"] = ROOT.TChain("Events")
  for mc in mcList:
    inTrees["TotalMC"].Add(inTrees[mc])


  ####################################################
  #
  #
  #
  ######################################################
  ROOT.gROOT.LoadMacro("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/modules/Helpers.h")
  ROOT.gROOT.LoadMacro("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/modules/SFProducerPUJetId.h")
  
  ##
  ## Need to compile first in "./modules" directory 
  ## to use these
  ##
  # ROOT.gSystem.Load("modules/Helpers_h.so")
  # ROOT.gSystem.Load("modules/SFProducerPUJetId_h.so")
  SetupSFProducerPUJetId("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/data/result.root",era)

  df_pre = MyDict()
  #
  # Data
  #
  df_pre["Data"]['central']["Initial"]  = ROOT.RDataFrame(inTrees["Data"])
  df_pre["Data"]['central']["Baseline"] = ApplyBaselineSelection(df_pre["Data"]['central']["Initial"], era, 'central',isMC=False)
  df_pre["Data"]['central']["Baseline"] = ApplyWeights(df_pre["Data"]['central']["Baseline"], "Baseline", isMC=False)
  df_count_Data = df_pre["Data"]['central']["Baseline"].Count()

  #
  # Total MC
  #
  syst_list = ['central','SF_up','SF_down','jesTotalDown','jesTotalUp']
  for syst in syst_list:
    df_pre["TotalMC"][syst]["Initial"]  = ROOT.RDataFrame(inTrees["TotalMC"])
    df_pre["TotalMC"][syst]["Baseline"] = ApplyBaselineSelection(df_pre["TotalMC"][syst]["Initial"], era,syst, isMC=True)
    df_pre["TotalMC"][syst]["Baseline"] = ApplyWeights(df_pre["TotalMC"][syst]["Baseline"], "Baseline", isMC=True)
    if syst =='central':
      df_count_totalMC = df_pre["TotalMC"][syst]["Baseline"].Sum("evtWeight_Baseline")
  #
  # Get the number of events in data and MC
  #
  nevents_data  = df_count_Data.GetValue()
  print("data = %d"  %nevents_data)
  nevents_mc={}
  scalemc2data = {}
  for syst in syst_list:
    nevents_mc[syst]    = df_count_totalMC.GetValue()
    #
    # Use this number to normalize MC to number of events in data
    
    scalemc2data[syst] = nevents_data/nevents_mc
    print("mc_%s   = %.2f" %(syst,nevents_mc[syst]))
    print("scalemc2data_%s = %.3f" % (syst,scalemc2data[syst]))

  ####################################################
  #
  #
  #
  ######################################################
  df = MyDict()
  df_counts = MyDict()
  df_noSF = MyDict()
  df_counts_noSF = MyDict()
  

  etaCutList = [
    "etaCentral",
    "etaForward",
  ]
  puIdWPList = [
    "Loose",
    "Medium",
    "Tight"
  ]

  

  #====================================
  #
  # Data
  #
  #====================================
  df["Data"]['central']["Initial"]        = ROOT.RDataFrame(inTrees["Data"])

  df["Data"]['central']["Baseline"]        = ApplyBaselineSelection(df["Data"]['central']["Initial"], era, 'central',isMC=False)
  df_counts["Data"]['central']["Baseline"] = df["Data"]["Baseline"].Count()

  df_noSF["Data"]['central']["Initial"]        = ROOT.RDataFrame(inTrees["Data"])

  df_noSF["Data"]['central']["Baseline"]        = ApplyBaselineSelection(df_noSF["Data"]['central']["Initial"], era,'central', isMC=False)
  df_counts_noSF["Data"]['central']["Baseline"] = df_noSF["Data"]['central']["Baseline"].Count()

  df, df_counts = ApplySelections(df, df_counts, "Data", isMC=False, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=True,applyPUIdMistagSF=True)
  df_noSF, df_counts_noSF = ApplySelections(df_noSF, df_counts_noSF, "Data", isMC=False, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=False,applyPUIdMistagSF=False)
  #====================================
  #
  # MC
  #
  #====================================

  for sample in mcList:
    for syst in syst_list:
      df[sample][syst]["Initial"] = ROOT.RDataFrame(inTrees[sample])
      df_noSF[sample][syst]["Initial"] = ROOT.RDataFrame(inTrees[sample])
      #
      #
      #
      df[sample][syst]["Baseline"] = ApplyBaselineSelection(df[sample][syst]["Initial"], era, syst,isMC=True)
      df[sample][syst]["Baseline"] = ApplyWeights(df[sample][syst]["Baseline"], selLevel="Baseline", isMC=True, normFactor=str(scalemc2data[syst]))
      df_counts[sample][syst]["Baseline"] = df[sample][syst]["Baseline"].Sum("evtWeight_Baseline")
      
      df_noSF[sample][syst]["Baseline"] = ApplyBaselineSelection(df_noSF[sample][syst]["Initial"], era, isMC=True)
      df_noSF[sample][syst]["Baseline"] = ApplyWeights(df_noSF[sample][syst]["Baseline"], selLevel="Baseline", isMC=True, normFactor=str(scalemc2data[syst]))
      df_counts_noSF[sample][syst]["Baseline"] = df_noSF[sample][syst]["Baseline"].Sum("evtWeight_Baseline")
      #
      #
      #
      df, df_counts = ApplySelections(df, df_counts, sample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=True,applyPUIdMistagSF=True)
      df_noSF, df_counts_noSF = ApplySelections(df_noSF, df_counts_noSF, sample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=False,applyPUIdMistagSF=False)

    if "subsamples" in samples[sample]:
      for subsample in samples[sample]["subsamples"]:
        df[subsample]["Baseline"] = df[sample]["Baseline"].Filter(samples[sample]["subsamples"][subsample]["selection"])
        df_counts[subsample]["Baseline"] = df[subsample]["Baseline"].Sum("evtWeight_Baseline")
        df_noSF[subsample]["Baseline"] = df_noSF[sample]["Baseline"].Filter(samples[sample]["subsamples"][subsample]["selection"])
        df_counts_noSF[subsample]["Baseline"] = df_noSF[subsample]["Baseline"].Sum("evtWeight_Baseline")
        #
        #
        #
        df, df_counts = ApplySelections(df, df_counts, subsample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=True,applyPUIdMistagSF=True)
        df_noSF, df_counts_noSF = ApplySelections(df_noSF, df_counts_noSF, subsample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList,applyPUIdEffSF=False,applyPUIdMistagSF=False)

  cutNames = [
    "prePuId",
    "etaCentral_prePuId",
    "etaForward_prePuId",
    "passPuIdLoose",
    "passPuIdMedium",
    "passPuIdTight",
  ]
  puIdSelList = ["passPuId"+wp for wp in puIdWPList]
  cutNames +=  ['_'.join(cuts) for cuts in list(itertools.product(etaCutList, puIdSelList))]

  histograms = MyDict()
  histo1D = MyDict()
  for sample in mcListFinal+["Data"]:
    for cut in cutNames:
      for hist in histoInfos:
        hModelTemp = copy.copy(histoInfos[hist]["model"])
        hModelTemp.fName = sample+"_"+cut+"_"+histoInfos[hist]["model"].fName
        if "Data" in sample:
          histo1D[sample]['central'][cut][hist] = df[sample]['central'][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"])
        else:
          if "Baseline"         in cut: weightName = "evtWeight_Baseline"
          elif "prePuId"        in cut: weightName = "evtWeight_prePuId"
          elif "passPuIdLoose"  in cut: weightName = "evtWeight_passPuIdLoose"
          elif "passPuIdMedium" in cut: weightName = "evtWeight_passPuIdMedium"
          elif "passPuIdTight"  in cut: weightName = "evtWeight_passPuIdTight"
        
          if ("Baseline" in cut) or ("prePuId" in cut):
            histo1D[sample][syst][cut][hist] = df[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
            histo1D[sample][syst][cut][hist] = df[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
          else:
            if 'SF' in syst:
              histo1D[sample][syst][cut][hist] = df[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName+'_'+syst)
            else: 
              histo1D[sample][syst][cut][hist] = df[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)


  histograms_noSF = MyDict()
  histo1D_noSF = MyDict()
  for sample in mcListFinal+["Data"]:
    for cut in cutNames:
      for hist in histoInfos:
        hModelTemp = copy.copy(histoInfos[hist]["model"])
        hModelTemp.fName = sample+"_"+cut+"_"+histoInfos[hist]["model"].fName
        if "Data" in sample:
          histo1D_noSF[sample]['central'][cut][hist] = df_noSF[sample]['central'][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"])
        else:
          if "Baseline"         in cut: weightName = "evtWeight_Baseline"
          elif "prePuId"        in cut: weightName = "evtWeight_prePuId"
          elif "passPuIdLoose"  in cut: weightName = "evtWeight_passPuIdLoose"
          elif "passPuIdMedium" in cut: weightName = "evtWeight_passPuIdMedium"
          elif "passPuIdTight"  in cut: weightName = "evtWeight_passPuIdTight"

          if ("Baseline" in cut) or ("prePuId" in cut):
            histo1D_noSF[sample][syst][cut][hist] = df_noSF[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
            histo1D_noSF[sample][syst][cut][hist] = df_noSF[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
          else:
            if 'SF' in syst:
              histo1D_noSF[sample][syst][cut][hist] = df_noSF[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName+'_'+syst)
            else:
              histo1D_noSF[sample][syst][cut][hist] = df_noSF[sample][syst][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
  #
  # Print out Baseline yields
  #
  print("Baseline")
  for sample in mcListFinal+["Data"]:
    for syst in syst_list:
      if sample == "Data" and syst != 'central':
        continue
      nevts = df_counts[sample][syst]["Baseline"].GetValue()
      print(sample+"_"+syst+":"+str(nevts))
    

  #
  # Get histograms
  #
  for sample in mcListFinal+["Data"]:
    for cut in cutNames:
      for hist in histoInfos:
        for syst in syst_list:
          if "Data" in sample and syst != 'central': continue
          histograms[sample][syst][cut][hist] = histo1D[sample][syst][cut][hist].GetValue()
          print(syst,sample,cut)
          histograms_noSF[sample][syst][cut][hist] = histo1D_noSF[sample][syst][cut][hist].GetValue()

  ####################################################
  #
  #
  #
  ######################################################
  outDir="/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/plots_pujetid_datamc_elch/"
  outDir2="/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/plots_pujetid_datamc_noSF/"




  #
  #
  #
  for cutName in cutNames:
    for hInfo in histoInfos:
      MakePlot(histograms, histoInfos, cutName, hInfo, "Data", mcListFinal, yearStr, lumiStr, outDir, extratext='SF Applied', noSF = False)
      MakePlot(histograms_noSF, histoInfos, cutName, hInfo, "Data", mcListFinal, yearStr, lumiStr, outDir, extratext='SF #bf{Not} Applied', noSF =True)

if __name__ == '__main__':
  main()
