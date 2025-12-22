####################################### BPHnano - Pentaquark Data Test #####################################
#### Creates custom nanoAOD for pentaquark search (J/psi + p and J/psi + p + K) on data
#### Based on run_bphNano_cfg.py
## Author: Based on G Karathanasis (gkaratha), CERN

from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

# Default data sample for pentaquark analysis
# Run2022D ParkingDoubleMuonLowMass0 dataset
defaultDataSample = ['root://cms-xrd-global.cern.ch//store/data/Run2022D/ParkingDoubleMuonLowMass0/MINIAOD/10Dec2022-v2/25610000/79a953fb-ecee-457c-a06a-41352cf1ec10.root']

options = VarParsing('python')

options.register('globalTag', '130X_dataRun3_Prompt_v3', 
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Global tag for data"
)

options.register('wantSummary', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Processing summary"
)

options.register('wantFullRECO', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Produces additional EDM file"
)

options.register('reportEvery', 100,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Report every N events"
)

options.register('skip', 0,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Skip first N events"
)

options.setDefault('maxEvents', 1000)
options.setDefault('tag', 'pentaquark_data')

print(options)
options.parseArguments()
print("////////////////// BPHnano Pentaquark Data Test ////////////////////////")
print("Running on DATA (isMC=False)")
print("Analysis: Pentaquark (J/psi + p and J/psi + p + K)")
print(options)
print("/////////////////////////////////////////////////////////////////////////")

globaltag = options.globalTag
isMC = False  # Always False for data

outputFileNANO = cms.untracked.string('bph_nano_pentaquark_data.root')
outputFileFEVT = cms.untracked.string('bph_edm_pentaquark_data.root')

if not options.inputFiles:
    options.inputFiles = defaultDataSample

annotation = '%s nevts:%d' % (outputFileNANO, options.maxEvents)

# Process
from Configuration.StandardSequences.Eras import eras

process = cms.Process('BPHNANO', eras.Run3)

# import of standard configurations
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('PhysicsTools.BPHNano.nanoBPH_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(options.skip),
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
)

process.nanoMetadata.strings.tag = annotation
# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string(annotation),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileFEVT,
    outputCommands = (cms.untracked.vstring('keep *',
                                            'drop *_*_SelectedTransient*_*',
                     )),
    splitLevel = cms.untracked.int32(0)
)

process.NANOAODoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAOD'),
        filterName = cms.untracked.string('')
    ),
    fileName = outputFileNANO,
    outputCommands = cms.untracked.vstring(
      'drop *',
      "keep nanoaodFlatTable_*Table_*_*",     # event data
      "keep nanoaodUniqueString_nanoMetadata_*_*",   # basic metadata
      "keep edmTriggerResults_*_*_*",
    )
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

# BPH customizations for data
from PhysicsTools.BPHNano.nanoBPH_cff import *
# Note: No MC customization (nanoAOD_customizeMC) for data

# Add required sequences for pentaquark analysis
process = nanoAOD_customizeMuonBPH(process, isMC)
process = nanoAOD_customizeDiMuonBPH(process, isMC)
process = nanoAOD_customizeTrackBPH(process, isMC)

# Add pentaquark analysis (both J/psi + p and J/psi + p + K)
process = nanoAOD_customizePentaquark(process, isMC)

print("Processing modules:", process.nanoSequence)

process.nanoAOD_BPH_step = cms.Path(process.nanoSequence)

process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

process.schedule = cms.Schedule(
    process.nanoAOD_BPH_step,
    process.endjob_step,
    process.NANOAODoutput_step
)

if options.wantFullRECO:
    process.schedule.insert(0, process.FEVTDEBUGHLToutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring(
        'nanoAOD_BPH_step',
    )
)

### from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3287/1/1/1/1/1.html
process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab = cms.untracked.bool(True)

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)

print("=" * 80)
print("Configuration complete. Ready to run on DATA.")
print("Output file:", outputFileNANO)
print("=" * 80)

