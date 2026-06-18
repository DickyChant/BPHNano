import FWCore.ParameterSet.Config as cms
from PhysicsTools.NanoAOD.common_cff import *

# Photon selection paths (can be customized)

# Use your custom PATPhotonRefSelector implemented in plugins
photonBPH = cms.EDFilter("PATPhotonRefSelector",
    src = cms.InputTag("slimmedPhotons"),
    cut = cms.string("pt > 1.0 && abs(eta) < 2.5"),  # basic selection
)

# Count filter for minimum number of photons
countPhotons = cms.EDFilter("PATCandViewCountFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("photonBPH")
)

photonBPHTable = cms.EDProducer("SimplePATPhotonFlatTableProducer",
    src = cms.InputTag("photonBPH"),
    cut = cms.string(""),  # we should not filter on cross linked collections
    name = cms.string("Photon"),
    doc = cms.string("slimmedPhotons after basic selection"),
    singleton = cms.bool(False),  # the number of entries is variable
    extension = cms.bool(False),  # this is the main table for the photons
    variables = cms.PSet(
        CandVars,
        energyErr = Var("getCorrectedEnergyError('regression2')", float, doc="energy error of the cluster from regression", precision=6),
        energyRaw = Var("superCluster().rawEnergy()", float, doc="raw energy of photon supercluster", precision=10),
        superclusterEta = Var("superCluster().eta()", float, doc="supercluster eta", precision=10),
        r9 = Var("full5x5_r9()", float, doc="R9 of the supercluster, calculated with full 5x5 region", precision=10),
        sieie = Var("full5x5_sigmaIetaIeta()", float, doc="sigma_IetaIeta of the supercluster, calculated with full 5x5 region", precision=10),
        sipip = Var("showerShapeVariables().sigmaIphiIphi", float, doc="sigmaIphiIphi of the supercluster", precision=10),
        sieip = Var("full5x5_showerShapeVariables().sigmaIetaIphi", float, doc="sigma_IetaIphi of the supercluster, calculated with full 5x5 region", precision=10),
        s4 = Var("full5x5_showerShapeVariables().e2x2/full5x5_showerShapeVariables().e5x5", float, doc="e2x2/e5x5 of the supercluster, calculated with full 5x5 region", precision=10),
        etaWidth = Var("superCluster().etaWidth()", float, doc="Width of the photon supercluster in eta", precision=10),
        phiWidth = Var("superCluster().phiWidth()", float, doc="Width of the photon supercluster in phi", precision=10),
        electronVeto = Var("passElectronVeto()", bool, doc="pass electron veto"),
        pixelSeed = Var("hasPixelSeed()", bool, doc="has pixel seed"),
        hasConversionTracks = Var("hasConversionTracks()", bool, doc="Variable specifying if photon has associated conversion tracks (one-legged or two-legged)"),
        trkSumPtHollowConeDR03 = Var("trkSumPtHollowConeDR03()", float, doc="Sum of track pT in a hollow cone of outer radius, inner radius", precision=8),
        trkSumPtSolidConeDR04 = Var("trkSumPtSolidConeDR04()", float, doc="Sum of track pT in a cone of dR=0.4", precision=8),
        ecalPFClusterIso = Var("ecalPFClusterIso()", float, doc="sum pt of ecal clusters, vetoing clusters part of photon", precision=8),
        hcalPFClusterIso = Var("hcalPFClusterIso()", float, doc="sum pt of hcal clusters, vetoing clusters part of photon", precision=8),
        pfPhoIso03 = Var("photonIso()", float, doc="PF absolute isolation dR=0.3, photon component (uncorrected)"),
        pfChargedIso = Var("chargedHadronIso()", float, doc="PF absolute isolation dR=0.3, charged component with dxy,dz match to PV", precision=8),
        pfChargedIsoPFPV = Var("chargedHadronPFPVIso()", float, doc="PF absolute isolation dR=0.3, charged component (PF PV only)"),
        pfChargedIsoWorstVtx = Var("chargedHadronWorstVtxIso()", float, doc="PF absolute isolation dR=0.3, charged component (Vertex with largest isolation)"),
        hoe = Var("hadronicOverEm()", float, doc="H over E", precision=8),
        isScEtaEB = Var("abs(superCluster().eta()) < 1.4442", bool, doc="is supercluster eta within barrel acceptance"),
        isScEtaEE = Var("abs(superCluster().eta()) > 1.566 && abs(superCluster().eta()) < 2.5", bool, doc="is supercluster eta within endcap acceptance"),
        seediEtaOriX = Var("superCluster().seedCrysIEtaOrIx", "int8", doc="iEta or iX of seed crystal. iEta is barrel-only, iX is endcap-only. iEta runs from -85 to +85, with no crystal at iEta=0. iX runs from 1 to 100."),
        seediPhiOriY = Var("superCluster().seedCrysIPhiOrIy", int, doc="iPhi or iY of seed crystal. iPhi is barrel-only, iY is endcap-only. iPhi runs from 1 to 360. iY runs from 1 to 100."),
        # position of photon is best approximated by position of seed cluster, not the SC centroid
        x_calo = Var("superCluster().seed().position().x()", float, doc="photon supercluster position on calorimeter, x coordinate (cm)", precision=10),
        y_calo = Var("superCluster().seed().position().y()", float, doc="photon supercluster position on calorimeter, y coordinate (cm)", precision=10),
        z_calo = Var("superCluster().seed().position().z()", float, doc="photon supercluster position on calorimeter, z coordinate (cm)", precision=10),
        # ES variables
        esEffSigmaRR = Var("full5x5_showerShapeVariables().effSigmaRR()", float, doc="preshower sigmaRR"),
        esEnergyOverRawE = Var("superCluster().preshowerEnergy()/superCluster().rawEnergy()", float, doc="ratio of preshower energy to raw supercluster energy"),
        haloTaggerMVAVal = Var("haloTaggerMVAVal()", float, doc="Value of MVA based BDT based beam halo tagger in the Ecal endcap (valid for pT > 200 GeV)", precision=8),
    ),
)

photonBPHMCMatch = cms.EDProducer("MCMatcher",  # cut on deltaR, deltaPt/Pt; pick best by deltaR
    src = photonBPHTable.src,  # final reco collection
    matched = cms.InputTag("finalGenParticlesBPH"),  # final mc-truth particle collection
    mcPdgId = cms.vint32(22),  # one or more PDG ID (22 = photon); absolute values (see below)
    checkCharge = cms.bool(False),  # True = require RECO and MC objects to have the same charge
    mcStatus = cms.vint32(1),  # PYTHIA status code (1 = stable, 2 = shower, 3 = hard scattering)
    maxDeltaR = cms.double(0.3),  # Minimum deltaR for the match
    maxDPtRel = cms.double(0.5),  # Minimum deltaPt/Pt for the match
    resolveAmbiguities = cms.bool(True),  # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(True),  # False = just match input in order; True = pick lowest deltaR pair first
)

photonBPHMCTable = cms.EDProducer("CandMCMatchTableProducerBPH",
    recoObjects = photonBPHTable.src,
    genParts = cms.InputTag("finalGenParticlesBPH"),
    mcMap = cms.InputTag("photonBPHMCMatch"),
    objName = photonBPHTable.name,
    objType = photonBPHTable.name,
    objBranchName = cms.string("genPart"),
    genBranchName = cms.string("photon"),
    docString = cms.string("MC matching to status==1 photons"),
)

photonBPHSequence = cms.Sequence(photonBPH)
photonBPHSequenceMC = cms.Sequence(photonBPH + photonBPHMCMatch)
photonBPHTables = cms.Sequence(photonBPHTable)
photonBPHTablesMC = cms.Sequence(photonBPHTable + photonBPHMCTable)
