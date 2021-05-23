#
# combine all data histos into one root file
#
HISTODIR="histos3D"
hadd -f ${HISTODIR}/Histo_DataUL17.root ${HISTODIR}/Histo_DataUL17*.root

