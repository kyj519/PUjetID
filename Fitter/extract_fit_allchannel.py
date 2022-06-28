# Standard importts
import os,sys,socket,argparse
import os
import ROOT
import math
import pprint
from array import array
import numpy as np
import collections

ROOT.gROOT.SetBatch(True)

# RooFit
ROOT.gSystem.Load("libRooFit.so")
ROOT.gSystem.Load("libRooFitCore.so")
ROOT.gROOT.SetStyle("Plain") # Not sure this is needed
ROOT.gSystem.SetIncludePath( "-I$ROOFITSYS/include/" )

'''
The general idea is to extract the efficiency and mistag rate of the PU ID based on a fit to the dphi(Z,jet) distribution. 
4 dphi(Z,jet) distributions are fitted simultaneously: 
-Passing or failing jets with good/bad  pt balance with the Z boson.

The fit uses up to 8 histograms (1 signal and 1 PU template per fitted distribution):
- h_dphi_genunmatched_PASS/FAIL: distribution for jets not matched to a gen jet and failing/passing the PU ID working point under study. At the moment these templates are not used and replaced by a flat distribution.
- h_dphi_genmatched_PASS/FAIL: Same for jets matched to a gen jet 
- Same plots with the suffix "badbalance": similar templates, obtained using Z+jets events where the pt(Z)/pt(j) balance is bad. 
'''

# ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)

printPNG=False

def getNormalizeHist(hist_orig):
    hist = hist_orig.Clone()
    nbin = hist.GetNbinsX()
    for i in range(1,nbin+1):
        content_orig=hist.GetBinContent(i)
        bin_width = hist.GetBinWidth(i)
        hist.SetBinContent(i,bin_width*content_orig)
        
    return hist
        
def MakeDPhiFit(
    h_dphi_genunmatched_PASS_Mu,h_dphi_genmatched_PASS_Mu,h_dphi_genunmatched_FAIL_Mu,h_dphi_genmatched_FAIL_Mu,
    h_dphi_PASS_Mu,h_dphi_FAIL_Mu, 
    h_dphi_genunmatched_PASS_badbalance_Mu,h_dphi_genmatched_PASS_badbalance_Mu,h_dphi_genunmatched_FAIL_badbalance_Mu,h_dphi_genmatched_FAIL_badbalance_Mu,
    h_dphi_PASS_badbalance_Mu,h_dphi_FAIL_badbalance_Mu,
    h_dphi_genunmatched_PASS_El,h_dphi_genmatched_PASS_El,h_dphi_genunmatched_FAIL_El,h_dphi_genmatched_FAIL_El,
    h_dphi_PASS_El,h_dphi_FAIL_El, 
    h_dphi_genunmatched_PASS_badbalance_El,h_dphi_genmatched_PASS_badbalance_El,h_dphi_genunmatched_FAIL_badbalance_El,h_dphi_genmatched_FAIL_badbalance_El,
    h_dphi_PASS_badbalance_El,h_dphi_FAIL_badbalance_El,  
    outputDir, pt, eta, cfitPASS_Mu, cfitFAIL_Mu, cfitPASS_badbalance_Mu,cfitFAIL_badbalance_Mu, cfitPASS_El, cfitFAIL_El, cfitPASS_badbalance_El, cfitFAIL_badbalance_El, 
    iBinCount, iBinTotal,
    isData=False, doEtaBins=False):
    print("------------------------------------------------------------------")
    if isData:
        print("Performing fits to extract efficiency and mistag rate in DATA") 
    else:
        print("Performing fits to extract efficiency and mistag rate in MC") 
    print("ptBin:"+ pt + ", etaBin:"+eta) 
    print("------------------------------------------------------------------")
    print("entries in PASS histos, Mu ch "+str(h_dphi_genunmatched_PASS_Mu.GetEntries())+","+str(h_dphi_genmatched_PASS_Mu.GetEntries())+","+str(h_dphi_PASS_Mu.GetEntries())+","+str(h_dphi_PASS_badbalance_Mu.GetEntries()))
    print("entries in FAIL histos, Mu ch "+str(h_dphi_genunmatched_FAIL_Mu.GetEntries())+","+str(h_dphi_genmatched_FAIL_Mu.GetEntries())+","+str(h_dphi_FAIL_Mu.GetEntries())+","+str(h_dphi_FAIL_badbalance_Mu.GetEntries()))
    print("entries in PASS histos, El ch "+str(h_dphi_genunmatched_PASS_El.GetEntries())+","+str(h_dphi_genmatched_PASS_El.GetEntries())+","+str(h_dphi_PASS_El.GetEntries())+","+str(h_dphi_PASS_badbalance_El.GetEntries()))
    print("entries in FAIL histos, El ch "+str(h_dphi_genunmatched_FAIL_El.GetEntries())+","+str(h_dphi_genmatched_FAIL_El.GetEntries())+","+str(h_dphi_FAIL_El.GetEntries())+","+str(h_dphi_FAIL_badbalance_El.GetEntries()))
    
    #
    # Calculate MC efficiency using gen-level information
    #
    eff_gen    = -1.0
    mistag_gen = -1.0
    if isData == False:
        n_mc_real_pass = h_dphi_genmatched_PASS_Mu.Integral() + h_dphi_genmatched_PASS_badbalance_Mu.Integral() + h_dphi_genmatched_PASS_El.Integral() + h_dphi_genmatched_PASS_badbalance_El.Integral()
        n_mc_real_fail = h_dphi_genmatched_FAIL_Mu.Integral() + h_dphi_genmatched_FAIL_badbalance_Mu.Integral() + h_dphi_genmatched_FAIL_El.Integral() + h_dphi_genmatched_FAIL_badbalance_El.Integral()
        n_mc_pu_pass   = h_dphi_genunmatched_PASS_Mu.Integral() + h_dphi_genunmatched_PASS_badbalance_Mu.Integral() +  h_dphi_genunmatched_PASS_El.Integral() + h_dphi_genunmatched_PASS_badbalance_El.Integral()
        n_mc_pu_fail   = h_dphi_genunmatched_FAIL_Mu.Integral() + h_dphi_genunmatched_FAIL_badbalance_Mu.Integral() + h_dphi_genunmatched_FAIL_El.Integral() + h_dphi_genunmatched_FAIL_badbalance_El.Integral()
        eff_gen    = n_mc_real_pass/(n_mc_real_pass+n_mc_real_fail)
        mistag_gen = n_mc_pu_pass/(n_mc_pu_pass+n_mc_pu_fail)
 

    #
    # Declare the observable
    #
    dphiZjet = ROOT.RooRealVar("dphiZjet","#Delta#phi(Z,jet)/#pi",0., 2.)
    #
    # Declare effcy and mistag
    #
    # iBinCount 39~44 -> 40<P_T<50, -2.5<eta<2.5
    effcy    = ROOT.RooRealVar("effcy","effcy",  0.9, 0.,1.)
    mistag   = ROOT.RooRealVar("mistag","mistag",0.1 ,0.,1.) 
    if not isData:
        mistag   = ROOT.RooRealVar("mistag","mistag",mistag_gen,0.,1.)
        effcy    = ROOT.RooRealVar("effcy","effcy",  eff_gen, 0.,1.)   
    #if iBinCount >= 39 and iBinCount <= 44: mistag   =  ROOT.RooRealVar("mistag","mistag",mistag_gen,bound_0p90 ,bound_1p10) 
    #if isData: mistag   = ROOT.RooRealVar("mistag","mistag",0.1 ,0.,1.) 
    ################# What follows concerns the first 4 templates (GOOD jet/Z pt balance) #################
    #
    # Total number of events of signal (=real jets) events and of PU (=pileup jets) events before applying PU ID
    #
    nbtot_Mu    = ROOT.RooRealVar("nbtot_Mu","nbtot_Mu",h_dphi_PASS_Mu.Integral() + h_dphi_FAIL_Mu.Integral())
    nbtotsig_Mu = ROOT.RooRealVar("nbtotsig_Mu","nbtotsig_Mu", 1.,h_dphi_PASS_Mu.Integral() + h_dphi_FAIL_Mu.Integral())
    nbtotpu_Mu  = ROOT.RooFormulaVar("nbtotpu_Mu","nbtot_Mu-nbtotsig_Mu",ROOT.RooArgList(nbtot_Mu,nbtotsig_Mu)) 

    nbtot_El   = ROOT.RooRealVar("nbtot_El","nbtot_El",h_dphi_PASS_El.Integral() + h_dphi_FAIL_El.Integral())
    nbtotsig_El = ROOT.RooRealVar("nbtotsig_El","nbtotsig_El", 1., h_dphi_PASS_El.Integral() + h_dphi_FAIL_El.Integral())
    nbtotpu_El  = ROOT.RooFormulaVar("nbtotpu_El","nbtot_El-nbtotsig_El",ROOT.RooArgList(nbtot_El,nbtotsig_El)) 
    #
    # Number of events from each category passing/failing the PU ID 
    #
    n_SIG_PASS_Mu = ROOT.RooFormulaVar("n_SIG_PASS_Mu","effcy*nbtotsig_Mu",     ROOT.RooArgList(effcy,nbtotsig_Mu))
    n_PU_PASS_Mu  = ROOT.RooFormulaVar("n_PU_PASS_Mu", "mistag*nbtotpu_Mu",     ROOT.RooArgList(mistag,nbtotpu_Mu))
    n_SIG_FAIL_Mu = ROOT.RooFormulaVar("n_SIG_FAIL_Mu","(1-effcy)*nbtotsig_Mu", ROOT.RooArgList(effcy,nbtotsig_Mu))
    n_PU_FAIL_Mu  = ROOT.RooFormulaVar("n_PU_FAIL_Mu", "(1-mistag)*nbtotpu_Mu", ROOT.RooArgList(mistag,nbtotpu_Mu))

    n_SIG_PASS_El = ROOT.RooFormulaVar("n_SIG_PASS_El","effcy*nbtotsig_El",     ROOT.RooArgList(effcy,nbtotsig_El))
    n_PU_PASS_El  = ROOT.RooFormulaVar("n_PU_PASS_El", "mistag*nbtotpu_El",     ROOT.RooArgList(mistag,nbtotpu_El))
    n_SIG_FAIL_El = ROOT.RooFormulaVar("n_SIG_FAIL_El","(1-effcy)*nbtotsig_El", ROOT.RooArgList(effcy,nbtotsig_El))
    n_PU_FAIL_El  = ROOT.RooFormulaVar("n_PU_FAIL_El", "(1-mistag)*nbtotpu_El", ROOT.RooArgList(mistag,nbtotpu_El))
    #
    # Import the data histograms
    #
    dh_dphiZjet_PASS_Mu = ROOT.RooDataHist("dh_dphiZjet_PASS_Mu", "dh_dphiZjet_PASS_Mu", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_PASS_Mu))
    dh_dphiZjet_FAIL_Mu = ROOT.RooDataHist("dh_dphiZjet_FAIL_Mu", "dh_dphiZjet_FAIL_Mu", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_FAIL_Mu))
    dh_dphiZjet_PASS_El = ROOT.RooDataHist("dh_dphiZjet_PASS_El", "dh_dphiZjet_PASS_El", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_PASS_El))
    dh_dphiZjet_FAIL_El = ROOT.RooDataHist("dh_dphiZjet_FAIL_El", "dh_dphiZjet_FAIL_El", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_FAIL_El))
    #
    # Define the pdf: 
    # First import the histos templates
    #
    dh_template_SIG_PASS_Mu = ROOT.RooDataHist("dh_template_SIG_PASS_Mu", "dh_template_SIG_PASS_Mu", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_PASS_Mu))
    dh_template_SIG_FAIL_Mu = ROOT.RooDataHist("dh_template_SIG_FAIL_Mu", "dh_template_SIG_FAIL_Mu", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_FAIL_Mu))
    dh_template_PU_PASS_Mu  = ROOT.RooDataHist("dh_template_PU_PASS_Mu",  "dh_template_PU_PASS_Mu",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_PASS_Mu))
    dh_template_PU_FAIL_Mu  = ROOT.RooDataHist("dh_template_PU_FAIL_Mu",  "dh_template_PU_FAIL_Mu",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_FAIL_Mu))

    dh_template_SIG_PASS_El = ROOT.RooDataHist("dh_template_SIG_PASS_El", "dh_template_SIG_PASS_El", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_PASS_El))
    dh_template_SIG_FAIL_El = ROOT.RooDataHist("dh_template_SIG_FAIL_El", "dh_template_SIG_FAIL_El", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_FAIL_El))
    dh_template_PU_PASS_El  = ROOT.RooDataHist("dh_template_PU_PASS_El",  "dh_template_PU_PASS_El",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_PASS_El))
    dh_template_PU_FAIL_El  = ROOT.RooDataHist("dh_template_PU_FAIL_El",  "dh_template_PU_FAIL_El",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_FAIL_El))
    #
    # Now convert them to PDF:
    #
    pdf_template_SIG_PASS_Mu = ROOT.RooHistPdf("pdf_template_SIG_PASS_Mu", "pdf_template_SIG_PASS_Mu", ROOT.RooArgSet(dphiZjet), dh_template_SIG_PASS_Mu,1)
    pdf_template_SIG_FAIL_Mu = ROOT.RooHistPdf("pdf_template_SIG_FAIL_Mu", "pdf_template_SIG_FAIL_Mu", ROOT.RooArgSet(dphiZjet), dh_template_SIG_FAIL_Mu,1)
    pdf_template_PU_PASS_Mu  = ROOT.RooHistPdf("pdf_template_PU_PASS_Mu",  "pdf_template_PU_PASS_Mu",  ROOT.RooArgSet(dphiZjet), dh_template_PU_PASS_Mu,1)
    pdf_template_PU_FAIL_Mu  = ROOT.RooHistPdf("pdf_template_PU_FAIL_Mu",  "pdf_template_PU_FAIL_Mu",  ROOT.RooArgSet(dphiZjet), dh_template_PU_FAIL_Mu,1)

    pdf_template_SIG_PASS_El = ROOT.RooHistPdf("pdf_template_SIG_PASS_El", "pdf_template_SIG_PASS_El", ROOT.RooArgSet(dphiZjet), dh_template_SIG_PASS_El,1)
    pdf_template_SIG_FAIL_El = ROOT.RooHistPdf("pdf_template_SIG_FAIL_El", "pdf_template_SIG_FAIL_El", ROOT.RooArgSet(dphiZjet), dh_template_SIG_FAIL_El,1)
    pdf_template_PU_PASS_El  = ROOT.RooHistPdf("pdf_template_PU_PASS_El",  "pdf_template_PU_PASS_El",  ROOT.RooArgSet(dphiZjet), dh_template_PU_PASS_El,1)
    pdf_template_PU_FAIL_El  = ROOT.RooHistPdf("pdf_template_PU_FAIL_El",  "pdf_template_PU_FAIL_El",  ROOT.RooArgSet(dphiZjet), dh_template_PU_FAIL_El,1)
    #
    # The PU template is taken to be a flat (pol0) distribution
    #
    pol0_PU_PASS_Mu = ROOT.RooPolynomial("pol0_PU_PASS_Mu","pol0",dphiZjet, ROOT.RooArgList())
    pol0_PU_FAIL_Mu = ROOT.RooPolynomial("pol0_PU_FAIL_Mu","pol0",dphiZjet, ROOT.RooArgList())

    pol0_PU_PASS_El = ROOT.RooPolynomial("pol0_PU_PASS_El","pol0",dphiZjet, ROOT.RooArgList())
    pol0_PU_FAIL_El = ROOT.RooPolynomial("pol0_PU_FAIL_El","pol0",dphiZjet, ROOT.RooArgList())
    #
    # Smears the SIGNAL template with a Gaussian to allow for different phi resolution between data and simulation. 
    #
    # PASS
    gauss_mean_PASS_Mu  = ROOT.RooRealVar("mean_PASS_Mu","mean",0,-0.05,0.05)
    gauss_sigma_PASS_Mu = ROOT.RooRealVar("sigma_PASS_Mu","sigma gauss",0.03,0.015,0.12)
    gauss_PASS_Mu       = ROOT.RooGaussian("gauss_PASS_Mu","gauss", dphiZjet ,gauss_mean_PASS_Mu,gauss_sigma_PASS_Mu) 
    tmpxg_SIG_PASS_Mu   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS_Mu","template x gauss" ,dphiZjet, pdf_template_SIG_PASS_Mu , gauss_PASS_Mu)

    gauss_mean_PASS_El  = ROOT.RooRealVar("mean_PASS_El","mean",0,-0.05,0.05)
    gauss_sigma_PASS_El = ROOT.RooRealVar("sigma_PASS_El","sigma gauss",0.03,0.015,0.12)
    gauss_PASS_El       = ROOT.RooGaussian("gauss_PASS_El","gauss", dphiZjet ,gauss_mean_PASS_El,gauss_sigma_PASS_El) 
    tmpxg_SIG_PASS_El   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS_El","template x gauss" ,dphiZjet, pdf_template_SIG_PASS_El , gauss_PASS_El)
    # FAIL
    gauss_mean_FAIL_Mu  = ROOT.RooRealVar("mean_FAIL_Mu","mean",0,-0.05,0.05)
    gauss_sigma_FAIL_Mu = ROOT.RooRealVar("sigma_FAIL_Mu","sigma gauss",0.03,0.015,0.12)
    gauss_FAIL_Mu       = ROOT.RooGaussian("gauss_FAIL_Mu","gauss", dphiZjet ,gauss_mean_FAIL_Mu,gauss_sigma_FAIL_Mu) 
    tmpxg_SIG_FAIL_Mu   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL_Mu","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL_Mu , gauss_FAIL_Mu)


    gauss_mean_FAIL_El  = ROOT.RooRealVar("mean_FAIL_El","mean",0,-0.05,0.05)
    gauss_sigma_FAIL_El = ROOT.RooRealVar("sigma_FAIL_El","sigma gauss",0.03,0.015,0.12)
    gauss_FAIL_El       = ROOT.RooGaussian("gauss_FAIL_El","gauss", dphiZjet ,gauss_mean_FAIL_El,gauss_sigma_FAIL_El) 
    tmpxg_SIG_FAIL_El   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL_El","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL_El , gauss_FAIL_El)
    #
    # Smears the PU template template with a Gaussian to allow for different phi resolution between data and simulation.  
    # Not needed if the template is a flat distribution.  
    #
    # PASS
    # gauss_mean_PU_PASS  = ROOT.RooRealVar("mean_PU_PASS","mean",0,-0.05,0.05)
    # gauss_sigma_PU_PASS = ROOT.RooRealVar("sigma_PU_PASS","sigma gauss",0.03,0.015,0.12)
    # gauss_PU_PASS       = ROOT.RooGaussian("gauss_PU_PASS","gauss", dphiZjet ,gauss_mean_PU_PASS,gauss_sigma_PU_PASS) 
    # tmpxg_PU_PASS       = ROOT.RooFFTConvPdf("tmpxg_PU_PASS","template x gauss" ,dphiZjet, pdf_template_PU_PASS , gauss_PU_PASS)
    # # FAIL
    # gauss_mean_PU_FAIL  = ROOT.RooRealVar("mean_PU_FAIL","mean",0,-0.05,0.05)
    # gauss_sigma_PU_FAIL = ROOT.RooRealVar("sigma_PU_FAIL","sigma gauss",0.03,0.015,0.12)
    # gauss_PU_FAIL       = ROOT.RooGaussian("gauss_PU_FAIL","gauss", dphiZjet ,gauss_mean_PU_FAIL,gauss_sigma_PU_FAIL) 
    # tmpxg_PU_FAIL       = ROOT.RooFFTConvPdf("tmpxg_PU_FAIL","template x gauss" ,dphiZjet, pdf_template_PU_FAIL , gauss_PU_FAIL)
    #
    # Convert to extended pdf 
    #
    extpdf_SIG_PASS_Mu = ROOT.RooExtendPdf("extpdf_SIG_PASS_Mu", "extpdf_SIG_PASS_Mu", tmpxg_SIG_PASS_Mu, n_SIG_PASS_Mu) 
    extpdf_SIG_FAIL_Mu = ROOT.RooExtendPdf("extpdf_SIG_FAIL_Mu", "extpdf_SIG_FAIL_Mu", tmpxg_SIG_FAIL_Mu, n_SIG_FAIL_Mu) 
    extpdf_PU_PASS_Mu  = ROOT.RooExtendPdf("extpdf_PU_PASS_Mu", "extpdf_PU_PASS_Mu",   pol0_PU_PASS_Mu,   n_PU_PASS_Mu)
    extpdf_PU_FAIL_Mu  = ROOT.RooExtendPdf("extpdf_PU_FAIL_Mu", "extpdf_PU_FAIL_Mu",  pol0_PU_FAIL_Mu,   n_PU_FAIL_Mu)

    extpdf_SIG_PASS_El = ROOT.RooExtendPdf("extpdf_SIG_PASS_El", "extpdf_SIG_PASS_El", tmpxg_SIG_PASS_El, n_SIG_PASS_El) 
    extpdf_SIG_FAIL_El = ROOT.RooExtendPdf("extpdf_SIG_FAIL_El", "extpdf_SIG_FAIL_El", tmpxg_SIG_FAIL_El, n_SIG_FAIL_El) 
    extpdf_PU_PASS_El  = ROOT.RooExtendPdf("extpdf_PU_PASS_El", "extpdf_PU_PASS_El",   pol0_PU_PASS_El,   n_PU_PASS_El)
    extpdf_PU_FAIL_El  = ROOT.RooExtendPdf("extpdf_PU_FAIL_El", "extpdf_PU_FAIL_El",   pol0_PU_FAIL_El,   n_PU_FAIL_El)
    #
    # PU+SIG PDF
    #
    extpdf_SIGandPU_PASS_Mu = ROOT.RooAddPdf("extpdf_SIGandPU_PASS_Mu", "Signal+PU_Mu PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS_Mu,extpdf_PU_PASS_Mu),ROOT.RooArgList(n_SIG_PASS_Mu,n_PU_PASS_Mu))
    extpdf_SIGandPU_FAIL_Mu = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL_Mu", "Signal+PU_Mu PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL_Mu,extpdf_PU_FAIL_Mu),ROOT.RooArgList(n_SIG_FAIL_Mu,n_PU_FAIL_Mu))

    
    extpdf_SIGandPU_PASS_El = ROOT.RooAddPdf("extpdf_SIGandPU_PASS_El", "Signal+PU_El PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS_El,extpdf_PU_PASS_El),ROOT.RooArgList(n_SIG_PASS_El,n_PU_PASS_El))
    extpdf_SIGandPU_FAIL_El = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL_El", "Signal+PU_El PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL_El,extpdf_PU_FAIL_El),ROOT.RooArgList(n_SIG_FAIL_El,n_PU_FAIL_El))

    ################# Same procedure for templates with BAD jet/Z pt balance ################# 
    #
    # Total number of events of signal (=real jets) events and of PU (=pileup jets) events before applying PU ID      
    #
    nbtot_badbalance_Mu    =  ROOT.RooRealVar("nbtot_badbalance_Mu","nbtot_badbalance_Mu",h_dphi_PASS_badbalance_Mu.Integral() + h_dphi_FAIL_badbalance_Mu.Integral())
    nbtotsig_badbalance_Mu =  ROOT.RooRealVar("nbtotsig_badbalance_Mu","nbtotsig_badbalance_Mu", 1., h_dphi_PASS_badbalance_Mu.Integral() + h_dphi_FAIL_badbalance_Mu.Integral())
    nbtotpu_badbalance_Mu  =  ROOT.RooFormulaVar("nbtotpu_badbalance_Mu","nbtot_badbalance_Mu-nbtotsig_badbalance_Mu",ROOT.RooArgList(nbtot_badbalance_Mu,nbtotsig_badbalance_Mu))

    nbtot_badbalance_El    =  ROOT.RooRealVar("nbtot_badbalance_El","nbtot_badbalance_El",h_dphi_PASS_badbalance_El.Integral() + h_dphi_FAIL_badbalance_El.Integral())
    nbtotsig_badbalance_El =  ROOT.RooRealVar("nbtotsig_badbalance_El","nbtotsig_badbalance_El", 1., h_dphi_PASS_badbalance_El.Integral() + h_dphi_FAIL_badbalance_El.Integral())
    nbtotpu_badbalance_El  =  ROOT.RooFormulaVar("nbtotpu_badbalance_El","nbtot_badbalance_El-nbtotsig_badbalance_El",ROOT.RooArgList(nbtot_badbalance_El,nbtotsig_badbalance_El))
    #
    # Number of events from each category passing/failing the PU ID
    #
    n_SIG_PASS_badbalance_Mu = ROOT.RooFormulaVar("n_SIG_PASS_badbalance_Mu","effcy*nbtotsig_badbalance_Mu",ROOT.RooArgList(effcy,nbtotsig_badbalance_Mu))
    n_PU_PASS_badbalance_Mu  = ROOT.RooFormulaVar("n_PU_PASS_badbalance_Mu","mistag*nbtotpu_badbalance_Mu",ROOT.RooArgList(mistag,nbtotpu_badbalance_Mu))
    n_SIG_FAIL_badbalance_Mu = ROOT.RooFormulaVar("n_SIG_FAIL_badbalance_Mu","(1-effcy)*nbtotsig_badbalance_Mu",ROOT.RooArgList(effcy,nbtotsig_badbalance_Mu))
    n_PU_FAIL_badbalance_Mu  = ROOT.RooFormulaVar("n_PU_FAIL_badbalance_Mu","(1-mistag)*nbtotpu_badbalance_Mu",ROOT.RooArgList(mistag,nbtotpu_badbalance_Mu))

    n_SIG_PASS_badbalance_El = ROOT.RooFormulaVar("n_SIG_PASS_badbalance_El","effcy*nbtotsig_badbalance_El",ROOT.RooArgList(effcy,nbtotsig_badbalance_El))
    n_PU_PASS_badbalance_El  = ROOT.RooFormulaVar("n_PU_PASS_badbalance_El","mistag*nbtotpu_badbalance_El",ROOT.RooArgList(mistag,nbtotpu_badbalance_El))
    n_SIG_FAIL_badbalance_El = ROOT.RooFormulaVar("n_SIG_FAIL_badbalance_El","(1-effcy)*nbtotsig_badbalance_El",ROOT.RooArgList(effcy,nbtotsig_badbalance_El))
    n_PU_FAIL_badbalance_El  = ROOT.RooFormulaVar("n_PU_FAIL_badbalance_El","(1-mistag)*nbtotpu_badbalance_El",ROOT.RooArgList(mistag,nbtotpu_badbalance_El))
    #
    #Import the data histograms  
    #
    dh_dphiZjet_PASS_badbalance_Mu = ROOT.RooDataHist("dh_dphiZjet_PASS_badbalance_Mu"  ,"dh_dphiZjet_PASS_badbalance_Mu"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_PASS_badbalance_Mu))
    dh_dphiZjet_FAIL_badbalance_Mu = ROOT.RooDataHist("dh_dphiZjet_FAIL_badbalance_Mu"  ,"dh_dphiZjet_FAIL_badbalance_Mu"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_FAIL_badbalance_Mu))
    dh_dphiZjet_PASS_badbalance_El = ROOT.RooDataHist("dh_dphiZjet_PASS_badbalance_El"  ,"dh_dphiZjet_PASS_badbalance_El"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_PASS_badbalance_El))
    dh_dphiZjet_FAIL_badbalance_El = ROOT.RooDataHist("dh_dphiZjet_FAIL_badbalance_El"  ,"dh_dphiZjet_FAIL_badbalance_El"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_FAIL_badbalance_El))
    #
    # Define the pdf:                   
    # First import the histos templates
    #
    dh_template_SIG_PASS_badbalance_Mu = ROOT.RooDataHist("dh_template_SIG_PASS_badbalance_Mu",  "dh_template_SIG_PASS_badbalance_Mu" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_PASS_badbalance_Mu))
    dh_template_SIG_FAIL_badbalance_Mu  = ROOT.RooDataHist("dh_template_SIG_FAIL_badbalance_Mu",  "dh_template_SIG_FAIL_badbalance_Mu" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_FAIL_badbalance_Mu))
    dh_template_PU_PASS_badbalance_Mu  = ROOT.RooDataHist("dh_template_PU_PASS_badbalance_Mu",  "dh_template_PU_PASS_badbalance_Mu" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_PASS_badbalance_Mu))
    dh_template_PU_FAIL_badbalance_Mu  = ROOT.RooDataHist("dh_template_PU_FAIL_badbalance_Mu",  "dh_template_PU_FAIL_badbalance_Mu" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_FAIL_badbalance_Mu))

    dh_template_SIG_PASS_badbalance_El  = ROOT.RooDataHist("dh_template_SIG_PASS_badbalance_El",  "dh_template_SIG_PASS_badbalance_El" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_PASS_badbalance_El))
    dh_template_SIG_FAIL_badbalance_El  = ROOT.RooDataHist("dh_template_SIG_FAIL_badbalance_El",  "dh_template_SIG_FAIL_badbalance_El" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_FAIL_badbalance_El))
    dh_template_PU_PASS_badbalance_El  = ROOT.RooDataHist("dh_template_PU_PASS_badbalance_El",  "dh_template_PU_PASS_badbalance_El" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_PASS_badbalance_El))
    dh_template_PU_FAIL_badbalance_El  = ROOT.RooDataHist("dh_template_PU_FAIL_badbalance_El",  "dh_template_PU_FAIL_badbalance_El" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_FAIL_badbalance_El))
    #
    # Now convert them to PDF:
    #
    pdf_template_SIG_PASS_badbalance_Mu = ROOT.RooHistPdf("pdf_template_SIG_PASS_badbalance_Mu", "pdf_template_SIG_PASS_badbalance_Mu", ROOT.RooArgSet(dphiZjet),dh_template_SIG_PASS_badbalance_Mu,1)
    pdf_template_SIG_FAIL_badbalance_Mu = ROOT.RooHistPdf("pdf_template_SIG_FAIL_badbalance_Mu", "pdf_template_SIG_FAIL_badbalance_Mu", ROOT.RooArgSet(dphiZjet),dh_template_SIG_FAIL_badbalance_Mu,1)
    pdf_template_PU_PASS_badbalance_Mu  = ROOT.RooHistPdf("pdf_template_PU_PASS_badbalance_Mu", "pdf_template_PU_PASS_badbalance_Mu",  ROOT.RooArgSet(dphiZjet),dh_template_PU_PASS_badbalance_Mu,1)
    pdf_template_PU_FAIL_badbalance_Mu  = ROOT.RooHistPdf("pdf_template_PU_FAIL_badbalance_Mu", "pdf_template_PU_FAIL_badbalance_Mu",  ROOT.RooArgSet(dphiZjet),dh_template_PU_FAIL_badbalance_Mu,1)

    pdf_template_SIG_PASS_badbalance_El = ROOT.RooHistPdf("pdf_template_SIG_PASS_badbalance_El", "pdf_template_SIG_PASS_badbalance_El", ROOT.RooArgSet(dphiZjet),dh_template_SIG_PASS_badbalance_El,1)
    pdf_template_SIG_FAIL_badbalance_El = ROOT.RooHistPdf("pdf_template_SIG_FAIL_badbalance_El", "pdf_template_SIG_FAIL_badbalance_El", ROOT.RooArgSet(dphiZjet),dh_template_SIG_FAIL_badbalance_El,1)
    pdf_template_PU_PASS_badbalance_El  = ROOT.RooHistPdf("pdf_template_PU_PASS_badbalance_El", "pdf_template_PU_PASS_badbalance_El",  ROOT.RooArgSet(dphiZjet),dh_template_PU_PASS_badbalance_El,1)
    pdf_template_PU_FAIL_badbalance_El  = ROOT.RooHistPdf("pdf_template_PU_FAIL_badbalance_El", "pdf_template_PU_FAIL_badbalance_El",  ROOT.RooArgSet(dphiZjet),dh_template_PU_FAIL_badbalance_El,1)
    #
    #The PU template is taken to be a flat (pol0) distribution   
    #
    pol0_PU_PASS_badbalance_Mu = ROOT.RooPolynomial("pol0_PU_PASS_badbalance_Mu","pol0",dphiZjet, ROOT.RooArgList());
    pol0_PU_FAIL_badbalance_Mu = ROOT.RooPolynomial("pol0_PU_FAIL_badbalance_Mu","pol0",dphiZjet, ROOT.RooArgList());
    
    pol0_PU_PASS_badbalance_El = ROOT.RooPolynomial("pol0_PU_PASS_badbalance_El","pol0",dphiZjet, ROOT.RooArgList());
    pol0_PU_FAIL_badbalance_El = ROOT.RooPolynomial("pol0_PU_FAIL_badbalance_El","pol0",dphiZjet, ROOT.RooArgList());
    #
    # Smears the SIGNAL template with a Gaussian to allow for different phi resolution between data and simulation. 
    #
    # PASS
    gauss_mean_PASS_badbalance_Mu  = ROOT.RooRealVar("mean_PASS_badbalance_Mu","mean",0,-0.05,0.05)
    gauss_sigma_PASS_badbalance_Mu = ROOT.RooRealVar("sigma_PASS_badbalance_Mu","sigma gauss",0.03,0.015,0.12)
    gauss_PASS_badbalance_Mu       = ROOT.RooGaussian("gauss_PASS_badbalance_Mu","gauss", dphiZjet ,gauss_mean_PASS_badbalance_Mu,gauss_sigma_PASS_badbalance_Mu)
    tmpxg_SIG_PASS_badbalance_Mu   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS_badbalance_Mu","template x gauss" ,dphiZjet, pdf_template_SIG_PASS_badbalance_Mu , gauss_PASS_badbalance_Mu)

    gauss_mean_PASS_badbalance_El  = ROOT.RooRealVar("mean_PASS_badbalance_El","mean",0,-0.05,0.05)
    gauss_sigma_PASS_badbalance_El = ROOT.RooRealVar("sigma_PASS_badbalance_El","sigma gauss",0.03,0.015,0.12)
    gauss_PASS_badbalance_El       = ROOT.RooGaussian("gauss_PASS_badbalance_El","gauss", dphiZjet ,gauss_mean_PASS_badbalance_El,gauss_sigma_PASS_badbalance_El)
    tmpxg_SIG_PASS_badbalance_El   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS_badbalance_El","template x gauss" ,dphiZjet, pdf_template_SIG_PASS_badbalance_El , gauss_PASS_badbalance_El)
    # FAIL
    gauss_mean_FAIL_badbalance_Mu  = ROOT.RooRealVar("mean_FAIL_badbalance_Mu","mean",0,-0.05,0.05)
    gauss_sigma_FAIL_badbalance_Mu = ROOT.RooRealVar("sigma_FAIL_badbalance_Mu","sigma gauss",0.03,0.015,0.12)
    gauss_FAIL_badbalance_Mu       = ROOT.RooGaussian("gauss_FAIL_badbalance_Mu","gauss", dphiZjet ,gauss_mean_FAIL_badbalance_Mu,gauss_sigma_FAIL_badbalance_Mu)
    tmpxg_SIG_FAIL_badbalance_Mu   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL_badbalance_Mu","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL_badbalance_Mu , gauss_FAIL_badbalance_Mu)

    gauss_mean_FAIL_badbalance_El  = ROOT.RooRealVar("mean_FAIL_badbalance_El","mean",0,-0.05,0.05)
    gauss_sigma_FAIL_badbalance_El = ROOT.RooRealVar("sigma_FAIL_badbalance_El","sigma gauss",0.03,0.015,0.12)
    gauss_FAIL_badbalance_El       = ROOT.RooGaussian("gauss_FAIL_badbalance_El","gauss", dphiZjet ,gauss_mean_FAIL_badbalance_El,gauss_sigma_FAIL_badbalance_El)
    tmpxg_SIG_FAIL_badbalance_El   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL_badbalance_El","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL_badbalance_El , gauss_FAIL_badbalance_El)
    #
    # Smears the PU template template with a Gaussian to allow for different phi resolution between data and simulation.  
    # Not needed if the template is a flat distribution.  
    #
    # PASS
    # gauss_mean_PU_PASS_badbalance  = ROOT.RooRealVar("mean_PU_PASS_badbalance","mean",0,-0.05,0.05)
    # gauss_sigma_PU_PASS_badbalance = ROOT.RooRealVar("sigma_PU_PASS_badbalance","sigma gauss",0.03,0.015,0.12)
    # gauss_PU_PASS_badbalance       = ROOT.RooGaussian("gauss_PU_PASS_badbalance","gauss", dphiZjet ,gauss_mean_PU_PASS_badbalance,gauss_sigma_PU_PASS_badbalance) 
    # tmpxg_PU_PASS_badbalance       = ROOT.RooFFTConvPdf("tmpxg_PU_PASS_badbalance","template x gauss" ,dphiZjet, pdf_template_PU_PASS_badbalance , gauss_PU_PASS_badbalance)
    # # FAIL
    # gauss_mean_PU_FAIL  = ROOT.RooRealVar("mean_PU_FAIL_badbalance","mean",0,-0.05,0.05)
    # gauss_sigma_PU_FAIL = ROOT.RooRealVar("sigma_PU_FAIL_badbalance","sigma gauss",0.03,0.015,0.12)
    # gauss_PU_FAIL       = ROOT.RooGaussian("gauss_PU_FAIL_badbalance","gauss", dphiZjet ,gauss_mean_PU_FAIL_badbalance, gauss_sigma_PU_FAIL_badbalance) 
    # tmpxg_PU_FAIL       = ROOT.RooFFTConvPdf("tmpxg_PU_FAIL_badbalance","template x gauss" ,dphiZjet, pdf_template_PU_FAIL_badbalance, gauss_PU_FAIL_badbalance)
    #
    # Convert to extended pdf 
    #
    extpdf_PU_PASS_badbalance_Mu    = ROOT.RooExtendPdf("extpdf_PU_PASS_badbalance_Mu", "extpdf_PU_PASS_Mu",   pol0_PU_PASS_badbalance_Mu,   n_PU_PASS_badbalance_Mu)
    extpdf_PU_FAIL_badbalance_Mu    = ROOT.RooExtendPdf("extpdf_PU_FAIL_badbalance_Mu", "extpdf_PU_FAIL_Mu",   pol0_PU_FAIL_badbalance_Mu,   n_PU_FAIL_badbalance_Mu)
    extpdf_SIG_PASS_badbalance_Mu   = ROOT.RooExtendPdf("extpdf_SIG_PASS_badbalance_Mu", "extpdf_SIG_PASS_Mu", tmpxg_SIG_PASS_badbalance_Mu, n_SIG_PASS_badbalance_Mu)
    extpdf_SIG_FAIL_badbalance_Mu   = ROOT.RooExtendPdf("extpdf_SIG_FAIL_badbalance_Mu", "extpdf_SIG_FAIL_Mu", tmpxg_SIG_FAIL_badbalance_Mu, n_SIG_FAIL_badbalance_Mu)


    extpdf_PU_PASS_badbalance_El    = ROOT.RooExtendPdf("extpdf_PU_PASS_badbalance_El", "extpdf_PU_PASS_El",   pol0_PU_PASS_badbalance_El,   n_PU_PASS_badbalance_El)
    extpdf_PU_FAIL_badbalance_El    = ROOT.RooExtendPdf("extpdf_PU_FAIL_badbalance_El", "extpdf_PU_FAIL_El",   pol0_PU_FAIL_badbalance_El,   n_PU_FAIL_badbalance_El)
    extpdf_SIG_PASS_badbalance_El   = ROOT.RooExtendPdf("extpdf_SIG_PASS_badbalance_El", "extpdf_SIG_PASS_El", tmpxg_SIG_PASS_badbalance_El, n_SIG_PASS_badbalance_El)
    extpdf_SIG_FAIL_badbalance_El   = ROOT.RooExtendPdf("extpdf_SIG_FAIL_badbalance_El", "extpdf_SIG_FAIL_El", tmpxg_SIG_FAIL_badbalance_El, n_SIG_FAIL_badbalance_El)

    #
    # PU+SIG PDF
    #
    extpdf_SIGandPU_PASS_badbalance_Mu = ROOT.RooAddPdf("extpdf_SIGandPU_PASS_badbalance_Mu", "Signal+PU PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS_badbalance_Mu,extpdf_PU_PASS_badbalance_Mu),ROOT.RooArgList(n_SIG_PASS_badbalance_Mu,n_PU_PASS_badbalance_Mu))
    extpdf_SIGandPU_FAIL_badbalance_Mu = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL_badbalance_Mu", "Signal+PU PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL_badbalance_Mu,extpdf_PU_FAIL_badbalance_Mu),ROOT.RooArgList(n_SIG_FAIL_badbalance_Mu,n_PU_FAIL_badbalance_Mu))
    
    
    extpdf_SIGandPU_PASS_badbalance_El = ROOT.RooAddPdf("extpdf_SIGandPU_PASS_badbalance_El", "Signal+PU PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS_badbalance_El,extpdf_PU_PASS_badbalance_El),ROOT.RooArgList(n_SIG_PASS_badbalance_El,n_PU_PASS_badbalance_El))
    extpdf_SIGandPU_FAIL_badbalance_El = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL_badbalance_El", "Signal+PU PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL_badbalance_El,extpdf_PU_FAIL_badbalance_El),ROOT.RooArgList(n_SIG_FAIL_badbalance_El,n_PU_FAIL_badbalance_El))
    #
    # Now we are ready to perform the simultaneous fit to all distributions. 
    #
    sample = ROOT.RooCategory("sample","sample")
    sample.defineType("PASSsample_Mu")
    sample.defineType("FAILsample_Mu")
    sample.defineType("PASSsample_badbalance_Mu")
    sample.defineType("FAILsample_badbalance_Mu")
    sample.defineType("PASSsample_El")
    sample.defineType("FAILsample_El")
    sample.defineType("PASSsample_badbalance_El")
    sample.defineType("FAILsample_badbalance_El")

    histdict = {"PASSsample_Mu": dh_dphiZjet_PASS_Mu,
                "FAILsample_Mu": dh_dphiZjet_FAIL_Mu,
                "PASSsample_badbalance_Mu": dh_dphiZjet_PASS_badbalance_Mu,
                "FAILsample_badbalance_Mu": dh_dphiZjet_FAIL_badbalance_Mu,
                "PASSsample_El": dh_dphiZjet_PASS_El,
                "FAILsample_El": dh_dphiZjet_FAIL_El,
                "PASSsample_badbalance_El": dh_dphiZjet_PASS_badbalance_El,
                "FAILsample_badbalance_El": dh_dphiZjet_FAIL_badbalance_El

                }
    histmap = ROOT.std.map("string","RooDataHist*")()
    for key, item in histdict.items():
        histmap.insert((key, item))
    combData = ROOT.RooDataHist("allevents",
                                "PASS+FAIL",
                                ROOT.RooArgList(dphiZjet),
                                sample,
                                histmap);
                                # ROOT.RooFit.Import("PASSsample_Mu",dh_dphiZjet_PASS_Mu),
                                # ROOT.RooFit.Import("FAILsample_Mu",dh_dphiZjet_FAIL_Mu),
                                # ROOT.RooFit.Import("PASSsample_badbalance_Mu",dh_dphiZjet_PASS_badbalance_Mu),
                                # ROOT.RooFit.Import("FAILsample_badbalance_Mu",dh_dphiZjet_FAIL_badbalance_Mu),
                                # ROOT.RooFit.Import("PASSsample_El",dh_dphiZjet_PASS_El),
                                # ROOT.RooFit.Import("FAILsample_El",dh_dphiZjet_FAIL_El),
                                # ROOT.RooFit.Import("PASSsample_badbalance_El",dh_dphiZjet_PASS_badbalance_El),
                                # ROOT.RooFit.Import("FAILsample_badbalance_El",dh_dphiZjet_FAIL_badbalance_El));
    
    simultpdf = ROOT.RooSimultaneous("simultpdf","simultaneous pdf",sample)
    simultpdf.addPdf(extpdf_SIGandPU_PASS_Mu,"PASSsample_Mu")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL_Mu,"FAILsample_Mu")
    simultpdf.addPdf(extpdf_SIGandPU_PASS_badbalance_Mu,"PASSsample_badbalance_Mu")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL_badbalance_Mu,"FAILsample_badbalance_Mu")
    simultpdf.addPdf(extpdf_SIGandPU_PASS_El,"PASSsample_El")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL_El,"FAILsample_El")
    simultpdf.addPdf(extpdf_SIGandPU_PASS_badbalance_El,"PASSsample_badbalance_El")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL_badbalance_El,"FAILsample_badbalance_El")
    ncpu = 1
    simultpdf.fitTo(combData,ROOT.RooFit.Save(),ROOT.RooFit.NumCPU(ncpu))
    simultpdf.fitTo(combData,ROOT.RooFit.Save(),ROOT.RooFit.NumCPU(ncpu))

    simultpdf.fitTo(combData,ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1),ROOT.RooFit.NumCPU(ncpu))
    simultpdf.fitTo(combData,ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1),ROOT.RooFit.NumCPU(ncpu))

    ROOT.gStyle.SetTitleStyle(0)
    ROOT.gStyle.SetTitleBorderSize(0)
    
    #
    # Plots the fits in PASS,GOOD frame. 
    #
    framePASS_Mu        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, GOOD Balance, Muon Channel"))
    if isData:
        combData.plotOn(framePASS_Mu,ROOT.RooFit.Cut("sample==sample::PASSsample_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS_Mu,ROOT.RooFit.Cut("sample==sample::PASSsample_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS_Mu,ROOT.RooFit.Slice(sample,"PASSsample_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS_Mu,ROOT.RooFit.Slice(sample,"PASSsample_Mu"),ROOT.RooFit.Components("extpdf_PU_PASS_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed));
    framePASS_Mu.SetMaximum(framePASS_Mu.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,GOOD frame. 
    #
    frameFAIL_Mu        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, GOOD Balance, Muon Channel"))
    if isData:
        combData.plotOn(frameFAIL_Mu,ROOT.RooFit.Cut("sample==sample::FAILsample_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL_Mu,ROOT.RooFit.Cut("sample==sample::FAILsample_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL_Mu,ROOT.RooFit.Slice(sample,"FAILsample_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL_Mu,ROOT.RooFit.Slice(sample,"FAILsample_Mu"),ROOT.RooFit.Components("extpdf_PU_FAIL_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))    
    frameFAIL_Mu.SetMaximum(frameFAIL_Mu.GetMaximum()*1.40)
    #
    # Plot the fit in PASS,BAD frame. 
    #
    framePASS_badbalance_Mu        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, BAD Balance, Muon Channel"))
    if isData:
        combData.plotOn(framePASS_badbalance_Mu,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS_badbalance_Mu,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS_badbalance_Mu,ROOT.RooFit.Slice(sample,"PASSsample_badbalance_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS_badbalance_Mu,ROOT.RooFit.Slice(sample,"PASSsample_badbalance_Mu"),ROOT.RooFit.Components("extpdf_PU_PASS_badbalance_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    framePASS_badbalance_Mu.SetMaximum(framePASS_badbalance_Mu.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,BAD frame. 
    #
    frameFAIL_badbalance_Mu        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, BAD Balance, Muon Channel"))
    if isData:
        combData.plotOn(frameFAIL_badbalance_Mu,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL_badbalance_Mu,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance_Mu"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL_badbalance_Mu,ROOT.RooFit.Slice(sample,"FAILsample_badbalance_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL_badbalance_Mu,ROOT.RooFit.Slice(sample,"FAILsample_badbalance_Mu"),ROOT.RooFit.Components("extpdf_PU_FAIL_badbalance_Mu"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    frameFAIL_badbalance_Mu.SetMaximum(frameFAIL_badbalance_Mu.GetMaximum()*1.40)

    nentries_PASS_Mu = h_dphi_PASS_Mu.GetEntries()
    nentries_FAIL_Mu = h_dphi_FAIL_Mu.GetEntries()
    nentries_PASS_badbalance_Mu = h_dphi_PASS_badbalance_Mu.GetEntries()
    nentries_FAIL_badbalance_Mu = h_dphi_FAIL_badbalance_Mu.GetEntries()
    #
    # Plots the fits in PASS,GOOD frame. 
    #
    framePASS_El        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, GOOD Balance, Elec Channel"))
    if isData:
        combData.plotOn(framePASS_El,ROOT.RooFit.Cut("sample==sample::PASSsample_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS_El,ROOT.RooFit.Cut("sample==sample::PASSsample_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS_El,ROOT.RooFit.Slice(sample,"PASSsample_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS_El,ROOT.RooFit.Slice(sample,"PASSsample_El"),ROOT.RooFit.Components("extpdf_PU_PASS_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed));
    framePASS_El.SetMaximum(framePASS_El.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,GOOD frame. 
    #
    frameFAIL_El        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, GOOD Balance, Elec Channel"))
    if isData:
        combData.plotOn(frameFAIL_El,ROOT.RooFit.Cut("sample==sample::FAILsample_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL_El,ROOT.RooFit.Cut("sample==sample::FAILsample_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL_El,ROOT.RooFit.Slice(sample,"FAILsample_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL_El,ROOT.RooFit.Slice(sample,"FAILsample_El"),ROOT.RooFit.Components("extpdf_PU_FAIL_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))    
    frameFAIL_El.SetMaximum(frameFAIL_El.GetMaximum()*1.40)
    #
    # Plot the fit in PASS,BAD frame. 
    #
    framePASS_badbalance_El        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, BAD Balance, Elec Channel"))
    if isData:
        combData.plotOn(framePASS_badbalance_El,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS_badbalance_El,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS_badbalance_El,ROOT.RooFit.Slice(sample,"PASSsample_badbalance_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS_badbalance_El,ROOT.RooFit.Slice(sample,"PASSsample_badbalance_El"),ROOT.RooFit.Components("extpdf_PU_PASS_badbalance_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    framePASS_badbalance_El.SetMaximum(framePASS_badbalance_El.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,BAD frame. 
    #
    frameFAIL_badbalance_El        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, BAD Balance, Elec Channel"))
    if isData:
        combData.plotOn(frameFAIL_badbalance_El,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL_badbalance_El,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance_El"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL_badbalance_El,ROOT.RooFit.Slice(sample,"FAILsample_badbalance_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL_badbalance_El,ROOT.RooFit.Slice(sample,"FAILsample_badbalance_El"),ROOT.RooFit.Components("extpdf_PU_FAIL_badbalance_El"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    frameFAIL_badbalance_El.SetMaximum(frameFAIL_badbalance_El.GetMaximum()*1.40)

    nentries_PASS_El = h_dphi_PASS_El.GetEntries()
    nentries_FAIL_El = h_dphi_FAIL_El.GetEntries()
    nentries_PASS_badbalance_El = h_dphi_PASS_badbalance_El.GetEntries()
    nentries_FAIL_badbalance_El = h_dphi_FAIL_badbalance_El.GetEntries()

    # Add chi2 info
    chi2_text_Mu = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text_Mu.SetTextAlign(11)
    chi2_text_Mu.AddText("#chi^{2} fit = %s" %round(framePASS_Mu.chiSquare(6),2))
    chi2_text_Mu.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text_Mu.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text_Mu.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS_Mu.getVal(),3), round(gauss_sigma_PASS_Mu.getError(),3)) )
    chi2_text_Mu.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL_Mu.getVal(),3), round(gauss_sigma_FAIL_Mu.getError(),3)) )
    chi2_text_Mu.AddText("Entries PASS "+"= {}".format(nentries_PASS_Mu))
    chi2_text_Mu.AddText("Entries FALL "+"= {}".format(nentries_FAIL_Mu))
    chi2_text_Mu.SetTextSize(0.03)
    chi2_text_Mu.SetTextColor(2)
    chi2_text_Mu.SetShadowColor(0)
    chi2_text_Mu.SetFillColor(0)
    chi2_text_Mu.SetLineColor(0)
    framePASS_Mu.addObject(chi2_text_Mu)
    frameFAIL_Mu.addObject(chi2_text_Mu)

    chi2_text_badbalance_Mu = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text_badbalance_Mu.SetTextAlign(11)
    chi2_text_badbalance_Mu.AddText("#chi^{2} fit = %s" %round(framePASS_Mu.chiSquare(6),2))
    chi2_text_badbalance_Mu.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text_badbalance_Mu.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text_badbalance_Mu.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS_badbalance_Mu.getVal(),3), round(gauss_sigma_PASS_badbalance_Mu.getError(),3)) )
    chi2_text_badbalance_Mu.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL_badbalance_Mu.getVal(),3), round(gauss_sigma_FAIL_badbalance_Mu.getError(),3)) )
    chi2_text_badbalance_Mu.AddText("Entries PASS "+"= {}".format(nentries_PASS_badbalance_Mu))
    chi2_text_badbalance_Mu.AddText("Entries FALL "+"= {}".format(nentries_FAIL_badbalance_Mu))
    chi2_text_badbalance_Mu.SetTextSize(0.03)
    chi2_text_badbalance_Mu.SetTextColor(2)
    chi2_text_badbalance_Mu.SetShadowColor(0)
    chi2_text_Mu.SetFillColor(0)
    chi2_text_badbalance_Mu.SetLineColor(0)
    framePASS_badbalance_Mu.addObject(chi2_text_badbalance_Mu)
    frameFAIL_badbalance_Mu.addObject(chi2_text_badbalance_Mu)

    chi2_text_El = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text_El.SetTextAlign(11)
    chi2_text_El.AddText("#chi^{2} fit = %s" %round(framePASS_El.chiSquare(6),2))
    chi2_text_El.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text_El.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text_El.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS_El.getVal(),3), round(gauss_sigma_PASS_El.getError(),3)) )
    chi2_text_El.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL_El.getVal(),3), round(gauss_sigma_FAIL_El.getError(),3)) )
    chi2_text_El.AddText("Entries PASS "+"= {}".format(nentries_PASS_El))
    chi2_text_El.AddText("Entries FALL "+"= {}".format(nentries_FAIL_El))
    chi2_text_El.SetTextSize(0.03)
    chi2_text_El.SetTextColor(2)
    chi2_text_El.SetShadowColor(0)
    chi2_text_El.SetFillColor(0)
    chi2_text_El.SetLineColor(0)
    framePASS_El.addObject(chi2_text_El)
    frameFAIL_El.addObject(chi2_text_El)

    chi2_text_badbalance_El = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text_badbalance_El.SetTextAlign(11)
    chi2_text_badbalance_El.AddText("#chi^{2} fit = %s" %round(framePASS_El.chiSquare(6),2))
    chi2_text_badbalance_El.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text_badbalance_El.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text_badbalance_El.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS_badbalance_El.getVal(),3), round(gauss_sigma_PASS_badbalance_El.getError(),3)) )
    chi2_text_badbalance_El.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL_badbalance_El.getVal(),3), round(gauss_sigma_FAIL_badbalance_El.getError(),3)) )
    chi2_text_badbalance_El.AddText("Entries PASS "+"= {}".format(nentries_PASS_badbalance_El))
    chi2_text_badbalance_El.AddText("Entries FALL "+"= {}".format(nentries_FAIL_badbalance_El))
    chi2_text_badbalance_El.SetTextSize(0.03)
    chi2_text_badbalance_El.SetTextColor(2)
    chi2_text_badbalance_El.SetShadowColor(0)
    chi2_text_El.SetFillColor(0)
    chi2_text_badbalance_El.SetLineColor(0)
    framePASS_badbalance_El.addObject(chi2_text_badbalance_El)
    frameFAIL_badbalance_El.addObject(chi2_text_badbalance_El)

    latexBinStr = ""
    latexBinStr += pt.split("To")[0]+" GeV < pT_{jet} < "+ pt.split("To")[1]+" GeV, "
    if doEtaBins:
        latexBinStr += eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")
    else:
        latexBinStr += eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")
    latexBinStr += ", Data" if isData else ", MC"     

    #
    #
    #
    cfitPASS_Mu.cd()
    cfitPASS_Mu.Clear()
    framePASS_Mu.Draw()
                                        
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.3*cfitPASS_Mu.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right   

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    framePASS_Mu.Print()
 
    legend = ROOT.TLegend(0.60,0.75,0.88,0.88)
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.Draw("same")
 
    #
    #
    #
    cfitFAIL_Mu.cd()
    cfitFAIL_Mu.Clear()
    frameFAIL_Mu.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    frameFAIL_Mu.Print()

    legend.Draw("same")

    #
    #
    #
    cfitPASS_badbalance_Mu.cd()
    cfitPASS_badbalance_Mu.Clear()
    framePASS_badbalance_Mu.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    framePASS_badbalance_Mu.Print()
    legend.Draw("same")

    #
    #
    #
    cfitFAIL_badbalance_Mu.cd()
    cfitFAIL_badbalance_Mu.Clear()
    frameFAIL_badbalance_Mu.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    frameFAIL_badbalance_Mu.Print()
    legend.Draw("same")

    fit_filename = "fit"
    typeStr = "data" if isData else "mc"
    
    pdfStr = "pdf"
    if iBinCount == 0: pdfStr = "pdf("
    elif iBinCount == iBinTotal-1: pdfStr = "pdf)"

    cfitPASS_Mu.SaveAs("{}/{}_PASS_GOODbal_{}_Mu.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL_Mu.SaveAs("{}/{}_FAIL_GOODbal_{}_Mu.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitPASS_badbalance_Mu.SaveAs("{}/{}_PASS_BADbal_{}_Mu.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL_badbalance_Mu.SaveAs("{}/{}_FAIL_BADbal_{}_Mu.{}".format(outputDir,fit_filename,typeStr,pdfStr))

    cfitPASS_El.cd()
    cfitPASS_El.Clear()
    framePASS_El.Draw()
                                        
    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.3*cfitPASS_El.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right   

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    framePASS_El.Print()
 
    legend = ROOT.TLegend(0.60,0.75,0.88,0.88)
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.Draw("same")
 
    #
    #
    #
    cfitFAIL_El.cd()
    cfitFAIL_El.Clear()
    frameFAIL_El.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    frameFAIL_El.Print()

    legend.Draw("same")

    #
    #
    #
    cfitPASS_badbalance_El.cd()
    cfitPASS_badbalance_El.Clear()
    framePASS_badbalance_El.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    framePASS_badbalance_El.Print()
    legend.Draw("same")

    #
    #
    #
    cfitFAIL_badbalance_El.cd()
    cfitFAIL_badbalance_El.Clear()
    frameFAIL_badbalance_El.Draw()

    latex2.DrawLatex(0.89, 0.915, latexBinStr)
    latex2.Draw("same")
    frameFAIL_badbalance_El.Print()
    legend.Draw("same")

    fit_filename = "fit"
    typeStr = "data" if isData else "mc"
    
    pdfStr = "pdf"
    if iBinCount == 0: pdfStr = "pdf("
    elif iBinCount == iBinTotal-1: pdfStr = "pdf)"

    cfitPASS_El.SaveAs("{}/{}_PASS_GOODbal_{}_El.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL_El.SaveAs("{}/{}_FAIL_GOODbal_{}_El.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitPASS_badbalance_El.SaveAs("{}/{}_PASS_BADbal_{}_El.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL_badbalance_El.SaveAs("{}/{}_FAIL_BADbal_{}_El.{}".format(outputDir,fit_filename,typeStr,pdfStr))


    print("eff (fit)    = {:.3f}".format(effcy.getVal())) 
    print("eff (gen)    = {:.3f}".format(eff_gen)) 
    print("mistag (fit) = {:.3f}".format(mistag.getVal())) 
    print("mistag (gen) = {:.3f}".format(mistag_gen)) 

    if isData:
        return effcy.getVal(), effcy.getError(), mistag.getVal(), mistag.getError()
    else: 
        return effcy.getVal(), effcy.getError(), mistag.getVal(), mistag.getError(), eff_gen, mistag_gen

def main():

    parser = argparse.ArgumentParser(description='Extract PU ID effcy/mistag rate and scale factors')
    #Optional arguments
    parser.add_argument("--input",     dest="input",         help="input directory path",      type=str)
    parser.add_argument("--output",    dest="output",        help="output directory path",     type=str)
    parser.add_argument("--year",      dest="year",          help="data year",                 type=str)
    parser.add_argument("--wp",        dest="workingpoint",  help="Loose or Medium or Tight",  type=str)
    parser.add_argument("--order",    default="LO", help = "LO or NLO", type=str)
    parser.add_argument("--useHerwig", default=False,        action='store_true')
    parser.add_argument("--usePowheg", default=False,        action='store_true')
    parser.add_argument("--syst",      dest="syst",          default="central", help="central,jerUp,jerDown,jesTotalUp,jesTotalDown", type=str)

    args = parser.parse_args()    
    
    inputDir  = args.input
    outputDir = args.output
    year = args.year 
    workingpoint = args.workingpoint
    print(args.order)
    
    if args.order == "LO":
        useNLO = False
    elif args.order == "NLO":
        useNLO = True
    print(useNLO)
    useHerwig = args.useHerwig
    usePowheg = args.usePowheg
    
    if args.syst == "central":
        syst = ""
    else:
        syst = args.syst
    # Make output directory if it does not exist
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    data_filename_Mu = ""
    mc_filename_Mu = ""
    data_filename_El = ""
    mc_filename_El = ""

    if year == "2016":
        data_filename_Mu = inputDir+"/Histo_Data16_Mu.root"
        mc_filename_Mu  = inputDir+"/Histo_MC16_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MC16_DY_AMCNLO_Mu.root"
        if useHerwig: mc_filename_Mu   = inputDir+"/Histo_MC16_DY_MG_HW_Mu.root"
        data_filename_El = inputDir+"/Histo_Data16_Mu.root"
        mc_filename_El   = inputDir+"/Histo_MC16_DY_MG_Mu.root"
        if useNLO:    mc_filename_El   = inputDir+"/Histo_MC16_DY_AMCNLO_Mu.root"
        if useHerwig: mc_filename_El  = inputDir+"/Histo_MC16_DY_MG_HW_Mu.root"
    elif year == "2017":
        data_filename_Mu = inputDir+"/Histo_Data17_Mu.root"
        mc_filename_Mu  = inputDir+"/Histo_MC17_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MC17_DY_AMCNLO_Mu.root"
        if useHerwig: mc_filename_Mu   = inputDir+"/Histo_MC17_DY_MG_HW_Mu.root"
        data_filename_El = inputDir+"/Histo_Data17_Mu.root"
        mc_filename_El   = inputDir+"/Histo_MC17_DY_MG_Mu.root"
        if useNLO:    mc_filename_El   = inputDir+"/Histo_MC17_DY_AMCNLO_Mu.root"
        if useHerwig: mc_filename_El  = inputDir+"/Histo_MC17_DY_MG_HW_Mu.root"
    elif year == "2018":
        data_filename = inputDir+"/Histo_Data18.root"
        mc_filename   = inputDir+"/Histo_MC18_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MC18_DY_AMCNLO.root"
        if useHerwig: mc_filename   = inputDir+"/Histo_MC18_DY_MG_HW.root"
    elif year == "UL2017":
        data_filename_Mu = inputDir+"/Histo_DataUL17_Mu.root"
        mc_filename_Mu  = inputDir+"/Histo_MCUL17_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MCUL17_DY_AMCNLO_Mu.root"
        data_filename_El = inputDir+"/Histo_DataUL17_El.root"
        mc_filename_El   = inputDir+"/Histo_MCUL17_DY_MG_El.root"
        if useNLO:    mc_filename_El   = inputDir+"/Histo_MCUL17_DY_AMCNLO_El.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL17_DY_MG_HW.root"
        # if usePowheg: mc_filename   = inputDir+"/Histo_MCUL17_DYToMuMu_PHG.root"
    elif year == "UL2018":
        data_filename_Mu = inputDir+"/Histo_DataUL18_Mu.root"
        mc_filename_Mu   = inputDir+"/Histo_MCUL18_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MCUL18_DY_AMCNLO_Mu.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL18_DY_MG_HW.root"
        # if usePowheg: mc_filename   = inputDir+"/Histo_MCUL18_DYToMuMu_PHG.root"
        data_filename_El = inputDir+"/Histo_DataUL18_El.root"
        mc_filename_El  = inputDir+"/Histo_MCUL18_DY_MG_El.root"
        if useNLO:    mc_filename_El = inputDir+"/Histo_MCUL18_DY_AMCNLO_El.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL18_DY_MG_HW.root"
        # if usePowheg: mc_filename   = inputDir+"/Histo_MCUL18_DYToMuMu_PHG.root"
    elif year == "UL2016APV":
        data_filename_Mu = inputDir+"/Histo_DataUL16APV_Mu.root"
        mc_filename_Mu   = inputDir+"/Histo_MCUL16APV_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MCUL16APV_DY_AMCNLO_Mu.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16APV_DY_MG_HW.root"
        if usePowheg: mc_filename_Mu   = inputDir+"/Histo_MCUL16APV_DYToMuMu_PHG_Mu.root"
        data_filename_El = inputDir+"/Histo_DataUL16APV_El.root"
        mc_filename_El   = inputDir+"/Histo_MCUL16APV_DY_MG_El.root"
        if useNLO:    mc_filename_El   = inputDir+"/Histo_MCUL16APV_DY_AMCNLO_El.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16APV_DY_MG_HW.root"
        if usePowheg: mc_filename_El   = inputDir+"/Histo_MCUL16APV_DYToMuMu_PHG_El.root"
    elif year == "UL2016":
        data_filename_Mu = inputDir+"/Histo_DataUL16_Mu.root"
        mc_filename_Mu   = inputDir+"/Histo_MCUL16_DY_MG_Mu.root"
        if useNLO:    mc_filename_Mu   = inputDir+"/Histo_MCUL16_DY_AMCNLO_Mu.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16_DY_MG_HW.root"
        if usePowheg: mc_filename_Mu   = inputDir+"/Histo_MCUL16_DYToMuMu_PHG_Mu.root"

        data_filename_El = inputDir+"/Histo_DataUL16_El.root"
        mc_filename_El   = inputDir+"/Histo_MCUL16_DY_MG_El.root"
        if useNLO:    mc_filename_El   = inputDir+"/Histo_MCUL16_DY_AMCNLO_El.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16_DY_MG_HW.root"
        if usePowheg: mc_filename_El   = inputDir+"/Histo_MCUL16_DYToMuMu_PHG_El.root"


    if syst != "":
        if  useHerwig or usePowheg:
            raise Exception("Can't specify systematics for Herwig/Powheg samples. Only LO and NLO samples.")
        else:
            mc_filename_El = mc_filename_El.replace("_El.root","_"+syst+"_El.root")
            mc_filename_Mu = mc_filename_Mu.replace("_Mu.root","_"+syst+"_Mu.root")
    print(mc_filename_El)
    print(mc_filename_Mu)
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetMarkerSize(0.5)
    # ROOT.gStyle.SetOptLogx()

    f_data_El = ROOT.TDCacheFile(data_filename_El,"READ")
    f_mc_El   = ROOT.TDCacheFile(mc_filename_El,  "READ")
    f_data_Mu = ROOT.TDCacheFile(data_filename_Mu,"READ")
    f_mc_Mu   = ROOT.TDCacheFile(mc_filename_Mu,  "READ")
    #
    # Check both file is open
    #
    if not(f_data_Mu.IsOpen()):
        raise Exception('Cannot open data input histo file:' + data_filename_Mu)
    if not(f_mc_Mu.IsOpen()):
        raise Exception('Cannot open mc input histo file:' + mc_filename_Mu)
    if not(f_data_El.IsOpen()):
        raise Exception('Cannot open data input histo file:' + data_filename_El)
    if not(f_mc_El.IsOpen()):
        raise Exception('Cannot open mc input histo file:' + mc_filename_El)
   
    #
    # pt Binning
    #
    _pt = [
        "20To25",
        "25To30",
        "30To40",
        "40To50",
    ]

    #
    # eta Binning
    #
    doEtaBins=True
    _eta = []
    if doEtaBins:
        _eta = [
            "neg5p0Toneg3p0",
            "neg3p0Toneg2p75",
            "neg2p75Toneg2p5",
            "neg2p5Toneg2p0",
            "neg2p0Toneg1p479",
            "neg1p479To0p0",
            "0p0Topos1p479",
            "pos1p479Topos2p0",
            "pos2p0Topos2p5",
            "pos2p5Topos2p75",
            "pos2p75Topos3p0",
            "pos3p0Topos5p0"
        ]
    else:
        _eta= [
            "0p0To1p479",
            "1p479To2p0",
            "2p0To2p5", 
            "2p5To2p75", 
            "2p75To3p0", 
            "3p0To5p0"
        ]

    #
    # Convert bin boundary strings to numerical values
    #
    xbins = []
    ybins = []
    # ptbin
    for ptBin in _pt:
        print(ptBin)
        xbins.append(float(ptBin.split("To")[0]))                                
        xbins.append(float(ptBin.split("To")[1]))  
    # etabin
    for etaBin in _eta:
        print(etaBin)
        if doEtaBins:
            lowBound   = etaBin.split("To")[0]
            lowBound   = lowBound.replace("pos","+").replace("neg","-")
            lowBound   = lowBound.replace("p",".")
            highBound  = etaBin.split("To")[1]
            highBound  = highBound.replace("pos","+").replace("neg","-")
            highBound  = highBound.replace("p",".")
        else:
            lowBound  = etaBin.split("To")[0].replace("p",".")
            highBound = etaBin.split("To")[1].replace("p",".")
        ybins.append(float(lowBound))               
        ybins.append(float(highBound)) 

    xbins.sort()
    ybins.sort()
    #
    # transform to numpy array for ROOT 
    #
    xbinsT = np.array(xbins)
    ybinsT = np.array(ybins)
    ## just in case there are duplicates
    xbinsTab = np.unique(xbinsT)
    ybinsTab = np.unique(ybinsT)

    heffdata    = ROOT.TH2F("heffdata",   "PU ID Eff Data, WP " +workingpoint+ ", "+year,   xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)
    heffmc      = ROOT.TH2F("heffmc",     "PU ID Eff MC, WP " +workingpoint+ ", "+year,     xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)
    hmistagdata = ROOT.TH2F("hmistagdata","PU ID Mistag Data, WP " +workingpoint+ ", "+year,xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)
    hmistagmc   = ROOT.TH2F("hmistagmc",  "PU ID Mistag MC, WP " +workingpoint+ ", "+year,  xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)
    heffgen     = ROOT.TH2F("heffgen",     "PU ID Eff MC (Gen-Based), WP " +workingpoint+ ", "+year,     xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)
    hmistaggen  = ROOT.TH2F("hmistaggen",  "PU ID Mistag MC (Gen-Based), WP " +workingpoint+ ", "+year,  xbinsTab.size-1,xbinsTab,ybinsTab.size-1,ybinsTab)

    
    heffdata.Sumw2()
    heffmc.Sumw2()
    hmistagdata.Sumw2()
    hmistagmc.Sumw2()
    heffgen.Sumw2()
    hmistaggen.Sumw2()

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPaintTextFormat("6.4f")

    cfitPASS_Mu = ROOT.TCanvas("cfitPASS_Mu","cfitPASS_Mu",600,600)
    cfitPASS_Mu.SetLogx(False)

    cfitFAIL_Mu = ROOT.TCanvas("cfitFAIL_Mu","cfitFAIL_Mu",600,600)
    cfitFAIL_Mu.SetLogx(False)

    cfitPASS_badbalance_Mu = ROOT.TCanvas("cfitPASS_badbalance_Mu","cfitPASS_badbalance_Mu",600,600)
    cfitPASS_badbalance_Mu.SetLogx(False)

    cfitFAIL_badbalance_Mu = ROOT.TCanvas("cfitFAIL_badbalance_Mu","cfitFAIL_badbalance_Mu",600,600)
    cfitFAIL_badbalance_Mu.SetLogx(False)

    cfitPASS_El = ROOT.TCanvas("cfitPASS_El","cfitPASS_El",600,600)
    cfitPASS_El.SetLogx(False)

    cfitFAIL_El = ROOT.TCanvas("cfitFAIL_El","cfitFAIL_El",600,600)
    cfitFAIL_El.SetLogx(False)

    cfitPASS_badbalance_El = ROOT.TCanvas("cfitPASS_badbalance_El","cfitPASS_badbalance_El",600,600)
    cfitPASS_badbalance_El.SetLogx(False)

    cfitFAIL_badbalance_El = ROOT.TCanvas("cfitFAIL_badbalance_El","cfitFAIL_badbalance_El",600,600)
    cfitFAIL_badbalance_El.SetLogx(False)

    iBinCount = 0
    iBinTotal = len(_pt) * len(_eta)
    
    binningStr = "_probeJet_dilep_dphi_norm"
    #binningStr = "_probeJet_dilep_dphi_m1_abs" 
    #binningStr = "_probeJet_dilep_dphiVarBin_norm"
    for i in range(0,len(_pt)):
        for j in range(0,len(_eta)):
            ptBinStr  = "_pt"+_pt[i]
            if doEtaBins:
                etaBinStr = "_eta"+_eta[j]
            else :
                etaBinStr = "_abseta"+_eta[j]

            binStr = etaBinStr+ptBinStr

            systStr=""
            if syst != "":
                systStr += "_"+syst

            #
            # Retrieve histograms: PASS ID, GOOD balance
            #
            h_dphi_mc_genunmatched_PASS_Mu = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_PASS_Mu  = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_PASS_Mu              = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_PASS_Mu            = f_data_Mu.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: FAIL ID, GOOD balance
            #
            h_dphi_mc_genunmatched_FAIL_Mu = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_FAIL_Mu   = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_FAIL_Mu              = f_mc_Mu.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_FAIL_Mu            = f_data_Mu.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: PASS ID, BAD balance
            #
            h_dphi_mc_genunmatched_PASS_badbalance_Mu =  f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_PASS_badbalance_Mu   =  f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_PASS_badbalance_Mu              =  f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_PASS_badbalance_Mu            =  f_data_Mu.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: FAIL ID, BAD balance
            #
            h_dphi_mc_genunmatched_FAIL_badbalance_Mu = f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_FAIL_badbalance_Mu   = f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_FAIL_badbalance_Mu              = f_mc_Mu.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_FAIL_badbalance_Mu            = f_data_Mu.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+binningStr)



            # Retrieve histograms: PASS ID, GOOD balance
            #
            h_dphi_mc_genunmatched_PASS_El = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_PASS_El   = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_PASS_El              = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_PASS_El            = f_data_El.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: FAIL ID, GOOD balance
            #
            h_dphi_mc_genunmatched_FAIL_El = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_FAIL_El   = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_FAIL_El              = f_mc_El.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_FAIL_El            = f_data_El.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: PASS ID, BAD balance
            #
            h_dphi_mc_genunmatched_PASS_badbalance_El =  f_mc_El.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_PASS_badbalance_El   =  f_mc_El.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_PASS_badbalance_El              =  f_mc_El.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_PASS_badbalance_El            =  f_data_El.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+binningStr)
            #
            # Retrieve histograms: FAIL ID, BAD balance
            #
            h_dphi_mc_genunmatched_FAIL_badbalance_El = f_mc_El.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_failGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_genmatched_FAIL_badbalance_El   = f_mc_El.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_passGenMatch"+binStr+binningStr+systStr)
            h_dphi_mc_FAIL_badbalance_El              = f_mc_El.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+binningStr+systStr)
            h_dphi_data_FAIL_badbalance_El            = f_data_El.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+binningStr)

            #
            # Perform fit on MC
            #
            eff_mc,eff_mc_err,mistag_mc,mistag_mc_err,eff_gen,mistag_gen=MakeDPhiFit(
                h_dphi_mc_genunmatched_PASS_Mu,h_dphi_mc_genmatched_PASS_Mu,h_dphi_mc_genunmatched_FAIL_Mu,h_dphi_mc_genmatched_FAIL_Mu,
                h_dphi_mc_PASS_Mu,h_dphi_mc_FAIL_Mu, 
                h_dphi_mc_genunmatched_PASS_badbalance_Mu, h_dphi_mc_genmatched_PASS_badbalance_Mu, h_dphi_mc_genunmatched_FAIL_badbalance_Mu, h_dphi_mc_genmatched_FAIL_badbalance_Mu, 
                h_dphi_mc_PASS_badbalance_Mu, h_dphi_mc_FAIL_badbalance_Mu,
                h_dphi_mc_genunmatched_PASS_El,h_dphi_mc_genmatched_PASS_El,h_dphi_mc_genunmatched_FAIL_El,h_dphi_mc_genmatched_FAIL_El,
                h_dphi_mc_PASS_El,h_dphi_mc_FAIL_El, 
                h_dphi_mc_genunmatched_PASS_badbalance_El, h_dphi_mc_genmatched_PASS_badbalance_El, h_dphi_mc_genunmatched_FAIL_badbalance_El, h_dphi_mc_genmatched_FAIL_badbalance_El, 
                h_dphi_mc_PASS_badbalance_El, h_dphi_mc_FAIL_badbalance_El,  
                outputDir,_pt[i], _eta[j], cfitPASS_Mu, cfitFAIL_Mu, cfitPASS_badbalance_Mu, cfitFAIL_badbalance_Mu, cfitPASS_El, cfitFAIL_El, cfitPASS_badbalance_El, cfitFAIL_badbalance_El, 
                iBinCount, iBinTotal,
                isData=False, doEtaBins=doEtaBins
            )
            heffmc.SetBinContent(i+1,j+1,    round(float(eff_mc),4))
            heffmc.SetBinError  (i+1,j+1,    round(float(eff_mc_err),4))
            hmistagmc.SetBinContent(i+1,j+1, round(float(mistag_mc),4))
            hmistagmc.SetBinError(i+1,j+1,   round(float(mistag_mc_err),4))
            heffgen.SetBinContent(i+1,j+1,    round(float(eff_gen),4))
            hmistaggen.SetBinContent(i+1,j+1, round(float(mistag_gen),4))
            f = open(os.path.join(outputDir, "bound_"+year+"_"+workingpoint[0]+".txt"),"a+")
            f.write("bin=%s, ibin = %d, ratio=%f, mistag_mc=%f, mistag_gen=%f, mistag_gen*0.25=%f, mistag_gen*1.75=%f\n" % (binStr,iBinCount, mistag_mc/mistag_gen,mistag_mc, mistag_gen, mistag_gen*0.25, mistag_gen*1.75))
            f.close()

            if (mistag_mc/mistag_gen) < 0.255 or (mistag_mc/mistag_gen) > 1.65:
                f = open(os.path.join(outputDir, "bound_alert_"+year+"_"+workingpoint[0]+".txt"),"a+")
                f.write("bin=%s, ratio=%f, mistag_mc=%f, mistag_gen=%f, mistag_gen*0.25=%f, mistag_gen*1.75=%f\n" % (binStr,mistag_mc/mistag_gen,mistag_mc, mistag_gen, mistag_gen*0.25, mistag_gen*1.75))
                f.close()


            #
            # Perform fit on Data
            #
            eff_data,eff_data_err,mistag_data,mistag_data_err=MakeDPhiFit(
                h_dphi_mc_genunmatched_PASS_Mu,h_dphi_mc_genmatched_PASS_Mu,h_dphi_mc_genunmatched_FAIL_Mu,h_dphi_mc_genmatched_FAIL_Mu,
                h_dphi_data_PASS_Mu,h_dphi_data_FAIL_Mu, 
                h_dphi_mc_genunmatched_PASS_badbalance_Mu, h_dphi_mc_genmatched_PASS_badbalance_Mu, h_dphi_mc_genunmatched_FAIL_badbalance_Mu, h_dphi_mc_genmatched_FAIL_badbalance_Mu, 
                h_dphi_data_PASS_badbalance_Mu, h_dphi_data_FAIL_badbalance_Mu,
                h_dphi_mc_genunmatched_PASS_El,h_dphi_mc_genmatched_PASS_El,h_dphi_mc_genunmatched_FAIL_El,h_dphi_mc_genmatched_FAIL_El,
                h_dphi_data_PASS_El,h_dphi_data_FAIL_El, 
                h_dphi_mc_genunmatched_PASS_badbalance_El, h_dphi_mc_genmatched_PASS_badbalance_El, h_dphi_mc_genunmatched_FAIL_badbalance_El, h_dphi_mc_genmatched_FAIL_badbalance_El, 
                h_dphi_data_PASS_badbalance_El, h_dphi_data_FAIL_badbalance_El,   
                outputDir,_pt[i], _eta[j], cfitPASS_Mu, cfitFAIL_Mu, cfitPASS_badbalance_Mu, cfitFAIL_badbalance_Mu, cfitPASS_El, cfitFAIL_El, cfitPASS_badbalance_El, cfitFAIL_badbalance_El,
                iBinCount, iBinTotal,
                isData=True, doEtaBins=doEtaBins
            )
            heffdata.SetBinContent(i+1,j+1,    round(float(eff_data),4))
            heffdata.SetBinError  (i+1,j+1,    round(float(eff_data_err),4))
            hmistagdata.SetBinContent(i+1,j+1, round(float(mistag_data),4))
            hmistagdata.SetBinError(i+1,j+1,   round(float(mistag_data_err),4))

            iBinCount += 1
            print("===========\n")

    del cfitPASS_Mu, cfitFAIL_Mu, cfitPASS_badbalance_Mu, cfitFAIL_badbalance_Mu, cfitPASS_El, cfitFAIL_El, cfitPASS_badbalance_El, cfitFAIL_badbalance_El

    xname = "Jet p_{T} [GeV]"
    yname = "Jet |#eta|"
    if doEtaBins:
        yname = "Jet #eta"

    heffmc.GetYaxis().SetTitle(yname)    
    heffmc.GetXaxis().SetTitle(xname)
    heffmc.GetXaxis().SetMoreLogLabels()

    heffdata.GetYaxis().SetTitle(yname)
    heffdata.GetXaxis().SetTitle(xname)
    heffdata.GetXaxis().SetMoreLogLabels()

    hmistagmc.GetYaxis().SetTitle(yname)
    hmistagmc.GetXaxis().SetTitle(xname)
    hmistagmc.GetXaxis().SetMoreLogLabels()

    hmistagdata.GetYaxis().SetTitle(yname)
    hmistagdata.GetXaxis().SetTitle(xname)
    hmistagdata.GetXaxis().SetMoreLogLabels()

    heffgen.GetYaxis().SetTitle(yname)    
    heffgen.GetXaxis().SetTitle(xname)
    heffgen.GetXaxis().SetMoreLogLabels()

    hmistaggen.GetYaxis().SetTitle(yname)
    hmistaggen.GetXaxis().SetTitle(xname)
    hmistaggen.GetXaxis().SetMoreLogLabels()

    def PlotPtSlices(ptBins, h2, hNamePrefix, pdfName):
        h2C = h2.Clone(h2.GetName()+"Clone")
        #
        # Get Eff/Mistag/SF vs eta in pt slices 
        #
        histoDict = collections.OrderedDict()
        for i in range(0,len(_pt)):
            iBin = i+1
            hName = hNamePrefix+"_pt"+ptBins[i]+"_eta"
            histoDict[hName] = h2.ProjectionY(hName, iBin, iBin)

        canv   = ROOT.TCanvas("canv","canv",600,600)
        legend = None
        ymin   = None 
        ymax   = None
        doLogY = False
        if "mistag_mc" in h2.GetName() or "mistaggen_mc" in h2.GetName() or "mistag_data" in h2.GetName():
            legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
            ymin = 0.001
            ymax = 6.000
            doLogY = True
        if "eff_mc" in h2.GetName() or "effgen_mc" in h2.GetName() or "eff_data" in h2.GetName():
            legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
            ymin = 0.20
            ymax = 1.40
        if "eff_sf" in h2.GetName() or "effgen_sf" in h2.GetName():
            legend = ROOT.TLegend(0.40,0.72,0.60,0.88)
            ymin = 0.65
            ymax = 1.35
        if "mistag_sf" in h2.GetName() or "mistaggen_sf" in h2.GetName():
            legend = ROOT.TLegend(0.68,0.72,0.88,0.88)
            ymin = 0.0
            ymax = 2.5
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
            legend.AddEntry(h,(ptBins[iH].replace("To"," < pT < "))+" GeV", "lp")
            if iH == 0:
              h.Draw("PE0")
            else:
              h.Draw("PE0SAME")
            legend.Draw("same")
        if doLogY:
            canv.SetLogy()
        canv.SaveAs(pdfName)
        del canv

    textsize=1

    wpShort = workingpoint[0]
   
    c2 = ROOT.TCanvas("c2","c2",600,600)
    heffmc.SetMinimum(0.4)
    heffmc.SetMaximum(1.0)
    heffmc.SetMarkerSize(textsize)
    heffmc.Draw("colztexterr")
    c2.SaveAs(os.path.join(outputDir, "h2_eff_mc"+year+"_"+wpShort+".pdf"))
    if printPNG: c2.SaveAs(os.path.join(outputDir, "h2_eff_mc"+year+"_"+wpShort+".png"))
    heffmc.SetName("h2_eff_mc"+year+"_"+wpShort)
    heffmc.SaveAs(os.path.join(outputDir, "h2_eff_mc"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, heffmc, "h_eff_mc"+year+"_"+wpShort, os.path.join(outputDir, "h_eff_mc"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c3 = ROOT.TCanvas("c3","c3",600,600)
    heffdata.SetMinimum(0.4)
    heffdata.SetMaximum(1.0)
    heffdata.SetMarkerSize(textsize)
    heffdata.Draw("colztexterr")
    c3.SaveAs(os.path.join(outputDir, "h2_eff_data"+year+"_"+wpShort+".pdf"))
    if printPNG: c3.SaveAs(os.path.join(outputDir, "h2_eff_data"+year+"_"+wpShort+".png"))
    heffdata.SetName("h2_eff_data"+year+"_"+wpShort)
    heffdata.SaveAs(os.path.join(outputDir, "h2_eff_data"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, heffdata, "h_eff_data"+year+"_"+wpShort, os.path.join(outputDir, "h_eff_data"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c4 = ROOT.TCanvas("c4","c4",600,600)
    heffdata.Sumw2()
    heffmc.Sumw2()
    heffsf = heffdata.Clone("heffsf")
    heffsf.Divide(heffmc)
    heffsf.SetNameTitle("effsf","Efficiency SF, WP " +workingpoint+ ", "+year)
    heffsf.SetMaximum(1.20)
    heffsf.SetMinimum(0.80)
    heffsf.SetMarkerSize(textsize)
    heffsf.Draw("colztext")
    c4.SaveAs(os.path.join(outputDir, "h2_eff_sf"+year+"_"+wpShort+".pdf"))
    if printPNG: c4.SaveAs(os.path.join(outputDir, "h2_eff_sf"+year+"_"+wpShort+".png"))
    heffsf.SetName("h2_eff_sf"+year+"_"+wpShort)
    heffsf.SaveAs(os.path.join(outputDir, "h2_eff_sf"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, heffsf, "h_eff_sf"+year+"_"+wpShort, os.path.join(outputDir, "h_eff_sf"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c6 = ROOT.TCanvas("c6","c6",600,600)
    hmistagmc.SetMinimum(0.0)
    hmistagmc.SetMaximum(0.5)
    hmistagmc.SetMarkerSize(textsize)
    hmistagmc.Draw("colztexterr")
    c6.SaveAs(os.path.join(outputDir, "h2_mistag_mc"+year+"_"+wpShort+".pdf"))
    if printPNG: c6.SaveAs(os.path.join(outputDir, "h2_mistag_mc"+year+"_"+wpShort+".png"))
    hmistagmc.SetName("h2_mistag_mc"+year+"_"+wpShort)
    hmistagmc.SaveAs(os.path.join(outputDir, "h2_mistag_mc"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, hmistagmc, "h_mistag_mc"+year+"_"+wpShort, os.path.join(outputDir, "h_mistag_mc"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c7 = ROOT.TCanvas("c7","c7",600,600)
    hmistagdata.SetMinimum(0.0)
    hmistagdata.SetMaximum(0.5)
    hmistagdata.SetMarkerSize(textsize)
    hmistagdata.Draw("colztexterr")
    c7.SaveAs(os.path.join(outputDir, "h2_mistag_data"+year+"_"+wpShort+".pdf"))
    if printPNG: c7.SaveAs(os.path.join(outputDir, "h2_mistag_data"+year+"_"+wpShort+".png"))
    hmistagdata.SetName("h2_mistag_data"+year+"_"+wpShort)
    hmistagdata.SaveAs(os.path.join(outputDir, "h2_mistag_data"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, hmistagdata, "h_mistag_data"+year+"_"+wpShort, os.path.join(outputDir, "h_mistag_data"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c8 = ROOT.TCanvas("c8","c8",600,600)
    hmistagdata.Sumw2()
    hmistagmc.Sumw2()
    hmistagsf = hmistagdata.Clone("hmistagsf")
    hmistagsf.Divide(hmistagmc)
    hmistagsf.SetNameTitle("mistagsf","Mistag SF, WP " +workingpoint+ ", "+year)
    hmistagsf.SetMaximum(2.0)
    hmistagsf.SetMinimum(0.0)
    hmistagsf.SetMarkerSize(textsize)
    hmistagsf.Draw("colztexterr")
    c8.SaveAs(os.path.join(outputDir, "h2_mistag_sf"+year+"_"+wpShort+".pdf"))
    if printPNG: c8.SaveAs(os.path.join(outputDir, "h2_mistag_sf"+year+"_"+wpShort+".png"))
    hmistagsf.SetName("h2_mistag_sf"+year+"_"+wpShort)
    hmistagsf.SaveAs(os.path.join(outputDir, "h2_mistag_sf"+year+"_"+wpShort+".root"))
    PlotPtSlices(_pt, hmistagsf, "h_mistag_sf"+year+"_"+wpShort, os.path.join(outputDir, "h_mistag_sf"+year+"_"+wpShort+"_ptBins_eta.pdf"))
  
    c9 = ROOT.TCanvas("c9","c9",600,600)
    heffgen.SetMinimum(0.4)
    heffgen.SetMaximum(1.0)
    heffgen.SetMarkerSize(textsize)
    heffgen.Draw("colztexterr")
    c9.SaveAs(os.path.join(outputDir, "h2_effgen_mc"+year+"_"+wpShort+".pdf"))
    if printPNG: c9.SaveAs(os.path.join(outputDir, "h2_effgen_mc"+year+"_"+wpShort+".png"))
    heffgen.SetName("h2_effgen_mc"+year+"_"+wpShort)
    heffgen.SaveAs(os.path.join(outputDir, "h2_effgen_mc"+year+"_"+wpShort+".root"))
    # PlotPtSlices(_pt, heffgen, "h_effgen_mc"+year+"_"+wpShort, os.path.join(outputDir, "h_effgen_mc"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c10 = ROOT.TCanvas("c10","c10",600,600)
    hmistaggen.SetMinimum(0.0)
    hmistaggen.SetMaximum(0.5)
    hmistaggen.SetMarkerSize(textsize)
    hmistaggen.Draw("colztexterr")
    c10.SaveAs(os.path.join(outputDir, "h2_mistaggen_mc"+year+"_"+wpShort+".pdf"))
    if printPNG: c10.SaveAs(os.path.join(outputDir, "h2_mistaggen_mc"+year+"_"+wpShort+".png"))
    hmistaggen.SetName("h2_mistaggen_mc"+year+"_"+wpShort)
    hmistaggen.SaveAs(os.path.join(outputDir, "h2_mistaggen_mc"+year+"_"+wpShort+".root"))
    # PlotPtSlices(_pt, hmistaggen, "h_mistaggen_mc"+year+"_"+wpShort, os.path.join(outputDir, "h_mistaggen_mc"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c11 = ROOT.TCanvas("c11","c11",600,600)
    heffgen.Sumw2()
    heffgensf = heffdata.Clone("heffgensf")
    heffgensf.Divide(heffgen)
    heffgensf.SetNameTitle("effgensf","Efficiency(Gen) SF , WP " +workingpoint+ ", "+year)
    heffgensf.SetMaximum(1.20)
    heffgensf.SetMinimum(0.80)
    heffgensf.SetMarkerSize(textsize)
    heffgensf.Draw("colztexterr")
    c11.SaveAs(os.path.join(outputDir, "h2_effgen_sf"+year+"_"+wpShort+".pdf"))
    if printPNG: c11.SaveAs(os.path.join(outputDir, "h2_effgen_sf"+year+"_"+wpShort+".png"))
    heffgensf.SetName("h2_effgen_sf"+year+"_"+wpShort)
    heffgensf.SaveAs(os.path.join(outputDir, "h2_effgen_sf"+year+"_"+wpShort+".root"))
    # PlotPtSlices(_pt, heffsf, "h_effgen_sf"+year+"_"+wpShort, os.path.join(outputDir, "h_effgen_sf"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    c12 = ROOT.TCanvas("c12","c12",600,600)
    hmistaggen.Sumw2()
    hmistaggensf = hmistagdata.Clone("hmistaggesf")
    hmistaggensf.Divide(hmistaggen)
    hmistaggensf.SetNameTitle("histaggensf","Mistag(Gen) SF, WP " +workingpoint+ ", "+year)
    hmistaggensf.SetMaximum(2.0)
    hmistaggensf.SetMinimum(0.0)
    hmistaggensf.SetMarkerSize(textsize)
    hmistaggensf.Draw("colztexterr")
    c12.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".pdf"))
    if printPNG: c8.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".png"))
    hmistaggensf.SetName("h2_mistaggen_sf"+year+"_"+wpShort)
    hmistaggensf.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".root"))
    # PlotPtSlices(_pt, hmistaggensf, "h_mistaggen_sf"+year+"_"+wpShort, os.path.join(outputDir, "h_mistaggen_sf"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    del c2, c3, c4, c6, c7, c8, c9, c10, c11, c12
    
if __name__ == '__main__':
    main()
