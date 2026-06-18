import FWCore.ParameterSet.Config as cms

# LowPtElectron "track-like" collection for the Upsilon->2mu2e e+e- legs.
# Mirrors tracksBPH (TrackMerger) but sources the central LowPtElectron collection
# (finalLowPtElectrons) and builds transient tracks from each electron's gsfTrack, so the
# 2mu2e vertex fit uses real soft electrons instead of generic charged tracks. Output
# carries ele_idx -> the LowPtElectron NanoAOD table (no separate track table needed).

lowPtEleTracks = cms.EDProducer(
    "LowPtEleMerger",
    electrons         = cms.InputTag("finalLowPtElectrons"),
    electronSelection = cms.string("pt > 0.5 && abs(eta) < 2.5"),   # soft electrons; builder tightens
)

lowPtEleTracksSequence   = cms.Sequence(lowPtEleTracks)
lowPtEleTracksSequenceMC = cms.Sequence(lowPtEleTracks)
