#### Script to plot the jet matching between isolated taus from DY and ak4 jets

from array import array
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import *
import ROOT
import math
from officialStyle import officialStyle
from cmsstyle import CMS_lumi

officialStyle(ROOT.gStyle, ROOT.TGaxis)
ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

max_files = 1000

nbins = 20
xmin = 0
xmax = 60

path_files = {
    "dy":["/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/dy10to50_cfgRun24_140X_Run2024_03092025/Nano/*","/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/dy50to120_cfgRun24_140X_Run2024_03102025/Nano/*","/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/dy120to200_cfgRun24_140X_Run2024_03102025/Nano/*","/eos/cms//store/cmst3/group/softJets/friti/bkg_samples_15000/dy200to400_cfgRun24_140X_Run2024_03102025/Nano/*"]
}

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

colours = {"jetmatch":ROOT.kMagenta,"HPS":ROOT.kBlack,"DeepTau":ROOT.kBlue,"pNet":ROOT.kRed,"UparT":ROOT.kGreen}
titles = {"jetmatch":"#tau/ak4 matching #Delta R<0.4",
          "HPS":"reco HPS",
          "DeepTau":"DeepTau",
          "pNet":"pNet",
          "UparT":"UparT"}

histos_list = ["jetmatch","HPS","DeepTau","pNet","UparT"]
histo_den = ROOT.TH1F("den","den",nbins,xmin,xmax)

histos = {}
for hist in histos_list:
    histos[hist] = ROOT.TH1F(hist,hist,nbins,xmin,xmax)
    histos[hist].Sumw2()
    histos[hist].SetDirectory(0)
    
paths = path_files["dy"]

files = []

for path in paths:
    path_files = os.popen("ls " + path).readlines()
    files.extend(path_files[:int(max_files/len(paths))])  # Take only the required number from each path


## loop over files
for fil in files[:max_files]:  # Keeping your original limit
    fil = fil.strip("\n")

    infile = ROOT.TFile.Open(fil)
    tree = InputTree(infile.Events)

    for i in range(tree.GetEntries()):
        event = Event(tree, i)
        genvistaus = Collection(event, "GenVisTau")
        genparts = Collection(event, "GenPart")
        jets = Collection(event, "Jet")
        taus = Collection(event, "Tau")
            
        for idx,genvistau in enumerate(genvistaus):
            genpartidx = genvistau.genPartIdxMother
            if genpartidx==-1 : continue
                                        
            if abs(genvistau.eta)>2.4: continue 

            histo_den.Fill(genvistau.pt) 
                
            jet,dr = closest(genvistau,jets)
            if dr<0.4:
                histos["jetmatch"].Fill(genvistau.pt)

            ## reco and IDs
            for tau in taus:
                if  tau.genPartIdx == idx: #match between reco and gen tau
                    histos["HPS"].Fill(genvistau.pt)
                    if tau.idDeepTau2018v2p5VSjet>=2: # Loose WP
                        histos["DeepTau"].Fill(genvistau.pt)
                    if tau.rawPNetVSjet>=0.25:
                        histos["pNet"].Fill(genvistau.pt)
                    if tau.rawUParTVSjet>=0.25:
                        histos["UparT"].Fill(genvistau.pt)


histos["jetmatch"].Divide(histo_den)
histos["HPS"].Divide(histo_den)
histos["DeepTau"].Divide(histo_den)
histos["pNet"].Divide(histo_den)
histos["UparT"].Divide(histo_den)

### PLOTTING
for idx,hist in enumerate(histos):
    c1.cd()
    histos[hist].SetTitle(";GEN visible #tau_{h} p_{T} (GeV);Efficiency")
    histos[hist].SetFillStyle(0)
    histos[hist].SetLineColor(colours[hist])
    histos[hist].SetMarkerColor(colours[hist])
    histos[hist].SetMaximum(1.3)
    if idx == 0:
        histos[hist].Draw("EP2")
    else:
        histos[hist].Draw("EP2 same")
    histos[hist].Draw("hist same")

    leg.AddEntry(histos[hist],titles[hist],'P')


CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = ' Simulation', lumi_13TeV = '  ')
leg.Draw("same")    
c1.SaveAs("plots/ztautau_ids_absetaL2p4.png")
c1.SaveAs("plots/ztautau_ids_absetaL2p4.pdf")








