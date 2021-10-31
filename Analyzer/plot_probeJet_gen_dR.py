# Standard importts
import os
import ROOT
from collections import OrderedDict 

colors = [ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta]

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.LoadMacro("rootlogon.C")
ROOT.gROOT.SetStyle("customStyle");

def main():

  outputDir="./plots_dR/"
  # Make output directory if it does not exist
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)

  inFileName="./histos3D/Histo_MCUL17_DY_MG.root"
  PlotDeltaR(inFileName,outputDir,"UL2017")

  inFileName="./histos3D/Histo_MCUL18_DY_MG.root"
  PlotDeltaR(inFileName,outputDir,"UL2018")

  inFileName="./histos3D/Histo_MCUL16APV_DY_MG.root"
  PlotDeltaR(inFileName,outputDir,"UL2016APV")

  # inFileName="./histos3D/Histo_MCUL16_DY_MG.root"
  # PlotDeltaR(inFileName,outputDir,"UL2016")

def PlotDeltaR(inFileName, outputDir, year="UL17"):

  Histograms = OrderedDict()

  ptBinsStr = [
    "pt20To25",
    "pt25To30",
    "pt30To40",
    "pt40To50",
  ]
  ptBinsN = len(ptBinsStr)

  inFile = ROOT.TFile(inFileName,"OPEN")
  h2 = inFile.Get("h2_passNJetSel_probeJet_pt_closestgen_dR")
  for iptBin in xrange(1,ptBinsN+1):
    binStr   = "%s" %(ptBinsStr[iptBin-1])
    histName = "h_%s_%s_probeJet_%s" %("passNJetSel", binStr, "closestgen_dR")
    Histograms[histName] = h2.ProjectionY(histName, iptBin, iptBin)
    Histograms[histName].SetLineColor(colors[iptBin-1])
    Histograms[histName].Scale(1./Histograms[histName].Integral(0,400))
  #
  #
  #
  canv = ROOT.TCanvas("canv", "", 600, 600)
  legend = ROOT.TLegend(0.65,0.65,0.85,0.85)
  legend.SetTextSize(0.03)
  legend.SetLineWidth(0)
  legend.SetFillStyle(0)
  legend.SetBorderSize(0)

  for iBin, histName in enumerate(Histograms):
    #
    if iBin==0:
      Histograms[histName].SetMaximum(1.0)
      Histograms[histName].SetMinimum(0.0001)
      Histograms[histName].GetXaxis().SetTitleSize(0.045)
      Histograms[histName].GetYaxis().SetTitleSize(0.045)
      Histograms[histName].GetXaxis().SetLabelSize(0.045)
      Histograms[histName].GetYaxis().SetLabelSize(0.045)
      Histograms[histName].GetXaxis().SetTitle("#DeltaR(probeJet,closest genJet)")
      Histograms[histName].GetYaxis().SetTitle("Arbitrary Unit")
      Histograms[histName].Draw("HIST")
    else:
      Histograms[histName].Draw("HISTSAME")
    #
    ptBinLeg = ptBinsStr[iBin]
    ptBinLeg = ptBinLeg.replace("pt","")
    ptBinLeg = ptBinLeg.replace("To"," < pT < ")
    legend.AddEntry(Histograms[histName], ptBinLeg, "l")

  legend.Draw(" same ")
  canv.SetLogy()
  canv.SaveAs(os.path.join(outputDir, "h_closestgen_dR_"+year+".pdf"))


if __name__ == '__main__':
  main()