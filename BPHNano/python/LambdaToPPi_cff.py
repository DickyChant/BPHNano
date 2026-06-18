import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

LambdaToPPi = cms.EDProducer(
    'DiTrackBuilder',
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    trk1Selection   = cms.string('pt > 0.5 && abs(eta) < 2.4 '),
    trk2Selection   = cms.string('pt > 0.5 && abs(eta) < 2.4 '),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    trk1Mass = cms.double(0.938),
    trk2Mass = cms.double(0.139),
    preVtxSelection = cms.string('abs(userCand("trk1").vz - userCand("trk2").vz) <= 1.0 '
                                 '&& mass() > 1.025 && mass() < 1.205 && pt() > 5'
                                 '&& charge() == 0'),
    postVtxSelection =  cms.string('userFloat("fitted_mass") > 1.11 && userFloat("fitted_mass") < 1.12'
                                   '&& userFloat("fitted_pt") > 5'
                                   '&& userFloat("sv_prob") > 0.01' # no apparent gain
                                   '&& abs(userFloat("fitted_cos_theta_2D"))>0.995' # 99% eff.
                                   '&& abs(userFloat("l_xy")) > 3*abs(userFloat("l_xy_unc")) && abs(userFloat("l_xy_unc"))>0')
)

CountLambdaPPi = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("LambdaToPPi")
)  

LambdaToPPiTable = cms.EDProducer("SimpleCompositeCandidateFlatTableProducer",
    src  = cms.InputTag("LambdaToPPi",'SelectedLambdaCollection'),
    cut  = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("LambdaToPPi"),
    doc  = cms.string("slimmedMuons for BPark after basic selection"),
    singleton = cms.bool(False), # the number of entries is variable
    extension = cms.bool(False), # this is the main table for the muons
    variables = cms.PSet(
        CandVars,
        fitted_mass = Var("userFloat('fitted_mass')", float, doc=""),
        fitted_pt   = Var("userFloat('fitted_pt')", float, doc=""),
        fitted_eta  = Var("userFloat('fitted_eta')", float, doc=""),
        fitted_phi  = Var("userFloat('fitted_phi')", float, doc=""),
        trk_deltaR      = Var("userFloat('trk_deltaR')", float, doc=""),
        cos_theta_2D      = Var("userFloat('cos_theta_2D')", float, doc=""),
        fitted_cos_theta_2D      = Var("userFloat('fitted_cos_theta_2D')", float, doc=""),
        l_xy      = Var("userFloat('l_xy')", float, doc=""),
        l_xy_unc      = Var("userFloat('l_xy_unc')", float, doc=""),
        svchi2      = Var("userFloat('sv_chi2')", float, doc=""),
        svprob      = Var("userFloat('sv_prob')", float, doc=""),
        trk1_mass   = Var("userFloat('trk1_mass')", float, doc=""),
        trk2_mass   = Var("userFloat('trk2_mass')", float, doc=""),
        trk1_charge   = Var("userFloat('trk1_charge')", float, doc=""),
        trk2_charge   = Var("userFloat('trk2_charge')", float, doc=""),
        trk1_idx    = Var("userInt('trk1_idx')", int, doc=""),
        trk2_idx    = Var("userInt('trk2_idx')", int, doc=""),
        vtx_x       = Var("userFloat('vtx_x')", float, doc=""),
        vtx_y       = Var("userFloat('vtx_y')", float, doc=""),
        vtx_z       = Var("userFloat('vtx_z')", float, doc=""),               
        dca = Var("userFloat('dca')", float, doc="the distance between the two trajectories at their closest approach in R-phi"),
    )
)


LambdaToPPiBPHMCMatch = cms.EDProducer("MCMatcher",                  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = LambdaToPPiTable.src,                           # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(3122),                             # one or more PDG ID (443 = J/psi); absolute values (see below)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(2),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                           # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)

LambdaToPPiBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = LambdaToPPiTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("LambdaToPPiBPHMCMatch"),
    objName     = LambdaToPPiTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("LambdaToPPi"),
    docString   = cms.string("MC matching to status==2 Lambda0"),
)


LambdaPPiSequence = cms.Sequence(LambdaToPPi)
LambdaPPiTables   = cms.Sequence(LambdaToPPiTable)
LambdaPPiSequenceMC = cms.Sequence(LambdaToPPi+LambdaToPPiBPHMCMatch)
LambdaPPiTablesMC   = cms.Sequence(LambdaToPPiTable+LambdaToPPiBPHMCTable)

