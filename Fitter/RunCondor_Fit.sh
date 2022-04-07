#
# Directory path containing all the histogram rootfiles
#

export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert
export LD_PRELOAD=/usr/lib64/libpdcap.so
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/dcap



INDIR="gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his_hadd/${6}"

#
# Directory path for the output of the fits
#
#OUTDIR="gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his/fitresult"
OUTDIR="/u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Fitter/result/${5}/${6}"
#runkeyformat = era+" "+order+" "+wp+" "+syst
#############################################################################
#
#
#
#############################################################################

python /u/user/yeonjoon/working_dir/PileUpJetIDSF/CMSSW_10_6_30/src/PUjetID/Fitter/extract_fit_allchannel.py --input $INDIR --output ${OUTDIR}/${2}_${4}/${1}_WP${3}/  --year $1 --wp $3 --syst $4 --order $2 
 