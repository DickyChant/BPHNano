#!/usr/bin/env python

import os
from argparse import ArgumentParser
from fnmatch import fnmatch
import yaml

import re
import datetime

try:
    from schema import Schema, And, Optional, SchemaError  # type: ignore
    _HAS_SCHEMA = True
except ImportError:
    # CMSSW environments often don't have extra pip deps installed.
    # We provide a lightweight validator below so this script still runs.
    _HAS_SCHEMA = False
    Schema = And = Optional = SchemaError = None  # type: ignore

from http.client import HTTPException


production_tag = datetime.date.today().strftime('%Y%b%d')


def parse_args():
    parser = ArgumentParser(description="A multicrab submission script")
    parser.add_argument('-y', '--yaml', default = 'test_samples.yml', help = 'File with dataset descriptions')
    parser.add_argument('-c', '--cmd', default='submit', choices = ['submit', 'status'], help= 'Crab command')
    parser.add_argument('-f', '--filter', default='*', help = 'filter samples, POSIX regular expressions allowed') 
    parser.add_argument('-w', '--workarea', default='BPHNANO_%s' % production_tag, help = 'Crab working area name')
    parser.add_argument('-o', '--outputdir', default= '/store/user/%s/' % os.environ.get('USER', 'sqian'), help='LFN Output high-level directory: the LFN will be saved in outputdir+workarea ')
    parser.add_argument('-s', '--site', default=None, help='Override CRAB storage site (config.Site.storageSite). If not set, the script will use YAML (samples.*.site or common.(data|mc).site) and fall back to T3_CH_CERNBOX.')
    parser.add_argument('-t', '--tag', default=production_tag, help='Production Tag extra')
    parser.add_argument('-p', '--psetcfg', default="../test/run_bphNano_cfg.py", help='Plugin configuration file')
    parser.add_argument('-e', '--extra', nargs='*', default=list(),  help='Optional extra input files')
    parser.add_argument('-tt', '--test', action='store_true', help='Flag a test job')
    parser.add_argument('-d', '--dir', default=None, help='For --cmd status: CRAB task directory (e.g. crab_projects/...)')
    return parser.parse_args()
    
def submit(config):
    try:
        from CRABAPI.RawCommand import crabCommand
        from CRABClient.ClientExceptions import ClientException
        crabCommand('submit', config = config)
    except ImportError as ie:
        print("Failed importing CRAB python modules.")
        print("Make sure CRAB is setup (e.g. `source /cvmfs/cms.cern.ch/common/crab-setup.sh`).")
        print("If you see `No module named 'past'`, install dependency with:")
        print("  python3 -m pip install --user future")
        raise
    except HTTPException as hte:
        print("Failed submitting task: %s" % (hte.headers))
    except ClientException as cle:
        print("Failed submitting task: %s" % (cle))

def status(directory):
    try:
        from CRABAPI.RawCommand import crabCommand
        from CRABClient.ClientExceptions import ClientException
        crabCommand('status', dir=directory)
    except ImportError:
        print("Failed importing CRAB python modules.")
        print("Make sure CRAB is setup (e.g. `source /cvmfs/cms.cern.ch/common/crab-setup.sh`).")
        print("If you see `No module named 'past'`, install dependency with:")
        print("  python3 -m pip install --user future")
        raise
    except HTTPException as hte:
        print("Failed submitting task: %s" % (hte.headers))
    except ClientException as cle:
        print("Failed submitting task: %s" % (cle))


if _HAS_SCHEMA:
    expected_schema = Schema({
        Optional("common"): {
            Optional("data"): {
                Optional("lumimask"): And(str, error="lumimask should be a string"),
                Optional("splitting"): And(int, error="splitting should be an integer"),
                Optional("globaltag"): And(str, error="globaltag should be a string"),
                Optional("site"): And(str, error="site should be a string"),
            },
            Optional("mc"): {
                Optional("splitting"): And(int, error="splitting should be an integer"),
                Optional("globaltag"): And(str, error="globaltag should be a string"),
                Optional("site"): And(str, error="site should be a string"),
            },
        },
        "samples": And(
            dict,
            error="samples should be a dict with keys dataset (str), isMC (bool). Optional keys: globaltag (str), site (str), parts (list(int))",
        ),
    })

    samples_schema = Schema({
        "dataset": And(str, error="dataset should be a string"),
        "isMC": And(bool, error="isMC should be a boolean"),
        Optional("decay"): And(str, error="decay to reconstruct"),
        Optional("goldenjson"): And(str, error="golden json file path should be a string"),
        Optional("lumimask"): And(str, error="lumimask should be a string"),
        Optional("globaltag"): And(str, error="globaltag should be a string"),
        Optional("site"): And(str, error="site should be a string"),
        Optional("parts"): [And(int, error="parts should be a list of integers")],
    })
else:
    expected_schema = None
    samples_schema = None


def validate_yaml(data):
    def _require(cond, msg):
        if not cond:
            raise RuntimeError(f"YAML structure is invalid: {msg}")

    def _opt_str(dct, key, where):
        if key in dct:
            _require(isinstance(dct[key], str), f"{where}.{key} should be a string")

    def _opt_int(dct, key, where):
        if key in dct:
            _require(isinstance(dct[key], int), f"{where}.{key} should be an integer")

    if _HAS_SCHEMA:
        try:
            expected_schema.validate(data)
            for name, content in data["samples"].items():
                samples_schema.validate(content)
            print("YAML structure is valid.")
            return
        except SchemaError as e:
            print("YAML structure is invalid:", e)
            import sys
            sys.exit(1)

    # Minimal builtin validation (no external dependencies)
    _require(isinstance(data, dict), "top-level YAML must be a mapping")
    _require("samples" in data, "missing required top-level key: samples")
    _require(isinstance(data["samples"], dict), "samples must be a mapping of sample_name -> sample_config")

    common = data.get("common", {})
    _require(isinstance(common, dict), "common must be a mapping if provided")
    for dtype in ("data", "mc"):
        if dtype in common:
            _require(isinstance(common[dtype], dict), f"common.{dtype} must be a mapping")
            _opt_str(common[dtype], "lumimask", f"common.{dtype}")
            _opt_int(common[dtype], "splitting", f"common.{dtype}")
            _opt_str(common[dtype], "globaltag", f"common.{dtype}")
            _opt_str(common[dtype], "site", f"common.{dtype}")

    for sname, sinfo in data["samples"].items():
        _require(isinstance(sname, str), "sample names (keys under samples) must be strings")
        _require(isinstance(sinfo, dict), f"samples.{sname} must be a mapping")
        _require("dataset" in sinfo, f"samples.{sname}.dataset is required")
        _require(isinstance(sinfo["dataset"], str), f"samples.{sname}.dataset should be a string")
        _require("isMC" in sinfo, f"samples.{sname}.isMC is required")
        _require(isinstance(sinfo["isMC"], bool), f"samples.{sname}.isMC should be a boolean")
        _opt_str(sinfo, "decay", f"samples.{sname}")
        _opt_str(sinfo, "goldenjson", f"samples.{sname}")
        _opt_str(sinfo, "lumimask", f"samples.{sname}")
        _opt_str(sinfo, "globaltag", f"samples.{sname}")
        _opt_str(sinfo, "site", f"samples.{sname}")
        if "parts" in sinfo:
            _require(isinstance(sinfo["parts"], list), f"samples.{sname}.parts should be a list of integers")
            _require(all(isinstance(x, int) for x in sinfo["parts"]), f"samples.{sname}.parts should be a list of integers")

    print("YAML structure is valid (builtin validation, schema package not installed).")
  

if __name__ == '__main__':

    args = parse_args()
    with open(args.yaml, "r") as f:
        samples = yaml.safe_load(f) # Parse YAML file
    validate_yaml(samples)
  
    if args.cmd == "submit":
        print("")
        print(f"Submit Crab jobs for {args.yaml} with filter {args.filter} applied")
        
        common_config = samples.get('common', {'data' : {}, 'mc' : {}})
        output_base = args.outputdir.rstrip('/')
        out_lfn_dir_base = f"{output_base}/{args.workarea}"

        # loop over samples
        for sample, sample_info in samples['samples'].items():
            parts = sample_info['parts'] if 'parts' in sample_info else [None]
            for part in parts:
                name = sample % part if part is not None else sample

                # filter names according to what we need
                if not fnmatch(name, args.filter):
                    continue

                data_type = 'mc' if sample_info['isMC'] else 'data'

                # Site precedence: CLI > per-sample > common.(data|mc) > fallback
                site = (
                    args.site
                    or sample_info.get('site', None)
                    or common_config.get(data_type, {}).get('site', None)
                    or 'T3_CH_CERNBOX'
                )

                # Golden JSON / lumiMask: sample overrides common
                lumimask = (
                    sample_info.get('lumimask', None)
                    or sample_info.get('goldenjson', None)
                    or common_config.get('data', {}).get('lumimask', None)
                )

                globaltag = sample_info.get('globaltag', "auto:run3_data")
                if globaltag == "auto:run3_data":
                    globaltag = common_config.get(data_type, {}).get('globaltag', "auto:run3_data")

                decay = sample_info.get('decay', 'all')
                maxevents = -1

                try:
                    from CRABClient.UserUtilities import config as crab_config
                except ImportError:
                    print("Failed importing CRAB python modules (CRABClient).")
                    print("Make sure CRAB is setup (e.g. `source /cvmfs/cms.cern.ch/common/crab-setup.sh`).")
                    print("If you see `No module named 'past'`, install dependency with:")
                    print("  python3 -m pip install --user future")
                    raise

                config_ = crab_config()

                config_.General.transferOutputs = True
                config_.General.transferLogs = True
                config_.General.workArea = args.workarea + "_" + name
                config_.General.requestName = name + "_" + production_tag

                config_.Data.publication = False
                config_.Data.outLFNDirBase = out_lfn_dir_base
                config_.Data.inputDBS = 'global'
                config_.Data.inputDataset = (
                    sample_info['dataset'] % part
                    if part is not None else
                    sample_info['dataset']
                )
                config_.Data.splitting = 'FileBased'
                config_.Data.unitsPerJob = common_config.get(data_type, {}).get('splitting', None)
                config_.Data.lumiMask = lumimask if not sample_info['isMC'] else ''

                config_.JobType.pluginName = 'Analysis'
                config_.JobType.psetName = args.psetcfg
                config_.JobType.maxJobRuntimeMin = 2700 # can not use with Automatic 
                config_.JobType.allowUndistributedCMSSW = True
                config_.JobType.inputFiles = args.extra
                config_.JobType.pyCfgParams = [
                    'isMC=%s' % sample_info['isMC'], 'reportEvery=1000',
                    'tag=%s' % production_tag,
                    'globalTag=%s' % globaltag,
                    'decay=%s' % decay,
                    'maxEvents=%s' % maxevents,
                 ]
                # Determine output filename based on config file
                if 'run_UE' in args.psetcfg or 'UE' in args.psetcfg:
                    output_filename = 'ue_nano.root'
                else:
                    output_filename = 'bph_nano.root'
                config_.JobType.outputFiles = [output_filename]

                config_.Site.storageSite = site

                if args.test:
                    config_.Data.totalUnits = 10

                print(name)
                print(f"Submit Crab job for {name} (site={site}, outLFNDirBase={out_lfn_dir_base})")
                print(config_)
                submit(config_)
    elif args.cmd == "status":
        if not args.dir:
            raise RuntimeError("For --cmd status you must pass --dir <crab_task_dir>")
        print(f"Getting crab status for {args.dir}")
        status(args.dir)
    else:
        print(f"Invalid Crab command : {args.cmd}")
    

