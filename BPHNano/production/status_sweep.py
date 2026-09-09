#!/usr/bin/env python3
"""Parallel `crab status` across a campaign workarea -> one summary.

    python3 status_sweep.py D0KSMM_2026Sep04

Runs `crab status` on every <TAG>_*/crab_* under this directory 8-way parallel and
aggregates task states, job states and failures, because 216 sequential status calls
take the better part of an hour.  Writes the raw per-task result to <TAG>_status.json
so a later look does not have to re-query the server.
"""
import collections
import glob
import json
import os
import sys
from multiprocessing import Pool

from CRABAPI.RawCommand import crabCommand

TAG = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: status_sweep.py <TAG>')
HERE = os.path.dirname(os.path.abspath(__file__))


def one(d):
    try:
        r = crabCommand('status', dir=d)
        return dict(dir=d, ok=True, sched=r.get('dagStatus'), task=r.get('status'),
                    jobs=r.get('jobsPerStatus') or {})
    except Exception as e:
        return dict(dir=d, ok=False, err=str(e)[:120], jobs={})


def main():
    dirs = sorted(glob.glob(os.path.join(HERE, TAG + '_*', 'crab_*')))
    print('tasks: %d' % len(dirs), flush=True)
    if not dirs:
        sys.exit('no task directories matched %s_*/crab_*' % TAG)
    with Pool(8) as p:
        res = p.map(one, dirs)
    json.dump(res, open(os.path.join(HERE, TAG + '_status.json'), 'w'))

    tst = collections.Counter()
    jobs = collections.Counter()
    bad = 0
    for r in res:
        if not r['ok']:
            bad += 1
            continue
        tst[str(r.get('sched') or r.get('task'))] += 1
        for k, v in r['jobs'].items():
            jobs[k] += v
    tot = sum(jobs.values()) or 1
    print('\n=== TASK STATE ===')
    for k, v in tst.most_common():
        print('  %-16s %d' % (k, v))
    if bad:
        print('  %-16s %d  (status query itself failed)' % ('QUERY-FAILED', bad))
    print('\n=== JOBS ===')
    for k, v in jobs.most_common():
        print('  %-14s %7d  %5.1f%%' % (k, v, 100.0 * v / tot))
    print('  %-14s %7d' % ('TOTAL', tot))
    print('\nCOMPLETION: %.1f%% (%d/%d)   failed=%d (%.2f%%)'
          % (100.0 * jobs.get('finished', 0) / tot, jobs.get('finished', 0), tot,
             jobs.get('failed', 0), 100.0 * jobs.get('failed', 0) / tot))
    fl = [(r['jobs']['failed'], os.path.basename(r['dir'])[5:])
          for r in res if (r.get('jobs') or {}).get('failed')]
    if fl:
        fl.sort(reverse=True)
        print('\ntasks with failures (top 8):')
        for n, name in fl[:8]:
            print('  %-5d %s' % (n, name))


if __name__ == '__main__':
    main()
