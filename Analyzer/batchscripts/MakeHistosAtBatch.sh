#!/bin/bash

cd ${JOBWORKDIR}
source ./sourceRecentROOT.sh
python MakeHistogramsHisto3D.py --sample ${1} --cores ${2} --useSkimNtuples
