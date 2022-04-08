#!/bin/bash
NCORES=$2
balanceN=$3
#
# Make skimmed ntuples


python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Analyzer/MakeHistogramsHisto3D.py --sample $1 --cores $2 --balanceN $3 --Ch $4 --useSkimNtuples
