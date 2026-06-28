#!/bin/bash
# All-in-one CRAB driver: sets up CMSSW + CRAB + checks the proxy, then runs a submit
# script (submit_zllv_crab.py / submit_upsilon_crab.py) forwarding all extra args to it.
#
# Usage:
#   ./crab_submit.sh <submit_script.py> [args...]
#
# Examples:
#   # dry-run preview (no env-sensitive ops, but still sets up env):
#   ./crab_submit.sh submit_zllv_crab.py --dry-run -f '*'
#
#   # real submission (zllv, full campaign, multicore, skim, to FNAL):
#   ./crab_submit.sh submit_zllv_crab.py -f '*' --tag zllv_$(date +%Y%b%d) \
#       --numcores 8 --unitsperjob 100 --maxmemory 16000 \
#       --site T3_US_FNALLPC --outputdir /store/user/$USER/zllv
#
#   # status of a campaign:
#   ./crab_submit.sh submit_zllv_crab.py -c status -t zllv_2026Jun19 -f '*'
#
# Release area is auto-detected from this script's location.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"          # .../PhysicsTools/BPHNano/production
SRC="$(cd "$HERE/../../.." && pwd)"                            # .../CMSSW_X/src

SCRIPT="${1:?usage: crab_submit.sh <submit_script.py> [args...]}"; shift
FWD=("$@")                                                     # forwarded args for the python script
set --                                                         # clear $@ so sourced setup scripts don't parse them

export SCRAM_ARCH=el9_amd64_gcc12
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd "$SRC"
eval $(scramv1 runtime -sh)                                   # cmsenv
source /cvmfs/cms.cern.ch/common/crab-setup.sh               # default 'prod' (no args)

# need a valid proxy for a real submit/status (dry-run is harmless without one)
if [[ " ${FWD[*]} " != *" --dry-run "* ]]; then
    voms-proxy-info -exists -valid 1:00 2>/dev/null || {
        echo ">>> No valid grid proxy. Run:  voms-proxy-init -rfc -voms cms -valid 192:00"; exit 2; }
fi

cd "$HERE"
echo ">>> python3 $SCRIPT ${FWD[*]}"
exec python3 "$SCRIPT" "${FWD[@]}"
