import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

########################### Selections ###########################
EtaTo4Mu = cms.EDProducer(
    'EtaTo4MuBuilder',
    muonCollection = cms.InputTag("slimmedMuons"), #same collection as in NanoAOD
    src = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    #lep1Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon && isGlobalMuon'),
    #lep2Selection = cms.string('pt > 1.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    #lep3Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon && isGlobalMuon'),
    #lep4Selection = cms.string('pt > 1.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep1Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep2Selection = cms.string('pt > 2.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep3Selection = cms.string('pt > 1.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    lep4Selection = cms.string('pt > 1.0 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon'),
    preVtxSelection  = cms.string('pt > 5. && charge() == 0  && (mass > 0.45 && mass < 0.9)'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 && userFloat("fitted_mass") > 0.45 && userFloat("fitted_mass") < 0.9'),
)

CountEtaTo4MuonBPH = cms.EDFilter(
    "PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("EtaTo4Mu:Selected4Leptons")
)

########################### Tables ###########################
EtaTo4MuTable = cms.EDProducer(
    "SimpleCompositeCandidateFlatTableProducer",
    src = cms.InputTag("EtaTo4Mu:Selected4Leptons"),
    cut = cms.string(""),
    name = cms.string("EtaTo4Mu"),
    doc  = cms.string("Four-muon collections"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        fitted_mass = Var("userFloat('fitted_mass')", float, doc="Fitted four-lepton mass"),
        fitted_eta = Var("userFloat('fitted_eta')", float, doc="Fitted four-lepton eta"),
        fitted_pt = Var("userFloat('fitted_pt')", float, doc="Fitted four-lepton pt"),
        fitted_phi = Var("userFloat('fitted_phi')", float, doc="Fitted four-lepton phi"),
        fitted_rapidity   = Var("userFloat('fitted_rapidity')", float, doc="Fitted four-lepton rapidity"),
        fitted_massErr = Var("userFloat('fitted_massErr')", float, doc="Fitted four-lepton mass error"),
        svprob = Var("userFloat('sv_prob')", float, doc="Vertex fit probability"),
        vtx_x = Var("userFloat('vtx_x')", float, doc="Vertex position x"),
        vtx_y = Var("userFloat('vtx_y')", float, doc="Vertex position y"),
        vtx_z = Var("userFloat('vtx_z')", float, doc="Vertex position z"),
        dca_avg = Var("userFloat('dca_avg')", float, doc="Average DCA between lepton tracks"),

        lep_min_deltaR = Var("userFloat('lep_min_deltaR')", float, doc="Minimum ΔR between the 4 muons"),
        lep_max_deltaR = Var("userFloat('lep_max_deltaR')", float, doc="Maximum ΔR between the 4 muons"),
        lep_avg_deltaR = Var("userFloat('lep_avg_deltaR')", float, doc="Average ΔR between the 4 muons"),

        l1_idx = Var("userInt('l1_idx')", int, doc="Index of lepton 1"),
        l2_idx = Var("userInt('l2_idx')", int, doc="Index of lepton 2"),
        l3_idx = Var("userInt('l3_idx')", int, doc="Index of lepton 3"),
        l4_idx = Var("userInt('l4_idx')", int, doc="Index of lepton 4"),
        fitted_l1_pt       = Var("userFloat('fitted_l1_pt')",      float, doc="Fitted l1 pT"),
        fitted_l1_eta      = Var("userFloat('fitted_l1_eta')",     float, doc="Fitted l1 eta"),
        fitted_l1_phi      = Var("userFloat('fitted_l1_phi')",     float, doc="Fitted l1 phi"),
        fitted_l2_pt       = Var("userFloat('fitted_l2_pt')",      float, doc="Fitted l2 pT"),
        fitted_l2_eta      = Var("userFloat('fitted_l2_eta')",     float, doc="Fitted l2 eta"),
        fitted_l2_phi      = Var("userFloat('fitted_l2_phi')",     float, doc="Fitted l2 phi"),
        fitted_l3_pt       = Var("userFloat('fitted_l3_pt')",      float, doc="Fitted l3 pT"),
        fitted_l3_eta      = Var("userFloat('fitted_l3_eta')",     float, doc="Fitted l3 eta"),
        fitted_l3_phi      = Var("userFloat('fitted_l3_phi')",     float, doc="Fitted l3 phi"),
        fitted_l4_pt       = Var("userFloat('fitted_l4_pt')",      float, doc="Fitted l4 pT"),
        fitted_l4_eta      = Var("userFloat('fitted_l4_eta')",     float, doc="Fitted l4 eta"),
        fitted_l4_phi      = Var("userFloat('fitted_l4_phi')",     float, doc="Fitted l4 phi"),
    )
)

########################### MC Matching ###########################

EtaTo4MuBPHMCMatch = cms.EDProducer(
    "MCMatcher",
    src         = EtaTo4MuTable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(221, 331),
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.05),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

EtaTo4MuBPHMCTable = cms.EDProducer(
    "CandMCMatchTableProducerBPH",
    recoObjects = EtaTo4MuTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("EtaTo4MuBPHMCMatch"),
    objName     = EtaTo4MuTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("EtaTo4Mu"),
    docString   = cms.string("MC matching to status==2 4-muon resonance"),
)

########################### Sequences ###########################

EtaTo4MuSequence = cms.Sequence(EtaTo4Mu)
EtaTo4MuTables = cms.Sequence(EtaTo4MuTable)
EtaTo4MuMCSequence = cms.Sequence(EtaTo4Mu + EtaTo4MuBPHMCMatch)
EtaTo4MuMCTables = cms.Sequence(EtaTo4MuTable + EtaTo4MuBPHMCTable)

