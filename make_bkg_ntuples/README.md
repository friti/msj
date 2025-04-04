## Reproduce miniAODs and NanoAODs

Starting from AOD samples, we can reproduce miniAODs and Nanoaods relaxing all the jets and tau cuts for low-pT tau studies.
To apply the new puppi tune, we use CMSSW_15_0_2 release and recluster the jets.

## Setup environment
`ssh lxplus8` or access the singularity with `cmssw-el8`
```
cmsrel CMSSW_15_0_2
cd CMSSW_15_0_2/src/
cmsenv
git cms-init
git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/PatAlgos

## changes with new parT branches
git cms-merge-topic -u friti:RelaxedCutsCMSSW1502

scram b -j8

cd ../..
```

## Send jobs on CONDOR
Use the `MultiSubmit_140X.py` and `production_2024_140X.sh`.
