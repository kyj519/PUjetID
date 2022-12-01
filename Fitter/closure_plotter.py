import ROOT,os,array,uuid,itertools
ROOT.gStyle.SetOptStat(0)
etabin = array.array('d',[-5.0, -3.0,-2.75,-2.5,-2.0,-1.479,0.0,1.479,2.0,2.5,2.75,3.0, 5.0])
ptbin = array.array('d',[20.0,25.0,30.0,40.0,50.0])
def set_Style(hist1,hist2):
    hist1.SetMarkerStyle(ROOT.kOpenDiamond)
    hist2.SetMarkerStyle(ROOT.kOpenTriangleUp)
    hist1.SetMarkerColor(46)
    hist2.SetMarkerColor(38)
    hist1.SetLineColorAlpha(46,1)
    hist2.SetLineColorAlpha(38,0.7)
    hist1.SetMarkerSize(1.5)
    hist2.SetMarkerSize(1.5)
    hist1.SetLineWidth(2)
    hist2.SetLineWidth(2)
def get_legend(hist1,hist2,param):
    legend = ROOT.TLegend(0.70,0.72,0.90,0.88)
    legend.AddEntry(hist1,param['leg_str'][0])
    legend.AddEntry(hist2,param['leg_str'][1])
    return legend
def get_bound(hist1,hist2):
    return max(hist1.GetMaximum(),hist2.GetMaximum())*1.2, min(hist1.GetMinimum(),hist2.GetMinimum())*0.8
def make_not_exist_dir(path):
    if os.path.isdir(path):
        return
    else:
        os.makedirs(path)
def get_random_str():
    return str(uuid.uuid4())
def errtoHist(hist,binx,biny):
    binlist = get_binN(hist,binx,biny,sliced=False)
    new_hist = ROOT.TH2D(get_random_str(),get_random_str(),len(ptbin)-1,ptbin,len(etabin)-1,etabin)
    for n in binlist:
        err = hist.GetBinError(n)
        new_hist.SetBinContent(n,err)
    return new_hist
def get_binN(hist,binx,biny,sliced = True):
    if sliced:
        binSlice = {}
        for i in range(len(binx)-1):
            binSlice[i]=[]
            x = hist.GetXaxis().FindBin(binx[i]/2+binx[i+1]/2)
            for j in range(len(biny)-1):
                y = hist.GetYaxis().FindBin(biny[j]/2+biny[j+1]/2)
                binSlice[i].append(hist.GetBin(x,y))
        return binSlice
    else:
        binlist = []
        for i in range(len(binx)-1):
            for j in range(len(biny)-1):
                x = hist.GetXaxis().FindBin(binx[i]/2+binx[i+1]/2)
                y = hist.GetYaxis().FindBin(biny[j]/2+biny[j+1]/2)
                binlist.append(hist.GetBin(x,y))
        return binlist
def NtoStr(n,bin):
    return 'p_T %s to %s' % (bin[n],bin[n+1])
def get_compare_stack(hist1,hist2,errhist1,errhist2,binx,biny):
    binSlice = get_binN(hist1,binx,biny)
    stacks = []
    for key, item in binSlice.items():
        ptstr = NtoStr(key,ptbin)
        stack = []
        hist1_slice = ROOT.TH1D(ptstr+'_1',ptstr+'_1',len(etabin)-1,etabin)
        hist2_slice = ROOT.TH1D(ptstr+'_2',ptstr+'_2',len(etabin)-1,etabin)
        for i in range(len(item)):
            hist1_slice.SetBinContent(i+1,hist1.GetBinContent(item[i]))
            hist2_slice.SetBinContent(i+1,hist2.GetBinContent(item[i]))
            hist1_slice.SetBinError(i+1,errhist1.GetBinContent(item[i]))
            hist2_slice.SetBinError(i+1,errhist2.GetBinContent(item[i]))
        stack.append(hist1_slice)
        stack.append(hist2_slice)
        stacks.append(stack)
    return stacks
def draw_stack(file_1,file_2,histkey,save_path,param):
    save_path = os.path.join(save_path,histkey)
    make_not_exist_dir(save_path)
    hist1 = file_1.Get(histkey)
    hist2 = file_2.Get(histkey)
    errhist1 = file_1.Get(histkey+'_Systuncty_Total')
    errhist2 = file_2.Get(histkey+'_Systuncty_Total')
    if 'gen' in histkey:
        errhist1 = errtoHist(hist1,ptbin,etabin)
        errhist2 = errtoHist(hist2,ptbin,etabin)
        
    stacks = get_compare_stack(hist1,hist2,errhist1,errhist2,ptbin,etabin)
    c1 = ROOT.TCanvas("","",600,600)
    for n in range(len(stacks)):
        stack = stacks[n]
        namestr = NtoStr(n,ptbin)
        set_Style(stack[0],stack[1])
        ubound,lbound = get_bound(stack[0],stack[1])
        stack[0].SetMaximum(ubound)
        stack[0].SetMinimum(lbound)
        stack[1].SetMaximum(ubound)
        stack[1].SetMinimum(lbound)
        c1.cd()
        stack[0].Draw("PE1")
        stack[1].Draw("PE1 same")
        leg = get_legend(stack[0],stack[1],param)
        leg.SetFillStyle(0)
        leg.Draw('same')
        c1.Draw()
        c1.SaveAs(os.path.join(save_path,namestr + '.pdf'))
def get_histkey(what, isMC,era,wp):
    return 'h2_%s_%sUL%s_%s' %  (what, 'mc', era, wp) if isMC else 'h2_%s_%sUL%s_%s' %  (what, 'data', era, wp) 

if __name__ == "__main__":
    target_1 = '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Fitter/result/Muon_Single_Ch/method3/postprocessed/result.root'
    target_2 = '/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Fitter/result/Electron_Single_Ch/method3/postprocessed/result.root'
    file_1 = ROOT.TFile(target_1,'READ')
    file_2= ROOT.TFile(target_2,'READ')
    eras = ['2018','2017','2016APV','2016']
    whats = ['eff','effgen','mistag','mistaggen']
    wps = ['T','M','L']
    isMCs = [True,False]
    param = {}
    param['leg_str']=['Muon Ch.','Electron Ch.']
    for tup in itertools.product(whats,isMCs,eras,wps):
        if 'gen' in tup[0] and not tup[1]: 
            continue
        histkey = get_histkey(tup[0],tup[1],tup[2],tup[3])
        draw_stack(file_1,file_2,histkey,'./Plot',param)
        if tup[1]:
            draw_stack(file_1,file_2,histkey.replace('mc','sf'),'./Plot',param)
