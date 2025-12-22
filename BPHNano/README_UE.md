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

For large-scale production, you can use the CRAB submission system. Example configuration coming soon.
