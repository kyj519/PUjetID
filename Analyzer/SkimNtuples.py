import sys
import os
import glob
import argparse
from collections import OrderedDict 

import ROOT
import VariableList
import SampleList
import SampleListUL

import datetime

ROOT.gROOT.SetBatch()
ROOT.gROOT.LoadMacro("./Helpers.h")

def main(sample_name):

  crabFiles = []
  if "DataUL" in sample_name or "MCUL" in sample_name:
    crabFiles = SampleListUL.Samples[sample_name].crabFiles
    EOSURL=SampleListUL.EOSURL
    EOSDIR=SampleListUL.EOSDIR
    NTUPDIR=SampleListUL.NTUPDIR
    xs = SampleListUL.Samples[sample_name].xs
    if "MCUL17" in sample_name:
      lumi = SampleListUL.lumi_UL2017
    elif "MCUL18" in sample_name:
      lumi = SampleListUL.lumi_UL2018
    elif "MCUL16APV" in sample_name 
      lumi = SampleListUL.lumi_UL2016APV
    elif "MCUL16" in sample_name:
      lumi = SampleListUL.lumi_UL2016
  else:
    crabFiles = SampleList.Samples[sample_name].crabFiles
    EOSURL=SampleList.EOSURL
    EOSDIR=SampleList.EOSDIR
    NTUPDIR=SampleList.NTUPDIR
    xs = SampleList.Samples[sample_name].xs

  print("Globbing File Paths:")
  FileList = []
  for files in crabFiles:
    print files
    FileList += [EOSURL+f for f in glob.glob(files)]
  
  # Creating std::vector as filelist holder to be plugged into RDataFrame
  vec = ROOT.vector('string')()
  
  print("List of files for the RDataFrame:")
  for f in FileList:
    print(f)
    vec.push_back(f)

  isMC = False
  ak4Systematics = []
  if "MC" in sample_name:
    isMC = True
    ak4Systematics=[
      "jesTotalUp",
      "jesTotalDown",
      # "jerUp",
      # "jerDown"
    ]
  #
  # Don't do ak4Systematics for MG+HW and AMCNLO
  #
  if "DY_MG_HW" in sample_name: ak4Systematics=[]
  if "DY_AMCNLO" in sample_name: ak4Systematics=[]

  #
  # Get sample sum of event weights from
  # Runs TTree. Using a simple pyroot
  # event looping. Should be quick
  #
  genEventCount = 0
  genEventSumw  = 0.
  treeRuns = None
  if isMC:
    treeRuns =  ROOT.TChain("Runs")
    for file in FileList: treeRuns.Add(file)
    nEventsRuns = treeRuns.GetEntries()
    for i in range(0, nEventsRuns):
      event = treeRuns.GetEntry(i)
      genEventCount += treeRuns.genEventCount
      genEventSumw  += treeRuns.genEventSumw
    print ("genEventCount: "+str(genEventCount))
    print ("genEventSumw: "+str(genEventSumw))

  #
  # Read all files into RDataFrame
  #
  df = ROOT.ROOT.RDataFrame("Events", vec)

  #############################################
  #
  # Define columns
  #
  #############################################
  if isMC:
    eventWeightScaleStr="float((%.5f * %.5f)/%.5f)"%(xs,lumi,genEventSumw)
    df = df.Define("eventWeightScale",eventWeightScaleStr)
    df = df.Define("mcXS","%.5f"%(xs))
    df = df.Define("mcSumOfWeight", "float("+str(genEventSumw)+")")
  else:
    df = df.Define("eventWeightScale","1.0")

  df = df.Define("passOS","lep0_charge * lep1_charge < 0.0")
  df = df.Define("passNJetSel","(nJetSel>=1)&&(nJetSelPt30Eta5p0<=1)&&(nJetSelPt20Eta2p4<=1)")
  if isMC:
    for syst in ak4Systematics:
      df = df.Define(syst+"_passNJetSel","("+syst+"_nJetSel>=1)&&("+syst+"_nJetSelPt30Eta5p0<=1)&&("+syst+"_nJetSelPt20Eta2p4<=1)")

  #############################################
  #
  # Define Filters
  #
  #############################################
  df_filters = OrderedDict()
  df_filters["passOS"] = df.Filter("passOS")

  filtStringNJetSel = "passNJetSel"
  for syst in ak4Systematics:
    filtStringNJetSel += "||"+syst+"_passNJetSel"
  df_filters["passNJetSelAll"] = df_filters["passOS"].Filter(filtStringNJetSel)

  #############################################
  #
  # Snapshot tree
  #
  #############################################
  #
  # Save at EOS
  #
  prefix=EOSURL
  prefix+=EOSDIR
  prefix+=NTUPDIR
  #
  #
  #
  initialCount = df.Count()
  finalCount = df_filters["passNJetSelAll"].Count()
  #
  # Save events with exactly one jet
  #
  outTreeName="Events"
  outTreeFileName = "%sntuple_%s.root" %(prefix,sample_name)
  print("Save tree %s in file %s"%(outTreeName,outTreeFileName))
  df_filters["passNJetSelAll"].Snapshot(outTreeName, outTreeFileName) 
  print("Initial NEvents in Tree:    "+str(initialCount.GetValue()))
  print("Final NEvents in Skim Tree: "+str(finalCount.GetValue()))

if __name__== "__main__":
  time_start = datetime.datetime.now()
  print("SkimNtuple.py::START::Time("+str(time_start)+")")

  parser = argparse.ArgumentParser("")
  parser.add_argument('-s', '--sample', type=str,  default="")
  parser.add_argument('-c', '--cores',  type=int,  default=4)

  args = parser.parse_args()
  print("sample = %s"%(args.sample))
  print("ncores = %d"%(args.cores))
 
  ROOT.ROOT.EnableImplicitMT(args.cores)
  main(args.sample)
 
  time_end = datetime.datetime.now()
  elapsed = time_end - time_start
  elapsed_str = str(datetime.timedelta(seconds=elapsed.seconds))
  print("SkimNtuple.py::DONE::Sample("+args.sample+")::Time("+str(time_end)+")::Elapsed("+elapsed_str+")")
