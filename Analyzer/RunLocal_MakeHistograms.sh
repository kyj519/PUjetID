#!/bin/bash
NCORES=4

SAMPLES=(
DataUL17B_DoubleMuon
DataUL17C_DoubleMuon
DataUL17D_DoubleMuon
DataUL17E_DoubleMuon
DataUL17F_DoubleMuon
MCUL17_DY_MG
MCUL17_DY_AMCNLO
DataUL18A_DoubleMuon
DataUL18B_DoubleMuon
DataUL18C_DoubleMuon
DataUL18D_DoubleMuon
MCUL18_DY_MG
MCUL18_DY_AMCNLO
DataUL16APVB_DoubleMuon
DataUL16APVC_DoubleMuon
DataUL16APVD_DoubleMuon
DataUL16APVE_DoubleMuon
DataUL16APVF_DoubleMuon
MCUL16APV_DY_MG
MCUL16APV_DY_AMCNLO
MCUL16APV_DYToMuMu_PHG
DataUL16F_DoubleMuon
DataUL16G_DoubleMuon
DataUL16H_DoubleMuon
MCUL16_DYToMuMu_PHG
)

#
# Make histograms from ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python MakeHistogramsHisto3D.py --sample $SAMPLE --cores $NCORES --useSkimNtuples
done
