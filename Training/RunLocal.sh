#
#
# ULNanoAODv9 UL2018
#
# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2018" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./MCUL18_DYJetsToLL_LO" \
# --isMC=1 \
# --dataStream="MC"

MAX_EVENTS=-1
python RunSkimmerLocal.py \
--era="UL2018" \
--maxEvents=${MAX_EVENTS} \
--outDir="./DataUL18_DoubleMuon" \
--isMC=0 \
--dataStream="DoubleMuon"
#
# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2018" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL18_EGamma" \
# --isMC=0 \
# --dataStream="EGamma"
#
# ULNanoAODv9 UL2017 
#
# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2017" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./MCUL17_DYJetsToLL_LO" \
# --isMC=1 \
# --dataStream="MC"
#
# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2017" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL17_DoubleMuon" \
# --isMC=0 \
# --dataStream="DoubleMuon"
#
# MAX_EVENTS=20000
# python RunSkimmerLocal.py \
# --era="UL2017" \
# --maxEvents=${MAX_EVENTS} \
# --outDir="./DataUL17_DoubleEG" \
# --isMC=0 \
# --dataStream="DoubleEG"
