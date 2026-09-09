import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

##################### D0 -> K_S(pi pi) (mu mu) ############################
#
# Target: D0 -> eta'(-> mu mu) K_S(-> pi pi).  eta' -> mu+mu- has never been
# observed, so the D0 mass peak is the tag that would prove it: a real eta'->mumu
# shows up as a D0 peak in m(mumu pipi) with m(mumu) at 957.8 MeV.  That exclusive
# tag is what suppresses the combinatorics an inclusive eta'->mumu search drowns in.
#
# The dimuon window is deliberately WIDE (0.40-1.15 GeV) rather than sitting on the
# eta', because the same final state then delivers its own normalisation channels:
#
#   eta   547.9 MeV   B(->mumu) = 5.8e-6    B(D0->K_S eta ) ~ 5.1e-3
#   omega 782.7 MeV   B(->mumu) = 7.4e-5    B(D0->K_S omega) ~ 1.1e-2
#   eta'  957.8 MeV   UNOBSERVED            B(D0->K_S eta') ~ 4.7e-3   <-- the search
#   phi  1019.5 MeV   B(->mumu) = 2.85e-4   B(D0->K_S phi ) ~ 4.7e-3
#
# eta -> mumu is the PHYSICS normalisation: same pseudoscalar -> mumu mechanism as
# the eta' (two-photon loop), so B(eta'->mumu)/B(eta->mumu) cancels much of the
# theory and muon-efficiency systematics.  phi -> mumu is the EXPERIMENTAL
# calibration: ~45x more abundant and only 62 MeV from the eta', so if the D0 peak
# is not visible there the eta' search is hopeless and we know it cheaply.
#
# The dimuon mass is left UNCONSTRAINED (dileptonMassContraint = -1) because m(mumu)
# is the search variable; the builder stores fitted_mll next to the D0 mass, giving a
# 2-D (m_D0, m_mumu) analysis instead of one window per hypothesis.

D0MuMu = cms.EDProducer(
    'DiMuonBuilder',
    src                = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    # offline looser than the trigger (HLT_DoubleMu4_3_LowMass), tracker muons so
    # that the very collimated pairs from a light resonance still reconstruct
    lep1Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    preVtxSelection  = cms.string('charge() == 0 && 0.40 < mass && mass < 1.15'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001'),
)

CountD0MuMu = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("D0MuMu:SelectedDiLeptons")
)

D0ToKshortMuMu = cms.EDProducer(
    'BToV0LLBuilder',
    dileptons             = cms.InputTag("D0MuMu:SelectedDiLeptons"),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    v0s                   = cms.InputTag('KshortToPiPi', 'SelectedV0Collection'),
    v0TransientTracks     = cms.InputTag('KshortToPiPi', 'SelectedV0TransientCollection'),
    tracks                = cms.InputTag("packedPFCandidates"),
    PUtracks              = cms.InputTag('tracksBPH', 'SelectedTracks'),
    beamSpot              = cms.InputTag("offlineBeamSpot"),
    # D0 is 1864.84 MeV; keep generous sidebands for the background fit
    preVtxSelection  = cms.string('pt > 3.0 '
                                  '&& 1.65 < mass && mass < 2.10 '
                                  '&& userFloat("min_dr") > 0.02'),
    postVtxSelection = cms.string('1.70 < userFloat("fitted_mass") && userFloat("fitted_mass") < 2.05 '
                                  '&& userFloat("sv_prob") > 0.001 '
                                  '&& userFloat("fitted_cos_theta_2D") > 0.9'),
    dileptonMassContraint = cms.double(-1)      # -1: m(mumu) free -- it is the observable
)

########################### Tables ###########################

D0ToKshortMuMuTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("D0ToKshortMuMu"),
    cut       = cms.string(""),
    name      = cms.string("D0ToKshortMuMu"),
    doc       = cms.string("D0 -> K_S(pi pi) mu mu ; m(mumu) spans eta/omega/eta'/phi"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        l1_idx      = uint('l1_idx'),
        l2_idx      = uint('l2_idx'),
        kshort_idx  = uint('v0_idx'),
        min_dr      = ufloat('min_dr'),
        max_dr      = ufloat('max_dr'),
        # fit and vtx info
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        vtx_x     = ufloat('vtx_x'),
        vtx_y     = ufloat('vtx_y'),
        vtx_z     = ufloat('vtx_z'),
        # post fit properties -- fit_mass is the D0, mll_fullfit is the SEARCH variable
        mll_fullfit     = ufloat('fitted_mll'),
        mkshort_fullfit = ufloat('fitted_v0_mass'),
        fit_mass        = ufloat('fitted_mass'),
        fit_massErr     = ufloat('fitted_massErr'),
        fit_pt          = ufloat('fitted_pt'),
        fit_eta         = ufloat('fitted_eta'),
        fit_phi         = ufloat('fitted_phi'),
        # post-fit muons
        fit_l1_pt  = ufloat('fitted_l1_pt'),
        fit_l1_eta = ufloat('fitted_l1_eta'),
        fit_l1_phi = ufloat('fitted_l1_phi'),
        fit_l2_pt  = ufloat('fitted_l2_pt'),
        fit_l2_eta = ufloat('fitted_l2_eta'),
        fit_l2_phi = ufloat('fitted_l2_phi'),
        # post-fit Kshort
        fit_kshort_pt  = ufloat('fitted_v0_pt'),
        fit_kshort_eta = ufloat('fitted_v0_eta'),
        fit_kshort_phi = ufloat('fitted_v0_phi'),
        # isolation / ip
        kshort_svip2d     = ufloat('v0_svip2d'),
        kshort_svip2d_err = ufloat('v0_svip2d_err'),
        l1_iso04          = ufloat('l1_iso04'),
        l2_iso04          = ufloat('l2_iso04'),
        kshort_iso04      = ufloat('v0_iso04'),
    )
)

D0MuMuTable = cms.EDProducer("SimpleCompositeCandidateFlatTableProducer",
    src       = cms.InputTag("D0MuMu:SelectedDiLeptons"),
    cut       = cms.string(""),
    name      = cms.string("D0MuMu"),
    doc       = cms.string("Wide low-mass dimuons feeding the D0 -> K_S mumu build"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        l1_idx  = uint('l1_idx'),
        l2_idx  = uint('l2_idx'),
        svprob  = ufloat('sv_prob'),
        chi2    = ufloat('sv_chi2'),
        vtx_x   = ufloat('vtx_x'),
        vtx_y   = ufloat('vtx_y'),
        vtx_z   = ufloat('vtx_z'),
        fitted_mass    = ufloat('fitted_mass'),
        fitted_massErr = ufloat('fitted_massErr'),
        fitted_pt      = ufloat('fitted_pt'),
        fitted_eta     = ufloat('fitted_eta'),
        fitted_phi     = ufloat('fitted_phi'),
    )
)

CountD0ToKshortMuMu = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("D0ToKshortMuMu")
)

########################### Sequences ############################
D0MuMuSequence         = cms.Sequence( D0MuMu )
D0MuMuTables           = cms.Sequence( D0MuMuTable )
D0ToKshortMuMuSequence = cms.Sequence( D0ToKshortMuMu )
D0ToKshortMuMuTables   = cms.Sequence( D0ToKshortMuMuTable )
