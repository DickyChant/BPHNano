#!/usr/bin/env python3
"""crab kill every task in a campaign workarea.

    python3 kill_campaign.py BCJPSILAMP_2026Aug30bc

Globs <TAG>_*/crab_* under this directory and kills each in parallel, the same
way mm_status.py sweeps `crab status`.  Killing is idempotent: tasks that have
already finished report an error, which is counted and printed, not fatal.
"""
import glob, os, sys
from multiprocessing import Pool
from CRABAPI.RawCommand import crabCommand

TAG = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: kill_campaign.py <TAG>')
HERE = os.path.dirname(os.path.abspath(__file__))


def one(d):
    try:
        crabCommand('kill', dir=d)
        return (True, os.path.basename(d), '')
    except Exception as e:
        return (False, os.path.basename(d), str(e)[:90])


def main():
    dirs = sorted(glob.glob(os.path.join(HERE, TAG + '_*', 'crab_*')))
    print('tasks to kill: %d' % len(dirs))
    if not dirs:
        sys.exit('no task directories matched %s_*/crab_*' % TAG)
    with Pool(8) as p:
        res = p.map(one, dirs)
    ok = sum(1 for r in res if r[0])
    print('KILL: attempted %d, accepted %d' % (len(res), ok))
    for r in res:
        if not r[0]:
            print('  FAIL %s : %s' % (r[1], r[2]))


if __name__ == '__main__':
    main()
