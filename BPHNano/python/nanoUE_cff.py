from __future__ import print_function
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.globals_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *

## UE-specific modules (no BPH dependencies)
from PhysicsTools.BPHNano.UE_cff import *
from PhysicsTools.BPHNano.pverticesBPH_cff import pVertexTable  # all PVs (PVtx_*) for merged-PV diagnostics

vertexTable.svSrc = cms.InputTag("slimmedSecondaryVertices")

# Base nano sequence with standard vertex and global tables
nanoSequenceUE = cms.Sequence(nanoMetadata + 
                              cms.Sequence(vertexTask) +
                              cms.Sequence(globalTablesTask) + 
                              cms.Sequence(vertexTablesTask) +
                              pVertexTable
                           )

def nanoAOD_customizeUE(process, isMC):
    """
    Customization for Underlying Event studies (FSQ-15-007-like)
    Non-BPH configuration for underlying event measurement at 13.6 TeV
    Completely standalone without BPH dependencies
    """
    if isMC:
        # Add gen particles and MC-matched tracks
        process.nanoSequenceUE = cms.Sequence( process.nanoSequenceUE + 
                                              genParticleUESequence + 
                                              genParticleUETables +
                                              packedGenChargedUETables +
                                              cms.Sequence(globalTablesMCTask) +   # Pileup_nPU/nTrueInt, genWeight
                                              tracksUESequenceMC +
                                              tracksUETablesMC +
                                              mbTrigUETables +
                                              genProcUETable )
    else:
        # Add only reco tracks (no gen particles)
        process.nanoSequenceUE = cms.Sequence( process.nanoSequenceUE +
                                              tracksUESequence +
                                              tracksUETables +
                                              mbTrigUETables )
    return process
