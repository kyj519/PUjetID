#!/bin/bash
NCORES=4
export LD_PRELOAD=/usr/lib64/libXrdPosixPreload.so
SAMPLES=(
DataUL18A_DoubleMuon
MCUL18_DY_MG
# MCUL16_DY_MG # Still not available on 16/01/2022
)

#
# Make skimmed ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python SkimNtuples.py --sample $SAMPLE --cores $NCORES
done
