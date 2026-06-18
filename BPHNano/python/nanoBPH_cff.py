from __future__ import print_function
import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.globals_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *
from PhysicsTools.NanoAOD.triggerObjects_cff import *
from PhysicsTools.NanoAOD.electrons_cff import *   # lowPtElectronTable / lowPtElectronTask / finalLowPtElectrons


##for gen and trigger muon
from PhysicsTools.BPHNano.pverticesBPH_cff import *
from PhysicsTools.BPHNano.genparticlesBPH_cff import *
from PhysicsTools.BPHNano.particlelevelBPH_cff import *
from PhysicsTools.BPHNano.globalsBPH_cff import *

## BPH collections
from PhysicsTools.BPHNano.muons_cff import *
from PhysicsTools.BPHNano.photons_cff import *
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
from PhysicsTools.BPHNano.EtaTo2L2PiGamma_cff import *
from PhysicsTools.BPHNano.BToMuMuGammaConv_cff import *
from PhysicsTools.BPHNano.UpsilonTo4Mu_cff import *
from PhysicsTools.BPHNano.UpsilonTo2Mu2E_cff import *
from PhysicsTools.BPHNano.lowPtEleTracks_cff import *   # LowPtElectron e-legs for 2mu2e
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
    #process.nanoSequence = cms.Sequence(process.nanoSequence + particleLevelBPHSequence + particleLevelBPHTables + genParticleBPHSequence + genParticleBPHTables )
    process.nanoSequence = cms.Sequence(process.nanoSequence + particleLevelBPHSequence + particleLevelBPHTables + genParticleBPHSequence + genParticleBPHTables + cms.Sequence(ppuTable) )
    return process

def nanoAOD_customizeMuonBPH(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables)
       #process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + countTrgMuons + muonBPHTables)
    return process

def nanoAOD_customizePhotonBPH(process,isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + photonBPHSequenceMC + photonBPHTablesMC)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + photonBPHSequence + photonBPHTables)
    return process

def nanoAOD_customizeDiMuonBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + MuMuMCSequence + MuMuMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + MuMuSequence + MuMuTables)
    return process

def nanoAOD_customizeEta2Mu2PiAnd4MuBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC + EtaMuMuMCSequence + EtaMuMuMCTables + EtaTo2L2PiMCSequence + EtaTo2L2PiMCTables + EtaTo4MuMCSequence + EtaTo4MuMCTables + EtaGenMCSequence + EtaGenMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables + EtaMuMuSequence + EtaMuMuTables + EtaTo2L2PiSequence + EtaTo2L2PiTables + EtaTo4MuSequence + EtaTo4MuTables)
    return process


def nanoAOD_customize2L2Pi1Gamma(process,isMC):
    if isMC:
        process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC + EtaMuMuMCSequence + EtaMuMuMCTables +  photonBPHSequenceMC + photonBPHTablesMC + EtaTo2L2Pi1GammaMCSequence + EtaTo2L2Pi1GammaMCTables)
    else:
        #process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables + EtaMuMuSequence + EtaMuMuTables +  photonBPHSequence + photonBPHTables + EtaTo2L2Pi1GammaSequence + EtaTo2L2Pi1GammaTables)
        process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables + EtaMuMuSequence + EtaMuMuTables + BToMuMuGammaConvSequence + BToMuMuGammaConvTables)
    return process


def nanoAOD_customizeEta2Mu2PiBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC + EtaMuMuMCSequence + EtaMuMuMCTables + EtaTo2L2PiMCSequence + EtaTo2L2PiMCTables + EtaGenMCSequence + EtaGenMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables + EtaMuMuSequence + EtaMuMuTables + EtaTo2L2PiSequence + EtaTo2L2PiTables)
    return process

def nanoAOD_customizeEtaTo4MuBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaTo4MuMCSequence + EtaTo4MuMCTables + EtaGenMCSequence + EtaGenMCTables )
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + EtaTo4MuSequence + EtaTo4MuTables)
    return process
       
def nanoAOD_customizeEtaBPH(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequenceMC + muonBPHTablesMC + EtaMuMuMCSequence + EtaMuMuMCTables + EtaTo2L2PiMCSequence + EtaTo2L2PiMCTables + EtaTo4MuMCSequence + EtaTo4MuMCTables + EtaGenMCSequence + EtaGenMCTables)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + muonBPHSequence + muonBPHTables + EtaMuMuSequence + EtaMuMuTables + EtaTo2L2PiSequence + EtaTo2L2PiTables + EtaTo4MuSequence + EtaTo4MuTables)
    return process

def nanoAOD_customizeBDKstar(process, isMC):
    if isMC:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BDKstarSequenceMC + BDKstarSequenceMCTable)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + BDKstarSequence + BDKstarSequenceTable)
    return process

def nanoAOD_customizeTrackBPH(process,isMC):
    if isMC:
       process.nanoSequence =  cms.Sequence( process.nanoSequence + tracksBPHSequenceMC + tracksBPHTablesMC)
    else:
       process.nanoSequence = cms.Sequence( process.nanoSequence + tracksBPHSequence + tracksBPHTables)
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


def nanoAOD_customizeUpsilon4Mu(process, isMC):
    """Slim Upsilon -> 4mu ONLY NanoAOD (no 2mu2e, no general-track table).

    Produces: Muon (muonBPH), the wide dimuon (MuMu, for the dimuon cross-check), and the
    UpsilonTo4Mu candidate table. Deliberately drops tracksBPH (the full general-track
    table, ~52 KB/evt) and UpsilonTo2Mu2E (the dimuon x track x track combinatorics that
    blows up to ~600 cand/evt). HLT bits via the output module; PU/gen via customizeMC.
    """
    MuMu.preVtxSelection  = cms.string('abs(userCand("l1").vz - userCand("l2").vz) <= 1. '
                                       '&& charge() == 0 && mass() > 0.2 && mass() < 10.0')
    MuMu.postVtxSelection = cms.string('userFloat("sv_prob") > 0.001 '
                                       '&& userFloat("fitted_mass") > 0.2 && userFloat("fitted_mass") < 10.0')
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + MuMuMCSequence + MuMuMCTables
            + UpsilonTo4MuMCSequence + UpsilonTo4MuMCTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + MuMuSequence + MuMuTables
            + UpsilonTo4MuSequence + UpsilonTo4MuTables)
    # slim the all-PV BPHNano table to z-only (PVtx_vz + nPVtx, ~tens of B/evt instead of ~1 KB)
    # for candidate<->PV z-matching; central PV_* (leading PV) + beamspot l_xy cover event sel + prompt.
    pVertexTable.slim = cms.bool(True)
    return process


def nanoAOD_customizeUpsilon4L(process, isMC):
    """Slim Upsilon -> 4mu  AND  Upsilon -> 2mu2e NanoAOD.

    Produces ONLY: Muon (muonBPH), LowPtElectron (central table) + its gsf-track collection
    (lowPtEleTracks, the soft e+e- legs for 2mu2e), the wide dimuon (MuMu), and the two
    4-lepton candidate tables. The 2mu2e trk{1,2}_idx index straight into the LowPtElectron
    table. HLT bits are kept via the output module (edmTriggerResults); PU (ppuTable) + gen
    come from nanoAOD_customizeMC. No general-track table; everything else (jets, MET, taus,
    photons, isotracks, ...) is simply never produced.
    """
    # WIDE dimuon window: the mumu pair in Upsilon->2mu2e is NOT at the Upsilon mass.
    MuMu.preVtxSelection  = cms.string('abs(userCand("l1").vz - userCand("l2").vz) <= 1. '
                                       '&& charge() == 0 && mass() > 0.2 && mass() < 10.0')
    MuMu.postVtxSelection = cms.string('userFloat("sv_prob") > 0.001 '
                                       '&& userFloat("fitted_mass") > 0.2 && userFloat("fitted_mass") < 10.0')
    # central-NanoAOD low-pT electron table (soft-e ID; match to UpsilonTo2Mu2E trk{1,2}_idx offline)
    lowPtElectronTable.src = cms.InputTag("finalLowPtElectrons")
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + lowPtEleTracksSequenceMC
            + MuMuMCSequence + MuMuMCTables
            + UpsilonTo4MuMCSequence + UpsilonTo4MuMCTables
            + UpsilonTo2Mu2EMCSequence + UpsilonTo2Mu2EMCTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + lowPtEleTracksSequence
            + MuMuSequence + MuMuTables
            + UpsilonTo4MuSequence + UpsilonTo4MuTables
            + UpsilonTo2Mu2ESequence + UpsilonTo2Mu2ETables)
    # finalLowPtElectrons (consumed by the scheduled lowPtEleTracks) and the LowPtElectron
    # table live in cms.Tasks -> associate them so the framework runs them unscheduled /
    # on-demand within the path (a Task wrapped in a Sequence does NOT do this for a
    # scheduled consumer).
    process.nanoSequence.associate(lowPtElectronTask, lowPtElectronTablesTask)
    # slim the all-PV BPHNano table to z-only (PVtx_vz + nPVtx) for candidate<->PV z-matching;
    # central PV_* (leading PV) + beamspot l_xy still cover event selection + the prompt cut.
    pVertexTable.slim = cms.bool(True)
    return process


