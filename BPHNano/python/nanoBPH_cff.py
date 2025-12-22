from __future__ import print_function
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.globals_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *
from PhysicsTools.NanoAOD.triggerObjects_cff import *


##for gen and trigger muon
from PhysicsTools.BPHNano.pverticesBPH_cff import *
from PhysicsTools.BPHNano.genparticlesBPH_cff import *
from PhysicsTools.BPHNano.particlelevelBPH_cff import *

## BPH collections
from PhysicsTools.BPHNano.muons_cff import *
from PhysicsTools.BPHNano.MuMu_cff import *
from PhysicsTools.BPHNano.tracks_cff import *
from PhysicsTools.BPHNano.KstarToKPi_cff import *
from PhysicsTools.BPHNano.KshortToPiPi_cff import *
from PhysicsTools.BPHNano.BToKLL_cff import *
from PhysicsTools.BPHNano.BToKstarLL_cff import *
from PhysicsTools.BPHNano.BToKshortLL_cff import *
#from PhysicsTools.BPHNano.BDh_cff_v3 import *

from PhysicsTools.BPHNano.LambdaToPPi_cff import *
from PhysicsTools.BPHNano.LambdabToLambdaLL_cff import *
from PhysicsTools.BPHNano.DiHs_cff import *
from PhysicsTools.BPHNano.EtaMuMu_cff import *
from PhysicsTools.BPHNano.EtaTo4Mu_cff import *
from PhysicsTools.BPHNano.EtaTo2L2Pi_cff import *
from PhysicsTools.BPHNano.LambdabToLambdahhBuilder import *
from PhysicsTools.BPHNano.BDKstar_cff import *
#from PhysicsTools.BPHNano.LambdabToLambdahhBuilder_v2 import *

vertexTable.svSrc = cms.InputTag("slimmedSecondaryVertices")



nanoSequence = cms.Sequence(nanoMetadata + 
                            cms.Sequence(vertexTask) +
                            cms.Sequence(globalTablesTask)+ 
                            cms.Sequence(vertexTablesTask) +
                            cms.Sequence(pVertexTable) 
                          )

def nanoAOD_customizeMC(process):
    process.nanoSequence = cms.Sequence(process.nanoSequence +particleLevelBPHSequence + genParticleBPHSequence+ genParticleBPHTables )
    return process

def nanoAOD_customizeMuonBPH(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables)
       #process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + countTrgMuons + muonBPHTables)
    return process



def nanoAOD_customizeDiMuonBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + MuMuMCSequence + MuMuMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + MuMuSequence + MuMuTables)
    return process

def nanoAOD_customizeEta2Mu2PiBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaMuMuMCSequence + EtaMuMuMCTables + EtaTo2L2PiMCSequence + EtaTo2L2PiMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaMuMuSequence + EtaMuMuTables + EtaTo2L2PiSequence + EtaTo2L2PiTables)
    return process

def nanoAOD_customizeEtaTo4MuBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaTo4MuMCSequence + EtaTo4MuMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaTo4MuSequence + EtaTo4MuTables)
    return process

def nanoAOD_customizeBDKstar(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BDKstarSequenceMC + BDKstarSequenceMCTable)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BDKstarSequence + BDKstarSequenceTable)
    return process

def nanoAOD_customizeTrackBPH(process,isMC):
    if isMC:
       process.nanoSequence =  cms.Sequence( process.nanoSequence + tracksBPHSequenceMC)# + tracksBPHTablesMC)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + tracksBPHSequence)# + tracksBPHTables)
    return process



def nanoAOD_customizeBToKLL(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BToKMuMuSequence + BToKMuMuTables  )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BToKMuMuSequence +CountBToKmumu + BToKMuMuTables)
    return process



def nanoAOD_customizeBToKstarLL(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + KstarPiKSequence + KstarPiKTables + BToKstarMuMuSequence + BToKstarMuMuTables  )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + KstarPiKSequence + CountKstarPiK+ KstarPiKTables+ BToKstarMuMuSequence + BToKstarMuMuTables  )
    return process




def nanoAOD_customizeBToKshortLL(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence+ KshortToPiPiSequenceMC + KshortToPiPiTablesMC + BToKshortMuMuSequence + BToKshortMuMuTables  )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence+ KshortToPiPiSequence + CountKshortToPiPi+ KshortToPiPiTables + BToKshortMuMuSequence + CountBToKshortMuMu +BToKshortMuMuTables  )
    return process


#def nanoAOD_customizeBDh_MC(process):
#    process.nanoSequence = cms.Sequence( process.nanoSequence + BDhSequenceMC + BDhSequenceMCTable )
#    return process
#
#def nanoAOD_customizeBDh_Data(process):
#    process.nanoSequence = cms.Sequence( process.nanoSequence+ BDhSequence + BDhSequenceTable )
#    return process
#
#def nanoAOD_customizeBDh(process, isMC):
#    if isMC:
#       process.nanoSequence = cms.Sequence( process.nanoSequence + BDhSequenceMC + BDhSequenceMCTable )
#       return process
#    else:
#       process.nanoSequence = cms.Sequence( process.nanoSequence+ BDhSequence + BDhSequenceTable )
#       return process


def nanoAOD_customizeLambda(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + LambdaPPiSequenceMC + LambdaPPiTablesMC + LambdabToLambdaMuMuMCSequence + LambdabToLambdaMuMuMCTables  )
       return process
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + LambdaPPiSequence + LambdaPPiTables + LambdabToLambdaMuMuSequence + LambdabToLambdaMuMuTables  )
       return process

def nanoAOD_customizeLambdahh(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + LambdaPPiSequenceMC + LambdaPPiTablesMC + LambdabToLambdahhSequenceMC + LambdabToLambdahhTablesMC  )
       return process
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + LambdaPPiSequence + LambdaPPiTables + LambdabToLambdahhSequence + LambdabToLambdahhTables  )
       return process

#def nanoAOD_customizeLambdahh_v2(process, isMC):
#    if isMC:
#       process.nanoSequence = cms.Sequence( process.nanoSequence + LambdabToLambdahhv2SequenceMC + LambdabToLambdahhv2SequenceMCTable )
#       return process
#    else:
#       process.nanoSequence = cms.Sequence( process.nanoSequence+ LambdabToLambdahhv2Sequence + LambdabToLambdahhv2SequenceTable )
#       return process


def nanoAOD_customizeBToXLL(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BToKMuMuSequence + BToKMuMuTables + KshortToPiPiSequenceMC + KshortToPiPiTablesMC + BToKshortMuMuSequence + BToKshortMuMuTables +  KstarPiKTables +KstarPiKTables+ BToKstarMuMuSequence + BToKstarMuMuTables  )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BToKMuMuSequence + BToKMuMuTables + KshortToPiPiSequence + KshortToPiPiTables + BToKshortMuMuSequence +BToKshortMuMuTables + KstarPiKSequence +  KstarPiKTables +KstarPiKTables+ BToKstarMuMuSequence + BToKstarMuMuTables )
    return process



