import FWCore.ParameterSet.Config as cms

# LowPtElectron "track-like" collection for the Upsilon->2mu2e e+e- legs.
# Mirrors tracksBPH (TrackMerger) but sources the central LowPtElectron collection
# (finalLowPtElectrons) and builds transient tracks from each electron's gsfTrack, so the
# 2mu2e vertex fit uses real soft electrons instead of generic charged tracks. Output
# carries ele_idx -> the LowPtElectron NanoAOD table (no separate track table needed).

lowPtEleTracks = cms.EDProducer(
    "LowPtEleMerger",
    electrons         = cms.InputTag("finalLowPtElectrons"),
    electrons2        = cms.InputTag(""),          # optional 2nd source; empty = unused
    # per-electron conversion match (the NanoAOD convVtxRadius branch is event-level and
    # therefore useless for deciding WHICH leg converted)
    conversions       = cms.InputTag("reducedEgamma", "reducedConversions"),
    electronSelection = cms.string("pt > 0.5 && abs(eta) < 2.5"),   # soft electrons; builder tightens
    # NOMINAL per-leg object choice: standard electron at/above this pT, LowPtElectron below.
    nominalPtThreshold = cms.double(10.0),
    # kinematic overlap removal between the two collections (gsfTrack refs cannot be compared:
    # different products) -- see LowPtEleMerger
    overlapDeltaR = cms.double(0.02),
    overlapRelPt  = cms.double(0.5),
)

# The two electron collections are COMPLEMENTARY in pT, not redundant: finalElectrons cuts at
# pt > 5 GeV while LowPtElectron covers roughly 1-5 GeV. Merging them into ONE collection holding both electron sources, so a single vertex fit yields all three
# lets a single vertex fit produce all three pairings -- both soft, MIXED (one hard + one
# soft, which is where a real eta' often lands), and both standard -- instead of only the two
# same-source ones that separate collections could give. Duplicates are removed inside the
# merger by gsfTrack, with the standard electron winning.
etapEleTracks = lowPtEleTracks.clone(
    electrons         = cms.InputTag("finalLowPtElectrons"),   # ele_src = 0
    # slimmedElectrons, NOT finalElectrons: the NanoAOD Electron table needs
    # slimmedElectronsWithUserData -> updatedJetsPuppi -> the whole jet sequence, which is far
    # too heavy here and only supplies jet-based isolation we do not use. Reading MiniAOD
    # directly keeps the producer slim; the leg's quality variables are stamped by the merger.
    electrons2        = cms.InputTag("slimmedElectrons"),      # ele_src = 1
    electronSelection = cms.string("pt > 0.5 && abs(eta) < 2.5"),
)

lowPtEleTracksSequence   = cms.Sequence(lowPtEleTracks)
lowPtEleTracksSequenceMC = cms.Sequence(lowPtEleTracks)
etapEleTracksSequence    = cms.Sequence(etapEleTracks)
etapEleTracksSequenceMC  = cms.Sequence(etapEleTracks)
