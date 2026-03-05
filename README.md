# nanoAOD producer customized for BPH analysis 

The focus is on B -> mumu X analyses.
Based on the code of RK 2018 (BParkingNano)

**New:** Non-BPH configuration for Underlying Event studies (FSQ-15-007-like) at 13.6 TeV is now available. See [BPHNano/README_UE.md](BPHNano/README_UE.md) for details.

## Getting started

```shell
cmsrel CMSSW_13_3_0
cd CMSSW_13_3_0/src
cmsenv
git cms-init
```
Architecture should be el8 or el9

## Add the BPHNano package and build everything

```shell
git clone git@github.com:DickyChant/BPHNano.git ./PhysicsTools
git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/NanoAODTools
scram b
```
or https equivalent

## To run on a test file

### BPH Nano (B physics)

```shell
cd PhysicsTools/BPHNano/test/
cmsenv 
cmsRun run_bphNano_cfg.py
```

### UE Nano (Underlying Event studies, FSQ-15-007-like, 13.6 TeV)

```shell
cd PhysicsTools/BPHNano/test/
cmsenv 
cmsRun run_UE_cfg.py
```

