#!/usr/bin/env python
from helpers import PlotDataMC
import plot_params
import os
import glob
import collections
import copy
import itertools
import argparse
import ROOT

from plot_params import colorsDict, colorsDict_2, histoInfos, getSamples
ROOT.gROOT.SetBatch(True)

ROOT.gROOT.LoadMacro(
    "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/tdrstyle.C")
ROOT.gROOT.ProcessLine("setTDRStyle();")

class MyDict(collections.OrderedDict):
    def __missing__(self, key):
        val = self[key] = MyDict()
        return val



prod_tag = "DiLeptonSkim_ULNanoV9_v1p4"
EOSURL = ""
path_inDir = "/gv0/Users/yeonjoon/ntuples_JMENano_DiLepton_Reskim/JetPUId_"+prod_tag+"/ntuples_skim/"


def ApplyBaselineSelection(df, era, syst, isMu):
    #
    # Event-level flags or
    #
    if syst == "central" or ('SF' in syst):
        syst_str_pre = ""
    else:
        syst_str_pre = syst+"_"
    df = df.Define("isMuMu", "(abs(lep0_pdgId)==13)&&(abs(lep1_pdgId)==13)")
    df = df.Define("isElEl", "(abs(lep0_pdgId)==11)&&(abs(lep1_pdgId)==11)")

    #
    # Baseline
    #
    if isMu:
        # Only muon channel at the moment
        df = df.Filter("passOS").Filter(
            syst_str_pre+"passNJetSel").Filter("isMuMu")
    else:
        df = df.Filter("passOS").Filter(
            syst_str_pre+"passNJetSel").Filter("isElEl")
    #
    # Define the probeJet
    #
    probeJetStr = syst_str_pre+"jetSel0"
    df = df.Define("probeJet_pt",     probeJetStr+"_pt")
    df = df.Define("probeJet_eta",    probeJetStr+"_eta")
    df = df.Define("probeJet_abseta", "fabs("+probeJetStr+"_eta)")
    df = df.Define("probeJet_phi",    probeJetStr+"_phi")
    df = df.Define("probeJet_dilep_dphi",
                   "DeltaPhi("+probeJetStr+"_dilep_dphi)")
    df = df.Define("probeJet_dilep_ptbalance", "dilep_pt/probeJet_pt")
    df = df.Define("probeJet_goodBalance",
                   "probeJet_dilep_dphi>2.5 && probeJet_dilep_dphi<3.78")
    df = df.Define("probeJet_etaCentral", "probeJet_abseta<2.5f")
    df = df.Define("probeJet_etaForward", "probeJet_abseta>=2.5f")
    # df = df.Define("probeJet_eta2p5To3p0","probeJet_abseta>=2.5f && probeJet_abseta<3.0f")
    # df = df.Define("probeJet_eta2p5To3p0_goodBal", "probeJet_eta2p5To3p0 && probeJet_goodBalance")
    isMC =1 
    
    if isMC:
        df = df.Define("probeJet_passGenMatch", probeJetStr+"_gen_match")
    if "UL16" in era:
        df = df.Define("probeJet_puIdFlag_Loose",
                       probeJetStr+"_puId & (1 << 0)")
        df = df.Define("probeJet_puIdFlag_Medium",
                       probeJetStr+"_puId & (1 << 1)")
        df = df.Define("probeJet_puIdFlag_Tight",
                       probeJetStr+"_puId & (1 << 2)")
    else:
        df = df.Define("probeJet_puIdFlag_Loose",
                       probeJetStr+"_puId & (1 << 2)")
        df = df.Define("probeJet_puIdFlag_Medium",
                       probeJetStr+"_puId & (1 << 1)")
        df = df.Define("probeJet_puIdFlag_Tight",
                       probeJetStr+"_puId & (1 << 0)")
    df = df.Define("probeJet_puIdLoose_pass",
                   "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Loose)")
    df = df.Define("probeJet_puIdMedium_pass",
                   "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Medium)")
    df = df.Define("probeJet_puIdTight_pass",
                   "(probeJet_pt >= 50.f) || (probeJet_pt < 50.f && probeJet_puIdFlag_Tight)")
    df = df.Define("probeJet_closestgen_dR",probeJetStr+"_closestgen_dR")
    df = df.Define("probeJet_puId_beta",probeJetStr+"_puId_beta")
    df = df.Define("probeJet_puId_dR2Mean",probeJetStr+"_puId_dR2Mean")
    df = df.Define("probeJet_puId_frac01",probeJetStr+"_puId_frac01")
    df = df.Define("probeJet_puId_frac02",probeJetStr+"_puId_frac02")
    df = df.Define("probeJet_puId_frac03",probeJetStr+"_puId_frac03")
    df = df.Define("probeJet_puId_frac04",probeJetStr+"_puId_frac04")
    df = df.Define("probeJet_puId_majW",probeJetStr+"_puId_majW")
    df = df.Define("probeJet_puId_minW",probeJetStr+"_puId_minW")
    df = df.Define("probeJet_puId_jetR",probeJetStr+"_puId_jetR")
    df = df.Define("probeJet_puId_jetRchg",probeJetStr+"_puId_jetRchg")
    df = df.Define("probeJet_nConstituents",probeJetStr+"_nConstituents")
    df = df.Define("probeJet_puId_nCharged",probeJetStr+"_puId_nCharged")
    df = df.Define("probeJet_puId_ptD",probeJetStr+"_puId_ptD")
    df = df.Define("probeJet_puId_pull",probeJetStr+"_puId_pull")
    df = df.Define("probeJet_chEmEF",probeJetStr+"_chEmEF")
    df = df.Define("probeJet_chHEF",probeJetStr+"_chHEF")
    df = df.Define("probeJet_neEmEF",probeJetStr+"_neEmEF")
    df = df.Define("probeJet_neHEF",probeJetStr+"_neHEF")
    df = df.Define("probeJet_muEF",probeJetStr+"_muEF")
    df = df.Define("probeJet_puIdDiscOTF",probeJetStr+"_puIdDiscOTF")
    df = df.Define("probeJet_puIdDisc",probeJetStr+"_puIdDisc")
    
    return df


def ApplyPUIdSelection(df, isMC=True, applyPUId=True, puIdWP="Loose"):

    if applyPUId:
      df = df.Filter("probeJet_puId"+puIdWP+"_pass")

    return df


def ApplySelections(df, df_counts, sample, isMC, etaCutList, puIdWPList):

  cutCombinations = ['_'.join(cuts) for cuts in list(itertools.product(etaCutList, puIdWPList))]
  #
  #
  #

  df[sample]["prePuId"] = df[sample]["Baseline"]
  df_counts[sample]["prePuId"] = df[sample]["prePuId"].Count()
  df[sample]["prePuId"] = ApplyWeights(
      df[sample]["prePuId"], selLevel="prePuId", isMC=isMC)

  for etaCut in etaCutList:
      preCutStr = "prePuId"
      cutStr = etaCut+"_prePuId"
      df[sample][cutStr] = df[sample][preCutStr].Filter("probeJet_"+etaCut)
      df[sample][cutStr] = ApplyWeights(
          df[sample][cutStr], selLevel="prePuId", isMC=isMC)
      df_counts[sample][cutStr] = df[sample][cutStr].Count()

  #
  #
  #
  for puIdWP in puIdWPList:
    preCutStr = "prePuId"
    cutStr = "passPuId"+puIdWP
    df[sample][cutStr] = ApplyPUIdSelection(df[sample][preCutStr], isMC=isMC, applyPUId=True,
                                            puIdWP=puIdWP)
    df[sample][cutStr] = ApplyWeights(
        df[sample][cutStr], selLevel="passPuId"+puIdWP, isMC=isMC)
    df_counts[sample][cutStr] = df[sample][cutStr].Count()
    for etaCut in etaCutList:
      preCutStr = etaCut+"_prePuId"
      cutStr = etaCut+"_passPuId"+puIdWP
      df[sample][cutStr] = ApplyPUIdSelection(df[sample][preCutStr], isMC=isMC, applyPUId=True,
                                                puIdWP=puIdWP)
      df[sample][cutStr] = ApplyWeights(df[sample][cutStr], selLevel="passPuId"+puIdWP, isMC=isMC)
      df_counts[sample][cutStr] = df[sample][cutStr].Count()

  return df, df_counts


def ApplyWeights(df, selLevel="Baseline", isMC=True, normFactor="1.f"):
  if isMC:
    if "Baseline" in selLevel and not (df.HasColumn("evtWeight_Baseline")):
      df = df.Define("evtWeight_Baseline",
                     "genWeight * eventWeightScale * puWeight * L1PreFiringWeight_Nom * " + normFactor)
    elif "prePuId" in selLevel and not (df.HasColumn("evtWeight_prePuId")):
      df = df.Define("evtWeight_prePuId",  "evtWeight_Baseline")
    elif "passPuIdLoose" in selLevel and not (df.HasColumn("evtWeight_passPuIdLoose")):
      df = df.Define("evtWeight_passPuIdLoose", "evtWeight_Baseline")
    elif "passPuIdMedium" in selLevel and not (df.HasColumn("evtWeight_passPuIdMedium")):
      df = df.Define("evtWeight_passPuIdMedium", "evtWeight_Baseline")
    elif "passPuIdTight" in selLevel and not (df.HasColumn("evtWeight_passPuIdTight")):
      df = df.Define("evtWeight_passPuIdTight", "evtWeight_Baseline")
  elif not (isMC) and not (df.HasColumn("evtWeight")):
    df = df.Define("evtWeight", "1.")

  return df


def MakePlot(doLogY,histograms_El,histograms_Mu, histoInfos, cutName="", histoName="", dataName="", mcList=[], year="", lumi="", outDir="", extratext=''):
    mcListTemp = list(mcList)

    xLat, yLat = 0.25, 0.91
    xLeg, yLeg = xLat + 0.30, yLat
    leg_h = 0.03 * len(mcListTemp)
    leg = ROOT.TLegend(xLeg, yLeg - leg_h, xLeg + 0.35, yLeg)
    leg.SetNColumns(2)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(43)
    leg.SetTextSize(18)

    histosTemp_El = {}
    histosTemp_Mu = {}



    stack_mc_El = ROOT.THStack("stack_"+histoName+"_" +cutName+"_El", histoName+"_"+cutName+"_El")
    stack_mc_Mu = ROOT.THStack("stack_"+histoName+"_" +cutName+"_Mu", histoName+"_"+cutName+"_Mu")
    stack_mc_all = ROOT.THStack("stack_"+histoName+"_" +cutName, histoName+"_"+cutName)
    
    for mc in mcListTemp:
      alpha = 0 if mc == 'DY_REAL' else 0.5
      h_El = histograms_El[mc][cutName][histoName]
      hC_El = h_El.Clone(mc+"_"+cutName+"_"+h_El.GetName())
      hC_El.SetLineColor(colorsDict[mc])
      hC_El.SetLineWidth(2)
      hC_El.SetFillColorAlpha(colorsDict[mc],alpha)
      hC_El.SetMarkerSize(0)
    
      stack_mc_El.Add(hC_El)
      histosTemp_El[mc] = hC_El
      h_mc_totalC_El = stack_mc_El.GetStack().Last().Clone(histoName+"_"+cutName+"_TotalMC_El")
      h_Mu = histograms_Mu[mc][cutName][histoName]
      hC_Mu = h_Mu.Clone(mc+"_"+cutName+"_"+h_Mu.GetName())
      hC_Mu.SetLineColor(colorsDict_2[mc])
      hC_Mu.SetLineWidth(2)
      hC_Mu.SetFillColorAlpha(colorsDict_2[mc],alpha)
      hC_Mu.SetMarkerSize(0)
      stack_mc_Mu.Add(hC_Mu)
      histosTemp_Mu[mc] = hC_Mu
      h_mc_totalC_Mu = stack_mc_Mu.GetStack().Last().Clone(histoName+"_"+cutName+"_TotalMC_Mu")
      stack_mc_all.Add(hC_Mu)
      stack_mc_all.Add(hC_El)

    #
    #
    #
    mcListTemp.reverse()
    for mc in mcListTemp:
      leg.AddEntry(histosTemp_Mu[mc], mc+"_Mu", "f")
      leg.AddEntry(histosTemp_El[mc], mc+"_El", "f")

    xaxistitle = histoInfos[histoName]["xaxistitle"]
    yaxistitle = "Events"

    if not os.path.exists("%sh_%s/%s" % (outDir, year, cutName)):
      os.makedirs("%sh_%s/%s" % (outDir, year, cutName))
    pdfName = "%sh_%s/%s/%s" % (outDir, year, cutName, histoName)
    PlotDataMC("h_"+cutName+"_"+histoName, stack_mc_all,stack_mc_El, h_mc_totalC_El,stack_mc_Mu, h_mc_totalC_Mu,
                leg, xaxistitle, yaxistitle, year, lumi, pdfName, doLogY,extratxt=extratext)


def main():

  parser = argparse.ArgumentParser("")
  parser.add_argument('--era', dest='era', type=str, required=True)
  parser.add_argument('--ncores', dest='ncores', type=int)
  parser.add_argument('--doLogY', dest='doLogY', default=False,action='store_true')
  args = parser.parse_args()
  ncores = args.ncores
  ROOT.ROOT.EnableImplicitMT(ncores)
  era = args.era
  doLogY = args.doLogY
  if era == "UL17":
    yearStr = "UL2017"
    lumiStr = "41.5"
  elif era == "UL18":
    yearStr = "UL2018"
    lumiStr = "59.8"
  elif era == "UL16":
    yearStr = "UL2016late"
    lumiStr = "16.8"
  elif era == "UL16APV":
    yearStr = "UL2016early"
    lumiStr = "19.5"
  else:
    raise Exception("Unrecognized era: "+era+". Please check!")

  MakeValidation(era, yearStr, lumiStr,doLogY)


def MakeValidation(era, yearStr, lumiStr, doLogY):


  samples = getSamples(era,path_inDir)
  sampleNames = samples.keys()

  mcList = ["DY"]
  mcListFinal = ["DY_PU", "DY_REAL"]

  ####################################################
  #
  #
  #
  ######################################################
  


  ####################################################
  #
  #
  #
  ######################################################
  inTrees = MyDict()
  inTrees["TotalMC"] = ROOT.TChain("Events")
  for sample in samples:
    inTrees[sample] = ROOT.TChain("Events")
    for file in samples[sample]["files"]:
      inTrees[sample].Add(EOSURL+file)
      inTrees["TotalMC"].Add(EOSURL+file)

  

    
  ROOT.gROOT.LoadMacro(
      "/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/modules/Helpers.h")
  df_pre = MyDict()
  df_pre["El"]["Initial"]  = ROOT.RDataFrame(inTrees["TotalMC"])
  df_pre["El"]["Baseline"] = ApplyBaselineSelection(df_pre["El"]["Initial"], era, syst='central',isMu=False)
  df_pre["El"]["Baseline"] = ApplyWeights(df_pre["El"]["Baseline"], "Baseline", isMC=True)
  df_count_El = df_pre["El"]["Baseline"].Sum("evtWeight_Baseline")

  df_pre["Mu"]["Initial"]  = ROOT.RDataFrame(inTrees["TotalMC"])
  df_pre["Mu"]["Baseline"] = ApplyBaselineSelection(df_pre["Mu"]["Initial"], era, syst='central',isMu=True)
  df_pre["Mu"]["Baseline"] = ApplyWeights(df_pre["Mu"]["Baseline"], "Baseline", isMC=True)
  df_count_Mu = df_pre["Mu"]["Baseline"].Sum("evtWeight_Baseline")




  nevents_Mu = df_count_Mu.GetValue()
  print("Mu = %f"  %nevents_Mu)
  nevents_El = df_count_El.GetValue()
  print("El = %f"  %nevents_El)

  scaleEl2Mu = nevents_Mu/nevents_El
  print("scaleEl2Mu = %.3f" % scaleEl2Mu)
  ####################################################
  #
  #
  #
  ######################################################


  df_El = MyDict()
  df_counts_El = MyDict()
  df_Mu = MyDict()
  df_counts_Mu = MyDict()
  etaCutList = [
    "etaCentral",
    "etaForward",
  ]
  puIdWPList = [
    "Loose",
    "Medium",
    "Tight"
  ]

  for sample in mcList:
      df_El[sample]["Initial"] = ROOT.RDataFrame(inTrees[sample])
      df_Mu[sample]["Initial"] = ROOT.RDataFrame(inTrees[sample])
      #
      #
      #
      df_El[sample]["Baseline"] = ApplyBaselineSelection(df_El[sample]["Initial"], era, syst='central', isMu=False)
      df_El[sample]["Baseline"] = ApplyWeights(df_El[sample]["Baseline"], selLevel="Baseline",normFactor=str(scaleEl2Mu))
      df_counts_El[sample]["Baseline"] = df_El[sample]["Baseline"].Sum("evtWeight_Baseline")

      df_Mu[sample]["Baseline"] = ApplyBaselineSelection(df_Mu[sample]["Initial"], era, syst='central', isMu=True)
      df_Mu[sample]["Baseline"] = ApplyWeights(df_Mu[sample]["Baseline"], selLevel="Baseline")
      df_counts_Mu[sample]["Baseline"] = df_Mu[sample]["Baseline"].Sum("evtWeight_Baseline")
      #
      #
      #
  df_El, df_counts_El = ApplySelections(df_El, df_counts_El, sample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList)
  df_Mu, df_counts_Mu = ApplySelections(df_Mu, df_counts_Mu, sample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList)

  if "subsamples" in samples[sample]:
    for subsample in samples[sample]["subsamples"]:
      df_El[subsample]["Baseline"] = df_El[sample]["Baseline"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts_El[subsample]["Baseline"] = df_El[subsample]["Baseline"].Sum("evtWeight_Baseline")
      df_Mu[subsample]["Baseline"] = df_Mu[sample]["Baseline"].Filter(samples[sample]["subsamples"][subsample]["selection"])
      df_counts_Mu[subsample]["Baseline"] = df_Mu[subsample]["Baseline"].Sum("evtWeight_Baseline")

      df_El, df_counts_El = ApplySelections(df_El, df_counts_El, subsample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList)
      df_Mu, df_counts_Mu = ApplySelections(df_Mu, df_counts_Mu, subsample, isMC=True, etaCutList=etaCutList, puIdWPList=puIdWPList)

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

  histograms_El = MyDict()
  histo1D_El = MyDict()

  for sample in mcListFinal:
    for cut in cutNames:
      for hist in histoInfos:
        hModelTemp = copy.copy(histoInfos[hist]["model"])
        hModelTemp.fName = sample+"_"+cut+"_"+histoInfos[hist]["model"].fName

        if "Baseline"         in cut: weightName = "evtWeight_Baseline"
        elif "prePuId"        in cut: weightName = "evtWeight_prePuId"
        elif "passPuIdLoose"  in cut: weightName = "evtWeight_passPuIdLoose"
        elif "passPuIdMedium" in cut: weightName = "evtWeight_passPuIdMedium"
        elif "passPuIdTight"  in cut: weightName = "evtWeight_passPuIdTight"
        if ("Baseline" in cut) or ("prePuId" in cut):
          histo1D_El[sample][cut][hist] = df_El[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
          histo1D_El[sample][cut][hist] = df_El[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
        else:
          histo1D_El[sample][cut][hist] = df_El[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)


  histograms_Mu = MyDict()
  histo1D_Mu = MyDict()
  for sample in mcListFinal:
    for cut in cutNames:
      for hist in histoInfos:
        hModelTemp = copy.copy(histoInfos[hist]["model"])
        hModelTemp.fName = sample+"_"+cut+"_"+histoInfos[hist]["model"].fName
        if "Baseline"         in cut: weightName = "evtWeight_Baseline"
        elif "prePuId"        in cut: weightName = "evtWeight_prePuId"
        elif "passPuIdLoose"  in cut: weightName = "evtWeight_passPuIdLoose"
        elif "passPuIdMedium" in cut: weightName = "evtWeight_passPuIdMedium"
        elif "passPuIdTight"  in cut: weightName = "evtWeight_passPuIdTight"
        if ("Baseline" in cut) or ("prePuId" in cut):
          histo1D_Mu[sample][cut][hist] = df_Mu[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
          histo1D_Mu[sample][cut][hist] = df_Mu[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
        else:
          histo1D_Mu[sample][cut][hist] = df_Mu[sample][cut].Histo1D(hModelTemp,histoInfos[hist]["branch"], weightName)
#
    # Print out Baseline yields
  #
  print("Baseline")
  for sample in mcListFinal:
    nevts_El = df_counts_El[sample]["Baseline"].GetValue()
    nevts_Mu = df_counts_Mu[sample]["Baseline"].GetValue() 

  #
  # Get histograms
  #
  for sample in mcListFinal:
    for cut in cutNames:
      for hist in histoInfos:
        histograms_El[sample][cut][hist] = histo1D_El[sample][cut][hist].GetValue()
        histograms_Mu[sample][cut][hist] = histo1D_Mu[sample][cut][hist].GetValue()

  ####################################################
  #
  #
  #
  ######################################################
  outDir="/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LogY_DiLeptonReskim/"
  outDir2="/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/LinearY_DiLeptonReskim/"




  #
  #
  #
  for cutName in cutNames:
    for hInfo in histoInfos:
      if not doLogY:
        outDir = outDir2
      MakePlot(doLogY,histograms_El,histograms_Mu,histoInfos, cutName, hInfo, "Data", mcListFinal, yearStr, lumiStr, outDir, extratext=cutName.replace('_',' ').replace('eta','\eta '))

if __name__ == '__main__':
  main()
    