# Standard importts
import os
import ROOT
import math
from array import array
import numpy as np
import collections

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.SetStyle("Plain") # Not sure this is needed
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetMarkerSize(0.5)

def main():
  outputDir="./results_eff_compare_genbasedvsfit/"
  # Make output directory if it does not exist
  if not os.path.exists(outputDir):
      os.makedirs(outputDir)

  inDir_eff_fit = "../results_ULNanoV9_v1p3/Baseline/" 
  inDir_eff_gen = "./results_eff_genbased/" 

  for year in ["UL2017","UL2018","UL2016APV"]:
    for wp in ["Loose","Medium","Tight"]:
      wpShort=wp[0]

      inFile_eff_fit    = ROOT.TFile.Open(inDir_eff_fit+"/"+year+"_WP"+wp+"/h2_eff_mc"+year+"_"+wpShort+".root")
      inFile_eff_gen    = ROOT.TFile.Open(inDir_eff_gen+"/h2_gen_eff_mc"+year+"_"+wpShort+".root")

      inFile_mistag_fit = ROOT.TFile.Open(inDir_eff_fit+"/"+year+"_WP"+wp+"/h2_mistag_mc"+year+"_"+wpShort+".root")
      inFile_mistag_gen = ROOT.TFile.Open(inDir_eff_gen+"/h2_gen_mistag_mc"+year+"_"+wpShort+".root")

      h2_eff_fit = inFile_eff_fit.Get("h2_eff_mc"+year+"_"+wpShort)
      h2_eff_gen = inFile_eff_gen.Get("h2_gen_eff_mc"+year+"_"+wpShort)

      h2_mistag_fit = inFile_mistag_fit.Get("h2_mistag_mc"+year+"_"+wpShort)
      h2_mistag_gen = inFile_mistag_gen.Get("h2_gen_mistag_mc"+year+"_"+wpShort)

      Plot2DGenEff(h2_eff_fit, h2_eff_gen, h2_mistag_fit, h2_mistag_gen, outputDir, year, wp)

def Plot2DGenEff(h2_eff_fit, h2_eff_gen, h2_mistag_fit, h2_mistag_gen, outputDir,  year="UL17", wp="Loose"):

  ROOT.gStyle.SetPaintTextFormat("4.2f")
  textsize=1

  #
  # Efficiency histo
  #
  h2_eff_diff = h2_eff_fit.Clone("h2_eff_diff")
  h2_eff_diff.Reset()

  nbinsX = h2_eff_fit.GetNbinsX()
  nbinsY = h2_eff_fit.GetNbinsY()

  for iBinX in range(1,nbinsX+1):
    for iBinY in range(1,nbinsY+1):
      eff_fit =  h2_eff_fit.GetBinContent(iBinX,iBinY)
      eff_gen =  h2_eff_gen.GetBinContent(iBinX,iBinY)
      diff = 2.00
      if eff_fit > 0.0:
        diff = abs((eff_gen-eff_fit)/eff_fit)
      h2_eff_diff.SetBinContent(iBinX,iBinY,diff)

  h2_eff_diff.SetTitle("|#DeltaEfficiency| " +wp+ ", "+year)
  
  #
  #
  #
  c1 = ROOT.TCanvas("c1","c1",600,600)
  h2_eff_diff.SetMinimum(0.0)
  h2_eff_diff.SetMaximum(0.1)
  h2_eff_diff.SetMarkerSize(textsize)
  h2_eff_diff.Draw("colztext")
  c1.SaveAs(outputDir+"h2_dif_eff_"+year+"_"+wp+".pdf")
  h2_eff_diff.SetName("h2_diff_eff_mc"+year+"_"+wp)
  # h2_eff_diff.SaveAs(outputDir+"h2_diff_eff_MC"+year+"_"+wp+".root")
  del c1


  #
  # Mistag histo
  #
  h2_mistag_diff = h2_mistag_fit.Clone("h2_mistag_diff")
  h2_mistag_diff.Reset()

  nbinsX = h2_mistag_fit.GetNbinsX()
  nbinsY = h2_mistag_fit.GetNbinsY()

  for iBinX in range(1,nbinsX+1):
    for iBinY in range(1,nbinsY+1):
      mistag_fit =  h2_mistag_fit.GetBinContent(iBinX,iBinY)
      mistag_gen =  h2_mistag_gen.GetBinContent(iBinX,iBinY)
      diff = 2.00
      if mistag_fit > 0.0:
        diff = abs((mistag_gen-mistag_fit)/mistag_fit)
      h2_mistag_diff.SetBinContent(iBinX,iBinY,diff)

  h2_mistag_diff.SetTitle("|#DeltaMistag| " +wp+ ", "+year)
  
  #
  #
  #
  c2 = ROOT.TCanvas("c2","c2",600,600)
  h2_mistag_diff.SetMinimum(0.0)
  h2_mistag_diff.SetMaximum(0.2)
  h2_mistag_diff.SetMarkerSize(textsize)
  h2_mistag_diff.Draw("colztext")
  c2.SaveAs(outputDir+"h2_dif_mistag_"+year+"_"+wp+".pdf")
  h2_mistag_diff.SetName("h2_diff_mistag_mc"+year+"_"+wp)
  # h2_mistag_diff.SaveAs(outputDir+"h2_diff_mistag_MC"+year+"_"+wp+".root")
  del c2





if __name__ == '__main__':
  main()