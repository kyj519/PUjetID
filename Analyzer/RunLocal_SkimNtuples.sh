#!/bin/bash
NCORES=4
export LD_PRELOAD=/usr/lib64/libXrdPosixPreload.so
SAMPLES=(
DataUL17B_DoubleMuon
DataUL17C_DoubleMuon
DataUL17D_DoubleMuon
DataUL17E_DoubleMuon
DataUL17F_DoubleMuon
MCUL17_DY_MG
DataUL18A_DoubleMuon
DataUL18B_DoubleMuon
DataUL18C_DoubleMuon
DataUL18D_DoubleMuon
MCUL18_DY_MG
DataUL16APVB_DoubleMuon
DataUL16APVC_DoubleMuon
DataUL16APVD_DoubleMuon
DataUL16APVE_DoubleMuon
DataUL16APVF_DoubleMuon
MCUL16APV_DY_MG
DataUL16F_DoubleMuon
DataUL16G_DoubleMuon
DataUL16H_DoubleMuon
# MCUL16_DY_MG # Still not available on 16/01/2022
)

#
# Make skimmed ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python SkimNtuples.py --sample $SAMPLE --cores $NCORES
done
