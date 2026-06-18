import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

########################### Selections ###########################

EtaMuMu = cms.EDProducer(
    'DiMuonBuilder',
    src = cms.InputTag('muonBPH', 'AllMuons'),
    transientTracksSrc = cms.InputTag('muonBPH', 'AllTransientMuons'),
    #src = cms.InputTag('muonBPH', 'SelectedMuons'),
    #transientTracksSrc = cms.InputTag('muonBPH', 'SelectedTransientMuons'),
    lep1Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon '),
    lep2Selection = cms.string('pt > 2 && abs(eta) < 2.4 && isLooseMuon && isTrackerMuon '),
    preVtxSelection  = cms.string('charge() == 0'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0')
)

CountEtaDiMuonBPH = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("EtaMuMu:SelectedDiLeptons")
)  

########################### Tables ###########################

EtaMuMuTable = cms.EDProducer("SimpleCompositeCandidateFlatTableProducer",
    src = cms.InputTag("EtaMuMu:SelectedDiLeptons"),
    cut = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("EtaMuMu"),
    doc  = cms.string("Dilepton collections"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), # this is the main table for the muons
    variables = cms.PSet(CandVars,
          fitted_mass     = Var("userFloat('fitted_mass')", float, doc="Fitted dilepton mass"),
          fitted_massErr  = Var("userFloat('fitted_massErr')", float, doc="Fitted dilepton massErr"),
          fitted_pt       = Var("userFloat('fitted_pt')",      float, doc="Fitted dilepton pT"),
          fitted_eta      = Var("userFloat('fitted_eta')",     float, doc="Fitted dilepton eta"),
          fitted_phi      = Var("userFloat('fitted_phi')",     float, doc="Fitted dilepton phi"),
          fitted_rapidity = Var("userFloat('fitted_rapidity')",float, doc="Fitted dilepton rapidity"),
          svprob = Var("userFloat('sv_prob')", float, doc="Vtx fit probability"),
          vtx_x =Var("userFloat('vtx_x')", float, doc="Vtx position in x"),
          vtx_y = Var("userFloat('vtx_y')", float, doc="Vtx position in y"),
          vtx_z = Var("userFloat('vtx_z')", float, doc="Vtx position in z"),
          dca = Var("userFloat('dca')", float, doc="the distance between the two trajectories at their closest approach in R-phi"),
          lep_deltaR = Var("userFloat('lep_deltaR')", float, doc="lep_deltaR"),
          l1_idx = Var("userInt('l1_idx')", int, doc="l1_idx"),
          l2_idx = Var("userInt('l2_idx')", int, doc="l2_idx"),
    )
)


EtaMuMuBPHMCMatch = cms.EDProducer("MCMatcher",                  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = EtaMuMuTable.src,                           # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(221, 331),                       # eta or eta'
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(22),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                           # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)

EtaMuMuBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = EtaMuMuTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("EtaMuMuBPHMCMatch"),
    objName     = EtaMuMuTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("EtaMuMu"),
    docString   = cms.string("MC matching to status==2 "),
)

EtaMuMuSequence = cms.Sequence(EtaMuMu)
EtaMuMuTables = cms.Sequence(EtaMuMuTable)
EtaMuMuMCSequence = cms.Sequence(EtaMuMu+EtaMuMuBPHMCMatch)
EtaMuMuMCTables = cms.Sequence(EtaMuMuTable+EtaMuMuBPHMCTable)
