import sys
import os
import glob
import argparse
from collections import OrderedDict 
import datetime

import ROOT
import VariableList
import SampleList
import SampleListUL

ROOT.gROOT.SetBatch()
ROOT.gROOT.LoadMacro("./Helpers.h")

#
#
#
varNamesToPlot = [
  "probeJet_dilep_dphi_norm"
]

def main(sample_name, useSkimNtuples, systStr, useNewTraining=False):
  
  isUL=False
  
  crabFiles   = []
  ntupleFiles = []

  if "DataUL" in sample_name or "MCUL" in sample_name:
    EOSURL      = SampleListUL.EOSURL
    crabFiles   = SampleListUL.Samples[sample_name].crabFiles
    ntupleFiles = SampleListUL.Samples[sample_name].ntupleFiles
    isUL=True
  else:
    EOSURL      = SampleList.EOSURL
    crabFiles   = SampleList.Samples[sample_name].crabFiles
    ntupleFiles = SampleList.Samples[sample_name].ntupleFiles


  FileList = []

  if useSkimNtuples:
    print "Globbing File Paths:"
    for files in ntupleFiles:
      print files
      FileList += [EOSURL+f for f in glob.glob(files)]
  else:
    print "Globbing File Paths:"
    for files in crabFiles:
      print files
      FileList += [EOSURL+f for f in glob.glob(files)]
  
  # Creating std::vector as filelist holder to be plugged into RDataFrame
  vec = ROOT.vector('string')()

  for f in FileList:
    vec.push_back(f)

  # Read all files into RDataFrame
  df = ROOT.ROOT.RDataFrame("Events", vec)
  isMC = False
  if "MC" in sample_name:
    isMC = True

  systStrPre  = ""
  systStrPost = ""
  if systStr != "": 
    systStrPre  = systStr+"_"
    systStrPost = "_"+systStr
  #############################################
  #
  # Define columns in RDataframe
  #
  #############################################
  # Define evtWeight variable
  if "Data" in sample_name:
    df = df.Define("evtWeight","1.0")
  else: #For MC
    df = df.Define("evtWeight","genWeight")

  # Define name for event weight
  weightName = "evtWeight"

  if not useSkimNtuples:
    df = df.Define("passOS","lep0_charge * lep1_charge < 0.0")
    if systStr != "":
      df = df.Define("passNJetSel","(nJetSel>=1)&&(nJetSelPt30Eta5p0<=1)&&(nJetSelPt20Eta2p4<=1)")
    else:
      df = df.Define(systStr+"passNJetSel","("+systStrPre+"nJetSel>=1)&&("+systStrPre+"nJetSelPt30Eta5p0<=1)&&("+systStrPre+"nJetSelPt20Eta2p4<=1)")

  #
  # Define flags for lepton channels if need to check by channel
  #
  df = df.Define("isElEl","(abs(lep0_pdgId)==11)&&(abs(lep1_pdgId)==11)")
  df = df.Define("isMuMu","(abs(lep0_pdgId)==13)&&(abs(lep1_pdgId)==13)")
  #
  # Define the probeJet
  #
  probeJetStr=systStrPre+"jetSel0"
  df = df.Define("probeJet_pt",             probeJetStr+"_pt")
  df = df.Define("probeJet_eta",            probeJetStr+"_eta")
  df = df.Define("probeJet_abseta",         "fabs("+probeJetStr+"_eta)")
  df = df.Define("probeJet_phi",            probeJetStr+"_phi")
  df = df.Define("probeJet_dilep_dphi",     probeJetStr+"_dilep_dphi")
  df = df.Define("probeJet_puIdDisc",       probeJetStr+"_puIdDisc")
  #
  # Guide on how to read the pileup ID bitmap variable: 
  # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID#miniAOD_and_nanoAOD
  #
  df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 2)")
  df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
  df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 0)")
  if isUL:
    df = df.Define("probeJet_puIdDiscOTF",  probeJetStr+"_puIdDiscOTF")
  if isMC:
    df = df.Define("probeJet_passGenMatch",probeJetStr+"_gen_match")

  #
  #
  #
  df = df.Define("probeJet_dilep_dphi_norm","DeltaPhiNorm(probeJet_dilep_dphi)")
  df = df.Define("probeJet_dilep_ptbalance","dilep_pt/probeJet_pt")
  #
  # Define pileup ID cuts
  # 
  if not isUL: #EOY
    #
    # NOTE: The pileup ID decision flag stored in NanoAOD (v7 and earlier) is based on 
    # the 80X BDT training and working point (as in the parent MiniAOD).
    #
    if not useNewTraining:
      df = df.Define("probeJet_puIdLoose_pass",  "probeJet_puIdFlag_Loose")
      df = df.Define("probeJet_puIdMedium_pass", "probeJet_puIdFlag_Medium")
      df = df.Define("probeJet_puIdTight_pass",  "probeJet_puIdFlag_Tight")
    #
    # Starting from NanoAODv7, the pileup ID BDT discriminant value is stored for each jet.
    # The discriminant is calculated based on the appropriate training for each Run-2 year.
    # i.e 80X for 2016, 94X for 2017 and 102X for 2018
    #
    else:
      argStr = "probeJet_pt,probeJet_eta,probeJet_puIdDisc"
      df = df.Define("probeJet_puIdLoose_pass",  "PUJetID_80XCut_WPLoose("+argStr+")")
      df = df.Define("probeJet_puIdMedium_pass", "PUJetID_80XCut_WPMedium("+argStr+")")
      df = df.Define("probeJet_puIdTight_pass",  "PUJetID_80XCut_WPTight("+argStr+")")
  else: #UL
    #
    # NOTE: In ULNanoAODv2 UL17, the pileup jet ID flag is based on the UL17 training
    # and cut values.
    #
    if not useNewTraining:
      df = df.Define("probeJet_puIdLoose_pass",  "probeJet_puIdFlag_Loose")
      df = df.Define("probeJet_puIdMedium_pass", "probeJet_puIdFlag_Medium")
      df = df.Define("probeJet_puIdTight_pass",  "probeJet_puIdFlag_Tight")
  #
  #
  #
  df = df.Define("probeJet_ptbalance_good","(probeJet_dilep_ptbalance>=0.5) && (probeJet_dilep_ptbalance<1.5)")
  df = df.Define("probeJet_ptbalance_bad","probeJet_dilep_ptbalance<0.5")
  #############################################
  #
  # Define Filters
  #
  #############################################
  df_filters  = OrderedDict()
  df_filters["passNJetSel"] = df.Filter("passOS").Filter(systStrPre+"passNJetSel")
  #
  # Choose column used for PU Id cuts
  #
  puIDCuts = OrderedDict()
  puIDCuts["passPUIDLoose"]  = "probeJet_puIdLoose_pass"
  puIDCuts["passPUIDMedium"] = "probeJet_puIdMedium_pass"
  puIDCuts["passPUIDTight"]  = "probeJet_puIdTight_pass"
  puIDCuts["failPUIDLoose"]  = "!probeJet_puIdLoose_pass"
  puIDCuts["failPUIDMedium"] = "!probeJet_puIdMedium_pass"
  puIDCuts["failPUIDTight"]  = "!probeJet_puIdTight_pass"
  #
  # Define pt balance cuts
  #
  ptBalanceCuts = OrderedDict()
  ptBalanceCuts["goodBal"] = "probeJet_ptbalance_good"
  ptBalanceCuts["badBal"]  = "probeJet_ptbalance_bad"

  selNames = []
  for ptBalCut in ptBalanceCuts:
    for puIDCut in puIDCuts:
      selName = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut
      filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut]
      df_filters[selName] = df_filters["passNJetSel"].Filter(filterStr)
      selNames.append(selName)
      #
      # Gen Matching requirement
      #
      if isMC:
        #
        # Pass
        #
        selName = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut + "_passGenMatch"
        filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (probeJet_passGenMatch)"
        df_filters[selName] = df_filters["passNJetSel"].Filter(filterStr)
        selNames.append(selName)
        #
        # Fail
        #
        selName = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut + "_failGenMatch"
        filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (!probeJet_passGenMatch)"
        df_filters[selName] = df_filters["passNJetSel"].Filter(filterStr)
        selNames.append(selName)

  #
  # Define probeJet eta bins
  #
  # etaBins = OrderedDict()
  # # Abs(eta)
  # # etaBins["abseta0p0To1p479"] = "(probeJet_abseta > 0.0)   && (probeJet_abseta <= 1.479)"
  # # etaBins["abseta1p479To2p0"] = "(probeJet_abseta > 1.479) && (probeJet_abseta <= 2.0)"
  # # etaBins["abseta2p0To2p5"]   = "(probeJet_abseta > 2.0)   && (probeJet_abseta <= 2.5)"
  # # etaBins["abseta2p5To2p75"]  = "(probeJet_abseta > 2.5)   && (probeJet_abseta <= 2.75)"
  # # etaBins["abseta2p75To3p0"]  = "(probeJet_abseta > 2.75)  && (probeJet_abseta <= 3.00)"
  # # etaBins["abseta3p0To5p0"]   = "(probeJet_abseta > 3.0)   && (probeJet_abseta <= 5.0)"
  # # negative eta
  # etaBins["etaneg5p0Toneg3p0"]   = "(probeJet_eta < -3.0)   && (probeJet_eta >= -5.0)"
  # etaBins["etaneg3p0Toneg2p75"]  = "(probeJet_eta < -2.75)  && (probeJet_eta >= -3.00)"
  # etaBins["etaneg2p75Toneg2p5"]  = "(probeJet_eta < -2.5)   && (probeJet_eta >= -2.75)"
  # etaBins["etaneg2p5Toneg2p0"]   = "(probeJet_eta < -2.0)   && (probeJet_eta >= -2.5)"
  # etaBins["etaneg2p0Toneg1p479"] = "(probeJet_eta < -1.479) && (probeJet_eta >= -2.0)"
  # etaBins["etaneg1p479To0p0"]    = "(probeJet_eta < 0.0)    && (probeJet_eta >= -1.479)"
  # # positive eta
  # etaBins["eta0p0Topos1p479"]    = "(probeJet_eta > 0.0)    && (probeJet_eta <= 1.479)"
  # etaBins["etapos1p479Topos2p0"] = "(probeJet_eta > 1.479)  && (probeJet_eta <= 2.0)"
  # etaBins["etapos2p0Topos2p5"]   = "(probeJet_eta > 2.0)    && (probeJet_eta <= 2.5)"
  # etaBins["etapos2p5Topos2p75"]  = "(probeJet_eta > 2.5)    && (probeJet_eta <= 2.75)"
  # etaBins["etapos2p75Topos3p0"]  = "(probeJet_eta > 2.75)   && (probeJet_eta <= 3.00)"
  # etaBins["etapos3p0Topos5p0"]   = "(probeJet_eta > 3.0)    && (probeJet_eta <= 5.0)"
  # #
  # # Define probeJet pt bins
  # #
  # ptBins = OrderedDict()
  # ptBins["pt20To25"]  = "(probeJet_pt > 20.) && (probeJet_pt <= 25.)"
  # ptBins["pt25To30"]  = "(probeJet_pt > 25.) && (probeJet_pt <= 30.)"
  # ptBins["pt30To40"]  = "(probeJet_pt > 30.) && (probeJet_pt <= 40.)"
  # ptBins["pt40To50"]  = "(probeJet_pt > 40.) && (probeJet_pt <= 50.)"

  etaBins = OrderedDict()
  # negative eta
  etaBins["etaneg5p0Toneg3p0"]   = "(probeJet_eta >= -5.000)  &&  (probeJet_eta < -3.000)"
  etaBins["etaneg3p0Toneg2p75"]  = "(probeJet_eta >= -3.000)  &&  (probeJet_eta < -2.750)"
  etaBins["etaneg2p75Toneg2p5"]  = "(probeJet_eta >= -2.750)  &&  (probeJet_eta < -2.500)"
  etaBins["etaneg2p5Toneg2p0"]   = "(probeJet_eta >= -2.500)  &&  (probeJet_eta < -2.000)"
  etaBins["etaneg2p0Toneg1p479"] = "(probeJet_eta >= -2.000)  &&  (probeJet_eta < -1.479)"
  etaBins["etaneg1p479To0p0"]    = "(probeJet_eta >= -1.479)  &&  (probeJet_eta <  0.000)"
  # positive eta
  etaBins["eta0p0Topos1p479"]    = "(probeJet_eta >= 0.000)  && (probeJet_eta < 1.479)"
  etaBins["etapos1p479Topos2p0"] = "(probeJet_eta >= 1.479)  && (probeJet_eta < 2.000)"
  etaBins["etapos2p0Topos2p5"]   = "(probeJet_eta >= 2.000)  && (probeJet_eta < 2.500)"
  etaBins["etapos2p5Topos2p75"]  = "(probeJet_eta >= 2.500)  && (probeJet_eta < 2.750)"
  etaBins["etapos2p75Topos3p0"]  = "(probeJet_eta >= 2.750)  && (probeJet_eta < 3.000)"
  etaBins["etapos3p0Topos5p0"]   = "(probeJet_eta >= 3.000)  && (probeJet_eta < 5.000)"
  # Define probeJet pt bins
  ptBins = OrderedDict()
  ptBins["pt20To25"]  = "(probeJet_pt >= 20.) && (probeJet_pt < 25.)"
  ptBins["pt25To30"]  = "(probeJet_pt >= 25.) && (probeJet_pt < 30.)"
  ptBins["pt30To40"]  = "(probeJet_pt >= 30.) && (probeJet_pt < 40.)"
  ptBins["pt40To50"]  = "(probeJet_pt >= 40.) && (probeJet_pt < 50.)"


  #
  # apply probeJet eta and pt cuts at the same time
  #
  cutNames = []
  for selName in selNames:
    for eta in etaBins:
      for pt in ptBins:
        cutNameStr = selName + "_"+ eta + "_" + pt
        filterStr  = etaBins[eta] + " && " + ptBins[pt]
        df_filters[cutNameStr] =  df_filters[selName].Filter(filterStr)
        cutNames.append(cutNameStr)

  ##############################################
  #
  # Define the cut levels that we want to make 
  # histograms
  #
  #############################################
  cutLevels = []
  cutLevels += cutNames

  ##############################################
  #
  # Make the histograms
  #
  #############################################
  Histograms = OrderedDict()
  #
  # Loop over cutLevels
  #
  for cutLevel in cutLevels:
    #
    # Loop over variables to plot
    #
    for varName in varNamesToPlot:
      var = VariableList.Variables[varName]
      #
      # Some exceptions 
      #
      if "probeJet" in varName and "passNJetSel" not in cutLevel: continue
      #
      # Define full name for histogram
      #
      histoNameFinal  = "h_%s_%s%s" %(cutLevel,varName,systStrPost)
      histoInfo = (histoNameFinal, histoNameFinal+";"+var.xAxis+";"+var.yAxis, var.nbins, var.xmin, var.xmax)
      Histograms[histoNameFinal] = df_filters[cutLevel].Histo1D(histoInfo, var.varNameInTree, weightName)

  print("Number of 1D histos: %s " %len(Histograms))
  numOfEvents = df.Count()
  print("Number of events in sample: %s " %numOfEvents.GetValue())
  ##############################################
  #
  # Save histograms in output rootfile
  #
  #############################################
  #
  # Create directory for output
  # 
  outDir = './histos/'
  if not(os.path.isdir(outDir)):
    os.mkdir(outDir)

  # Open a new ROOT file to store TH1
  outFileName = "%sHisto_%s%s.root"%(outDir,sample_name,systStrPost)
  f = ROOT.TFile(outFileName, 'RECREATE')

  # Loop over the Histograms dictionary and store TH1 in ROOT file
  for histName in Histograms:
    Histograms[histName].Write()

  f.Close()
  print("Histos saved in %s" %outFileName)

if __name__== "__main__":
  time_start = datetime.datetime.now()
  print("MakeHistograms.py::START::Time("+str(time_start)+")")

  parser = argparse.ArgumentParser("")
  parser.add_argument('--sample',         dest='sample',         type=str,  default="")
  parser.add_argument('--cores',          dest='cores',          type=int,  default=4)
  parser.add_argument('--useSkimNtuples', dest='useSkimNtuples', action='store_true')
  parser.add_argument('--useNewTraining', dest='useNewTraining', action='store_true')

  args = parser.parse_args()
  print "sample = %s" %(args.sample)
  print "ncores = %d" %(args.cores)
  print "useSkimNtuples = %r" %(args.useSkimNtuples)
  print "useNewTraining = %r" %(args.useNewTraining)

  isMC = False
  if "MC" in args.sample:
    isMC = True
  
  #
  # List all jet energy scale and resolution systematics
  #
  ak4Systematics=[]
  if isMC:
    ak4Systematics=[
      "jesTotalUp",
      "jesTotalDown",
      "jerUp",
      "jerDown"
    ]
  # Don't do ak4Systematics for MG+HW and AMCNLO
  if "MG_HW" in args.sample: ak4Systematics=[]
  if "AMCNLO" in args.sample: ak4Systematics=[]
  
  ROOT.ROOT.EnableImplicitMT(args.cores)
  #
  # Do Nominal
  #
  main(args.sample,args.useSkimNtuples,"",args.useNewTraining)
  #
  # Do Systematics
  #
  for systStr in ak4Systematics:
    main(args.sample,args.useSkimNtuples,systStr,args.useNewTraining)

  time_end = datetime.datetime.now()
  elapsed = time_end - time_start
  elapsed_str = str(datetime.timedelta(seconds=elapsed.seconds))
  print("MakeHistograms.py::DONE::Sample("+args.sample+")::Time("+str(time_end)+")::Elapsed("+elapsed_str+")")
