import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

##################### D+/Ds+ -> pi+ mu+ mu-  ###############################
#
# Reproduces the CMS internal analysis "Search for eta' -> mu+mu- and Measurement of
# eta -> mu+mu- in D+ and Ds+ Decays" (2026-06-26), which uses D+ -> eta(')pi+ and
# Ds+ -> eta(')pi+ with the dimuon from the eta('), normalised to D+(s) -> phi(mumu)pi+.
#
# ONE mass window covers both parents, the same trick as the K/pi bachelor hypotheses
# in the Xi_b build:
#     D+   1869.66 MeV
#     Ds+  1968.35 MeV
#
# m(mumu) is left UNCONSTRAINED -- it is the search variable, spanning eta(547.9),
# omega(782.7), eta'(957.8) and phi(1019.5) in one spectrum.
#
# Why build this when the note already exists: it lets us (a) cross-check their result
# independently, and (b) test the muon-ID question directly.  Their selection applies
# TIGHT muon ID, which carries |dxy| < 0.2 cm and |dz| < 0.5 cm w.r.t. the PV.  Those
# are prompt-muon requirements imposed on a displaced charm decay (c*tau = 312 um for
# D+, 150 um for Ds+), and in their ~41-pileup sample the dz cut is partly a
# PV-association cut rather than a muon-quality one.
#
# Because the dominant background is genuine D -> pi mu mu Dalitz physics -- real muons
# from a real displaced D -- muon ID does not separate signal from background: it scales
# BOTH by the same efficiency.  So S/sqrt(B) goes as sqrt(eps), and loosening tight ->
# soft (62.8% -> 97.9% measured in our K_S sample, a factor 1.56) predicts about
# sqrt(1.56) = 1.25, a ~25% gain, comparable to the ~23% they project from adding the
# helicity angle.  This build is what lets that be measured rather than argued.

DPiMuMu = cms.EDProducer(
    'DiMuonBuilder',
    src                = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    # deliberately LOOSE here: the muon working point is applied offline so that
    # tight/medium/soft can be compared on the same ntuple
    lep1Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    preVtxSelection  = cms.string('charge() == 0 && 0.40 < mass && mass < 1.15'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001'),
)

DToPiMuMu = cms.EDProducer(
    'BToTrkLLBuilder',
    dileptons             = cms.InputTag('DPiMuMu', 'SelectedDiLeptons'),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    kaons                 = cms.InputTag('tracksBPH', 'SelectedTracks'),
    kaonsTransientTracks  = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    trackMass             = cms.double(0.13957039),      # the bachelor is a PION
    beamSpot              = cms.InputTag('offlineBeamSpot'),
    PUtracks              = cms.InputTag('tracksBPH', 'SelectedTracks'),
    # Window spans D+ and Ds+ together, with sidebands for the background fit.
    # Matches the note's rectangular pre-selection (displaced SV, pt(D) > 10, D mass
    # window).  Applied at PRODUCTION rather than offline for a storage reason: this
    # channel keeps 3.56% of events against 0.045% for D0 -> K_S mumu, so a full
    # campaign at pt(D) > 4 would write ~2.6 TB.  Tightening to the note's own
    # preselection roughly halves that and makes the comparison cleaner.
    # The MUON working point is deliberately NOT tightened here -- that is the
    # variable under study and stays loose so tight/medium/soft can be compared
    # offline on identical candidates.
    preVtxSelection  = cms.string('pt > 10.0 '
                                  '&& 1.75 < mass && mass < 2.10 '
                                  '&& userFloat("min_dr") > 0.02'),
    postVtxSelection = cms.string('1.78 < userFloat("fitted_mass") && userFloat("fitted_mass") < 2.06 '
                                  '&& userFloat("sv_prob") > 0.01 '
                                  '&& userFloat("fitted_cos_theta_2D") > 0.99'),
    dileptonMassContraint = cms.double(-1)      # m(mumu) free -- it is the observable
)

########################### Tables ###########################

DToPiMuMuTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag('DToPiMuMu'),
    cut       = cms.string(''),
    name      = cms.string('DToPiMuMu'),
    doc       = cms.string("D+/Ds+ -> pi+ mu mu ; m(mumu) spans eta/omega/eta'/phi"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        l1_idx    = uint('l1_idx'),
        l2_idx    = uint('l2_idx'),
        trk_idx   = uint('trk_idx'),
        min_dr    = ufloat('min_dr'),
        max_dr    = ufloat('max_dr'),
        # fit and vertex
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        vtx_x     = ufloat('vtx_x'),
        vtx_y     = ufloat('vtx_y'),
        vtx_z     = ufloat('vtx_z'),
        # post-fit: fit_mass is the D, mll_fullfit is the SEARCH variable
        mll_fullfit = ufloat('fitted_mll'),
        fit_mass    = ufloat('fitted_mass'),
        fit_massErr = ufloat('fitted_massErr'),
        fit_pt      = ufloat('fitted_pt'),
        fit_eta     = ufloat('fitted_eta'),
        fit_phi     = ufloat('fitted_phi'),
        fit_l1_pt   = ufloat('fitted_l1_pt'),
        fit_l1_eta  = ufloat('fitted_l1_eta'),
        fit_l1_phi  = ufloat('fitted_l1_phi'),
        fit_l2_pt   = ufloat('fitted_l2_pt'),
        fit_l2_eta  = ufloat('fitted_l2_eta'),
        fit_l2_phi  = ufloat('fitted_l2_phi'),
        fit_trk_pt  = ufloat('fitted_trk_pt'),
        fit_trk_eta = ufloat('fitted_trk_eta'),
        fit_trk_phi = ufloat('fitted_trk_phi'),
        # isolation
        l1_iso04  = ufloat('l1_iso04'),
        l2_iso04  = ufloat('l2_iso04'),
        trk_iso04 = ufloat('trk_iso04'),
    )
)

CountDToPiMuMu = cms.EDFilter('PATCandViewCountFilter',
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag('DToPiMuMu')
)

########################### Sequences ############################
DPiMuMuSequence     = cms.Sequence( DPiMuMu )
DToPiMuMuSequence   = cms.Sequence( DToPiMuMu )
DToPiMuMuTables     = cms.Sequence( DToPiMuMuTable )
