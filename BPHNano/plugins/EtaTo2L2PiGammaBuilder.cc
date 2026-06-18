////////////////////////////// EtaTo2L2PiGammaBuilder //////////////////////////////
/// authors: Y Lai (Princeton)
// takes the dilepton collection (2 muons for J/Psi), ditrack collection (2 pions), 
// and photon collection (1 or 2 photons) and produces B0->J/Psi(->2muon)+eta(->2pi+photon(s))
// Supports:
// - eta -> 2pi + gamma (direct, nPhotons=1)
// - eta -> 2pi + pi0 -> 2pi + 2gamma (via pi0 decay, nPhotons=2)
// using a four-track vertex (2 muons + 2 pions) with photons added

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/PatCandidates/interface/Photon.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"

class EtaTo2L2PiGammaBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit EtaTo2L2PiGammaBuilder(const edm::ParameterSet &cfg):
    etaMassMin_(cfg.exists("etaMassMin") ? cfg.getParameter<double>("etaMassMin") : 0.),
    etaMassMax_(cfg.exists("etaMassMax") ? cfg.getParameter<double>("etaMassMax") : 999.),
    pi0MassMin_(cfg.exists("pi0MassMin") ? cfg.getParameter<double>("pi0MassMin") : 0.),
    pi0MassMax_(cfg.exists("pi0MassMax") ? cfg.getParameter<double>("pi0MassMax") : 999.),
    jpsiMassMin_(cfg.exists("jpsiMassMin") ? cfg.getParameter<double>("jpsiMassMin") : 0.),
    jpsiMassMax_(cfg.exists("jpsiMassMax") ? cfg.getParameter<double>("jpsiMassMax") : 999.),
    bMassMin_(cfg.exists("bMassMin") ? cfg.getParameter<double>("bMassMin") : 0.),
    bMassMax_(cfg.exists("bMassMax") ? cfg.getParameter<double>("bMassMax") : 999.),
    gammaPairMassMin_(cfg.exists("gammaPairMassMin") ? cfg.getParameter<double>("gammaPairMassMin") : 0.),
    gammaPairMassMax_(cfg.exists("gammaPairMassMax") ? cfg.getParameter<double>("gammaPairMassMax") : 999.),
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    // selections
    trk1_selection_{cfg.getParameter<std::string>("trk1Selection")},
    trk2_selection_{cfg.getParameter<std::string>("trk2Selection")},
    pho1_selection_{cfg.getParameter<std::string>("pho1Selection")},
    pho2_selection_{cfg.exists("pho2Selection") ? cfg.getParameter<std::string>("pho2Selection") : std::string("pt > 0")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    nPhotons_{cfg.getParameter<int>("nPhotons")},  // 1 or 2
    //inputs
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("tracks"))),
    ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    photons_{consumes<pat::PhotonCollection>( cfg.getParameter<edm::InputTag>("photons") )},
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )}
  {
    //output
    produces<pat::CompositeCandidateCollection>();
    if (nPhotons_ != 1 && nPhotons_ != 2) {
      throw cms::Exception("Configuration") << "nPhotons must be 1 or 2, got " << nPhotons_;
    }
  }

  ~EtaTo2L2PiGammaBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:
  double etaMassMin_, etaMassMax_, pi0MassMin_, pi0MassMax_, jpsiMassMin_, jpsiMassMax_, bMassMin_, bMassMax_, gammaPairMassMin_, gammaPairMassMax_;


  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  // selections
  const StringCutObjectSelector<pat::CompositeCandidate> trk1_selection_; // cuts on leading pion
  const StringCutObjectSelector<pat::CompositeCandidate> trk2_selection_; // sub-leading pion
  const StringCutObjectSelector<pat::Photon> pho1_selection_; // cuts on leading photon
  const StringCutObjectSelector<pat::Photon> pho2_selection_; // cuts on sub-leading photon (only for nPhotons=2)
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;
  const int nPhotons_;  // 1 or 2

  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> tracks_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_;
  const edm::EDGetTokenT<pat::PhotonCollection> photons_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;

};

void EtaTo2L2PiGammaBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> tracks;
  evt.getByToken(tracks_, tracks);
  edm::Handle<TransientTrackCollection> ttracks;
  evt.getByToken(ttracks_, ttracks);

  edm::Handle<pat::PhotonCollection> photons;
  evt.getByToken(photons_, photons);

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  edm::ESHandle<MagneticField> fieldHandle;
  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);
  
  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());

  // Loop over all muon pairs (J/Psi candidates)
  for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
    edm::Ptr<pat::CompositeCandidate> ll_ptr(dileptons, ll_idx);
    edm::Ptr<reco::Candidate> l1_ptr = ll_ptr->userCand("l1");
    edm::Ptr<reco::Candidate> l2_ptr = ll_ptr->userCand("l2");
    int l1_idx = ll_ptr->userInt("l1_idx");
    int l2_idx = ll_ptr->userInt("l2_idx");

    // Loop over pion pairs
    for (size_t trk1_idx = 0; trk1_idx < tracks->size(); ++trk1_idx ) {
      edm::Ptr<pat::CompositeCandidate> trk1_ptr( tracks, trk1_idx );
      if (!trk1_selection_(*trk1_ptr)) continue;

      for (size_t trk2_idx = trk1_idx + 1; trk2_idx < tracks->size(); ++trk2_idx) {
        edm::Ptr<pat::CompositeCandidate> trk2_ptr( tracks, trk2_idx );
        if (!trk2_selection_(*trk2_ptr)) continue;

        if ((trk1_ptr->charge() + trk2_ptr->charge()) != 0) continue;

        // Loop over photons (1 or 2 depending on nPhotons_)
        if (nPhotons_ == 1) {
          // Single photon case: eta -> 2pi + gamma
          for (size_t pho1_idx = 0; pho1_idx < photons->size(); ++pho1_idx) {
            edm::Ptr<pat::Photon> pho1_ptr(photons, pho1_idx);
            if (!pho1_selection_(*pho1_ptr)) continue;
            
            // Create a dummy null pointer for pho2 (not used)
            edm::Ptr<pat::Photon> pho2_ptr;
            size_t pho2_idx = 999999;  // invalid index
            
            // Process single photon candidate
            {

            // Build 4-vectors
            math::PtEtaPhiMLorentzVector l1_p4(
                l1_ptr->pt(),
                l1_ptr->eta(),
                l1_ptr->phi(),
                MUON_MASS
            );
            math::PtEtaPhiMLorentzVector l2_p4(
                l2_ptr->pt(),
                l2_ptr->eta(),
                l2_ptr->phi(),
                MUON_MASS
            );
            math::PtEtaPhiMLorentzVector trk1_p4(
                trk1_ptr->pt(),
                trk1_ptr->eta(),
                trk1_ptr->phi(),
                PI_MASS
            );
            math::PtEtaPhiMLorentzVector trk2_p4(
                trk2_ptr->pt(),
                trk2_ptr->eta(),
                trk2_ptr->phi(),
                PI_MASS
            );
            math::PtEtaPhiMLorentzVector pho1_p4(
                pho1_ptr->pt(),
                pho1_ptr->eta(),
                pho1_ptr->phi(),
                0.0  // photon mass = 0
            );
            math::PtEtaPhiMLorentzVector pho2_p4(0, 0, 0, 0);  // zero 4-vector for 1-photon case
            if (nPhotons_ == 2) {
              pho2_p4 = math::PtEtaPhiMLorentzVector(
                  pho2_ptr->pt(),
                  pho2_ptr->eta(),
                  pho2_ptr->phi(),
                  0.0  // photon mass = 0
              );
            }
            
            // J/Psi = l1 + l2
            auto jpsi_p4 = l1_p4 + l2_p4;
            double m_jpsi = jpsi_p4.mass();
            if(m_jpsi < jpsiMassMin_ || m_jpsi > jpsiMassMax_) continue;
            
            // eta = trk1 + trk2 + pho1 (+ pho2 if nPhotons==2)
            auto eta_p4 = trk1_p4 + trk2_p4 + pho1_p4;
            if (nPhotons_ == 2) {
              eta_p4 += pho2_p4;
            }
            double m_eta = eta_p4.mass();
            if(m_eta < etaMassMin_ || m_eta > etaMassMax_) continue;
            // pi0/gamma pair window for nPhotons=2
            if (nPhotons_ == 2) {
              double m_2gamma = (pho1_p4 + pho2_p4).mass();
              if(m_2gamma < pi0MassMin_ || m_2gamma > pi0MassMax_) continue;
            }
            // B0 = J/Psi + eta
            auto b0_p4 = jpsi_p4 + eta_p4;
            double m_b = b0_p4.mass();
            if(m_b < bMassMin_ || m_b > bMassMax_) continue;
            
            // B0 candidate
            pat::CompositeCandidate cand;

            cand.setP4(b0_p4);
            cand.setCharge( l1_ptr->charge() + l2_ptr->charge() + trk1_ptr->charge() + trk2_ptr->charge() );
            
            // save daughters - unfitted
            cand.addUserCand("l1", l1_ptr);
            cand.addUserCand("l2", l2_ptr);
            cand.addUserCand("trk1", trk1_ptr);
            cand.addUserCand("trk2", trk2_ptr);
            cand.addUserCand("pho1", pho1_ptr);
            if (nPhotons_ == 2) {
              cand.addUserCand("pho2", pho2_ptr);
            }
            cand.addUserCand("dilepton", ll_ptr);

            // save indices
            cand.addUserInt("l1_idx", l1_idx);
            cand.addUserInt("l2_idx", l2_idx);
            cand.addUserInt("ll_idx", ll_idx);
            cand.addUserInt("trk1_idx", trk1_idx);
            cand.addUserInt("trk2_idx", trk2_idx);
            cand.addUserInt("pho1_idx", pho1_idx);
            if (nPhotons_ == 2) {
              cand.addUserInt("pho2_idx", pho2_idx);
            } else {
              cand.addUserInt("pho2_idx", -1);  // invalid index for 1-photon case
            }
            cand.addUserInt("nPhotons", nPhotons_);  // store number of photons
            cand.addUserFloat("trk1_mass", trk1_ptr->mass());
            cand.addUserFloat("trk2_mass", trk2_ptr->mass());

            // Calculate intermediate masses
            cand.addUserFloat("m_jpsi", jpsi_p4.mass());
            cand.addUserFloat("m_eta", eta_p4.mass());
            cand.addUserFloat("m_2pi", (trk1_p4 + trk2_p4).mass());
            if (nPhotons_ == 2) {
              cand.addUserFloat("m_2gamma", (pho1_p4 + pho2_p4).mass());
            } else {
              cand.addUserFloat("m_2gamma", -1.0);  // not applicable for 1-photon case
            }

            // Convert photon pointers to Candidate pointers for min_max_dr
            std::vector<edm::Ptr<reco::Candidate>> cands = {l1_ptr, l2_ptr, trk1_ptr, trk2_ptr};
            cands.push_back(edm::Ptr<reco::Candidate>(pho1_ptr));
            if (nPhotons_ == 2) {
              cands.push_back(edm::Ptr<reco::Candidate>(pho2_ptr));
            }
            auto dr_info = min_max_dr(cands);
            cand.addUserFloat("min_dr", dr_info.first);
            cand.addUserFloat("max_dr", dr_info.second);

            // check if pass pre vertex cut
            if ( !pre_vtx_selection_(cand) ) continue;

            // Fit vertex with 4 tracks (2 muons + 2 pions)
            // Photons don't have tracks, so they're not included in the vertex fit
            KinVtxFitter fitter(
              { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx), ttracks->at(trk1_idx), ttracks->at(trk2_idx) },
              { MUON_MASS, MUON_MASS, PI_MASS, PI_MASS},
              { LEP_SIGMA, LEP_SIGMA, PI_SIGMA, PI_SIGMA }
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

            // refitted kinematic vars for tracks
            cand.addUserFloat("fitted_ditrack_mass", 
                            (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());
            cand.addUserFloat("fitted_mll",
                            (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());
            
            // Fitted J/Psi (from fitted muons)
            auto fitted_jpsi_p4 = fitter.daughter_p4(0) + fitter.daughter_p4(1);
            cand.addUserFloat("fitted_m_jpsi", fitted_jpsi_p4.mass());
            
            // Eta from fitted pions + photons (photons not fitted)
            auto fitted_eta_p4 = fitter.daughter_p4(2) + fitter.daughter_p4(3) + pho1_p4;
            if (nPhotons_ == 2) {
              fitted_eta_p4 += pho2_p4;
            }
            cand.addUserFloat("fitted_m_eta", fitted_eta_p4.mass());
            
            // B0 from fitted J/Psi + fitted eta
            auto fitted_b0_p4 = fitted_jpsi_p4 + fitted_eta_p4;
            cand.addUserFloat("fitted_pt", fitted_b0_p4.pt());
            cand.addUserFloat("fitted_eta", fitted_b0_p4.eta());
            cand.addUserFloat("fitted_phi", fitted_b0_p4.phi());
            cand.addUserFloat("fitted_mass", fitted_b0_p4.mass());
            cand.addUserFloat("fitted_massErr",
                            sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
            cand.addUserFloat("fitted_rapidity", fitted_b0_p4.Rapidity());

            // other vars
            cand.addUserFloat("cos_theta_2D",
                            cos_theta_2D(fitter, *beamspot, cand.p4()));

            cand.addUserFloat("fitted_cos_theta_2D",
                            cos_theta_2D(fitter, *beamspot, fitted_b0_p4));

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
            std::vector<std::string> dnames{ "l1", "l2", "trk1", "trk2" };

            for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
              cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt", fitter.daughter_p4(idaughter).pt() );
              cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
              cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
            }
            
            // Photon kinematics (not fitted, use original)
            cand.addUserFloat("fitted_pho1_pt", pho1_p4.pt());
            cand.addUserFloat("fitted_pho1_eta", pho1_p4.eta());
            cand.addUserFloat("fitted_pho1_phi", pho1_p4.phi());
            if (nPhotons_ == 2) {
              cand.addUserFloat("fitted_pho2_pt", pho2_p4.pt());
              cand.addUserFloat("fitted_pho2_eta", pho2_p4.eta());
              cand.addUserFloat("fitted_pho2_phi", pho2_p4.phi());
            } else {
              cand.addUserFloat("fitted_pho2_pt", -1.0);
              cand.addUserFloat("fitted_pho2_eta", -999.0);
              cand.addUserFloat("fitted_pho2_phi", -999.0);
            }

            // track impact parameter from B0 SV
            TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
            std::pair<bool, Measurement1D> cur2DIP1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
            cand.addUserFloat("trk1_svip2d", cur2DIP1.second.value());
            cand.addUserFloat("trk1_svip2d_err", cur2DIP1.second.error());

            TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
            std::pair<bool, Measurement1D> cur2DIP2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
            cand.addUserFloat("trk2_svip2d", cur2DIP2.second.value());
            cand.addUserFloat("trk2_svip2d_err", cur2DIP2.second.error());

            //compute isolation (for tracks only, photons don't have tracks)
            std::vector<float> isos = TrackerIsolation(tracks, cand, dnames);
            for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
              cand.addUserFloat(dnames[idaughter] + "_iso04", isos[idaughter]);
            }

            ret_val->push_back(cand);
            }  // end of single photon processing block
          }  // for (size_t pho1_idx = 0; pho1_idx < photons->size(); ++pho1_idx)
        } else {
          // Two photon case: eta -> 2pi + pi0 -> 2pi + 2gamma
          for (size_t pho1_idx = 0; pho1_idx < photons->size(); ++pho1_idx) {
            edm::Ptr<pat::Photon> pho1_ptr(photons, pho1_idx);
            if (!pho1_selection_(*pho1_ptr)) continue;

            for (size_t pho2_idx = pho1_idx + 1; pho2_idx < photons->size(); ++pho2_idx) {
              edm::Ptr<pat::Photon> pho2_ptr(photons, pho2_idx);
              if (!pho2_selection_(*pho2_ptr)) continue;
              
              // Process two-photon candidate (same processing as 1-photon case, but with pho2)
              // B0 candidate
              pat::CompositeCandidate cand;
              
              // Build 4-vectors
              math::PtEtaPhiMLorentzVector l1_p4(
                  l1_ptr->pt(),
                  l1_ptr->eta(),
                  l1_ptr->phi(),
                  MUON_MASS
              );
              math::PtEtaPhiMLorentzVector l2_p4(
                  l2_ptr->pt(),
                  l2_ptr->eta(),
                  l2_ptr->phi(),
                  MUON_MASS
              );
              math::PtEtaPhiMLorentzVector trk1_p4(
                  trk1_ptr->pt(),
                  trk1_ptr->eta(),
                  trk1_ptr->phi(),
                  PI_MASS
              );
              math::PtEtaPhiMLorentzVector trk2_p4(
                  trk2_ptr->pt(),
                  trk2_ptr->eta(),
                  trk2_ptr->phi(),
                  PI_MASS
              );
              math::PtEtaPhiMLorentzVector pho1_p4(
                  pho1_ptr->pt(),
                  pho1_ptr->eta(),
                  pho1_ptr->phi(),
                  0.0  // photon mass = 0
              );
              math::PtEtaPhiMLorentzVector pho2_p4(
                  pho2_ptr->pt(),
                  pho2_ptr->eta(),
                  pho2_ptr->phi(),
                  0.0  // photon mass = 0
              );
              
              // J/Psi = l1 + l2
              auto jpsi_p4 = l1_p4 + l2_p4;
              // eta = trk1 + trk2 + pho1 + pho2
              auto eta_p4 = trk1_p4 + trk2_p4 + pho1_p4 + pho2_p4;
              // B0 = J/Psi + eta
              auto b0_p4 = jpsi_p4 + eta_p4;
              
              cand.setP4(b0_p4);
              cand.setCharge( l1_ptr->charge() + l2_ptr->charge() + trk1_ptr->charge() + trk2_ptr->charge() );
              
              // save daughters - unfitted
              cand.addUserCand("l1", l1_ptr);
              cand.addUserCand("l2", l2_ptr);
              cand.addUserCand("trk1", trk1_ptr);
              cand.addUserCand("trk2", trk2_ptr);
              cand.addUserCand("pho1", pho1_ptr);
              cand.addUserCand("pho2", pho2_ptr);
              cand.addUserCand("dilepton", ll_ptr);

              // save indices
              cand.addUserInt("l1_idx", l1_idx);
              cand.addUserInt("l2_idx", l2_idx);
              cand.addUserInt("ll_idx", ll_idx);
              cand.addUserInt("trk1_idx", trk1_idx);
              cand.addUserInt("trk2_idx", trk2_idx);
              cand.addUserInt("pho1_idx", pho1_idx);
              cand.addUserInt("pho2_idx", pho2_idx);
              cand.addUserInt("nPhotons", nPhotons_);
              cand.addUserFloat("trk1_mass", trk1_ptr->mass());
              cand.addUserFloat("trk2_mass", trk2_ptr->mass());

              // Calculate intermediate masses
              cand.addUserFloat("m_jpsi", jpsi_p4.mass());
              cand.addUserFloat("m_eta", eta_p4.mass());
              cand.addUserFloat("m_2pi", (trk1_p4 + trk2_p4).mass());
              cand.addUserFloat("m_2gamma", (pho1_p4 + pho2_p4).mass());

              // Convert photon pointers to Candidate pointers for min_max_dr
              std::vector<edm::Ptr<reco::Candidate>> cands = {l1_ptr, l2_ptr, trk1_ptr, trk2_ptr};
              cands.push_back(edm::Ptr<reco::Candidate>(pho1_ptr));
              cands.push_back(edm::Ptr<reco::Candidate>(pho2_ptr));
              auto dr_info = min_max_dr(cands);
              cand.addUserFloat("min_dr", dr_info.first);
              cand.addUserFloat("max_dr", dr_info.second);

              // check if pass pre vertex cut
              if ( !pre_vtx_selection_(cand) ) continue;

              // Fit vertex with 4 tracks (2 muons + 2 pions)
              KinVtxFitter fitter(
                { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx), ttracks->at(trk1_idx), ttracks->at(trk2_idx) },
                { MUON_MASS, MUON_MASS, PI_MASS, PI_MASS},
                { LEP_SIGMA, LEP_SIGMA, PI_SIGMA, PI_SIGMA }
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

              // refitted kinematic vars for tracks
              cand.addUserFloat("fitted_ditrack_mass", 
                              (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());
              cand.addUserFloat("fitted_mll",
                              (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());
              
              // Fitted J/Psi (from fitted muons)
              auto fitted_jpsi_p4 = fitter.daughter_p4(0) + fitter.daughter_p4(1);
              cand.addUserFloat("fitted_m_jpsi", fitted_jpsi_p4.mass());
              
              // Eta from fitted pions + photons (photons not fitted)
              auto fitted_eta_p4 = fitter.daughter_p4(2) + fitter.daughter_p4(3) + pho1_p4 + pho2_p4;
              cand.addUserFloat("fitted_m_eta", fitted_eta_p4.mass());
              
              // B0 from fitted J/Psi + fitted eta
              auto fitted_b0_p4 = fitted_jpsi_p4 + fitted_eta_p4;
              cand.addUserFloat("fitted_pt", fitted_b0_p4.pt());
              cand.addUserFloat("fitted_eta", fitted_b0_p4.eta());
              cand.addUserFloat("fitted_phi", fitted_b0_p4.phi());
              cand.addUserFloat("fitted_mass", fitted_b0_p4.mass());
              cand.addUserFloat("fitted_massErr",
                              sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
              cand.addUserFloat("fitted_rapidity", fitted_b0_p4.Rapidity());

              // other vars
              cand.addUserFloat("cos_theta_2D",
                              cos_theta_2D(fitter, *beamspot, cand.p4()));

              cand.addUserFloat("fitted_cos_theta_2D",
                              cos_theta_2D(fitter, *beamspot, fitted_b0_p4));

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
              std::vector<std::string> dnames{ "l1", "l2", "trk1", "trk2" };

              for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
                cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt", fitter.daughter_p4(idaughter).pt() );
                cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
                cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
              }
              
              // Photon kinematics (not fitted, use original)
              cand.addUserFloat("fitted_pho1_pt", pho1_p4.pt());
              cand.addUserFloat("fitted_pho1_eta", pho1_p4.eta());
              cand.addUserFloat("fitted_pho1_phi", pho1_p4.phi());
              cand.addUserFloat("fitted_pho2_pt", pho2_p4.pt());
              cand.addUserFloat("fitted_pho2_eta", pho2_p4.eta());
              cand.addUserFloat("fitted_pho2_phi", pho2_p4.phi());

              // track impact parameter from B0 SV
              TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
              std::pair<bool, Measurement1D> cur2DIP1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
              cand.addUserFloat("trk1_svip2d", cur2DIP1.second.value());
              cand.addUserFloat("trk1_svip2d_err", cur2DIP1.second.error());

              TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
              std::pair<bool, Measurement1D> cur2DIP2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
              cand.addUserFloat("trk2_svip2d", cur2DIP2.second.value());
              cand.addUserFloat("trk2_svip2d_err", cur2DIP2.second.error());

              //compute isolation (for tracks only, photons don't have tracks)
              std::vector<float> isos = TrackerIsolation(tracks, cand, dnames);
              for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
                cand.addUserFloat(dnames[idaughter] + "_iso04", isos[idaughter]);
              }

              ret_val->push_back(cand);

            } // for (size_t pho2_idx = pho1_idx + 1; pho2_idx < photons->size(); ++pho2_idx)
          } // for (size_t pho1_idx = 0; pho1_idx < photons->size(); ++pho1_idx)
        }  // else (nPhotons_ == 2)
      } // for (size_t trk2_idx = trk2_idx + 1; trk2_idx < tracks->size(); ++trk2_idx)
    } // for (size_t trk1_idx = 0; trk1_idx < tracks->size(); ++trk1_idx)
  } // for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx)

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(EtaTo2L2PiGammaBuilder);

