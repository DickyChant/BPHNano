import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

# Upsilon(1S/2S/3S) -> 4 muons.
# Reuses the EtaTo4MuBuilder (generic 4-lepton + 4-track KinematicVertexFit), only the
# mass window changes (eta 0.45-0.9 -> Upsilon ~8-11.5 GeV) and the MC PDG ids (221/331 -> bottomonia).

UpsilonTo4Mu = cms.EDProducer(
    'EtaTo4MuBuilder',
    muonCollection = cms.InputTag("slimmedMuons"),
    src = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    beamSpot = cms.InputTag("offlineBeamSpot"),   # for l_xy / pointing (prompt requirement)
    # four muons; Upsilon->4mu muons are harder than eta->4mu but keep it inclusive
    lep1Selection = cms.string('pt > 3.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep3Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep4Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    preVtxSelection  = cms.string('charge() == 0 && pt > 2. && (mass > 8.0 && mass < 11.5)'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 '
                                  '&& userFloat("fitted_mass") > 8.0 && userFloat("fitted_mass") < 11.5 '
                                  '&& userFloat("l_xy") < 0.2'),   # PROMPT: Upsilon has ~zero lifetime (loose 2mm, tunable; save l_xy_sig and tighten offline)
)

########################### Tables ###########################
UpsilonTo4MuTable = cms.EDProducer(
    "SimpleCompositeCandidateFlatTableProducer",
    src = cms.InputTag("UpsilonTo4Mu:Selected4Leptons"),
    cut = cms.string(""),
    name = cms.string("UpsilonTo4Mu"),
    doc  = cms.string("Upsilon -> 4 muon candidates"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        fitted_mass     = Var("userFloat('fitted_mass')", float, doc="Fitted four-lepton mass"),
        fitted_eta      = Var("userFloat('fitted_eta')", float, doc="Fitted four-lepton eta"),
        fitted_pt       = Var("userFloat('fitted_pt')", float, doc="Fitted four-lepton pt"),
        fitted_phi      = Var("userFloat('fitted_phi')", float, doc="Fitted four-lepton phi"),
        fitted_rapidity = Var("userFloat('fitted_rapidity')", float, doc="Fitted four-lepton rapidity"),
        fitted_massErr  = Var("userFloat('fitted_massErr')", float, doc="Fitted four-lepton mass error"),
        svprob = Var("userFloat('sv_prob')", float, doc="Vertex fit probability"),
        vtx_x  = Var("userFloat('vtx_x')", float, doc="Vertex position x"),
        vtx_y  = Var("userFloat('vtx_y')", float, doc="Vertex position y"),
        vtx_z  = Var("userFloat('vtx_z')", float, doc="Vertex position z"),
        dca_avg = Var("userFloat('dca_avg')", float, doc="Average DCA between the four tracks"),
        l_xy     = Var("userFloat('l_xy')",     float, doc="Transverse flight distance from beamspot (cm); prompt ~0"),
        l_xy_unc = Var("userFloat('l_xy_unc')", float, doc="Uncertainty on l_xy (cm)"),
        l_xy_sig = Var("userFloat('l_xy_sig')", float, doc="l_xy significance l_xy/unc (prompt cut handle)"),
        cos_theta_2D        = Var("userFloat('cos_theta_2D')",        float, doc="cos pointing angle (pre-fit p4) vs beamspot"),
        fitted_cos_theta_2D = Var("userFloat('fitted_cos_theta_2D')", float, doc="cos pointing angle (fitted p4) vs beamspot"),
        max_mu_dz = Var("userFloat('max_mu_dz')", float, doc="Largest pairwise |dz| among the 4 muons (cm); z-prompt proxy"),
        lep_min_deltaR = Var("userFloat('lep_min_deltaR')", float, doc="Minimum dR between the 4 muons"),
        lep_max_deltaR = Var("userFloat('lep_max_deltaR')", float, doc="Maximum dR between the 4 muons"),
        lep_avg_deltaR = Var("userFloat('lep_avg_deltaR')", float, doc="Average dR between the 4 muons"),
        l1_idx = Var("userInt('l1_idx')", int, doc="Muon index 1"),
        l2_idx = Var("userInt('l2_idx')", int, doc="Muon index 2"),
        l3_idx = Var("userInt('l3_idx')", int, doc="Muon index 3"),
        l4_idx = Var("userInt('l4_idx')", int, doc="Muon index 4"),
        fitted_l1_pt  = Var("userFloat('fitted_l1_pt')",  float, doc="Fitted l1 pT"),
        fitted_l1_eta = Var("userFloat('fitted_l1_eta')", float, doc="Fitted l1 eta"),
        fitted_l1_phi = Var("userFloat('fitted_l1_phi')", float, doc="Fitted l1 phi"),
        fitted_l2_pt  = Var("userFloat('fitted_l2_pt')",  float, doc="Fitted l2 pT"),
        fitted_l2_eta = Var("userFloat('fitted_l2_eta')", float, doc="Fitted l2 eta"),
        fitted_l2_phi = Var("userFloat('fitted_l2_phi')", float, doc="Fitted l2 phi"),
        fitted_l3_pt  = Var("userFloat('fitted_l3_pt')",  float, doc="Fitted l3 pT"),
        fitted_l3_eta = Var("userFloat('fitted_l3_eta')", float, doc="Fitted l3 eta"),
        fitted_l3_phi = Var("userFloat('fitted_l3_phi')", float, doc="Fitted l3 phi"),
        fitted_l4_pt  = Var("userFloat('fitted_l4_pt')",  float, doc="Fitted l4 pT"),
        fitted_l4_eta = Var("userFloat('fitted_l4_eta')", float, doc="Fitted l4 eta"),
        fitted_l4_phi = Var("userFloat('fitted_l4_phi')", float, doc="Fitted l4 phi"),
    )
)

########################### MC Matching ###########################
UpsilonTo4MuBPHMCMatch = cms.EDProducer(
    "MCMatcher",
    src         = UpsilonTo4MuTable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(553, 100553, 200553),   # Upsilon(1S,2S,3S)
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.05),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

UpsilonTo4MuBPHMCTable = cms.EDProducer(
    "CandMCMatchTableProducerBPH",
    recoObjects = UpsilonTo4MuTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("UpsilonTo4MuBPHMCMatch"),
    objName     = UpsilonTo4MuTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("UpsilonTo4Mu"),
    docString   = cms.string("MC matching to status==2 Upsilon(nS) -> 4mu"),
)

########################### Sequences ###########################
UpsilonTo4MuSequence   = cms.Sequence(UpsilonTo4Mu)
UpsilonTo4MuTables     = cms.Sequence(UpsilonTo4MuTable)
UpsilonTo4MuMCSequence = cms.Sequence(UpsilonTo4Mu + UpsilonTo4MuBPHMCMatch)
UpsilonTo4MuMCTables   = cms.Sequence(UpsilonTo4MuTable + UpsilonTo4MuBPHMCTable)
