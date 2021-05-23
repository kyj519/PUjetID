#!/bin/bash
NCORES=4

SAMPLES=(
DataUL17B_DoubleMuon
DataUL17C_DoubleMuon
DataUL17D_DoubleMuon
DataUL17E_DoubleMuon
DataUL17F_DoubleMuon
DataUL17B_DoubleEG
DataUL17C_DoubleEG
DataUL17D_DoubleEG
DataUL17E_DoubleEG
DataUL17F_DoubleEG
MCUL17_DY_MG
MCUL17_DY_AMCNLO
)

#
# Make histograms from ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python MakeHistogramsHisto3D.py  --sample $SAMPLE --cores $NCORES --useSkimNtuples --useNewTraining
done



