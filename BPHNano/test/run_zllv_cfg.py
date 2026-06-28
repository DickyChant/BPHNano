####################### BPHNano: Z -> mu mu V , V -> h+h-  (phi->KK / rho->pipi) ######################
# Z -> V l+l- first-observation search (Bergstrom-Robinett PLB245(1990)249).
# Dataset: STANDARD muon PDs  /Muon0,/Muon1,/Muon2  (Run2025*-PromptReco MINIAOD) -- NOT
# ParkingDoubleMuonLowMass (parking is soft/busy and the wrong trigger). Single-muon HLT
# (HLT_IsoMu24 / HLT_Mu50) fires on one energetic Z lepton.  Skim: >=1 (phi OR rho) candidate.
#
# cmsRun test/run_zllv_cfg.py inputFiles="file:muon_miniaod.root" isMC=0 \
#     globalTag=150X_dataRun3_Prompt_v1 outputFiles=zllv_nano.root
#   trigger="HLT_IsoMu24_v* HLT_Mu50_v*"  -> require a single-muon path (production)
#   wideWindow=1  -> open the V + Z windows + accept all fits (mechanics check)
#   skim=0        -> keep ALL events (no >=1-candidate filter; for the mechanics check)
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'zllv_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
options.register('trigger', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "space-separated single-muon HLT wildcards to require (empty=none)")
options.register('skim', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "1: keep events with >=1 (phi OR rho) candidate; 0: keep all")
options.register('mode', 'mumu', VarParsing.multiplicity.singleton, VarParsing.varType.string, "lepton channel: 'mumu' (/Muon), 'ee' (/EGamma), or 'all'")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: open V+Z windows, accept all fits")
options.register('nThreads', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "cmsRun threads/streams (set = CRAB JobType.numCores)")
options.setDefault('maxEvents', -1)
options.parseArguments()

gt = options.globalTag
if gt == 'auto':
    gt = '150X_mcRun3_2024_realistic_v1' if options.isMC else '150X_dataRun3_Prompt_v1'

from Configuration.StandardSequences.Eras import eras
process = cms.Process('BPHNANO', eras.Run3)
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('PhysicsTools.BPHNano.nanoBPH_cff')
process.load('TrackingTools/TransientTrack/TransientTrackBuilder_cfi')

process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))
process.source = cms.Source("PoolSource", fileNames=cms.untracked.vstring(options.inputFiles))
process.options = cms.untracked.PSet(
    wantSummary=cms.untracked.bool(options.wantSummary),
    numberOfThreads=cms.untracked.uint32(options.nThreads),
    numberOfStreams=cms.untracked.uint32(0),   # 0 -> = numberOfThreads
)

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, gt, '')
process.nanoMetadata.strings.tag = cms.string(options.outputFiles)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(dataTier=cms.untracked.string('NANOAOD'), filterName=cms.untracked.string('')),
    fileName = cms.untracked.string(options.outputFiles),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep nanoaodFlatTable_*Table_*_*',          # Muon, MuMuWide?, ZToMuMuPhi/Rho, PV, (PU/gen on MC)
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',              # HLT bits
    ),
)

_channels = {'mumu': ('mumu',), 'ee': ('ee',), 'all': ('mumu', 'ee')}[options.mode]
from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeZLLV
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeZLLV(process, options.isMC, channels=_channels)

# the four V builders, by channel; only those for the active channel(s) exist on the process
_builders = []
if 'mumu' in _channels: _builders += [process.ZToMuMuPhi, process.ZToMuMuRho]
if 'ee'   in _channels: _builders += [process.ZToEEPhi,   process.ZToEERho]

if options.wideWindow:   # diagnostic: the early V (di-track) window (vMassMin/Max) still bounds the
    # combinatorics in C++; here we drop the Z-mass + prompt cuts -> measure the realistic
    # V+dilepton candidate RATE and the m(hh) spectrum within the rho/phi window.
    for b in _builders:
        b.preVtxSelection  = cms.string('charge() == 0')
        b.postVtxSelection = cms.string('userFloat("sv_prob") > 0')

# ---- single-LEPTON trigger requirement (production); empty => no HLT filter (mechanics test) ----
do_trig = len(options.trigger.split()) > 0
if do_trig:
    import HLTrigger.HLTfilters.hltHighLevel_cfi as hlt
    process.singleLepHLT = hlt.hltHighLevel.clone(
        HLTPaths = cms.vstring(*options.trigger.split()),
        andOr = cms.bool(True),          # OR of the listed paths
        throw = cms.bool(False),
    )

# ---- skim: >=1 candidate in ANY active (channel x V) collection, via OR'd filter paths ----
import PhysicsTools.BPHNano.ZToLLV_cff as zllv
_counts = []
if 'mumu' in _channels: _counts += [('ZToMuMuPhi', zllv.CountZToMuMuPhi), ('ZToMuMuRho', zllv.CountZToMuMuRho)]
if 'ee'   in _channels: _counts += [('ZToEEPhi',   zllv.CountZToEEPhi),   ('ZToEERho',   zllv.CountZToEERho)]
_pre = (process.singleLepHLT + process.nanoSequence) if do_trig else process.nanoSequence

if options.skim:
    _paths = []
    for name, filt in _counts:
        pname = 'skim_' + name
        setattr(process, 'Count' + name, filt)
        setattr(process, pname, cms.Path(_pre + getattr(process, 'Count' + name)))
        _paths.append(pname)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(SelectEvents=cms.vstring(*_paths))
    process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
    process.schedule = cms.Schedule(*([getattr(process, p) for p in _paths] + [process.NANOAODoutput_step]))
else:
    process.nanoAOD_step = cms.Path(_pre)
    process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
