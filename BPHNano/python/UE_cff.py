import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

# Configuration for Underlying Event studies
# Following FSQ-15-007 analysis for underlying event measurement at 13 TeV

# Track selection for UE studies
# We want all charged particles for UE measurements
tracksUE = cms.EDProducer(
    "TrackMerger",
    beamSpot        = cms.InputTag("offlineBeamSpot"),
    tracks          = cms.InputTag("packedPFCandidates"),
    lostTracks      = cms.InputTag("lostTracks"),
    trackSelection  = cms.string("pt>0.5 && abs(eta)<2.5"),  # Standard UE cuts
    muons           = cms.InputTag("slimmedMuons"),
    electrons       = cms.InputTag("slimmedElectrons"),
    maxDzDilep      = cms.double(-1.0),
    dcaSig          = cms.double(-100000),
)

trackUETable = cms.EDProducer(
    "SimpleCompositeCandidateFlatTableProducer",
    src  = cms.InputTag("tracksUE:SelectedTracks"),
    cut  = cms.string(""),
    name = cms.string("Track"),
    doc  = cms.string("charged particle tracks for UE studies"),
    singleton = cms.bool(False),
    extension = cms.bool(False), 
    variables = cms.PSet(
        CandVars,
        vx = Var("vx()", float, doc="x coordinate of vtx position [cm]"),
        vy = Var("vy()", float, doc="y coordinate of vtx position [cm]"),
        vz = Var("vz()", float, doc="z coordinate of vtx position [cm]"),
        # User variables defined in plugins/TrackMerger.cc
        isPacked  = Var("userInt('isPacked')", bool, doc="track from packedCandidate collection"),
        isLostTrk = Var("userInt('isLostTrk')", bool, doc="track from lostTrack collection"),
        dz      = Var("userFloat('dz')", float, doc="dz signed wrt first PV [cm]"),
        dxy     = Var("userFloat('dxy')", float, doc="dxy (with sign) wrt first PV [cm]"),
        dzS     = Var("userFloat('dzS')", float, doc="dz/err (with sign) wrt first PV [cm]"),
        dxyS    = Var("userFloat('dxyS')", float, doc="dxy/err (with sign) wrt first PV [cm]"),
        DCASig  = Var("userFloat('DCASig')", float, doc="significance of xy-distance of closest approach wrt beamspot"),
        isMatchedToMuon = Var("userInt('isMatchedToMuon')", bool, doc="track was used to build a muon"),
        isMatchedToEle  = Var("userInt('isMatchedToEle')", bool, doc="track was used to build a PF ele"),
        nValidHits      = Var("userInt('nValidHits')", int, doc="Number of valid hits"),
        ptErr      = Var("userFloat('ptErr')", float, doc="Pt uncertainty"),
        normChi2   = Var("userFloat('normChi2')", float, doc="Track fit chi-squared divided by n.d.o.f."),
        nValidPixelHits = Var("userInt('nValidPixelHits')", float, doc="Number of pixel hits"),
        ),
)

tracksUEMCMatch = cms.EDProducer("MCMatcher",
    src         = trackUETable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(321, 211, 2212, 13, 11),  # kaon, pion, proton, muon, electron
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(1),
    maxDeltaR   = cms.double(0.03),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

tracksUEMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects   = tracksUEMCMatch.src,
    genParts      = cms.InputTag("finalGenParticlesBPH"),
    mcMap         = cms.InputTag("tracksUEMCMatch"),
    objName       = trackUETable.name,
    objType       = trackUETable.name,
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("track"),
    docString     = cms.string("MC matching for UE tracks"),
)

tracksUESequence   = cms.Sequence(tracksUE)
tracksUESequenceMC = cms.Sequence(tracksUE + tracksUEMCMatch)
tracksUETables     = cms.Sequence(trackUETable)
tracksUETablesMC   = cms.Sequence(trackUETable + tracksUEMCTable)
