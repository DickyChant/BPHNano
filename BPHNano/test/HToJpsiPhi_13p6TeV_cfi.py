import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

# H -> J/psi phi , J/psi -> mu+ mu- , phi -> K+ K-  (ggH, 13.6 TeV, CP5) -- acceptance study.
generator = cms.EDFilter("Pythia8GeneratorFilter",
    maxEventsToPrint = cms.untracked.int32(1),
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1.0),
    comEnergy = cms.double(13600.),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'HiggsSM:gg2H = on',
            '25:m0 = 125.0',
            # keep standard H channels open for the production xsec, add H->J/psi phi with a huge BR
            '25:addChannel = 1 1000000.0 100 443 333',   # H -> J/psi phi
            '443:onMode = off', '443:onIfMatch = 13 -13',   # J/psi -> mu+ mu-
            '333:onMode = off', '333:onIfMatch = 321 -321', # phi -> K+ K-
        ),
        parameterSets = cms.vstring('pythia8CommonSettings', 'pythia8CP5Settings', 'processParameters')
    )
)
ProductionFilterSequence = cms.Sequence(generator)
