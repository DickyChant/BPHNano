import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

########################### Pentaquark -> J/psi p ###########################
# Pc(4312), Pc(4440), Pc(4457) -> J/psi p search

PentaquarkToJpsiP = cms.EDProducer(
    'PentaquarkToJpsiPBuilder',
    dileptons = cms.InputTag("MuMu:SelectedDiLeptons"),
    leptonTransientTracks = cms.InputTag('muonBPH', 'SelectedTransientMuons'),
    protons = cms.InputTag('tracksBPH', 'SelectedTracks'),
    protonsTransientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    PUtracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    preVtxSelection  = cms.string('pt > 3.0'
                                  '&& 4.0 < mass && mass < 5.0'
                                  '&& userFloat("min_dr") > 0.03'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.001'
                                  '&& userFloat("fitted_cos_theta_2D") > 0.9'),
    dileptonMassContraint = cms.double(3.0969)  # J/psi mass constraint
)

########################### Pentaquark -> J/psi p K ###########################
# Full Lambda_b -> J/psi p K analysis for pentaquark search
# Pc -> J/psi p resonance in Lambda_b -> J/psi p K decays

PentaquarkToJpsiPK = cms.EDProducer(
    'PentaquarkToJpsiPKBuilder',
    dileptons = cms.InputTag("MuMu:SelectedDiLeptons"),
    leptonTransientTracks = cms.InputTag('muonBPH', 'SelectedTransientMuons'),
    tracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    transientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    PUtracks = cms.InputTag('tracksBPH', 'SelectedTracks'),
    beamSpot = cms.InputTag("offlineBeamSpot"),
    preVtxSelection  = cms.string('pt > 5.'
                                  '&& 5.2 < mass && mass < 6.0'
                                  '&& userFloat("min_dr") > 0.03'),
    postVtxSelection = cms.string('5.2 < userFloat("fitted_mass") && userFloat("fitted_mass") < 6.0'
                                  '&& userFloat("sv_prob") > 0.001'
                                  '&& userFloat("fitted_cos_theta_2D") > 0.9'),
    dileptonMassContraint = cms.double(3.0969)  # J/psi mass constraint
)

########################### Tables ###########################

# J/psi + p Table
PentaquarkToJpsiPTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("PentaquarkToJpsiP"),
    cut       = cms.string(""),
    name      = cms.string("PentaquarkJpsiP"),
    doc       = cms.string("Pentaquark -> J/psi p candidates (Pc search)"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        # pre-fit quantities
        CandVars,
        l1_idx = uint('l1_idx'),
        l2_idx = uint('l2_idx'),
        proton_idx = uint('proton_idx'),
        ll_idx = uint('ll_idx'),
        minDR  = ufloat('min_dr'),
        maxDR  = ufloat('max_dr'),
        # Pre-fit J/psi + p mass
        jpsi_p_mass = ufloat('jpsi_p_mass'),
        # fit and vtx info
        svprob   = ufloat('sv_prob'),
        l_xy     = ufloat('l_xy'),
        l_xy_unc = ufloat('l_xy_unc'),
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
        # Mll
        mll_fullfit = ufloat('fitted_mll'),
        # Cos(theta)
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        # post-fit momentum
        fit_mass    = ufloat('fitted_mass'),
        fit_massErr = ufloat('fitted_massErr'),
        fit_pt      = ufloat('fitted_pt'),
        fit_eta     = ufloat('fitted_eta'),
        fit_phi     = ufloat('fitted_phi'),
        # Fitted J/psi + p mass (Pc candidate)
        fit_jpsi_p_mass = ufloat('fitted_jpsi_p_mass'),
        # Post-fit tracks
        fit_l1_pt   = ufloat('fitted_l1_pt'),
        fit_l1_eta  = ufloat('fitted_l1_eta'),
        fit_l1_phi  = ufloat('fitted_l1_phi'),
        fit_l2_pt   = ufloat('fitted_l2_pt'),
        fit_l2_eta  = ufloat('fitted_l2_eta'),
        fit_l2_phi  = ufloat('fitted_l2_phi'),
        fit_proton_pt  = ufloat('fitted_proton_pt'),
        fit_proton_eta = ufloat('fitted_proton_eta'),
        fit_proton_phi = ufloat('fitted_proton_phi'),
        # Impact parameters
        proton_svip2d     = ufloat('proton_svip2d'),
        proton_svip2d_err = ufloat('proton_svip2d_err'),
        # Isolation
        l1_iso04     = ufloat('l1_iso04'),
        l2_iso04     = ufloat('l2_iso04'),
        proton_iso04 = ufloat('proton_iso04'),
    )
)

# J/psi + p + K Table (Lambda_b -> J/psi p K for Pc search)
PentaquarkToJpsiPKTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("PentaquarkToJpsiPK"),
    cut       = cms.string(""),
    name      = cms.string("PentaquarkJpsiPK"),
    doc       = cms.string("Lambda_b -> J/psi p K candidates (Pentaquark Pc search)"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        # pre-fit quantities
        CandVars,
        l1_idx     = uint('l1_idx'),
        l2_idx     = uint('l2_idx'),
        proton_idx = uint('proton_idx'),
        kaon_idx   = uint('kaon_idx'),
        ll_idx     = uint('ll_idx'),
        min_dr     = ufloat('min_dr'),
        max_dr     = ufloat('max_dr'),
        # Pre-fit invariant masses
        jpsi_p_mass = ufloat('jpsi_p_mass'),  # Pc candidate mass
        jpsi_k_mass = ufloat('jpsi_k_mass'),
        p_k_mass    = ufloat('p_k_mass'),
        # vtx info
        chi2      = ufloat('sv_chi2'),
        svprob    = ufloat('sv_prob'),
        cos2D     = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        l_xy      = ufloat('l_xy'),
        l_xy_unc  = ufloat('l_xy_unc'),
        # post-fit momentum/masses
        mll_fullfit       = ufloat('fitted_mll'),
        fit_jpsi_p_mass   = ufloat('fitted_jpsi_p_mass'),  # Pc candidate fitted mass
        fit_jpsi_k_mass   = ufloat('fitted_jpsi_k_mass'),
        fit_p_k_mass      = ufloat('fitted_p_k_mass'),
        fit_mass          = ufloat('fitted_mass'),
        fit_massErr       = ufloat('fitted_massErr'),
        fit_pt            = ufloat('fitted_pt'),
        fit_eta           = ufloat('fitted_eta'),
        fit_phi           = ufloat('fitted_phi'),
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
        fit_l1_pt      = ufloat('fitted_l1_pt'),
        fit_l1_eta     = ufloat('fitted_l1_eta'),
        fit_l1_phi     = ufloat('fitted_l1_phi'),
        fit_l2_pt      = ufloat('fitted_l2_pt'),
        fit_l2_eta     = ufloat('fitted_l2_eta'),
        fit_l2_phi     = ufloat('fitted_l2_phi'),
        fit_proton_pt  = ufloat('fitted_proton_pt'),
        fit_proton_eta = ufloat('fitted_proton_eta'),
        fit_proton_phi = ufloat('fitted_proton_phi'),
        fit_kaon_pt    = ufloat('fitted_kaon_pt'),
        fit_kaon_eta   = ufloat('fitted_kaon_eta'),
        fit_kaon_phi   = ufloat('fitted_kaon_phi'),
        # isolation 
        l1_iso04     = ufloat('l1_iso04'),
        l2_iso04     = ufloat('l2_iso04'),
        proton_iso04 = ufloat('proton_iso04'),
        kaon_iso04   = ufloat('kaon_iso04'),
        # Impact parameters
        proton_svip2d     = ufloat('proton_svip2d'),
        proton_svip2d_err = ufloat('proton_svip2d_err'),
        kaon_svip2d       = ufloat('kaon_svip2d'),
        kaon_svip2d_err   = ufloat('kaon_svip2d_err'),
    )
)

########################### Counters ###########################

CountPentaquarkToJpsiP = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("PentaquarkToJpsiP")
)

CountPentaquarkToJpsiPK = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("PentaquarkToJpsiPK")
)

########################### MC Matching ###########################

# Pc -> J/psi p MC matching
PentaquarkToJpsiPBPHMCMatch = cms.EDProducer("MCMatcher",
    src         = PentaquarkToJpsiPTable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(4312, 4440, 4457),  # Pc states PDG IDs
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.03),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

PentaquarkToJpsiPBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = PentaquarkToJpsiPTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("PentaquarkToJpsiPBPHMCMatch"),
    objName     = PentaquarkToJpsiPTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("PentaquarkJpsiP"),
    docString   = cms.string("MC matching to Pc pentaquark states"),
)

# Lambda_b -> J/psi p K MC matching
PentaquarkToJpsiPKBPHMCMatch = cms.EDProducer("MCMatcher",
    src         = PentaquarkToJpsiPKTable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(5122),  # Lambda_b PDG ID
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.03),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

PentaquarkToJpsiPKBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = PentaquarkToJpsiPKTable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("PentaquarkToJpsiPKBPHMCMatch"),
    objName     = PentaquarkToJpsiPKTable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("PentaquarkJpsiPK"),
    docString   = cms.string("MC matching to Lambda_b for pentaquark search"),
)

########################### Sequences ###########################

# J/psi + p sequences
PentaquarkToJpsiPSequence = cms.Sequence(PentaquarkToJpsiP)
PentaquarkToJpsiPTables = cms.Sequence(PentaquarkToJpsiPTable)
PentaquarkToJpsiPMCSequence = cms.Sequence(PentaquarkToJpsiP + PentaquarkToJpsiPBPHMCMatch)
PentaquarkToJpsiPMCTables = cms.Sequence(PentaquarkToJpsiPTable + PentaquarkToJpsiPBPHMCTable)

# J/psi + p + K sequences (Lambda_b for Pc search)
PentaquarkToJpsiPKSequence = cms.Sequence(PentaquarkToJpsiPK)
PentaquarkToJpsiPKTables = cms.Sequence(PentaquarkToJpsiPKTable)
PentaquarkToJpsiPKMCSequence = cms.Sequence(PentaquarkToJpsiPK + PentaquarkToJpsiPKBPHMCMatch)
PentaquarkToJpsiPKMCTables = cms.Sequence(PentaquarkToJpsiPKTable + PentaquarkToJpsiPKBPHMCTable)
