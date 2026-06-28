# Z→ℓℓV (zllv-15x) — all-in-one: from empty area to CRAB submission

Copy-paste from a bare lxplus/cmslpc (el9) shell. Produces the slim Z→ℓℓV NanoAOD and submits
the standard `/Muon0` + `/EGamma0` (2024+2025) campaign to the grid. ~20 min of build + setup.

---

## Step 0 — shell environment (every new shell)
```bash
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init -rfc -voms cms -valid 192:00          # grid proxy (for DAS + CRAB)
```

## Step 1 — make the CMSSW release
```bash
cd /uscms_data/d3/sitianq/bph_nano          # your working dir
cmsrel CMSSW_15_0_15
```

## Step 2 — clone the package + build
```bash
cd CMSSW_15_0_15/src
cmsenv
git cms-init
git clone -b zllv-15x https://github.com/DickyChant/BPHNano.git PhysicsTools
git cms-addpkg PhysicsTools/NanoAOD
scram b -j8
```
⚠️ **Gotcha:** `git cms-addpkg` can silently drop tracked files from the BPHNano working tree
(e.g. `python/common_cff.py`). `scram b` still "succeeds" but `cmsRun` later dies with
`No module named PhysicsTools.BPHNano.common_cff`. Guard against it:
```bash
cd PhysicsTools/BPHNano
git status                                  # look for deleted (' D') tracked files
git checkout -- .                           # restore any that were dropped
cd ../.. && scram b -j8 python && cd PhysicsTools/BPHNano
```

## Step 3 — (optional) validate the build on a few real events
```bash
cd test
F=$(dasgoclient -query="file dataset=/Muon0/Run2025D-PromptReco-v1/MINIAOD" | head -1)
cmsRun run_zllv_cfg.py inputFiles="root://cms-xrd-global.cern.ch/$F" \
    isMC=0 mode=mumu trigger="HLT_IsoMu24_v* HLT_Mu50_v*" \
    globalTag=150X_dataRun3_Prompt_v1 outputFiles=/tmp/zllv_test.root maxEvents=2000
cd ..
```

## Step 4 — (re)generate the sample list   *(skip if `samples_zllv.yml` already present)*
```bash
cd production
python3 gen_samples_zllv.py > samples_zllv.yml      # DAS query: exact paths + PPD GT + golden URL
```

## Step 5 — preview (dry-run, no submission)
```bash
./crab_submit.sh submit_zllv_crab.py --dry-run -f '*'
```

## Step 6 — submit (multicore, skim, to FNAL)
```bash
./crab_submit.sh submit_zllv_crab.py -f '*' \
    --tag zllv_$(date +%Y%b%d) \
    --numcores 8 --unitsperjob 100 --maxmemory 16000 \
    --site T3_US_FNALLPC --outputdir /store/user/$USER/zllv
```
`crab_submit.sh` is the all-in-one driver (cmsenv + crab-setup + proxy check, then the submit
script). 32 tasks: `/Muon0`→mumu, `/EGamma0`→ee, 2024 (MINIv6NANOv15, GT `150X_dataRun3_v2`) +
2025 (PromptReco, GT `150X_dataRun3_Prompt_v1`), golden JSON via URL, skim = ≥1 φ/ρ candidate.

## Step 7 — monitor
```bash
./crab_submit.sh submit_zllv_crab.py -c status -t zllv_$(date +%Y%b%d) -f '*'
# or a single task:  crab status -d production/ZLLV_<tag>_<sample>/crab_<requestName>
```

---

### Notes
- Full flag reference, the upsilon-channel equivalent, and the CRAB gotchas (forking submit, the
  `nThreads` cfg option, kill-before-resubmit) are in **`PhysicsTools/BPHNano/production/README_crab.md`**.
- Re-running a submit with the same `--tag` requires killing the old server tasks (`crab kill`) and
  removing the local `<tag>` workArea dirs first.
- The `production/submit_on_crab.py` that ships in the repo is the *old generic* script and does
  **not** work for zllv (passes `decay=`/`tag=` the cfg rejects) — use `submit_zllv_crab.py`.
