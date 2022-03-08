import sys
import crab_common 
import helpers

#crab_common.config.JobType.maxJobRuntimeMin  = 480

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
    crab_common.config.JobType.scriptArgs = [
      'era=2016',
      'isMC=0',
      'dataStream='+dataStreamName,
    ]
    #
    # Have to make unique requestName. 
    #
    primaryName   = dataset.split('/')[1]
    #
    # TO DO: Fix This
    #
    secondaryName = dataset.split('/')[2]
    secondaryName = secondaryName.replace("02Apr2020","Data16NanoAODv7") #CHECK
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