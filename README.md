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

## CRAB Submission for Large-Scale Production

For processing large datasets on the grid using CRAB (CMS Remote Analysis Builder):

### Setup CRAB

```shell
source /cvmfs/cms.cern.ch/common/crab-setup.sh
```

### Prepare Dataset Configuration

Create a YAML file (e.g., `pentaquark_samples.yml`) with your datasets. The format follows the schema defined in `production/submit_on_crab.py`:

```yaml
common:
  data:
    lumimask: None
    splitting: 10
    globaltag: 124X_dataRun3_v15
  mc:
    splitting: 1
    globaltag: 130X_mcRun3_2022_realistic_postEE_v6

samples:
  pentaquark_data_2022C_part%d:
    dataset: /ParkingDoubleMuonLowMass%d/Run2022C-10Dec2022-v2/MINIAOD
    goldenjson: /eos/user/c/cmsdqm/www/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json
    decay: pentaquark
    globaltag: 124X_dataRun3_v15
    isMC: False
    parts:
      - 0
      - 1
      - 2
  
  pentaquark_mc_LambdaBToJpsiLambda:
    dataset: /LambdaBToJpsiLambda_JpsiFilter_MuFilter_LambdaFilter_TuneCP5_13p6TeV_pythia8-evtgen/Run3Summer22MiniAODv4-130X_mcRun3_2022_realistic_v5-v2/MINIAODSIM
    decay: pentaquark
    isMC: True
    globaltag: 130X_mcRun3_2022_realistic_postEE_v6
```

### Submit Jobs to CRAB

Use the multicrab submission script:

```shell
cd PhysicsTools/BPHNano/production/

# Submit all samples in the YAML file
python submit_on_crab.py -y pentaquark_samples.yml -c submit -p ../test/run_pentaquark_mc_cfg.py -w PENTAQUARK_$(date +%Y%b%d)

# Submit with filter (only samples matching pattern)
python submit_on_crab.py -y pentaquark_samples.yml -c submit -f "*2022C*" -p ../test/run_pentaquark_data_cfg.py

# Check status of submitted jobs
python submit_on_crab.py -y pentaquark_samples.yml -c status -w PENTAQUARK_2024Dec23
```

### Command Options

- `-y, --yaml`: YAML file with dataset descriptions
- `-c, --cmd`: CRAB command (`submit` or `status`)
- `-f, --filter`: Filter samples by pattern (POSIX regex)
- `-w, --workarea`: CRAB working area name
- `-o, --outputdir`: LFN output directory
- `-p, --psetcfg`: Plugin configuration file (e.g., `run_pentaquark_mc_cfg.py`)
- `-s, --site`: Storage site (default: T3_CH_CERNBOX)
- `-t, --tag`: Production tag
- `-tt, --test`: Submit test job

### Example: Submit Pentaquark Analysis

For MC:
```shell
python submit_on_crab.py \
  -y pentaquark_samples.yml \
  -c submit \
  -f "*pentaquark_mc*" \
  -p ../test/run_pentaquark_mc_cfg.py \
  -w PENTAQUARK_MC_$(date +%Y%b%d) \
  -o /store/user/YOUR_USERNAME/
```

For Data:
```shell
python submit_on_crab.py \
  -y pentaquark_samples.yml \
  -c submit \
  -f "*pentaquark_data*" \
  -p ../test/run_pentaquark_data_cfg.py \
  -w PENTAQUARK_DATA_$(date +%Y%b%d) \
  -o /store/user/YOUR_USERNAME/
```

### Monitor and Retrieve Results

```shell
# Check job status
crab status -d crab_projects/PENTAQUARK_MC_2024Dec23/crab_pentaquark_mc_LambdaBToJpsiLambda/

# Get output files
crab getoutput -d crab_projects/PENTAQUARK_MC_2024Dec23/crab_pentaquark_mc_LambdaBToJpsiLambda/

# Resubmit failed jobs
crab resubmit -d crab_projects/PENTAQUARK_MC_2024Dec23/crab_pentaquark_mc_LambdaBToJpsiLambda/
```

See `production/README` for more details on the YAML format and multicrab submission system.

