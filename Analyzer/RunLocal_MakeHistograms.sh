#!/bin/bash
NCORES=4

SAMPLES=(
# MC16_DY_MG
# MC17_DY_MG
# MC18_DY_MG
# MC16_DY_AMCNLO
# MC17_DY_AMCNLO
# MC18_DY_AMCNLO
# MC16_DY_MG_HW
# MC17_DY_MG_HW
# MC18_DY_MG_HW
# Data16B_DoubleMuon
# Data16C_DoubleMuon
# Data16D_DoubleMuon
# Data16E_DoubleMuon
# Data16F_DoubleMuon
# Data16G_DoubleMuon
# Data16H_DoubleMuon
# Data17B_DoubleMuon
# Data17C_DoubleMuon
# Data17D_DoubleMuon
# Data17E_DoubleMuon
# Data17F_DoubleMuon
# Data18A_DoubleMuon
# Data18B_DoubleMuon
# Data18C_DoubleMuon
# Data18D_DoubleMuon
# Data16B_DoubleEG
# Data16C_DoubleEG
# Data16D_DoubleEG
# Data16E_DoubleEG
# Data16F_DoubleEG
# Data16G_DoubleEG
# Data16H_DoubleEG
# Data17B_DoubleEG
# Data17C_DoubleEG
# Data17D_DoubleEG
# Data17E_DoubleEG
# Data17F_DoubleEG
# Data18A_EGamma
# Data18B_EGamma
# Data18C_EGamma
# Data18D_EGamma
)
SAMPLES=(
MCUL17_DY_MG
# MCUL17_DY_AMCNLO
# DataUL17B_DoubleMuon
# DataUL17C_DoubleMuon
# DataUL17D_DoubleMuon
# DataUL17E_DoubleMuon
DataUL17F_DoubleMuon
)

#
# Make histograms from ntuples
#
for SAMPLE in ${SAMPLES[@]}
do
  python MakeHistograms.py  --sample $SAMPLE --cores $NCORES --useSkimNtuples --useNewTraining
  # python MakeHistogramsHisto3D.py  --sample $SAMPLE --cores $NCORES --useSkimNtuples --useNewTraining
done



