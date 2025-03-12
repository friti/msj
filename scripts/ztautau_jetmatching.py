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

max_files = 2000

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

nbins = 20
xmin = 0
xmax = 60

bins = ["inclusive","barrel","endcap"]
colours = {"inclusive":ROOT.kMagenta,"barrel":ROOT.kOrange,"endcap":ROOT.kBlue}

jetmatch_singletau_histos = {}
jetmatch_singletau_histos_den = {}

## read files
paths = path_files["dy"]

files = []

for path in paths:
    path_files = os.popen("ls " + path).readlines()
    files.extend(path_files[:int(max_files/len(paths))])  # Take only the required number from each path


for wp in bins:
    print("Processing ",wp)
    jetmatch_singletau_histos[wp]=ROOT.TH1F("jetmatch_singletau_"+wp,"jetmatch_singletau_"+wp,nbins,xmin,xmax)
    jetmatch_singletau_histos_den[wp]=ROOT.TH1F("jetmatch_singletau_den_"+wp,"jetmatch_singletau_den_"+wp,nbins,xmin,xmax)

    jetmatch_singletau_histos[wp].Sumw2()
    jetmatch_singletau_histos_den[wp].Sumw2()

    jetmatch_singletau_histos[wp].SetDirectory(0)
    jetmatch_singletau_histos_den[wp].SetDirectory(0)


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
                                        
                if abs(genvistau.eta)>2.4: continue # always true

                if wp == "barrel" and not (abs(genvistau.eta)>0 and abs(genvistau.eta)<1.3): continue
                if wp == "endcap" and not (abs(genvistau.eta)>1.3 and abs(genvistau.eta)<2.4): continue

                jetmatch_singletau_histos_den[wp].Fill(genvistau.pt) 
                
                jet,dr = closest(genvistau,jets)
                if dr<0.4:
                    jetmatch_singletau_histos[wp].Fill(genvistau.pt)

    jetmatch_singletau_histos[wp].Divide(jetmatch_singletau_histos_den[wp])

### PLOTTING
for idx,wp in enumerate(bins):
    c1.cd()
    jetmatch_singletau_histos[wp].SetTitle(";GEN visible #tau_{h} p_{T};ak4/gen #tau_{h} match efficiency")
    jetmatch_singletau_histos[wp].SetFillStyle(0)
    jetmatch_singletau_histos[wp].SetLineColor(colours[wp])
    jetmatch_singletau_histos[wp].SetMarkerColor(colours[wp])
    jetmatch_singletau_histos[wp].SetMaximum(1.3)
    if idx == 0:
        jetmatch_singletau_histos[wp].Draw("EP2")
    else:
        jetmatch_singletau_histos[wp].Draw("EP2 same")
    jetmatch_singletau_histos[wp].Draw("hist same")

    if wp == "inclusive":
        leg.AddEntry(jetmatch_singletau_histos[wp],"Z #rightarrow #tau #tau: inclusive 0<|#eta|<2.4",'P')
    elif wp == "barrel":
        leg.AddEntry(jetmatch_singletau_histos[wp],"Z #rightarrow #tau #tau: 0<|#eta|<1.3",'P')

    elif wp == "endcap":
        leg.AddEntry(jetmatch_singletau_histos[wp],"Z #rightarrow #tau #tau: 1.3<|#eta|<2.4",'P')


CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = ' Simulation', lumi_13TeV = '')
leg.Draw("same")    
c1.SaveAs("plots/ztautau_ak4_matching.png")
c1.SaveAs("plots/ztautau_ak4_matching.pdf")








