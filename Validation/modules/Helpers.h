#include "TMath.h"

using namespace std;

float DeltaPhiNorm(float dphi){
  float _dphi = 0.0;
  if(dphi > 0.0) _dphi = dphi;
  if(dphi < 0.0) {
    _dphi = dphi + (2*TMath::Pi());
  }
  return _dphi/TMath::Pi();
}
float DeltaPhi(float dphi){
  float _dphi = 0.0;
  if(dphi > 0.0) _dphi = dphi;
  if(dphi < 0.0) {
    _dphi = dphi + (2*TMath::Pi());
  }
  return _dphi;
}
