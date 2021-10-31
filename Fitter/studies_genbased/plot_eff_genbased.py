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

  ROOT.gStyle.SetTitleStyle(0)
  ROOT.gStyle.SetTitleBorderSize(0)

  outputDir="./results_eff_genbased/"
  # Make output directory if it does not exist
  if not os.path.exists(outputDir):
      os.makedirs(outputDir)

  inFileName="../../Analyzer/histos3D/Histo_MCUL17_DY_MG.root"
  Plot2DGenEff(inFileName,outputDir,"UL2017","Loose")
  Plot2DGenEff(inFileName,outputDir,"UL2017","Medium")
  Plot2DGenEff(inFileName,outputDir,"UL2017","Tight")

  inFileName="../../Analyzer/histos3D/Histo_MCUL18_DY_MG.root"
  Plot2DGenEff(inFileName,outputDir,"UL2018","Loose")
  Plot2DGenEff(inFileName,outputDir,"UL2018","Medium")
  Plot2DGenEff(inFileName,outputDir,"UL2018","Tight")

  inFileName="../../Analyzer/histos3D/Histo_MCUL16APV_DY_MG.root"
  Plot2DGenEff(inFileName,outputDir,"UL2016APV","Loose")
  Plot2DGenEff(inFileName,outputDir,"UL2016APV","Medium")
  Plot2DGenEff(inFileName,outputDir,"UL2016APV","Tight")

  # inFileName="../Analyzer/histos3D/Histo_MCUL16_DY_MG.root"
  # Plot2DGenEff(inFileName,outputDir,"UL2016","Loose")
  # Plot2DGenEff(inFileName,outputDir,"UL2016","Medium")
  # Plot2DGenEff(inFileName,outputDir,"UL2016","Tight")

def PlotPtSlices(h2, hNamePrefix, pdfName):
  _pt = [
    "20To25",
    "25To30",
    "30To40",
    "40To50",
  ]
  xbins = []
  # ptbin
  for ptBin in _pt:
    xbins.append(float(ptBin.split("To")[0]))
    xbins.append(float(ptBin.split("To")[1]))

  h2C = h2.Clone(h2.GetName()+"Clone")
  #
  # Get Eff/Mistag/SF vs eta in pt slices 
  #
  histoDict = collections.OrderedDict()
  for i in range(0,len(_pt)):
    iBin = i+1
    hName = hNamePrefix+"_pt"+_pt[i]+"_eta"
    histoDict[hName] = h2.ProjectionY(hName, iBin, iBin)

  canv   = ROOT.TCanvas("canv","canv",600,600)
  legend = None
  ymin   = None 
  ymax   = None
  doLogY = False
  if "h2_gen_mistag" in h2.GetName():
    legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
    ymin = 0.001
    ymax = 6.000
    doLogY = True
  if "h2_gen_eff" in h2.GetName():
    legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
    ymin = 0.2
    ymax = 1.4
  if "h2_gen_purity" in h2.GetName():
    legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
    ymin = 0.0
    ymax = 1.5
  legend.SetFillColor(0)
  legend.SetLineColor(0)

  marker = [ROOT.kOpenCircle, ROOT.kOpenSquare, 
    ROOT.kOpenTriangleUp, ROOT.kOpenDiamond
  ]

  for iH, hName in enumerate(histoDict):
    h = histoDict[hName]
    h.SetMinimum(ymin)
    h.SetMaximum(ymax)
    h.SetMarkerSize(1.5)
    h.SetMarkerColor(ROOT.kRed+iH)
    h.SetMarkerStyle(marker[iH])
    h.SetLineColor(ROOT.kRed+iH)
    h.SetLineWidth(2)
    legend.AddEntry(h,(_pt[iH].replace("To"," < pT < "))+" GeV", "lp")
    if iH == 0:
      h.Draw("PE0")
    else:
      h.Draw("PE0SAME")
    legend.Draw("same")
  if doLogY:
    canv.SetLogy()
  canv.SaveAs(pdfName)
  del canv

def Plot2DGenEff(inFileName, outputDir, year="UL17", wp="Loose"):

  ROOT.gStyle.SetPaintTextFormat("4.2f")
  textsize=1

  wpShort=wp[0]

  inFile = ROOT.TFile(inFileName)

  #
  #
  #
  histoDict = collections.OrderedDict()
  histoDict["passPUID_passGenMatch"] = inFile.Get("h2_passNJetSel_probeJet_passPUID"+wp+"_passGenMatch_probeJet_pt_eta_count")
  histoDict["passPUID_failGenMatch"] = inFile.Get("h2_passNJetSel_probeJet_passPUID"+wp+"_failGenMatch_probeJet_pt_eta_count")
  histoDict["failPUID_passGenMatch"] = inFile.Get("h2_passNJetSel_probeJet_failPUID"+wp+"_passGenMatch_probeJet_pt_eta_count")
  histoDict["failPUID_failGenMatch"] = inFile.Get("h2_passNJetSel_probeJet_failPUID"+wp+"_failGenMatch_probeJet_pt_eta_count")

  #
  # Efficiency histo
  #
  h2_eff_denom = histoDict["passPUID_passGenMatch"].Clone("h2_gen_eff_denom")
  h2_eff_denom.Add(histoDict["failPUID_passGenMatch"]) # Denominator
  h2_eff_denom.Sumw2()
    
  
  h2_eff = histoDict["passPUID_passGenMatch"].Clone("h2_gen_eff") # Numerator
  h2_eff.Sumw2()
  h2_eff.Divide(h2_eff, h2_eff_denom,1,1,"B") # Numer/Denom = Eff
  h2_eff.SetTitle("MC-only Gen-based Efficiency, WP " +wp+ ", "+year)
  h2_eff.GetXaxis().SetTitle("Jet p_{T} [GeV]")   
  h2_eff.GetYaxis().SetTitle("Jet #eta")   
  
  #
  #
  #
  c1 = ROOT.TCanvas("c1","c1",600,600)
  h2_eff.SetMinimum(0.4)
  h2_eff.SetMaximum(1.0)
  h2_eff.SetMarkerSize(textsize)

  h2_eff.Draw("colztexterr")
  c1.SaveAs(outputDir+"h2_gen_eff_mc_"+year+"_"+wpShort+".pdf")
  h2_eff.SetName("h2_gen_eff_mc"+year+"_"+wpShort)
  h2_eff.SaveAs(outputDir+"h2_gen_eff_mc_"+year+"_"+wpShort+".root")
  PlotPtSlices(h2_eff, "h_gen_eff_mc_"+year+"_"+wpShort, outputDir+"h_gen_eff_mc_"+year+"_"+wpShort+"_ptBins_eta.pdf")
  del c1

  #
  # Mistag histo
  #
  h2_mistag_denom = histoDict["passPUID_failGenMatch"].Clone("h2_gen_mistag_denom")
  h2_mistag_denom.Add(histoDict["failPUID_failGenMatch"]) # Denominator
  h2_mistag_denom.Sumw2()
  
  h2_mistag = histoDict["passPUID_failGenMatch"].Clone("h2_gen_mistag") # Numerator
  h2_mistag.Sumw2()
  h2_mistag.Divide(h2_mistag, h2_mistag_denom,1,1,"B") # Numer/Denom = Mistag
  h2_mistag.SetTitle("MC-only Gen-based Mistag, WP " +wp+ ", "+year)
  h2_mistag.GetXaxis().SetTitle("Jet p_{T} [GeV]")   
  h2_mistag.GetYaxis().SetTitle("Jet |#eta|")   
  
  #
  #
  #
  c2 = ROOT.TCanvas("c2","c2",600,600)
  h2_mistag.SetMinimum(0.01)
  h2_mistag.SetMaximum(1.0)
  h2_mistag.SetMarkerSize(textsize)
  h2_mistag.Draw("colztexterr")
  c2.SaveAs(outputDir+"h2_gen_mistag_mc_"+year+"_"+wpShort+".pdf")
  h2_mistag.SetName("h2_gen_mistag_mc"+year+"_"+wpShort)
  h2_mistag.SaveAs(outputDir+"h2_gen_mistag_mc_"+year+"_"+wpShort+".root")
  PlotPtSlices(h2_mistag, "h_gen_mistag_mc_"+year+"_"+wpShort, outputDir+"h_gen_mistag_mc_"+year+"_"+wpShort+"_ptBins_eta.pdf")
  del c2

  #
  # Purity histo
  #
  h2_purity_denom = histoDict["passPUID_passGenMatch"].Clone("h2_gen_purity_denom")
  h2_purity_denom.Add(histoDict["passPUID_failGenMatch"]) # Denominator
  h2_purity_denom.Sumw2()
  
  h2_purity = histoDict["passPUID_passGenMatch"].Clone("h2_gen_purity") # Numerator
  h2_purity.Sumw2()
  h2_purity.Divide(h2_purity, h2_purity_denom,1,1,"B") # Numer/Denom = Purity
  h2_purity.SetTitle("MC-only Gen-based Purity, WP " +wp+ ", "+year)
  
  #
  #
  #
  c3 = ROOT.TCanvas("c2","c2",600,600)
  h2_purity.SetMinimum(0.01)
  h2_purity.SetMaximum(1.0)
  h2_purity.SetMarkerSize(textsize)
  h2_purity.Draw("colztexterr")
  c3.SaveAs(outputDir+"h2_gen_purity_mc_"+year+"_"+wpShort+".pdf")
  PlotPtSlices(h2_purity, "h_gen_purity_mc_"+year+"_"+wpShort, outputDir+"h_gen_purity_mc_"+year+"_"+wpShort+"_ptBins_eta.pdf")
  del c3

  inFile.Close()


if __name__ == '__main__':
  main()