#!/bin/bash

cd ${JOBWORKDIR}
source ./sourceRecentROOT.sh
python SkimNtuples.py --sample ${1} --cores ${2}
