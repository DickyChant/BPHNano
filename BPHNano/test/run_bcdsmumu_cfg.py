####################### BPHNano: Bc+ -> (mu mu) Ds+  slim NanoAOD ######################
# Bc+ -> (mu mu) Ds+ with Ds+ -> phi(K+ K-) pi+.  One build, three modes, because the
# dimuon mass is unconstrained over 2.0-4.4 GeV:
#     Bc+ -> J/psi Ds+     m(mumu) = 3.0969   normalisation, measured BR
#     Bc+ -> psi(2S) Ds+   m(mumu) = 3.6861   normalisation
#     Bc+ -> mu mu Ds+     continuum          the rare search
#
# Ds*+ is NOT targeted for now: the photon from Ds*+ -> Ds+ gamma is unreconstructed and
# would put the candidate near 6131 MeV, below the 6.15 GeV window edge.
#
# RATE TEST: run with skim=0 to count candidates per event before committing to a
# campaign -- five-track combinatorics is the risk here.
#
# cmsRun test/run_bcdsmumu_cfg.py inputFiles="file:miniaod.root" isMC=0 \
#     globalTag=auto outputFiles=bc_nano.root skim=0 maxEvents=20000
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'bc_ds_mumu_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
options.register('skim', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "1: keep events with >=1 D0 candidate; 0: keep all")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: open the dimuon and Bc windows")
options.register('mllMin', 2.00, VarParsing.multiplicity.singleton, VarParsing.varType.float, "dimuon mass window low edge [GeV]")
options.register('mllMax', 4.40, VarParsing.multiplicity.singleton, VarParsing.varType.float, "dimuon mass window high edge [GeV]")
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
        'keep nanoaodFlatTable_*Table_*_*',      # Muon, BcMuMu, PhiToKK, BcToDsMuMu, PV
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',          # HLT bits (DoubleMu4_3_LowMass etc.)
    ),
)

from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeBcToDsMuMu
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeBcToDsMuMu(process, options.isMC)

# dimuon window is configurable so the search region can be moved without editing the cff
process.BcMuMu.preVtxSelection = cms.string(
    'charge() == 0 && %.4f < mass && mass < %.4f' % (options.mllMin, options.mllMax))

if options.wideWindow:      # diagnostic: measure the true candidate rate, full spectrum
    process.BcMuMu.preVtxSelection = cms.string('charge() == 0 && 1.0 < mass && mass < 4.4')
    process.BcToDsMuMu.postVtxSelection = cms.string(
        '6.0 < userFloat("fitted_mass") && userFloat("fitted_mass") < 6.6 '
        '&& userFloat("sv_prob") > 0.0')

process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    # process.load() of nanoBPH_cff already attached CountBcToDsMuMu to the process
    # under that label.  Re-assigning the SAME object under a second name raises
    # "Attempting to change the label of an attribute of the Process" -- clone instead.
    import PhysicsTools.BPHNano.BcToDsMuMu_cff as d0
    if not hasattr(process, 'CountBcToDsMuMuSkim'):
        process.CountBcToDsMuMuSkim = d0.CountBcToDsMuMu.clone()
    process.skim_BcToDsMuMu = cms.Path(process.nanoSequence + process.CountBcToDsMuMuSkim)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
        SelectEvents=cms.vstring('skim_BcToDsMuMu'))
    process.schedule = cms.Schedule(process.skim_BcToDsMuMu, process.NANOAODoutput_step)
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
