// original author: RK18 team
#include "KinVtxFitter.h"
#include <memory>
#include "RecoVertex/KinematicFitPrimitives/interface/KinematicParticleFactoryFromTransientTrack.h"
#include "RecoVertex/KinematicFit/interface/KinematicParticleVertexFitter.h"
#include "RecoVertex/KinematicFit/interface/KinematicConstrainedVertexFitter.h"
#include "RecoVertex/KinematicFit/interface/KinematicParticleVertexFitter.h"
#include "RecoVertex/KinematicFit/interface/TwoTrackMassKinematicConstraint.h" // MIGHT be useful for Phi->KK?
#include "RecoVertex/KinematicFit/interface/MassKinematicConstraint.h"

KinVtxFitter::KinVtxFitter(const std::vector<reco::TransientTrack> tracks, 
                           const std::vector<double> masses, 
                           std::vector<float> sigmas):
  n_particles_{masses.size()} {
  
  KinematicParticleFactoryFromTransientTrack factory;
  std::vector<RefCountedKinematicParticle> particles;
  for(size_t i = 0; i < tracks.size(); ++i) {
    particles.emplace_back(
      factory.particle(
        tracks.at(i), masses.at(i), kin_chi2_, 
        kin_ndof_, sigmas[i]
        )
      );
  }

  KinematicParticleVertexFitter kcv_fitter;    
  RefCountedKinematicTree vtx_tree = kcv_fitter.fit(particles);

  if (vtx_tree->isEmpty() || !vtx_tree->isValid() || !vtx_tree->isConsistent()) {
    success_ = false; 
    return;
  }

  vtx_tree->movePointerToTheTop(); 
  fitted_particle_ = vtx_tree->currentParticle();
  fitted_vtx_ = vtx_tree->currentDecayVertex();
  if (!fitted_particle_->currentState().isValid() || !fitted_vtx_->vertexIsValid()){ 
    success_ = false; 
    return;
  }
  fitted_state_ = fitted_particle_->currentState();
  fitted_children_ = vtx_tree->finalStateParticles();
  if(fitted_children_.size() != n_particles_) { 
    success_=false; 
    return;
  }
  fitted_track_ = fitted_particle_->refittedTransientTrack();
  success_ = true;
}



KinVtxFitter::KinVtxFitter(const std::vector<reco::TransientTrack> tracks, 
                           const std::vector<double> masses, 
                           std::vector<float> sigmas, ParticleMass dilep_mass):
  n_particles_{masses.size()} {
  
  KinematicParticleFactoryFromTransientTrack factory;
  std::vector<RefCountedKinematicParticle> particles;
  for(size_t i = 0; i < tracks.size(); ++i) {
    particles.emplace_back(
      factory.particle(
        tracks.at(i), masses.at(i), kin_chi2_, 
        kin_ndof_, sigmas[i]
        )
      );
  }

  // BUGFIX: both branches used to re-DECLARE `dilep_const` inside the if/else, shadowing the
  // outer pointer, which therefore stayed UNINITIALISED and was handed to fit() -> undefined
  // behaviour. Also, KinematicConstrainedVertexFitter::fit() takes a MultiTrackKinematicConstraint,
  // so the MassKinematicConstraint branch was the wrong type anyway.
  //
  // TwoTrackMassKinematicConstraint constrains the invariant mass of the FIRST TWO particles in
  // `particles`. So the caller decides WHAT gets constrained purely by ordering: pass
  // {trk1, trk2, lep1, lep2} to constrain a di-track (e.g. phi->KK), or {lep1, lep2, ...} to
  // constrain the dilepton. Applies for any n>=2.
  std::unique_ptr<MultiTrackKinematicConstraint> dilep_const(
      new TwoTrackMassKinematicConstraint(dilep_mass));

  KinematicConstrainedVertexFitter kcv_fitter;
  RefCountedKinematicTree vtx_tree = kcv_fitter.fit(particles, dilep_const.get());

  if (vtx_tree->isEmpty() || !vtx_tree->isValid() || !vtx_tree->isConsistent()) {
    success_ = false; 
    return;
  }

  vtx_tree->movePointerToTheTop(); 
  fitted_particle_ = vtx_tree->currentParticle();
  fitted_vtx_ = vtx_tree->currentDecayVertex();
  if (!fitted_particle_->currentState().isValid() || !fitted_vtx_->vertexIsValid()){ 
    success_ = false; 
    return;
  }
  fitted_state_ = fitted_particle_->currentState();
  fitted_children_ = vtx_tree->finalStateParticles();
  if(fitted_children_.size() != n_particles_) { 
    success_=false; 
    return;
  }
  fitted_track_ = fitted_particle_->refittedTransientTrack();
  success_ = true;
}

