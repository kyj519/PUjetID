from curses import erasechar
import os
from re import I
from termios import N_TTY
import ROOT
import argparse
import array
import numpy as np
import itertools
ncore = 32
#######
####global params####
isPOG = True
N_lower_bound = 0.1
N_upper_bound = 0.8
lr = 0.2
#######
def getBalanceStr(N_up,N_down,isPOGStyle = False):
    if not isPOGStyle:
        goodbalFilterstr = '(probeJet_dilep_ptbalance<(1+%s*probeJet_jer_from_pt))&&(probeJet_dilep_ptbalance>(1-%s*probeJet_jer_from_pt))'%(N_up,N_down)
        badbalFilterstr = '(probeJet_dilep_ptbalance>(1+%s*probeJet_jer_from_pt))||(probeJet_dilep_ptbalance<(1-%s*probeJet_jer_from_pt))'%(N_up,N_down)
    else:
        goodbalFilterstr = '(probeJet_dilep_ptbalance<(1+%s))&&(probeJet_dilep_ptbalance>(1-%s))'%(N_up,N_down)
        badbalFilterstr = '(probeJet_dilep_ptbalance>(1+%s))||(probeJet_dilep_ptbalance<(1-%s))'%(N_up,N_down)
        
    return goodbalFilterstr, badbalFilterstr
def calc_accuracy(goodbal_matched, goodbal_unmatched, badbal_matched, badbal_unmatched):
    totalN = goodbal_matched + goodbal_unmatched + badbal_matched + badbal_unmatched

    return (goodbal_matched+badbal_unmatched)/totalN

def calc_f1(goodbal_matched, goodbal_unmatched, badbal_matched, badbal_unmatched):
    tp = goodbal_matched
    fp = goodbal_unmatched
    tn = badbal_unmatched
    fn = badbal_matched
    
    precision = tp/(tp+fp)
    sensitivity = tp/(tp+fn)
    
    return precision*sensitivity/(sensitivity+precision)
    
def get_accuracy( N_up, N_down, passdf, faildf):
        bins = array.array("d",[ii/50 for ii in range(61)])
        binsN = len(bins)-1
        histoinfo1d = ROOT.RDF.TH1DModel("Gen Matched","Gen Matched",binsN,bins)
        histoinfo1d2 = ROOT.RDF.TH1DModel("Gen Matched Fail","Gen Matched Fail",binsN,bins)
        goodbalFilterstr, badbalFilterstr = getBalanceStr(N_up, N_down,isPOGStyle=True) 
        genMatched_goodbalPtr = passdf.Filter(goodbalFilterstr).Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        genUnmatched_goodbalPtr = faildf.Filter(goodbalFilterstr).Histo1D(histoinfo1d2,"probeJet_pt_undoJER", "evtWeight")
        genMatched_badbalPtr = passdf.Filter(badbalFilterstr).Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        genUnmatched_badbalPtr = faildf.Filter(badbalFilterstr).Histo1D(histoinfo1d2,"probeJet_pt_undoJER", "evtWeight")
        
        genMatched_goodbal = genMatched_goodbalPtr.GetPtr()
        genUnmatched_goodbal = genUnmatched_goodbalPtr.GetPtr() 
        genMatched_badbal = genMatched_badbalPtr.GetPtr()
        genUnmatched_badbal = genUnmatched_badbalPtr.GetPtr()
        #genMatched = df.Filter('probeJet_passGenMatch').Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        #genUnmatched = df.Filter('!probeJet_passGenMatch').Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        accuracy = calc_accuracy(genMatched_goodbal.GetEntries(),genUnmatched_goodbal.GetEntries(),genMatched_badbal.GetEntries(),genUnmatched_badbal.GetEntries())
        
        return accuracy
    
def get_f1( N_up, N_down, passdf, faildf):
        bins = array.array("d",[ii/50 for ii in range(500)])
        binsN = len(bins)-1
        histoinfo1d = ROOT.RDF.TH1DModel("Gen Matched","Gen Matched",binsN,bins)
        histoinfo1d2 = ROOT.RDF.TH1DModel("Gen Matched Fail","Gen Matched Fail",binsN,bins)
        goodbalFilterstr, badbalFilterstr = getBalanceStr(N_up, N_down,isPOGStyle=True)  
        genMatched_goodbalPtr = passdf.Filter(goodbalFilterstr).Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        genUnmatched_goodbalPtr = faildf.Filter(goodbalFilterstr).Histo1D(histoinfo1d2,"probeJet_pt_undoJER", "evtWeight")
        genMatched_badbalPtr = passdf.Filter(badbalFilterstr).Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        genUnmatched_badbalPtr = faildf.Filter(badbalFilterstr).Histo1D(histoinfo1d2,"probeJet_pt_undoJER", "evtWeight")
        
        genMatched_goodbal = genMatched_goodbalPtr.GetPtr()
        genUnmatched_goodbal = genUnmatched_goodbalPtr.GetPtr() 
        genMatched_badbal = genMatched_badbalPtr.GetPtr()
        genUnmatched_badbal = genUnmatched_badbalPtr.GetPtr()
        #genMatched = df.Filter('probeJet_passGenMatch').Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        #genUnmatched = df.Filter('!probeJet_passGenMatch').Histo1D(histoinfo1d,"probeJet_pt_undoJER", "evtWeight")
        f1 =calc_f1(genMatched_goodbal.GetEntries(),genUnmatched_goodbal.GetEntries(),genMatched_badbal.GetEntries(),genUnmatched_badbal.GetEntries())
        
        return f1
    
def compute_N(era, pt1, pt2, eta1, eta2, binN):
    print(era)
    ROOT.ROOT.EnableImplicitMT(ncore)

    ntuple_path = '/gv0/Users/yeonjoon/ntuples/JetPUId_DiLeptonSkim_ULNanoV9_v1p4/ntuples_skim/'
    
    file_by_era={}
 
    njet = ['0','1','2']
    file_by_era[era]=[ntuple_path+'ntuple_MCUL'+era+'_DY_AMCNLO_'+ n+'J.root' for n in njet ]
    print(file_by_era)
    etabin = array.array('d',[-5.0, -3.0,-2.75,-2.5,-2.0,-1.479,0.0,1.479,2.0,2.5,2.75,3.0, 5.0])
    ptbin = array.array('d',[20.0,25.0,30.0,40.0,50.0])
   
    vec = ROOT.vector('string')()
    for file in file_by_era[era]: 
        print(file)
        vec.push_back(file)

    df = ROOT.RDataFrame('Events', vec)
    systStrPre  = ""
    systStrPost = ""
    systStr = ""
    probeJetStr=systStrPre+"jetSel0"

    df = df.Define("evtWeight","genWeight*eventWeightScale*puWeight*L1PreFiringWeight_Nom")
    weightName = "evtWeight"
    df = df.Define("isElEl","(abs(lep0_pdgId)==11)&&(abs(lep1_pdgId)==11)")
    df = df.Define("isMuMu","(abs(lep0_pdgId)==13)&&(abs(lep1_pdgId)==13)")
    df = df.Define("rho", "fixedGridRhoFastjetAll")
    #
    # Define the probeJet
    #
    

    
   
    df = df.Define("probeJet_passGenMatch", probeJetStr+"_gen_match")
    df = df.Define("probeJet_pt",             probeJetStr+"_pt")
    df = df.Define("probeJet_jer_corr", probeJetStr+"_jer_CORR")
    df = df.Define("probeJet_pt_undoJER",             "probeJet_pt/probeJet_jer_corr")
    df = df.Define("probeJet_eta",            probeJetStr+"_eta")
    df = df.Define("probeJet_abseta",         "fabs("+probeJetStr+"_eta)")
    df = df.Define("probeJet_phi",            probeJetStr+"_phi")
    df = df.Define("probeJet_dilep_dphi",     probeJetStr+"_dilep_dphi")
    df = df.Define("probeJet_puIdDisc",       probeJetStr+"_puIdDisc")
    df = df.Define("probeJet_jer_from_pt", probeJetStr+"_jer_from_pt")
    df = df.Define("probeJet_jer_from_pt_nom", probeJetStr+"_jer_from_pt_nom")
    df = df.Define("probeJet_jer_from_pt_nano", probeJetStr+"_jer_from_pt_nano")
    
    df = df.Define("probeJet_dilep_ptbalance","dilep_pt/probeJet_pt")
    df = df.Define("probeJet_dilep_ptbalance_anomaly", "fabs(probeJet_dilep_ptbalance-1)")
    if '16' in era:
        print('reverse bit oredering: era = %s' % era)
        df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 0)")
        df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
        df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 2)")
    else:
       
        df = df.Define("probeJet_puIdFlag_Loose", probeJetStr+"_puId & (1 << 2)")
        df = df.Define("probeJet_puIdFlag_Medium",probeJetStr+"_puId & (1 << 1)")
        df = df.Define("probeJet_puIdFlag_Tight", probeJetStr+"_puId & (1 << 0)")
        

    df = df.Define("probeJet_puIdLoose_pass",  "probeJet_puIdFlag_Loose")
    df = df.Define("probeJet_puIdMedium_pass", "probeJet_puIdFlag_Medium")
    df = df.Define("probeJet_puIdTight_pass",  "probeJet_puIdFlag_Tight")
    # if pf == 'P':
    #     if wp == 'L': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(probeJet_puIdLoose_pass)")
    #     elif wp == 'M': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(probeJet_puIdMedium_pass)")
    #     elif wp == 'T': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(probeJet_puIdTight_pass)") 
    # else:
    #     if wp == 'L': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(!probeJet_puIdLoose_pass)")
    #     elif wp == 'M': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(!probeJet_puIdMedium_pass)")
    #     elif wp == 'T': df_Filtered = df.Filter("(passOS)&&(passNJetSel)&&(!probeJet_puIdTight_pass)") 
    df_Filtered = df.Filter("(passOS)&&(passNJetSel)")
    
    Nlist = [0.5*n for n in range(1,3)]
    bins = array.array("d",[ii/50 for ii in range(61)])
    binsN = len(bins)-1
    histoinfo1d = ROOT.RDF.TH1DModel("Gen Matched","Gen Matched",binsN,bins)
    histoinfo1d2 = ROOT.RDF.TH1DModel("Gen Matched Fail","Gen Matched Fail",binsN,bins)
    balbins = array.array("d",[jj/50.0 for jj in range(100)])
    balbinsN = len(balbins)-1
    histoinfo1dbal = ROOT.RDF.TH1DModel("","",balbinsN,balbins)

    passdf = df_Filtered.Filter('(probeJet_passGenMatch) && (%s<probeJet_pt_undoJER) && (%s>probeJet_pt_undoJER) && (%s<probeJet_eta)&&(%s>probeJet_eta)' % (pt1, pt2, eta1, eta2))
    faildf = df_Filtered.Filter('(!probeJet_passGenMatch) && (%s<probeJet_pt_undoJER) && (%s>probeJet_pt_undoJER) && (%s<probeJet_eta)&&(%s>probeJet_eta)' % (pt1, pt2, eta1, eta2))
    balpass_ptr = passdf.Histo1D(histoinfo1dbal,"probeJet_dilep_ptbalance", "evtWeight")
    balfail_ptr = faildf.Histo1D(histoinfo1dbal,"probeJet_dilep_ptbalance", "evtWeight")
    balpass = balpass_ptr.GetPtr()
    balfail = balfail_ptr.GetPtr()
    balpass.SetLineColor(ROOT.kBlue)
    balfail.SetLineColor(ROOT.kRed)
    
    hs = ROOT.THStack("","")
    hs.Add(balpass)
    hs.Add(balfail)
    
    c = ROOT.TCanvas("","",1600,1600)
    c.cd()
    hs.Draw("hist e nostack")
    c.Draw()
    c.SaveAs(('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/BalanceStudy/Plot/%s_pt%sto%s_eta%sto%s'%(era,pt1,pt2,eta1,eta2)).replace('.','p')+'.png')
    bestN_up = 0
    bestN_down = 0
    bestAccuracy = 0
    gridN = 6
    tick = (N_upper_bound - N_lower_bound)/gridN
    Ngrid = [i*tick for i in range(1,gridN)]
    for N_tuple in itertools.product(Ngrid, Ngrid):
        accuracy = get_f1(N_tuple[0],N_tuple[1],passdf,faildf)
        if accuracy > bestAccuracy:
            bestN_down = N_tuple[1]
            bestN_up = N_tuple[0]
            bestAccuracy = accuracy

    Nlist_up = [bestN_up,bestN_up*1.001]
    Nlist_down = [bestN_down,bestN_down*1.001]
    
    acculist = []
   
    for iter in range(200):
        N_up = Nlist_up[iter]
        N_down = Nlist_down[iter]
        if N_up<N_lower_bound: 
            Nlist_up[iter] = N_lower_bound
            N_up = N_lower_bound
        
        if N_down<N_lower_bound: 
            Nlist_down[iter] = N_lower_bound
            N_down = N_lower_bound
            
        if N_up>N_upper_bound: 
            Nlist_up[iter] = N_upper_bound
            N_up = N_upper_bound
        if N_down>N_upper_bound: 
            Nlist_down[iter] = N_upper_bound
            N_down = N_upper_bound
        accuracy = get_f1(N_up,N_down,passdf,faildf)
        if accuracy > bestAccuracy:
            bestN_up = Nlist_up[iter]
            bestN_down = Nlist_down[iter]
            bestAccuracy = accuracy
        if iter == 0:
            acculist.append(accuracy)
        else:
            acculist.append(accuracy)
            if Nlist_up[iter]-Nlist_up[iter-1] == 0:
                dfdx = Nlist_up[iter] 
            else:
                dfdx = Nlist_up[iter]+lr*(accuracy-get_f1(Nlist_up[iter-1],N_down,passdf,faildf))/(Nlist_up[iter]-Nlist_up[iter-1])
                
                
            if Nlist_down[iter]-Nlist_down[iter-1] == 0:
                dfdy = Nlist_down[iter] 
            else:
                dfdy = Nlist_down[iter]+lr*(accuracy-get_f1(N_up,Nlist_down[iter-1],passdf,faildf))/(Nlist_down[iter]-Nlist_down[iter-1])
            Nlist_up.append(dfdx)
            Nlist_down.append(dfdy)
        print("iteration = %s, currnet N = %s,%s, accuarcy = %s" % (iter, N_up, N_down, acculist[iter]))
        if (abs(acculist[iter] - acculist[iter - 1]) < 1e-5) and iter != 0:
            break
        

                    
    print('eta %s to %s, pt %s to %s, best N is %s, %s, accuracy = %s' % (eta1, eta2, pt1, pt2, bestN_up, bestN_down, bestAccuracy))
    
    #f = ROOT.TFile("%s_%s.root"%(era,wp),'UPDATE')
    #n_hist = f.Get("best_N")
    #pur_hist = f.Get("best_pur")
    #n_hist.SetBinContent(binN,bestN)
    #pur_hist.SetBinContent(binN,bestAccuracy)
    #n_hist.Write()
    #pur_hist.Write()
    #f.Close()

    #f = open("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/BalanceStudy/rawresult/%s_%s_%s.txt"%(era,wp,binN), "w+")
    f = open("/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/BalanceStudy/rawresult/%s_%s_pt%sto%s_eta%sto%s.txt"%(era,binN,pt1,pt2,eta1,eta2), "w+")
    f.write("%s %s %s\n"%(bestN_up,bestN_down, bestAccuracy))
    f.close()
    
    
            

                    
def submit_condor():
    import htcondor
    eras = ['18','17','16APV','16']
    wps = ['T','M','L']
    pfs = ['P','F']
    etabin = array.array('d',[-5.0, -3.0,-2.75,-2.5,-2.0,-1.479,0.0,1.479,2.0,2.5,2.75,3.0, 5.0])
    ptbin = array.array('d',[20.0,25.0,30.0,40.0,50.0])
    best_n_hist = ROOT.TH2D("best_N","best_N",4,ptbin,12,etabin)
    accuracy_hist = ROOT.TH2D("best_pur","best_pur",4,ptbin,12,etabin)

    for i in range(best_n_hist.GetNcells()):
        best_n_hist.SetBinContent(i,999)
        accuracy_hist.SetBinContent(i,999)
    for era in eras:
        
        #f = ROOT.TFile("%s_%s.root"%(era,wp),'RECREATE')
        #best_n_hist.Write()
        #accuracy_hist.Write()
        #f.Close()
        for i in range(len(ptbin)-1):
            for j in range(len(etabin)-1):
                binXn = best_n_hist.GetXaxis().FindBin((ptbin[i]+ptbin[i+1])/2)
                binYn = best_n_hist.GetYaxis().FindBin((etabin[j]+etabin[j+1])/2)
                binN=best_n_hist.GetBin(binXn,binYn,0)
                submit_dic = {"executable": '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/BalanceStudy/balstudy.sh',
                "jobbatchname": "PUJets_balanceStudy_%s"%(era),
                #"jobbatchname": "PUJets_histo",	
                "universe":"vanilla",
                "request_cpus":ncore,
                "log":"log/%s/pt%sto%s_eta%sto%s.log"%(era,ptbin[i],ptbin[i+1],etabin[j],etabin[j+1]),
                "RequestMemory": 8192*2,
                "getenv":"True",
                "should_transfer_files":"YES",
                "when_to_transfer_output" : "ON_EXIT",
                "output": "out/%s/pt%sto%s_eta%sto%s.out"%(era,ptbin[i],ptbin[i+1],etabin[j],etabin[j+1]),
                "error" : "err/%s/pt%sto%s_eta%sto%s.err"%(era,ptbin[i],ptbin[i+1],etabin[j],etabin[j+1]),
                "arguments" : "%s %s %s %s %s %s" % (era, ptbin[i],ptbin[i+1],etabin[j],etabin[j+1],binN),
                "concurrency_limits" : 'n800.yeonjoon'
                }
                sub = htcondor.Submit(submit_dic)
                schedd = htcondor.Schedd()         
                submit_result = schedd.submit(sub)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--era', type=str)
    parser.add_argument('--wp', type=str)
    parser.add_argument('--pf', type=str)
    parser.add_argument('--pt1', type=str)
    parser.add_argument('--pt2', type=str)
    parser.add_argument('--eta1', type=str)
    parser.add_argument('--eta2', type=str)
    parser.add_argument('--binN', type=str)
    parser.add_argument('--isCondorjob', default = False, action='store_true')
    args = parser.parse_args()
    era = args.era
    isCondorjob = args.isCondorjob
    if isCondorjob:
        pt1 = float(args.pt1)
        pt2 = float(args.pt2)
        eta1 = float(args.eta1)
        eta2 = float(args.eta2)
        binN = int(args.binN)
    #     pf = args.pf
    
    if isCondorjob:
        compute_N(era,pt1,pt2,eta1,eta2,binN)
    else:
        os.system('rm -rf err/* out/* log/*')
        os.system('mkdir err/16 err/16APV err/17 err/18')
        os.system('mkdir log/16 log/16APV log/17 log/18')
        os.system('mkdir out/16 out/16APV out/17 out/18')
        os.system('rm -rf rawresult/*')
        submit_condor()