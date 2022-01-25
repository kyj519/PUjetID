#!/usr/bin/env python
import argparse
import subprocess
import glob
import os
import ROOT
from array import array
import time

import samplesInfo
#
#
#
def add_weight_branch(file, xsec, lumi=1000., treename='Events', wgtbranch='xsecWeight'):
  def _get_sum(tree, wgtvar):
    htmp = ROOT.TH1D('htmp', 'htmp', 1, 0, 10)
    tree.Project('htmp', '1.0', wgtvar)
    return float(htmp.Integral())

  def _fill_const_branch(tree, branch_name, buff, lenVar=None):
    if lenVar is not None:
      b = tree.Branch(branch_name, buff, '%s[%s]/F' % (branch_name, lenVar))
      b_lenVar = tree.GetBranch(lenVar)
      buff_lenVar = array('I', [0])
      b_lenVar.SetAddress(buff_lenVar)
    else:
      b = tree.Branch(branch_name, buff, branch_name + '/F')

    b.SetBasketSize(tree.GetEntries() * 2)  # be sure we do not trigger flushing
    for i in range(tree.GetEntries()):
      if lenVar is not None:
        b_lenVar.GetEntry(i)
      b.Fill()

    b.ResetAddress()
    if lenVar is not None:
      b_lenVar.ResetAddress()

  f = ROOT.TFile(file, 'UPDATE')
  run_tree = f.Get('Runs')
  tree = f.Get(treename)

  # fill cross section weights to the 'Events' tree
  sumwgts = _get_sum(run_tree, 'genEventSumw')
  xsecwgt = xsec * lumi / sumwgts
  xsec_buff = array('f', [xsecwgt])
  _fill_const_branch(tree, wgtbranch, xsec_buff)
  
  # fill sum of weights to the 'Events' tree
  sumwgts_buff = array('f', [sumwgts])
  _fill_const_branch(tree, "genEventSumw", sumwgts_buff)

  # fill xsec to the 'Events' tree
  xsec_buff = array('f', [xsec])
  _fill_const_branch(tree, "xsec", xsec_buff)

  # fill LHE weight re-normalization factors
  if tree.GetBranch('LHEScaleWeight'):
    run_tree.GetEntry(0)
    nScaleWeights = run_tree.nLHEScaleSumw
    scale_weight_norm_buff = array('f', [sumwgts / _get_sum(run_tree, 'LHEScaleSumw[%d]*genEventSumw' % i) for i in range(nScaleWeights)])
    print('LHEScaleWeightNorm: ' + str(scale_weight_norm_buff))
    _fill_const_branch(tree, 'LHEScaleWeightNorm', scale_weight_norm_buff, lenVar='nLHEScaleWeight')

  if tree.GetBranch('LHEPdfWeight'):
    run_tree.GetEntry(0)
    nPdfWeights = run_tree.nLHEPdfSumw
    pdf_weight_norm_buff = array('f', [sumwgts / _get_sum(run_tree, 'LHEPdfSumw[%d]*genEventSumw' % i) for i in range(nPdfWeights)])
    print('LHEPdfWeightNorm: ' + str(pdf_weight_norm_buff))
    _fill_const_branch(tree, 'LHEPdfWeightNorm', pdf_weight_norm_buff, lenVar='nLHEPdfWeight')

  tree.Write(treename, ROOT.TObject.kOverwrite)
  f.Close()
#
#
#
parser = argparse.ArgumentParser("")
parser.add_argument('-s',  '--sample', type=str, default="")

args = parser.parse_args()
sample = args.sample

samplesInfoDict = samplesInfo.samplesInfoDict
path_inDir = samplesInfo.path_inDir
path_outDir = samplesInfo.path_outDir
EOSURL = samplesInfo.EOSURL


if sample in samplesInfoDict:
  print("Sample path is in samplesInfoDict: "+sample) 
else:
  raise RuntimeError("Sample path is NOT in samplesInfoDict: "+sample+". Please check again!")

#
# Make output directory on EOS if it doesn't exist
#
if not os.path.exists(path_outDir):
  os.makedirs(path_outDir)

timerMain = ROOT.TStopwatch()
timerMain.Start()

print("===================START")
print("Merging: " + sample)
#
# Check if sample is MC or not
#
isMC = True if "MC" in sample else False
#
#
#
inFileList=[]
for path in samplesInfoDict[sample]["path"]:
  pathSampleToGlob = path_inDir+path
  inFileList += [EOSURL+f for f in glob.glob(pathSampleToGlob)]

if len(inFileList) == 0:
  raise RuntimeError("List of file empty for: "+sample)

print("Sample input files:")
for file in inFileList:
  print(file)
print("------------------------------")

#
# Merged output file path
#
mergedFileName = "%s.root"%(sample)
mergedFileTempPath = "%s/%s"%(os.getenv("TMPDIR"), mergedFileName)
print("Temporary merged output file path: "+mergedFileTempPath)
#
#
#
path_exec = "../../../PhysicsTools/NanoAODTools/scripts/haddnano.py"
command = [path_exec, mergedFileTempPath] + inFileList
subprocess.call(command) #call() is a py2 command
print("------------------------------")
#
#
#
sleep_nseconds=10
print("Sleep Now For A While: "+str(sleep_nseconds)+" seconds")
time.sleep(sleep_nseconds)
print("------------------------------")
#
#
#
if isMC:
  print("Adding weight branches for: " + sample)
  add_weight_branch(
    mergedFileTempPath,
    xsec=samplesInfo.samplesInfoDict[sample]["xsec"],
    lumi=1.0, # Set to 1.0 inverse-picobarn. Normalize later in template maker
    treename="Events",
    wgtbranch="xsecWeight",
  )
  print("Finished adding weight branches")
timerMain.Stop()
timerMain.Print()
timerMain.Continue()
print("------------------------------")
#
#
#
mergedFileFinalPath = "%s%s/%s.root"%(EOSURL,path_outDir,sample)
print("Copying file to final destination directory: "+mergedFileFinalPath)
command = ["xrdcp", "-f", mergedFileTempPath, mergedFileFinalPath]
subprocess.call(command) #call() is a py2 command
timerMain.Stop()
timerMain.Print()
timerMain.Continue()
print("------------------------------")
#
#
#
print("Deleting local temporary file: "+mergedFileTempPath)
command = ["rm", "-fv", mergedFileTempPath]
subprocess.call(command) #call() is a py2 command
timerMain.Stop()
timerMain.Print()
print("===================DONE::"+sample)

