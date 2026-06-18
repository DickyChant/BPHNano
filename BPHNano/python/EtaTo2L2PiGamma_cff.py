import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

########################### Eta -> 2mu 2pion gamma(s) (B0->J/Psi+eta) ###########################
# Supports:
# - eta -> 2pi + gamma (direct, nPhotons=1)
# - eta -> 2pi + pi0 -> 2pi + 2gamma (via pi0 decay, nPhotons=2)

# Configuration for 2-photon case (eta -> 2pi + pi0 -> 2pi + 2gamma)
EtaTo2L2PiGamma = cms.EDProducer(
    'EtaTo2L2PiGammaBuilder',
    # Mass windows (all in GeV)
    etaMassMin = cms.double(0.50),
    etaMassMax = cms.double(0.58),
    pi0MassMin = cms.double(0.11),
    pi0MassMax = cms.double(0.16),
    jpsiMassMin = cms.double(3.00),
    jpsiMassMax = cms.double(3.20),
    bMassMin = cms.double(4.5),
    bMassMax = cms.double(6.0),
    gammaPairMassMin = cms.double(0.10), # if needed
    gammaPairMassMax = cms.double(0.16),
    dileptons = cms.InputTag("EtaMuMu:SelectedDiLeptons"),  # J/Psi -> 2mu
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),  # 2 pions
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    photons = cms.InputTag("photonBPH"),  # photons
    beamSpot = cms.InputTag("offlineBeamSpot"),
    nPhotons = cms.int32(2),  # 2 photons for pi0 -> 2gamma decay
    trk1Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5'),
    trk2Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5'),
    pho1Selection   = cms.string('pt > 2.0 && abs(eta) < 2.5'),
    pho2Selection   = cms.string('pt > 2.0 && abs(eta) < 2.5'),
    preVtxSelection  = cms.string('pt > 5. && charge() == 0 && mass > 4.5 && mass < 6.0'),  # B0 mass window
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 && userFloat("fitted_mass") > 4.5 && userFloat("fitted_mass") < 6.0'),
)

# Configuration for 1-photon case (eta -> 2pi + gamma direct)
EtaTo2L2Pi1Gamma = cms.EDProducer(
    'EtaTo2L2PiGammaBuilder',
    # Mass windows (all in GeV)
    etaMassMin = cms.double(0.50),
    etaMassMax = cms.double(1.20),
    jpsiMassMin = cms.double(3.00),
    jpsiMassMax = cms.double(3.20),
    bMassMin = cms.double(4.8),
    bMassMax = cms.double(6.2),
    dileptons = cms.InputTag("EtaMuMu:SelectedDiLeptons"),  # J/Psi -> 2mu
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),  # 2 pions
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    photons = cms.InputTag("photonBPH"),  # photons
    beamSpot = cms.InputTag("offlineBeamSpot"),
    nPhotons = cms.int32(1),  # 1 photon for direct decay
    trk1Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5'),
    trk2Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5'),
    pho1Selection   = cms.string('pt > 1.0 && abs(eta) < 2.5'),
    # pho2Selection not needed for nPhotons=1
    preVtxSelection  = cms.string('pt > 5. && charge() == 0'),  # B0 mass window
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0'),
)

########################### Tables ###########################

EtaTo2L2PiGammaTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("EtaTo2L2PiGamma"),
    cut       = cms.string(""),
    name      = cms.string("EtaTo2L2PiGamma"),
    doc       = cms.string("B0->J/Psi(->2mu)+eta(->2pi+2gamma) Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        # pre-fit quantities
        CandVars,
        l1_idx      = uint('l1_idx'),
        l2_idx      = uint('l2_idx'),
        ll_idx      = uint('ll_idx'),
        trk1_idx    = uint('trk1_idx'),
        trk2_idx    = uint('trk2_idx'),
        pho1_idx    = uint('pho1_idx'),
        pho2_idx    = uint('pho2_idx'),
        nPhotons    = uint('nPhotons'),  # 1 or 2
        trk1_mass   = ufloat('trk1_mass'),
        trk2_mass   = ufloat('trk2_mass'),
        min_dr      = ufloat('min_dr'),
        max_dr      = ufloat('max_dr'),
        # intermediate masses (pre-fit)
        m_jpsi      = ufloat('m_jpsi'),
        m_eta       = ufloat('m_eta'),
        m_2pi       = ufloat('m_2pi'),
        m_2gamma    = ufloat('m_2gamma'),
        # vtx info
        chi2        = ufloat('sv_chi2'),
        svprob      = ufloat('sv_prob'),
        cos2D       = ufloat('cos_theta_2D'),
        fit_cos2D   = ufloat('fitted_cos_theta_2D'),
        l_xy        = ufloat('l_xy'),
        l_xy_unc    = ufloat('l_xy_unc'),
        # post-fit momentum /masses
        mll_fullfit       = ufloat('fitted_mll'),  # J/Psi mass from fitted muons
        mtrktrk_fullfit   = ufloat('fitted_ditrack_mass'),  # 2pi mass from fitted pions
        fitted_m_jpsi     = ufloat('fitted_m_jpsi'),  # J/Psi from fitted muons
        fitted_m_eta      = ufloat('fitted_m_eta'),  # eta from fitted pions + photons
        fitted_mass       = ufloat('fitted_mass'),  # B0 mass
        fitted_massErr    = ufloat('fitted_massErr'),
        fitted_pt         = ufloat('fitted_pt'),
        fitted_eta        = ufloat('fitted_eta'),
        fitted_phi        = ufloat('fitted_phi'),
        fitted_rapidity   = ufloat('fitted_rapidity'),
        # vertex
        vtx_x   = ufloat('vtx_x'),
        vtx_y   = ufloat('vtx_y'),
        vtx_z   = ufloat('vtx_z'),
        vtx_cxx = ufloat('vtx_cxx'),
        vtx_cyy = ufloat('vtx_cyy'),
        vtx_czz = ufloat('vtx_czz'),
        vtx_cyx = ufloat('vtx_cyx'),
        vtx_czx = ufloat('vtx_czx'),
        vtx_czy = ufloat('vtx_czy'),
        # post-fit tracks/leptons
        #l1
        fit_l1_pt  = ufloat('fitted_l1_pt'),
        fit_l1_eta = ufloat('fitted_l1_eta'),
        fit_l1_phi = ufloat('fitted_l1_phi'),
        #l2
        fit_l2_pt  = ufloat('fitted_l2_pt'),
        fit_l2_eta = ufloat('fitted_l2_eta'),
        fit_l2_phi = ufloat('fitted_l2_phi'),
        #pion1
        fit_trk1_pt  = ufloat('fitted_trk1_pt'),
        fit_trk1_eta = ufloat('fitted_trk1_eta'),
        fit_trk1_phi = ufloat('fitted_trk1_phi'),
        #pion2
        fit_trk2_pt  = ufloat('fitted_trk2_pt'),
        fit_trk2_eta = ufloat('fitted_trk2_eta'),
        fit_trk2_phi = ufloat('fitted_trk2_phi'),
        #photons (not fitted, use original kinematics)
        fit_pho1_pt  = ufloat('fitted_pho1_pt'),
        fit_pho1_eta = ufloat('fitted_pho1_eta'),
        fit_pho1_phi = ufloat('fitted_pho1_phi'),
        fit_pho2_pt  = ufloat('fitted_pho2_pt'),
        fit_pho2_eta = ufloat('fitted_pho2_eta'),
        fit_pho2_phi = ufloat('fitted_pho2_phi'),
        # isolation 
        l1_iso04   = ufloat('l1_iso04'),
        l2_iso04   = ufloat('l2_iso04'),
        trk1_iso04 = ufloat('trk1_iso04'),
        trk2_iso04 = ufloat('trk2_iso04'),
        trk1_svip2d     = ufloat('trk1_svip2d'),
        trk1_svip2d_err = ufloat('trk1_svip2d_err'),
        trk2_svip2d     = ufloat('trk2_svip2d'),
        trk2_svip2d_err = ufloat('trk2_svip2d_err'),
    )
)

CountEtaTo2L2PiGamma = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("EtaTo2L2PiGamma")
)

# Table for 1-photon case (can reuse same structure, just different src)
EtaTo2L2Pi1GammaTable = EtaTo2L2PiGammaTable.clone(
    src = cms.InputTag("EtaTo2L2Pi1Gamma"),
    name = cms.string("EtaTo2L2Pi1Gamma"),
    doc = cms.string("B0->J/Psi(->2mu)+eta(->2pi+gamma) Variables"),
)

CountEtaTo2L2Pi1Gamma = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("EtaTo2L2Pi1Gamma")
)

EtaTo2L2PiGammaBPHMCMatch = cms.EDProducer("MCMatcher",  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src         = EtaTo2L2PiGammaTable.src,  # final reco collection
    matched     = cms.InputTag("finalGenParticlesBPH"),  # final mc-truth particle collection
    mcPdgId     = cms.vint32(511),  # B0 PDG ID
    checkCharge = cms.bool(False),  # True = require RECO and MC objects to have the same charge
    mcStatus    = cms.vint32(22),  # PYTHIA status code (22 = intermediate, 2 = shower, 3 = hard scattering)
    maxDeltaR   = cms.double(0.1),  # Minimum deltaR for the match
    maxDPtRel   = cms.double(0.5),  # Minimum deltaPt/Pt for the match
    resolveAmbiguities    = cms.bool(True),  # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),  # False = just match input in order; True = pick lowest deltaR pair first
)

EtaTo2L2PiGammaBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = EtaTo2L2PiGammaTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("EtaTo2L2PiGammaBPHMCMatch"),
    objName     = EtaTo2L2PiGammaTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("EtaTo2L2PiGamma"),
    docString   = cms.string("MC matching to status==22 B0"),
)

########################### Sequencies  ############################
# 2-photon sequences
EtaTo2L2PiGammaSequence = cms.Sequence( EtaTo2L2PiGamma )
EtaTo2L2PiGammaTables   = cms.Sequence( EtaTo2L2PiGammaTable )
EtaTo2L2PiGammaMCSequence = cms.Sequence( EtaTo2L2PiGamma + EtaTo2L2PiGammaBPHMCMatch )
EtaTo2L2PiGammaMCTables   = cms.Sequence( EtaTo2L2PiGammaTable + EtaTo2L2PiGammaBPHMCTable )

# 1-photon sequences
EtaTo2L2Pi1GammaSequence = cms.Sequence( EtaTo2L2Pi1Gamma )
EtaTo2L2Pi1GammaTables   = cms.Sequence( EtaTo2L2Pi1GammaTable )
# MC matching for 1-photon (can reuse same matcher config)
EtaTo2L2Pi1GammaBPHMCMatch = EtaTo2L2PiGammaBPHMCMatch.clone(
    src = EtaTo2L2Pi1GammaTable.src,
)
EtaTo2L2Pi1GammaBPHMCTable = EtaTo2L2PiGammaBPHMCTable.clone(
    recoObjects = EtaTo2L2Pi1GammaTable.src,
    mcMap = cms.InputTag("EtaTo2L2Pi1GammaBPHMCMatch"),
    objName = EtaTo2L2Pi1GammaTable.name,
    genBranchName = cms.string("EtaTo2L2Pi1Gamma"),
    docString = cms.string("MC matching to status==22 B0 (1-photon case)"),
)
EtaTo2L2Pi1GammaMCSequence = cms.Sequence( EtaTo2L2Pi1Gamma + EtaTo2L2Pi1GammaBPHMCMatch )
EtaTo2L2Pi1GammaMCTables   = cms.Sequence( EtaTo2L2Pi1GammaTable + EtaTo2L2Pi1GammaBPHMCTable )

