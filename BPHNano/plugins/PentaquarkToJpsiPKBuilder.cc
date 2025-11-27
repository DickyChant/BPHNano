////////////////////////////// PentaquarkToJpsiPKBuilder //////////////////////////////
/// Pentaquark search: J/psi + p (proton) + K (kaon)
/// For searches of pentaquark states like Pc -> J/psi p K in Lambda_b decays
/// Adapted from BToTrkTrkLLBuilder

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"

class PentaquarkToJpsiPKBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit PentaquarkToJpsiPKBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    // selections
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    //inputs
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    tracks_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("tracks") )},
    tracks_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    pu_tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("PUtracks"))),
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )},
    dilepton_constraint_{cfg.getParameter<double>("dileptonMassContraint")}
  {
    //output
    produces<pat::CompositeCandidateCollection>();
  }

  ~PentaquarkToJpsiPKBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:

  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  // selections
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;

  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> tracks_;
  const edm::EDGetTokenT<TransientTrackCollection> tracks_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> pu_tracks_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  const double dilepton_constraint_;

};

void PentaquarkToJpsiPKBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> tracks;
  evt.getByToken(tracks_, tracks);
  edm::Handle<TransientTrackCollection> tracks_ttracks;
  evt.getByToken(tracks_ttracks_, tracks_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> pu_tracks;
  evt.getByToken(pu_tracks_, pu_tracks);

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  edm::ESHandle<MagneticField> fieldHandle;
  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);


  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());

  // Loop over all track pairs (proton + kaon)
  for (size_t proton_idx = 0; proton_idx < tracks->size(); ++proton_idx) {
    edm::Ptr<pat::CompositeCandidate> proton_ptr(tracks, proton_idx);
    
    // Proton with assumed proton mass
    math::PtEtaPhiMLorentzVector proton_p4(
      proton_ptr->pt(),
      proton_ptr->eta(),
      proton_ptr->phi(),
      PROTON_MASS
    );

    for (size_t kaon_idx = 0; kaon_idx < tracks->size(); ++kaon_idx) {
      if (kaon_idx == proton_idx) continue; // Skip same track
      
      edm::Ptr<pat::CompositeCandidate> kaon_ptr(tracks, kaon_idx);
      
      // Kaon with assumed kaon mass
      math::PtEtaPhiMLorentzVector kaon_p4(
        kaon_ptr->pt(),
        kaon_ptr->eta(),
        kaon_ptr->phi(),
        K_MASS
      );

      for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
        edm::Ptr<pat::CompositeCandidate> ll_ptr(dileptons, ll_idx);
        edm::Ptr<reco::Candidate> l1_ptr = ll_ptr->userCand("l1");
        edm::Ptr<reco::Candidate> l2_ptr = ll_ptr->userCand("l2");
        int l1_idx = ll_ptr->userInt("l1_idx");
        int l2_idx = ll_ptr->userInt("l2_idx");

        // Lambda_b candidate (or pentaquark search candidate)
        pat::CompositeCandidate cand;
        cand.setP4(ll_ptr->p4() + proton_p4 + kaon_p4);
        cand.setCharge( l1_ptr->charge() + l2_ptr->charge() + proton_ptr->charge() + kaon_ptr->charge() );

        // save daughters - unfitted
        cand.addUserCand("l1", l1_ptr);
        cand.addUserCand("l2", l2_ptr);
        cand.addUserCand("proton", proton_ptr);
        cand.addUserCand("kaon", kaon_ptr);
        cand.addUserCand("dilepton", ll_ptr);

        // save indices
        cand.addUserInt("l1_idx", l1_idx);
        cand.addUserInt("l2_idx", l2_idx);
        cand.addUserInt("proton_idx", proton_idx);
        cand.addUserInt("kaon_idx", kaon_idx);
        cand.addUserInt("ll_idx", ll_idx);

        auto dr_info = min_max_dr({l1_ptr, l2_ptr, proton_ptr, kaon_ptr});
        cand.addUserFloat("min_dr", dr_info.first);
        cand.addUserFloat("max_dr", dr_info.second);

        // J/psi + p invariant mass (Pc candidate mass before fit)
        cand.addUserFloat("jpsi_p_mass", (ll_ptr->p4() + proton_p4).mass());
        // J/psi + K invariant mass
        cand.addUserFloat("jpsi_k_mass", (ll_ptr->p4() + kaon_p4).mass());
        // p + K invariant mass
        cand.addUserFloat("p_k_mass", (proton_p4 + kaon_p4).mass());

        // check if pass pre vertex cut
        if ( !pre_vtx_selection_(cand) ) continue;

        KinVtxFitter fitter(
          { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx),
            tracks_ttracks->at(proton_idx), tracks_ttracks->at(kaon_idx)
          },
          { l1_ptr->mass(), l2_ptr->mass(), PROTON_MASS, K_MASS },
          { LEP_SIGMA, LEP_SIGMA, PROTON_SIGMA, K_SIGMA }
          );

        if (!fitter.success()) continue;

        // Candidate position
        cand.setVertex(
          reco::Candidate::Point(
            fitter.fitted_vtx().x(),
            fitter.fitted_vtx().y(),
            fitter.fitted_vtx().z()
          )
        );

        // vertex vars
        cand.addUserFloat("sv_chi2", fitter.chi2());
        cand.addUserFloat("sv_ndof", fitter.dof());
        cand.addUserFloat("sv_prob", fitter.prob());

        // refitted kinematic vars
        // J/psi + p fitted mass (Pc candidate)
        cand.addUserFloat("fitted_jpsi_p_mass",
                          (fitter.daughter_p4(0) + fitter.daughter_p4(1) + fitter.daughter_p4(2)).mass() );
        // J/psi + K fitted mass
        cand.addUserFloat("fitted_jpsi_k_mass",
                          (fitter.daughter_p4(0) + fitter.daughter_p4(1) + fitter.daughter_p4(3)).mass() );
        // p + K fitted mass
        cand.addUserFloat("fitted_p_k_mass",
                          (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass() );
        // J/psi fitted mass
        cand.addUserFloat("fitted_mll",
                          (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());

        auto fit_p4 = fitter.fitted_p4();
        cand.addUserFloat("fitted_pt"  , fit_p4.pt());
        cand.addUserFloat("fitted_eta" , fit_p4.eta());
        cand.addUserFloat("fitted_phi" , fit_p4.phi());
        cand.addUserFloat("fitted_mass", fit_p4.mass());
        cand.addUserFloat("fitted_massErr",
                          sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));

        // other vars
        cand.addUserFloat("cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, cand.p4()));

        cand.addUserFloat("fitted_cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, fit_p4));

        auto lxy = l_xy(fitter, *beamspot);
        cand.addUserFloat("l_xy", lxy.value());
        cand.addUserFloat("l_xy_unc", lxy.error());

        // post fit selection
        if ( !post_vtx_selection_(cand) ) continue;

        cand.addUserFloat("vtx_x", cand.vx());
        cand.addUserFloat("vtx_y", cand.vy());
        cand.addUserFloat("vtx_z", cand.vz());

        const auto& covMatrix = fitter.fitted_vtx_uncertainty();
        cand.addUserFloat("vtx_cxx", covMatrix.cxx());
        cand.addUserFloat("vtx_cyy", covMatrix.cyy());
        cand.addUserFloat("vtx_czz", covMatrix.czz());
        cand.addUserFloat("vtx_cyx", covMatrix.cyx());
        cand.addUserFloat("vtx_czx", covMatrix.czx());
        cand.addUserFloat("vtx_czy", covMatrix.czy());

        // refitted daughters (leptons/tracks)
        std::vector<std::string> dnames{ "l1", "l2", "proton", "kaon" };

        for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt" , fitter.daughter_p4(idaughter).pt() );
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
        }

        // track impact parameter from SV
        TrajectoryStateOnSurface tsos_p = extrapolator.extrapolate(tracks_ttracks->at(proton_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> cur2DIP_p = signedTransverseImpactParameter(tsos_p, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("proton_svip2d" , cur2DIP_p.second.value());
        cand.addUserFloat("proton_svip2d_err" , cur2DIP_p.second.error());

        TrajectoryStateOnSurface tsos_k = extrapolator.extrapolate(tracks_ttracks->at(kaon_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> cur2DIP_k = signedTransverseImpactParameter(tsos_k, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("kaon_svip2d" , cur2DIP_k.second.value());
        cand.addUserFloat("kaon_svip2d_err" , cur2DIP_k.second.error());

        //compute isolation
        std::vector<float> isos = TrackerIsolation(pu_tracks, cand, dnames );
        for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
          cand.addUserFloat(dnames[idaughter] + "_iso04", isos[idaughter]);
        }

        if (dilepton_constraint_ > 0) {
          ParticleMass dilep_mass = dilepton_constraint_;
          // Mass constraint is applied to the first two particles in the "particles" vector
          // Make sure that the first two particles are the ones you want to constrain
          KinVtxFitter constraint_fitter(
              { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx),
                tracks_ttracks->at(proton_idx), tracks_ttracks->at(kaon_idx)
              },
              { l1_ptr->mass(), l2_ptr->mass(), PROTON_MASS, K_MASS },
              { LEP_SIGMA, LEP_SIGMA, PROTON_SIGMA, K_SIGMA },
              dilep_mass);

          if (constraint_fitter.success()) {
            auto constraint_p4 = constraint_fitter.fitted_p4();
            cand.addUserFloat("constraint_sv_prob", constraint_fitter.prob());
            cand.addUserFloat("constraint_pt", constraint_p4.pt());
            cand.addUserFloat("constraint_eta", constraint_p4.eta());
            cand.addUserFloat("constraint_phi", constraint_p4.phi());
            cand.addUserFloat("constraint_mass", constraint_fitter.fitted_candidate().mass());
            cand.addUserFloat("constraint_massErr",
                              sqrt(constraint_fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
            cand.addUserFloat("constraint_mll" ,
                              (constraint_fitter.daughter_p4(0) + constraint_fitter.daughter_p4(1)).mass());
            // Constrained J/psi + p mass (Pc)
            cand.addUserFloat("constraint_jpsi_p_mass",
                              (constraint_fitter.daughter_p4(0) + constraint_fitter.daughter_p4(1) + constraint_fitter.daughter_p4(2)).mass());
            // Constrained J/psi + K mass
            cand.addUserFloat("constraint_jpsi_k_mass",
                              (constraint_fitter.daughter_p4(0) + constraint_fitter.daughter_p4(1) + constraint_fitter.daughter_p4(3)).mass());
            // Constrained p + K mass
            cand.addUserFloat("constraint_p_k_mass",
                              (constraint_fitter.daughter_p4(2) + constraint_fitter.daughter_p4(3)).mass());
          } else {
            cand.addUserFloat("constraint_sv_prob", -99);
            cand.addUserFloat("constraint_pt", -99);
            cand.addUserFloat("constraint_eta", -99);
            cand.addUserFloat("constraint_phi", -99);
            cand.addUserFloat("constraint_mass", -99);
            cand.addUserFloat("constraint_massErr", -99);
            cand.addUserFloat("constraint_mll" , -99);
            cand.addUserFloat("constraint_jpsi_p_mass", -99);
            cand.addUserFloat("constraint_jpsi_k_mass", -99);
            cand.addUserFloat("constraint_p_k_mass", -99);
          }
        }

        ret_val->push_back(cand);

      } // for(size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {

    } // for(size_t kaon_idx = 0; kaon_idx < tracks->size(); ++kaon_idx)

  } // for(size_t proton_idx = 0; proton_idx < tracks->size(); ++proton_idx)

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(PentaquarkToJpsiPKBuilder);
