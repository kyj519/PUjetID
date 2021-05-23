#!/usr/bin/env python
import os,sys
import ROOT
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *

print "RunSkimmerLocal.py START"

parser = argparse.ArgumentParser("")
parser.add_argument('--era',              type=str, default="")
parser.add_argument('--maxEvents',        type=int, default=-1)
parser.add_argument('--outDir',           type=str, default=".")
parser.add_argument('--isMC',             type=int ,default=0)
parser.add_argument('--dataStream',       type=str ,default="")

args        = parser.parse_args()
era         = args.era
maxEvents   = args.maxEvents
outDir      = args.outDir
isMC        = args.isMC
dataStream  = args.dataStream

print "args = ", args
print "era  = ", era
print "isMC = ", isMC 
print "dataStream = ", dataStream

isDoubleElecData=False
isDoubleMuonData=False

if "DoubleEG" in dataStream:
  isDoubleElecData = True
if "EGamma" in dataStream:
  isDoubleElecData = True
if "DoubleMuon" in dataStream:
  isDoubleMuonData = True

print "isDoubleElecData = ", isDoubleElecData
print "isDoubleMuonData = ", isDoubleMuonData

if isMC and (isDoubleElecData or isDoubleMuonData):
  raise Exception('isMC flag cannot be set to true with isDoubleMuonData or isDoubleElecData. Please check! (isMC={},isDoubleMuonData={},isDoubleElecData={})'.format(isMC,isDoubleMuonData,isDoubleElecData))

CMSXROOTD="root://xrootd-cms.infn.it/"
files=[]

if era == "2016":
  if isMC:
    files = [
      "/store/mc/RunIISummer16NanoAODv7/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_Nano02Apr2020_102X_mcRun2_asymptotic_v8_ext2-v1/120000/0643F6C0-C42B-564C-A9BD-161948BBFB81.root"
    ]
  else:
    if isDoubleMuonData:
      files = [
        "/store/data/Run2016H/DoubleMuon/NANOAOD/02Apr2020-v1/250000/24C37CC0-C415-5F43-96A6-F5D37E30B79B.root",
      ]
    elif isDoubleElecData:
      files = [
        "/store/data/Run2016H/DoubleEG/NANOAOD/02Apr2020-v1/250000/47FD42C2-6583-D941-95F4-1BFF0061C7D5.root",
      ]
  files = [CMSXROOTD+file for file in files]
elif era == "UL2017":
  if isMC:
    files = [
      "/store/mc/RunIISummer20UL17NanoAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mc2017_realistic_v8-v1/260000/135273C9-F6AB-444E-B7C2-8AFE427CB644.root"
    ]
  else:
    if isDoubleMuonData:
      files = [
        "/store/data/Run2017F/DoubleMuon/NANOAOD/UL2017_MiniAODv1_NanoAODv2-v1/280000/E9587C57-2425-0F4F-821E-E671B13B1C2F.root",
      ]
    elif isDoubleElecData:
      files = []
  files = [CMSXROOTD+file for file in files]

varTxtFileIn="./script/branches_in.txt"
varTxtFileOut="./script/branches_out.txt"

from RunSkimmerHelper import *
#
# Get JSON
#
CMSSW_BASE = os.getenv('CMSSW_BASE')
jsonInput = None
if not isMC:
  jsonInput = CMSSW_BASE+GetJSON(era)
#
# Get selection string
#
selection = GetSelection(era)
#
# Get list of modules modules
#
modules = GetModules(era,isMC,dataStream)

print "\n"
print "Just printout what we will give to the PostProcessor"
print "JSON      : ", jsonInput
print "SELECTION : ", selection
print "MODULES   : ", modules

maxEntries=None
if maxEvents > 0:
  maxEntries=maxEvents
  print "Maximum Number of Events to run over: ", maxEvents

p=PostProcessor(
  outDir, 
  files,
  cut=selection,
  branchsel=varTxtFileIn,
  outputbranchsel=varTxtFileOut,
  modules=modules,
  provenance=False,
  fwkJobReport=False,
  jsonInput=jsonInput if not(isMC) else None,
  maxEntries=maxEntries
)
p.run()

print "RunSkimmerLocal.py DONE"
