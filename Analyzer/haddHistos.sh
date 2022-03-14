#
# combine all data histos into one root file
#
export X509_USER_PROXY=/u/user/yeonjoon/proxy.cert
export LD_PRELOAD="/usr/lib64/libpdcap.so"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/lib64/dcap"
HISTODIR="gsidcap://cluster142.knu.ac.kr//pnfs/knu.ac.kr/data/cms/store/user/yeonjoon/ntuples/result_his"


mkdir ./temp
ls $HISTODIR | xargs -I{} cp $HISTODIR/{} ./temp/ &
wait
hadd -f ./temp/Histo_DataUL17.root ./temp/Histo_DataUL17*_*.root
hadd -f ./temp/Histo_DataUL18.root ./temp/Histo_DataUL18*_*.root
hadd -f ./temp/Histo_DataUL16APV.root ./temp/Histo_DataUL16APV*_*.root
hadd -f ./temp/Histo_DataUL16.root ./temp/Histo_DataUL16[FGH]_*.root

cp ./temp/Histo_DataUL17.root ${HISTODIR}
cp ./temp/Histo_DataUL18.root ${HISTODIR}
cp ./temp/Histo_DataUL16APV.root ${HISTODIR}
cp ./temp/Histo_DataUL16.root ${HISTODIR}
rm -rf ./temp