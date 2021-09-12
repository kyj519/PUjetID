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


ERAS=(
UL2017
UL2018
UL2016APV
)

for YEAR in ${ERAS[@]}
do
  RunFitter ${INDIR} ${OUTDIR} ${YEAR}
  # RunFitterNLO ${INDIR} ${OUTDIR} ${YEAR}
  # RunFitterHerwig ${INDIR} ${OUTDIR} ${YEAR}
done