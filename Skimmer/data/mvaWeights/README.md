# PileUp BDT Weights

In order to calculate the PileUp BDT discriminant for each jet on the fly while reading in JMEnano inputs, the weights 
must be downloaded. Below are the instructions for the Ultra-Legacy training weights.

## UL2017 weights

Get the weights from cms-data/RecoJets-JetProducers 

```bash
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL17_Eta0p0To2p5_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL17_Eta2p5To2p75_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL17_Eta2p75To3p0_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL17_Eta3p0To5p0_chs_BDT.weights.xml.gz
```

then unzip

```bash
gzip -d pileupJetId_UL17_Eta0p0To2p5_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL17_Eta2p5To2p75_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL17_Eta2p75To3p0_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL17_Eta3p0To5p0_chs_BDT.weights.xml.gz
```

## UL2018 weights

Get the weights from cms-data/RecoJets-JetProducers 

```bash
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL18_Eta0p0To2p5_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL18_Eta2p5To2p75_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL18_Eta2p75To3p0_chs_BDT.weights.xml.gz
wget https://github.com/cms-data/RecoJets-JetProducers/raw/master/pileupJetId_UL18_Eta3p0To5p0_chs_BDT.weights.xml.gz
```

then unzip

```bash
gzip -d pileupJetId_UL18_Eta0p0To2p5_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL18_Eta2p5To2p75_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL18_Eta2p75To3p0_chs_BDT.weights.xml.gz
gzip -d pileupJetId_UL18_Eta3p0To5p0_chs_BDT.weights.xml.gz
```
