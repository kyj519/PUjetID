import math
import ROOT 
import collections
import array
import math

def PlotDataMC(canvName, mcStack, dataHist, mcTotal,mcTotal_syst, leg, xaxistitle, yaxistitle, year, lumi, doLogy, pdfName, extratxt = ''):
  #
  # Make TCanvas
  #
  canv = ROOT.TCanvas(canvName,"canv", 800, 800)
  canv.SetFillStyle( 4000 )
  ROOT.SetOwnership(canv,False)
  #
  # Make upper TPad
  #
  the_low_margin = 0.3
  pad1 = ROOT.TPad(canvName+"_pad1","pad1",0.0, the_low_margin, 1.0, 1.0)
  pad1.SetTopMargin( 0.06 )
  pad1.SetBottomMargin( 0.0 )
  pad1.SetFillStyle( 4000 )
  pad1.SetFillColor( 0 )
  pad1.SetFrameFillStyle( 4000 )
  pad1.SetFrameFillColor( 0 )
  pad1.Draw()
  #
  # Make lower TPad
  #
  pad2 = ROOT.TPad(canvName+"_pad2","pad2",0.0, 0.0, 1.0, the_low_margin)
  pad2.SetTopMargin( 0.05 )
  pad2.SetBottomMargin( 0.325 )
  pad2.SetFillStyle( 4000 )
  pad2.SetFillColor( 0 )
  pad2.SetFrameFillStyle( 4000 )
  pad2.SetFrameFillColor( 0 )
  pad2.Draw()

  #
  # TLatex for texts
  #
  latex = ROOT.TLatex()
  latex.SetNDC()
  latex.SetTextFont( 42 )
  latex.SetTextSize( 0.035 )
  latex.SetTextColor( 1 )
  latex.SetTextAlign( 12 )
  
  Internal = "#bf{CMS} Work In Progress"
  Lumi = '%s fb^{-1}' %lumi
  extratext = extratxt
  
  latex.DrawLatex(0.15, 0.92, Internal );
  latex.SetTextSize( 0.03 );
  if "early" in year or "late" in year:
    latex.DrawLatex(0.57, 0.98, Lumi+' ('+year+' 13 TeV)');
  else:
    latex.DrawLatex(0.64, 0.98, Lumi+' ('+year+' 13 TeV)');
  latex.DrawLatex(0.15,0.88,extratext)
  latex.SetTextSize( 0.028 );
  
  
  
  

  #
  # Draw histogram in 1st pad
  #
  pad1.cd()
  pad1.SetBottomMargin(0.00)
  #
  # backgrounds
  #
  mcStack.Draw("hist")
  mcStack.GetXaxis().SetTitle(xaxistitle)
  mcStack.GetYaxis().SetTitle(yaxistitle)
  #
  # Draw Error band of total bkgd
  #
  systematics = mcTotal_syst 
  Syst = GetSystematicUncertaintyBand(mcTotal,systematics)
  Syst.SetFillColor( ROOT.kBlack )
  Syst.SetFillStyle( 3001 )
  Syst.SetLineColor( ROOT.kWhite )
  Syst.SetMarkerStyle( 1 )
  Syst.Draw( 'E2same' )
  #
  # data
  #
  SetDataStyle( dataHist )
  dataHist.Draw("PEX0same")
  #
  # Adjust min and max
  #
  maximum = None 
  maximum = max(mcStack.GetMaximum(),dataHist.GetMaximum())
  mcStack.SetMaximum(maximum * 1.50)
  mcStack.SetMinimum(0.01)
  pad1.Update()
  
  #
  # Add uncertainties legend
  #
  if(len(systematics) == 0):
    leg.AddEntry( Syst, 'Stat Unc.', 'F' )
  else:
    leg.AddEntry( Syst, 'Stat+Syst Unc.', 'F' )
  #
  # legend
  #
  leg.Draw("same")
  if doLogy: 
    pad1.SetLogy()
    mcStack.SetMaximum(maximum * 100)
    mcStack.SetMinimum(0.1)
    pad1.Update()
  #
  # Go to 2nd pad 
  #
  pad2.cd()
  pad2.SetGridy()
  Ratio, SystBand = GetRatioHistogram( dataHist, mcTotal, Syst )
  SetDataStyle( Ratio )
  Ratio.GetXaxis().SetTitle(mcStack.GetXaxis().GetTitle())
  #
  # Draw ratio plot
  #
  Ratio.Draw()
  #
  # Draw systematics band
  #
  SystBand.SetFillColor( ROOT.kBlack )
  SystBand.SetFillStyle( 3001 )
  SystBand.SetLineColor( ROOT.kWhite )
  SystBand.SetMarkerStyle( 1 )
  SystBand.Draw( 'E2same' )

  pad2.Update()
  #
  # Draw line (#TEMP)
  #
  line = ROOT.TLine( pad2.GetUxmin(), 1, pad2.GetUxmax(), 1 )
  line.SetLineColor( ROOT.kRed + 1 )
  line.SetLineWidth( 4 )
  line.Draw()
  #
  # Draw ratio again
  #
  Ratio.Draw( 'same' )      
  canv.Print( pdfName + ".eps")
  canv.Print( pdfName + ".pdf")

  mcStack.GetHists().Delete()
  del mcStack
  del dataHist
  del mcTotal
  del canv
  
def GetSystematicUncertaintyBand(nom,systematics):
  
  from ROOT import TGraphAsymmErrors
  from math import sqrt,pow
  # 
  # This is the quadrature sum of all the systematics this sample knows about.
  # 
  n_bins_combined = nom.GetNbinsX()
  x=[]; ex_up=[]; ex_down=[]
  y=[]; ey_up=[]; ey_down=[]

  for i in xrange(1, n_bins_combined+1, 1):
    
    up = 0.0
    down = 0.0
    
    x.append(nom.GetBinCenter(i))
    bin_width = nom.GetBinWidth(i)

    ex_down.append(bin_width/2.)
    ex_up.append(bin_width/2.)
    y.append(nom.GetBinContent(i))
    
    for sysHist in systematics:
      # print sysHist.GetName()
      n_bins = sysHist.GetNbinsX()
      if not n_bins == n_bins_combined:
        raise RuntimeError('Number of bins in histograms does not agree between systematics.')
      nominal = nom.GetBinContent(i)
      this_syst = sysHist.GetBinContent(i)
      up,down = addInQuadrature(this_syst, nominal, up, down)

    up,down = addInStatBin(i,nom,up,down)

    if up > 0: 
      ey_up.append(sqrt(up))
    else: 
      ey_up.append(0)
    if down > 0: 
      ey_down.append(sqrt(down))
    else: 
      ey_down.append(0)
    
  x = array.array('d',x)
  y = array.array('d',y)
  ex_up   = array.array('d',ex_up)
  ex_down = array.array('d',ex_down)
  ey_up   = array.array('d',ey_up)
  ey_down = array.array('d',ey_down)
  
  ratio = TGraphAsymmErrors(n_bins_combined, x, y, ex_down, ex_up, ey_down, ey_up)
  
  return ratio

def GetRatioHistogram( Data, MonteCarlo, Syst ):
  
  Result = Data.Clone( 'RatioHistogramFor' + Data.GetName() )
  SystBand = Syst.Clone( 'RatioHistogramFor' + MonteCarlo.GetName())
  SystBandFinal = Syst.Clone( 'FinalRatioHistogramFor' + MonteCarlo.GetName())
  
  AverageRatio = 0
  NumberOfPoints = 0

  for i in range(0, Result.GetNbinsX()):
    bin = i + 1
    
    x = SystBand.GetX()[i]
    y = SystBand.GetY()[i]
    
    xtemp = SystBandFinal.GetX()[i]
    ytemp = SystBandFinal.GetY()[i]
    
    x_err_up   = SystBand.GetEXhigh()[i]
    x_err_down = SystBand.GetEXlow()[i]
    y_err_up   = SystBand.GetEYhigh()[i]
    y_err_down = SystBand.GetEYlow()[i]
    
    SystBandFinal.SetPoint(i, x, 1.)
    if y > 0:
      SystBandFinal.SetPointEYhigh(i, y_err_up / y)
      SystBandFinal.SetPointEYlow(i, y_err_down / y)
    else:
      SystBandFinal.SetPointEYhigh(i, 0)
      SystBandFinal.SetPointEYlow(i, 0)
    
    SystBandFinal.SetPointEXhigh(i, x_err_up )
    SystBandFinal.SetPointEXlow(i, x_err_down )
    
    if MonteCarlo.GetBinContent( bin ) > 0:
      Result.SetBinContent( bin, Data.GetBinContent( bin ) / MonteCarlo.GetBinContent( bin ) )
      Result.SetBinError( bin, math.sqrt( math.pow( Data.GetBinError( bin ) / MonteCarlo.GetBinContent( bin ), 2 ) + math.pow( Data.GetBinContent( bin ) * MonteCarlo.GetBinError( bin ) / math.pow( MonteCarlo.GetBinContent( bin ), 2 ), 2 ) ) )
      AverageRatio += Data.GetBinContent( bin ) / MonteCarlo.GetBinContent( bin )
      NumberOfPoints += 1.
    
  Result.SetLineStyle( 1 )
  Result.SetLineColor( ROOT.kBlack )
  Result.SetMarkerSize( 0.8 )
  Result.GetYaxis().SetNdivisions( 5, 3, 0 )
  Result.SetMaximum( 1.50 )
  Result.SetMinimum( 0.50 )
  #Result.GetYaxis().SetTitle( '#frac{Data}{Pred}' )
  Result.GetYaxis().SetTitle( 'Data/Pred.' )
  Result.GetYaxis().CenterTitle( True )
  
  return (Result,SystBandFinal)

def SetDataStyle( h ):

  x = h.GetXaxis()
  x.SetLabelFont( 43 )
  x.SetTitleFont( 43 )
  x.SetLabelSize( 20 )
  x.SetTitleSize( 22 )
  
  y = h.GetYaxis()
  y.SetLabelFont( 43 )
  y.SetTitleFont( 43 )
  y.SetLabelSize( 20 )
  y.SetTitleSize( 22 )
  
  h.SetMarkerStyle( 20 )
  h.SetMarkerSize( 0.8 )
  h.SetLineColor( 1 )
  
  h.SetTitleOffset( 1.9, 'Y' )
  h.SetTitleOffset( 3.3, 'X' )

def addQuad(sys, nom):
  from math import sqrt,pow
  
  sys_diff = sys - nom
  sys_diff += pow(sys_diff,2)
  
  return sys_diff

def addInQuadrature(sys, nom, up, down):
  from math import sqrt,pow
  
  sys_diff = sys - nom
  
  if sys_diff > 0:
    up += pow(sys_diff,2)
  elif sys_diff < 0:
    down += pow(sys_diff,2)
    
  return (up,down)

def addInStat(nom, up, down):
  from math import sqrt,pow
  
  mcstat = nom.GetBinError(1)
  
  up += pow(mcstat,2)
  down += pow(mcstat,2)
  
  return (up,down)

def addInStatBin(i,nom, up, down):
  from math import sqrt,pow
  
  mcstat = nom.GetBinError(i)
  up += pow(mcstat,2)
  down += pow(mcstat,2)
  
  return (up,down)

def show_overflow(hist):
  #
  # Show overflow and underflow on a TH1
  #
  nbins          = hist.GetNbinsX()
  underflow      = hist.GetBinContent(   0   )
  underflowerror = hist.GetBinError  (   0   )
  overflow       = hist.GetBinContent(nbins+1)
  overflowerror  = hist.GetBinError  (nbins+1)
  firstbin       = hist.GetBinContent(   1   )
  firstbinerror  = hist.GetBinError  (   1   )
  lastbin        = hist.GetBinContent( nbins )
  lastbinerror   = hist.GetBinError  ( nbins )

  if underflow != 0 :
    newcontent = underflow + firstbin
    if firstbin == 0 :
        newerror = underflowerror
    else:
        newerror = math.sqrt( underflowerror * underflowerror + firstbinerror * firstbinerror )
    hist.SetBinContent(1, newcontent)
    hist.SetBinError  (1, newerror)

  if overflow != 0 :
    newcontent = overflow + lastbin
    if lastbin == 0 :
        newerror = overflowerror
    else:
        newerror = math.sqrt( overflowerror * overflowerror + lastbinerror * lastbinerror )
    hist.SetBinContent(nbins, newcontent)
    hist.SetBinError  (nbins, newerror) 