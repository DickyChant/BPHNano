import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *


# Used to study lambdaB -> lambda0(->\p\pi) + 2h
BtoD0Kstar = cms.EDProducer("BtoD0KstarProducer",    
   # which beamSpot to reference
   beamSpot        = cms.InputTag('offlineBeamSpot'),
   vertices        = cms.InputTag('offlineSlimmedPrimaryVertices'),
   tracks          = cms.InputTag("packedPFCandidates"),
   lostTracks      = cms.InputTag("lostTracks"),
   # all Tracks
   tkNHitsCut      = cms.int32(3),    # Number of valid hits on track
   minTrackPt      = cms.double(1.0),
   maxTrackEta     = cms.double(2.5), # Eta of track
   tkChi2Cut       = cms.double(10.), # Track normalized Chi2
   tkIPSigXYCut    = cms.double(0.2),
   # Ks0
   Ks0_dcacut            = cms.double(0.2),
   Ks0_TrkDcaSigXYCut    = cms.double(0.5),
   ks0_vtxChi2Cut        = cms.double(-1),
   ks0_vtxDecaySigXYCut  = cms.double(0.5),
   ks0_vtxDecaySigXYZCut = cms.double(-1),
   ks0_cosThetaXYCut     = cms.double(0.9995),
   ks0_cosThetaXYZCut    = cms.double(0.9999),
   Ks0_l_xyzSigCut       = cms.double(3),
   # D0
   D0_trkPtCut          = cms.double(0.5),   # Pt cut of track 3, 4
   D0_trkdca            = cms.double(0.2),
   D0_TrkDcaSigXYCut    = cms.double(0.2),
   D0_PtCut             = cms.double(2),
   D0_vtxDecaySigXYCut  = cms.double(0.5),
   # B
   B_PtCut         = cms.double(-1),
   # mass window
   KS0_MASS_window  = cms.double(0.02), # fitted sigma 0.00426
   KSTAR_MASS_window= cms.double(0.09),  # fitted sigma 0.0171
   D0_MASS_window   = cms.double(0.07), # fitted sigma 0.0143
   BPLUS_MASS_window= cms.double(0.4),  # fitted sigma 0.03585 
   verbose         = cms.int32(0)
)

D0Table = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("BtoD0Kstar", "D0"),
    cut       = cms.string(""),
    name      = cms.string("D0"),
    doc       = cms.string("D0 Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        dca                = ufloat('dca'),
        dot_product        = ufloat('dot_product'),
        trk1_dcasig        = ufloat('trk1_dcasig'),
        trk2_dcasig        = ufloat('trk2_dcasig'),
        pv_alpha2D         = ufloat('pv_alpha2D'),
        pv_alpha3D         = ufloat('pv_alpha3D'),
        MC_pv_alpha2D      = ufloat('MC_pv_alpha2D'),
        MC_pv_alpha3D      = ufloat('MC_pv_alpha3D'),
        massErr            = ufloat('massErr'),
        chi2               = ufloat('chi2'),
        ndof               = ufloat('ndof'),
        prob               = ufloat('prob'),
        vx                 = ufloat('vx'),
        vy                 = ufloat('vy'),
        vz                 = ufloat('vz'),
        lxy                = ufloat('lxy'),
        lxySig             = ufloat('lxySig'),
        lxyz               = ufloat('lxyz'),
        lxyzSig            = ufloat('lxyzSig'),
        MC_pt                 = ufloat('MC_pt'),
        MC_eta                = ufloat('MC_eta'),
        MC_phi                = ufloat('MC_phi'),
        MC_mass               = ufloat('MC_mass'),
        MC_massErr            = ufloat('MC_massErr'),
        MC_chi2               = ufloat('MC_chi2'),
        MC_ndof               = ufloat('MC_ndof'),
        MC_prob               = ufloat('MC_prob'),
        MC_vx                 = ufloat('MC_vx'),
        MC_vy                 = ufloat('MC_vy'),
        MC_vz                 = ufloat('MC_vz'),
        MC_lxy                = ufloat('MC_lxy'),
        MC_lxySig             = ufloat('MC_lxySig'),
        MC_lxyz               = ufloat('MC_lxyz'),
        MC_lxyzSig            = ufloat('MC_lxyzSig'),
        raw_pt                 = ufloat('raw_pt'),
        raw_eta                = ufloat('raw_eta'),
        raw_phi                = ufloat('raw_phi'),
        raw_mass               = ufloat('raw_mass'),
        raw_d1_pt                 = ufloat('raw_d1_pt'),
        raw_d1_eta                = ufloat('raw_d1_eta'),
        raw_d1_phi                = ufloat('raw_d1_phi'),
        raw_d1_mass               = ufloat('raw_d1_mass'),
        raw_d2_pt                 = ufloat('raw_d2_pt'),
        raw_d2_eta                = ufloat('raw_d2_eta'),
        raw_d2_phi                = ufloat('raw_d2_phi'),
        raw_d2_mass               = ufloat('raw_d2_mass'),
        raw_d1_numberOfValidHits  = ufloat('raw_d1_numberOfValidHits'),
        raw_d1_normalizedChi2     = ufloat('raw_d1_normalizedChi2'),
        raw_d1_dxy_pv             = ufloat('raw_d1_dxy_pv'),
        raw_d2_numberOfValidHits  = ufloat('raw_d2_numberOfValidHits'),
        raw_d2_normalizedChi2     = ufloat('raw_d2_normalizedChi2'),
        raw_d2_dxy_pv             = ufloat('raw_d2_dxy_pv'),
        hyp_m1_idx = uint('hyp_m1_idx'),
        hyp_m2_idx = uint('hyp_m2_idx'),
        )
)
D0MCMatch = cms.EDProducer("MCMatcher",            # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = D0Table.src,                      # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(421),                            # one or more PDG ID (13 = mu); absolute values (see below)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(2),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                            # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)
D0MCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = D0Table.src,
    genParts = cms.InputTag("finalGenParticlesBPH"),
    mcMap = cms.InputTag("D0MCMatch"),
    objName = D0Table.name,
    objType = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("D0"),
    docString = cms.string("MC matching to status==2 D0"),
)

KstarTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("BtoD0Kstar", "Kstar"),
    cut       = cms.string(""),
    name      = cms.string("Kstar"),
    doc       = cms.string("Kstar Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        ks0_dca = ufloat('ks0_dca'),
        ks0_dot_product = ufloat('ks0_dot_product'),
        ks0_trk1_dcasig = ufloat('ks0_trk1_dcasig'),
        ks0_trk2_dcasig = ufloat('ks0_trk2_dcasig'),
        ks0_Kin_kstar_l_xySig = ufloat('ks0_Kin_kstar_l_xySig'),
        ks0_Kin_kstar_l_xyzSig = ufloat('ks0_Kin_kstar_l_xyzSig'),
        Ks0_pv_alpha2D         = ufloat('Ks0_pv_alpha2D'),
        Ks0_pv_alpha3D         = ufloat('Ks0_pv_alpha3D'),
        Ks0_MC_pv_alpha2D      = ufloat('Ks0_MC_pv_alpha2D'),
        Ks0_MC_pv_alpha3D      = ufloat('Ks0_MC_pv_alpha3D'),
        ks0_pt                 = ufloat('ks0_pt'),
        ks0_eta                = ufloat('ks0_eta'),
        ks0_phi                = ufloat('ks0_phi'),
        ks0_mass               = ufloat('ks0_mass'),
        ks0_massErr            = ufloat('ks0_massErr'),
        ks0_chi2               = ufloat('ks0_chi2'),
        ks0_ndof               = ufloat('ks0_ndof'),
        ks0_prob               = ufloat('ks0_prob'),
        ks0_vx                 = ufloat('ks0_vx'),
        ks0_vy                 = ufloat('ks0_vy'),
        ks0_vz                 = ufloat('ks0_vz'),
        ks0_lxy                = ufloat('ks0_lxy'),
        ks0_lxySig             = ufloat('ks0_lxySig'),
        ks0_lxyz               = ufloat('ks0_lxyz'),
        ks0_lxyzSig            = ufloat('ks0_lxyzSig'),
        ks0_MC_pt                 = ufloat('ks0_MC_pt'),
        ks0_MC_eta                = ufloat('ks0_MC_eta'),
        ks0_MC_phi                = ufloat('ks0_MC_phi'),
        ks0_MC_mass               = ufloat('ks0_MC_mass'),
        ks0_MC_massErr            = ufloat('ks0_MC_massErr'),
        ks0_MC_chi2               = ufloat('ks0_MC_chi2'),
        ks0_MC_ndof               = ufloat('ks0_MC_ndof'),
        ks0_MC_prob               = ufloat('ks0_MC_prob'),
        ks0_MC_vx                 = ufloat('ks0_MC_vx'),
        ks0_MC_vy                 = ufloat('ks0_MC_vy'),
        ks0_MC_vz                 = ufloat('ks0_MC_vz'),
        ks0_MC_lxy                = ufloat('ks0_MC_lxy'),
        ks0_MC_lxySig             = ufloat('ks0_MC_lxySig'),
        ks0_MC_lxyz               = ufloat('ks0_MC_lxyz'),
        ks0_MC_lxyzSig            = ufloat('ks0_MC_lxyzSig'),
        ks0_raw_pt                 = ufloat('ks0_raw_pt'),
        ks0_raw_eta                = ufloat('ks0_raw_eta'),
        ks0_raw_phi                = ufloat('ks0_raw_phi'),
        ks0_raw_mass               = ufloat('ks0_raw_mass'),
        ks0_trk1_idx = uint('ks0_trk1_idx'),    
        ks0_trk2_idx = uint('ks0_trk2_idx'),
        bachelor_idx = uint('bachelor_idx'),
        massErr            = ufloat('massErr'),
        chi2               = ufloat('chi2'),
        ndof               = ufloat('ndof'),
        prob               = ufloat('prob'),
        vx                 = ufloat('vx'),
        vy                 = ufloat('vy'),
        vz                 = ufloat('vz'),
        lxy                = ufloat('lxy'),
        lxySig             = ufloat('lxySig'),
        lxyz               = ufloat('lxyz'),
        lxyzSig            = ufloat('lxyzSig'),
        MC_pt                 = ufloat('MC_pt'),
        MC_eta                = ufloat('MC_eta'),
        MC_phi                = ufloat('MC_phi'),
        MC_mass               = ufloat('MC_mass'),
        MC_massErr            = ufloat('MC_massErr'),
        MC_chi2               = ufloat('MC_chi2'),
        MC_ndof               = ufloat('MC_ndof'),
        MC_prob               = ufloat('MC_prob'),
        MC_vx                 = ufloat('MC_vx'),
        MC_vy                 = ufloat('MC_vy'),
        MC_vz                 = ufloat('MC_vz'),
        MC_lxy                = ufloat('MC_lxy'),
        MC_lxySig             = ufloat('MC_lxySig'),
        MC_lxyz               = ufloat('MC_lxyz'),
        MC_lxyzSig            = ufloat('MC_lxyzSig'),
        raw_pt                 = ufloat('raw_pt'),
        raw_eta                = ufloat('raw_eta'),
        raw_phi                = ufloat('raw_phi'),
        raw_mass               = ufloat('raw_mass'),
        raw_trk1_pt                 = ufloat('raw_trk1_pt'),
        raw_trk1_eta                = ufloat('raw_trk1_eta'),
        raw_trk1_phi                = ufloat('raw_trk1_phi'),
        raw_trk1_mass               = ufloat('raw_trk1_mass'),
        raw_trk2_pt                 = ufloat('raw_trk2_pt'),
        raw_trk2_eta                = ufloat('raw_trk2_eta'),
        raw_trk2_phi                = ufloat('raw_trk2_phi'),
        raw_trk2_mass               = ufloat('raw_trk2_mass'),
        raw_trk3_pt                 = ufloat('raw_trk3_pt'),
        raw_trk3_eta                = ufloat('raw_trk3_eta'),
        raw_trk3_phi                = ufloat('raw_trk3_phi'),
        raw_trk3_mass               = ufloat('raw_trk3_mass'),
        raw_trk1_numberOfValidHits  = ufloat('raw_trk1_numberOfValidHits'),
        raw_trk1_normalizedChi2     = ufloat('raw_trk1_normalizedChi2'),
        raw_trk1_dxy_pv             = ufloat('raw_trk1_dxy_pv'),
        raw_trk2_numberOfValidHits  = ufloat('raw_trk2_numberOfValidHits'),
        raw_trk2_normalizedChi2     = ufloat('raw_trk2_normalizedChi2'),
        raw_trk2_dxy_pv             = ufloat('raw_trk2_dxy_pv'),
        raw_trk3_numberOfValidHits  = ufloat('raw_trk3_numberOfValidHits'),
        raw_trk3_normalizedChi2     = ufloat('raw_trk3_normalizedChi2'),
        raw_trk3_dxy_pv             = ufloat('raw_trk3_dxy_pv'),
        )
)
KstarMCMatch = cms.EDProducer("MCMatcher",            # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = KstarTable.src,                      # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(323),                            # one or more PDG ID (13 = mu); absolute values (see below)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(2),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                            # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)
KstarMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = KstarTable.src,
    genParts = cms.InputTag("finalGenParticlesBPH"),
    mcMap = cms.InputTag("KstarMCMatch"),
    objName = KstarTable.name,
    objType = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("Kstar"),
    docString = cms.string("MC matching to status==2 Kstar"),
)

BTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("BtoD0Kstar", "B"),
    cut       = cms.string(""),
    name      = cms.string("B"),
    doc       = cms.string("B Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        massErr = ufloat('massErr'),
        chi2 = ufloat('chi2'),
        ndof = ufloat('ndof'),
        prob = ufloat('prob'),
        vx                 = ufloat('vx'),
        vy                 = ufloat('vy'),
        vz                 = ufloat('vz'),
        lxy                = ufloat('lxy'),
        lxySig             = ufloat('lxySig'),
        lxyz               = ufloat('lxyz'),
        lxyzSig            = ufloat('lxyzSig'),
        MC_pt = ufloat('MC_pt'),
        MC_eta = ufloat('MC_eta'),
        MC_phi = ufloat('MC_phi'),
        MC_mass = ufloat('MC_mass'),
        MC_massErr = ufloat('MC_massErr'),
        MC_chi2 = ufloat('MC_chi2'),
        MC_ndof = ufloat('MC_ndof'),
        MC_prob = ufloat('MC_prob'),
        MC_vx                 = ufloat('MC_vx'),
        MC_vy                 = ufloat('MC_vy'),
        MC_vz                 = ufloat('MC_vz'),
        MC_lxy                = ufloat('MC_lxy'),
        MC_lxySig             = ufloat('MC_lxySig'),
        MC_lxyz               = ufloat('MC_lxyz'),
        MC_lxyzSig            = ufloat('MC_lxyzSig'),
        raw_pt                 = ufloat('raw_pt'),
        raw_eta                = ufloat('raw_eta'),
        raw_phi                = ufloat('raw_phi'),
        raw_mass               = ufloat('raw_mass'),
        d0_idx = uint('d0_idx'),
        kstar_idx = uint('kstar_idx'),
        D0_mass = ufloat('D0_mass'),
        Kstar_mass = ufloat('Kstar_mass'),
        Ks0_mass = ufloat('Ks0_mass'),
        )
)
BMCMatch = cms.EDProducer("MCMatcher",            # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = BTable.src,                      # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),       # final mc-truth particle collection
    mcPdgId     = cms.vint32(521),                            # one or more PDG ID (13 = mu); absolute values (see below)
    checkCharge = cms.bool(False),                            # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(2),                              # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),                            # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),                            # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),                   # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),                   # False = just match input in order; True = pick lowest deltaR pair first
)
BMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = BTable.src,
    genParts = cms.InputTag("finalGenParticlesBPH"),
    mcMap = cms.InputTag("BMCMatch"),
    objName = BTable.name,
    objType = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("B"),
    docString = cms.string("MC matching to status==2 B"),
)

# Gen match
BDKstarGen = cms.EDProducer("BDKstarGen",
   genParticle = cms.InputTag('finalGenParticlesBPH'),
)
BDKstarGenmatchTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("BDKstarGen", "BDKstarGenmatch"),
    cut       = cms.string(""),
    name      = cms.string("BGenmatch"),
    doc       = cms.string("genpart Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        idx_B    = uint('idx_B'),
        B_charge = uint('B_charge'),
        idx_D0 = uint("idx_D0"),
        idx_D0_dau1 = uint("idx_D0_dau1"),
        idx_D0_dau2 = uint("idx_D0_dau2"),
        idx_Kstar = uint("idx_Kstar"),
        idx_Kstar_pi = uint("idx_Kstar_pi"),
        idx_Ks  = uint("idx_Ks"),
        idx_Ks_pi1 = uint("idx_Ks_pi1"),
        idx_Ks_pi2 = uint("idx_Ks_pi2")
        )
)

Countgenpart = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("BDKstarGen", "BDKstarGenmatch")
)


BDKstarSequence = cms.Sequence(BtoD0Kstar)
BDKstarSequenceTable = cms.Sequence(D0Table + KstarTable + BTable)

BDKstarSequenceMC = cms.Sequence(BDKstarGen + BtoD0Kstar + D0MCMatch + KstarMCMatch + BMCMatch)
BDKstarSequenceMCTable = cms.Sequence(BDKstarGenmatchTable + D0Table + KstarTable + BTable + D0MCTable + KstarMCTable + BMCTable)



