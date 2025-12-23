####################################### UE Nano #####################################
#### Creates custom nanoAOD for Underlying Event studies (FSQ-15-007-like)
#### Non-BPH configuration for underlying event measurement at 13.6 TeV
## Author: Based on BPHnano structure

from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms


def Defaultsamples(isMC):
    if isMC:
        # Using QCD/MB samples for UE studies
        return ['root://cms-xrd-global.cern.ch//store/mc/Run3Summer22MiniAODv4/QCD_PT-15to7000_TuneCP5_Flat_13p6TeV_pythia8/MINIAODSIM/124X_mcRun3_2022_realistic_v12-v2/30000/0009b550-7ebe-46b1-9bce-da8fb8c2cc32.root']
    else:
        # Using MinimumBias or ZeroBias data
        return ['root://cms-xrd-global.cern.ch//store/data/Run2022D/JetMET0/MINIAOD/10Dec2022-v2/50000/006a1c1a-e849-4c59-9de2-caf94c24ff81.root']


options = VarParsing('python')

options.register('globalTag', '130X_dataRun3_Prompt_v3', 
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Global tag"
)

options.register('isMC', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Adds gen info/matching"
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
options.setDefault('tag', 'UE')

print(options)
options.parseArguments()
print("////////////////// UE nano running with options: ////////////////////////")
print(options)
print("/////////////////////////////////////////////////////////////////////////")

# Use provided globalTag if specified, otherwise use defaults
if options.globalTag == '130X_dataRun3_Prompt_v3':  # Default value
    globaltag = '124X_mcRun3_2022_realistic_v11' if options.isMC else '130X_dataRun3_Prompt_v3'
else:
    globaltag = options.globalTag

if options.isMC:
   options.tag+="_mc"
else:
   options.tag+="_data"

outputFileNANO = cms.untracked.string('_'.join(['ue_nano',options.tag])+'.root')
outputFileFEVT = cms.untracked.string('_'.join(['ue_edm',options.tag])+'.root')

if not options.inputFiles:
   options.inputFiles = Defaultsamples(options.isMC)

annotation = '%s nevts:%d' % (outputFileNANO, options.maxEvents)

# Process
from Configuration.StandardSequences.Eras import eras

process = cms.Process('UENANO',eras.Run3)

# import of standard configurations
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('PhysicsTools.BPHNano.nanoUE_cff')
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
    skipEvents=cms.untracked.uint32(options.skip),
)

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
)

process.nanoMetadata.strings.tag = annotation
# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string(annotation),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.0 $')
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

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, globaltag, '')

from PhysicsTools.BPHNano.nanoUE_cff import *

# Add UE specific customization (non-BPH nano for underlying event studies)
# For MC, this also adds gen particles automatically
process = nanoAOD_customizeUE(process, options.isMC)

print("Processing modules:", process.nanoSequenceUE)

process.nanoAOD_UE_step = cms.Path(process.nanoSequenceUE)

process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.NANOAODoutput_step = cms.EndPath(process.NANOAODoutput)

process.schedule = cms.Schedule(
    process.nanoAOD_UE_step,
    process.endjob_step,
    process.NANOAODoutput_step
    )

if options.wantFullRECO:
   process.schedule.insert(0,process.FEVTDEBUGHLToutput_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

process.NANOAODoutput.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring(
        'nanoAOD_UE_step',
    )
)

### from https://hypernews.cern.ch/HyperNews/CMS/get/physics-validation/3287/1/1/1/1/1.html
process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))
process.NANOAODoutput.fakeNameForCrab=cms.untracked.bool(True)

process.load("TrackingTools/TransientTrack/TransientTrackBuilder_cfi")
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)

print(process.dumpPython())
