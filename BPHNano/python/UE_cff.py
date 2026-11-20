import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.genparticles_cff import *

# Configuration for Underlying Event studies
# Following FSQ-15-007-like analysis for underlying event measurement at 13.6 TeV
# This is a standalone configuration without BPH dependencies

# Track selection for UE studies
# We want all charged particles for UE measurements
tracksUE = cms.EDProducer(
    "TrackMerger",
    beamSpot        = cms.InputTag("offlineBeamSpot"),
    tracks          = cms.InputTag("packedPFCandidates"),
    lostTracks      = cms.InputTag("lostTracks"),
    # Slightly looser than the analysis cuts (pt>0.5, |eta|<2.5) to avoid edge migration between
    # PackedCandidate::pt() and bestTrack()->pt(); final cuts applied offline.
    trackSelection  = cms.string("pt>0.4 && abs(eta)<2.6"),
    keepAllCharged  = cms.bool(True),   # keep e/mu/p too (instanton = all charged particles)
    vertices        = cms.InputTag("offlineSlimmedPrimaryVertices"),
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
        nValidPixelHits = Var("userInt('nValidPixelHits')", int, doc="Number of pixel hits"),
        dxyBS      = Var("userFloat('dxyBS')", float, doc="transverse DCA wrt beamspot [cm]"),
        dxyPV0     = Var("userFloat('dxyPV0')", float, doc="dxy of bestTrack wrt PV[0] [cm]"),
        dzPV0      = Var("userFloat('dzPV0')", float, doc="dz of bestTrack wrt PV[0] [cm]"),
        hasPV0     = Var("userInt('hasPV0')", bool, doc="PV[0] existed (else dxyPV0/dzPV0 wrt beamspot)"),
        fromPV     = Var("userInt('fromPV')", "uint8", doc="PackedCandidate::fromPV() wrt PV[0] (0..3)"),
        pvAssocQuality = Var("userInt('pvAssocQuality')", "uint8", doc="PackedCandidate::pvAssociationQuality()"),
        highPurity = Var("userInt('highPurity')", bool, doc="track is highPurity"),
        ),
)

tracksUEMCMatch = cms.EDProducer("MCMatcher",
    src         = trackUETable.src,
    matched     = cms.InputTag("finalGenParticles"),
    mcPdgId     = cms.vint32(321, 211, 2212, 13, 11),  # kaon, pion, proton, muon, electron
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(1),
    maxDeltaR   = cms.double(0.03),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

tracksUEMCTable = cms.EDProducer("CandMCMatchTableProducer",
    recoObjects   = tracksUEMCMatch.src,
    genParts      = cms.InputTag("finalGenParticles"),
    mcMap         = cms.InputTag("tracksUEMCMatch"),
    objName       = trackUETable.name,
    objType       = trackUETable.name,
    branchName    = cms.string("genPart"),
    docString     = cms.string("MC matching for UE tracks"),
)

tracksUESequence   = cms.Sequence(tracksUE)
tracksUESequenceMC = cms.Sequence(finalGenParticles + tracksUE + tracksUEMCMatch)
tracksUETables     = cms.Sequence(trackUETable)
tracksUETablesMC   = cms.Sequence(trackUETable + tracksUEMCTable)

# Gen particle table for UE studies (use standard genParticleTable)
genParticleUETable = genParticleTable.clone(
    src = cms.InputTag("finalGenParticles")
)

genParticleUESequence = cms.Sequence(finalGenParticles)
genParticleUETables = cms.Sequence(genParticleUETable)

# Particle-level truth for UE/instanton: all stable charged particles from packedGenParticles
# (prunedGenParticles/finalGenParticles drops soft stable charged hadrons).
packedGenChargedUETable = cms.EDProducer(
    "SimpleCandidateFlatTableProducer",
    src  = cms.InputTag("packedGenParticles"),
    cut  = cms.string("status == 1 && charge != 0 && pt > 0.4 && abs(eta) < 2.6"),
    name = cms.string("GenCharged"),
    doc  = cms.string("stable charged gen particles (packedGenParticles) for UE/instanton truth"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        pt     = Var("pt", float, precision=12),
        eta    = Var("eta", float, precision=12),
        phi    = Var("phi", float, precision=12),
        charge = Var("charge", int),
        pdgId  = Var("pdgId", int),
    ),
)
packedGenChargedUETables = cms.Sequence(packedGenChargedUETable)
