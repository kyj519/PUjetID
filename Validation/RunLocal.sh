#!/bin/sh


ERALIST=(
UL18
UL17
UL16
UL16APV
)

for ERA in ${ERALIST[@]}
do
	python MakeHistograms.py --era ${ERA}
done
