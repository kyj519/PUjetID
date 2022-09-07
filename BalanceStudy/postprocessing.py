import os, ROOT
import array

from attr import fields_dict

filelist = os.listdir('rawresult')
etabin = array.array('d',[-5.0, -3.0,-2.75,-2.5,-2.0,-1.479,0.0,1.479,2.0,2.5,2.75,3.0, 5.0])
ptbin = array.array('d',[20.0,25.0,30.0,40.0,50.0])

eras = ['18','17','16','16APV']
wps = ['T', 'M', 'L']
pfs = ['P','F']
whats = ['best_N_up','best_N_low', 'accuracy']
histdict = {}
for era in eras:
    for what in whats:
        histdict['%s_%s' % (era,what)] = ROOT.TH2D('UL20%s_%s' % (era,what),'UL20%s_%s' % (era,what),len(ptbin)-1,ptbin,len(etabin)-1,etabin)

for file in filelist:
    era = file.replace('.txt','').split('_')[0]
    binN = int(file.replace('.txt','').split('_')[1])
    line=''
    with open('rawresult/'+file,'r') as f:
        line = f.readline()
    bestN_up = float(line.split(' ')[0])
    bestN_low = float(line.split(' ')[1])
    accuracy = float(line.split(' ')[2])
    histdict['%s_%s' % (era,'best_N_up')].SetBinContent(binN,bestN_up)
    histdict['%s_%s' % (era,'best_N_low')].SetBinContent(binN,bestN_low)
    histdict['%s_%s' % (era,'accuracy')].SetBinContent(binN,accuracy)

filedict = {}

 
file = ROOT.TFile('balanceHist.root','RECREATE')
c = ROOT.TCanvas('','',1600,1600)

for histkey, hist in histdict.items():
    hist.Write()

 
file.Close()

for histkey, hist in histdict.items():
    c.Clear()
    c.cd()
    hist.Draw('COLZ TEXT')
    c.SaveAs('/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/BalanceStudy/balncePlot/%s.png'%histkey)