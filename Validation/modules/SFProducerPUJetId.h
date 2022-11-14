//
//
//
//
//
#include <string>
#include <iostream>
#include "TFile.h"
#include "TH2F.h"

using namespace std;

class SFProducerPUJetId {       

  public:
    SFProducerPUJetId(string,string,string);

    void LoadSF();

    float GetSF(float,float,bool);

    float Get_EffSF_PUID(float,float,bool,int);
    float Get_EffSFUnc_PUID(float,float);
    float Get_EffMC_PUID(float,float);

    float Get_MistagSF_PUID(float,float,bool,int);
    float Get_MistagSFUnc_PUID(float,float);
    float Get_MistagMC_PUID(float,float);

    float GetTH2DBinContent(TH2F*,float,float);

    TFile* m_SFFile = nullptr;

    TH2F*  m_Hist_Eff_SF     = nullptr;
    TH2F*  m_Hist_Eff_SFUnc  = nullptr;
    TH2F*  m_Hist_Eff_MC     = nullptr;

    TH2F*  m_Hist_Mistag_SF     = nullptr;
    TH2F*  m_Hist_Mistag_SFUnc  = nullptr;  
    TH2F*  m_Hist_Mistag_MC     = nullptr;

  private:
    string m_eraName;
    string m_sfFileName;
    string m_wp;
};

SFProducerPUJetId::SFProducerPUJetId(string _eraName, string _sfFileName, string _wp){
  cout << "SFProducerPUJetId::SFProducerPUJetId()::In Constructor" << endl;
  m_eraName = _eraName;
  m_sfFileName = _sfFileName;
  m_wp = _wp;
}

void SFProducerPUJetId::LoadSF()
{
  cout << "SFProducerPUJetId::LoadSF()::Load SF for era = " << m_eraName << ", wp = " << m_wp << endl;
  
  //
  // Load SF
  //
  m_SFFile = new TFile(m_sfFileName.c_str(),"READ");

  //
  // Get MC eff and SF
  //
  string histName_Eff_SF    = "h2_eff_sf"+m_eraName+"_"+m_wp;
  string histName_Eff_SFUnc = "h2_eff_sf"+m_eraName+"_"+m_wp+"_Systuncty";
  string histName_Eff_MC    = "h2_eff_mc"+m_eraName+"_"+m_wp;

  // cout << histName_Eff_SF << endl;
  // cout << histName_Eff_SFUnc << endl;
  // cout << histName_Eff_MC << endl;

  m_Hist_Eff_SF    = (TH2F*)m_SFFile->Get(histName_Eff_SF.c_str());
  m_Hist_Eff_SFUnc = (TH2F*)m_SFFile->Get(histName_Eff_SFUnc.c_str());
  m_Hist_Eff_MC    = (TH2F*)m_SFFile->Get(histName_Eff_MC.c_str());

  //
  // Get MC mistag and SF
  //

  string histName_Mistag_SF    = "h2_mistag_sf"+m_eraName+"_"+m_wp;
  string histName_Mistag_SFUnc = "h2_mistag_sf"+m_eraName+"_"+m_wp+"_Systuncty";
  string histName_Mistag_MC    = "h2_mistag_mc"+m_eraName+"_"+m_wp;

  // cout << histName_Mistag_SF << endl;
  // cout << histName_Mistag_SFUnc << endl;
  // cout << histName_Mistag_MC << endl;

  m_Hist_Mistag_SF    = (TH2F*)m_SFFile->Get(histName_Mistag_SF.c_str());
  m_Hist_Mistag_SFUnc = (TH2F*)m_SFFile->Get(histName_Mistag_SFUnc.c_str());
  m_Hist_Mistag_MC    = (TH2F*)m_SFFile->Get(histName_Mistag_MC.c_str());
}

//
//
//
float SFProducerPUJetId::GetSF(float pt, float eta, bool isHSJet){
  if (isHSJet){
    return Get_EffSF_PUID(pt,eta,true,0);
  }else{
    return Get_MistagSF_PUID(pt,eta,false,0);
  }
}
//
//
//
float SFProducerPUJetId::Get_EffSF_PUID(float pt, float eta, bool isHSJet, int syst){
  float uncty = 0.;
  float sf = 1.;
  if (pt < 50 && isHSJet){// Hardcoded here
    uncty =  Get_EffSFUnc_PUID(pt, eta);
    sf = GetTH2DBinContent(m_Hist_Eff_SF, pt, eta);
    sf = sf + ((float)syst * uncty);
    if(sf<=0.) sf = 1e-9;
    return sf;
  }
  return sf;
}
float SFProducerPUJetId::Get_EffSFUnc_PUID(float pt, float eta){
    return GetTH2DBinContent(m_Hist_Eff_SFUnc, pt, eta);
}
float SFProducerPUJetId::Get_EffMC_PUID(float pt, float eta){
  return GetTH2DBinContent(m_Hist_Eff_MC, pt, eta);
}
//
//
//
float SFProducerPUJetId::Get_MistagSF_PUID(float pt, float eta, bool isHSJet, int syst){
  float uncty = 0.;
  float sf = 1.;
  if (pt < 50. && (!isHSJet)){ // Hardcoded here
    uncty =  Get_MistagSFUnc_PUID(pt, eta);
    sf = GetTH2DBinContent(m_Hist_Mistag_SF, pt, eta);
    sf = sf + ((float)syst * uncty);
    if(sf<=0.) sf = 1e-9;
    return sf;
    // if (sf < 0.0001){ // For bins with SF == 0. TO DO: Should really check why its 0.
    //   sf = 1.0;
    // }
  }
  return sf;
}
float SFProducerPUJetId::Get_MistagSFUnc_PUID(float pt, float eta){
 
  return GetTH2DBinContent(m_Hist_Mistag_SFUnc, pt, eta);
  // if (sf < 0.0001){ // For bins with SF == 0. TO DO: Should really check why its 0.
  //   sf = 1.0;
  // }
  

}
float SFProducerPUJetId::Get_MistagMC_PUID(float pt, float eta){
  return GetTH2DBinContent(m_Hist_Mistag_MC, pt, eta);
}
//
//
//
float SFProducerPUJetId::GetTH2DBinContent(TH2F* h2, float x_var, float y_var){
  return h2->GetBinContent(h2->FindBin(x_var, y_var));
}