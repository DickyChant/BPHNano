/// Bc+ -> (mu mu) Ds+,  Ds+ -> phi(K+ K-) pi+
///
/// Built from BToTrkTrkLLBuilder, which fits dilepton + ditrack (4 tracks); this adds
/// the bachelor pion for a 5-track Bc vertex.
///
/// One build covers all three lines of interest because the dimuon mass is left free:
///     Bc+ -> J/psi Ds(*)+      m(mumu) at 3.0969
///     Bc+ -> psi(2S) Ds(*)+    m(mumu) at 3.6861
///     Bc+ -> mu mu Ds(*)+      m(mumu) continuum, up to m(Bc)-m(Ds) = 4.307
/// so the resonant modes and the rare non-resonant search share one campaign, and the
/// resonant ones normalise the search.  J/psi Ds+ additionally gives the Bc yield in
/// our own data, which is what turns the Bc -> J/psi Lambda~ p limit from an event
/// count into a branching-fraction ratio.
///
/// Ds*+ needs NO extra code: Ds*+ -> Ds+ gamma with the photon unreconstructed appears
/// as a satellite ~150 MeV below the Bc in m(mumu K K pi).  The Bc mass window is kept
/// wide enough downward to retain it rather than cutting it away.
///
/// The phi arrives as a DiTrack candidate (both tracks given the kaon mass); the
/// bachelor pion is taken from the track collection, with an explicit overlap check
/// against the two phi kaons -- without it the same track can be used twice.

////////////////////////////// BcToDsLLBuilder //////////////////////////////
/// original authors: G Karathanasis (CERN),  G Melachroinos (NKUA)
// takes the ditrack collection and a dilepton collection and produces B moth
// - ers using a four-track vertex

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

class BcToDsLLBuilder : public edm::global::EDProducer<> {

  // perhaps we need better structure here (begin run etc)
public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit BcToDsLLBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    // selections
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    //inputs
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    // dileptons_kinVtxs_{consumes<std::vector<KinVtxFitter> >( cfg.getParameter<edm::InputTag>("dileptonKinVtxs") )},
    kstars_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("ditracks") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    kstars_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    pions_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("pions") )},
    pions_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("pionsTransientTracks") )},
    pion_mass_{cfg.getParameter<double>("pionMass")},
    pu_tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("PUtracks"))),
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )},
    dilepton_constraint_{cfg.getParameter<double>("dileptonMassContraint")}
  {
    //output
    produces<pat::CompositeCandidateCollection>();
  }

  ~BcToDsLLBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:

  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  // selections
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;

  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  //const edm::EDGetTokenT<std::vector<KinVtxFitter> > dileptons_kinVtxs_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> kstars_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<TransientTrackCollection> kstars_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> pions_;
  const edm::EDGetTokenT<TransientTrackCollection> pions_ttracks_;
  const double pion_mass_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> pu_tracks_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  const double dilepton_constraint_;

};

void BcToDsLLBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
// edm::Handle<std::vector<KinVtxFitter> > dileptons_kinVtxs;
//  evt.getByToken(dileptons_kinVtxs_, dileptons_kinVtxs);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> kstars;
  evt.getByToken(kstars_, kstars);
  edm::Handle<TransientTrackCollection> kstars_ttracks;
  evt.getByToken(kstars_ttracks_, kstars_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> pions;
  evt.getByToken(pions_, pions);
  edm::Handle<TransientTrackCollection> pions_ttracks;
  evt.getByToken(pions_ttracks_, pions_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> pu_tracks;
  evt.getByToken(pu_tracks_, pu_tracks);

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  edm::ESHandle<MagneticField> fieldHandle;
  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);


  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());


  for (size_t kstar_idx = 0; kstar_idx < kstars->size(); ++kstar_idx) {
    // both k* and lep pair already passed cuts; no need for more preselection
    edm::Ptr<pat::CompositeCandidate> kstar_ptr(kstars, kstar_idx);
    edm::Ptr<reco::Candidate> trk1_ptr = kstar_ptr->userCand("trk1");
    edm::Ptr<reco::Candidate> trk2_ptr = kstar_ptr->userCand("trk2");
    int trk1_idx = kstar_ptr->userInt("trk1_idx");
    int trk2_idx = kstar_ptr->userInt("trk2_idx");

    for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
      edm::Ptr<pat::CompositeCandidate> ll_ptr(dileptons, ll_idx);
      edm::Ptr<reco::Candidate> l1_ptr = ll_ptr->userCand("l1");
      edm::Ptr<reco::Candidate> l2_ptr = ll_ptr->userCand("l2");
      int l1_idx = ll_ptr->userInt("l1_idx");
      int l2_idx = ll_ptr->userInt("l2_idx");

      // B0 candidate
      // ---- bachelor pion loop: the third hadron that completes the Ds+ ----
      for (size_t pi_idx = 0; pi_idx < pions->size(); ++pi_idx) {
      edm::Ptr<pat::CompositeCandidate> pi_ptr(pions, pi_idx);

      // OVERLAP REMOVAL: the bachelor must not be one of the two phi kaons.
      // Without this the same track enters the fit twice and produces a fake Ds.
      if ((int)pi_idx == trk1_idx || (int)pi_idx == trk2_idx) continue;

      pat::CompositeCandidate cand;
      math::PtEtaPhiMLorentzVector pi_p4(pi_ptr->pt(), pi_ptr->eta(), pi_ptr->phi(), pion_mass_);
      cand.setP4(ll_ptr->p4() + kstar_ptr->p4() + pi_p4);
      // Bc+ = mu+ mu- K+ K- pi+  ->  |Q| = 1
      cand.setCharge( l1_ptr->charge() + l2_ptr->charge()
                      + trk1_ptr->charge() + trk2_ptr->charge() + pi_ptr->charge() );

      // save daughters - unfitted
      cand.addUserCand("l1", l1_ptr);
      cand.addUserCand("l2", l2_ptr);
      cand.addUserCand("trk1", trk1_ptr);
      cand.addUserCand("trk2", trk2_ptr);
      cand.addUserCand("pi", pi_ptr);
      cand.addUserCand("kstar", kstar_ptr);
      cand.addUserCand("dilepton", ll_ptr);

      // save indices
      cand.addUserInt("l1_idx", l1_idx);
      cand.addUserInt("l2_idx", l2_idx);
      cand.addUserInt("trk1_idx", trk1_idx);
      cand.addUserInt("trk2_idx", trk2_idx);
      cand.addUserInt("pi_idx", pi_idx);
      cand.addUserInt("kstar_idx" , kstar_idx);
      cand.addUserFloat("trk1_mass", kstar_ptr->userFloat("trk1_mass"));
      cand.addUserFloat("trk2_mass", kstar_ptr->userFloat("trk2_mass"));
      cand.addUserInt("second_mass_hypothesis" , kstar_ptr->userInt("second_mass_hypothesis"));

      auto dr_info = min_max_dr({l1_ptr, l2_ptr, trk1_ptr, trk2_ptr, pi_ptr});
      cand.addUserFloat("min_dr", dr_info.first);
      cand.addUserFloat("max_dr", dr_info.second);


      // check if pass pre vertex cut
      if ( !pre_vtx_selection_(cand) ) continue;

      KinVtxFitter fitter(
        { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx),
          kstars_ttracks->at(trk1_idx), kstars_ttracks->at(trk2_idx),
          pions_ttracks->at(pi_idx)
        },
        { l1_ptr->mass(), l2_ptr->mass(), kstar_ptr->userFloat("trk1_mass"),
          kstar_ptr->userFloat("trk2_mass"), pion_mass_
        },
        { LEP_SIGMA, LEP_SIGMA, K_SIGMA, K_SIGMA, K_SIGMA }
        );

      if (!fitter.success()) continue;

      // B0 position
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
      // m(K K)   -> the phi, confirms the Ds sub-resonance
      cand.addUserFloat("fitted_ditrack_mass",
                        (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass() );
      // m(K K pi) -> the Ds+ itself; cut on this offline, it is the charm tag
      cand.addUserFloat("fitted_ds_mass",
                        (fitter.daughter_p4(2) + fitter.daughter_p4(3)
                         + fitter.daughter_p4(4)).mass() );
      cand.addUserFloat("fitted_pi_pt",  fitter.daughter_p4(4).pt());
      cand.addUserFloat("fitted_pi_eta", fitter.daughter_p4(4).eta());
      cand.addUserFloat("fitted_pi_phi", fitter.daughter_p4(4).phi());
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
      std::vector<std::string> dnames{ "l1", "l2", "trk1", "trk2", "pi" };

      for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt" , fitter.daughter_p4(idaughter).pt() );
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
        cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
      }

      // track impact parameter from dilepton SV
      TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(kstars_ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
      std::pair<bool, Measurement1D> cur2DIP1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
      cand.addUserFloat("trk1_svip2d" , cur2DIP1.second.value());
      cand.addUserFloat("trk1_svip2d_err" , cur2DIP1.second.error());

      TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(kstars_ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
      std::pair<bool, Measurement1D> cur2DIP2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
      cand.addUserFloat("trk2_svip2d" , cur2DIP2.second.value());
      cand.addUserFloat("trk2_svip2d_err" , cur2DIP2.second.error());

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
              kstars_ttracks->at(trk1_idx), kstars_ttracks->at(trk2_idx),
              pions_ttracks->at(pi_idx)
            },
            { l1_ptr->mass(), l2_ptr->mass(),
              kstar_ptr->userFloat("trk1_mass"), kstar_ptr->userFloat("trk2_mass"),
              pion_mass_
            },
            { LEP_SIGMA, LEP_SIGMA, K_SIGMA, K_SIGMA, K_SIGMA },
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
        } else {
          cand.addUserFloat("constraint_sv_prob", -99);
          cand.addUserFloat("constraint_pt", -99);
          cand.addUserFloat("constraint_eta", -99);
          cand.addUserFloat("constraint_phi", -99);
          cand.addUserFloat("constraint_mass", -99);
          cand.addUserFloat("constraint_massErr", -99);
          cand.addUserFloat("constraint_mll" , -99);
        }
      }

      ret_val->push_back(cand);

      } // for(size_t pi_idx = 0; pi_idx < pions->size(); ++pi_idx)

    } // for(size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {

  } // for(size_t k_idx = 0; k_idx < kstars->size(); ++k_idx)

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(BcToDsLLBuilder);
