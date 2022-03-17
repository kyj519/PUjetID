#
# ULNanoAODv9 UL2017 
#

MAX_EVENTS=1000
python RunSkimmerLocal.py \
--era="UL2017" \
--maxEvents=${MAX_EVENTS} \
--outDir="./MCUL17_DYJetsToLL_LO" \
--isMC=1 \
--dataStream="MC"

echo "#######################################"
echo "#######################################"
echo "#######################################"

MAX_EVENTS=1000
 python RunSkimmerLocal.py \
 --era="UL2017" \
 --maxEvents=${MAX_EVENTS} \
 --outDir="./DataUL17_DoubleMuon" \
 --isMC=0 \
 --dataStream="DoubleMuon" \

echo "#######################################"
echo "#######################################"
echo "#######################################"

# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2017" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL17_DoubleEG" \
# --isMC=0 \
# --dataStream="DoubleEG"
#
#
#
#
# ULNanoAODv9 UL2018
#
MAX_EVENTS=1000
python RunSkimmerLocal.py \
--era="UL2018" \
--maxEvents=${MAX_EVENTS} \
--outDir="./MCUL18_DYJetsToLL_LO" \
--isMC=1 \
--dataStream="MC"

echo "#######################################"
echo "#######################################"
echo "#######################################"

MAX_EVENTS=1000
python RunSkimmerLocal.py \
--era="UL2018" \
--maxEvents=${MAX_EVENTS} \
--outDir="./DataUL18_DoubleMuon" \
--isMC=0 \
--dataStream="DoubleMuon"

echo "#######################################"
echo "#######################################"
echo "#######################################"

# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2018" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL18_EGamma" \
# --isMC=0 \
# --dataStream="EGamma"
#
#
# ULNanoAODv9 UL2016APV
#
MAX_EVENTS=1000
python RunSkimmerLocal.py \
--era="UL2016APV" \
--maxEvents=${MAX_EVENTS} \
--outDir="./MCUL16APV_DYJetsToLL_LO" \
--isMC=1 \
--dataStream="MC"

echo "#######################################"
echo "#######################################"
echo "#######################################"

MAX_EVENTS=1000
python RunSkimmerLocal.py \
--era="UL2016APV" \
--maxEvents=${MAX_EVENTS} \
--outDir="./DataUL16APV_DoubleMuon" \
--isMC=0 \
--dataStream="DoubleMuon"

echo "#######################################"
echo "#######################################"
echo "#######################################"

# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2016APV" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL16APV_DoubleEG" \
# --isMC=0 \
# --dataStream="DoubleEG"


