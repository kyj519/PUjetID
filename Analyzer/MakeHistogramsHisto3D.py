import sys
import os
import glob
import argparse
from collections import OrderedDict 
import datetime

import array
import ROOT
import SampleList
import SampleListUL

ROOT.gROOT.SetBatch()
ROOT.gROOT.LoadMacro("./Helpers.h")

#
#
#
ptBins  = [20.,25.,30.,40.,50.]
ptBinsArray = array.array('d',ptBins)
ptBinsN = len(ptBins)-1
ptBinsStr = []
ptBinsStr.append("pt20To25")
ptBinsStr.append("pt25To30")
ptBinsStr.append("pt30To40")
ptBinsStr.append("pt40To50")

#
#
#
etaBins = [
  -5.000,
  -3.000,
  -2.750,
  -2.500,
  -2.000,
  -1.479,
  0.000,
  +1.479,
  +2.000,
  +2.500,
  +2.750,
  +3.000,
  +5.000
]
etaBinsArray = array.array('d',etaBins)
etaBinsN = len(etaBins)-1
etaBinsStr = []  
etaBinsStr.append("etaneg5p0Toneg3p0")
etaBinsStr.append("etaneg3p0Toneg2p75")
etaBinsStr.append("etaneg2p75Toneg2p5")
etaBinsStr.append("etaneg2p5Toneg2p0")
etaBinsStr.append("etaneg2p0Toneg1p479")
etaBinsStr.append("etaneg1p479To0p0")
etaBinsStr.append("eta0p0Topos1p479")
etaBinsStr.append("etapos1p479Topos2p0")
etaBinsStr.append("etapos2p0Topos2p5")
etaBinsStr.append("etapos2p5Topos2p75")
etaBinsStr.append("etapos2p75Topos3p0")
etaBinsStr.append("etapos3p0Topos5p0")

#
#
#
absEtaBins = [
  0.,1.479,2.0,2.5,2.75,3.0,5.0
]
absEtaBinsArray = array.array('d',absEtaBins)
absEtaBinsN = len(absEtaBins)-1
absEtaBinsStr = []  
absEtaBinsStr.append("abseta0p0To1p479")
absEtaBinsStr.append("abseta1p479To2p0")
absEtaBinsStr.append("abseta2p0To2p5")
absEtaBinsStr.append("abseta2p5To2p75")
absEtaBinsStr.append("abseta2p75To3p0")
absEtaBinsStr.append("abseta3p0To5p0")

#
#
#
dphiBinsN = 100
dphiBinSize = 0.02
dphiBins =[round(x*dphiBinSize, 2) for x in xrange(0,dphiBinsN+1)]
dphiBinsArray = array.array('d',dphiBins)
dphiBinsN = len(dphiBins)-1


#
#
#
deltaRBinsN = 200
deltaRBinSize = 0.02
deltaRBins =[round(x*deltaRBinSize, 2) for x in xrange(0,deltaRBinsN+1)]
deltaRBinsArray = array.array('d',deltaRBins)
deltaRBinsN = len(deltaRBins)-1

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
    print("Globbing File Paths:")
    for files in ntupleFiles:
      print(files)
      FileList += [EOSURL+f for f in glob.glob(files)]
  else:
    print "Globbing File Paths:"
    for files in crabFiles:
      print(files)
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
  # Note: For ULNanoAODv9 UL2016 APV and nonAPV, there is a bug where Tight and Loose WP cuts were
  # switched (https://github.com/cms-sw/cmssw/blob/CMSSW_10_6_26/RecoJets/JetProducers/python/PileupJetIDCutParams_cfi.py#L82-L101)
  # so the bit ordering has to be reversed
  #
  if "DataUL16" in sample_name or "MCUL16" in sample_name:
    df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 0)")
    df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
    df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 2)")
  else:
    df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 2)")
    df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
    df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 0)")
  # if isUL: # For JMENano
  #   df = df.Define("probeJet_puIdDiscOTF",  probeJetStr+"_puIdDiscOTF")
  if isMC:
    df = df.Define("probeJet_passGenMatch", probeJetStr+"_gen_match")
    df = df.Define("probeJet_closestgen_dR", probeJetStr+"_closestgen_dR")
    df = df.Define("probeJet_gen_dR", probeJetStr+"_gen_dR")
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
    # For ULNanoAODv9, each era year has its own BDT training included in its own production.
    # Just use the decision as stored in the bitmap variable
    #
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
  df_filters["passNJetSel"] = df.Filter("passOS").Filter(systStrPre+"passNJetSel").Filter("isMuMu") #Only muon channel at the moment

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
      cutNameStr = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut
      filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut]
      df_filters[cutNameStr] = df_filters["passNJetSel"].Filter(filterStr)
      selNames.append(cutNameStr)
      #
      # Gen Matching requirement
      #
      if isMC:
        #
        # Pass
        #
        cutNameStr = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut + "_passGenMatch"
        filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (probeJet_passGenMatch)"
        df_filters[cutNameStr] = df_filters["passNJetSel"].Filter(filterStr)
        selNames.append(cutNameStr)
        #
        # Fail
        #
        cutNameStr = "passNJetSel_probeJet_" + ptBalCut + "_" + puIDCut + "_failGenMatch"
        filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (!probeJet_passGenMatch)"
        df_filters[cutNameStr] = df_filters["passNJetSel"].Filter(filterStr)
        selNames.append(cutNameStr)

  ##############################################
  #
  # Define the cut levels that we want to make 
  # histograms
  #
  #############################################
  cutLevels = []
  cutLevels += selNames

  ##############################################
  #
  # Make the 3D histograms
  #
  ###############################################
  Histograms3D = OrderedDict()
  #
  # etaBins
  #
  for cutLevel in cutLevels:
    histoNameFinal  = "h3_%s_probeJet_pt_eta_dilep_dphi_norm%s" %(cutLevel,systStrPost)
    histoInfo = ROOT.RDF.TH3DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, etaBinsN, etaBinsArray, dphiBinsN, dphiBinsArray)
    Histograms3D[histoNameFinal] = df_filters[cutLevel].Histo3D(histoInfo, "probeJet_pt","probeJet_eta","probeJet_dilep_dphi_norm", weightName)
  #
  # absEtaBins
  #
  # for cutLevel in cutLevels:
  #   histoNameFinal  = "h3_%s_probeJet_pt_abseta_dilep_dphi_norm%s" %(cutLevel,systStrPost)
  #   histoInfo = ROOT.RDF.TH3DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, absEtaBinsN, absEtaBinsArray, dphiBinsN, dphiBinsArray)
  #   Histograms3D[histoNameFinal] = df_filters[cutLevel].Histo3D(histoInfo, "probeJet_pt","probeJet_abseta","probeJet_dilep_dphi_norm", weightName)

  print("Number of 3D histos: %s " %len(Histograms3D))
  #####################################################
  #
  # For Gen-based Efficiency, Mistag and Purity studies
  #
  #####################################################
  selGenNames = []
  if isMC:
    for puIDCut in puIDCuts:
      #
      # PassGenMatch
      #
      cutNameStr = "passNJetSel_probeJet_" + puIDCut + "_passGenMatch"
      filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (probeJet_passGenMatch)"
      df_filters[cutNameStr] = df_filters["passNJetSel"].Filter(filterStr)
      selGenNames.append(cutNameStr)
      #
      # FailGenMatch
      #
      cutNameStr = "passNJetSel_probeJet_" + puIDCut + "_failGenMatch"
      filterStr  = ptBalanceCuts[ptBalCut] + " && " + puIDCuts[puIDCut] + " && (!probeJet_passGenMatch)"
      df_filters[cutNameStr] = df_filters["passNJetSel"].Filter(filterStr)
      selGenNames.append(cutNameStr)

  cutLevels = []
  cutLevels += selGenNames
  #
  # Make the 2D histograms. Counts in pt and eta bins
  #
  Histograms2D = OrderedDict()
  for cutLevel in cutLevels:
    histoNameFinal  = "h2_%s_probeJet_pt_eta_count%s" %(cutLevel,systStrPost)
    histoInfo = ROOT.RDF.TH2DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, etaBinsN, etaBinsArray)
    Histograms2D[histoNameFinal] = df_filters[cutLevel].Histo2D(histoInfo, "probeJet_pt","probeJet_eta", weightName)

  print("Number of 2D histos: %s " %len(Histograms2D))
  #####################################################
  #
  # DeltaR between 
  #
  #####################################################
  if isMC:
    histoNameFinal  = "h3_%s_probeJet_pt_eta_closestgen_dR%s" %("passNJetSel",systStrPost)
    histoInfo = ROOT.RDF.TH3DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, etaBinsN, etaBinsArray, deltaRBinsN, deltaRBinsArray)
    Histograms3D[histoNameFinal] = df_filters["passNJetSel"].Histo3D(histoInfo, "probeJet_pt","probeJet_eta","probeJet_closestgen_dR", weightName)
    #
    histoNameFinal  = "h3_%s_probeJet_pt_eta_gen_dR%s" %("passNJetSel",systStrPost)
    histoInfo = ROOT.RDF.TH3DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, etaBinsN, etaBinsArray, deltaRBinsN, deltaRBinsArray)
    Histograms3D[histoNameFinal] = df_filters["passNJetSel"].Histo3D(histoInfo, "probeJet_pt","probeJet_eta","probeJet_gen_dR", weightName)
    #
    histoNameFinal  = "h2_%s_probeJet_pt_closestgen_dR%s" %("passNJetSel",systStrPost)
    histoInfo = ROOT.RDF.TH2DModel(histoNameFinal, histoNameFinal, ptBinsN, ptBinsArray, deltaRBinsN, deltaRBinsArray)
    Histograms2D[histoNameFinal] = df_filters["passNJetSel"].Histo2D(histoInfo, "probeJet_pt","probeJet_closestgen_dR", weightName)

  ##############################################
  #
  # This will trigger the lazy actions
  #
  ###############################################
  numOfEvents = df.Count()
  print("Number of events in sample: %s " %numOfEvents.GetValue())

  ##############################################
  #
  # Project the 3D histograms
  #
  ##############################################
  def ProjectTH3(h3, HistoDict, varName, systStrPost):
    h3Name  = h3.GetName()
    selName = h3Name.replace("h3_","")

    if "_eta_" in selName:
      selName  = selName.replace("_probeJet_pt_eta_%s"%(varName),"")
      nBinsY   = etaBinsN
      yBinsStr = etaBinsStr
    elif "_abseta_" in selName:
      selName  = selName.replace("_probeJet_pt_abseta_%s"%(varName),"")
      nBinsY   = absEtaBinsN
      yBinsStr = absEtaBinsStr

    nBinsX = ptBinsN
    xBinsStr = ptBinsStr

    if systStrPost != "":
      selName = selName.replace(systStrPost,"")

    for iBinX in xrange(1,nBinsX+1):
      for iBinY in xrange(1,nBinsY+1):
        binStr   = "%s_%s" %(yBinsStr[iBinY-1], xBinsStr[iBinX-1]) #eta first, then pt
        histName = "h_%s_%s_probeJet_%s%s" %(selName, binStr, varName, systStrPost)
        HistoDict[histName] = h3.ProjectionZ(histName, iBinX, iBinX, iBinY, iBinY)
    return HistoDict
  
  Histograms = OrderedDict()

  #
  # Loop over TH3s
  #
  for hist3DName in Histograms3D:
    h3 = Histograms3D[hist3DName].GetValue()
    h3Name = h3.GetName()
    if "dilep_dphi_norm" in h3Name:
      Histograms = ProjectTH3(h3, Histograms, "dilep_dphi_norm", systStrPost)
    elif "_closestgen_dR" in h3Name:
      Histograms = ProjectTH3(h3, Histograms, "closestgen_dR", systStrPost)
    elif "_gen_dR" in h3Name:
      Histograms = ProjectTH3(h3, Histograms, "gen_dR", systStrPost)

  print("Number of 1D histos: %s " %len(Histograms))
  ##############################################
  #
  # Save histograms in output rootfile
  #
  #############################################
  #
  # Create directory for output
  # 
  outDir = './histos3D/'
  if not(os.path.isdir(outDir)):
    os.mkdir(outDir)

  # Open a new ROOT file to store TH1
  outFileName = "%sHisto_%s%s.root"%(outDir,sample_name,systStrPost)
  f = ROOT.TFile(outFileName, 'RECREATE')

  # Loop over the Histograms3D dictionary and store TH3 in ROOT file
  for hist3DName in Histograms3D:
    Histograms3D[hist3DName].Write()

  # Loop over the Histograms2D dictionary and store TH2 in ROOT file
  for hist2DName in Histograms2D:
    Histograms2D[hist2DName].Write()

  # Loop over the Histograms1D dictionary and store TH1 in ROOT file
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
  print("sample = %s" %(args.sample))
  print("ncores = %d" %(args.cores))
  print("useSkimNtuples = %r" %(args.useSkimNtuples))
  print("useNewTraining = %r" %(args.useNewTraining))

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
      # "jerUp",
      # "jerDown"
    ]
  # Don't do ak4Systematics for MG+HW, AMCNLO and PHG
  if "MG_HW" in args.sample: ak4Systematics=[]
  if "AMCNLO" in args.sample: ak4Systematics=[]
  if "PHG" in args.sample: ak4Systematics=[]
  
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
  print("MakeHistogramsHisto3D.py::DONE::Sample("+args.sample+")::Time("+str(time_end)+")::Elapsed("+elapsed_str+")")
