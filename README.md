# nanoAOD producer customized for BPH analysis 

The focus is on B -> mumu X analyses.
Based on the code of RK 2018 (BParkingNano)

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
or https equivalent:
```shell
git clone https://github.com/DickyChant/BPHNano.git ./PhysicsTools
git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/NanoAODTools
scram b
```

## To run on a test file

```shell
cd PhysicsTools/BPHNano/test/
cmsenv 
cmsRun run_bphNano_cfg.py
```

## Available Analyses

After building with `scram b`, you can run different BPH analyses by customizing the nanoAOD configuration. Here are the available customization functions:

### Pentaquark Analysis (J/psi + p and J/psi + p + K)

For pentaquark searches (Pc states like Pc(4312), Pc(4440), Pc(4457)):

```python
from PhysicsTools.BPHNano.nanoBPH_cff import *

# Add required sequences
process = nanoAOD_customizeMuonBPH(process, isMC)
process = nanoAOD_customizeDiMuonBPH(process, isMC)
process = nanoAOD_customizeTrackBPH(process, isMC)

# Add pentaquark analysis - choose one:
process = nanoAOD_customizePentaquark(process, isMC)      # Full search (J/psi + p and J/psi + p + K)
process = nanoAOD_customizePentaquarkJpsiP(process, isMC) # J/psi + p only
process = nanoAOD_customizePentaquarkJpsiPK(process, isMC) # J/psi + p + K only (Lambda_b decays)
```

Run examples:

**Using the dedicated pentaquark test files (recommended):**
```shell
cd PhysicsTools/BPHNano/test/
# For data:
cmsRun run_pentaquark_data_cfg.py maxEvents=1000

# For MC:
cmsRun run_pentaquark_mc_cfg.py maxEvents=1000
```

**Using the general configuration file:**
```shell
cd PhysicsTools/BPHNano/test/
cmsRun run_bphNano_cfg.py decay="pentaquark" isMC=False maxEvents=1000  # data
cmsRun run_bphNano_cfg.py decay="pentaquark" isMC=True maxEvents=1000   # MC
```

### Other Available Analyses

- **Eta to 4 muons**: `nanoAOD_customizeEtaTo4MuBPH(process, isMC)`
- **Eta to 2 leptons + 2 pions**: `nanoAOD_customizeEta2Mu2PiBPH(process, isMC)`
- **B to K ll**: `nanoAOD_customizeBToKLL(process, isMC)`
- **B to K* ll**: `nanoAOD_customizeBToKstarLL(process, isMC)`
- **B to K_short ll**: `nanoAOD_customizeBToKshortLL(process, isMC)`
- **Lambda_b to Lambda ll**: `nanoAOD_customizeLambda(process, isMC)`
- **Lambda_b to Lambda hh**: `nanoAOD_customizeLambdahh(process, isMC)`
- **B to D* K**: `nanoAOD_customizeBDKstar(process, isMC)`

