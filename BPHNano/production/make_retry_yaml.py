#!/usr/bin/env python3
"""Build a reduced sample yaml containing ONLY the datasets whose CRAB task is in a
terminal-failed state (SUBMITREFUSED / SUBMITFAILED), so they can be resubmitted without
touching the tasks that are already running fine.

Terminal states cannot be recovered with `crab resubmit` -- the task must be submitted anew.

Usage:
  python3 make_retry_yaml.py <status_file> <in.yml> <tag> > retry.yml
    status_file : lines of "<STATE> <projectdir>"  (from the enumeration sweep)
    tag         : the campaign tag used to build requestNames

It reproduces submit_*_crab.py's request_name() exactly, so a dataset is matched to its
task by construction rather than by trying to reverse the name mangling.
"""
import sys
import yaml

BAD_STATES = ("SUBMITREFUSED", "SUBMITFAILED", "UNKNOWN")


def request_name(dataset, tag):
    _, primary, era, _tier = dataset.split('/')
    return ('%s_%s_%s' % (primary, era, tag)).replace('-', '_')[:100]


def main():
    status_file, in_yml, tag = sys.argv[1], sys.argv[2], sys.argv[3]

    bad = set()
    for line in open(status_file):
        parts = line.split()
        if len(parts) < 2:
            continue
        state, path = parts[0], parts[1]
        if state in BAD_STATES:
            bad.add(path.rstrip('/').split('/')[-1][len('crab_'):])

    cfg = yaml.safe_load(open(in_yml))
    out_samples = {}
    n_keep = n_drop = 0
    for sname, s in cfg['samples'].items():
        keep = [d for d in s['datasets'] if request_name(d, tag) in bad]
        n_keep += len(keep)
        n_drop += len(s['datasets']) - len(keep)
        if keep:
            s2 = dict(s)
            s2['datasets'] = keep
            out_samples[sname] = s2

    cfg['samples'] = out_samples
    sys.stderr.write("retry: %d dataset(s); leaving %d healthy task(s) alone\n" % (n_keep, n_drop))
    yaml.safe_dump(cfg, sys.stdout, default_flow_style=False, sort_keys=False)


if __name__ == '__main__':
    main()
