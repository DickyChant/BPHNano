import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *
from PhysicsTools.BPHNano.UpsilonTo4Mu_cff import UpsilonTo4Mu, UpsilonTo4MuTable

# ============================================================================
#  eta_c -> 4 mu   (charmonium-region 4-muon scan)
#
#  Same generic EtaTo4MuBuilder as eta->4mu and Upsilon->4mu: four muons + a 4-track
#  KinematicVertexFit, with the mass window as a plain cut string. Only the window,
#  the muon thresholds and the MC PDG ids change.
#
#  WINDOW 2.80-3.90 GeV is deliberately WIDER than eta_c alone. It covers:
#      eta_c(1S) 2.9839   <- the target
#      J/psi     3.0969   <- CONTROL / NORMALISATION: J/psi is copiously produced in this
#                            dataset, so a 4mu signal there validates the chain and
#                            calibrates the sensitivity. No J/psi peak => no reach, which
#                            is itself the useful answer.
#      chi_c0/1/2 3.4147 / 3.5107 / 3.5562
#      eta_c(2S) 3.6376
#      psi(2S)   3.6861
#  Slice offline; it is only a cut string.
#
#  NO PROMPT (l_xy) CUT, unlike the Upsilon config: charmonium reaches us both promptly
#  AND from B decays (B -> eta_c X), which are displaced. l_xy / l_xy_sig / cos_theta_2D
#  are stored so prompt-vs-displaced can be separated offline instead of being thrown away
#  in the producer.
#
#  Muon thresholds are softer than the Upsilon ones (a 2.98 GeV parent gives each muon only
#  ~0.75 GeV in the rest frame) but not as soft as eta->4mu. muonBPH itself floors at pt>1.0.
# ============================================================================

ETAC_MASS_MIN = 2.80
ETAC_MASS_MAX = 3.90

# Muon selection follows the PUBLISHED eta->4mu recipe (BPH-22-003 / AN-25-223, preapp slide 11):
#   slimmedMuons, pT > 4 (3) GeV, |eta| < 2.4, MEDIUM ID, opposite charge, and TRIGGER MATCHING.
# The pT thresholds are not arbitrary: the dataset is collected with HLT_DoubleMu4_3_LowMass, so
# an event CANNOT have fired the trigger without muons above 4/3 GeV. Going softer than that (as
# an earlier version of this file did, at 2.0/1.5/1.0/1.0 + Loose ID) only manufactures
# combinations that can never be signal -- which is exactly what produced a featureless,
# purely combinatorial m(4mu) spectrum in the first pass over 2024 data.
EtaCTo4Mu = UpsilonTo4Mu.clone(
    lep1Selection = cms.string('pt > 4.0 && abs(eta) < 2.4 && isMediumMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isMediumMuon && isTrackerMuon'),
    lep3Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isMediumMuon && isTrackerMuon'),
    lep4Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isMediumMuon && isTrackerMuon'),
    preVtxSelection  = cms.string('charge() == 0 && pt > 3. '
                                  '&& (mass > %.2f && mass < %.2f)' % (ETAC_MASS_MIN, ETAC_MASS_MAX)),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 '
                                  '&& userFloat("fitted_mass") > %.2f && userFloat("fitted_mass") < %.2f'
                                  % (ETAC_MASS_MIN, ETAC_MASS_MAX)),
)

########################### Table ###########################
EtaCTo4MuTable = UpsilonTo4MuTable.clone(
    src  = cms.InputTag("EtaCTo4Mu", "Selected4Leptons"),
    name = cms.string("EtaCTo4Mu"),
    doc  = cms.string("charmonium-region 4-muon candidates (2.80-3.90 GeV): eta_c(1S), "
                      "J/psi (control), chi_c, eta_c(2S), psi(2S)"),
)

########################### MC matching ###########################
# 441 = eta_c(1S), 100441 = eta_c(2S); 443 = J/psi, 100443 = psi(2S) kept so the control
# peak is matchable too. mcStatus 2 follows the Upsilon config.
EtaCTo4MuBPHMCMatch = cms.EDProducer("MCMatcher",
    src         = EtaCTo4MuTable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(441, 100441, 443, 100443),
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.05),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

EtaCTo4MuBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects   = EtaCTo4MuTable.src,
    genParts      = cms.InputTag("finalGenParticlesBPH"),
    mcMap         = cms.InputTag("EtaCTo4MuBPHMCMatch"),
    objName       = EtaCTo4MuTable.name,
    objType       = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("EtaCTo4Mu"),
    docString     = cms.string("MC matching to eta_c / J/psi / psi(2S) -> 4mu"),
)

########################### Count filter (skim) ###########################
CountEtaCTo4Mu = cms.EDFilter("CandViewCountFilter",
    src=cms.InputTag("EtaCTo4Mu", "Selected4Leptons"), minNumber=cms.uint32(1))

########################### Sequences ###########################
EtaCTo4MuSequence   = cms.Sequence(EtaCTo4Mu)
EtaCTo4MuTables     = cms.Sequence(EtaCTo4MuTable)
EtaCTo4MuMCSequence = cms.Sequence(EtaCTo4Mu + EtaCTo4MuBPHMCMatch)
EtaCTo4MuMCTables   = cms.Sequence(EtaCTo4MuTable + EtaCTo4MuBPHMCTable)
