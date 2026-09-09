import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *
from PhysicsTools.BPHNano.UpsilonTo2Mu2E_cff import UpsilonTo2Mu2E, UpsilonTo2Mu2ETable
from PhysicsTools.BPHNano.EtaMuMu_cff import EtaMuMu

# ============================================================================
#  eta'(958) -> mu+ mu- e+ e-
#
#  Mirrors the eta -> 4mu / eta -> 2l2pi recipe (AN-25-223) into the eta' region,
#  but with the two hadron legs replaced by ELECTRONS. Reuses UpsilonTo2Mu2EBuilder,
#  which is generic: the mass window is a cut string and the builder always assigns
#  MUON_MASS to the two leptons and ELECTRON_MASS to the two tracks.
#
#  E-LEG SOURCES:
#     EtaPrimeTo2Mu2EEle   : the OR of LowPtElectron + standard slimmedElectrons, de-duplicated,
#                            in ONE vertex fit. This is the production configuration.
#     EtaPrimeTo2Mu2ELowPt : LowPtElectron only -- kept as the simple historical cross-check.
#  The generic-track variant (e-legs from packedPFCandidates+lostTracks under the electron
#  mass hypothesis) has been REMOVED. It existed only to check LowPtElectron against generic
#  tracks; now that both real electron collections are used in one fit it adds nothing, and
#  with the mass window widened to 0.45 GeV its combinatorics over every packedPFCandidate
#  blow up and crash the job (bus error).
#
#  Mass window 0.45-1.15 GeV. It used to start at 0.80, which covered eta'(957.8) and the
#  phi(1019) but left the analysis with NO calibration line. Extending down to 0.45 brings in
#  the eta(548), whose eta -> mu+mu- e+e- decay CMS has now OBSERVED and measured:
#  B = (2.4 +- 0.8)e-6, CMS-BPH-24-001 / arXiv:2605.00615, from 2022 alone. That makes the eta
#  a standard candle of known rate sitting in the same sample, reconstructed the same way --
#  the role J/psi -> 4mu plays for the 4mu channel -- so the eta' can be measured as a ratio
#  to it instead of in absolute terms.
#
#  NOTE the dilepton is EtaMuMu (wide-open: charge==0, sv_prob>0), NOT the Upsilon MuMu:
#  m(mumu) in eta'->2mu2e is squeezed into [2*m_mu, m_eta'] = [0.211, 0.958] GeV.
# ============================================================================

ETAP_MASS_MIN = 0.45      # was 0.80; lowered to include the eta(548) calibration line
ETAP_MASS_MAX = 1.15

# charge: |q| <= 2 keeps BOTH the opposite-sign signal (q = 0) and the same-sign e+e+ / e-e-
# combinatorial control (q = +-2, since the dimuon is already required opposite-sign). The
# 4-body charge is stored, so the two separate offline. Without this there is no combinatorial
# control at all -- the old 'charge() == 0' left 0-4 same-sign candidates in the whole campaign.
_pre_sel = ('pt > 5. && abs(charge()) <= 2 '                  # pt>5 = the boost requirement
            '&& (mass > %.2f && mass < %.2f)' % (ETAP_MASS_MIN, ETAP_MASS_MAX))
_post_sel = ('userFloat("sv_prob") > 0.0 '
             '&& userFloat("fitted_mass") > %.2f && userFloat("fitted_mass") < %.2f'
             % (ETAP_MASS_MIN, ETAP_MASS_MAX))
# no l_xy cut here: eta' is prompt, but l_xy / cos_theta_2D are stored so the prompt
# requirement can be tightened offline instead of being baked into the producer.

_trk_sel = 'pt > 0.5 && abs(eta) < 2.5'   # IDENTICAL in both variants -> fair comparison

########################### Dimuon ###########################
# A DEDICATED dimuon for eta'. The stock EtaMuMu is wide open (charge==0, sv_prob>0, NO mass
# window), so on muon-rich Parking data every OS dimuon gets crossed with every electron pair
# and each combination costs a 4-track KinematicVertexFit -> the producer crawls.
# Kinematics bound it for free: in eta' -> mu+mu- e+e- the dimuon must satisfy
#   2*m_mu = 0.211 GeV  <  m(mumu)  <  m_eta' = 0.958 GeV
# so a [0.20, 1.00] window loses no signal and removes almost all of the combinatorics.
# The window also covers the eta(548) calibration line, where m(mumu) < 0.548.
EtaPrimeMuMu = EtaMuMu.clone(
    preVtxSelection  = cms.string('abs(userCand("l1").vz - userCand("l2").vz) <= 1. '
                                  '&& charge() == 0 && mass() > 0.20 && mass() < 1.00'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001 '
                                  '&& userFloat("fitted_mass") > 0.20 && userFloat("fitted_mass") < 1.00'),
)

########################### Builders (two e-leg variants) ###########################
EtaPrimeTo2Mu2ELowPt = UpsilonTo2Mu2E.clone(
    dileptons        = cms.InputTag("EtaPrimeMuMu", "SelectedDiLeptons"),
    tracks           = cms.InputTag('lowPtEleTracks', 'SelectedElectrons'),
    transientTracks  = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectrons'),
    transientTracksLow     = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectronsLow'),
    transientTracksNominal = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectronsNominal'),
    trk1Selection    = cms.string(_trk_sel),
    trk2Selection    = cms.string(_trk_sel),
    allowSameSignTrackPair = cms.bool(True),   # build the same-sign control alongside signal
    preVtxSelection  = cms.string(_pre_sel),
    postVtxSelection = cms.string(_post_sel),
)

# e-legs from BOTH electron collections at once (LowPtElectron ~1-5 GeV + standard >5 GeV,
# duplicates removed). trk{1,2}_src say which table each leg came from, giving the three
# analysis categories in one collection:
#   (0,0) both LowPtElectron   (0,1)/(1,0) mixed   (1,1) both standard
# Fit them as three categories with a common mass and per-category resolution and yield.
EtaPrimeTo2Mu2EEle = UpsilonTo2Mu2E.clone(
    dileptons        = cms.InputTag("EtaPrimeMuMu", "SelectedDiLeptons"),
    tracks           = cms.InputTag('etapEleTracks', 'SelectedElectrons'),
    transientTracks  = cms.InputTag('etapEleTracks', 'SelectedTransientElectrons'),
    transientTracksLow     = cms.InputTag('etapEleTracks', 'SelectedTransientElectronsLow'),
    transientTracksNominal = cms.InputTag('etapEleTracks', 'SelectedTransientElectronsNominal'),
    trk1Selection    = cms.string(_trk_sel),
    trk2Selection    = cms.string(_trk_sel),
    allowSameSignTrackPair = cms.bool(True),
    preVtxSelection  = cms.string(_pre_sel),
    postVtxSelection = cms.string(_post_sel),
)


########################### Tables ###########################
# clone the Upsilon 2mu2e table so the variable list stays in sync with the builder
EtaPrimeTo2Mu2ELowPtTable = UpsilonTo2Mu2ETable.clone(
    src  = cms.InputTag("EtaPrimeTo2Mu2ELowPt"),
    name = cms.string("EtaPrimeTo2Mu2ELowPt"),
    doc  = cms.string("eta(548)/eta'(958) -> mu+mu- e+e- ; e-legs from LowPtElectron "
                      "(trk{1,2}_idx index into the LowPtElectron table). charge==0 is the "
                      "signal, |charge|==2 the same-sign combinatorial control."),
)

EtaPrimeTo2Mu2EEleTable = UpsilonTo2Mu2ETable.clone(
    src  = cms.InputTag("EtaPrimeTo2Mu2EEle"),
    name = cms.string("EtaPrimeTo2Mu2EEle"),
    doc  = cms.string("eta(548)/eta'(958) -> mu+mu- e+e- ; e-legs from LowPtElectron AND the "
                      "standard Electron collection. trk{1,2}_src = 0 -> LowPtElectron table, "
                      "1 -> Electron table; (src1,src2) gives the three fit categories. "
                      "charge==0 is signal, |charge|==2 the same-sign control."),
)


########################### MC matching ###########################
# 331 = eta'(958). mcStatus covers both conventions seen in this package
# (2 = shower/decayed, 22 = hard scattering); validate on MC before trusting.
def _mc_match(src_tag, label):
    return cms.EDProducer("MCMatcher",
        src         = src_tag,
        matched     = cms.InputTag("finalGenParticlesBPH"),
        mcPdgId     = cms.vint32(331),
        checkCharge = cms.bool(False),
        mcStatus    = cms.vint32(2, 22),
        maxDeltaR   = cms.double(0.1),
        maxDPtRel   = cms.double(0.5),
        resolveAmbiguities    = cms.bool(True),
        resolveByMatchQuality = cms.bool(True),
    )

EtaPrimeTo2Mu2ELowPtBPHMCMatch = _mc_match(EtaPrimeTo2Mu2ELowPtTable.src, "LowPt")
EtaPrimeTo2Mu2EEleBPHMCMatch   = _mc_match(EtaPrimeTo2Mu2EEleTable.src,   "Ele")

def _mc_table(table, matcher_name):
    return cms.EDProducer("CandMCMatchTableProducerBPH",
        recoObjects   = table.src,
        genParts      = cms.InputTag("finalGenParticlesBPH"),
        mcMap         = cms.InputTag(matcher_name),
        objName       = table.name,
        objType       = cms.string("Other"),
        objBranchName = cms.string("genPart"),
        genBranchName = cms.string(table.name.value()),
        docString     = cms.string("MC matching to eta'(958) -> 2mu2e"),
    )

EtaPrimeTo2Mu2ELowPtBPHMCTable = _mc_table(EtaPrimeTo2Mu2ELowPtTable, "EtaPrimeTo2Mu2ELowPtBPHMCMatch")
EtaPrimeTo2Mu2EEleBPHMCTable   = _mc_table(EtaPrimeTo2Mu2EEleTable,   "EtaPrimeTo2Mu2EEleBPHMCMatch")

########################### Count filters (for the skim) ###########################
CountEtaPrimeTo2Mu2ELowPt = cms.EDFilter("CandViewCountFilter",
    src=cms.InputTag("EtaPrimeTo2Mu2ELowPt"), minNumber=cms.uint32(1))
CountEtaPrimeTo2Mu2EEle = cms.EDFilter("CandViewCountFilter",
    src=cms.InputTag("EtaPrimeTo2Mu2EEle"), minNumber=cms.uint32(1))

########################### Sequences ###########################
EtaPrimeMuMuSequence         = cms.Sequence(EtaPrimeMuMu)
EtaPrimeTo2Mu2ELowPtSequence = cms.Sequence(EtaPrimeMuMu + EtaPrimeTo2Mu2ELowPt)
EtaPrimeTo2Mu2ELowPtTables   = cms.Sequence(EtaPrimeTo2Mu2ELowPtTable)
EtaPrimeTo2Mu2EEleSequence   = cms.Sequence(EtaPrimeTo2Mu2EEle)    # add on top of EtaPrimeMuMu
EtaPrimeTo2Mu2EEleTables     = cms.Sequence(EtaPrimeTo2Mu2EEleTable)
