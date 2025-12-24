/////////////////////////////// PentaquarkToJpsiPBuilder ///////////////////////////////
/// Pentaquark search: J/psi + p (proton)
/// Adapted from BToTrkLLBuilder for pentaquark searches (Pc -> J/psi p)

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"

class PentaquarkToJpsiPBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit PentaquarkToJpsiPBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    protons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("protons") )},
    protons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("protonsTransientTracks") )},
    pu_tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("PUtracks"))),
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )},
    dilepton_constraint_{cfg.getParameter<double>("dileptonMassContraint")}
  {
    produces<pat::CompositeCandidateCollection>();
  }

  ~PentaquarkToJpsiPBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:

  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  //selections
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;

  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> protons_;
  const edm::EDGetTokenT<TransientTrackCollection> protons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> pu_tracks_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  const double dilepton_constraint_;
};

void PentaquarkToJpsiPBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> protons;
  evt.getByToken(protons_, protons);
  edm::Handle<TransientTrackCollection> protons_ttracks;
  evt.getByToken(protons_ttracks_, protons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> pu_tracks;
  evt.getByToken(pu_tracks_, pu_tracks);

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  edm::ESHandle<MagneticField> fieldHandle;
  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);

  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());

  for (size_t p_idx = 0; p_idx < protons->size(); ++p_idx) {
    edm::Ptr<pat::CompositeCandidate> p_ptr(protons, p_idx);

    math::PtEtaPhiMLorentzVector p_p4(
      p_ptr->pt(),
      p_ptr->eta(),
      p_ptr->phi(),
      PROTON_MASS
    );

    for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
      edm::Ptr<pat::CompositeCandidate> ll_prt(dileptons, ll_idx);
      edm::Ptr<reco::Candidate> l1_ptr = ll_prt->userCand("l1");
      edm::Ptr<reco::Candidate> l2_ptr = ll_prt->userCand("l2");
      int l1_idx = ll_prt->userInt("l1_idx");
      int l2_idx = ll_prt->userInt("l2_idx");

      pat::CompositeCandidate cand;
      cand.setP4(ll_prt->p4() + p_p4);
      cand.setCharge(ll_prt->charge() + p_ptr->charge());
      
      // Save daughters - unfitted
      cand.addUserCand("l1", l1_ptr);
      cand.addUserCand("l2", l2_ptr);
      cand.addUserCand("proton", p_ptr);
      cand.addUserCand("dilepton", ll_prt);

      cand.addUserInt("l1_idx", l1_idx);
      cand.addUserInt("l2_idx", l2_idx);
      cand.addUserInt("proton_idx", p_idx);
      cand.addUserInt("ll_idx", ll_idx);

      auto dr_info = min_max_dr({l1_ptr, l2_ptr, p_ptr});
      cand.addUserFloat("min_dr", dr_info.first);
      cand.addUserFloat("max_dr", dr_info.second);

      // J/psi + p invariant mass (for Pc search)
      cand.addUserFloat("jpsi_p_mass", (ll_prt->p4() + p_p4).mass());

      if ( !pre_vtx_selection_(cand) ) continue;

      KinVtxFitter fitter(
          { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx),
            protons_ttracks->at(p_idx)
          },
          {l1_ptr->mass(), l2_ptr->mass(), PROTON_MASS},
          {LEP_SIGMA, LEP_SIGMA, PROTON_SIGMA}
          );

      if (!fitter.success()) continue;
      cand.setVertex(
        reco::Candidate::Point(
          fitter.fitted_vtx().x(),
          fitter.fitted_vtx().y(),
          fitter.fitted_vtx().z()
        )
      );
      cand.addUserInt("sv_OK" , fitter.success());
      cand.addUserFloat("sv_chi2", fitter.chi2());
      cand.addUserFloat("sv_ndof", fitter.dof());
      cand.addUserFloat("sv_prob", fitter.prob());
      cand.addUserFloat("fitted_mll" ,
                        (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());
      auto fit_p4 = fitter.fitted_p4();
      cand.addUserFloat("fitted_pt"  , fit_p4.pt());
      cand.addUserFloat("fitted_eta" , fit_p4.eta());
      cand.addUserFloat("fitted_phi" , fit_p4.phi());
      cand.addUserFloat("fitted_mass", fitter.fitted_candidate().mass());
      cand.addUserFloat("fitted_massErr",
                      sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
      
      // J/psi + p fitted mass (Pc candidate mass)
      cand.addUserFloat("fitted_jpsi_p_mass", 
                        (fitter.daughter_p4(0) + fitter.daughter_p4(1) + fitter.daughter_p4(2)).mass());

      cand.addUserFloat("cos_theta_2D",
                        cos_theta_2D(fitter, *beamspot, cand.p4()));
      cand.addUserFloat("fitted_cos_theta_2D",
                        cos_theta_2D(fitter, *beamspot, fit_p4));

      auto lxy = l_xy(fitter, *beamspot);
      cand.addUserFloat("l_xy", lxy.value());
      cand.addUserFloat("l_xy_unc", lxy.error());

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
      std::vector<std::string> dnames{ "l1", "l2", "proton" };

      for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt" ,
                          fitter.daughter_p4(idaughter).pt() );

        cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta",
                          fitter.daughter_p4(idaughter).eta() );

        cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi",
                          fitter.daughter_p4(idaughter).phi() );
      }

      // proton impact parameter from SV
      TrajectoryStateOnSurface tsos = extrapolator.extrapolate(protons_ttracks->at(p_idx).impactPointState(), fitter.fitted_vtx());
      std::pair<bool, Measurement1D> cur2DIP = signedTransverseImpactParameter(tsos, fitter.fitted_refvtx(), *beamspot);
      cand.addUserFloat("proton_svip2d" , cur2DIP.second.value());
      cand.addUserFloat("proton_svip2d_err" , cur2DIP.second.error());

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
          protons_ttracks->at(p_idx)
        },
        {l1_ptr->mass(), l2_ptr->mass(), PROTON_MASS},
        {LEP_SIGMA, LEP_SIGMA, PROTON_SIGMA},
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
          // Constrained J/psi + p mass
          cand.addUserFloat("constraint_jpsi_p_mass",
                            (constraint_fitter.daughter_p4(0) + constraint_fitter.daughter_p4(1) + constraint_fitter.daughter_p4(2)).mass());
        } else {
          cand.addUserFloat("constraint_sv_prob", -99);
          cand.addUserFloat("constraint_pt", -99);
          cand.addUserFloat("constraint_eta", -99);
          cand.addUserFloat("constraint_phi", -99);
          cand.addUserFloat("constraint_mass", -99);
          cand.addUserFloat("constraint_massErr", -99);
          cand.addUserFloat("constraint_mll" , -99);
          cand.addUserFloat("constraint_jpsi_p_mass", -99);
        }
      }

      ret_val->push_back(cand);
    } // for(size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
  } // for(size_t p_idx = 0; p_idx < protons->size(); ++p_idx)


  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(PentaquarkToJpsiPBuilder);
