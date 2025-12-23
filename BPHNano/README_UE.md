# Underlying Event NanoAOD (FSQ-15-007)

Non-BPH configuration for underlying event measurement at 13 TeV, following the FSQ-15-007 analysis.

**This configuration is completely independent of BPH modules** - it uses only standard NanoAOD components.

## Overview

This configuration creates a NanoAOD focused on underlying event studies rather than B physics. It includes:
- Charged particle tracks (pt > 0.5 GeV, |eta| < 2.5)
- Primary vertices
- Generator-level particles (for MC, using standard `finalGenParticles`)
- Basic event metadata

**No BPH dependencies:** Uses `nanoUE_cff.py` instead of `nanoBPH_cff.py` for a truly standalone UE configuration.

## Running the configuration

### Test with MC sample

```shell
cd PhysicsTools/BPHNano/test/
cmsenv
cmsRun run_UE_cfg.py isMC=True maxEvents=1000
```

### Test with Data sample

```shell
cd PhysicsTools/BPHNano/test/
cmsenv
cmsRun run_UE_cfg.py isMC=False maxEvents=1000
```

### Custom input files

```shell
cmsRun run_UE_cfg.py inputFiles="file:myinput.root" outputFiles="myoutput.root" maxEvents=1000 isMC=True
```

## Configuration Details

### Track Selection
- Minimum pT: 0.5 GeV (standard for UE studies)
- Maximum |η|: 2.5
- Includes both packedPFCandidates and lostTracks

### Output Content
The NanoAOD output contains:
- Track table with kinematic variables (pt, eta, phi, mass)
- Track quality variables (chi2, number of hits)
- Impact parameters (dxy, dz) with respect to primary vertex
- Generator matching (for MC only)

### Differences from BPH Nano
- **Completely standalone:** No BPH module dependencies
- **Standard NanoAOD components:** Uses `finalGenParticles` instead of `finalGenParticlesBPH`
- **Standard MC matching:** Uses `CandMCMatchTableProducer` instead of `CandMCMatchTableProducerBPH`
- No B meson reconstruction
- No dimuon reconstruction
- No muon-specific selections
- Focuses on inclusive charged particle tracking
- Optimized for minimum bias and QCD samples

## Use Case: FSQ-15-007 Analysis

This configuration is designed for underlying event measurements following the FSQ-15-007 analysis strategy:
1. Study charged particle multiplicity and pT distributions
2. Measure underlying event activity in minimum bias events
3. Study correlations between tracks and primary vertices
4. Generator-level comparisons for MC tuning

## Production with CRAB

For large-scale production, you can use the CRAB (CMS Remote Analysis Builder) submission system to process many files in parallel on the grid.

### Using the multicrab submission script

The repository includes a multicrab submission script at `BPHNano/production/submit_on_crab.py` that can be adapted for UE nanoAOD production.

#### Basic CRAB workflow:

1. **Create a YAML configuration file** (e.g., `ue_samples.yml`):

```yaml
common:
  data:
    lumimask: 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/Cert_Collisions2022_355100_362760_Golden.json'
    splitting: 2
    globaltag: '130X_dataRun3_Prompt_v3'
  mc:
    splitting: 2
    globaltag: '124X_mcRun3_2022_realistic_v12'

samples:
  QCD_Flat_MC_2022:
    dataset: '/QCD_PT-15to7000_TuneCP5_Flat_13p6TeV_pythia8/Run3Summer22MiniAODv4-124X_mcRun3_2022_realistic_v12-v2/MINIAODSIM'
    isMC: True
  
  JetMET_Data_2022D:
    dataset: '/JetMET0/Run2022D-10Dec2022-v2/MINIAOD'
    isMC: False
```

2. **Submit jobs to CRAB**:

```bash
cd BPHNano/production/
python submit_on_crab.py \
  -y ue_samples.yml \
  -p ../test/run_UE_cfg.py \
  -w UE_NANO_2024 \
  -o /store/user/<your_username>/ \
  -s T2_CH_CERN
```

3. **Check job status**:

```bash
crab status -d UE_NANO_2024_QCD_Flat_MC_2022
# Or for the data sample:
crab status -d UE_NANO_2024_JetMET_Data_2022D
```

**Note:** The multicrab script is currently configured for BPH nano production. You may need to modify the default pset configuration in the script or ensure `run_UE_cfg.py` is compatible with the expected parameters.

### Direct CRAB configuration

Alternatively, you can create a standalone CRAB configuration file:

```python
from CRABClient.UserUtilities import config
config = config()

config.General.requestName = 'UE_Nano_QCD_2022'
config.General.workArea = 'crab_projects_UE'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../test/run_UE_cfg.py'
config.JobType.maxJobRuntimeMin = 2700
config.JobType.allowUndistributedCMSSW = True

# For MC
config.JobType.pyCfgParams = ['isMC=True', 'maxEvents=-1']

config.Data.inputDataset = '/QCD_PT-15to7000_TuneCP5_Flat_13p6TeV_pythia8/Run3Summer22MiniAODv4-124X_mcRun3_2022_realistic_v12-v2/MINIAODSIM'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 2
config.Data.publication = False
config.Data.outLFNDirBase = '/store/user/<your_username>/'

config.Site.storageSite = 'T2_CH_CERN'
```

Then submit with:
```bash
crab submit -c crab_config_ue.py
```

### Tips for UE production

- **For minimum bias/QCD samples**: Use `FileBased` splitting with 2-5 files per job
- **For data**: Always specify the appropriate golden JSON lumimask
- **Storage**: Ensure you have write access to the specified T2/T3 site
- **Output**: Files will be named `ue_nano_<tag>_<mc|data>.root`

For more details, see the [CRAB documentation](https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideCrab).
