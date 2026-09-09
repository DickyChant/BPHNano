####################### BPHNano: eta_c -> 4mu (charmonium-region 4mu scan) ######################
# mu+mu- phi(->K+K-). Window 2.8-5.6 GeV spans eta_c -> mumu.phi (target) and
# B_s -> J/psi phi 5.367 (CONTROL) -- the B_s peak calibrates the mumuKK efficiency.
#
# cmsRun test/run_mumuphi_cfg.py inputFiles="file:miniaod.root" isMC=0 \
#     globalTag=150X_dataRun3_Prompt_v1 outputFiles=mumuphi_nano.root
#   skim=1        -> keep only events with >=1 candidate (default)
#   wideWindow=1  -> open to 2.0-5.0 and drop the post-fit mass cut (spectrum diagnostic)
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'mumuphi_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
options.register('skim', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "1: keep events with >=1 candidate; 0: keep all")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: open window to 2.0-5.0, drop post-fit mass cut")
options.register('nThreads', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "cmsRun threads/streams (= CRAB JobType.numCores)")
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
        'keep nanoaodFlatTable_*Table_*_*',      # Muon, MuMuPhi, PV, (PU/gen on MC)
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',          # HLT bits
    ),
)

from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeMuMuPhi
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeMuMuPhi(process, options.isMC)

if options.wideWindow:   # measure the real candidate rate + the full m(4mu) spectrum
    for _b in (process.BsToJpsiPhi, process.EtaCToMuMuPhi):
        _b.preVtxSelection  = cms.string('charge() == 0 && mass > 2.0 && mass < 6.0')
        _b.postVtxSelection = cms.string('userFloat("sv_prob") > 0.0')

import PhysicsTools.BPHNano.MuMuPhi_cff as mp
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    # keep the event if EITHER channel has a candidate (OR of two filter paths)
    # NB: use .clone() (or a matching attribute name) -- assigning an already-labelled module
    # to a DIFFERENT process attribute renames it and CMSSW rejects the config.
    process.CountBsToJpsiPhi   = mp.CountBsToJpsiPhi.clone()
    process.CountEtaCToMuMuPhi = mp.CountEtaCToMuMuPhi.clone()
    process.skim_bs   = cms.Path(process.nanoSequence + process.CountBsToJpsiPhi)
    process.skim_etac = cms.Path(process.nanoSequence + process.CountEtaCToMuMuPhi)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
        SelectEvents=cms.vstring('skim_bs', 'skim_etac'))
    process.schedule = cms.Schedule(process.skim_bs, process.skim_etac, process.NANOAODoutput_step)
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
