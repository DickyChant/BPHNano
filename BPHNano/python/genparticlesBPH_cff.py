import FWCore.ParameterSet.Config as cms
from  PhysicsTools.NanoAOD.genparticles_cff import *


# for BPHPark start with merged particles (pruned + packed),
# where pruned contain K* states, but not final states, 
# and packed contain final states (K pi).
# then you save also final states (granddaughters)
finalGenParticlesBPH = finalGenParticles.clone(
  src = cms.InputTag("mergedGenParticles"),
  select = cms.vstring(
	"drop *",
        "keep++ (abs(pdgId) == 511 || abs(pdgId) == 521 || abs(pdgId)==531 || abs(pdgId)==221)",  #keep all B0(=511) and B+/-(521) + their daughters and granddaughters
        "keep++ abs(pdgId) == 5122", #  keep full lambda_b0
   )
)

genParticleBPHTable = genParticleTable.clone(
  src = cms.InputTag("finalGenParticlesBPH"),
  # drop the inherited GenPart_iso external variable: the central `genIso` ValueMap is keyed
  # to finalGenParticles, not finalGenParticlesBPH, so it is neither scheduled nor aligned here.
  externalVariables = cms.PSet(),
  variables = cms.PSet(
      genParticleTable.variables,
      vx = Var("vx()", float, doc="x coordinate of the production vertex position, in cm"),
      vy = Var("vy()", float, doc="y coordinate of the production vertex position, in cm"),
      vz = Var("vz()", float, doc="z coordinate of the production vertex position, in cm"),
  )
)



genParticleBPHSequence = cms.Sequence(finalGenParticlesBPH)
genParticleBPHTables = cms.Sequence(genParticleBPHTable)

