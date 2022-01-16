import ROOT
import os

ROOT.gROOT.SetBatch()
ROOT.gROOT.ProcessLine(".L Helpers.h+O")
ROOT.gROOT.ProcessLine(".L SFProducerPUJetId.h+O")
