## Fake rate plots for state-of-the art IDs (DeepTau, pNet, UparT)

from array import array
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import *
import ROOT
import math
from officialStyle import officialStyle
from cmsstyle import CMS_lumi
from plotting_functions import *

ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)
officialStyle(ROOT.gStyle, ROOT.TGaxis)

### some options
max_files = 200

c1 = ROOT.TCanvas('c1', '', 700, 700)
c1.Draw()
c1.cd()
c1.SetTicks(True)

leg = ROOT.TLegend(0.24,.75,.95,.90)
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.035)

samples_bkg ={
    "qcd":"/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/qcd_cfgRun24_140X_Run2024_03092025/Nano/*",
    "ttbar":"/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/ttbar_cfgRun24_140X_Run2024_03092025/Nano/*"
}

nbins = 20
xmin = 0
xmax = 100

colours = {"HPS":ROOT.kBlack,"DeepTau":ROOT.kBlue,"pNet":ROOT.kRed,"UparT":ROOT.kGreen}
titles = {"jetmatch":"#tau/ak4 matching #Delta R<0.4",
          "HPS":"reco HPS",
          "DeepTau":"DeepTau",
          "pNet":"pNet",
          "UparT":"UparT"}

histos_list = ["HPS","DeepTau","pNet","UparT"]
histo_den = ROOT.TH1F("den","den",nbins,xmin,xmax)

histos = {}
for hist in histos_list:
    histos[hist] = ROOT.TH1F(hist,hist,nbins,xmin,xmax)
    histos[hist].Sumw2()
    histos[hist].SetDirectory(0)

    
for sample in samples_bkg:
    files = os.popen("ls "+samples_bkg[sample]).readlines()

    for fil in files[:max_files]:
        fil = fil.strip("\n")

        infile = ROOT.TFile.Open(fil)
        tree = InputTree(infile.Events)

        for i in range(tree.GetEntries()):
            event = Event(tree,i)

            genvistaus = Collection(event, "GenVisTau")
            jets = Collection(event, "Jet")
            genjets = Collection(event, "GenJet")
            genparts = Collection(event, "GenPart")
            taus = Collection(event, "Tau")
        
            ## reco jets NOT matching with get Taus
            for jet in jets:

                if abs(jet.eta)>2.4: continue
                
                genpart, dr = closest(jet, genparts)
                if abs(genpart.pdgId) == 15: continue ## NOT matching with taus!!
                
                if dr<0.15:
                    histo_den.Fill(jet.pt)

                    ## this reco jets doesn't match with a gen tau, but does it match with a reco tau?
                    tau, dr = closest(jet, taus)
                    if dr<0.15:
                        histos["HPS"].Fill(jet.pt)

                        ## does the tau pass the IDs?

                        ## deeptau
                        if tau.idDeepTau2018v2p5VSjet>=2:
                            histos["DeepTau"].Fill(jet.pt)

                        if tau.rawPNetVSjet>=0.25:
                            histos["pNet"].Fill(jet.pt)
                        if tau.rawUParTVSjet>=0.25:
                            histos["UparT"].Fill(jet.pt)


histos["HPS"].Divide(histo_den)
histos["DeepTau"].Divide(histo_den)
histos["pNet"].Divide(histo_den)
histos["UparT"].Divide(histo_den)

### PLOTTING
for idx,hist in enumerate(histos):
    c1.cd()
    histos[hist].SetTitle(";RECO jet p_{T} (GeV);Efficiency")
    histos[hist].SetFillStyle(0)
    histos[hist].SetLineColor(colours[hist])
    histos[hist].SetMarkerColor(colours[hist])
    histos[hist].SetMaximum(1.3 * histos[hist].GetMaximum())
    if idx == 0:
        histos[hist].Draw("EP2")
    else:
        histos[hist].Draw("EP2 same")
    histos[hist].Draw("hist same")

    leg.AddEntry(histos[hist],titles[hist],'P')


CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = ' Simulation', lumi_13TeV = '  ')
leg.Draw("same")
c1.SaveAs("plots/fakerate.png")
c1.SaveAs("plots/fakerate.pdf")


