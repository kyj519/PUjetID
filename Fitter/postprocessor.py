import argparse
import uuid
import ROOT
import os
import itertools
import array
import numpy as np

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
def make_not_exist_dir(path):
    if os.path.isdir(path):
        return
    else:
        os.makedirs(path)
    
def get_hist_f_path(era,wp,kind,syst,methodN):
    return os.path.join( folder_path,'method%s/NLO_%s' % (methodN,syst),'%s_WP%s'%(era,wp),'h2_%s%s_%s.root'%(kind,era,wp[0]))


def get_hist_key(era,wp,kind):
    return 'h2_%s%s_%s' % (kind, era, wp[0])

def iterBin(hist,binX,binY):
    binN = []
    for i in range(len(binX)-1):
        for j in range(len(binY)-1):
            binXn = hist.GetXaxis().FindBin((binX[i]+binX[i+1])/2)
            binYn = hist.GetYaxis().FindBin((binY[j]+binY[j+1])/2)
            binN.append(hist.GetBin(binXn,binYn,0))
            
    return binN
#############global varaibles#################
eras = ['UL2018', 'UL2017', 'UL2016', 'UL2016APV']
wps = ['Tight','Medium','Loose']
systs = ['jesTotal', 'jer']
etabin = array.array('d',[-5.0, -3.0,-2.75,-2.5,-2.0,-1.479,0.0,1.479,2.0,2.5,2.75,3.0, 5.0])
ptbin = array.array('d',[20.0,25.0,30.0,40.0,50.0])
allsyst = ['%s%s'%(tup[0],tup[1]) for tup in itertools.product(systs,['Up','Down'])]
allsyst.append('central')
kinds = ['%s_%s'%(tup[0],tup[1]) for tup in itertools.product(['eff','mistag'],['mc','data','sf'])]
folder_path = ""
final_root_path = ""
##############################################
   

def readFiles(folder_path,methodN):
    syst_hist_f={}
    syst_hist={}
    for key in allsyst: 
        syst_hist[key] = {}
        syst_hist_f[key] = {}
    
    syst_hist['gen'] = {}
    syst_hist['Systuncty_Total'] = {}
    syst_hist['fitUncty'] = {}
    syst_hist_f['gen'] = {}

    for tup in itertools.product(eras,wps,kinds):
        for syst in allsyst:
            syst_hist_f[syst][get_hist_key(tup[0],tup[1],tup[2])] = ROOT.TFile(get_hist_f_path(tup[0],tup[1],tup[2],syst,methodN),'READ')
            syst_hist[syst][get_hist_key(tup[0],tup[1],tup[2])] = syst_hist_f[syst][get_hist_key(tup[0],tup[1],tup[2])].Get(get_hist_key(tup[0],tup[1],tup[2]))
        if 'data' in tup[2]: continue
        syst_hist_f['gen'][get_hist_key(tup[0],tup[1],tup[2])] = ROOT.TFile(get_hist_f_path(tup[0],tup[1],tup[2],'central',methodN).replace('eff','effgen').replace('mistag','mistaggen'),'READ')
        syst_hist['gen'][get_hist_key(tup[0],tup[1],tup[2])] = syst_hist_f['gen'][get_hist_key(tup[0],tup[1],tup[2])].Get(get_hist_key(tup[0],tup[1],tup[2]).replace('eff','effgen').replace('mistag','mistaggen'))
        
        for key,item in syst_hist.items():
            for key2, item2 in item.items():
                item2.SetDirectory(0)
                
    return syst_hist

def combine_systerr(syst_hist):
    final_root = ROOT.TFile(final_root_path,'RECREATE')
    for key, item in syst_hist['central'].items():
        syst_hist['Systuncty_Total'][key] = ROOT.TH2F('%s_Systuncty_Total'% key,'%s_Systuncty_Total'% key,len(ptbin)-1,ptbin,len(etabin)-1,etabin)
        syst_hist['fitUncty'][key] = ROOT.TH2F('%s_fitUncty'% key,'%s_fitUncty'% key,len(ptbin)-1,ptbin,len(etabin)-1,etabin)
        syst_hist['Systuncty_Total'][key].SetMaximum(0.1)
        syst_hist['fitUncty'][key].SetMaximum(0.05)
        for binN in iterBin(syst_hist['Systuncty_Total'][key],ptbin,etabin):
            Systuncty_Total = 0
            for syst in systs:
                central = syst_hist['central'][key].GetBinContent(binN)
                up = syst_hist['%sUp'%syst][key].GetBinContent(binN)
                down = syst_hist['%sDown'%syst][key].GetBinContent(binN)
                maxUncty = max(np.abs(central-up),np.abs(central-down))
                Systuncty_Total = Systuncty_Total**2+maxUncty**2
                Systuncty_Total = np.sqrt(Systuncty_Total)
            staterr = syst_hist['central'][key].GetBinError(binN)
            syst_hist['fitUncty'][key].SetBinContent(binN,staterr)
            Systuncty_Total = Systuncty_Total**2 + staterr**2
            Systuncty_Total = np.sqrt(Systuncty_Total)
                
            syst_hist['Systuncty_Total'][key].SetBinContent(binN,Systuncty_Total)

        random_str = str(uuid.uuid4())
        c1 = ROOT.TCanvas(random_str,random_str,4800,1600)
        c1.Divide(3,1)
        c1.cd(1)
        syst_hist['central'][key].Draw('COLZ TEXT')
        c1.cd(2)
        syst_hist['Systuncty_Total'][key].Draw('COLZ TEXT')
        c1.cd(3)
        syst_hist['fitUncty'][key].Draw('COLZ TEXT')
        c1.Draw() 
        make_not_exist_dir(os.path.join(folder_path,'method%s/postprocessed/Plot'%methodN))
        c1.SaveAs(os.path.join(folder_path,'method%s/postprocessed/Plot'%methodN,key+'.png'))
        final_root.cd()
        syst_hist['Systuncty_Total'][key].Write()
        syst_hist['central'][key].Write()
        if not 'data' in key:
            syst_hist['gen'][key].Write()
    final_root.Close()
    
def condor_submit(target_path, methodN):
    submit_dic = {"executable": 'postprocessor.sh',
                  "arguments" : '%s %s' % (target_path, methodN),
    "jobbatchname": "PUJets_postprocessing",
    "universe":"vanilla",
    "request_cpus":1,
    "log":"postprocessor.log",
    "getenv":"True",
    "should_transfer_files":"YES",
    "when_to_transfer_output" : "ON_EXIT",
    "output": "postprocessor.out",
    "error" : "postprocessor.err",
    }

    sub = htcondor.Submit(submit_dic)
    schedd = htcondor.Schedd()         
    submit_result = schedd.submit(sub)  

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str)
    parser.add_argument('--methodN', type=int)
    parser.add_argument('--isCondor',type=int, default=0)
    args = parser.parse_args()
    folder_path = args.folder
    isCondor = args.isCondor
    folder_path = os.path.abspath(folder_path)
    print(folder_path)
    if isCondor:
        methodN = args.methodN
        syst_hist_dict = readFiles(folder_path,methodN)
        final_root_path = os.path.join(folder_path,'method%s/postprocessed/result.root'%methodN)
        make_not_exist_dir(os.path.join(folder_path,'method%s/postprocessed'%methodN))
        combine_systerr(syst_hist=syst_hist_dict)
    else:
        import htcondor
        for i in range(6):
            condor_submit(folder_path, i)
    
    
    
