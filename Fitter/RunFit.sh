#
# Directory path containing all the histogram rootfiles
#
INDIR="../Analyzer/histos3D/"
#
# Directory path for the output of the fits
#
OUTDIR="./results_ULNanoV9_v1p4/"

#############################################################################
#
#
#
#############################################################################
function RunFitterNLO {
  python extract_fit_v2.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit_v2.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit_v2.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPTight/  --year ${3} --wp Tight
}

function RunFitterNLOSyst {
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO_${4}/${3}_WPLoose/  --year ${3} --syst ${4} --wp Loose
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO_${4}/${3}_WPMedium/ --year ${3} --syst ${4} --wp Medium
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO_${4}/${3}_WPTight/  --year ${3} --syst ${4} --wp Tight
}

#
#
#
ERAS=(
UL2018
UL2017
UL2016
UL2016APV
)
for YEAR in ${ERAS[@]}
do
  RunFitterNLO ${INDIR} ${OUTDIR} ${YEAR}
  RunFitterNLOSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalUp
  RunFitterNLOSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalDown
done

#############################################################################
#
#
#
#############################################################################
function RunFitterLO {
  python extract_fit.py --input ${1} --output ${2}/LO/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --input ${1} --output ${2}/LO/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --input ${1} --output ${2}/LO/${3}_WPTight/  --year ${3} --wp Tight
}

function RunFitterLOSyst {
  python extract_fit.py --input ${1} --output ${2}/LO_${4}/${3}_WPLoose/  --year ${3} --syst ${4} --wp Loose
  python extract_fit.py --input ${1} --output ${2}/LO_${4}/${3}_WPMedium/ --year ${3} --syst ${4} --wp Medium
  python extract_fit.py --input ${1} --output ${2}/LO_${4}/${3}_WPTight/  --year ${3} --syst ${4} --wp Tight
}

#
#
#
# ERAS=(
# UL2018
# UL2017
# UL2016APV
# )
# for YEAR in ${ERAS[@]}
# do
#   RunFitterLO ${INDIR} ${OUTDIR} ${YEAR}
#   RunFitterLOSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalUp
#   RunFitterLOSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalDown
# done


#############################################################################
#
#
#
#############################################################################
function RunFitterPowheg {
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPTight/  --year ${3} --wp Tight
}
#
#
#
# ERAS=(
# UL2016APV
# UL2016
# )
# for YEAR in ${ERAS[@]}
# do
#   RunFitterPowheg ${INDIR} ${OUTDIR} ${YEAR}
# done

#############################################################################
#
#
#
#############################################################################
# function RunFitterHerwig {
#   python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPLoose/  --year ${3} --wp Loose
#   python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPMedium/ --year ${3} --wp Medium
#   python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPTight/  --year ${3} --wp Tight
# }

