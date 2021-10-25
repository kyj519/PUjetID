#
# Directory path containing all the histogram rootfiles
#
INDIR="../Analyzer/histos3D/"
#
# Directory path for the output of the fits
#
OUTDIR="./results_ULNanoV9_v1p1/"

function RunFitter {
  python extract_fit.py --input ${1} --output ${2}/Baseline/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --input ${1} --output ${2}/Baseline/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --input ${1} --output ${2}/Baseline/${3}_WPTight/  --year ${3} --wp Tight
}

function RunFitterSyst {
  python extract_fit.py --input ${1} --output ${2}/${4}/${3}_WPLoose/  --year ${3} --syst ${4} --wp Loose
  python extract_fit.py --input ${1} --output ${2}/${4}/${3}_WPMedium/ --year ${3} --syst ${4} --wp Medium
  python extract_fit.py --input ${1} --output ${2}/${4}/${3}_WPTight/  --year ${3} --syst ${4} --wp Tight
}

function RunFitterNLO {
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --useNLO --input ${1} --output ${2}/NLO/${3}_WPTight/  --year ${3} --wp Tight
}

function RunFitterHerwig {
  python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --useHerwig --input ${1} --output ${2}/Herwig/${3}_WPTight/  --year ${3} --wp Tight
}

function RunFitterPowheg {
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPLoose/  --year ${3} --wp Loose
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPMedium/ --year ${3} --wp Medium
  python extract_fit.py --usePowheg --input ${1} --output ${2}/Powheg/${3}_WPTight/  --year ${3} --wp Tight
}

#
#
#
ERAS=(
UL2017
UL2018
UL2016APV
)
for YEAR in ${ERAS[@]}
do
  RunFitter ${INDIR} ${OUTDIR} ${YEAR}
  RunFitterSyst ${INDIR} ${OUTDIR} ${YEAR} jerUp
  RunFitterSyst ${INDIR} ${OUTDIR} ${YEAR} jerDown
  RunFitterSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalUp
  RunFitterSyst ${INDIR} ${OUTDIR} ${YEAR} jesTotalDown
  RunFitterNLO ${INDIR} ${OUTDIR} ${YEAR}
done
#
#
#
ERAS=(
UL2016APV
UL2016
)
for YEAR in ${ERAS[@]}
do
  RunFitterPowheg ${INDIR} ${OUTDIR} ${YEAR}
done
