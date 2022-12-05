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

CMSXROOTD="root://cms-xrd-global.cern.ch//"
files=[]

if era == "UL2017":
  if isMC:
    files = ["/store/mc/RunIISummer20UL17NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/20UL17JMENano_106X_mc2017_realistic_v9-v1/2430000/0DBEF8A7-C29A-C64D-90FA-2DB21FB5876C.root "]
  else:
    if isDoubleMuonData: files = [
      # "/store/data/Run2017F/DoubleMuon/NANOAOD/UL2017_MiniAODv2_NanoAODv9-v1/120000/16F764BE-E96D-A44D-B252-272721365F16.root"
      "/store/data/Run2017B/DoubleMuon/NANOAOD/UL2017_MiniAODv2_NanoAODv9-v1/120000/7CDC57C5-1722-094A-AB1B-00B93B31CA83.root"
    ]
    elif isDoubleElecData: files = ["/store/data/Run2017F/DoubleEG/NANOAOD/UL2017_MiniAODv2_NanoAODv9-v1/270000/0F4C5317-F7FD-3C4C-AC79-231630A7E4E1.root"]
elif era == "UL2018":
  if isMC:
    files = ["/store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_upgrade2018_realistic_v16_L1v1-v1/120000/0CF0CDED-7582-7A49-84CD-0E5F73DE27B0.root"]
  else:
    if isDoubleMuonData: files = ["/store/data/Run2018C/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/130000/66302C54-6134-EF49-A766-A9A47B406837.root"]
    elif isDoubleElecData: files = ["/store/data/Run2018C/EGamma/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/250000/EA38CB63-D226-8E4C-A396-176C62A66CC8.root"]
elif era == "UL2016APV":
  if isMC:
    files = ["/store/mc/RunIISummer20UL16NanoAODAPVv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/106X_mcRun2_asymptotic_preVFP_v11-v1/280000/E9B9F84B-B094-504F-967E-CC85267C7F21.root"]
  else:
    if isDoubleMuonData: files = ["/store/data/Run2016E/DoubleMuon/NANOAOD/HIPM_UL2016_MiniAODv2_NanoAODv9-v1/70000/CEFE6A03-BC80-5D41-AA6D-756D57739CE1.root"]
    elif isDoubleElecData: files = ["/store/data/Run2016E/DoubleEG/NANOAOD/HIPM_UL2016_MiniAODv2_NanoAODv9-v1/120000/AE3D102E-2535-B941-A7B5-AE4FB44E5B29.root"]

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
modules = GetModules(era,isMC,dataStream,True)

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
