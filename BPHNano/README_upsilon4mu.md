# Υ(1S/2S/3S) → 4μ  and  Υ → 2μ2e  — slim BPHNano (CMSSW_15_0_15)

Branch `upsilon4mu-15x`. A trigger/cut port of the AN-25-223 η→4μ recipe to the Υ region,
producing a **slim** NanoAOD (~0.65 KB/event for both channels) with a real 4-track
KinematicVertexFit and prompt variables. Reads 2025/2026 Parking MiniAOD.

## Setup (lxplus, el9)
```shell
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_15_0_15 && cd CMSSW_15_0_15/src && cmsenv
git cms-init
# clone THIS branch as ./PhysicsTools  -> package lands at PhysicsTools/BPHNano
git clone -b upsilon4mu-15x https://github.com/DickyChant/BPHNano.git PhysicsTools
git cms-addpkg PhysicsTools/NanoAOD
scram b -j8
```

## Run
```shell
cd PhysicsTools/BPHNano/test
cmsRun run_upsilon4l_cfg.py \
    inputFiles="file:miniaod.root" isMC=0 mode=4l \
    globalTag=150X_dataRun3_Prompt_v1 outputFiles=ups4l_nano.root
```
- `mode=4mu` → 4μ only (no Track table, no 2μ2e).
- `mode=4l`  → 4μ **and** 2μ2e (adds LowPtElectron + the e-leg producer; +~35 B/evt).
- `wideWindow=1` → diagnostic: open the 4μ mass window + accept all fits (study the spectrum).
- MC: add `isMC=1` (gen matching + PU); pick the matching MC GlobalTag.

## What it produces (slim)
`UpsilonTo4Mu`, `UpsilonTo2Mu2E`, `Muon` (muonBPH AllMuons), `LowPtElectron`, `MuMu`
(wide-window dimuon), `PVtx_vz`+`nPVtx` (z of every good PV, for candidate↔PV matching),
central `PV_*`, HLT bits, (PU/gen on MC). No general-track / jet / MET / tau tables.

Prompt variables on both candidates: `l_xy`, `l_xy_unc`, `l_xy_sig`, `cos_theta_2D`,
`fitted_cos_theta_2D` (4μ also `max_mu_dz`); default `postVtxSelection` includes a loose
prompt cut `l_xy < 0.2 cm` (tunable — Υ is prompt). `UpsilonTo2Mu2E_trk{1,2}_idx` index
directly into the `LowPtElectron` table.

## CRAB
Point your CRAB `JobType.psetName` at `PhysicsTools/BPHNano/test/run_upsilon4l_cfg.py` and pass
the pset args via `JobType.pyCfgParams`, e.g.:
```python
config.JobType.psetName    = 'run_upsilon4l_cfg.py'
config.JobType.pyCfgParams = ['isMC=0', 'mode=4l', 'globalTag=150X_dataRun3_Prompt_v1']
config.Data.inputDataset   = '/ParkingDoubleMuonLowMass0/Run2025D-PromptReco-v1/MINIAOD'
config.Data.splitting      = 'FileBased'
```
(`outputFiles` is handled by CRAB; the cfg registers it.)

## Key implementation notes
- **2μ2e e-legs from LowPtElectron**, not generic tracks: `plugins/LowPtEleMerger.cc` reads
  `finalLowPtElectrons` as an `edm::View<pat::Electron>` (it is a RefVector) and emits
  `SelectedElectrons` + `SelectedTransientElectrons` (gsf-track transient tracks). This fixed
  a ~607-candidate/event combinatorial explosion (now ~0.01/evt, ~260× faster).
- `nanoAOD_customizeUpsilon4L` must `process.nanoSequence.associate(lowPtElectronTask,
  lowPtElectronTablesTask)` — a Task wrapped in a Sequence is not scheduled for a scheduled
  consumer.
- 15X port: removed `run3_nanoAOD_122/124` era modifiers in `globalsBPH_cff.py`; emptied
  `plugins/SimpleFlatTableProducerBPHPlugins.cc` (those producers are central in 15X).
- `PVertexBPHTable` gained a `slim` flag (vz-only) → `PVtx_vz` + `nPVtx`.
