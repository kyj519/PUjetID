#!/bin/bash
NCORES=$2
#
# Make skimmed ntuples

export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert


python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Analyzer/SkimNtuples.py --sample $1 --cores $NCORES
echo NCORES=$NCORES