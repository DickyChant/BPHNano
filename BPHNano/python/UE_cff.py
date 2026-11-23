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

# BPHNano's own MC-match table producer (as for the other BPHNano MC tables): NanoAOD's
# CandMCMatchTableProducer changed its interface in 16_0_X (requires "src").
tracksUEMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects   = tracksUEMCMatch.src,
    genParts      = cms.InputTag("finalGenParticles"),
    mcMap         = cms.InputTag("tracksUEMCMatch"),
    objName       = trackUETable.name,
    objType       = trackUETable.name,
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("track"),
    docString     = cms.string("MC matching for UE tracks"),
)

tracksUESequence   = cms.Sequence(tracksUE)
tracksUESequenceMC = cms.Sequence(finalGenParticles + tracksUE + tracksUEMCMatch)
tracksUETables     = cms.Sequence(trackUETable)
tracksUETablesMC   = cms.Sequence(trackUETable + tracksUEMCTable)

# Gen particle table for UE studies (use standard genParticleTable)
genParticleUETable = genParticleTable.clone(
    src = cms.InputTag("finalGenParticles"),
    externalVariables = cms.PSet(),  # drop NanoAOD's lepton 'iso' (needs genIso); not used for UE
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

# Minimum-bias trigger emulation. The 2026 special low-PU runs recorded only ZeroBias; the L1_MinimumBiasHF* seeds
# are in the menu with prescale 0 (final rate 0), but their uGT initial decisions are evaluated for every event.
# L1i_*: initial decisions (L1InitialBitsTableProducer); HF_*: per-side HF PF-candidate summary (HFSummaryTableProducer).
l1InitialUETable = cms.EDProducer(
    "L1InitialBitsTableProducer",
    src   = cms.InputTag("gtStage2Digis"),
    name  = cms.string("L1i"),
    seeds = cms.vstring("L1_MinimumBiasHF0_AND_BptxAND", "L1_MinimumBiasHF0", "L1_MinimumBiasHF1_AND_BptxAND",
                        "L1_MinimumBiasHF1_OR_BptxAND", "L1_MinimumBiasHF2_AND_BptxAND", "L1_MinimumBiasHF2_OR_BptxAND",
                        "L1_ZeroBias", "L1_SingleJet8_BptxAND", "L1_IsolatedBunch", "L1_FirstCollisionInOrbit"),
)
hfSummaryUETable = cms.EDProducer(
    "HFSummaryTableProducer",
    src        = cms.InputTag("packedPFCandidates"),
    name       = cms.string("HF"),
    thresholds = cms.vdouble(3., 5., 10., 20.),
)
mbTrigUETables = cms.Sequence(l1InitialUETable + hfSummaryUETable)

# MC only: generator process code (Pythia 8 SoftQCD: 101 ND, 103/104 SD, 105 DD, 106 CD).
genProcUETable = cms.EDProducer(
    "SimpleGenEventFlatTableProducer",
    src  = cms.InputTag("generator"),
    name = cms.string("GenProc"),
    doc  = cms.string("generator process code"),
    extension = cms.bool(False),
    variables = cms.PSet(
        id = Var("signalProcessID", int, doc="GenEventInfoProduct::signalProcessID"),
    ),
)
