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
from PhysicsTools.BPHNano.BcToDsMuMu_cff import *
from PhysicsTools.BPHNano.tracks_cff import *
from PhysicsTools.BPHNano.KstarToKPi_cff import *
from PhysicsTools.BPHNano.KshortToPiPi_cff import *
from PhysicsTools.BPHNano.BToKLL_cff import *
from PhysicsTools.BPHNano.BToKstarLL_cff import *
from PhysicsTools.BPHNano.BToKshortLL_cff import *
from PhysicsTools.BPHNano.D0ToKshortMuMu_cff import *
from PhysicsTools.BPHNano.DToPiMuMu_cff import *
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
from PhysicsTools.BPHNano.EtaPrimeTo2Mu2E_cff import *
from PhysicsTools.BPHNano.EtaCTo4Mu_cff import *
from PhysicsTools.BPHNano.MuMuPhi_cff import *
from PhysicsTools.BPHNano.lowPtEleTracks_cff import *
from PhysicsTools.BPHNano.EtaPrimeToMuMuGamma_cff import *   # mu mu + converted photon   # LowPtElectron e-legs for 2mu2e
from PhysicsTools.BPHNano.ZToLLV_cff import *            # Z -> ll V (V=phi->KK / rho->pipi)
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
    # genWeightsTable produces the per-event `genWeight` (incl. NLO sign) -- was missing,
    # so DY(amcatnlo)/signal MC could not be normalised. lheInfoTable already ran (LHE_* branches).
    process.nanoSequence = cms.Sequence(process.nanoSequence + genWeightsTable + particleLevelBPHSequence + particleLevelBPHTables + genParticleBPHSequence + genParticleBPHTables + cms.Sequence(ppuTable) )
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


def nanoAOD_customizeMuMuPhi(process, isMC):
    """mu+mu- phi(->K+K-), m(mumuKK) 2.8-5.6 GeV.

    Spans eta_c -> mumu.phi (rare target) AND B_s -> J/psi phi (abundant control), so the
    B_s peak calibrates the mu-mu-K-K efficiency. Needs muonBPH + tracksBPH (the K legs);
    the narrow phi di-track window is applied inside the builder BEFORE the 4-track fit,
    which is what keeps the combinatorics affordable.
    """
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC + tracksBPHSequence
            + MuMuPhiSequence + MuMuPhiTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables + tracksBPHSequence
            + MuMuPhiSequence + MuMuPhiTables)
    pVertexTable.slim = cms.bool(True)
    return process


def nanoAOD_customizeEtaC4Mu(process, isMC):
    """eta_c -> 4mu : charmonium-region (2.80-3.90 GeV) 4-muon scan.

    Deliberately spans eta_c(1S) 2.984 up through psi(2S) 3.686, so J/psi (3.097) sits in the
    same spectrum as a normalisation/validation peak. Only needs muonBPH -- the 4mu builder
    takes muons directly, no dilepton collection required.
    """
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + EtaCTo4MuMCSequence + EtaCTo4MuMCTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + EtaCTo4MuSequence + EtaCTo4MuTables)
    pVertexTable.slim = cms.bool(True)
    return process


def nanoAOD_customizeEtaPrime2Mu2E(process, isMC, variant='both'):
    """eta(548)/eta'(958) -> mu+mu- e+e-, with up to THREE e-leg variants on the same events.

    variant:
      'lowpt' : e-legs from LowPtElectron (~1-5 GeV)              -> EtaPrimeTo2Mu2ELowPt
      'ele'   : e-legs from LowPtElectron AND standard Electron in ONE fit, with
                trk{1,2}_src giving the three categories (both soft / mixed / both
                standard)                                     -> EtaPrimeTo2Mu2EEle
      'all'   : ele + lowpt

    The e-leg sources are reconstructed on the SAME events so they can be compared directly.
    LowPtElectron and Electron are complementary in pT (roughly 1-5 and >5 GeV); the 'ele'
    variant merges them before the fit (duplicates removed by gsfTrack) so that the MIXED
    pairing exists at all, which two separate builds could never produce.

    The generic-track e-leg variant has been removed, so tracksBPH (a TrackMerger over every
    packedPFCandidate + lostTrack) is no longer scheduled here at all -- it was the expensive
    part and the only consumer is gone.
    """
    _need_lowpt = variant in ('lowpt', 'all')
    _need_ele   = variant in ('ele', 'all')
    # the mu mu gamma normalisation channel: cheap (photons are pre-made in the
    # MiniAOD) so it rides along with 'ele' and 'all' by default
    _need_gamma = variant in ('ele', 'all', 'gamma')
    if not (_need_lowpt or _need_ele or _need_gamma):
        raise ValueError("nanoAOD_customizeEtaPrime2Mu2E: unknown variant %r" % variant)

    # tracksBPH (TrackMerger over every packedPFCandidate+lostTrack) is EXPENSIVE and is only
    # needed by the generic-track variant -> only schedule it when that variant is requested.
    seq = cms.Sequence(EtaPrimeMuMu)
    tab = cms.Sequence()
    if _need_lowpt:
        seq += EtaPrimeTo2Mu2ELowPt
        tab += EtaPrimeTo2Mu2ELowPtTable
    if _need_ele:
        seq += EtaPrimeTo2Mu2EEle
        tab += EtaPrimeTo2Mu2EEleTable
    if _need_gamma:
        seq += EtaPrimeToMuMuGamma
        tab += EtaPrimeToMuMuGammaTable

    process.nanoSequence = cms.Sequence(process.nanoSequence
        + (muonBPHSequenceMC + muonBPHTablesMC if isMC else muonBPHSequence + muonBPHTables)
        + ((lowPtEleTracksSequenceMC if isMC else lowPtEleTracksSequence)
           if _need_lowpt else cms.Sequence())
        + ((etapEleTracksSequenceMC if isMC else etapEleTracksSequence)
           if _need_ele else cms.Sequence())
        + seq + tab)

    if isMC:
        if _need_lowpt:
            process.nanoSequence += cms.Sequence(EtaPrimeTo2Mu2ELowPtBPHMCMatch
                                                 + EtaPrimeTo2Mu2ELowPtBPHMCTable)
        if _need_ele:
            process.nanoSequence += cms.Sequence(EtaPrimeTo2Mu2EEleBPHMCMatch
                                                 + EtaPrimeTo2Mu2EEleBPHMCTable)

    # finalLowPtElectrons / finalElectrons and their tables live in cms.Tasks -> associate them
    # so the framework runs them for a scheduled consumer (same reason as customizeUpsilon4L).
    if _need_lowpt:
        lowPtElectronTable.src = cms.InputTag("finalLowPtElectrons")
        process.nanoSequence.associate(lowPtElectronTask, lowPtElectronTablesTask)
    if _need_ele:
        # only the LowPtElectron table is scheduled: the standard legs come from
        # slimmedElectrons (MiniAOD) and carry their own stamped quality variables, so the
        # heavy central Electron table (and its jet dependency) is not needed.
        lowPtElectronTable.src = cms.InputTag("finalLowPtElectrons")
        process.nanoSequence.associate(lowPtElectronTask, lowPtElectronTablesTask)
    pVertexTable.slim = cms.bool(True)
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


def nanoAOD_customizeZLLV(process, isMC, channels=('mumu', 'ee')):
    """Z -> l l V , V -> h+ h-  (V = phi->KK / rho->pipi ; l = mu and/or e). [first-observation search]

    `channels` selects the lepton final states. tracksBPH (the V daughters, from
    packedPFCandidates) is always added; 'mumu' adds Muon (muonBPH) + the WIDE dimuon
    (MuMuWide) + ZToMuMu{Phi,Rho}; 'ee' adds ZElectrons (slimmedElectrons transient tracks)
    + DiEle + ZToEE{Phi,Rho}. The general-track TABLE (~52 KB/evt) is NOT added.
    Collect with a standard SINGLE-lepton HLT (run cfg: HLT_IsoMu24/Mu50 for mumu on /Muon,
    HLT_Ele30_WPTight_Gsf for ee on /EGamma); skim >=1 candidate via OR'd filter paths.
    """
    add = [tracksBPHSequenceMC if isMC else tracksBPHSequence]   # V daughters, always
    if 'mumu' in channels:
        add += [muonBPHSequenceMC if isMC else muonBPHSequence,
                muonBPHTablesMC  if isMC else muonBPHTables,
                ZToMuMuVSequence, ZToMuMuVTables]
    if 'ee' in channels:
        add += [ZToEEVSequence, ZToEEVTables]
    seq = process.nanoSequence
    for a in add:
        seq = cms.Sequence(seq + a)
    process.nanoSequence = seq
    pVertexTable.slim = cms.bool(True)
    return process




def nanoAOD_customizeD0ToKshortMuMu(process, isMC):
    """D0 -> K_S(pi pi) mu mu, for eta'(958) -> mu+mu-.

    eta' -> mumu is unobserved; the D0 mass peak is the tag that would establish it.
    The dimuon window is wide (0.40-1.15 GeV) so the same sample carries its own
    normalisations: eta(548) -> mumu is the physics normalisation (same pseudoscalar
    two-photon mechanism as the eta', so the ratio cancels theory and muon-efficiency
    systematics) and phi(1020) -> mumu the experimental calibration (~45x more
    abundant, only 62 MeV from the eta').  omega(783) is a further cross-check.

    The K_S is displaced (c*tau = 2.68 cm) and is handled by V0ReBuilder, which fits
    the two pions at their OWN vertex and hands BToV0LLBuilder the fitted composite
    transient track -- no pion is forced into the D0 vertex.  There is no K_S mass
    constraint in that fit, so recover the resolution offline by mass subtraction:
    m_corr(D0) = m(mumu pipi) - m(pipi) + m_KS(PDG), using the stored mkshort_fullfit.

    tracksBPH runs as a producer because V0ReBuilder's track_match needs it.
    """
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + tracksBPHSequence
            + KshortToPiPiSequenceMC + KshortToPiPiTablesMC
            + D0MuMuSequence + D0MuMuTables
            + D0ToKshortMuMuSequence + D0ToKshortMuMuTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + tracksBPHSequence
            + KshortToPiPiSequence + KshortToPiPiTables
            + D0MuMuSequence + D0MuMuTables
            + D0ToKshortMuMuSequence + D0ToKshortMuMuTables)
    # NB: the Count* EDFilters are deliberately NOT in the sequence.  Inside it they
    # stop the path for candidate-less events, so with skim=0 the output module still
    # wants every event but the tables were never produced -> ProductNotFound.  The
    # pset adds the filter as its own skim path when skim=1.
    pVertexTable.slim = cms.bool(True)
    return process


def nanoAOD_customizeDToPiMuMu(process, isMC):
    """D+/Ds+ -> pi+ mu+ mu-, reproducing the CMS eta'/eta -> mumu charm analysis.

    One mass window (1.78-2.06) holds both parents, D+ at 1869.66 and Ds+ at 1968.35.
    m(mumu) is left free -- it is the search variable and spans eta/omega/eta'/phi.

    Muon selection is deliberately LOOSE in the producer so that tight / medium / soft
    can be compared offline on one ntuple.  That comparison is the point: the note this
    reproduces applies Tight muon ID, whose |dxy| < 0.2 cm and |dz| < 0.5 cm are
    prompt-muon cuts imposed on a displaced charm decay, and in a ~41-pileup sample the
    dz requirement is partly a PV-association cut.  Since the dominant background is
    genuine D -> pi mu mu Dalitz physics with real muons, muon ID scales signal and
    background alike, so S/sqrt(B) goes as sqrt(eps) -- loosening tight to soft is
    predicted to gain ~25%, which this build lets us measure.

    tracksBPH is required as a producer: the bachelor pion comes from SelectedTracks.
    """
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + tracksBPHSequence
            + DPiMuMuSequence
            + DToPiMuMuSequence + DToPiMuMuTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + tracksBPHSequence
            + DPiMuMuSequence
            + DToPiMuMuSequence + DToPiMuMuTables)
    # Count* filters stay OUT of the sequence -- inside it they stop the path for
    # candidate-less events, so with skim=0 the output module still wants every event
    # while the tables were never produced (ProductNotFound).
    pVertexTable.slim = cms.bool(True)
    return process


def nanoAOD_customizeBcToDsMuMu(process, isMC):
    """Bc+ -> (mu mu) Ds+, Ds+ -> phi(K+K-) pi+.

    One build carries three modes because m(mumu) is unconstrained over 2.0-4.4 GeV:
    J/psi Ds+ (3.0969), psi(2S) Ds+ (3.6861) and the non-resonant mu mu Ds+ continuum
    up to the m(Bc)-m(Ds) = 4.307 kinematic limit.  The two resonant modes normalise
    the non-resonant search, and J/psi Ds+ -- which has a measured branching fraction --
    gives the Bc yield in our own data, turning the Bc+ -> J/psi Lambda~ p event-count
    limit into a branching-fraction ratio.

    Ds*+ is NOT targeted: Ds*+ -> Ds+ gamma with the photon lost would sit near 6131
    MeV, and the Bc window starts at 6.15 to exclude it.

    Five tracks (mu mu K K pi) go into one vertex.  The phi arrives as a DiTrack with
    both tracks at the kaon mass; the bachelor pion comes from tracksBPH with an
    explicit index check against the two kaons, without which the same track would be
    used twice and fabricate a Ds.
    """
    if isMC:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequenceMC + muonBPHTablesMC
            + tracksBPHSequence
            + BcToDsMuMuSequence + BcToDsMuMuTables)
    else:
        process.nanoSequence = cms.Sequence(process.nanoSequence
            + muonBPHSequence + muonBPHTables
            + tracksBPHSequence
            + BcToDsMuMuSequence + BcToDsMuMuTables)
    # Count* filter stays OUT of the sequence -- see the note in the D0 customiser.
    pVertexTable.slim = cms.bool(True)
    return process
