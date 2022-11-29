#
# Directory path containing all the histogram rootfiles
#

INDIR="/gv0/Users/yeonjoon/ntuples/result_his_hadd/${6}"

#
# Directory path for the output of the fits
#
#OUTDIR="gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his/fitresult"
OUTDIR="/data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Fitter/result/${5}/${6}"
#runkeyformat = era+" "+order+" "+wp+" "+syst
#############################################################################
#
#
#
#############################################################################

python /data6/Users/yeonjoon/CMSSW_10_6_30/src/PUjetID/Fitter/extract_fit.py --input $INDIR --output ${OUTDIR}/${2}_${4}/${1}_WP${3}/  --year $1 --wp $3 --syst $4 --order $2 --channel El 
 