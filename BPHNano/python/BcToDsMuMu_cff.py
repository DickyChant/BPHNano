import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

##################  Bc+ -> (mu mu) Ds+,  Ds+ -> phi(K+K-) pi+  ####################
#
# ONE build covers all three modes because m(mumu) is left unconstrained:
#     Bc+ -> J/psi Ds(*)+     m(mumu) = 3.0969
#     Bc+ -> psi(2S) Ds(*)+   m(mumu) = 3.6861
#     Bc+ -> mu mu Ds(*)+     m(mumu) continuum, up to m(Bc) - m(Ds) = 4.307
#
# Motivation beyond the modes themselves: Bc+ -> J/psi Ds+ has a measured branching
# fraction, so reconstructing it in the SAME dataset gives the Bc yield in our own
# data.  That is what converts the existing Bc+ -> J/psi Lambda~ p result from an
# event-count upper limit (550-1300 events) into a branching-fraction ratio.
#
# Ds*+ is deliberately NOT targeted for now.  Ds*+ -> Ds+ gamma (Delta_m = 143.8 MeV)
# with the photon unreconstructed would appear as a satellite near 6131 MeV, so the mass
# window is cut at 6.15 GeV to leave it OUT rather than opened down to collect it.  The
# fully reconstructed Bc+ peak at 6274.7 keeps ~5 sigma of room below it.
#
# Ds+ -> phi pi+ is the golden mode: B = 4.5% x B(phi->KK) = 49.1%.  The same K+K-pi+
# final state also collects Ds+ -> K*0(892) K+, which is why m(KK) is stored rather
# than cut hard in production -- both sub-resonances are separable offline.

# ---- the phi: a ditrack with BOTH tracks given the kaon mass ----
PhiToKK = cms.EDProducer(
    'DiTrackBuilder',
    tracks          = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    trk1Selection   = cms.string('pt > 0.7 && abs(eta) < 2.4'),
    trk2Selection   = cms.string('pt > 0.7 && abs(eta) < 2.4'),
    beamSpot        = cms.InputTag('offlineBeamSpot'),
    trk1Mass        = cms.double(0.493677),         # K
    trk2Mass        = cms.double(0.493677),         # K
    preVtxSelection = cms.string('abs(userCand("trk1").vz - userCand("trk2").vz) <= 1.0 '
                                 '&& charge() == 0 '
                                 '&& 0.98 < mass && mass < 1.07'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001 '
                                  '&& 0.99 < userFloat("fitted_mass") '
                                  '&& userFloat("fitted_mass") < 1.05'),
)

# ---- the dimuon: WIDE, it carries the search variable ----
BcMuMu = cms.EDProducer(
    'DiMuonBuilder',
    src                = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    # loose on purpose: the working point is applied offline so tight/medium/soft stay
    # comparable on identical candidates, the same choice as the D0 and DPi builds
    lep1Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    # 2.0-4.4 spans J/psi, psi(2S) and the non-resonant continuum up to the 4.307
    # kinematic limit.  It does NOT go below 2.0: the low-q2 continuum is dominated by
    # combinatorics and would multiply the 5-track combinatorics beyond usefulness.
    preVtxSelection  = cms.string('charge() == 0 && 2.0 < mass && mass < 4.4'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001'),
)

BcToDsMuMu = cms.EDProducer(
    'BcToDsLLBuilder',
    dileptons             = cms.InputTag('BcMuMu', 'SelectedDiLeptons'),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    ditracks              = cms.InputTag('PhiToKK', 'SelectedLambdaCollection'),
    transientTracks       = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    pions                 = cms.InputTag('tracksBPH', 'SelectedTracks'),
    pionsTransientTracks  = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    pionMass              = cms.double(0.13957039),
    PUtracks              = cms.InputTag('tracksBPH', 'SelectedTracks'),
    beamSpot              = cms.InputTag('offlineBeamSpot'),
    # Bc+ is 6274.7 MeV.  Lower edge 6.15 sits ABOVE the Ds*+ satellite (~6131) so the
    # partially reconstructed mode is excluded; upper edge 6.45 gives sideband.
    preVtxSelection  = cms.string('pt > 8.0 && 6.05 < mass && mass < 6.55'),
    postVtxSelection = cms.string('6.15 < userFloat("fitted_mass") '
                                  '&& userFloat("fitted_mass") < 6.45 '
                                  '&& userFloat("sv_prob") > 0.005 '
                                  '&& userFloat("fitted_cos_theta_2D") > 0.99 '
                                  # the Ds+ tag: 1968.35 MeV, +-40 MeV
                                  '&& 1.928 < userFloat("fitted_ds_mass") '
                                  '&& userFloat("fitted_ds_mass") < 2.008'),
    dileptonMassContraint = cms.double(-1)      # m(mumu) free -- it is the observable
)

########################### Tables ###########################

BcToDsMuMuTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag('BcToDsMuMu'),
    cut       = cms.string(''),
    name      = cms.string('BcToDsMuMu'),
    doc       = cms.string('Bc+ -> (mumu) Ds+, Ds+ -> phi(KK) pi+'),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        l1_idx   = uint('l1_idx'),
        l2_idx   = uint('l2_idx'),
        trk1_idx = uint('trk1_idx'),
        trk2_idx = uint('trk2_idx'),
        pi_idx   = uint('pi_idx'),
        min_dr   = ufloat('min_dr'),
        max_dr   = ufloat('max_dr'),
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        # the three masses that define the decay
        fit_mass    = ufloat('fitted_mass'),          # Bc
        fit_massErr = ufloat('fitted_massErr'),
        mll_fullfit = ufloat('fitted_mll'),           # J/psi / psi(2S) / continuum
        mds_fullfit = ufloat('fitted_ds_mass'),       # Ds+
        mphi_fullfit= ufloat('fitted_ditrack_mass'),  # phi
        fit_pt      = ufloat('fitted_pt'),
        fit_eta     = ufloat('fitted_eta'),
        fit_phi     = ufloat('fitted_phi'),
        fit_pi_pt   = ufloat('fitted_pi_pt'),
        fit_pi_eta  = ufloat('fitted_pi_eta'),
        fit_pi_phi  = ufloat('fitted_pi_phi'),
    )
)

CountBcToDsMuMu = cms.EDFilter('PATCandViewCountFilter',
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag('BcToDsMuMu')
)

########################### Sequences ############################
BcToDsMuMuSequence = cms.Sequence( PhiToKK * BcMuMu * BcToDsMuMu )
BcToDsMuMuTables   = cms.Sequence( BcToDsMuMuTable )
