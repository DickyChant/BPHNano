#!/usr/bin/env python3
"""crab resubmit every task that still carries failed JOBS, optionally avoiding sites.

    python3 resubmit_jobfailures.py D0KSMM_2026Sep04 [T2_US_Nebraska,T2_US_Caltech]

status_sweep.py records jobsPerStatus per task; a task can be RUNNING or COMPLETED and
still hold failed jobs, which resubmit_failed.py (keyed on task state) will not catch.

Blacklisting is not free: DAS shows these datasets have a single US disk replica, so
excluding it forces WAN reads from the remaining copy.  Retries have already succeeded
that way, but it trades a site problem for a slower one.
"""
import json
import os
import sys
from multiprocessing import Pool

from CRABAPI.RawCommand import crabCommand

TAG = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: resubmit_jobfailures.py <TAG> [sites]')
BLACK = sys.argv[2] if len(sys.argv) > 2 else ''
HERE = os.path.dirname(os.path.abspath(__file__))


def one(d):
    args = ['--siteblacklist=%s' % BLACK] if BLACK else []
    try:
        crabCommand('resubmit', *args, dir=d)
        return (True, os.path.basename(d), '')
    except Exception as e:
        return (False, os.path.basename(d), str(e)[:110])


def main():
    rows = json.load(open(os.path.join(HERE, TAG + '_status.json')))
    dirs = [r['dir'] for r in rows if (r.get('jobs') or {}).get('failed')]
    tot = sum((r.get('jobs') or {}).get('failed', 0) for r in rows)
    print('tasks carrying failed jobs: %d  (%d jobs)' % (len(dirs), tot))
    print('site blacklist: %s' % (BLACK or '(none)'))
    if not dirs:
        sys.exit(0)
    for d in dirs:
        n = [r for r in rows if r['dir'] == d][0]['jobs'].get('failed')
        print('  %-4d %s' % (n, os.path.basename(d).replace('crab_', '')[:70]))
    with Pool(8) as p:
        res = p.map(one, dirs)
    ok = sum(1 for r in res if r[0])
    print('\nRESUBMIT: attempted %d, accepted %d' % (len(res), ok))
    for r in res:
        if not r[0]:
            print('  FAIL %s : %s' % (r[1].replace('crab_', ''), r[2]))


if __name__ == '__main__':
    main()
