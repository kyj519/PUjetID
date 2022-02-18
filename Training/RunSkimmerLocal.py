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

if era == "UL2017":
  if isMC:
    files = ["/store/mc/RunIISummer20UL17NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/20UL17JMENano_106X_mc2017_realistic_v9-v1/2430000/2A52CFEE-0B47-B34F-8A88-82481C9FBD50.root"]
  else:
    if isDoubleMuonData: files = ["/store/data/Run2017F/DoubleMuon/NANOAOD/UL2017_MiniAODv2_JMENanoAODv9-v1/2500000/727978E9-485D-FE48-B9CD-364CE42A656D.root"]
    elif isDoubleElecData: files = ["/store/data/Run2017F/DoubleEG/NANOAOD/UL2017_MiniAODv2_JMENanoAODv9-v1/100000/8F7E0F1A-6A3C-8B46-89B7-81C2E7951161.root"]
elif era == "UL2018":
  if isMC:
    files = ["/store/mc/RunIISummer20UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/20UL18JMENano_106X_upgrade2018_realistic_v16_L1v1-v1/230000/8D8A094D-7829-EE49-8245-EB4A2CB7483C.root"]
  else:
    if isDoubleMuonData: files = [
      "/store/data/Run2018C/DoubleMuon/NANOAOD/UL2018_MiniAODv2_JMENanoAODv9-v1/100000/BEC06A5C-652E-8E47-8738-69175BC2621A.root"
    ]
    elif isDoubleElecData: files = ["/store/data/Run2018C/EGamma/NANOAOD/UL2018_MiniAODv2_JMENanoAODv9-v1/250000/2F2B038D-F015-4147-BD8D-AE2C10394132.root"]



# files = [CMSXROOTD+file for file in files]

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
