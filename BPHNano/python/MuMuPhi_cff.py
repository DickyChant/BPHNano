import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *
from PhysicsTools.BPHNano.ZToLLV_cff import ZToMuMuPhi, ZToMuMuPhiTable, MuMuWide

# ============================================================================
#  mu+ mu- phi(1020), phi -> K+K-   --  TWO channels, built together on the same events
#
#  Motivated by eta_c(1S) -> gamma phi (PDG 1.15e-5): the mu mu version is the virtual-photon
#  analogue eta_c -> gamma* phi -> mu mu phi.
#
#  They are built SEPARATELY because their signatures are opposite, so shared cuts would be
#  the worst of both worlds:
#
#              m(mumu)          vertex        m(mumuKK)     mass constraint
#    B_s       J/psi 3.097      DISPLACED     5.3669        m(mumu) -> J/psi   (muons dominate)
#    eta_c     < 1.97           PROMPT        2.9839        m(KK)   -> phi     (KK carries more)
#
#  B_s -> J/psi phi is the CONTROL: abundant here and one of the best-measured B_s modes, so
#  it calibrates the mu-mu-K-K efficiency end to end. No B_s peak => the eta_c search has no
#  reach, which is itself the answer.
#
#  Both use the phi window EARLY in the builder (vMassMin/Max), which is what bounds the
#  combinatorics before the expensive 4-track fit.
# ============================================================================

PHI_LO, PHI_HI = 1.01, 1.03      # phi(1020), Gamma = 4.25 MeV
PHI_MASS  = 1.019455
JPSI_MASS = 3.096900

# --- shared soft dimuon. MuMuWide is tuned for Z (mu pT > 5/3) and would kill charmonium,
# where J/psi -> mumu gives ~1.5 GeV muons. Window spans BOTH the eta_c region (m(mumu) up to
# m_etac - m_phi = 1.97) and the J/psi needed by B_s.
MuMuCharm = MuMuWide.clone(
    lep1Selection   = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection   = cms.string('pt > 1.5 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    preVtxSelection = cms.string('abs(userCand("l1").vz - userCand("l2").vz) <= 1. '
                                 '&& charge() == 0 && mass() > 0.20 && mass() < 4.00'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001 '
                                  '&& userFloat("fitted_mass") > 0.20 && userFloat("fitted_mass") < 4.00'),
)

_PHI_POST = ('userFloat("fitted_ditrack_mass") > %.3f && userFloat("fitted_ditrack_mass") < %.3f'
             % (PHI_LO, PHI_HI))

# ---------------- CONTROL: B_s -> J/psi(mumu) phi(KK) ----------------
# dimuon pinned to J/psi, m(mumuKK) around the B_s, and DISPLACED (B_s ctau ~ 450 um).
# l_xy_sig is required loosely here; tighten offline. Constrain m(mumu) -> J/psi.
BsToJpsiPhi = ZToMuMuPhi.clone(
    dileptons        = cms.InputTag('MuMuCharm', 'SelectedDiLeptons'),
    vMassMin         = cms.double(PHI_LO),
    vMassMax         = cms.double(PHI_HI),
    massConstraint   = cms.string('dilepton'),
    constraintMass   = cms.double(JPSI_MASS),
    preVtxSelection  = cms.string('charge() == 0 && mass() > 5.0 && mass() < 5.8'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.01 '
                                  '&& userFloat("fitted_mass") > 5.0 && userFloat("fitted_mass") < 5.8 '
                                  '&& userFloat("fitted_mll") > 2.95 && userFloat("fitted_mll") < 3.25 '
                                  '&& userFloat("l_xy") > 0.01 '   # displaced: >100 um
                                  '&& ' + _PHI_POST),
)

# ---------------- SEARCH: eta_c -> mu mu phi(KK) ----------------
# low-mass dimuon, PROMPT, m(mumuKK) around eta_c(1S) (window kept open to psi(2S) so chi_c /
# eta_c(2S) are visible and the sidebands are usable). Constrain m(KK) -> phi.
# No l_xy cut baked in -- prompt-ness is left to the offline fit; l_xy is stored.
EtaCToMuMuPhi = ZToMuMuPhi.clone(
    dileptons        = cms.InputTag('MuMuCharm', 'SelectedDiLeptons'),
    vMassMin         = cms.double(PHI_LO),
    vMassMax         = cms.double(PHI_HI),
    massConstraint   = cms.string('ditrack'),
    constraintMass   = cms.double(PHI_MASS),
    preVtxSelection  = cms.string('charge() == 0 && mass() > 2.80 && mass() < 3.80'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.01 '
                                  '&& userFloat("fitted_mass") > 2.80 && userFloat("fitted_mass") < 3.80 '
                                  '&& userFloat("fitted_mll") < 2.10 '     # NOT a J/psi -> orthogonal to B_s
                                  '&& ' + _PHI_POST),
)

########################### Tables ###########################
BsToJpsiPhiTable = ZToMuMuPhiTable.clone(
    src  = cms.InputTag("BsToJpsiPhi"), name = cms.string("BsToJpsiPhi"),
    doc  = cms.string("CONTROL: B_s -> J/psi(mumu) phi(K+K-), m(mumu) J/psi-constrained, displaced"),
)
EtaCToMuMuPhiTable = ZToMuMuPhiTable.clone(
    src  = cms.InputTag("EtaCToMuMuPhi"), name = cms.string("EtaCToMuMuPhi"),
    doc  = cms.string("SEARCH: eta_c -> mu mu phi(K+K-), m(KK) phi-constrained, low-mass dimuon"),
)

########################### Count filters (skim: either channel) ###########################
CountBsToJpsiPhi   = cms.EDFilter("CandViewCountFilter", src=cms.InputTag("BsToJpsiPhi"),   minNumber=cms.uint32(1))
CountEtaCToMuMuPhi = cms.EDFilter("CandViewCountFilter", src=cms.InputTag("EtaCToMuMuPhi"), minNumber=cms.uint32(1))

########################### Sequences ###########################
MuMuPhiSequence = cms.Sequence(MuMuCharm + BsToJpsiPhi + EtaCToMuMuPhi)
MuMuPhiTables   = cms.Sequence(BsToJpsiPhiTable + EtaCToMuMuPhiTable)
