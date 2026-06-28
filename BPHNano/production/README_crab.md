# CRAB submission (upsilon & zllv campaigns)

End-to-end multicrab for the slim BPHNano channels. Two pieces per channel:

| channel | cfg (test/) | generator | sample list | submit script |
|---------|-------------|-----------|-------------|---------------|
| Upsilon→4ℓ | `run_upsilon4l_cfg.py` | `gen_samples_upsilon.py` | `samples_upsilon.yml` | `submit_upsilon_crab.py` |
| Z→ℓℓV    | `run_zllv_cfg.py`      | `gen_samples_zllv.py`    | `samples_zllv.yml`    | `submit_zllv_crab.py` |

`crab_submit.sh` is the all-in-one wrapper: it sets up CMSSW + CRAB + checks the proxy, then
runs the chosen submit script. The submit scripts are generic — same engine, different cfg/yaml.

## 0. One-time per shell
```bash
voms-proxy-init -rfc -voms cms -valid 192:00      # grid proxy (192h)
```
`crab_submit.sh` does `cmsenv` + `source crab-setup.sh` for you (auto-detects the release area).

## 1. (Re)generate the sample list   — only when datasets/GTs/golden change
Queries DAS for the exact per-part MINIAOD paths and writes the yaml with the PPD-recommended
GlobalTag + golden-JSON per year. The generators print the yaml to stdout, so run them directly
(after `cmsenv` + proxy, for `dasgoclient`) and redirect:
```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ../../.. && cmsenv && cd -      # or any shell with cmsenv done
python3 gen_samples_zllv.py > samples_zllv.yml
```
Edit the `SAMPLES`/`GROUPS` dict at the top of the generator to change era coverage or campaign.
If the yaml is already good, skip this step.

## 2. Preview (dry-run) — always do this first
```bash
./crab_submit.sh submit_zllv_crab.py --dry-run -f '*'
```
Prints one line per task: dataset, pyCfgParams, lumiMask, splitting/cores, site/LFN. No proxy
needed, nothing submitted.

## 3. Submit
```bash
./crab_submit.sh submit_zllv_crab.py -f '*' \
    --tag zllv_$(date +%Y%b%d) \
    --numcores 8 --unitsperjob 100 --maxmemory 16000 \
    --site T3_US_FNALLPC --outputdir /store/user/$USER/zllv
```
- one CRAB task per dataset; output → `<outputdir>/<workArea>/...`
- `--tag` goes into both the requestName and the workArea — **keep it unique** vs any other live
  submission (so names don't collide).
- HARD-STOPS before submitting if any GlobalTag/lumimask still contains `VERIFY`.

### Upsilon equivalent
```bash
./crab_submit.sh submit_upsilon_crab.py -f '*' \
    --mode 4l --skim --tag y4l_$(date +%Y%b%d) \
    --numcores 8 --unitsperjob 200 --maxmemory 16000 \
    --site T3_US_FNALLPC --outputdir /store/user/$USER/y4l
```

## Key flags (both submit scripts)
| flag | meaning |
|------|---------|
| `-f GLOB` | sample-name filter (`'*'`, `'data_Muon0_2025'`, `'data_Run2024*'`) |
| `--tag T` | campaign tag → requestName + workArea (default: today's date) |
| `--numcores N` | cores/job → `JobType.numCores` **and** pset `nThreads=N` (multithreaded cmsRun) |
| `--unitsperjob N` | files/job (`FileBased`); overrides `common.<type>.splitting` in the yaml |
| `--maxmemory MB` | per-job memory; use ~2000×numcores (e.g. 16000 for 8 cores) |
| `--site` / `--outputdir` | storage site + LFN base |
| `--mode` | upsilon: `4mu`/`4l`; zllv: `mumu`/`ee`/`all` (else per-sample value from yaml) |
| `--skim` (upsilon) / default-on, `--noskim` (zllv) | keep only events with ≥1 candidate |
| `--test` | cap each task to 10 units (quick grid test) |
| `--dry-run` | preview only |

## Status / kill
```bash
# status of a whole campaign (loops crab status over the tasks):
./crab_submit.sh submit_zllv_crab.py -c status -t zllv_2026Jun19 -f '*'
# or per task directly:
crab status -d ZLLV_zllv_2026Jun19_data_Muon0_2025/crab_Muon0_Run2025D_PromptReco_v1_zllv_2026Jun19
# kill a task:
crab kill -d <project_dir>
```

## Gotchas (learned the hard way)
- **Forking submit.** Each `crab submit` runs in its own `multiprocessing.Process`. CRAB caches
  the imported pset in-process, so looping submits with different per-sample pyCfgParams (GT, mode)
  in ONE process dies with *"A different CMSSW configuration was already cached"*. The fork gives a
  fresh cache each task — do NOT "optimize" it away.
- **`nThreads` must be registered in the cfg.** Both cfgs register a `nThreads` VarParsing option
  that sets `process.options.numberOfThreads`. The submit script always passes `nThreads=<numcores>`;
  if a cfg lacks the option, every task fails at config import with *"'nThreads' not registered"*.
- **golden JSON.** `lumimask` in the yaml is a `cms-service-dqmdc` URL — CRAB reads URLs directly,
  no local download. Swap to a local path if you prefer.
- **ReReco version scatter.** Across the 8 parking parts, the `-vN` suffix differs per part, so the
  yaml lists the *exact* full dataset paths (no `%d` template). The generators handle this via DAS.
- **`submit_on_crab.py` (the old generic script) is NOT for these channels** — it emits
  `decay=`/`tag=` pyCfgParams that `run_{upsilon4l,zllv}_cfg.py` reject. Use the dedicated scripts.
- **Resubmitting same tag** → kill the old server tasks first (`crab kill`) and `rm -rf` the local
  `<tag>` workArea dirs, else you get "working area already exists" / duplicate tasks.
