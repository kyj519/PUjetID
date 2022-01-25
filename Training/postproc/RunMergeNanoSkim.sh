#!/bin/sh

SAMPLE=${1}
cd ${JOBWORKDIR}
python MergeNanoSkim.py --sample ${SAMPLE}
