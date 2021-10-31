{
  cout << endl << "Welcome to rootlogon.C" << endl;
  TStyle *customStyle= new TStyle("customStyle","customStyle");
  gROOT->SetStyle("Plain");
  customStyle->SetPalette(1,0);
  // use plain black on white colors
  Int_t icol=0;
  customStyle->SetFrameBorderMode(icol);
  customStyle->SetCanvasBorderMode(icol);
  customStyle->SetPadBorderMode(icol);
  customStyle->SetPadColor(icol);
  customStyle->SetCanvasColor(icol);
  customStyle->SetStatColor(icol);
  //customStyle->SetFillColor(icol);
  customStyle->SetFuncColor(kRed);
  customStyle->SetFuncWidth(1);
  // set the paper & margin sizes
  customStyle->SetPaperSize(20,20);
  customStyle->SetPadTopMargin(0.05);
  customStyle->SetPadBottomMargin(0.12);
  customStyle->SetPadLeftMargin(0.15);
  customStyle->SetPadRightMargin(0.04);
  // use large fonts
  //Int_t font=72;
  Int_t font=42;
  Double_t tsize=0.05;
  customStyle->SetTextFont(font);
  customStyle->SetTextSize(tsize);
  customStyle->SetLabelFont(font,"x");
  customStyle->SetTitleFont(font,"x");
  customStyle->SetLabelFont(font,"y");
  customStyle->SetTitleFont(font,"y");
  customStyle->SetLabelFont(font,"z");
  customStyle->SetTitleFont(font,"z");

  customStyle->SetLabelSize(tsize,"x");
  customStyle->SetTitleSize(tsize,"x");
  customStyle->SetLabelSize(tsize,"y");
  customStyle->SetTitleSize(tsize,"y");
  customStyle->SetLabelSize(tsize,"z");
  customStyle->SetTitleSize(tsize,"z");

  customStyle->SetTitleOffset(1.1,"x");
  customStyle->SetTitleOffset(1.5,"y");
  //use bold lines and markers
  //customStyle->SetMarkerStyle(20);
  //customStyle->SetMarkerSize(1.2);
  //customStyle->SetHistLineWidth(1.);
  customStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes
  //get rid of X error bars and y error bar caps
  //customStyle->SetErrorX(0.001);
  //do not display any of the standard histogram decorations
  customStyle->SetOptTitle(0);
  //customStyle->SetOptStat(111111);
  customStyle->SetOptStat(0);
  //customStyle->SetOptFit(111111);
  customStyle->SetOptFit(0);
  // put tick marks on top and RHS of plots
  customStyle->SetPadTickX(1);
  customStyle->SetPadTickY(1);

  customStyle->SetOptLogx(0);
  customStyle->SetOptLogy(0);
  customStyle->SetOptLogz(0);

  //gStyle->SetPadTickX(1);
  //gStyle->SetPadTickY(1);
  customStyle->SetPadTickY(1);
}
