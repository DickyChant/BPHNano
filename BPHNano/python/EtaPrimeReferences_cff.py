import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *
from PhysicsTools.BPHNano.EtaPrimeTo2Mu2E_cff import ETAP_MASS_MIN, ETAP_MASS_MAX
from PhysicsTools.BPHNano.EtaTo4Mu_cff import EtaTo4Mu, EtaTo4MuTable, EtaTo4MuBPHMCMatch, EtaTo4MuBPHMCTable
from PhysicsTools.BPHNano.EtaTo2L2Pi_cff import (EtaTo2L2Pi, EtaTo2L2PiTable,
                                                 EtaTo2L2PiBPHMCMatch, EtaTo2L2PiBPHMCTable)
from PhysicsTools.BPHNano.tracks_cff import tracksBPH

# ============================================================================
#  REFERENCE channels for the eta/eta' -> mu+mu- e+e- search, built on the same events:
#    4mu    : eta -> mu+mu- mu+mu-   the same double-Dalitz decay with muons (B = 5.0e-9, CMS)
#    2mu2pi : eta' -> pi+pi- mu+mu-  B = 2.0e-5 (BESIII); eta -> pi+pi- mu+mu- is not seen
#
#  The stock EtaTo4Mu / EtaTo2L2Pi builders stop at 0.90 GeV, below the eta'. Here both use
#  the 2mu2e window and preselection (pt > 5, |charge| <= 2 so the same-sign 4mu combinations
#  stay as a combinatorial control -- the 2mu2pi builder itself only pairs opposite-sign pions --
#  and sv_prob > 0, tightened offline; 2mu2pi alone cuts sv_prob > 0.1, see below). 2mu2pi also takes the
#  2mu2e DIMUON (EtaPrimeMuMu), so the signal and this reference share the muon pair.
#  Table names are the stock ones: EtaTo4Mu_*, EtaTo2L2Pi_*.
# ============================================================================

_pre_sel = ('pt > 5. && abs(charge()) <= 2 && (mass > %.2f && mass < %.2f)'
            % (ETAP_MASS_MIN, ETAP_MASS_MAX))
_post_sel = ('userFloat("sv_prob") > 0.0 '
             '&& userFloat("fitted_mass") > %.2f && userFloat("fitted_mass") < %.2f'
             % (ETAP_MASS_MIN, ETAP_MASS_MAX))

########################### 4mu ###########################
EtaPrimeTo4Mu = EtaTo4Mu.clone(
    beamSpot         = cms.InputTag('offlineBeamSpot'),   # the builder needs it; the stock cff lacks it
    preVtxSelection  = cms.string(_pre_sel),
    postVtxSelection = cms.string(_post_sel),
)
EtaPrimeTo4MuTable = full_precision_p4(EtaTo4MuTable.clone(
    src = cms.InputTag('EtaPrimeTo4Mu', 'Selected4Leptons'),
    doc = cms.string("eta/eta' -> 4mu reference channel (l{1..4}_idx index the Muon table). "
                     "charge==0 is the signal, |charge|==2 the same-sign control."),
))
EtaPrimeTo4MuBPHMCMatch = EtaTo4MuBPHMCMatch.clone(src = EtaPrimeTo4MuTable.src)
EtaPrimeTo4MuBPHMCTable = EtaTo4MuBPHMCTable.clone(
    recoObjects = EtaPrimeTo4MuTable.src,
    mcMap       = cms.InputTag('EtaPrimeTo4MuBPHMCMatch'),
)
CountEtaPrimeTo4Mu = cms.EDFilter('CandViewCountFilter',
    src = EtaPrimeTo4MuTable.src, minNumber = cms.uint32(1))

########################### 2mu2pi ###########################
# Pion tracks: packedPFCandidates + lostTracks through the TrackMerger, cut at the builder's
# pT > 1 GeV so fewer transient tracks are built. A track that IS a muon is excluded: the stock
# builder never checks, and a muon fitted twice gives a perfect-looking vertex.
etapPionTracks = tracksBPH.clone(trackSelection = cms.string('pt > 1.0 && abs(eta) < 2.5'))
_pion_sel = 'pt > 1.0 && abs(eta) < 2.5 && userInt("isMatchedToMuon") == 0'
EtaPrimeTo2Mu2Pi = EtaTo2L2Pi.clone(
    dileptons        = cms.InputTag('EtaPrimeMuMu', 'SelectedDiLeptons'),
    tracks           = cms.InputTag('etapPionTracks', 'SelectedTracks'),
    transientTracks  = cms.InputTag('etapPionTracks', 'SelectedTransientTracks'),
    trk1Selection    = cms.string(_pion_sel),
    trk2Selection    = cms.string(_pion_sel),
    preVtxSelection  = cms.string(_pre_sel),
    # sv_prob > 0.1 (the BPH-24-001 4-lepton cut) at the producer: every OS pion pair near a
    # dimuon fits, and at sv_prob > 0 this channel alone put 2.0% of 2025D events in the skim
    # (x4.7 on the 2mu2e + mu mu gamma skim); at 0.1 it is 1.2% (x3.2), for ~10% of a real decay.
    postVtxSelection = cms.string(_post_sel.replace('userFloat("sv_prob") > 0.0', 'userFloat("sv_prob") > 0.1')),
)
EtaPrimeTo2Mu2PiTable = full_precision_p4(EtaTo2L2PiTable.clone(
    src = cms.InputTag('EtaPrimeTo2Mu2Pi'),
    doc = cms.string("eta/eta' -> pi+pi- mu+mu- reference channel. The pion track table is not "
                     "stored: use fit_trk{1,2}_*. Always neutral: the builder only pairs "
                     "opposite-sign pions and the dimuon is opposite-sign."),
))
EtaPrimeTo2Mu2PiBPHMCMatch = EtaTo2L2PiBPHMCMatch.clone(src = EtaPrimeTo2Mu2PiTable.src)
EtaPrimeTo2Mu2PiBPHMCTable = EtaTo2L2PiBPHMCTable.clone(
    recoObjects = EtaPrimeTo2Mu2PiTable.src,
    mcMap       = cms.InputTag('EtaPrimeTo2Mu2PiBPHMCMatch'),
)
CountEtaPrimeTo2Mu2Pi = cms.EDFilter('CandViewCountFilter',
    src = EtaPrimeTo2Mu2PiTable.src, minNumber = cms.uint32(1))
