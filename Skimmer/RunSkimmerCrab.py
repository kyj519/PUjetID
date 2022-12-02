#!/usr/bin/env python
import os,sys
import ROOT
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *

print "RunSkimmerCrab.py START"

parser = argparse.ArgumentParser("")
parser.add_argument('-jobNum','--jobNum', type=int, default=1 ) #NOTE: This will be given by condor on the grid. not by us
parser.add_argument('--era',              type=str, default="")
parser.add_argument('--isMC',             type=int ,default=0)
parser.add_argument('--dataStream',       type=str ,default="")
parser.add_argument('--useJMENano', type=int, default = 0)

args = parser.parse_args()
era  = args.era
isMC = args.isMC
dataStream = args.dataStream
useJMENano = True if args.useJMENano else False

print "args = ", args
print "era  = ", era
print "isMC = ", isMC 
print "dataStream = ", dataStream
print 'useJMENano', useJMENano  

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
modules = GetModules(era,isMC,dataStream,useJMENano)

print "\n"
print "Just printout what we will give to the PostProcessor"
print "JSON      : ", jsonInput
print "SELECTION : ", selection
print "MODULES   : ", modules

# 
# This takes care of converting the input files from CRAB
#
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles, runsAndLumis

p=PostProcessor(
  ".", 
  inputFiles(),
  cut=selection,
  branchsel="branches_in.txt",
  outputbranchsel="branches_out.txt",
  modules=modules,
  provenance=True,
  fwkJobReport=True,
  jsonInput=jsonInput if not(isMC) else None,
  prefetch = True
)
p.run()

print "RunSkimmerCrab.py DONE"
os.system("ls -lR")
