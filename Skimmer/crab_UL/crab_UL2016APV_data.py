import sys
import crab_common 
import helpers

crab_common.config.JobType.maxJobRuntimeMin = 240 

def GetDataStream(name):
  if "DoubleEG" in name:   return "DoubleEG"
  if "DoubleMuon" in name: return "DoubleMuon"

if __name__ == '__main__':
  #
  # Read in txt file with list of samples
  #
  f = open(sys.argv[1]) 
  samplelist =  helpers.GetSampleList(f)

  print "Will send crab jobs for the following samples:"
  for dataset in samplelist:
    print dataset
  print "\n\n"

  from CRABAPI.RawCommand import crabCommand
  for i, dataset in enumerate(samplelist):
    print "%d/%d:Sending CRAB job: %s" % (i+1,len(samplelist), dataset)
    crab_common.config.Data.inputDataset = dataset
    #
    #
    #
    dataStreamName=GetDataStream(dataset)
    runPeriod=dataset.split("-")[0][-1:]

    crab_common.config.JobType.scriptArgs = [
      'era=UL2016APV',
      'isMC=0',
      'dataStream='+dataStreamName,
      'runPeriod='+runPeriod
    ]
    if 'JMENano' in dataset:
      crab_common.config.JobType.scriptArgs.append('useJMENano=1')
    #
    # Have to make unique requestName. 
    #
    primaryName   = dataset.split('/')[1]
    #
    # TO DO: Fix This
    #
    secondaryName = dataset.split('/')[2]
    secondaryName = secondaryName.replace("HIPM_UL2016_MiniAODv2_JMENanoAODv9_","DataUL16APVNanoAODv9") #CHECK
    secondaryName = secondaryName.replace("HIPM_UL2016_MiniAODv2_NanoAODv9","DataUL16APVNanoAODv9") #CHECK
    secondaryName = secondaryName.replace("-v1","") #CHECK
    secondaryName = secondaryName.replace("-v2","") #CHECK
    secondaryName = secondaryName.replace("-v3","") #CHECK
    #
    requestName = primaryName + "_" + secondaryName
    requestName = crab_common.reqNamePrefix + "_" + requestName + "_" + crab_common.version
    crab_common.config.General.requestName   = requestName
    #  
    outputDatasetTag = crab_common.reqNamePrefix + "_" + secondaryName + "_" + crab_common.version 
    crab_common.config.Data.outputDatasetTag = outputDatasetTag 
    #
    print "requestName: ", requestName 
    print "outputDatasetTag: ", outputDatasetTag
    crabCommand('submit', config = crab_common.config)
    print ""