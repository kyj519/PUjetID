import os
import ROOT
import math
import collections
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPaintTextFormat("4.3f")
ROOT.gROOT.SetStyle("Plain")

resultsDir  = "./results_ULNanoV9_v1p4/"
outputDir   = "./results_final_EffAndSf_ULNanoV9_v1p4/"
outFileName = "PUID_SFAndEff_ULNanoV9_v1p4"
printPNG    = False
#
#
#
def main():
  eras = [
    "UL2018",
    "UL2017",
    "UL2016",
    "UL2016APV",
  ]
  wps = [
    "Loose",
    "Medium",
    "Tight"
  ]
  #
  #
  #
  histo2DList = []
  for wp in wps:
    for era in eras:
      histo2DList += MakeMaps(resultsDir,era,wp)
  #
  #
  #
  histo2DList.sort(key=lambda x:x.GetName())

  #
  # Make output directory if it does not exist
  #
  if not os.path.exists(outputDir):
    os.makedirs(outputDir)
  
  #
  #
  #
  outFile = ROOT.TFile(outputDir+"/"+outFileName+".root","RECREATE")
  for h2 in histo2DList:
    h2.SetMarkerSize(1)
    h2.Write()
  outFile.Close()

  #
  #
  #
  inFile = ROOT.TFile(outputDir+"/"+outFileName+".root","OPEN")
  h2KeysList = inFile.GetListOfKeys()
  for h2Key in h2KeysList:
    h2 = h2Key.ReadObj()
    if "FracSystuncty" in h2.GetName(): continue # Don't plot FracSystuncty
    PlotMap(h2)

def PlotMap(h2):
  ROOT.gStyle.SetPaintTextFormat("6.6f")
  h2Name = h2.GetName()
  canv = ROOT.TCanvas("canv","canv",600,600)
  h2.SetMarkerSize(1.40)
  h2.Draw("colztext")
  canv.SaveAs(os.path.join(outputDir, h2Name+".pdf"))
  if printPNG: canv.SaveAs(os.path.join(outputDir, h2Name+".png"))
  del canv

def MakeMaps(resultsDir,era,wp):

  wpStr  = wp[0]
  eraStr = era
  
  def GetHistoFromFile(inDir, hName):
    inFile = ROOT.TFile.Open("%s%s.root"%(inDir,hName))
    h = inFile.Get(hName)
    hC = h.Clone(hName)
    ROOT.SetOwnership(hC, False); hC.SetDirectory(0)
    inFile.Close()
    return hC

  def MakeMapSystFit(hNominal):
    h2_syst = hNominal.Clone("h2_syst")
    h2_syst.Reset()
    h2_syst.SetMaximum(0.100)
    h2_syst.SetMinimum(0.000)

    h2_syst_frac = hNominal.Clone("h2_syst_frac")
    h2_syst_frac.Reset()
    h2_syst_frac.SetMaximum(0.100)
    h2_syst_frac.SetMinimum(0.000)

    nbinsX = hNominal.GetNbinsX()
    nbinsY = hNominal.GetNbinsY()

    for iBinX in range(1,nbinsX+1):
      for iBinY in range(1,nbinsY+1):
        valNominal = hNominal.GetBinContent(iBinX,iBinY)
        valSyst = hNominal.GetBinError(iBinX,iBinY)
        h2_syst.SetBinContent(iBinX,iBinY,valSyst)
        if valNominal > 0:
          h2_syst_frac.SetBinContent(iBinX,iBinY,(valSyst/valNominal))
        else:
          h2_syst_frac.SetBinContent(iBinX,iBinY,0)
    return h2_syst, h2_syst_frac

  def MakeMapSystOneSided(hNominal, hSyst):
    h2_syst = hNominal.Clone("h2_syst")
    h2_syst.Reset()
    h2_syst.SetMaximum(0.100)
    h2_syst.SetMinimum(0.000)

    h2_syst_frac = hNominal.Clone("h2_syst_frac")
    h2_syst_frac.Reset()
    h2_syst_frac.SetMaximum(0.100)
    h2_syst_frac.SetMinimum(0.000)

    nbinsX = hNominal.GetNbinsX()
    nbinsY = hNominal.GetNbinsY()

    for iBinX in range(1,nbinsX+1):
      for iBinY in range(1,nbinsY+1):
        valNominal =  hNominal.GetBinContent(iBinX,iBinY)
        valSyst =  hSyst.GetBinContent(iBinX,iBinY)
        absDiff = abs(valNominal-valSyst)
        h2_syst.SetBinContent(iBinX,iBinY,absDiff)
        if valNominal > 0:
          absDiffFrac = absDiff/valNominal
        else:
          absDiffFrac = 0
        h2_syst_frac.SetBinContent(iBinX,iBinY,absDiffFrac)

    return h2_syst, h2_syst_frac

  def MakeMapSystTwoSided(hNominal, hSystUp, hSystDown):
    h2_syst = hNominal.Clone("h2_syst")
    h2_syst.Reset()
    h2_syst.SetMaximum(0.100)
    h2_syst.SetMinimum(0.000)

    h2_syst_frac = hNominal.Clone("h2_syst_frac")
    h2_syst_frac.Reset()
    h2_syst_frac.SetMaximum(0.100)
    h2_syst_frac.SetMinimum(0.000)

    nbinsX = hNominal.GetNbinsX()
    nbinsY = hNominal.GetNbinsY()

    for iBinX in range(1,nbinsX+1):
      for iBinY in range(1,nbinsY+1):
        valNominal = hNominal.GetBinContent(iBinX,iBinY)
        valSystUp = hSystUp.GetBinContent(iBinX,iBinY)
        valSystDown = hSystDown.GetBinContent(iBinX,iBinY)
        absDiff_SystUp   = abs(valNominal - valSystUp)
        absDiff_SystDown = abs(valNominal - valSystDown)
        absDiff = max(absDiff_SystUp,absDiff_SystDown)
        h2_syst.SetBinContent(iBinX,iBinY,absDiff)
        if valNominal > 0:
          absDiffFrac = absDiff/valNominal
        else:
          absDiffFrac = 0
        h2_syst_frac.SetBinContent(iBinX,iBinY,absDiffFrac)

    return h2_syst, h2_syst_frac

  def MakeMapSystTotal(hNominal, hSystList=[]):
    h2_syst = hNominal.Clone("h2_syst")
    h2_syst.Reset()
    h2_syst.SetMaximum(0.100)
    h2_syst.SetMinimum(0.000)

    h2_syst_frac = hNominal.Clone("h2_syst_frac")
    h2_syst_frac.Reset()
    h2_syst_frac.SetMaximum(0.100)
    h2_syst_frac.SetMinimum(0.000)

    nbinsX = hNominal.GetNbinsX()
    nbinsY = hNominal.GetNbinsY()

    for iBinX in range(1,nbinsX+1):
      for iBinY in range(1,nbinsY+1):
        valNominal =  hNominal.GetBinContent(iBinX,iBinY)
        #
        #
        #
        valSystTotal = 0.
        for hSyst in hSystList:
          valSyst =  hSyst.GetBinContent(iBinX,iBinY)
          valSystTotal += (valSyst*valSyst)
        valSystTotal = math.sqrt(valSystTotal)
        h2_syst.SetBinContent(iBinX,iBinY,valSystTotal)
        if valNominal > 0:
          absDiffFrac = valSystTotal/valNominal
        else:
          absDiffFrac = 0
        h2_syst_frac.SetBinContent(iBinX,iBinY,absDiffFrac)

    return h2_syst, h2_syst_frac
  
  #
  # Use NLO sample as Nominal.
  #
  inDir_Nominal      = resultsDir + "/NLO/%s_WP%s/" %(era,wp)
  inDir_jesTotalUp   = resultsDir + "/NLO_jesTotalUp/%s_WP%s/" %(era,wp)
  inDir_jesTotalDown = resultsDir + "/NLO_jesTotalDown/%s_WP%s/" %(era,wp)

  #
  # MC Eff & MC Mistag
  #
  print("Retrieving MC Eff and Mistag for "+ wp +" WP and era " + era)
  h2_eff_mc    = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_eff_mc",eraStr,wpStr))
  h2_mistag_mc = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_mistag_mc",eraStr,wpStr))

  #
  # SF Eff & SF Mistag
  #
  print("Retrieving SF Eff and Mistag for "+ wp +" WP and era " + era)
  h2_eff_sf    = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_eff_sf",eraStr,wpStr))
  h2_mistag_sf = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_mistag_sf",eraStr,wpStr))

  #
  # SF Eff & SF Mistag (Fit Uncertainty)
  #
  print("Retrieving Fit Uncertainty for SF Eff and Mistag for "+ wp +" WP and era " + era)
  h2_eff_sf_syst_fit, h2_eff_sf_fracsyst_fit = MakeMapSystFit(h2_eff_sf)
  h2_eff_sf_syst_fit.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"Systuncty_Fit"),"Efficiency SF Unc (Fit), WP " +wp+ ", "+era)
  h2_eff_sf_fracsyst_fit.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"FracSystuncty_Fit"),"Efficiency SF Fractional Unc (Fit), WP " +wp+ ", "+era)

  h2_mistag_sf_syst_fit,h2_mistag_sf_fracsyst_fit = MakeMapSystFit(h2_mistag_sf)
  h2_mistag_sf_syst_fit.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"Systuncty_Fit"),"Mistag SF Unc (Fit), WP " +wp+ ", "+era)
  h2_mistag_sf_fracsyst_fit.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"FracSystuncty_Fit"),"Efficiency SF Fractional Unc (Fit), WP " +wp+ ", "+era)

  #
  # SF Eff & SF Mistag (Uncertainty due to difference wrt to Gen-based info Efficiency and Mistag)
  #
  print("Retrieving Gen Uncertainty for SF Eff and Mistag for "+ wp +" WP and era " + era)
  h2_effgen_sf       = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_effgen_sf",eraStr,wpStr))

  h2_eff_sf_syst_gen, h2_eff_sf_fracsyst_gen = MakeMapSystOneSided(h2_eff_sf,h2_effgen_sf)
  h2_eff_sf_syst_gen.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"Systuncty_Gen"),"Efficiency SF Unc (Gen), WP " +wp+ ", "+era)
  h2_eff_sf_fracsyst_gen.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"FracSystuncty_Gen"),"Efficiency SF Fractional Unc (Gen), WP " +wp+ ", "+era)

  h2_mistaggen_sf = GetHistoFromFile(inDir_Nominal, "%s%s_%s"%("h2_mistaggen_sf",eraStr,wpStr))

  h2_mistag_sf_syst_gen, h2_mistag_sf_fracsyst_gen = MakeMapSystOneSided(h2_mistag_sf,h2_mistaggen_sf)
  h2_mistag_sf_syst_gen.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"Systuncty_Gen"),"Mistag SF Unc (Gen), WP " +wp+ ", "+era)
  h2_mistag_sf_fracsyst_gen.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"FracSystuncty_Gen"),"Mistag SF Fractional Unc (Gen), WP " +wp+ ", "+era)

  #
  # SF Eff & SF Mistag (Uncertainty due JES)
  #
  print("Retrieving JES Uncertainty for SF Eff and Mistag for "+ wp +" WP and era " + era)
  h2_eff_sf_jesUp    = GetHistoFromFile(inDir_jesTotalUp, "%s%s_%s"%("h2_eff_sf",eraStr,wpStr))
  h2_eff_sf_jesDown  = GetHistoFromFile(inDir_jesTotalDown, "%s%s_%s"%("h2_eff_sf",eraStr,wpStr))

  h2_eff_sf_syst_jes, h2_eff_sf_fracsyst_jes = MakeMapSystTwoSided(h2_eff_sf,h2_eff_sf_jesUp,h2_eff_sf_jesDown)
  h2_eff_sf_syst_jes.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"Systuncty_JES"),"Efficiency SF Unc (JES), WP " +wp+ ", "+era)
  h2_eff_sf_fracsyst_jes.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"FracSystuncty_JES"),"Efficiency SF Fractional Unc (JES), WP " +wp+ ", "+era)

  h2_mistag_sf_jesUp    = GetHistoFromFile(inDir_jesTotalUp, "%s%s_%s"%("h2_mistag_sf",eraStr,wpStr))
  h2_mistag_sf_jesDown  = GetHistoFromFile(inDir_jesTotalDown, "%s%s_%s"%("h2_mistag_sf",eraStr,wpStr))

  h2_mistag_sf_syst_jes, h2_mistag_sf_fracsyst_jes = MakeMapSystTwoSided(h2_mistag_sf,h2_mistag_sf_jesUp,h2_mistag_sf_jesDown)
  h2_mistag_sf_syst_jes.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"Systuncty_JES"),"Mistag SF Unc (JES), WP " +wp+ ", "+era)
  h2_mistag_sf_fracsyst_jes.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"FracSystuncty_JES"),"Mistag SF Fractional Unc (JES), WP " +wp+ ", "+era)

  #
  # Calculate total uncertainty for sf efficiency and sf mistag
  #
  hSystList = [
    h2_eff_sf_syst_fit,
    h2_eff_sf_syst_gen,
    h2_eff_sf_syst_jes,
  ]
  h2_eff_sf_syst_total, h2_eff_sf_fracsyst_total =  MakeMapSystTotal(h2_eff_sf,hSystList)
  h2_eff_sf_syst_total.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"Systuncty"),"Efficiency SF Unc (Total), WP " +wp+ ", "+era)
  h2_eff_sf_fracsyst_total.SetNameTitle("%s%s_%s_%s"%("h2_eff_sf",eraStr,wpStr,"FracSystuncty"),"Efficiency SF Fractional Unc (Total), WP " +wp+ ", "+era)

  hSystList = [
    h2_mistag_sf_syst_fit,
    h2_mistag_sf_syst_gen,
    h2_mistag_sf_syst_jes,
  ]
  h2_mistag_sf_syst_total, h2_mistag_sf_fracsyst_total =  MakeMapSystTotal(h2_mistag_sf,hSystList)
  h2_mistag_sf_syst_total.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"Systuncty"),"Mistag SF Unc (Total), WP " +wp+ ", "+era)
  h2_mistag_sf_fracsyst_total.SetNameTitle("%s%s_%s_%s"%("h2_mistag_sf",eraStr,wpStr,"FracSystuncty"),"Mistag SF Fractional Unc (Total), WP " +wp+ ", "+era)

  h2List = [
    h2_eff_mc,
    h2_mistag_mc,
    h2_eff_sf,
    h2_mistag_sf,
    h2_eff_sf_syst_fit,
    h2_eff_sf_fracsyst_fit,
    h2_mistag_sf_syst_fit,
    h2_mistag_sf_fracsyst_fit,
    h2_eff_sf_syst_gen,
    h2_eff_sf_fracsyst_gen,
    h2_mistag_sf_syst_gen,
    h2_mistag_sf_fracsyst_gen,
    h2_eff_sf_syst_jes,
    h2_eff_sf_fracsyst_jes,
    h2_mistag_sf_syst_jes,
    h2_mistag_sf_fracsyst_jes,
    h2_eff_sf_syst_total,
    h2_eff_sf_fracsyst_total,
    h2_mistag_sf_syst_total,
    h2_mistag_sf_fracsyst_total
  ]
  return h2List

if __name__ == '__main__':
  main()
