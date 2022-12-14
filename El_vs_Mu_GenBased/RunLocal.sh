#!/bin/bash


ERALIST=(
UL18
UL17
UL16
UL16APV
)

python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/MakePlot.py --era ${ERALIST[$1]} --ncores 32 --doLogY &
python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/El_vs_Mu_GenBased/MakePlot.py --era ${ERALIST[$1]} --ncores 32

