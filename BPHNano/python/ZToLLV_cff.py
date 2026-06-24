import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

# ============================================================================
#  Z -> l+ l- V ,  V -> h+ h-  (vector meson as two charged tracks)
#  V = phi(1020) -> K+K-  (narrow, clean)  or  rho0(770) -> pi+pi-  (broad)
#  l = mu (this file) ; e channel needs a standard-electron transient-track
#  producer (see TODO at bottom) and is scaffolded but not wired yet.
#
#  Inputs reused from the existing BPHNano chain:
#    muonBPH:AllMuons / muonBPH:AllTransientMuons   (energetic Z muons)
#    tracksBPH:SelectedTracks / :SelectedTransientTracks  (from packedPFCandidates)
#  Trigger: collect with a standard SINGLE-lepton HLT (set in the run cfg).
# ============================================================================

MUON_MASS  = 0.10565837
MUON_SIGMA = 0.0000001     # match the LEP_SIGMA scale used in helper.h (1e-3..1e-7); fit is stable
ELE_MASS   = 0.000511
ELE_SIGMA  = 0.00001
PI_MASS    = 0.139571
K_MASS     = 0.493677
H_SIGMA    = 0.000016      # PI_SIGMA == K_SIGMA in helper.h

# ---- wide dimuon (NOT J/psi-windowed): the Z's energetic lepton pair ----
MuMuWide = cms.EDProducer(
    'DiMuonBuilder',
    src                = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    lep1Selection      = cms.string('pt > 5 && abs(eta) < 2.4 && isLooseMuon'),
    lep2Selection      = cms.string('pt > 3 && abs(eta) < 2.4 && isLooseMuon'),
    preVtxSelection    = cms.string('charge() == 0 && mass() > 1.0'),
    postVtxSelection   = cms.string('userFloat("sv_prob") > 0.0'),
)

# ---- shared track selection (V daughters): a Z->V gives an energetic (~30-45 GeV) V, so its
# kaons/pions are ~GeV+; pt>1.0 keeps signal while cutting the pileup-track combinatorics ~10x ----
_TRK_SEL = 'pt > 1.0 && abs(eta) < 2.5'

# common prompt + Z-window post-fit cut; Z is prompt -> small l_xy. KEPT LOOSE on purpose:
# the m(ll) Z-VETO (signal = m(ll) below the Z; Z->ll+hadrons bkg = m(ll)=m_Z) is applied
# OFFLINE, not here -- baking it into the skim would discard the m(ll)~91 CONTROL region needed
# for background estimation. m(ll) is stored (`mll`). Isolation also stored, not cut (experimental).
_Z_POST = ('userFloat("sv_prob") > 0.001 '
           '&& userFloat("fitted_mass") > 70 && userFloat("fitted_mass") < 110 '
           '&& userFloat("l_xy") < 0.1')


def _zllv(dileptons, lep_ttracks, lep_mass, lep_sigma, trk_mass, trk_sigma, v_lo, v_hi):
    """Configure one ZToLLVBuilder instance for a given lepton+track hypothesis and V window.
    The [v_lo, v_hi] di-track window is enforced EARLY in the builder (vMassMin/vMassMax) so the
    expensive candidate-build + 4-track fit only runs for pairs inside the rho/phi window -> bounds
    the combinatorics; the fitted-mass window repeats it post-fit."""
    return cms.EDProducer(
        'ZToLLVBuilder',
        dileptons             = cms.InputTag(dileptons),
        leptonTransientTracks = cms.InputTag(lep_ttracks[0], lep_ttracks[1]),
        tracks                = cms.InputTag('tracksBPH', 'SelectedTracks'),
        transientTracks       = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
        beamSpot              = cms.InputTag('offlineBeamSpot'),
        lepMass  = cms.double(lep_mass),
        lepSigma = cms.double(lep_sigma),
        trkMass  = cms.double(trk_mass),
        trkSigma = cms.double(trk_sigma),
        vMassMin = cms.double(v_lo),
        vMassMax = cms.double(v_hi),
        trk1Selection = cms.string(_TRK_SEL),
        trk2Selection = cms.string(_TRK_SEL),
        preVtxSelection = cms.string('charge() == 0 && mass() > 60 && mass() < 120'),
        postVtxSelection = cms.string(
            _Z_POST + ' && userFloat("fitted_ditrack_mass") > %g '
            '&& userFloat("fitted_ditrack_mass") < %g' % (v_lo, v_hi)),
    )


# phi(1020) -> K+K-  : narrow window (signal 1.019 + small sidebands for the peak fit)
ZToMuMuPhi = _zllv('MuMuWide:SelectedDiLeptons', ('muonBPH', 'AllTransientMuons'),
                   MUON_MASS, MUON_SIGMA, K_MASS, H_SIGMA, 1.00, 1.05)
# rho0(770) -> pi+pi- : broad window
ZToMuMuRho = _zllv('MuMuWide:SelectedDiLeptons', ('muonBPH', 'AllTransientMuons'),
                   MUON_MASS, MUON_SIGMA, PI_MASS, H_SIGMA, 0.50, 1.00)


########################### Tables ###########################

def _zllv_table(src, name, doc):
    return cms.EDProducer(
        'SimpleCompositeCandidateFlatTableProducer',
        src = cms.InputTag(src), cut = cms.string(""),
        name = cms.string(name), doc = cms.string(doc),
        singleton = cms.bool(False), extension = cms.bool(False),
        variables = cms.PSet(
            CandVars,
            l1_idx = uint('l1_idx'), l2_idx = uint('l2_idx'), ll_idx = uint('ll_idx'),
            trk1_idx = uint('trk1_idx'), trk2_idx = uint('trk2_idx'),
            mll        = ufloat('mll'),
            m_ditrack  = ufloat('m_ditrack'),
            ditrack_pt = ufloat('ditrack_pt'),   # pT(hh): energetic for a real Z->V, soft for combinatorial
            dilep_pt   = ufloat('dilep_pt'),
            min_dr = ufloat('min_dr'), max_dr = ufloat('max_dr'),
            # vtx + prompt
            chi2 = ufloat('sv_chi2'), svprob = ufloat('sv_prob'),
            cos2D = ufloat('cos_theta_2D'), fit_cos2D = ufloat('fitted_cos_theta_2D'),
            l_xy = ufloat('l_xy'), l_xy_unc = ufloat('l_xy_unc'), l_xy_sig = ufloat('l_xy_sig'),
            # post-fit masses (fitted_mass = Z candidate, fitted_ditrack_mass = V)
            mll_fullfit     = ufloat('fitted_mll'),
            mditrack_fullfit = ufloat('fitted_ditrack_mass'),
            ditrack_pt_fullfit = ufloat('fitted_ditrack_pt'),
            fitted_mass    = ufloat('fitted_mass'),
            fitted_massErr = ufloat('fitted_massErr'),
            fitted_pt = ufloat('fitted_pt'), fitted_eta = ufloat('fitted_eta'),
            fitted_phi = ufloat('fitted_phi'), fitted_rapidity = ufloat('fitted_rapidity'),
            vtx_x = ufloat('vtx_x'), vtx_y = ufloat('vtx_y'), vtx_z = ufloat('vtx_z'),
            # isolation + track IP
            l1_iso04 = ufloat('l1_iso04'), l2_iso04 = ufloat('l2_iso04'),
            trk1_iso04 = ufloat('trk1_iso04'), trk2_iso04 = ufloat('trk2_iso04'),
            trk1_svip2d = ufloat('trk1_svip2d'), trk2_svip2d = ufloat('trk2_svip2d'),
            # V-candidate isolation (sum pT of other tracks in dR<0.4 around V, excl. the 2 V tracks)
            v_iso = ufloat('v_iso'), v_iso_sumpt = ufloat('v_iso_sumpt'), v_iso_n = uint('v_iso_n'),
        )
    )


ZToMuMuPhiTable = _zllv_table('ZToMuMuPhi', 'ZToMuMuPhi', 'Z -> mu mu phi(->KK)')
ZToMuMuRhoTable = _zllv_table('ZToMuMuRho', 'ZToMuMuRho', 'Z -> mu mu rho(->pipi)')


def _count(src):
    return cms.EDFilter("PATCandViewCountFilter",
                        minNumber = cms.uint32(1), maxNumber = cms.uint32(999999),
                        src = cms.InputTag(src))


CountZToMuMuPhi = _count('ZToMuMuPhi')
CountZToMuMuRho = _count('ZToMuMuRho')


########################### e+e- channel (Z -> ee V) ###########################
# standard-electron transient tracks (parallel pat::Electron + TransientTrack) -> DiEle
ZElectrons = cms.EDProducer(
    'ElectronMerger',
    electrons         = cms.InputTag('slimmedElectrons'),
    electronSelection = cms.string('pt > 5 && abs(eta) < 2.5'),
    # standard Run3 cut-based MEDIUM ID applied in C++ (the string selector does NOT evaluate
    # electronID()). Selects real Z electrons; without it the dielectron is fakes/soft-e and
    # m(ee hh) sits well below the Z. Embedded WP verified present (medium passes ~16% of e).
    electronID        = cms.string('cutBasedElectronID-RunIIIWinter22-V1-medium'),
    electronIDmin     = cms.double(0.5),
)
# DiElectronBuilder = DiLeptonBuilder<pat::Electron> (already registered); fits the e+e- vertex
DiEle = cms.EDProducer(
    'DiElectronBuilder',
    src                = cms.InputTag('ZElectrons', 'Electrons'),
    transientTracksSrc = cms.InputTag('ZElectrons', 'TransientElectrons'),
    lep1Selection      = cms.string('pt > 5'),
    lep2Selection      = cms.string('pt > 5'),
    preVtxSelection    = cms.string('charge() == 0 && mass() > 1.0'),
    postVtxSelection   = cms.string('userFloat("sv_prob") > 0.0'),
)
# (the leptonTransientTracks for ZToEE* is the SAME ZElectrons:TransientElectrons that DiEle indexed)
ZToEEPhi = _zllv('DiEle:SelectedDiLeptons', ('ZElectrons', 'TransientElectrons'),
                 ELE_MASS, ELE_SIGMA, K_MASS, H_SIGMA, 1.00, 1.05)
ZToEERho = _zllv('DiEle:SelectedDiLeptons', ('ZElectrons', 'TransientElectrons'),
                 ELE_MASS, ELE_SIGMA, PI_MASS, H_SIGMA, 0.50, 1.00)
ZToEEPhiTable = _zllv_table('ZToEEPhi', 'ZToEEPhi', 'Z -> ee phi(->KK)')
ZToEERhoTable = _zllv_table('ZToEERho', 'ZToEERho', 'Z -> ee rho(->pipi)')
CountZToEEPhi = _count('ZToEEPhi')
CountZToEERho = _count('ZToEERho')


########################### Sequences ###########################
# mu mu V : MuMuWide feeds both V hypotheses
ZToMuMuVSequence = cms.Sequence(MuMuWide + ZToMuMuPhi + ZToMuMuRho)
ZToMuMuVTables   = cms.Sequence(ZToMuMuPhiTable + ZToMuMuRhoTable)
# ee V : ZElectrons -> DiEle feeds both V hypotheses
ZToEEVSequence = cms.Sequence(ZElectrons + DiEle + ZToEEPhi + ZToEERho)
ZToEEVTables   = cms.Sequence(ZToEEPhiTable + ZToEERhoTable)
