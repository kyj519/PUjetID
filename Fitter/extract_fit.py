# Standard importts
import os,sys,socket,argparse
import os
import ROOT
import math
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

def MakeDPhiFit(
    h_dphi_genunmatched_PASS,h_dphi_genmatched_PASS,h_dphi_genunmatched_FAIL,h_dphi_genmatched_FAIL,
    h_dphi_PASS,h_dphi_FAIL, 
    h_dphi_genunmatched_PASS_badbalance,h_dphi_genmatched_PASS_badbalance,h_dphi_genunmatched_FAIL_badbalance,h_dphi_genmatched_FAIL_badbalance,
    h_dphi_PASS_badbalance,h_dphi_FAIL_badbalance, 
    outputDir, pt, eta, cfitPASS, cfitFAIL, cfitPASS_badbalance, cfitFAIL_badbalance, iBinCount, iBinTotal,
    isData=False, doEtaBins=False):
    
    print("Performing fits to extract efficiency and mistag rate") 
    print("entries in PASS histos "+str(h_dphi_genunmatched_PASS.GetEntries())+","+str(h_dphi_genmatched_PASS.GetEntries())+","+str(h_dphi_PASS.GetEntries())+","+str(h_dphi_PASS_badbalance.GetEntries()))
    print("entries in FAIL histos "+str(h_dphi_genunmatched_FAIL.GetEntries())+","+str(h_dphi_genmatched_FAIL.GetEntries())+","+str(h_dphi_FAIL.GetEntries())+","+str(h_dphi_FAIL_badbalance.GetEntries()))
    print("ptBin:"+pt) 
    print("etaBin:"+eta) 
    
    #
    # 
    #
    eff_gen    = -1.0
    mistag_gen = -1.0
    if isData == False:
        n_mc_real_pass = h_dphi_genmatched_PASS.Integral() + h_dphi_genmatched_PASS_badbalance.Integral()
        n_mc_real_fail = h_dphi_genmatched_FAIL.Integral() + h_dphi_genmatched_FAIL_badbalance.Integral()
        n_mc_pu_pass   = h_dphi_genunmatched_PASS.Integral() + h_dphi_genunmatched_PASS_badbalance.Integral()
        n_mc_pu_fail   = h_dphi_genunmatched_FAIL.Integral() + h_dphi_genunmatched_FAIL_badbalance.Integral()
        eff_gen    = n_mc_real_pass/(n_mc_real_pass+n_mc_real_fail)
        mistag_gen = n_mc_pu_pass/(n_mc_pu_pass+n_mc_pu_fail)
 

    #
    #Declare the observable
    #
    dphiZjet = ROOT.RooRealVar("dphiZjet","#Delta#phi(Z,jet)/#pi",0., 2.)
    #
    # Declare effcy and mistag
    #
    effcy    = ROOT.RooRealVar("effcy","effcy",  0.9, 0.,1.)
    mistag   = ROOT.RooRealVar("mistag","mistag",0.1, 0.,1.)
    
    ################# What follows concerns the first 4 templates (GOOD jet/Z pt balance) #################
    #
    # Total number of events of signal (=real jets) events and of PU (=pileup jets) events before applying PU ID
    #
    nbtot    = ROOT.RooRealVar("nbtot","nbtot",h_dphi_PASS.Integral() + h_dphi_FAIL.Integral())
    nbtotsig = ROOT.RooRealVar("nbtotsig","nbtotsig", 1., h_dphi_PASS.Integral() + h_dphi_FAIL.Integral() )
    nbtotpu  = ROOT.RooFormulaVar("nbtotpu","nbtot-nbtotsig",ROOT.RooArgList(nbtot,nbtotsig)) 
    #
    # Number of events from each category passing/failing the PU ID 
    #
    n_SIG_PASS = ROOT.RooFormulaVar("n_SIG_PASS","effcy*nbtotsig",     ROOT.RooArgList(effcy,nbtotsig))
    n_PU_PASS  = ROOT.RooFormulaVar("n_PU_PASS", "mistag*nbtotpu",     ROOT.RooArgList(mistag,nbtotpu))
    n_SIG_FAIL = ROOT.RooFormulaVar("n_SIG_FAIL","(1-effcy)*nbtotsig", ROOT.RooArgList(effcy,nbtotsig))
    n_PU_FAIL  = ROOT.RooFormulaVar("n_PU_FAIL", "(1-mistag)*nbtotpu", ROOT.RooArgList(mistag,nbtotpu))
    #
    # Import the data histograms
    #
    dh_dphiZjet_PASS = ROOT.RooDataHist("dh_dphiZjet_PASS", "dh_dphiZjet_PASS", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_PASS))
    dh_dphiZjet_FAIL = ROOT.RooDataHist("dh_dphiZjet_FAIL", "dh_dphiZjet_FAIL", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_FAIL))
    #
    # Define the pdf: 
    # First import the histos templates
    #
    dh_template_SIG_PASS = ROOT.RooDataHist("dh_template_SIG_PASS", "dh_template_SIG_PASS", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_PASS))
    dh_template_SIG_FAIL = ROOT.RooDataHist("dh_template_SIG_FAIL", "dh_template_SIG_FAIL", ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genmatched_FAIL))
    dh_template_PU_PASS  = ROOT.RooDataHist("dh_template_PU_PASS",  "dh_template_PU_PASS",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_PASS))
    dh_template_PU_FAIL  = ROOT.RooDataHist("dh_template_PU_FAIL",  "dh_template_PU_FAIL",  ROOT.RooArgList(dphiZjet), ROOT.RooFit.Import(h_dphi_genunmatched_FAIL))
    #
    # Now convert them to PDF:
    #
    pdf_template_SIG_PASS = ROOT.RooHistPdf("pdf_template_SIG_PASS", "pdf_template_SIG_PASS", ROOT.RooArgSet(dphiZjet), dh_template_SIG_PASS)
    pdf_template_SIG_FAIL = ROOT.RooHistPdf("pdf_template_SIG_FAIL", "pdf_template_SIG_FAIL", ROOT.RooArgSet(dphiZjet), dh_template_SIG_FAIL)
    pdf_template_PU_PASS  = ROOT.RooHistPdf("pdf_template_PU_PASS",  "pdf_template_PU_PASS",  ROOT.RooArgSet(dphiZjet), dh_template_PU_PASS)
    pdf_template_PU_FAIL  = ROOT.RooHistPdf("pdf_template_PU_FAIL",  "pdf_template_PU_FAIL",  ROOT.RooArgSet(dphiZjet), dh_template_PU_FAIL)
    #
    # The PU template is taken to be a flat (pol0) distribution
    #
    pol0_PU_PASS = ROOT.RooPolynomial("pol0_PU_PASS","pol0",dphiZjet, ROOT.RooArgList())
    pol0_PU_FAIL = ROOT.RooPolynomial("pol0_PU_FAIL","pol0",dphiZjet, ROOT.RooArgList())
    #
    # Smears the SIGNAL template with a Gaussian to allow for different phi resolution between data and simulation. 
    #
    # PASS
    gauss_mean_PASS  = ROOT.RooRealVar("mean_PASS","mean",0,-0.05,0.05)
    gauss_sigma_PASS = ROOT.RooRealVar("sigma_PASS","sigma gauss",0.02,0.001,0.2)
    gauss_PASS       = ROOT.RooGaussian("gauss_PASS","gauss", dphiZjet ,gauss_mean_PASS,gauss_sigma_PASS) 
    tmpxg_SIG_PASS   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS","template x gauss" ,dphiZjet, pdf_template_SIG_PASS , gauss_PASS)
    # FAIL
    gauss_mean_FAIL  = ROOT.RooRealVar("mean_FAIL","mean",0,-0.05,0.05)
    gauss_sigma_FAIL = ROOT.RooRealVar("sigma_FAIL","sigma gauss",0.02,0.001,0.2)
    gauss_FAIL       = ROOT.RooGaussian("gauss_FAIL","gauss", dphiZjet ,gauss_mean_FAIL,gauss_sigma_FAIL) 
    tmpxg_SIG_FAIL   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL , gauss_FAIL)
    #
    # Smears the PU template template with a Gaussian to allow for different phi resolution between data and simulation.  
    # Not needed if the template is a flat distribution.  
    #
    # PASS
    # gauss_mean_PU_PASS  = ROOT.RooRealVar("mean_PU_PASS","mean",0,-0.05,0.05)
    # gauss_sigma_PU_PASS = ROOT.RooRealVar("sigma_PU_PASS","sigma gauss",0.02,0.001,0.2)
    # gauss_PU_PASS       = ROOT.RooGaussian("gauss_PU_PASS","gauss", dphiZjet ,gauss_mean_PU_PASS,gauss_sigma_PU_PASS) 
    # tmpxg_PU_PASS       = ROOT.RooFFTConvPdf("tmpxg_PU_PASS","template x gauss" ,dphiZjet, pdf_template_PU_PASS , gauss_PU_PASS)
    # # FAIL
    # gauss_mean_PU_FAIL  = ROOT.RooRealVar("mean_PU_FAIL","mean",0,-0.05,0.05)
    # gauss_sigma_PU_FAIL = ROOT.RooRealVar("sigma_PU_FAIL","sigma gauss",0.02,0.001,0.2)
    # gauss_PU_FAIL       = ROOT.RooGaussian("gauss_PU_FAIL","gauss", dphiZjet ,gauss_mean_PU_FAIL,gauss_sigma_PU_FAIL) 
    # tmpxg_PU_FAIL       = ROOT.RooFFTConvPdf("tmpxg_PU_FAIL","template x gauss" ,dphiZjet, pdf_template_PU_FAIL , gauss_PU_FAIL)
    #
    # Convert to extended pdf 
    #
    extpdf_SIG_PASS = ROOT.RooExtendPdf("extpdf_SIG_PASS", "extpdf_SIG_PASS", tmpxg_SIG_PASS, n_SIG_PASS) 
    extpdf_SIG_FAIL = ROOT.RooExtendPdf("extpdf_SIG_FAIL", "extpdf_SIG_FAIL", tmpxg_SIG_FAIL, n_SIG_FAIL) 
    extpdf_PU_PASS  = ROOT.RooExtendPdf("extpdf_PU_PASS", "extpdf_PU_PASS",   pol0_PU_PASS,   n_PU_PASS)
    extpdf_PU_FAIL  = ROOT.RooExtendPdf("extpdf_PU_FAIL", "extpdf_PU_FAIL",   pol0_PU_FAIL,   n_PU_FAIL)
    #
    # PU+SIG PDF
    #
    extpdf_SIGandPU_PASS = ROOT.RooAddPdf("extpdf_SIGandPU_PASS", "Signal+PU PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS,extpdf_PU_PASS),ROOT.RooArgList(n_SIG_PASS,n_PU_PASS))
    extpdf_SIGandPU_FAIL = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL", "Signal+PU PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL,extpdf_PU_FAIL),ROOT.RooArgList(n_SIG_FAIL,n_PU_FAIL))

    
    ################# Same procedure for templates with BAD jet/Z pt balance ################# 
    #
    # Total number of events of signal (=real jets) events and of PU (=pileup jets) events before applying PU ID      
    #
    nbtot_badbalance    =  ROOT.RooRealVar("nbtot_badbalance","nbtot_badbalance",h_dphi_PASS_badbalance.Integral() + h_dphi_FAIL_badbalance.Integral())
    nbtotsig_badbalance =  ROOT.RooRealVar("nbtotsig_badbalance","nbtotsig_badbalance", 1., h_dphi_PASS_badbalance.Integral() + h_dphi_FAIL_badbalance.Integral())
    nbtotpu_badbalance  =  ROOT.RooFormulaVar("nbtotpu_badbalance","nbtot_badbalance-nbtotsig_badbalance",ROOT.RooArgList(nbtot_badbalance,nbtotsig_badbalance))
    #
    # Number of events from each category passing/failing the PU ID
    #
    n_SIG_PASS_badbalance = ROOT.RooFormulaVar("n_SIG_PASS_badbalance","effcy*nbtotsig_badbalance",ROOT.RooArgList(effcy,nbtotsig_badbalance))
    n_PU_PASS_badbalance  = ROOT.RooFormulaVar("n_PU_PASS_badbalance","mistag*nbtotpu_badbalance",ROOT.RooArgList(mistag,nbtotpu_badbalance))
    n_SIG_FAIL_badbalance = ROOT.RooFormulaVar("n_SIG_FAIL_badbalance","(1-effcy)*nbtotsig_badbalance",ROOT.RooArgList(effcy,nbtotsig_badbalance))
    n_PU_FAIL_badbalance  = ROOT.RooFormulaVar("n_PU_FAIL_badbalance","(1-mistag)*nbtotpu_badbalance",ROOT.RooArgList(mistag,nbtotpu_badbalance))
    #
    #Import the data histograms  
    #
    dh_dphiZjet_PASS_badbalance = ROOT.RooDataHist("dh_dphiZjet_PASS_badbalance"  ,"dh_dphiZjet_PASS_badbalance"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_PASS_badbalance))
    dh_dphiZjet_FAIL_badbalance = ROOT.RooDataHist("dh_dphiZjet_FAIL_badbalance"  ,"dh_dphiZjet_FAIL_badbalance"  ,ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_FAIL_badbalance))
    #
    # Define the pdf:                   
    # First import the histos templates
    #
    dh_template_SIG_PASS_badbalance  = ROOT.RooDataHist("dh_template_SIG_PASS_badbalance",  "dh_template_SIG_PASS_badbalance" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_PASS_badbalance))
    dh_template_SIG_FAIL_badbalance  = ROOT.RooDataHist("dh_template_SIG_FAIL_badbalance",  "dh_template_SIG_FAIL_badbalance" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genmatched_FAIL_badbalance))
    dh_template_PU_PASS_badbalance  = ROOT.RooDataHist("dh_template_PU_PASS_badbalance",  "dh_template_PU_PASS_badbalance" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_PASS_badbalance))
    dh_template_PU_FAIL_badbalance  = ROOT.RooDataHist("dh_template_PU_FAIL_badbalance",  "dh_template_PU_FAIL_badbalance" , ROOT.RooArgList(dphiZjet),ROOT.RooFit.Import(h_dphi_genunmatched_FAIL_badbalance))
    #
    # Now convert them to PDF:
    #
    pdf_template_SIG_PASS_badbalance = ROOT.RooHistPdf("pdf_template_SIG_PASS_badbalance", "pdf_template_SIG_PASS_badbalance", ROOT.RooArgSet(dphiZjet),dh_template_SIG_PASS_badbalance)
    pdf_template_SIG_FAIL_badbalance = ROOT.RooHistPdf("pdf_template_SIG_FAIL_badbalance", "pdf_template_SIG_FAIL_badbalance", ROOT.RooArgSet(dphiZjet),dh_template_SIG_FAIL_badbalance)
    pdf_template_PU_PASS_badbalance  = ROOT.RooHistPdf("pdf_template_PU_PASS_badbalance", "pdf_template_PU_PASS_badbalance",  ROOT.RooArgSet(dphiZjet),dh_template_PU_PASS_badbalance)
    pdf_template_PU_FAIL_badbalance  = ROOT.RooHistPdf("pdf_template_PU_FAIL_badbalance", "pdf_template_PU_FAIL_badbalance",  ROOT.RooArgSet(dphiZjet),dh_template_PU_FAIL_badbalance)
    #
    #The PU template is taken to be a flat (pol0) distribution   
    #
    pol0_PU_PASS_badbalance = ROOT.RooPolynomial("pol0_PU_PASS_badbalance","pol0",dphiZjet, ROOT.RooArgList());
    pol0_PU_FAIL_badbalance = ROOT.RooPolynomial("pol0_PU_FAIL_badbalance","pol0",dphiZjet, ROOT.RooArgList());
    #
    # Smears the SIGNAL template with a Gaussian to allow for different phi resolution between data and simulation. 
    #
    # PASS
    gauss_mean_PASS_badbalance  = ROOT.RooRealVar("mean_PASS_badbalance","mean",0,-0.05,0.05)
    gauss_sigma_PASS_badbalance = ROOT.RooRealVar("sigma_PASS_badbalance","sigma gauss",0.02,0.001,0.2)
    gauss_PASS_badbalance       = ROOT.RooGaussian("gauss_PASS_badbalance","gauss", dphiZjet ,gauss_mean_PASS_badbalance,gauss_sigma_PASS_badbalance)
    tmpxg_SIG_PASS_badbalance   = ROOT.RooFFTConvPdf("tmpxg_SIG_PASS_badbalance","template x gauss" ,dphiZjet, pdf_template_SIG_PASS_badbalance , gauss_PASS_badbalance)
    # FAIL
    gauss_mean_FAIL_badbalance  = ROOT.RooRealVar("mean_FAIL_badbalance","mean",0,-0.05,0.05)
    gauss_sigma_FAIL_badbalance = ROOT.RooRealVar("sigma_FAIL_badbalance","sigma gauss",0.02,0.001,0.2)
    gauss_FAIL_badbalance       = ROOT.RooGaussian("gauss_FAIL_badbalance","gauss", dphiZjet ,gauss_mean_FAIL_badbalance,gauss_sigma_FAIL_badbalance)
    tmpxg_SIG_FAIL_badbalance   = ROOT.RooFFTConvPdf("tmpxg_SIG_FAIL_badbalance","template x gauss" ,dphiZjet, pdf_template_SIG_FAIL_badbalance , gauss_FAIL_badbalance)
    #
    # Smears the PU template template with a Gaussian to allow for different phi resolution between data and simulation.  
    # Not needed if the template is a flat distribution.  
    #
    # PASS
    # gauss_mean_PU_PASS_badbalance  = ROOT.RooRealVar("mean_PU_PASS_badbalance","mean",0,-0.05,0.05)
    # gauss_sigma_PU_PASS_badbalance = ROOT.RooRealVar("sigma_PU_PASS_badbalance","sigma gauss",0.02,0.001,0.2)
    # gauss_PU_PASS_badbalance       = ROOT.RooGaussian("gauss_PU_PASS_badbalance","gauss", dphiZjet ,gauss_mean_PU_PASS_badbalance,gauss_sigma_PU_PASS_badbalance) 
    # tmpxg_PU_PASS_badbalance       = ROOT.RooFFTConvPdf("tmpxg_PU_PASS_badbalance","template x gauss" ,dphiZjet, pdf_template_PU_PASS_badbalance , gauss_PU_PASS_badbalance)
    # # FAIL
    # gauss_mean_PU_FAIL  = ROOT.RooRealVar("mean_PU_FAIL_badbalance","mean",0,-0.05,0.05)
    # gauss_sigma_PU_FAIL = ROOT.RooRealVar("sigma_PU_FAIL_badbalance","sigma gauss",0.02,0.001,0.2)
    # gauss_PU_FAIL       = ROOT.RooGaussian("gauss_PU_FAIL_badbalance","gauss", dphiZjet ,gauss_mean_PU_FAIL_badbalance, gauss_sigma_PU_FAIL_badbalance) 
    # tmpxg_PU_FAIL       = ROOT.RooFFTConvPdf("tmpxg_PU_FAIL_badbalance","template x gauss" ,dphiZjet, pdf_template_PU_FAIL_badbalance, gauss_PU_FAIL_badbalance)
    #
    # Convert to extended pdf 
    #
    extpdf_PU_PASS_badbalance    = ROOT.RooExtendPdf("extpdf_PU_PASS_badbalance", "extpdf_PU_PASS",   pol0_PU_PASS_badbalance,   n_PU_PASS_badbalance)
    extpdf_PU_FAIL_badbalance    = ROOT.RooExtendPdf("extpdf_PU_FAIL_badbalance", "extpdf_PU_FAIL",   pol0_PU_FAIL_badbalance,   n_PU_FAIL_badbalance)
    extpdf_SIG_PASS_badbalance   = ROOT.RooExtendPdf("extpdf_SIG_PASS_badbalance", "extpdf_SIG_PASS", tmpxg_SIG_PASS_badbalance, n_SIG_PASS_badbalance)
    extpdf_SIG_FAIL_badbalance   = ROOT.RooExtendPdf("extpdf_SIG_FAIL_badbalance", "extpdf_SIG_FAIL", tmpxg_SIG_FAIL_badbalance, n_SIG_FAIL_badbalance)

    #
    # PU+SIG PDF
    #
    extpdf_SIGandPU_PASS_badbalance = ROOT.RooAddPdf("extpdf_SIGandPU_PASS_badbalance", "Signal+PU PDF (PASS)", ROOT.RooArgList(extpdf_SIG_PASS_badbalance,extpdf_PU_PASS_badbalance),ROOT.RooArgList(n_SIG_PASS_badbalance,n_PU_PASS_badbalance))
    extpdf_SIGandPU_FAIL_badbalance = ROOT.RooAddPdf("extpdf_SIGandPU_FAIL_badbalance", "Signal+PU PDF (FAIL)", ROOT.RooArgList(extpdf_SIG_FAIL_badbalance,extpdf_PU_FAIL_badbalance),ROOT.RooArgList(n_SIG_FAIL_badbalance,n_PU_FAIL_badbalance))
    
    #
    # Now we are ready to perform the simultaneous fit to all distributions. 
    #
    sample = ROOT.RooCategory("sample","sample")
    sample.defineType("PASSsample")
    sample.defineType("FAILsample")
    sample.defineType("PASSsample_badbalance")
    sample.defineType("FAILsample_badbalance")
    
    combData = ROOT.RooDataHist("allevents","PASS+FAIL",
                                ROOT.RooArgList(dphiZjet),ROOT.RooFit.Index(sample),
                                ROOT.RooFit.Import("PASSsample",dh_dphiZjet_PASS),
                                ROOT.RooFit.Import("FAILsample",dh_dphiZjet_FAIL) ,
                                ROOT.RooFit.Import("PASSsample_badbalance",dh_dphiZjet_PASS_badbalance),
                                ROOT.RooFit.Import("FAILsample_badbalance",dh_dphiZjet_FAIL_badbalance)  
    );
    
    simultpdf = ROOT.RooSimultaneous("simultpdf","simultaneous pdf",sample)
    simultpdf.addPdf(extpdf_SIGandPU_PASS,"PASSsample")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL,"FAILsample")
    simultpdf.addPdf(extpdf_SIGandPU_PASS_badbalance,"PASSsample_badbalance")
    simultpdf.addPdf(extpdf_SIGandPU_FAIL_badbalance,"FAILsample_badbalance")
    
    # simultpdf.fitTo(combData,ROOT.RooFit.Save())
    # simultpdf.fitTo(combData,ROOT.RooFit.Save())

    simultpdf.fitTo(combData,ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))
    simultpdf.fitTo(combData,ROOT.RooFit.Save(), ROOT.RooFit.PrintLevel(-1))

    ROOT.gStyle.SetTitleStyle(0)
    ROOT.gStyle.SetTitleBorderSize(0)
    
    #
    # Plots the fits in PASS,GOOD frame. 
    #
    framePASS        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, GOOD Balance"))
    if isData:
        combData.plotOn(framePASS,ROOT.RooFit.Cut("sample==sample::PASSsample"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS,ROOT.RooFit.Cut("sample==sample::PASSsample"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS,ROOT.RooFit.Slice(sample,"PASSsample"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS,ROOT.RooFit.Slice(sample,"PASSsample"),ROOT.RooFit.Components("extpdf_PU_PASS"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed));
    framePASS.SetMaximum(framePASS.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,GOOD frame. 
    #
    frameFAIL        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, GOOD Balance"))
    if isData:
        combData.plotOn(frameFAIL,ROOT.RooFit.Cut("sample==sample::FAILsample"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL,ROOT.RooFit.Cut("sample==sample::FAILsample"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL,ROOT.RooFit.Slice(sample,"FAILsample"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL,ROOT.RooFit.Slice(sample,"FAILsample"),ROOT.RooFit.Components("extpdf_PU_FAIL"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))    
    frameFAIL.SetMaximum(frameFAIL.GetMaximum()*1.40)
    #
    # Plot the fit in PASS,BAD frame. 
    #
    framePASS_badbalance        = dphiZjet.frame(ROOT.RooFit.Title("PASS ID, BAD Balance"))
    if isData:
        combData.plotOn(framePASS_badbalance,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(framePASS_badbalance,ROOT.RooFit.Cut("sample==sample::PASSsample_badbalance"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))
    
    simultpdf.plotOn(framePASS_badbalance,ROOT.RooFit.Slice(sample,"PASSsample_badbalance"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(framePASS_badbalance,ROOT.RooFit.Slice(sample,"PASSsample_badbalance"),ROOT.RooFit.Components("extpdf_PU_PASS_badbalance"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    framePASS_badbalance.SetMaximum(framePASS_badbalance.GetMaximum()*1.40)
    #
    # Plot the fit in FAIL,BAD frame. 
    #
    frameFAIL_badbalance        = dphiZjet.frame(ROOT.RooFit.Title("FAIL ID, BAD Balance"))
    if isData:
        combData.plotOn(frameFAIL_badbalance,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),ROOT.RooFit.FillStyle(0))
    else:
        combData.plotOn(frameFAIL_badbalance,ROOT.RooFit.Cut("sample==sample::FAILsample_badbalance"),ROOT.RooFit.MarkerSize(0.7),ROOT.RooFit.MarkerStyle(20),ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2),ROOT.RooFit.FillStyle(0))

    simultpdf.plotOn(frameFAIL_badbalance,ROOT.RooFit.Slice(sample,"FAILsample_badbalance"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData));
    simultpdf.plotOn(frameFAIL_badbalance,ROOT.RooFit.Slice(sample,"FAILsample_badbalance"),ROOT.RooFit.Components("extpdf_PU_FAIL_badbalance"),ROOT.RooFit.ProjWData(ROOT.RooArgSet(sample),combData),ROOT.RooFit.LineStyle(ROOT.kDashed))
    frameFAIL_badbalance.SetMaximum(frameFAIL_badbalance.GetMaximum()*1.40)

    nentries_PASS = h_dphi_PASS.GetEntries()
    nentries_FAIL = h_dphi_FAIL.GetEntries()
    nentries_PASS_badbalance = h_dphi_PASS_badbalance.GetEntries()
    nentries_FAIL_badbalance = h_dphi_FAIL_badbalance.GetEntries()

    # Add chi2 info
    chi2_text = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text.SetTextAlign(11)
    chi2_text.AddText("#chi^{2} fit = %s" %round(framePASS.chiSquare(6),2))
    chi2_text.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS.getVal(),3), round(gauss_sigma_PASS.getError(),3)) )
    chi2_text.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL.getVal(),3), round(gauss_sigma_FAIL.getError(),3)) )
    chi2_text.AddText("Entries PASS "+"= {}".format(nentries_PASS))
    chi2_text.AddText("Entries FALL "+"= {}".format(nentries_FAIL))
    chi2_text.SetTextSize(0.03)
    chi2_text.SetTextColor(2)
    chi2_text.SetShadowColor(0)
    chi2_text.SetFillColor(0)
    chi2_text.SetLineColor(0)
    framePASS.addObject(chi2_text)
    frameFAIL.addObject(chi2_text)

    chi2_text_badbalance = ROOT.TPaveText(0.15,0.65,0.15,0.88,"NBNDC")
    chi2_text_badbalance.SetTextAlign(11)
    chi2_text_badbalance.AddText("#chi^{2} fit = %s" %round(framePASS.chiSquare(6),2))
    chi2_text_badbalance.AddText("Eff "+"= {} #pm {}".format(round(effcy.getVal(),3), round(effcy.getError(),3)))
    chi2_text_badbalance.AddText("Mistag "+"= {} #pm {}".format(round(mistag.getVal(),3), round(mistag.getError(),3)) )
    chi2_text_badbalance.AddText("Sigma PASS "+"= {} #pm {}".format(round(gauss_sigma_PASS_badbalance.getVal(),3), round(gauss_sigma_PASS_badbalance.getError(),3)) )
    chi2_text_badbalance.AddText("Sigma FAIL "+"= {} #pm {}".format(round(gauss_sigma_FAIL_badbalance.getVal(),3), round(gauss_sigma_FAIL_badbalance.getError(),3)) )
    chi2_text_badbalance.AddText("Entries PASS "+"= {}".format(nentries_PASS_badbalance))
    chi2_text_badbalance.AddText("Entries FALL "+"= {}".format(nentries_FAIL_badbalance))
    chi2_text_badbalance.SetTextSize(0.03)
    chi2_text_badbalance.SetTextColor(2)
    chi2_text_badbalance.SetShadowColor(0)
    chi2_text.SetFillColor(0)
    chi2_text_badbalance.SetLineColor(0)
    framePASS_badbalance.addObject(chi2_text_badbalance)
    frameFAIL_badbalance.addObject(chi2_text_badbalance)

    #
    #
    #
    # cfitPASS = ROOT.TCanvas("cfitPASS","cfitPASS",600,600)
    # cfitPASS.SetLogx(False)
    cfitPASS.cd()
    cfitPASS.Clear()
    framePASS.Draw()

    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.3*cfitPASS.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right                                                     

    if doEtaBins:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", MC")
    else:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", MC")

    latex2.Draw("same")
    framePASS.Print()
 
    legend = ROOT.TLegend(0.60,0.75,0.88,0.88)
    legend.SetFillColor(0);
    legend.SetLineColor(0);
    legend.Draw("same")
 
    #
    #
    #
    cfitFAIL.cd()
    cfitFAIL.Clear()
    frameFAIL.Draw()
    if doEtaBins:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", MC")
    else:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", MC")
    latex2.Draw("same")
    frameFAIL.Print()

    legend.Draw("same")

    #
    #
    #
    cfitPASS_badbalance.cd()
    cfitPASS_badbalance.Clear()
    framePASS_badbalance.Draw()
    if doEtaBins:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", MC")
    else:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", MC")
    latex2.Draw("same")
    framePASS_badbalance.Print()
    legend.Draw("same")

    #
    #
    #
    cfitFAIL_badbalance.cd()
    cfitFAIL_badbalance.Clear()
    frameFAIL_badbalance.Draw()
    if doEtaBins:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("neg","-").replace("pos","+").replace("p",".")+" < #eta_{jet} < "+eta.split("To")[1].replace("neg","-").replace("pos","+").replace("p",".")+ ", MC")
    else:
        if isData:        
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", Data")
        else:
            latex2.DrawLatex(0.89, 0.915,pt.split("To")[0]+" GeV < pT_{jet} < "+pt.split("To")[1]+" GeV, "+eta.split("To")[0].replace("p",".")+" < |#eta_{jet}| < "+eta.split("To")[1].replace("p",".")+ ", MC")

    latex2.Draw("same")
    frameFAIL_badbalance.Print()
    legend.Draw("same")

    fit_filename = "fit"
    typeStr = "data" if isData else "mc"
    
    pdfStr = "pdf"
    if iBinCount == 0: pdfStr = "pdf("
    elif iBinCount == iBinTotal-1: pdfStr = "pdf)"

    cfitPASS.SaveAs("{}/{}_PASS_GOODbal_{}.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL.SaveAs("{}/{}_FAIL_GOODbal_{}.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitPASS_badbalance.SaveAs("{}/{}_PASS_BADbal_{}.{}".format(outputDir,fit_filename,typeStr,pdfStr))
    cfitFAIL_badbalance.SaveAs("{}/{}_FAIL_BADbal_{}.{}".format(outputDir,fit_filename,typeStr,pdfStr))

    print("eff_fit  = " + str(effcy.getVal())) 
    print("eff_gen  = " + str(eff_gen)) 
    print("mistag_fit = " + str(mistag.getVal())) 
    print("mistag_gen = " + str(mistag_gen)) 

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
    parser.add_argument("--useNLO",    default=False,        action='store_true')
    parser.add_argument("--useHerwig", default=False,        action='store_true')
    parser.add_argument("--usePowheg", default=False,        action='store_true')
    parser.add_argument("--syst",      dest="syst",          default="", help="jerUp,jerDown,jesTotalUp,jesTotalDown", type=str)

    args = parser.parse_args()    
    
    inputDir  = args.input
    outputDir = args.output
    year = args.year 
    workingpoint = args.workingpoint
    useNLO = args.useNLO
    useHerwig = args.useHerwig
    usePowheg = args.usePowheg
    syst = args.syst

    # Make output directory if it does not exist
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    data_filename = ""
    mc_filename = ""

    if year == "2016":
        data_filename = inputDir+"/Histo_Data16.root"
        mc_filename   = inputDir+"/Histo_MC16_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MC16_DY_AMCNLO.root"
        if useHerwig: mc_filename   = inputDir+"/Histo_MC16_DY_MG_HW.root"
    elif year == "2017":
        data_filename = inputDir+"/Histo_Data17.root"
        mc_filename   = inputDir+"/Histo_MC17_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MC17_DY_AMCNLO.root"
        if useHerwig: mc_filename   = inputDir+"/Histo_MC17_DY_MG_HW.root"
    elif year == "2018":
        data_filename = inputDir+"/Histo_Data18.root"
        mc_filename   = inputDir+"/Histo_MC18_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MC18_DY_AMCNLO.root"
        if useHerwig: mc_filename   = inputDir+"/Histo_MC18_DY_MG_HW.root"
    elif year == "UL2017":
        data_filename = inputDir+"/Histo_DataUL17.root"
        mc_filename   = inputDir+"/Histo_MCUL17_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MCUL17_DY_AMCNLO.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL17_DY_MG_HW.root"
        # if usePowheg: mc_filename   = inputDir+"/Histo_MCUL17_DYToMuMu_PHG.root"
    elif year == "UL2018":
        data_filename = inputDir+"/Histo_DataUL18.root"
        mc_filename   = inputDir+"/Histo_MCUL18_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MCUL18_DY_AMCNLO.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL18_DY_MG_HW.root"
        # if usePowheg: mc_filename   = inputDir+"/Histo_MCUL18_DYToMuMu_PHG.root"
    elif year == "UL2016APV":
        data_filename = inputDir+"/Histo_DataUL16APV.root"
        mc_filename   = inputDir+"/Histo_MCUL16APV_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MCUL16APV_DY_AMCNLO.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16APV_DY_MG_HW.root"
        if usePowheg: mc_filename   = inputDir+"/Histo_MCUL16APV_DYToMuMu_PHG.root"
    elif year == "UL2016":
        data_filename = inputDir+"/Histo_DataUL16.root"
        mc_filename   = inputDir+"/Histo_MCUL16_DY_MG.root"
        if useNLO:    mc_filename   = inputDir+"/Histo_MCUL16_DY_AMCNLO.root"
        # if useHerwig: mc_filename   = inputDir+"/Histo_MCUL16_DY_MG_HW.root"
        if usePowheg: mc_filename   = inputDir+"/Histo_MCUL16_DYToMuMu_PHG.root"


    if syst != "":
        if  useHerwig or usePowheg:
            raise Exception("Can't specify systematics for Herwig/Powheg samples. Only LO and NLO samples.")
        else:
            mc_filename = mc_filename.replace(".root","_"+syst+".root")

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetMarkerSize(0.5)
    # ROOT.gStyle.SetOptLogx()

    f_data = ROOT.TFile(data_filename,"READ")
    f_mc   = ROOT.TFile(mc_filename,  "READ")
   
    #
    # Check both file is open
    #
    if not(f_data.IsOpen()):
        raise Exception('Cannot open data input histo file:' + data_filename)
    if not(f_mc.IsOpen()):
        raise Exception('Cannot open mc input histo file:' + mc_filename)
   
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
        xbins.append(float(ptBin.split("To")[0]))                                
        xbins.append(float(ptBin.split("To")[1]))  
    # etabin
    for etaBin in _eta:
        print etaBin
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
    ROOT.gStyle.SetPaintTextFormat("4.2f")

    cfitPASS = ROOT.TCanvas("cfitPASS","cfitPASS",600,600)
    cfitPASS.SetLogx(False)

    cfitFAIL = ROOT.TCanvas("cfitFAIL","cfitFAIL",600,600)
    cfitFAIL.SetLogx(False)

    cfitPASS_badbalance = ROOT.TCanvas("cfitPASS_badbalance","cfitPASS_badbalance",600,600)
    cfitPASS_badbalance.SetLogx(False)

    cfitFAIL_badbalance = ROOT.TCanvas("cfitFAIL_badbalance","cfitFAIL_badbalance",600,600)
    cfitFAIL_badbalance.SetLogx(False)

    iBinCount = 0
    iBinTotal = len(_pt) * len(_eta)
    
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
            h_dphi_mc_genunmatched_PASS = f_mc.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_failGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_genmatched_PASS   = f_mc.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+"_passGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_PASS              = f_mc.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_data_PASS            = f_data.Get("h_passNJetSel_probeJet_goodBal_passPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm")
            #
            # Retrieve histograms: FAIL ID, GOOD balance
            #
            h_dphi_mc_genunmatched_FAIL = f_mc.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_failGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_genmatched_FAIL   = f_mc.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+"_passGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_FAIL              = f_mc.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_data_FAIL            = f_data.Get("h_passNJetSel_probeJet_goodBal_failPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm")
            #
            # Retrieve histograms: PASS ID, BAD balance
            #
            h_dphi_mc_genunmatched_PASS_badbalance =  f_mc.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_failGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_genmatched_PASS_badbalance   =  f_mc.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+"_passGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_PASS_badbalance              =  f_mc.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_data_PASS_badbalance            =  f_data.Get("h_passNJetSel_probeJet_badBal_passPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm")
            #
            # Retrieve histograms: FAIL ID, BAD balance
            #
            h_dphi_mc_genunmatched_FAIL_badbalance = f_mc.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_failGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_genmatched_FAIL_badbalance   = f_mc.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+"_passGenMatch"+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_mc_FAIL_badbalance              = f_mc.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm"+systStr)
            h_dphi_data_FAIL_badbalance            = f_data.Get("h_passNJetSel_probeJet_badBal_failPUID"+workingpoint+binStr+"_probeJet_dilep_dphi_norm")
            #
            # Perform fit on MC
            #
            eff_mc,eff_mc_err,mistag_mc,mistag_mc_err,eff_gen,mistag_gen=MakeDPhiFit(
                h_dphi_mc_genunmatched_PASS,h_dphi_mc_genmatched_PASS,h_dphi_mc_genunmatched_FAIL,h_dphi_mc_genmatched_FAIL,
                h_dphi_mc_PASS,h_dphi_mc_FAIL, 
                h_dphi_mc_genunmatched_PASS_badbalance, h_dphi_mc_genmatched_PASS_badbalance, h_dphi_mc_genunmatched_FAIL_badbalance, h_dphi_mc_genmatched_FAIL_badbalance, 
                h_dphi_mc_PASS_badbalance, h_dphi_mc_FAIL_badbalance, 
                outputDir,_pt[i], _eta[j], cfitPASS, cfitFAIL, cfitPASS_badbalance, cfitFAIL_badbalance, iBinCount, iBinTotal,
                isData=False, doEtaBins=doEtaBins
            )
            heffmc.SetBinContent(i+1,j+1,    round(float(eff_mc),4))
            heffmc.SetBinError  (i+1,j+1,    round(float(eff_mc_err),4))
            hmistagmc.SetBinContent(i+1,j+1, round(float(mistag_mc),4))
            hmistagmc.SetBinError(i+1,j+1,   round(float(mistag_mc_err),4))
            heffgen.SetBinContent(i+1,j+1,    round(float(eff_gen),4))
            hmistaggen.SetBinContent(i+1,j+1, round(float(mistag_gen),4))

            #
            # Perform fit on Data
            #
            eff_data,eff_data_err,mistag_data,mistag_data_err=MakeDPhiFit(
                h_dphi_mc_genunmatched_PASS,h_dphi_mc_genmatched_PASS,h_dphi_mc_genunmatched_FAIL,h_dphi_mc_genmatched_FAIL,
                h_dphi_data_PASS,h_dphi_data_FAIL, 
                h_dphi_mc_genunmatched_PASS_badbalance,h_dphi_mc_genmatched_PASS_badbalance,h_dphi_mc_genunmatched_FAIL_badbalance,h_dphi_mc_genmatched_FAIL_badbalance,
                h_dphi_data_PASS_badbalance,h_dphi_data_FAIL_badbalance, 
                outputDir,_pt[i], _eta[j], cfitPASS, cfitFAIL, cfitPASS_badbalance, cfitFAIL_badbalance, iBinCount, iBinTotal,
                isData=True, doEtaBins=doEtaBins
            )
            heffdata.SetBinContent(i+1,j+1,    round(float(eff_data),4))
            heffdata.SetBinError  (i+1,j+1,    round(float(eff_data_err),4))
            hmistagdata.SetBinContent(i+1,j+1, round(float(mistag_data),4))
            hmistagdata.SetBinError(i+1,j+1,   round(float(mistag_data_err),4))

            iBinCount += 1
            print "==========="

    del cfitPASS, cfitFAIL, cfitPASS_badbalance, cfitFAIL_badbalance

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
    heffsf.Draw("colztexterr")
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
    c8.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".pdf"))
    if printPNG: c8.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".png"))
    hmistaggensf.SetName("h2_mistaggen_sf"+year+"_"+wpShort)
    hmistaggensf.SaveAs(os.path.join(outputDir, "h2_mistaggen_sf"+year+"_"+wpShort+".root"))
    # PlotPtSlices(_pt, hmistaggensf, "h_mistaggen_sf"+year+"_"+wpShort, os.path.join(outputDir, "h_mistaggen_sf"+year+"_"+wpShort+"_ptBins_eta.pdf"))

    del c2, c3, c4, c6, c7, c8, c9, c10, c11, c12
    
if __name__ == '__main__':
    main()
