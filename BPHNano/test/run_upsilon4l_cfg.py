####################### BPHNano: Upsilon -> 4mu + 2mu2e slim NanoAOD ######################
# cmsRun test/run_upsilon4l_cfg.py inputFiles="file:miniaod.root" outputFiles="upsilon4l_nano.root" isMC=0
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'upsilon4l_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD file")
options.register('mode', '4mu', VarParsing.multiplicity.singleton, VarParsing.varType.string, "channels: '4mu' (4mu only) or '4l' (4mu + 2mu2e; 2mu2e still uses general tracks - WIP)")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: wideWindow=1 opens the 4mu mass window (0.5-60) to check the builder emits candidates")
options.register('skim', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "keep only events with >=1 Upsilon candidate (4mu, or 4mu||2mu2e in 4l mode)")
options.register('nThreads', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "cmsRun threads/streams (set = CRAB JobType.numCores)")
options.setDefault('maxEvents', -1)
options.parseArguments()

# sensible default GlobalTags (override with globalTag=...)
gt = options.globalTag
if gt == 'auto':
    gt = '140X_mcRun3_2024_realistic_v26' if options.isMC else '140X_dataRun3_PromptAnalysis_v1'

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

# ---- slim output: only the flat tables we actually produce + HLT bits + metadata ----
process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(dataTier=cms.untracked.string('NANOAOD'), filterName=cms.untracked.string('')),
    fileName = cms.untracked.string(options.outputFiles),
    outputCommands = cms.untracked.vstring(
        'drop *',
        'keep nanoaodFlatTable_*Table_*_*',          # Muon, LowPtElectron, Track, MuMu, UpsilonTo4Mu, UpsilonTo2Mu2E, PV, (PU/gen on MC)
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',              # HLT bits
    ),
)

# ---- build the slim BPH sequence ----
from PhysicsTools.BPHNano.nanoBPH_cff import (nanoAOD_customizeMC, nanoAOD_customizeMuonBPH,
                                              nanoAOD_customizeUpsilon4Mu, nanoAOD_customizeUpsilon4L)
if options.isMC:
    process = nanoAOD_customizeMC(process)
if options.mode == '4mu':
    process = nanoAOD_customizeUpsilon4Mu(process, options.isMC)   # 4mu only: no Track table, no 2mu2e
else:
    process = nanoAOD_customizeUpsilon4L(process, options.isMC)    # WIP: 2mu2e legs still general tracks

if options.wideWindow:   # diagnostic only: open the mass window AND accept every successful
    process.UpsilonTo4Mu.preVtxSelection  = cms.string('charge() == 0 && pt > 2. && mass > 0.5 && mass < 60.')
    process.UpsilonTo4Mu.postVtxSelection = cms.string('')   # fit (no sv_prob/l_xy cut) to study the full candidate spectrum

# ---- optional skim: keep only events with >=1 Upsilon candidate (OR across channels) ----
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    process.countUps4Mu = cms.EDFilter("CandViewCountFilter",
        src=cms.InputTag("UpsilonTo4Mu", "Selected4Leptons"), minNumber=cms.uint32(1))
    process.nanoAOD_step = cms.Path(process.nanoSequence + process.countUps4Mu)
    steps = [process.nanoAOD_step]
    sel = ['nanoAOD_step']
    if options.mode != '4mu':   # 4l: also keep events with a 2mu2e candidate
        process.countUps2Mu2E = cms.EDFilter("CandViewCountFilter",
            src=cms.InputTag("UpsilonTo2Mu2E"), minNumber=cms.uint32(1))
        process.nanoAOD_step_2mu2e = cms.Path(process.nanoSequence + process.countUps2Mu2E)
        steps.append(process.nanoAOD_step_2mu2e)
        sel.append('nanoAOD_step_2mu2e')
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(SelectEvents=cms.vstring(*sel))
    process.schedule = cms.Schedule(*(steps + [process.NANOAODoutput_step]))
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
