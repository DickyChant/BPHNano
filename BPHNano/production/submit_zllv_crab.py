#!/usr/bin/env python3
"""CRAB submission for the Upsilon->4mu/2mu2e slim NanoAOD.

Consumes samples_upsilon.yml (explicit per-dataset lists from gen_samples_upsilon.py)
and drives run_upsilon4l_cfg.py, passing the pset args it actually understands
(isMC / mode / globalTag / reportEvery / maxEvents) -- NOT decay/tag like the generic
submit_on_crab.py, which run_upsilon4l_cfg.py would reject.

One CRAB task per MINIAOD dataset. Submission HARD-STOPS if any GlobalTag or lumimask
still contains "VERIFY" (so placeholder samples can't be submitted by accident); use
--dry-run to preview configs without that check.

Examples:
  python3 submit_upsilon_crab.py --dry-run                       # preview all
  python3 submit_upsilon_crab.py -f 'data_Run2025*' --test       # 10-unit test jobs, 2025 only
  python3 submit_upsilon_crab.py -f 'data_Run2025D' \
        --site T3_US_FNALLPC --outputdir /store/user/<you>       # real submit
"""
import os
import datetime
from fnmatch import fnmatch
from argparse import ArgumentParser

import yaml

PROD_TAG = datetime.date.today().strftime('%Y%b%d')


def parse_args():
    p = ArgumentParser(description="Upsilon BPHNano CRAB submission")
    p.add_argument('-y', '--yaml', default='samples_zllv.yml', help='sample list')
    p.add_argument('-c', '--cmd', default='submit', choices=['submit', 'status'])
    p.add_argument('-f', '--filter', default='*', help='glob on sample name (e.g. data_Run2025*)')
    p.add_argument('-w', '--workarea', default='ZLLV_%s' % PROD_TAG)
    p.add_argument('-o', '--outputdir',
                   default='/store/user/%s/zllv' % os.environ.get('CERNUSERNAME', os.environ.get('USER', 'CHANGEME')),
                   help='output LFN base dir. Defaults to /store/user/$CERNUSERNAME/zllv (CRAB username, '
                        'e.g. sqian; falls back to $USER) -- matches the existing data/DY output area.')
    p.add_argument('-s', '--site', default='T3_US_FNALLPC', help='storage site')
    p.add_argument('-p', '--psetcfg', default='../test/run_zllv_cfg.py')
    p.add_argument('-m', '--mode', default=None, choices=['mumu', 'ee', 'all'],
                   help='override the per-sample mode (default: use sample value, else 4l)')
    p.add_argument('--maxevents', type=int, default=-1)
    p.add_argument('--numcores', type=int, default=1, help='cores/threads per job (CRAB numCores + pset nThreads)')
    p.add_argument('--maxmemory', type=int, default=2500, help='per-job memory cap MB (raise for many cores)')
    p.add_argument('--unitsperjob', type=int, default=None, help='files per job; default = common.<type>.splitting from yaml')
    p.add_argument('--noskim', action='store_true', help='disable the >=1-candidate skim (default: skim on)')
    p.add_argument('--ignore-locality', action='store_true',
                   help='run anywhere + xrootd-read the input (needed for MC only on T1/tape, e.g. DY; '
                        'avoids the "idle too long" 50665 kill from being pinned to slow/remote sites)')
    p.add_argument('-t', '--tag', default=PROD_TAG, help='campaign tag (in requestName + workArea); keep distinct from other live submissions')
    p.add_argument('--test', action='store_true', help='cap each task to 10 units')
    p.add_argument('--dry-run', action='store_true', help='print configs, do not submit (skips VERIFY check)')
    return p.parse_args()


def request_name(dataset, tag):
    # /ParkingDoubleMuonLowMass3/Run2025D-PromptReco-v1/MINIAOD -> ParkingDoubleMuonLowMass3_Run2025D_PromptReco_v1_<tag>
    _, primary, era, _tier = dataset.split('/')
    name = ('%s_%s_%s' % (primary, era, tag)).replace('-', '_')
    return name[:100]


def main():
    args = parse_args()
    if args.workarea == 'ZLLV_%s' % PROD_TAG:   # default workArea follows the campaign tag
        args.workarea = 'ZLLV_%s' % args.tag
    with open(args.yaml) as f:
        cfg = yaml.safe_load(f)
    common = cfg.get('common', {})

    selected = {n: s for n, s in cfg['samples'].items() if fnmatch(n, args.filter)}
    if not selected:
        print('No samples match filter %r' % args.filter)
        return

    # placeholder guard
    if not args.dry_run:
        bad = []
        for n, s in selected.items():
            gt = str(s.get('globaltag', ''))
            lm = str(s.get('lumimask', ''))
            if 'VERIFY' in gt or 'VERIFY' in lm:
                bad.append('  %s: globaltag=%s lumimask=%s' % (n, gt, lm))
        if bad:
            print('Refusing to submit: fill in these VERIFY_* placeholders first '
                  '(or use --dry-run):\n' + '\n'.join(bad))
            return
        if 'CHANGEME' in args.outputdir:
            print('Set --outputdir to your writable LFN area (e.g. /store/user/<you>).')
            return

    if args.cmd == 'status':
        from CRABAPI.RawCommand import crabCommand
        for n in selected:
            d = os.path.join(args.workarea + '_' + n)
            try:
                crabCommand('status', dir=d)
            except Exception as e:
                print('status failed for %s: %s' % (n, e))
        return

    if not args.dry_run:
        from CRABClient.UserUtilities import config
        from CRABAPI.RawCommand import crabCommand
        from multiprocessing import Process

    n_tasks = 0
    for sname, s in selected.items():
        datasets = s.get('datasets')
        if not datasets:  # legacy %d template fallback
            base = s['dataset']
            datasets = [base % p for p in s.get('parts', [None])] if '%d' in base else [base]
        isMC = bool(s.get('isMC', False))
        dtype = 'mc' if isMC else 'data'
        gt = s.get('globaltag') or common.get(dtype, {}).get('globaltag')
        splitting = args.unitsperjob or common.get(dtype, {}).get('splitting', 20)
        lumimask = s.get('lumimask') if not isMC else None
        mode = args.mode or s.get('mode', 'mumu')
        trigger = s.get('trigger', '')

        for ds in datasets:
            n_tasks += 1
            req = request_name(ds, args.tag)
            pyCfgParams = ['isMC=%s' % isMC, 'mode=%s' % mode, 'trigger=%s' % trigger,
                           'globalTag=%s' % gt, 'skim=%d' % (0 if args.noskim else 1),
                           'reportEvery=1000', 'maxEvents=%s' % args.maxevents,
                           'nThreads=%d' % args.numcores]
            # NanoAOD (EDM) output is auto-detected by CRAB from the cfg's NanoAODOutputModule;
            # do NOT declare it in JobType.outputFiles (that is for non-EDM/TFileService outputs,
            # and declaring a name the job never writes fails stageout with "output file not found").

            if args.dry_run:
                print('--- task %d: %s' % (n_tasks, req))
                print('    dataset    = %s' % ds)
                print('    pyCfgParams= %s' % pyCfgParams)
                print('    lumiMask   = %s' % lumimask)
                print('    split/cores= %d files/job, %d cores, %d MB' % (splitting, args.numcores, args.maxmemory))
                print('    site/LFN   = %s  %s/%s' % (args.site, args.outputdir, args.workarea))
                continue

            c = config()
            c.General.transferOutputs = True
            c.General.transferLogs = True
            c.General.workArea = args.workarea + '_' + sname
            c.General.requestName = req
            c.JobType.pluginName = 'Analysis'
            c.JobType.psetName = args.psetcfg
            c.JobType.pyCfgParams = pyCfgParams
            c.JobType.maxJobRuntimeMin = 2700
            c.JobType.numCores = args.numcores
            c.JobType.maxMemoryMB = args.maxmemory
            c.JobType.allowUndistributedCMSSW = True
            c.Data.inputDataset = ds
            c.Data.inputDBS = 'global'
            c.Data.splitting = 'FileBased'
            c.Data.unitsPerJob = splitting
            c.Data.publication = False
            c.Data.outLFNDirBase = args.outputdir + '/' + args.workarea
            if lumimask:
                c.Data.lumiMask = lumimask
            if args.test:
                c.Data.totalUnits = 10
            c.Site.storageSite = args.site
            if args.ignore_locality:
                # input only on T1/tape (e.g. DY MC). Neither extreme works: US-only whitelist
                # starves (0 matches/day), fully-open sends jobs to far sites that WAN-read the
                # input and get killed idle (50665). Balance: whitelist well-connected T2s in the
                # REGIONS that host a disk copy (FNAL-US, CNAF-IT, JINR-RU) -> many matching slots,
                # each with a fast read from a nearby copy. (No T3_US_FNALLPC: that pool is saturated.)
                c.Data.ignoreLocality = True
                c.Site.whitelist = ['T2_US_*', 'T2_IT_*', 'T2_CH_*', 'T2_DE_*',
                                    'T2_FR_*', 'T2_UK_*', 'T2_RU_*', 'T2_BE_*']

            print('Submitting %s' % req)
            # each submit in its own forked process: CRAB caches the imported pset in-process,
            # so looping submits with different pyCfgParams in one process fails with
            # "A different CMSSW configuration was already cached". A fresh fork avoids that.
            p = Process(target=crabCommand, args=('submit',), kwargs={'config': c})
            p.start()
            p.join()
            if p.exitcode != 0:
                print('  submit failed (exit %s)' % p.exitcode)

    print('\n%d task(s) %s' % (n_tasks, 'previewed (dry-run)' if args.dry_run else 'processed'))


if __name__ == '__main__':
    main()
