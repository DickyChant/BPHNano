####################### BPHNano: D+/Ds+ -> pi+ mu mu  slim NanoAOD ######################
# Reproduction of the CMS internal note "Search for eta' -> mu+mu- and Measurement of
# eta -> mu+mu- in D+ and Ds+ Decays": D+ -> eta(') pi+ and Ds+ -> eta(') pi+ with the
# dimuon from the eta('), normalised to D+(s) -> phi(mumu) pi+.
#
# ONE mass window covers both parents:  D+ 1869.66 MeV,  Ds+ 1968.35 MeV.
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
# stores fitted_mll beside the D mass, giving a 2-D (m_D, m_mumu) analysis.
#
# The muon working point is deliberately LOOSE here.  The note applies TIGHT muon ID,
# whose |dxy| < 0.2 cm and |dz| < 0.5 cm are prompt-muon cuts imposed on a displaced
# charm decay; keeping the ID loose in production lets tight/medium/soft be compared
# offline on identical candidates.
#
# NOTE (2026-09-06): the first campaign, DPIMM_2026Sep05, is INVALID.  Upstream
# BToTrkLLBuilder read its `trackMass` parameter and then never used it, hard-coding
# K_MASS in the pre-fit four-vector and in both kinematic fits, so every candidate was
# reconstructed as m(K mu mu).  The shift is Delta_m = gamma_D * Delta_E_trk, and with
# pt(D) > 10 GeV the boost gamma_D ~ 6-10 turns a ~100 MeV energy difference into ~0.9
# GeV of mass: measured median +0.918 GeV (RMS 0.61) on candidates passing the correct
# window.  A genuine D therefore landed near 2.8 GeV, entirely OUTSIDE the 1.78-2.06
# postVtxSelection, so real signal was cut away at production and the surviving sample
# is pure background -- nothing recoverable offline.  Fixed in BToTrkLLBuilder.cc;
# BToKLL_cff.py also had trackMass in MeV, harmless while unused and wrong once live.
#
# cmsRun test/run_dpimumu_cfg.py inputFiles="file:miniaod.root" isMC=0 \
#     globalTag=150X_dataRun3_Prompt_v1 outputFiles=d_pi_mumu_nano.root
#   skim=1       -> keep only events with >=1 D+/Ds+ candidate (default)
#   wideWindow=1 -> diagnostic: open both windows to measure the true candidate rate
from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

options = VarParsing('python')
options.register('isMC', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "MC: gen + PU + matching")
options.register('globalTag', 'auto', VarParsing.multiplicity.singleton, VarParsing.varType.string, "GlobalTag")
options.register('wantSummary', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Processing summary")
options.register('reportEvery', 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Report every N")
options.register('outputFiles', 'd_pi_mumu_nano.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "output NanoAOD")
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

from PhysicsTools.BPHNano.nanoBPH_cff import nanoAOD_customizeMC, nanoAOD_customizeDToPiMuMu
if options.isMC:
    process = nanoAOD_customizeMC(process)
process = nanoAOD_customizeDToPiMuMu(process, options.isMC)

# dimuon window is configurable so the search region can be moved without editing the cff
process.DPiMuMu.preVtxSelection = cms.string(
    'charge() == 0 && %.4f < mass && mass < %.4f' % (options.mllMin, options.mllMax))

if options.wideWindow:      # diagnostic: measure the true candidate rate, full spectrum
    process.DPiMuMu.preVtxSelection = cms.string('charge() == 0 && 0.2 < mass && mass < 3.2')
    process.DToPiMuMu.preVtxSelection = cms.string('pt > 2.0 && 1.5 < mass && mass < 2.4')
    process.DToPiMuMu.postVtxSelection = cms.string('userFloat("sv_prob") > 0.0')

process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)
if options.skim:
    # process.load() of nanoBPH_cff already attached CountD0ToKshortMuMu to the process
    # under that label.  Re-assigning the SAME object under a second name raises
    # "Attempting to change the label of an attribute of the Process" -- clone instead.
    import PhysicsTools.BPHNano.DToPiMuMu_cff as dpi
    if not hasattr(process, 'CountDToPiMuMuSkim'):
        process.CountDToPiMuMuSkim = dpi.CountDToPiMuMu.clone()
    process.skim_DToPiMuMu = cms.Path(process.nanoSequence + process.CountDToPiMuMuSkim)
    process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
        SelectEvents=cms.vstring('skim_DToPiMuMu'))
    process.schedule = cms.Schedule(process.skim_DToPiMuMu, process.NANOAODoutput_step)
else:
    process.nanoAOD_step = cms.Path(process.nanoSequence)
    process.schedule = cms.Schedule(process.nanoAOD_step, process.NANOAODoutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)
process.add_(cms.Service('InitRootHandlers', EnableIMT=cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)
