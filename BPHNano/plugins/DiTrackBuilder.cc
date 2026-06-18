/////////////////////////////// DiTrackBuilder ///////////////////////////////
/// original authors: G Karathanasis (CERN),  G Melachroinos (NKUA)
// takes selected track collection and a mass hypothesis and produces ditrack ca
// -ndidates



#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "TrackingTools/PatternTools/interface/ClosestApproachInRPhi.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"




class DiTrackBuilder : public edm::global::EDProducer<> {


public:

  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit DiTrackBuilder(const edm::ParameterSet &cfg):
    trk1_selection_{cfg.getParameter<std::string>("trk1Selection")},
    trk2_selection_{cfg.getParameter<std::string>("trk2Selection")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    pfcands_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("tracks") )},
    ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )},
    trk1_mass_{ cfg.getParameter<double>("trk1Mass")},
    trk2_mass_{ cfg.getParameter<double>("trk2Mass")}
  {

    //output
    produces<pat::CompositeCandidateCollection>("SelectedLambdaCollection");
    produces<TransientTrackCollection>("SelectedLambda");
  }

  ~DiTrackBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:
  const StringCutObjectSelector<pat::CompositeCandidate> trk1_selection_; // cuts on leading cand
  const StringCutObjectSelector<pat::CompositeCandidate> trk2_selection_; // sub-leading cand
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_; // cut on the di-lepton before the SV fit
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_; // cut on the di-lepton after the SV fit
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> pfcands_; //input PF cands this is sorted in pT in previous step
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_; //input TTracks of PF cands
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  double trk1_mass_;
  double trk2_mass_;
};


void DiTrackBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &) const {

  //inputs
  edm::Handle<pat::CompositeCandidateCollection> pfcands;
  evt.getByToken(pfcands_, pfcands);
  edm::Handle<TransientTrackCollection> ttracks;
  evt.getByToken(ttracks_, ttracks);
  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  // output
  std::unique_ptr<pat::CompositeCandidateCollection> kstar_out(new pat::CompositeCandidateCollection());
  std::unique_ptr<TransientTrackCollection> trans_out( new TransientTrackCollection );


  // main loop
  for (size_t trk1_idx = 0; trk1_idx < pfcands->size(); ++trk1_idx ) {

    edm::Ptr<pat::CompositeCandidate> trk1_ptr( pfcands, trk1_idx );
    if (!trk1_selection_(*trk1_ptr)) continue;

    for (size_t trk2_idx = trk1_idx + 1; trk2_idx < pfcands->size(); ++trk2_idx) {

      edm::Ptr<pat::CompositeCandidate> trk2_ptr( pfcands, trk2_idx );
      if (!trk2_selection_(*trk2_ptr)) continue;
        
      if ((trk1_ptr->charge() + trk2_ptr->charge())!=0) continue;

      // trk1 should have higher pT, and assume it to be proton
      //if(trk1_ptr->pt()<trk2_ptr->pt()){
      //    std::cout<<"trk 1, 2 pt: "<< trk1_ptr->pt()<<" "<< trk2_ptr->pt()<<std::endl;
      //    continue;
      //}

      // Loop in all possible hypothesis
      // for ( std::pair<double, double> masses : { std::pair<double, double>(trk1_mass_, trk2_mass_), std::pair<double, double>(trk2_mass_, trk1_mass_) } ) {
      for ( std::pair<double, double> masses : { std::pair<double, double>(trk1_mass_, trk2_mass_)} ) {

        // create a lambda candidate; add first quantities that can be used for pre fit selection
        pat::CompositeCandidate kstar_cand;
        auto trk1_p4 = trk1_ptr->polarP4();
        auto trk2_p4 = trk2_ptr->polarP4();
        trk1_p4.SetM(masses.first);
        trk2_p4.SetM(masses.second);
        //adding stuff for pre fit selection
        kstar_cand.setP4(trk1_p4 + trk2_p4);
        kstar_cand.setCharge(trk1_ptr->charge() + trk2_ptr->charge());
        kstar_cand.addUserFloat("trk_deltaR", reco::deltaR(*trk1_ptr, *trk2_ptr));
        // save indices
        kstar_cand.addUserInt("trk1_idx", trk1_idx );
        kstar_cand.addUserInt("trk2_idx", trk2_idx );
        kstar_cand.addUserFloat("trk1_mass", masses.first);
        kstar_cand.addUserFloat("trk2_mass", masses.second);
        kstar_cand.addUserFloat("trk1_charge", trk1_ptr->charge());
        kstar_cand.addUserFloat("trk2_charge", trk2_ptr->charge());
        // save cands
        kstar_cand.addUserCand("trk1", trk1_ptr );
        kstar_cand.addUserCand("trk2", trk2_ptr );
        // selection before fit
        if ( !pre_vtx_selection_(kstar_cand) ) continue;
        
	//std::cout<<"---> Before fit, trk1 "<<trk1_idx<<" trk2 "<<trk2_idx<<" dr "<< reco::deltaR(*trk1_ptr, *trk2_ptr)<<" pt1 "<<trk1_p4.pt()<<" pt2 "<<trk2_p4.pt()<<" mass "<<(trk1_p4+trk2_p4).mass()<<std::endl;
        
	KinVtxFitter fitter(
            {ttracks->at(trk1_idx), ttracks->at(trk2_idx)},
            { masses.first, masses.second },
            {K_SIGMA, K_SIGMA} //K and PI sigma equal...
                           );

	//std::cout<<"Pass fit"<<std::endl;

        if ( !fitter.success() ) continue;
        kstar_cand.setVertex(
          reco::Candidate::Point(
            fitter.fitted_vtx().x(),
            fitter.fitted_vtx().y(),
            fitter.fitted_vtx().z()
          )
        );
        // save quantities after fit
        kstar_cand.addUserInt("sv_ok", fitter.success() ? 1 : 0);
        kstar_cand.addUserFloat("sv_chi2", fitter.chi2());
        kstar_cand.addUserFloat("sv_ndof", fitter.dof());
        kstar_cand.addUserFloat("sv_prob", fitter.prob());
        kstar_cand.addUserFloat("fitted_mass", fitter.fitted_candidate().mass() );
        kstar_cand.addUserFloat("fitted_massErr", sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)) );
        kstar_cand.addUserFloat("fitted_pt",
                                fitter.fitted_candidate().globalMomentum().perp() );

        kstar_cand.addUserFloat("fitted_eta",
                                fitter.fitted_candidate().globalMomentum().eta() );

        kstar_cand.addUserFloat("fitted_phi",
                                fitter.fitted_candidate().globalMomentum().phi() );

        kstar_cand.addUserFloat("vtx_x", kstar_cand.vx());
        kstar_cand.addUserFloat("vtx_y", kstar_cand.vy());
        kstar_cand.addUserFloat("vtx_z", kstar_cand.vz());
	auto fit_p4 = fitter.fitted_p4();

        kstar_cand.addUserFloat("cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, kstar_cand.p4()));
        kstar_cand.addUserFloat("fitted_cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, fit_p4));
        auto lxy = l_xy(fitter, *beamspot);
        kstar_cand.addUserFloat("l_xy", lxy.value());
        kstar_cand.addUserFloat("l_xy_unc", lxy.error());

        // after fit selection
        if ( !post_vtx_selection_(kstar_cand) ) continue;

        const auto& posImpact = ttracks->at(trk1_idx).impactPointTSCP();
        const auto& negImpact = ttracks->at(trk2_idx).impactPointTSCP();
        if (!posImpact.isValid() || !negImpact.isValid()) continue;
        FreeTrajectoryState const& posState = posImpact.theState();
        FreeTrajectoryState const& negState = negImpact.theState();
        ClosestApproachInRPhi cApp;
        cApp.calculate(posState, negState);
        if (!cApp.status()) continue;
        //  the distance between the two trajectories at their closest approach in R-phi
        float dca = std::abs(cApp.distance());
        kstar_cand.addUserFloat("dca", dca);

        // Ks0 hypothesis
        KinVtxFitter fitter_ks0(
            {ttracks->at(trk1_idx), ttracks->at(trk2_idx)},
            { PI_MASS, PI_MASS },
            {PI_SIGMA, PI_SIGMA}
                           );
        if ( fitter_ks0.success() ){
		kstar_cand.addUserFloat("fitted_ks0_mass", fitter_ks0.fitted_candidate().mass() );
		kstar_cand.addUserFloat("fitted_ks0_massErr", sqrt(fitter_ks0.fitted_candidate().kinematicParametersError().matrix()(6, 6)) );
        }else{
		kstar_cand.addUserFloat("fitted_ks0_mass", -1);
		kstar_cand.addUserFloat("fitted_ks0_massErr", -1);
	}

        kstar_out->emplace_back(kstar_cand);
        auto V0TT = fitter.fitted_candidate_ttrk();
        trans_out->emplace_back(V0TT);

      } // end for ( auto & masses:
    } // end for(size_t trk2_idx = trk1_idx + 1
  } //for(size_t trk1_idx = 0

  evt.put(std::move(kstar_out), "SelectedLambdaCollection");
  evt.put(std::move(trans_out), "SelectedLambda");
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(DiTrackBuilder);
