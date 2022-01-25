#!/bin/sh


ERALIST=(
UL17
UL18
UL16APV
)

for ERA in ${ERALIST[@]}
do
	python MakeHistograms.py --era ${ERA}
done
