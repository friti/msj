# ReRun MiniAODs
2024, 140X samples

## Setup the environment
```
cmsrel CMSSW_14_0_19
cd CMSSW_14_0_19/src
cmsenv
git cms-init

# Add necessary packages
git cms-addpkg PhysicsTools/nanoAOD
git cms-addpkg PhysicsTools/PatAlgos

# Merge the topic for relaxed cuts in miniAODs and NanoAODs
git cms-merge-topic -u friti:RelaxedCutsCMSSW14019
scram b -j8 
```

## Send job on CRAB
```
python3 submit_on_crab_qcd_bkg.py
python3 submit_on_crab_tt_bkg.py
```
