#!/bin/bash
# Script to submit UE (Underlying Events) jobs with corrected configuration
# Make sure you have: cmsenv and source /cvmfs/cms.cern.ch/common/crab-setup.sh

# Get today's date tag
TODAY=$(date +%Y%b%d)

# Submit UE jobs with the correct config file
python3 submit_on_crab.py \
    -y ue_samples.yml \
    -p ../test/run_UE_cfg.py \
    -w "New_UE_NANO_${TODAY}" \
    -c submit

echo ""
echo "Submission complete! Check status with:"
echo "  ./check_crab_status.sh status"

