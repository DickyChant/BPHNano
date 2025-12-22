from __future__ import print_function
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.globals_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *

## UE-specific modules (no BPH dependencies)
from PhysicsTools.BPHNano.UE_cff import *

vertexTable.svSrc = cms.InputTag("slimmedSecondaryVertices")

# Base nano sequence with standard vertex and global tables
nanoSequenceUE = cms.Sequence(nanoMetadata + 
                              cms.Sequence(vertexTask) +
                              cms.Sequence(globalTablesTask)+ 
                              cms.Sequence(vertexTablesTask)
                           )

def nanoAOD_customizeUE_MC(process):
    """Add gen particles and MC matching for UE studies"""
    process.nanoSequenceUE = cms.Sequence(process.nanoSequenceUE + 
                                          genParticleUESequence + 
                                          genParticleUETables)
    return process

def nanoAOD_customizeUE(process, isMC):
    """
    Customization for Underlying Event studies (FSQ-15-007)
    Non-BPH configuration for underlying event measurement at 13 TeV
    Completely standalone without BPH dependencies
    """
    if isMC:
        process.nanoSequenceUE = cms.Sequence( process.nanoSequenceUE + tracksUESequenceMC + tracksUETablesMC )
    else:
        process.nanoSequenceUE = cms.Sequence( process.nanoSequenceUE + tracksUESequence + tracksUETables )
    return process
