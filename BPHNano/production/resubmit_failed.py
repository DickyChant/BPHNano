#!/usr/bin/env python3
"""crab resubmit every task a status sweep left in a given state.

    python3 resubmit_failed.py D0KSMM_2026Sep04 [STATE]

Reads <TAG>_status.json written by status_sweep.py rather than re-querying 216 tasks,
selects the tasks in STATE (default FAILED -- these are dead at task level and will not
retry on their own), and resubmits them 8-way parallel.  Resubmission is idempotent:
a task that has since recovered reports an error, which is counted and printed, not
fatal.
"""
import json
import os
import sys
from multiprocessing import Pool

from CRABAPI.RawCommand import crabCommand

TAG = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: resubmit_failed.py <TAG> [STATE]')
STATE = sys.argv[2] if len(sys.argv) > 2 else 'FAILED'
HERE = os.path.dirname(os.path.abspath(__file__))


def one(d):
    try:
        crabCommand('resubmit', dir=d)
        return (True, os.path.basename(d), '')
    except Exception as e:
        return (False, os.path.basename(d), str(e)[:110])


def main():
    js = os.path.join(HERE, TAG + '_status.json')
    rows = json.load(open(js))
    dirs = [r['dir'] for r in rows if r.get('task') == STATE]
    print('tasks in state %s: %d' % (STATE, len(dirs)))
    if not dirs:
        sys.exit(0)
    for d in dirs:
        print('  ' + os.path.basename(d).replace('crab_', ''))
    with Pool(8) as p:
        res = p.map(one, dirs)
    ok = sum(1 for r in res if r[0])
    print('\nRESUBMIT: attempted %d, accepted %d' % (len(res), ok))
    for r in res:
        if not r[0]:
            print('  FAIL %s : %s' % (r[1].replace('crab_', ''), r[2]))


if __name__ == '__main__':
    main()
