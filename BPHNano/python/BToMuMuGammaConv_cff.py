import FWCore.ParameterSet.Config as cms
from PhysicsTools.BPHNano.common_cff import *

########################### B0/Bs -> mu mu + gamma (gamma -> e+ e-) ###########################
# The builder finds converted photons (e+e-) and combines them with muon pairs.

BToMuMuGammaConv = cms.EDProducer(
    'BToMuMuGammaConvBuilder',
    # B mass window (GeV)
    bMassMin = cms.double(4.5),
    bMassMax = cms.double(6.5),
    # conversion radius window (cm) - conversions near ~1.5 cm are expected for early detector material
    convRMin = cms.double(0.5),
    convRMax = cms.double(5.0),
    applyMassConstraint = cms.bool(True),  # try to apply m=0 constraint on e+e- pair
    eleSelection = cms.string('pt > 0.5 && abs(eta) < 2.5'),
    postVtxSelection = cms.string('userFloat("conv_prob") > 0.000001'),
    dileptons = cms.InputTag("EtaMuMu:SelectedDiLeptons"),  # e.g. dimuon J/psi or direct muon pair
    leptonTransientTracks = cms.InputTag('muonBPH', 'AllTransientMuons'),
    electrons = cms.InputTag('tracksBPH', 'SelectedTracks'),
    electronTransientTracks = cms.InputTag('tracksBPH', 'SelectedTransientTracks'),
    beamSpot = cms.InputTag("offlineBeamSpot"),
)

BToMuMuGammaConvTable = cms.EDProducer(
    'SimpleCompositeCandidateFlatTableProducer',
    src       = cms.InputTag("BToMuMuGammaConv"),
    cut       = cms.string(""),
    name      = cms.string("BToMuMuGammaConv"),
    doc       = cms.string("B->mumu + converted photon (e+e-) Variables"),
    singleton = cms.bool(False),
    extension = cms.bool(False),
    variables = cms.PSet(
        CandVars,
        ll_idx = uint('ll_idx'),
        e1_idx = uint('e1_idx'),
        e2_idx = uint('e2_idx'),
        conv_vtx_x = ufloat('conv_vtx_x'),
        conv_vtx_y = ufloat('conv_vtx_y'),
        conv_vtx_z = ufloat('conv_vtx_z'),
        conv_vtx_r = ufloat('conv_vtx_r'),
        conv_chi2 = ufloat('conv_chi2'),
        conv_ndof = ufloat('conv_ndof'),
        conv_prob = ufloat('conv_prob'),
        conv_dca = ufloat('conv_dca'),
        conv_poca_r = ufloat('conv_poca_r'),
        conv_poca_z = ufloat('conv_poca_z'),
        conv_pointing_cos = ufloat('conv_pointing_cos'),
        conv_mass = ufloat('conv_mass'),
        conv_mass_constrained = ufloat('conv_mass_constrained'),
        conv_pt = ufloat('conv_pt'),
        conv_eta = ufloat('conv_eta'),
        conv_phi = ufloat('conv_phi'),
        # constraint summary (if applied)
        conv_constraint_sv_prob = ufloat('conv_constraint_sv_prob'),
        conv_constraint_pt = ufloat('conv_constraint_pt'),
        conv_constraint_eta = ufloat('conv_constraint_eta'),
        conv_constraint_phi = ufloat('conv_constraint_phi'),
        conv_constraint_mass = ufloat('conv_constraint_mass'),
        conv_constraint_massErr = ufloat('conv_constraint_massErr'),
        conv_constraint_mll = ufloat('conv_constraint_mll'),
        # dimuon (dilepton) 4-vector
        dilep_pt = ufloat('dilep_pt'),
        dilep_eta = ufloat('dilep_eta'),
        dilep_phi = ufloat('dilep_phi'),
        dilep_mass = ufloat('dilep_mass'),
        fitted_mass = ufloat('fitted_mass'),
        fitted_pt = ufloat('fitted_pt'),
        fitted_eta = ufloat('fitted_eta'),
        fitted_phi = ufloat('fitted_phi'),
    )
)

CountBToMuMuGammaConv = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(999999),
    src       = cms.InputTag("BToMuMuGammaConv")
)

BToMuMuGammaConvSequence = cms.Sequence( BToMuMuGammaConv )
BToMuMuGammaConvTables   = cms.Sequence( BToMuMuGammaConvTable )
