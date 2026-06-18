import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

DiHs = cms.EDProducer(
    'DiTrackBuilder',
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    trk1Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5 '),
    trk2Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5 '),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    trk1Mass = cms.double(0.493677), # K mass
    trk2Mass = cms.double(0.493677),

    preVtxSelection = cms.string('abs(userCand("trk1").vz - userCand("trk2").vz) <= 0.5 '
                                 '&& 0 < mass() && mass() < 6.0 '
                                 '&& charge() == 0'),
    postVtxSelection =  cms.string(' 0 < userFloat("fitted_mass") && userFloat("fitted_mass") < 6.0'
                                 '&& userFloat("sv_prob") > 0.01')
)

CountDiHs = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("DiHs")
)  

DiHsTable = cms.EDProducer("SimpleCompositeCandidateFlatTableProducer",
    src  = cms.InputTag("DiHs",'SelectedLambdaCollection'),
    cut  = cms.string(""), #we should not filter on cross linked collections
    name = cms.string("DiHs"),
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
        trk1_idx    = Var("userInt('trk1_idx')", int, doc=""),
        trk2_idx    = Var("userInt('trk2_idx')", int, doc=""),
        second_mass_hypothesis = Var("userInt('second_mass_hypothesis')", int, doc=""),
        vtx_x       = Var("userFloat('vtx_x')", float, doc=""),
        vtx_y       = Var("userFloat('vtx_y')", float, doc=""),
        vtx_z       = Var("userFloat('vtx_z')", float, doc=""),               
        dca = Var("userFloat('dca')", float, doc="the distance between the two trajectories at their closest approach in R-phi"),
    )
)

DiHsSequence = cms.Sequence(DiHs)
DiHsTables   = cms.Sequence(DiHsTable)
