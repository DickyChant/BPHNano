import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *
from PhysicsTools.BPHNano.EtaPrimeTo2Mu2E_cff import EtaPrimeMuMu, ETAP_MASS_MIN, ETAP_MASS_MAX

# ============================================================================
#  eta(548)/eta'(958) -> mu+ mu- gamma, with the photon CONVERTED.
#
#  This is the NORMALISATION channel for the 2mu2e double-Dalitz search, exactly as in
#  CMS-BPH-24-001: the two modes have the same final-state particles, so the signal is
#  measured as a ratio and most systematics cancel. B(eta' -> mu+mu- gamma) = 1.09e-4 and
#  B(eta -> mu+mu- gamma) = 3.1e-4 are both known, which is what gives the search an
#  absolute scale.
#
#  The photons are taken from "oniaPhotonCandidates:conversions", which is ALREADY in the
#  Parking MiniAOD (OniaPhotonConversionProducer runs during PAT production): ~1.6 converted
#  photons per event at a pT median of ~0.8 GeV, which is the range a radiative eta'/eta
#  decay populates. Nothing needs to be re-run, and the producer must NOT be re-run on
#  MiniAOD anyway -- it unconditionally dereferences a reco::PFCandidateCollection that
#  MiniAOD does not contain.
#
#  Why this beats catching the conversion in the 2mu2e build: there, the photon is only seen
#  when BOTH of its legs happen to be reconstructed as LowPtElectron/Electron. Here the
#  conversion is used directly, so the efficiency is far higher -- and gamma_vtx_r (the
#  conversion radius: beam pipe ~2-3 cm, first pixel layers ~3-6 cm) is available per
#  candidate to confirm the photon is real.
# ============================================================================

EtaPrimeToMuMuGamma = cms.EDProducer(
    'MuMuGammaBuilder',
    dileptons = cms.InputTag('EtaPrimeMuMu', 'SelectedDiLeptons'),
    photons   = cms.InputTag('oniaPhotonCandidates', 'conversions'),
    beamSpot  = cms.InputTag('offlineBeamSpot'),
    # a genuine conversion happens in material, not at the beamline; the Onia producer's own
    # default is rho > 1.5 cm and this keeps that spirit while staying loose enough to study
    # the radius distribution offline
    photonSelection = cms.string('pt > 0.2 && abs(eta) < 2.5'),
    preSelection    = cms.string('mass > %.2f && mass < %.2f' % (ETAP_MASS_MIN, ETAP_MASS_MAX)),
    postSelection   = cms.string(''),
)

EtaPrimeToMuMuGammaTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag('EtaPrimeToMuMuGamma'),
    cut       = cms.string(''),
    name      = cms.string('EtaPrimeToMuMuGamma'),
    doc       = cms.string("eta(548)/eta'(958) -> mu+mu- gamma with a CONVERTED photon "
                           "(oniaPhotonCandidates:conversions). Normalisation channel for the "
                           "2mu2e double-Dalitz search; gamma_vtx_r is the conversion radius."),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        ll_idx    = uint('ll_idx'),
        gamma_idx = uint('gamma_idx'),
        l1_idx    = uint('l1_idx'),
        l2_idx    = uint('l2_idx'),
        # the dimuon: in a radiative decay m(mumu) is the Dalitz variable, not a resonance
        ll_mass    = ufloat('ll_mass'),
        ll_massErr = ufloat('ll_massErr'),
        ll_pt      = ufloat('ll_pt'),
        ll_svprob  = ufloat('ll_svprob'),
        # the photon, and where it converted
        gamma_pt    = ufloat('gamma_pt'),
        gamma_eta   = ufloat('gamma_eta'),
        gamma_phi   = ufloat('gamma_phi'),
        gamma_vtx_r = ufloat('gamma_vtx_r'),
        gamma_vtx_z = ufloat('gamma_vtx_z'),
        gamma_trk0_pt = ufloat('gamma_trk0_pt'),
        gamma_trk1_pt = ufloat('gamma_trk1_pt'),
        dR_ll_gamma   = ufloat('dR_ll_gamma'),
    )
)

CountEtaPrimeToMuMuGamma = cms.EDFilter("CandViewCountFilter",
    src=cms.InputTag("EtaPrimeToMuMuGamma"), minNumber=cms.uint32(1))

EtaPrimeToMuMuGammaSequence = cms.Sequence(EtaPrimeToMuMuGamma)
EtaPrimeToMuMuGammaTables   = cms.Sequence(EtaPrimeToMuMuGammaTable)
