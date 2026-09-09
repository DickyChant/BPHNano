# zllv CRAB submissions — please run from your (ylo) account

Hi ylo — sqian's grid fair-share/priority is stalled: **all** of sqian's CRAB jobs (even clean
2022–2023 *data*, which matches trivially) have sat 100% idle for days, while **your** jobs are
scheduling fine (fresh output on EOS today). So could you submit the two things below from your
account? They'll land in **your** `/store/user/ylo/zllv/` area.

Two tasks:
1. **DY MC** (spurious-signal background) — 2 generators: amcatnloFXFX + madgraphMLM.
2. **2022–2023 muon data** (optional but wanted) — extends the μμφ statistics.

---

## 0. Setup (every shell)
```bash
export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd <your CMSSW_15_0_15/src that has PhysicsTools/BPHNano>   # your existing zllv checkout
eval $(scramv1 runtime -sh)
source /cvmfs/cms.cern.ch/common/crab-setup.sh
voms-proxy-init -rfc -voms cms -valid 192:00
```

## 1. Grab the two driver files (from sqian's area — read-only OK)
Copy them into **your** `PhysicsTools/BPHNano/production/`:
```bash
cd $CMSSW_BASE/src/PhysicsTools/BPHNano/production
cp /uscms_data/d3/sitianq/bph_nano/CMSSW_15_0_15/src/PhysicsTools/BPHNano/production/submit_zllv_crab.py .
cp /uscms_data/d3/sitianq/bph_nano/CMSSW_15_0_15/src/PhysicsTools/BPHNano/production/samples_zllv.yml .
```
(Your `../test/run_zllv_cfg.py` from your zllv checkout is used automatically — same producer you
already ran for the data.)

## 2. Submit the DY MC (both generators)
```bash
python3 submit_zllv_crab.py -c submit -t zllv_dymc_ylo -f 'mc_DYto2Mu_Summer24*' \
    --numcores 2 --maxmemory 4000 --unitsperjob 10 --ignore-locality \
    --outputdir /store/user/ylo/zllv
```
- `mc_DYto2Mu_Summer24*` matches **both** samples (amcatnloFXFX **and** madgraphMLM) → 2 tasks.
- `--ignore-locality` is **required** for DY: its MiniAOD is only on T1 disk/tape, so jobs must run
  at a T2 and xrootd-read it. The script whitelists well-connected T2s near the disk copies
  (US/IT/CH/DE/FR/UK/RU/BE) so they match *and* read fast (avoids the "idle too long" 50665 kill).
- `2 core / 4000 MB`, `10 files/job` — modest, matches easily.

## 3. Submit the 2022–2023 muon data (optional)
```bash
python3 submit_zllv_crab.py -c submit -t zllv_2022_2023_ylo -f 'data_Muon*_202[23]' \
    --numcores 2 --maxmemory 4000 \
    --outputdir /store/user/ylo/zllv
```
- Matches `data_Muon_2022` (5 eras, `/Muon` C–G) + `data_Muon0_2023` + `data_Muon1_2023` (7 eras each).
- 22Sep2023 reReco, GT `150X_dataRun3_v2`, golden JSONs baked into the yml. No `--ignore-locality`
  needed for data (well-distributed) — but if any sits idle with 50665, add it.

## 4. Check status
```bash
python3 submit_zllv_crab.py -c status -t zllv_dymc_ylo -f '*'
python3 submit_zllv_crab.py -c status -t zllv_2022_2023_ylo -f '*'
# or per task:  crab status -d ZLLV_zllv_dymc_ylo_mc_DYto2Mu_Summer24/crab_*
```
Healthy = jobs moving to **running/finished** within a few hours. Output appears under
`/store/user/ylo/zllv/ZLLV_zllv_dymc_ylo_*/` and `.../ZLLV_zllv_2022_2023_ylo_*/`.

## Notes / gotchas
- **`--outputdir /store/user/ylo/zllv`** must use your CRAB username (`ylo`), not a login name —
  CRAB rejects a mismatched LFN base with an HTTP 400 "Invalid input parameter".
- If a submit refuses because a workArea already exists, `rm -rf` that stub dir and re-run.
- Ping sqian when they're running; we'll harvest the output the same way as your data.

Thanks!! 🙏
