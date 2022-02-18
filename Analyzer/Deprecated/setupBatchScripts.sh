#
# creat batchlog directory
#
mkdir -p BatchLog
#
# copy file and change WORKDIR string in the file to path to current directory
#
cp ./batchscripts/SkimNtuplesAtBatch.sh .
REPLACE="${PWD}"
sed -i "s|REPLACEME|${REPLACE}|g" ./SkimNtuplesAtBatch.sh
cp ./batchscripts/SkimNtuplesAtBatch.sh.sub .
#
# copy file and change WORKDIR string in the file to path to current directory
#
cp ./batchscripts/MakeHistosAtBatch.sh .
REPLACE="${PWD}"
sed -i "s|REPLACEME|${REPLACE}|g" ./MakeHistosAtBatch.sh
cp ./batchscripts/MakeHistosAtBatch.sh.sub .
