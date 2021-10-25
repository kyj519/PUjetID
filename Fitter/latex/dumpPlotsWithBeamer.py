import collections
import ROOT
import os

def main():

  version="results_ULNanoV9_v1p1"
  showFitInEachBin=True

  eras = [
    "UL2017",
    "UL2018",
    "UL2016APV",
  ]

  for year in eras:
    outFileName="DumpPlots_PUIDSF_"+version+"_Baseline_"+year
    inDir="../"+version+"/Baseline/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

    outFileName="DumpPlots_PUIDSF_"+version+"_NLO_"+year
    inDir="../"+version+"/NLO/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

    outFileName="DumpPlots_PUIDSF_"+version+"_jerUp_"+year
    inDir="../"+version+"/jerUp/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

    outFileName="DumpPlots_PUIDSF_"+version+"_jerDown_"+year
    inDir="../"+version+"/jerDown/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

    outFileName="DumpPlots_PUIDSF_"+version+"_jesTotalUp_"+year
    inDir="../"+version+"/jesTotalUp/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

    outFileName="DumpPlots_PUIDSF_"+version+"_jesTotalDown_"+year
    inDir="../"+version+"/jesTotalDown/"
    CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

  # eras = [
  #   "UL2016APV",
  #   "UL2016",
  # ]
  # for year in eras:
  #   outFileName="DumpPlots_PUIDSF_"+version+"_Powheg_"+year
  #   inDir="../"+version+"/Powheg/"
  #   CompilePlots(inDir, version, year, outFileName, showFitInEachBin)

def CompilePlots(inDir, version, year, outFileName, showFitInEachBin=True):
  
  ptBins = [
    ("20To25", "$20 < p_{T} < 25$"),
    ("25To30", "$25 < p_{T} < 30$"),
    ("30To40", "$30 < p_{T} < 40$"),
    ("40To50", "$40 < p_{T} < 50$"),
  ]

  # etaBins = [
  #  ("0p0To1p479", "$0.0 < |\\eta| < 1.479$"),
  #  ("1p479To2p0", "$1.479 < |\\eta| < 2.0$"),
  #  ("2p0To2p5"  , "$2.0 < |\\eta| < 2.5$"),
  #  ("2p5To2p75" , "$2.5 < |\\eta| < 2.75$"),
  #  ("2p75To3p0" , "$2.75 < |\\eta| < 3.0$"),
  #  ("3p0To5p0"  , "$3.0 < |\\eta| < 5.0$"),
  # ]

  etaBins = [
    ("neg5p0Toneg3p0",  "$-5.0 < |\\eta| < -3.0$"),
    ("neg3p0Toneg2p75", "$-3.0 < |\\eta| < -2.75$"),
    ("neg2p75Toneg2p5", "$-2.75 < |\\eta| < -2.5$"),
    ("neg2p5Toneg2p0",  "$-2.5 < |\\eta| < -2.0$"),
    ("neg2p0Toneg1p479","$-2.0 < |\\eta| < -1.479$"),
    ("neg1p479To0p0",   "$-1.479 < |\\eta| < 0.0$"),
    ("0p0Topos1p479",   "$0.0 < |\\eta| < 1.479$"),
    ("pos1p479Topos2p0","$1.479 < |\\eta| < 2.0$"),
    ("pos2p0Topos2p5",  "$2.0 < |\\eta| < 2.5$"),
    ("pos2p5Topos2p75", "$2.5 < |\\eta| < 2.75$"),
    ("pos2p75Topos3p0", "$2.75 < |\\eta| < 3.0$"),
    ("pos3p0Topos5p0",  "$3.0 < |\\eta| < 5.0$"),
  ]

  binList = []
  for ptBin in ptBins:
    for etaBin in etaBins:
      binList += [ 
        (ptBin[0]+"_"+etaBin[0], ptBin[1]+","+etaBin[1])
      ]

  WPYearList = []
  if year == "2016":
    WPYearList = [
      (inDir+"/2016_WPLoose",  "2016_Loose",  "2016 Loose WP"),
      (inDir+"/2016_WPMedium", "2016_Medium", "2016 Medium WP"),
      (inDir+"/2016_WPTight",  "2016_Tight",  "2016 Tight WP"),
    ]
  elif year == "2017":
    WPYearList = [
      (inDir+"/2017_WPLoose",  "2017_Loose",  "2017 Loose WP"),
      (inDir+"/2017_WPMedium", "2017_Medium", "2017 Medium WP"),
      (inDir+"/2017_WPTight",  "2017_Tight",  "2017 Tight WP"),
    ]
  elif year == "2018":
    WPYearList = [
      (inDir+"/2018_WPLoose",  "2018_Loose",  "2018 Loose WP"),
      (inDir+"/2018_WPMedium", "2018_Medium", "2018 Medium WP"),
      (inDir+"/2018_WPTight",  "2018_Tight",  "2018 Tight WP"),
    ]
  elif year == "UL2017":
    WPYearList = [
      (inDir+"/UL2017_WPLoose",  "UL2017_Loose",  "UL2017 Loose WP"),
      (inDir+"/UL2017_WPMedium", "UL2017_Medium", "UL2017 Medium WP"),
      (inDir+"/UL2017_WPTight",  "UL2017_Tight",  "UL2017 Tight WP"),
    ]
  elif year == "UL2018":
    WPYearList = [
      (inDir+"/UL2018_WPLoose",  "UL2018_Loose",  "UL2018 Loose WP"),
      (inDir+"/UL2018_WPMedium", "UL2018_Medium", "UL2018 Medium WP"),
      (inDir+"/UL2018_WPTight",  "UL2018_Tight",  "UL2018 Tight WP"),
    ]
  elif year == "UL2016APV":
    WPYearList = [
      (inDir+"/UL2016APV_WPLoose",  "UL2016APV_Loose",  "UL2016 APV Loose WP"),
      (inDir+"/UL2016APV_WPMedium", "UL2016APV_Medium", "UL2016 APV Medium WP"),
      (inDir+"/UL2016APV_WPTight",  "UL2016APV_Tight",  "UL2016 APV Tight WP"),
    ]
  elif year == "UL2016":
    WPYearList = [
      (inDir+"/UL2016_WPLoose",  "UL2016_Loose",  "UL2016 nonAPV Loose WP"),
      (inDir+"/UL2016_WPMedium", "UL2016_Medium", "UL2016 nonAPV Medium WP"),
      (inDir+"/UL2016_WPTight",  "UL2016_Tight",  "UL2016 nonAPV Tight WP"),
    ]

  outFile = open(outFileName+".tex","w")

  makeHeader(outFile)
  makeTemplates(outFile)
  makeBeginDocument(outFile)
  makeMainContent(outFile,WPYearList,binList, showFitInEachBin)
  makeEndDocument(outFile)
  outFile.close()

  os.system("pdflatex %s.tex"%(outFileName))
  os.system("pdflatex %s.tex"%(outFileName))
  os.system("rm -rvf *.aux *.lof *.log *.out *.toc *.nav *.snm")

  # EOSWWW="~/EOS/www/"
  # os.system("cp -v ./%s.pdf %s/"%(outFileName, EOSWWW))

def makeHeader(outFile):
  outFile.write("\\documentclass{beamer} \n")
  outFile.write("\\setbeamertemplate{footline}[frame number] \n")
  outFile.write("\\setbeamertemplate{frametitle}{ \n")
  outFile.write(" \\vspace{0.05mm} \n")
  outFile.write(" \\insertframetitle \n")
  outFile.write("}\n")
  outFile.write("\\setbeamertemplate{navigation symbols}{}\n")
  outFile.write("\\setbeamersize{text margin left=1.5mm,text margin right=0.2mm} \n")
  outFile.write("\\setbeamerfont{frametitle}{size=\\normalsize}\n")
  outFile.write("\n")
  outFile.write("\\usepackage{tabularx}\n")
  outFile.write("\\usepackage{graphicx}\n")
  outFile.write("\\usepackage{subcaption}\n")
  outFile.write("\\newcolumntype{C}{>{\centering\\arraybackslash}X}\n")
  outFile.write("\\usepackage{booktabs}\n")
  outFile.write("\\usepackage[labelformat=empty]{caption}\n")
  outFile.write("\\captionsetup{font=scriptsize,labelfont=scriptsize,justification=centering}\n")
  outFile.write("\n")
  outFile.write("\\renewcommand{\\arraystretch}{0.01}\n")
  outFile.write("\n")
  outFile.write("\\AtBeginSection[]{\n")
  outFile.write(" \\begin{frame}\n")
  outFile.write(" \\vfill\n")
  outFile.write(" \\centering\n")
  outFile.write(" \\begin{beamercolorbox}[sep=8pt,center,shadow=true,rounded=true]{title}\n")
  outFile.write("   \\usebeamerfont{title}\\insertsectionhead\\par%\n")
  outFile.write(" \\end{beamercolorbox}\n")
  outFile.write(" \\vfill\n")
  outFile.write(" \\end{frame}\n")
  outFile.write("}\n")


def makeTemplates(outFile):
  outFile.write("\n\n\n\n")
  outFile.write("\\newcommand{\\PlotsForEachBinDataAndMC}[3]\n")
  outFile.write("{\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{#3}\n")
  outFile.write("\\begin{figure}[t]\n")
  outFile.write("\\begin{minipage}[t]{0.49\\textwidth}%\n")
  outFile.write("\\centering\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_PASS_GOODbal_data}\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_FAIL_GOODbal_data}\\\\\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_PASS_BADbal_data}\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_FAIL_BADbal_data}\n")
  outFile.write("\\caption[]{Data}\n")
  outFile.write("\\end{minipage}%\n")
  outFile.write("{\\color{black}\\vrule\\hspace{4pt}}%\n")
  outFile.write("\\begin{minipage}[t]{0.49\\textwidth}%\n")
  outFile.write("\\centering\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_PASS_GOODbal_mc}\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_FAIL_GOODbal_mc}\\\\\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_PASS_BADbal_mc}\n")
  outFile.write("\\includegraphics[scale=0.16]{#1/fit_#2_FAIL_BADbal_mc}\n")
  outFile.write("\\caption[]{MC}\n")
  outFile.write("\\end{minipage}%\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("}\n")
  outFile.write("\n\n\n")
  outFile.write("\\newcommand{\\PlotsEffMistagSF}[3]\n")
  outFile.write("{\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Efficiency SF (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\includegraphics[width=0.72\\textwidth]{#1/h2_eff_sf_#2}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Efficiency in Data and MC (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\begin{minipage}[b]{0.49\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h2_eff_data_#2}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.49\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h2_eff_mc_#2}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Mistag SF (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\includegraphics[width=0.72\\textwidth]{#1/h2_mistag_sf_#2}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Mistag in Data and MC (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\begin{minipage}[b]{0.49\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h2_mistag_data_#2}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.49\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h2_mistag_mc_#2}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("}\n")
  outFile.write("\n\n\n")
  outFile.write("\\newcommand{\\PlotsEffMistagSFSlices}[3]\n")
  outFile.write("{\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Efficiency (Data, MC, SF) (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_eff_data_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_eff_mc_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_eff_sf_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("\\begin{frame}\n")
  outFile.write("\\frametitle{Mistag (Data, MC, SF) (#3)}\n")
  outFile.write("\\begin{figure}[ht]\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_mistag_data_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_mistag_mc_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\begin{minipage}[b]{0.31\\linewidth}\n")
  outFile.write("\\includegraphics[width=\\textwidth]{#1/h_mistag_sf_#2_ptBins_eta}\n")
  outFile.write("\\end{minipage}\n")
  outFile.write("\\end{figure}\n")
  outFile.write("\\end{frame}\n")
  outFile.write("}\n")
  outFile.write("\n\n\n")

def makeBeginDocument(outFile):
  outFile.write("\\begin{document}\n")
  outFile.write("\\begin{frame}{Overview}\n")
  outFile.write("\\tableofcontents[hideallsubsections]\n")
  outFile.write("\\end{frame}\n")

def makeMainContent(outFile,WPYearList,binList,showFitInEachBin=True):
  for WPYear in WPYearList:
    outFile.write("\\section{%s}\n" %WPYear[2])
    outFile.write("\\PlotsEffMistagSF{%s}{%s}{%s}\n" %(WPYear[0],WPYear[1],WPYear[2]))
    outFile.write("\\PlotsEffMistagSFSlices{%s}{%s}{%s}\n" %(WPYear[0],WPYear[1],WPYear[2]))
    if showFitInEachBin:
      for binEntry in binList:
        outFile.write("\\PlotsForEachBinDataAndMC{%s}{%s}{%s, %s}\n" %(WPYear[0],binEntry[0],binEntry[1],WPYear[2]))

def makeEndDocument(outFile):
  outFile.write("\\end{document}\n")

if __name__ == "__main__":
  main()
  