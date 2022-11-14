#!/bin/bash


ERALIST=(
UL18
UL17
UL16
UL16APV
)

python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Validation/MakeHistograms.py --era ${ERALIST[$1]} --ncores 32

