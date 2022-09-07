import ROOT
import root_numpy as rnp
import numpy as np
import shutil, os


#loop over inside the TFile
#save all hist name
def getListOfNames(iFile):
  iFile.cd()
  return [ key.ReadObj().GetName() for key in ROOT.gDirectory.GetListOfKeys() ]


# find pattern h_passNJetSel_
histName1D            = lambda nameList: filter(lambda name: "h_passNJetSel_" in name, nameList )
	
# find pattern _passGenMatch_
histName_passGenMatch = lambda nameList: filter(lambda name: "_passGenMatch_" in name, nameList )

# find pattern _failGenMatch_
histName_failGenMatch = lambda nameList: filter(lambda name: "_failGenMatch_" in name, nameList )

# get list of histograms
getListOfHist         = lambda iFile, nameList: [ (name, iFile.Get(name)) for name in nameList ]


# symmetrize bins if it has negatives
def symmetrizeNegativeBins(hist):
  print(hist.GetName())
  outHist = hist.Clone()
  harray = rnp.hist2array(outHist, copy=False, include_overflow=True).T.flat
  sumw2  = rnp.array(outHist.GetSumw2(), copy=False).flat

  nBinsX = len(harray)
  if nBinsX % 2 == 1:
    raise Exception("hist: " + hist.GetName() + " dose not has even number binning!!")
 
  # negative bin mask
  neg_bin_mask = harray < 0.
  neg_bin_mask_fliped = np.flip(neg_bin_mask)
 
  # symmetrize negative bin mask
  neg_bin_mask_sym = neg_bin_mask + neg_bin_mask_fliped

  neg_harray =  harray * neg_bin_mask_sym
  neg_harray_fliped = np.flip(neg_harray)

  neg_sumw2  = sumw2 * neg_bin_mask_sym
  neg_sumw2_fliped  = np.flip(neg_sumw2)
  # take average
  avg_neg_harray = (neg_harray + neg_harray_fliped) / 2.
  avg_neg_sumw2  = (neg_sumw2 + neg_sumw2_fliped ) / 2.

  
  # add symmetrized negative bins and positive bins
  pos_harray = harray * (neg_bin_mask_sym == False)
  for i in range(len(harray)):
    harray[i] = pos_harray[i] + avg_neg_harray[i]


  pos_sumw2  = sumw2 * (neg_bin_mask_sym == False )
  for i in range(len(sumw2)):
    sumw2[i]  = pos_sumw2[i] + avg_neg_sumw2[i]

  

  return outHist


# average out nearby bins
def avgNearNegativeBins(hist):

  
  outHist = hist.Clone()
  harray = rnp.hist2array(outHist, copy=False, include_overflow=True).T.flat
  sumw2  = rnp.array(outHist.GetSumw2(), copy=False).flat

  indices = (harray[:] < 0.)
  for i in range(len(indices)):
    # skip first and last bin
    if i==0:
      continue
    elif (i+1) == len(indices):
      continue
    
    index      = indices[i]
    index_prev = indices[i-1]
    index_next = indices[i+1]


    # index == True
    if not index:
      continue

    # no nearby negative bins
    if int(index) + int(index_prev) + int(index_next) > 1:
      continue

    # average nearby three bins
    avg_value  = (harray[i-1] + harray[i] + harray[i+1]) / 3.
    harray[i-1] = avg_value
    harray[i]   = avg_value
    harray[i+1] = avg_value

    sumw2_curr = sumw2[i]
    sumw2_prev = sumw2[i-1]
    sumw2_next = sumw2[i+1]

    avg_sumw2   = (sumw2_curr + sumw2_prev + sumw2_next) / 3.
    sumw2[i]    = avg_sumw2
    sumw2[i-1]  = avg_sumw2
    sumw2[i+1]  = avg_sumw2

  return outHist

  #harray = rnp.hist2array(hist, copy=True)

  #nBinsX = harray.size
  #if nBinsX % 2 == 1:
  #  raise Exception("hist: " + hist.GetName() + " dose not has even number binning!!")

  ## negative bin mask
  #neg_bin_mask = harray < 0.
  #neg_bin_mask_rolled = np.roll(neg_bin_mask,1)
  #neg_bin_mask_rolled[-1] = False

  ## fine subsequent negative bins
  #neg_bin_mask_conv2 = np.convolve(neg_bin_mask, np.ones(2), mode='same' )
  #if np.sum(neg_bin_mask_conv2 == 2.) > 0.:
  #  print("hist: " + hist.GetName() + "has two adjacent negative bins")
  #  print("skip!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
  #  return hist
  #neg_bin_mask_conv2[-1] = False

  ##neg_bin_mask_conv3 = np.convolve(neg_bin_mask, np.ones(2, dtype=bool), mode='same' )
  ##neg_bin_mask_conv = np.roll(neg_bin_mask_conv, 1)

  #harray_conv = np.convolve(harray, np.ones(2)/2., mode='same' )
  #harray_conv_rolled = np.roll(harray_conv, 1)

  #avg_neg_harray = (harray_conv * neg_bin_mask) + (harray_conv_rolled * neg_bin_mask_rolled)
  #pos_haddry     = harray * ((neg_bin_mask + neg_bin_mask_rolled) == False)

  #avg_harray     = avg_neg_harray + pos_haddry
  #
  ##print(neg_bin_mask)
  ##print(neg_bin_mask_conv2.astype(bool))

  #outHist = hist.Clone()
  #outHist = rnp.array2hist(avg_harray, outHist)

  #return outHist


def fixForceNegativeBins(hist):
  
  outHist = hist.Clone()
  harray = rnp.hist2array(outHist, copy=False, include_overflow=True).T.flat
  sumw2 = rnp.array(outHist.GetSumw2(), copy=False).flat
  sumw  = np.sqrt(sumw2)

  indices = np.nonzero( (harray[:] < 0.) * ( (harray[:] + sumw) > 0.) )[0]
  if not indices.size == 0:

    #fix uncertainty
    for index in indices:
      sumw2[index]  = harray[index] + sumw[index]
    #set zero  
    harray[indices] = 0.

  return outHist


def saveHistogram(outFile, hist_list1, hist_list2):

  outFile.cd()


  for _, hist1 in hist_list1:
    hist1.Write()

  for _, hist2 in hist_list2:
    hist2.Write()
  
  #save after add two hist: failGenMatched, passGenMatched
  
  removePattern = lambda x: x.replace("_passGenMatch","").replace("_failGenMatch","")
  mergeHist_list1 = [ (removePattern(name), hist1) for name, hist1 in hist_list1  ]
  mergeHist_list2 = [ (removePattern(name), hist2) for name, hist2 in hist_list2  ]
  mergeHist_list  = [ (name1, hist1, hist2) for name1, hist1 in mergeHist_list1 for name2, hist2 in mergeHist_list2 if name1 == name2  ]


  for name, hist1, hist2 in mergeHist_list:
    mergedHist = hist1.Clone(name)
    mergedHist.Add(hist2)
    mergedHist.Write()


def saveComparison(outFile, hist_list1, hist_list2, orig_hist_list1, orig_hist_list2):
  ROOT.gROOT.SetBatch(True)
  outFile.cd()
  outFile.mkdir("comparison")
  outFile.cd("comparison")


  pair_hist_list1 = [ (name1, hist1, hist2) for name1, hist1 in hist_list1 for name2, hist2 in orig_hist_list1 if name1==name2 ]
  pair_hist_list2 = [ (name1, hist1, hist2) for name1, hist1 in hist_list2 for name2, hist2 in orig_hist_list2 if name1==name2 ]

  for name1, hist1, hist2 in pair_hist_list1 + pair_hist_list2:
    canvas = ROOT.TCanvas(name1, name1, 800, 600)
    canvas.cd()

    hist2.SetLineColor(ROOT.kBlue)
    hist2.Draw()


    hist1.SetLineColor(ROOT.kRed)
    hist1.Draw("same")

    canvas.Write()
    canvas.Close()

  
  #save after add two hist: failGenMatched, passGenMatched
  
  removePattern = lambda x: x.replace("_passGenMatch","").replace("_failGenMatch","")
  mergeHist_list1 = [ (removePattern(name), hist1, hist2) for name, hist1, hist2 in pair_hist_list1 ]
  mergeHist_list2 = [ (removePattern(name), hist3, hist4) for name, hist3, hist4 in pair_hist_list2 ]
  mergeHist_list  = [ (name1, hist1, hist2, hist3, hist4) for name1, hist1, hist2 in mergeHist_list1 for name2, hist3, hist4 in mergeHist_list2 if name1 == name2 ]


  for name, hist1, hist2, hist3, hist4 in mergeHist_list:
    canvas = ROOT.TCanvas(name, name, 800, 600)
    canvas.cd()

    mergedHist1 = hist1.Clone(name)
    mergedHist1.Add(hist3)
    mergedHist2 = hist2.Clone(name)
    mergedHist2.Add(hist4)

    mergedHist1.SetLineColor(ROOT.kRed)
    mergedHist1.Draw()
    mergedHist2.SetLineColor(ROOT.kBlue)
    mergedHist2.Draw("same")

    canvas.Write()
    canvas.Close()


def negativeSuppressor(inputFileName, conserveOriginal = True):
  outFileName   = inputFileName.replace(".root","") + "_suppressNegatives" + ".root"

  inputFile = ROOT.TFile(inputFileName, "READ")
  outFile = ROOT.TFile(outFileName, "RECREATE")


  exampleRun = False
  saveHist   = True
  if exampleRun:
    hist = inputFile.Get("h_passNJetSel_probeJet_badBal_passPUIDTight_failGenMatch_etaneg1p479To0p0_pt40To50_probeJet_dilep_dphi_norm")
    outHist = symmetrizeNegativeBins(hist)
    outHist = avgNearNegativeBins(outHist)
    outHist = fixForceNegativeBins(outHist)

    #c1 = ROOT.TCanvas("c1","c1",800,600)
    #c2 = ROOT.TCanvas("c2","c2",800,600)
    #c1.cd()
    hist.Draw("")
    #c2.cd()
    outHist.SetLineColor(ROOT.kRed)
    outHist.Draw("same")

  if saveHist:
    #get histogram name list
    histName_list = histName1D(getListOfNames(inputFile))
    histName_list_passGenMatched = histName_passGenMatch(histName_list)
    histName_list_failGenMatched = histName_failGenMatch(histName_list)
    #get histogram from file
    hist_list_passGenMatched     = getListOfHist(inputFile, histName_list_passGenMatched)
    hist_list_failGenMatched     = getListOfHist(inputFile, histName_list_failGenMatched)

    #suppress negative bin histograms
    targetFcn = lambda x : fixForceNegativeBins( avgNearNegativeBins(  symmetrizeNegativeBins(  x  )  )  )
    outHist_list_passGenMatched = [ (name, targetFcn(hist)) for name, hist in hist_list_passGenMatched ]
    outHist_list_failGenMatched = [ (name, targetFcn(hist)) for name, hist in hist_list_failGenMatched ]

    #save histogram
    saveHistogram(outFile, outHist_list_passGenMatched, outHist_list_failGenMatched)
    saveComparison(outFile, outHist_list_passGenMatched, outHist_list_failGenMatched, hist_list_passGenMatched, hist_list_failGenMatched)
    if not conserveOriginal:
      shutil.move(inputFileName, inputFileName.replace(".root",".old"))
      os.remove(inputFileName.replace(".root",".old"))
      shutil.move(outFileName,inputFileName)
       

