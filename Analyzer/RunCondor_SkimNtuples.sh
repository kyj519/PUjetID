#!/bin/bash
NCORES=$2
#
# Make skimmed ntuples

export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert
export LD_PRELOAD="/usr/lib64/libpdcap.so"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib64/dcap"

python /u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Analyzer/SkimNtuples.py --sample $1 --cores $NCORES
echo NCORES=$NCORES