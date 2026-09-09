####################### BPHNano: eta'(958) -> mu+mu- e+e- slim NanoAOD ######################
# Builds BOTH e-leg variants on the same events so they can be compared directly:
#   EtaPrimeTo2Mu2ELowPt : e-legs from LowPtElectron (gsf tracks)
#
# cmsRun test/run_etaprime_cfg.py inputFiles="file:miniaod.root" isMC=0 \
#     globalTag=150X_dataRun3_Prompt_v1 outputFiles=etaprime_nano.root
#   skim=1        -> keep only events with >=1 candidate in EITHER variant (default)
#   variant=both|lowpt|trk|ele|all -> which e-leg variant(s) to run (default both)
#     'ele' merges LowPtElectron + standard Electron into ONE fit, so the MIXED pairing
#     (one hard + one soft e) exists; trk{1,2}_src then give the three fit categories.
#   wideWindow=1  -> open the eta' mass window (0.3-3.0) to study the full spectrum
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'etaprime_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
options.register('skim', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "1: keep events with >=1 eta' candidate (either variant); 0: keep all")
options.register('variant', 'ele', VarParsing.multiplicity.singleton, VarParsing.varType.string, "e-leg variant: 'ele' (default, ONE pass over the OR of both electron collections), 'lowpt', or 'all'")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: open the mass window (0.3-3.0) + drop post-fit mass cut")
options.register('nThreads', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "cmsRun threads/streams (set = CRAB JobType.numCores)")
options.setDefault('maxEvents', -1)
options.parseArguments()

gt = options.globalTag
if gt == 'auto':
    gt = '150X_mcRun3_2024_realistic_v2' if options.isMC else '150X_dataRun3_Prompt_v1'

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
    numberOfStreams=cms.untracked.uint32(0),
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
        'keep nanoaodFlatTable_*Table_*_*',      # Muon, LowPtElectron, EtaMuMu, EtaPrimeTo2Mu2E*, PV, (PU/gen on MC)
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',          # HLT bits
    ),
)

from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeEtaPrime2Mu2E
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeEtaPrime2Mu2E(process, options.isMC, variant=options.variant)

_active = [process.EtaPrimeTo2Mu2ELowPt] if options.variant in ('lowpt','all') else []
if options.variant in ('ele','all'):        _active.append(process.EtaPrimeTo2Mu2EEle)
if options.variant in ('ele','all','gamma'): _active.append(process.EtaPrimeToMuMuGamma)

if options.wideWindow:   # diagnostic: measure the real candidate rate + full m(2mu2e) spectrum
    for b in _active:
        b.preVtxSelection  = cms.string('pt > 5. && charge() == 0 && (mass > 0.3 && mass < 3.0)')
        b.postVtxSelection = cms.string('userFloat("sv_prob") > 0.0')

# ---- skim: >=1 candidate in ANY active variant, via OR'd filter paths ----
import PhysicsTools.BPHNano.EtaPrimeTo2Mu2E_cff as ep
_counts = []
if options.variant in ('lowpt', 'all'): _counts.append(('EtaPrimeTo2Mu2ELowPt', ep.CountEtaPrimeTo2Mu2ELowPt))
if options.variant in ('ele', 'all'):           _counts.append(('EtaPrimeTo2Mu2EEle',   ep.CountEtaPrimeTo2Mu2EEle))
# NOTE: the mu mu gamma normalisation channel is deliberately NOT added to the skim OR --
# it is far more abundant than the 2mu2e signal and would blow the output size up.
# It rides along in events the 2mu2e skim already keeps.

process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    _paths = []
    for name, filt in _counts:
        pname = 'skim_' + name
        setattr(process, 'Count' + name, filt)
        setattr(process, pname, cms.Path(process.nanoSequence + getattr(process, 'Count' + name)))
        _paths.append(pname)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(SelectEvents=cms.vstring(*_paths))
    process.schedule = cms.Schedule(*([getattr(process, p) for p in _paths] + [process.NANOAODoutput_step]))
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
