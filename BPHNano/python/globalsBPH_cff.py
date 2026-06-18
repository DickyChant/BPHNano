import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.nano_eras_cff import *
from PhysicsTools.NanoAOD.globalVariablesTableProducer_cfi import globalVariablesTableProducer

ppuTable = cms.EDProducer("NPUTablesProducer",
        src = cms.InputTag("slimmedAddPileupInfo"),
        pvsrc = cms.InputTag("offlineSlimmedPrimaryVertices"),
        zbins = cms.vdouble( [0.0,1.7,2.6,3.0,3.5,4.2,5.2,6.0,7.5,9.0,12.0] ),
        savePtHatMax = cms.bool(True),
)
# 15X: the run3_nanoAOD_122/124 era modifiers no longer exist; drop the era-gated
# savePtHatMax tweak (cosmetic, keeps the PU branches as-is).
#puTableTask = cms.Task(puTable)
