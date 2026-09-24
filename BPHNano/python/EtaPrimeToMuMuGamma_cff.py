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
    # 'skip'  : a missing photon collection yields no candidates for that event (default)
    # 'throw' : fail the job instead -- for auditing whether a dataset is affected
    # Either way EtaPrimeToMuMuGammaInput_photonsPresent records it per event.
    missingPhotons  = cms.string('skip'),
    # 3-body fit (Kirill Ivanov's recipe): the dimuon's l1_idx/l2_idx index muonBPH:AllMuons, and
    # AllTransientMuons is index-aligned with it
    muonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    # The conversion pair becomes ONE photon particle before the 3-body fit, in two ways stored
    # side by side: the fit CMS conversion reconstruction runs (vertex + PhiTheta colinearity;
    # 99.8% efficient, reproduces the stored conversion) -> fitted_mass, svprob, ...; and, if
    # fourBodyFit, Kirill's own photon fit: plain 2-track vertex fit + zero-mass constraint
    # (fails for ~41% of conversions: the tracks are tangent at the vertex) -> *_4body.
    # No pi0 veto here: it is an analysis cut on gamma_flags, never a production one.
    fourBodyFit = cms.bool(True),
    # = RecoEgamma/EgammaPhotonProducers/python/allConversions_cfi.py (the colinearity fit)
    conversionFitParameters = cms.PSet(
        maxDelta            = cms.double(0.01),
        maxReducedChiSq     = cms.double(225.),
        minChiSqImprovement = cms.double(50.),
        maxNbrOfIterations  = cms.int32(40),
    ),
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
        # CandVars stores mass at precision=10, i.e. quantised in 2^-11 = 0.49 MeV steps below
        # 1 GeV -- a comb that aliases against any binning. Overridden to full precision; it must
        # be done INSIDE a clone (a PSet refuses a second 'mass' after CandVars is merged in).
        CandVars.clone(mass = Var("mass", float, precision=-1, doc="mu mu + photon 4-vector sum (no vertex fit)")),
        # --- 4body: the same fit with Kirill's own photon fit (fourBodyFit; status -9 = off) ---
        sv_ok_4body          = uint('sv_ok_4body'),
        fitted_mass_4body    = ufloat('fitted_mass_4body', doc="mass with Kirill's photon fit (2-track vertex + zero-mass); -1 if a fit failed"),
        fitted_massErr_4body = ufloat('fitted_massErr_4body'),
        svprob_4body         = ufloat('svprob_4body'),
        gamma_fit_status_4body = uint('gamma_fit_status_4body', doc="as gamma_fit_status, Kirill's photon fit; -9 = not run"),
        gamma_fit_prob_4body   = ufloat('gamma_fit_prob_4body'),
        # --- 3-body fit: mu+ mu- and the conversion photon (colinearity-constrained fit) ---
        sv_ok          = uint('sv_ok'),
        fitted_mass    = ufloat('fitted_mass', doc="3-body fit mass; -1 if the fit failed"),
        fitted_massErr = ufloat('fitted_massErr'),
        svprob         = ufloat('svprob', doc="3-body vertex probability"),
        fitted_pt      = ufloat('fitted_pt'),
        fitted_eta     = ufloat('fitted_eta'),
        fitted_phi     = ufloat('fitted_phi'),
        vtx_x = ufloat('vtx_x'), vtx_y = ufloat('vtx_y'), vtx_z = ufloat('vtx_z'),
        gamma_flags     = uint('gamma_flags', doc="OniaPhotonConversionProducer flags; pi0 veto (analysis level) = (gamma_flags & 16) == 0"),
        gamma_fit_status = uint('gamma_fit_status', doc="conversion fit: 1 ok; 0 no tracks, -1 bad transient track, "
                                "-2/-3/-4 ee vertex fit threw/invalid/chi2<0, -5/-6 zero-mass constraint threw/invalid (4body fit only)"),
        gamma_fit_prob  = ufloat('gamma_fit_prob', doc="conversion 2-track vertex fit prob (colinearity-constrained)"),
        gamma_fit_vtx_r = ufloat('gamma_fit_vtx_r'),
        gamma_fit_vtx_z = ufloat('gamma_fit_vtx_z'),
        gamma_fit_pt    = ufloat('gamma_fit_pt'),
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

# full-precision eta/phi (mass already is, above)
full_precision_p4(EtaPrimeToMuMuGammaTable)
