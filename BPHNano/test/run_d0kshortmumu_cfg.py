####################### BPHNano: D0 -> K_S(pi pi) mu mu  slim NanoAOD ######################
# Target: D0 -> eta'(958) -> mu+mu-, with K_S -> pi+pi-.  eta' -> mumu has never been
# observed, so the D0 mass peak is the tag that would establish it.
#
# The dimuon window is deliberately WIDE (0.40-1.15 GeV), so one campaign delivers the
# search and both of its normalisations:
#   eta   (547.9)  B(->mumu)=5.8e-6    physics normalisation: same P -> mumu two-photon
#                                      mechanism as the eta', so the ratio cancels much
#                                      of the theory and muon-efficiency systematics
#   omega (782.7)  B(->mumu)=7.4e-5    cross-check
#   eta'  (957.8)  UNOBSERVED          <-- the search
#   phi  (1019.5)  B(->mumu)=2.85e-4   experimental calibration: ~45x more abundant than
#                                      the eta and only 62 MeV from the eta'
#
# m(mumu) is left UNCONSTRAINED in the fit because it IS the search variable; the builder
# stores fitted_mll beside the D0 mass, giving a 2-D (m_D0, m_mumu) analysis.
#
# The K_S is displaced (c*tau = 2.68 cm).  V0ReBuilder fits the two pions at their OWN
# vertex and passes BToV0LLBuilder the fitted COMPOSITE transient track, so no pion is
# ever forced into the D0 vertex.  That fit applies no K_S mass constraint, so recover
# the resolution offline by mass subtraction:
#     m_corr(D0) = m(mumu pipi) - m(pipi) + m_KS(PDG)
# using the stored mkshort_fullfit.  No decay-tree fitter is needed: the dimuon sits far
# from the kinematic limit m(D0) - m(K_S) = 1367 MeV, so there is no edge to sharpen.
#
# cmsRun test/run_d0kshortmumu_cfg.py inputFiles="file:miniaod.root" isMC=0 \
#     globalTag=150X_dataRun3_Prompt_v1 outputFiles=d0_nano.root
#   skim=1       -> keep only events with >=1 D0 candidate (default)
#   wideWindow=1 -> diagnostic: open both windows to measure the true candidate rate
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'd0_kshort_mumu_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
options.register('skim', 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "1: keep events with >=1 D0 candidate; 0: keep all")
options.register('wideWindow', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "diagnostic: open the dimuon and D0 windows")
options.register('mllMin', 0.40, VarParsing.multiplicity.singleton, VarParsing.varType.float, "dimuon mass window low edge [GeV]")
options.register('mllMax', 1.15, VarParsing.multiplicity.singleton, VarParsing.varType.float, "dimuon mass window high edge [GeV]")
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
        'keep nanoaodFlatTable_*Table_*_*',      # Muon, D0MuMu, Kshort, D0ToKshortMuMu, PV
        'keep nanoaodUniqueString_nanoMetadata_*_*',
        'keep edmTriggerResults_*_*_*',          # HLT bits (DoubleMu4_3_LowMass etc.)
    ),
)

from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeD0ToKshortMuMu
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeD0ToKshortMuMu(process, options.isMC)

# dimuon window is configurable so the search region can be moved without editing the cff
process.D0MuMu.preVtxSelection = cms.string(
    'charge() == 0 && %.4f < mass && mass < %.4f' % (options.mllMin, options.mllMax))

if options.wideWindow:      # diagnostic: measure the true candidate rate, full spectrum
    process.D0MuMu.preVtxSelection = cms.string('charge() == 0 && 0.2 < mass && mass < 3.2')
    process.D0ToKshortMuMu.preVtxSelection = cms.string('pt > 2.0 && 1.5 < mass && mass < 2.4')
    process.D0ToKshortMuMu.postVtxSelection = cms.string('userFloat("sv_prob") > 0.0')

process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    # process.load() of nanoBPH_cff already attached CountD0ToKshortMuMu to the process
    # under that label.  Re-assigning the SAME object under a second name raises
    # "Attempting to change the label of an attribute of the Process" -- clone instead.
    import PhysicsTools.BPHNano.D0ToKshortMuMu_cff as d0
    if not hasattr(process, 'CountD0ToKshortMuMuSkim'):
        process.CountD0ToKshortMuMuSkim = d0.CountD0ToKshortMuMu.clone()
    process.skim_D0ToKshortMuMu = cms.Path(process.nanoSequence + process.CountD0ToKshortMuMuSkim)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
        SelectEvents=cms.vstring('skim_D0ToKshortMuMu'))
    process.schedule = cms.Schedule(process.skim_D0ToKshortMuMu, process.NANOAODoutput_step)
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
