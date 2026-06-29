# H/Z → J/ψ(→μ⁺μ⁻) φ(→K⁺K⁻)  — exclusive boson decay to two vector mesons

A search for the exclusive decays **H → J/ψ φ** and **Z → J/ψ φ**, reconstructed as
**μ⁺μ⁻ (J/ψ) + K⁺K⁻ (φ)**. This reuses the **`ZToLLVBuilder`** (dilepton + ditrack + 4-track
`KinVtxFitter`) unchanged — only the configuration differs from the Z→Vℓℓ channels.

## Physics / motivation
- Table 7 of König–Neubert (exclusive Higgs decays to a meson pair): **B(H→J/ψφ) ≈ 1×10⁻⁹**.
  The signature is gorgeous (μμKK, fully reconstructed, J/ψ and φ both narrow), but the **SM rate
  is tiny** → ~10⁴–10⁵ below HL-LHC reach. So this is a **limit / anomalous-Yukawa (Hcc, Hss) probe**,
  in the spirit of the existing H→J/ψγ, H→φγ searches — not an SM discovery.
- The **same final state from the Z** (Z→J/ψφ) is also targeted: σ(Z) ≫ σ(H), so the Z peak may be
  the more accessible one despite a different BR. Hence the parent-mass window spans **both 91 and 125**.
- **Acceptance is excellent**: from a 125 (or 91) GeV parent, J/ψ and φ are each hard
  (pT ≈ 45–68 GeV), so their daughters are well above threshold and central.

## Reconstruction (config-only; same C++ builder)
`python/ZToLLV_cff.py`:
- **`MuMuJpsi`** — `DiMuonBuilder`, J/ψ-windowed (m(μμ) 2.9–3.3), μ pT 4/3, Loose ID. The J/ψ→μμ is
  soft enough to fire **BParking `HLT_DoubleMu4_3_LowMass`** even when the J/ψ is boosted.
- **`HZToJpsiPhi`** — `_zllv(MuMuJpsi, K, φ-window 1.00–1.05, par_lo=70, par_hi=130)`: φ→K⁺K⁻ ditrack +
  prompt 4-track vertex; **parent window 70–130 spans the Z (91) and H (125)**. In the table,
  `mll` = m(J/ψ), `fitted_mass` = the parent (J/ψφ) mass. φ is required **prompt** (l_xy < 0.1)
  to reject φ/J/ψ from b-hadron decays.

## Build & run
```bash
scram b -j8
cmsRun PhysicsTools/BPHNano/test/run_zllv_cfg.py inputFiles=file:miniaod.root mode=jpsiphi \
    isMC=0 skim=1 trigger="HLT_DoubleMu4_3_LowMass_v*" outputFiles=jpsiphi_nano.root
# skim=1 keeps events with >=1 HZToJpsiPhi candidate; trigger="" => no HLT filter (mechanics)
```
Datasets: BParking `ParkingDoubleMuonLowMass` (J/ψ→μμ trigger) or `/Muon*` (single/di-muon HLT).

## ⚠ Reconstruction finding (300-evt H→J/ψφ MC, 2026-06-29)
**The boosted φ→KK is unresolvable, so the H peak at 125 is mostly lost** (reco eff ≈3% vs 66% gen
acc). Cause is physics, not the builder: **φ→KK Q-value = m_φ−2m_K = 32 MeV**, so a φ boosted to
~63 GeV (from the 125 H) emits its two kaons at **ΔR≈0.006** — far below the CMS ~0.02 two-track
limit (only 13% of φ→KK have ΔR>0.02). The real φ is reconstructed as ≤1 track; candidates pair the
(resolvable, ΔR~0.135) J/ψ→μμ with a soft combinatorial KK → m(J/ψφ) piles at ~90, not 125.
- Contrast Z→Vℓℓ (this same builder works there): the φ *recoils* against the ℓℓ and is **soft**
  (~7 GeV) → kaons ΔR~0.04, resolvable → ~36% eff. Hard 2-body φ vs soft recoil φ = opposite fate.
- ⇒ J/ψφ is doubly limited: B(H→J/ψφ)~1e-9 **and** an unreconstructable φ. The **reconstructable**
  exclusive-H→VV cousin is **H→J/ψJ/ψ→4μ** (both Q-values large → μ ΔR~0.135 resolvable; reuses the
  upsilon_4mu 4μ machinery). The builder/branch below are correct and kept for the record.

## Signal MC
- **H→J/ψφ**: `test/HToJpsiPhi_13p6TeV_cfi.py` — **ggH built-in Pythia8** + `25:addChannel` forcing
  H→J/ψφ, J/ψ→μμ, φ→KK. **This works** (unlike the Z, where `addChannel` is ignored): GEN verified
  h0→J/ψφ with both mesons from the Higgs, pT≈68 GeV. cmsDriver: `--step GEN,SIM` from this fragment.
- **Z→J/ψφ**: Pythia `addChannel` fails for the Z (production couples to decay → vanishing xsec) —
  use the **POWHEG-DY + LHE-decayer** route (cf. the `zllv` gridpacks), adapted to a 2-body
  Z→J/ψ(μμ)φ(KK) decay. *(TODO.)*
