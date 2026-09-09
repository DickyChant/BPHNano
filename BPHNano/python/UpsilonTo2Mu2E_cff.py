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
    transientTracksLow     = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectronsLow'),
    transientTracksNominal = cms.InputTag('lowPtEleTracks', 'SelectedTransientElectronsNominal'),
    beamSpot              = cms.InputTag("offlineBeamSpot"),
    trk1Selection    = cms.string('pt > 0.5 && abs(eta) < 2.5'),   # soft electrons
    trk2Selection    = cms.string('pt > 0.5 && abs(eta) < 2.5'),
    # keep the e pair opposite-sign by default; the eta' config turns this on to build the
    # same-sign combinatorial control alongside the signal
    allowSameSignTrackPair = cms.bool(False),
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
        # NOMINAL mass: per leg, the standard electron at/above nominalPtThreshold (10 GeV)
        # and the LowPtElectron below it.
        fitted_mass    = ufloat('fitted_mass'),
        fitted_massErr = ufloat('fitted_massErr'),
        # The same candidate refitted under each explicit object choice, leg1 then leg2.
        # -1 (both mass and error) when a leg lacks the reconstruction that combination needs.
        fitted_mass_lowlow            = ufloat('fitted_mass_lowlow'),
        fitted_massErr_lowlow         = ufloat('fitted_massErr_lowlow'),
        fitted_mass_lownominal        = ufloat('fitted_mass_lownominal'),
        fitted_massErr_lownominal     = ufloat('fitted_massErr_lownominal'),
        fitted_mass_nominallow        = ufloat('fitted_mass_nominallow'),
        fitted_massErr_nominallow     = ufloat('fitted_massErr_nominallow'),
        fitted_mass_nominalnominal    = ufloat('fitted_mass_nominalnominal'),
        fitted_massErr_nominalnominal = ufloat('fitted_massErr_nominalnominal'),
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
        # --- conversion handles (see UpsilonTo2Mu2EBuilder / LowPtEleMerger) ---
        # per-leg match to a reconstructed photon conversion, and that conversion's radius.
        # NOTE: use these, NOT the central LowPtElectron_convVtxRadius branch, which is filled
        # per event and is identical for every electron in an event.
        # e-leg provenance: 0 = LowPtElectron table, 1 = Electron table, -1 = generic track.
        # (trk1_src, trk2_src) defines the three analysis categories.
        trk1_src = uint('trk1_src'),
        trk2_src = uint('trk2_src'),
        trk1_conv_matched = uint('trk1_conv_matched'),
        trk2_conv_matched = uint('trk2_conv_matched'),
        # Both reconstructions of each leg. has_low / has_nominal = 1 when that
        # reconstruction exists for the leg; *_idx index into the LowPtElectron and Electron
        # collections respectively (-1 when absent).
        # Availability category. Per leg: 0 = only LowPtElectron, 1 = only standard
        # (slimmedElectron), 2 = both. Combined: ele_cat = trk1_ele_cat*3 + trk2_ele_cat,
        # i.e. 0..8, the nine categories.
        ele_cat = uint('ele_cat'),
        trk1_ele_cat = uint('trk1_ele_cat'), trk2_ele_cat = uint('trk2_ele_cat'),
        trk1_has_low = uint('trk1_has_low'), trk2_has_low = uint('trk2_has_low'),
        trk1_has_nominal = uint('trk1_has_nominal'), trk2_has_nominal = uint('trk2_has_nominal'),
        trk1_low_idx = uint('trk1_low_idx'), trk2_low_idx = uint('trk2_low_idx'),
        trk1_nominal_idx = uint('trk1_nominal_idx'), trk2_nominal_idx = uint('trk2_nominal_idx'),
        trk1_low_pt = ufloat('trk1_low_pt'), trk2_low_pt = ufloat('trk2_low_pt'),
        trk1_low_eta = ufloat('trk1_low_eta'), trk2_low_eta = ufloat('trk2_low_eta'),
        trk1_low_phi = ufloat('trk1_low_phi'), trk2_low_phi = ufloat('trk2_low_phi'),
        trk1_nominal_pt = ufloat('trk1_nominal_pt'), trk2_nominal_pt = ufloat('trk2_nominal_pt'),
        trk1_nominal_eta = ufloat('trk1_nominal_eta'), trk2_nominal_eta = ufloat('trk2_nominal_eta'),
        trk1_nominal_phi = ufloat('trk1_nominal_phi'), trk2_nominal_phi = ufloat('trk2_nominal_phi'),
        trk1_lost_hits = uint('trk1_lost_hits'), trk2_lost_hits = uint('trk2_lost_hits'),
        trk1_pass_conv_veto = uint('trk1_pass_conv_veto'),
        trk2_pass_conv_veto = uint('trk2_pass_conv_veto'),
        trk1_sieie = ufloat('trk1_sieie'), trk2_sieie = ufloat('trk2_sieie'),
        trk1_hoe = ufloat('trk1_hoe'), trk2_hoe = ufloat('trk2_hoe'),
        trk1_conv_dr = ufloat('trk1_conv_dr'), trk2_conv_dr = ufloat('trk2_conv_dr'),
        trk1_conv_r = ufloat('trk1_conv_r'),
        trk2_conv_r = ufloat('trk2_conv_r'),
        # dedicated two-track e+e- vertex: radius separates a converted photon (beam pipe
        # ~2-3 cm, pixels ~3-6 cm) from a prompt double-Dalitz pair (~0)
        ee_vtx_r  = ufloat('ee_vtx_r'),
        ee_vtx_x  = ufloat('ee_vtx_x'),
        ee_vtx_y  = ufloat('ee_vtx_y'),
        ee_vtx_z  = ufloat('ee_vtx_z'),
        ee_svprob = ufloat('ee_svprob'),
        ee_mass   = ufloat('ee_mass'),
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
