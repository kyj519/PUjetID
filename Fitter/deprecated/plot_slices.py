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
  inFileName="results_ULNanoV2_v1p1/Baseline/UL2017_WPMedium/h2_mistag_mc_UL2017_Medium.root"
  PlotSlices(inFileName)

def PlotSlices(inFileName):

  #
  # pt Binning
  #
  _pt = [
    "20To25",
    "25To30",
    "30To40",
    "40To50",
  ]

  inFile  = ROOT.TFile.Open(inFileName)
  histo2D = inFile.Get("h2_mistag_mcUL2017_Medium")
  print histo2D

  histoDict = collections.OrderedDict()

  for i in range(0,len(_pt)):
    iBin = i+1
    histName = "h_mistag_mcUL17_Medium_pt"+_pt[i]+"_eta"
    histoDict[histName] = histo2D.ProjectionY(histName,iBin,iBin)
    print i

  color  = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kMagenta]
  marker = [ROOT.kOpenCircle, ROOT.kOpenSquare, ROOT.kOpenTriangleUp, ROOT.kOpenDiamond]

  c1 = ROOT.TCanvas("c1","c1",600,600)


  legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
  legend.SetFillColor(0)
  legend.SetLineColor(0)


  for iH, hName in enumerate(histoDict):
    h = histoDict[hName]
    # h.SetMinimum(0.2)
    # h.SetMaximum(1.8)
    h.SetMinimum(0.005)
    h.SetMaximum(6.0)
    h.SetMarkerSize(1.5)
    # h.SetMarkerColor(color[iH])
    h.SetMarkerColor(ROOT.kRed+iH)
    h.SetMarkerStyle(marker[iH])
    # h.SetLineColor(color[iH])
    h.SetLineColor(ROOT.kRed+iH)
    h.SetLineWidth(2)
    legend.AddEntry(h,(_pt[iH].replace("To"," < pT < "))+" GeV", "lp")
    if iH == 0:
      # h.Draw("PE0X0")
      h.Draw("PE0")
    else:
      # h.Draw("PE0X0SAME")
      h.Draw("PE0SAME")
    print iH
  legend.Draw("same")
  c1.SetLogy()
  c1.SaveAs("test.pdf")


if __name__ == '__main__':
  main()