#
# combine all data histos into one root file
#
HISTODIR="histos3D"
hadd -f ${HISTODIR}/Histo_DataUL17.root ${HISTODIR}/Histo_DataUL17*_*.root
hadd -f ${HISTODIR}/Histo_DataUL18.root ${HISTODIR}/Histo_DataUL18*_*.root
hadd -f ${HISTODIR}/Histo_DataUL16APV.root ${HISTODIR}/Histo_DataUL16APV*_*.root
hadd -f ${HISTODIR}/Histo_DataUL16.root ${HISTODIR}/Histo_DataUL16[FGH]_*.root
