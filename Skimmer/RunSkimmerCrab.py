#!/usr/bin/env python
import os,sys
import ROOT
import argparse
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2016
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2017
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeight_2018

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import * 

from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_mc
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_data_dielectron
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2016_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2017_data_dimuon 
from PUjetID.Skimmer.SkimmerDiLepton import SkimmerDiLepton_2018_data_dimuon 

print "RunSkimmerCrab.py START"

parser = argparse.ArgumentParser("")
parser.add_argument('-jobNum','--jobNum', type=int, default=1 ) #NOTE: This will be given by condor on the grid. not by us
parser.add_argument('--era',              type=str, default="")
parser.add_argument('--isMC',             type=int ,default=0)
parser.add_argument('--dataStream',       type=str ,default="")

args = parser.parse_args()
era  = args.era
isMC = args.isMC
dataStream = args.dataStream

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
)
p.run()

print "RunSkimmerCrab.py DONE"
os.system("ls -lR")

