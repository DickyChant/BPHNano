import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

# Upsilon -> mu+mu- e+e-.  A (wide-window) dimuon + two soft charged tracks treated as
# electrons, common 4-track vertex fit (UpsilonTo2Mu2EBuilder = EtaTo2L2Pi with e mass).
# NOTE: the input dimuon (MuMu) must be produced with a WIDE mass window (~0.2-10 GeV),
# since the mumu pair in Upsilon->2mu2e is not at the Upsilon mass. The two e-legs come from
# the LowPtElectron collection (lowPtEleTracks: gsf-track transient tracks), NOT generic
# tracks; trk{1,2}_idx index directly into the LowPtElectron table (kept in the output).

UpsilonTo2Mu2E = cms.EDProducer(
    'UpsilonTo2Mu2EBuilder',
    dileptons             = cms.InputTag("MuMu", "SelectedDiLeptons"),
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    tracks                = cms.InputTag('lowPtEleTracks', 'SelectedElectrons'),
    transientTracks       = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectrons'),
    beamSpot              = cms.InputTag("offlineBeamSpot"),
    trk1Selection    = cms.string('pt > 0.5 && abs(eta) < 2.5'),   # soft electrons
    trk2Selection    = cms.string('pt > 0.5 && abs(eta) < 2.5'),
    preVtxSelection  = cms.string('charge() == 0 && pt > 2. && (mass > 8.0 && mass < 11.5)'),
    postVtxSelection = cms.string('userFloat("sv_prob") > 0.0 '
                                  '&& userFloat("fitted_mass") > 8.0 && userFloat("fitted_mass") < 11.5 '
                                  '&& userFloat("l_xy") < 0.2'),   # PROMPT: Upsilon has ~zero lifetime (loose, tunable)
)

########################### Table ###########################
UpsilonTo2Mu2ETable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("UpsilonTo2Mu2E"),
    cut       = cms.string(""),
    name      = cms.string("UpsilonTo2Mu2E"),
    doc       = cms.string("Upsilon -> mu+mu- e+e- candidates"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        l1_idx   = uint('l1_idx'),
        l2_idx   = uint('l2_idx'),
        ll_idx   = uint('ll_idx'),
        trk1_idx = uint('trk1_idx'),     # -> index into the LowPtElectron table
        trk2_idx = uint('trk2_idx'),
        trk1_mass = ufloat('trk1_mass'),
        trk2_mass = ufloat('trk2_mass'),
        min_dr   = ufloat('min_dr'),
        max_dr   = ufloat('max_dr'),
        chi2     = ufloat('sv_chi2'),
        svprob   = ufloat('sv_prob'),
        cos2D    = ufloat('cos_theta_2D'),
        fit_cos2D = ufloat('fitted_cos_theta_2D'),
        l_xy     = ufloat('l_xy'),
        l_xy_unc = ufloat('l_xy_unc'),
        mll_fullfit = ufloat('fitted_mll'),
        mee_fullfit = ufloat('fitted_mee'),
        fitted_mass    = ufloat('fitted_mass'),
        fitted_massErr = ufloat('fitted_massErr'),
        fitted_pt      = ufloat('fitted_pt'),
        fitted_eta     = ufloat('fitted_eta'),
        fitted_phi     = ufloat('fitted_phi'),
        fitted_rapidity = ufloat('fitted_rapidity'),
        vtx_x = ufloat('vtx_x'), vtx_y = ufloat('vtx_y'), vtx_z = ufloat('vtx_z'),
        vtx_cxx = ufloat('vtx_cxx'), vtx_cyy = ufloat('vtx_cyy'), vtx_czz = ufloat('vtx_czz'),
        vtx_cyx = ufloat('vtx_cyx'), vtx_czx = ufloat('vtx_czx'), vtx_czy = ufloat('vtx_czy'),
        fit_l1_pt = ufloat('fitted_l1_pt'), fit_l1_eta = ufloat('fitted_l1_eta'), fit_l1_phi = ufloat('fitted_l1_phi'),
        fit_l2_pt = ufloat('fitted_l2_pt'), fit_l2_eta = ufloat('fitted_l2_eta'), fit_l2_phi = ufloat('fitted_l2_phi'),
        fit_trk1_pt = ufloat('fitted_trk1_pt'), fit_trk1_eta = ufloat('fitted_trk1_eta'), fit_trk1_phi = ufloat('fitted_trk1_phi'),
        fit_trk2_pt = ufloat('fitted_trk2_pt'), fit_trk2_eta = ufloat('fitted_trk2_eta'), fit_trk2_phi = ufloat('fitted_trk2_phi'),
        l1_iso04 = ufloat('l1_iso04'), l2_iso04 = ufloat('l2_iso04'),
        trk1_iso04 = ufloat('trk1_iso04'), trk2_iso04 = ufloat('trk2_iso04'),
        trk1_svip2d = ufloat('trk1_svip2d'), trk1_svip2d_err = ufloat('trk1_svip2d_err'),
        trk2_svip2d = ufloat('trk2_svip2d'), trk2_svip2d_err = ufloat('trk2_svip2d_err'),
    )
)

########################### MC Matching ###########################
UpsilonTo2Mu2EBPHMCMatch = cms.EDProducer("MCMatcher",
    src         = UpsilonTo2Mu2ETable.src,
    matched     = cms.InputTag("finalGenParticlesBPH"),
    mcPdgId     = cms.vint32(553, 100553, 200553),
    checkCharge = cms.bool(False),
    mcStatus    = cms.vint32(2),
    maxDeltaR   = cms.double(0.1),
    maxDPtRel   = cms.double(0.5),
    resolveAmbiguities    = cms.bool(True),
    resolveByMatchQuality = cms.bool(True),
)

UpsilonTo2Mu2EBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = UpsilonTo2Mu2ETable.src,
    genParts    = cms.InputTag("finalGenParticlesBPH"),
    mcMap       = cms.InputTag("UpsilonTo2Mu2EBPHMCMatch"),
    objName     = UpsilonTo2Mu2ETable.name,
    objType     = cms.string("Other"),
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("UpsilonTo2Mu2E"),
    docString   = cms.string("MC matching to status==2 Upsilon(nS) -> 2mu2e"),
)

########################### Sequences ###########################
UpsilonTo2Mu2ESequence   = cms.Sequence(UpsilonTo2Mu2E)
UpsilonTo2Mu2ETables     = cms.Sequence(UpsilonTo2Mu2ETable)
UpsilonTo2Mu2EMCSequence = cms.Sequence(UpsilonTo2Mu2E + UpsilonTo2Mu2EBPHMCMatch)
UpsilonTo2Mu2EMCTables   = cms.Sequence(UpsilonTo2Mu2ETable + UpsilonTo2Mu2EBPHMCTable)
