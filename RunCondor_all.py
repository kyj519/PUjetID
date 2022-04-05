import htcondor
from datetime import datetime
import Analyzer.RunCondor_SkimNtuples as skimSubmitter
import Analyzer.RunCondor_MakeHistograms as histogramSubmitter
import Fitter.RunCondor_Fit as fitSubmitter
import Analyzer.haddhisto as haddHisto
import argparse

class params:
	def __init__(self):
		pass

