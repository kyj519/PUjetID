#!/bin/bash
NCORES=4
export LD_PRELOAD=/usr/lib64/libpdcap.so
SAMPLES=(
'test'
# MCUL16_DY_MG # Still not available on 16/01/2022
)

#
# Make skimmed ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python /u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Analyzer/SkimNtuples.py --sample $SAMPLE --cores $NCORES
done
