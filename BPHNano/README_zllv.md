# Z → ℓ⁺ℓ⁻ V ,  V → h⁺h⁻   (V = φ→K⁺K⁻ / ρ⁰→π⁺π⁻ ;  ℓ = μ, e)

Branch `zllv-15x` (CMSSW_15_0_15). A **first-observation search** for the rare Z decay
Z → V ℓ⁺ℓ⁻ (Bergström & Robinett, Phys. Lett. B **245** (1990) 249; B up to ~10⁻⁵ for light V).
Reads **standard `/Muon` and `/EGamma` Run3 MiniAOD** (NOT parking) and produces a slim NanoAOD
with a 4-track KinematicVertexFit, prompt + pT(hh) + isolation variables.

## What it builds
- `plugins/ZToLLVBuilder.cc` — dilepton + 2 tracks (V→hh) → 4-track vertex fit. Parametrized:
  lepton mass (μ/e) **and** track mass (π/K) are config doubles → one builder serves φ→KK and
  ρ→ππ, μμ and ee. Early V-mass window (`vMassMin/Max`) bounds the combinatorics. Saves the Z
  candidate (`fitted_mass`), `mll`, `m_ditrack`, `ditrack_pt` (pT of V), prompt vars
  (`l_xy`, `cos_theta_2D`), and `v_iso` (ΣpT in ΔR<0.4 around V, excl. the 2 V tracks).
- `plugins/ElectronMerger.cc` — standard `slimmedElectrons` → parallel `pat::ElectronCollection`
  + transient tracks, with the Run3 **cut-based MEDIUM ID** applied in C++, feeding `DiElectronBuilder`.
- `python/ZToLLV_cff.py` — `MuMuWide` (wide dimuon) + `ZElectrons`/`DiEle` + `ZToMuMu{Phi,Rho}` +
  `ZToEE{Phi,Rho}` + tables + count filters. Skim selection is kept **loose** (Z-window 70–110 +
  prompt `l_xy<0.1`); the **m(ℓℓ) Z-veto and isolation are applied OFFLINE** (both stored) so the
  m(ℓℓ)≈91 control sideband is preserved for background estimation.
- `python/nanoBPH_cff.py` — `nanoAOD_customizeZLLV(process, isMC, channels=('mumu','ee'))`.
- `test/run_zllv_cfg.py` — `mode=mumu|ee|all`, `trigger="HLT_IsoMu24_v* HLT_Mu50_v*"`,
  `skim=1` (≥1 candidate, OR'd filter paths), `wideWindow=1` (diagnostic).

## Setup (lxplus, el9)
```shell
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_15_0_15 && cd CMSSW_15_0_15/src && cmsenv
git cms-init
git clone -b zllv-15x https://github.com/DickyChant/BPHNano.git PhysicsTools
git cms-addpkg PhysicsTools/NanoAOD
scram b -j8
```

## Run
```shell
cd PhysicsTools/BPHNano/test
# mu mu V on /Muon:
cmsRun run_zllv_cfg.py inputFiles="file:muon_miniaod.root" isMC=0 mode=mumu \
    trigger="HLT_IsoMu24_v* HLT_Mu50_v*" globalTag=150X_dataRun3_Prompt_v1 outputFiles=zllv_mu.root
# ee V on /EGamma:
cmsRun run_zllv_cfg.py inputFiles="file:egamma_miniaod.root" isMC=0 mode=ee \
    trigger="HLT_Ele30_WPTight_Gsf_v*" globalTag=150X_dataRun3_Prompt_v1 outputFiles=zllv_ee.root
```

## CRAB
```python
config.JobType.psetName    = 'run_zllv_cfg.py'
# mu mu  -> /Muon0,/Muon1,/Muon2  ;  ee -> /EGamma0..3
config.JobType.pyCfgParams = ['isMC=0', 'mode=mumu', 'trigger=HLT_IsoMu24_v* HLT_Mu50_v*',
                              'globalTag=150X_dataRun3_Prompt_v1']
config.Data.inputDataset   = '/Muon0/Run2025C-PromptReco-v1/MINIAOD'
config.Data.splitting      = 'FileBased'
```

## Validated (10k evts each, Run2025C /Muon0 + /EGamma0 MiniAOD)
All 4 channels (μμ/ee × φ/ρ) reconstruct candidates; **m(KK) peaks on φ(1020)**; loose skim
≈3.3% (μμ) / 0.7% (ee) at ~2.1 KB/evt. The Z-box background is **Z→ℓℓ+hadrons** (m(ℓℓ)=m_Z,
soft pT(hh)≈4–6 GeV) — suppressed offline by the m(ℓℓ) Z-veto and **pT(hh)>~20 GeV** (a real
Z→V gives an energetic V, pT(hh)≈30–45 GeV); `v_iso` separates isolated signal from the
non-isolated background. Per-event ~40–66 ms (track cut pt>1.0).
