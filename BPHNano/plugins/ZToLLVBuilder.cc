////////////////////////////// ZToLLVBuilder //////////////////////////////
// Z -> l+ l- V  with  V -> h+ h-  (a vector meson reconstructed as two charged tracks).
//   - lepton hypothesis (mu or e) is configurable via lepMass/lepSigma
//   - track  hypothesis (pi for rho, K for phi, ...) via trkMass/trkSigma
//   - the di-track mass window selects the vector meson (rho ~0.5-1.0, phi ~1.00-1.04)
//   - the 4-track common-vertex fit + a PROMPT requirement (cos_theta_2D ~ 1, small l_xy)
//     suppress Drell-Yan l+l- + 2 random/displaced tracks
//   - the full l+l-h+h- mass is required near the Z (skim window in the cff)
// Structure mirrors EtaTo2L2PiBuilder (Y. Lai) with the masses promoted to parameters.

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

class ZToLLVBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit ZToLLVBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    // mass hypotheses (lepton = mu/e, track = pi/K)
    lep_mass_{cfg.getParameter<double>("lepMass")},
    lep_sigma_{cfg.getParameter<double>("lepSigma")},
    trk_mass_{cfg.getParameter<double>("trkMass")},
    trk_sigma_{cfg.getParameter<double>("trkSigma")},
    mass_constraint_{cfg.getParameter<std::string>("massConstraint")},
    constraint_mass_{cfg.getParameter<double>("constraintMass")},
    v_mass_min_{cfg.getParameter<double>("vMassMin")},
    v_mass_max_{cfg.getParameter<double>("vMassMax")},
    // selections
    trk1_selection_{cfg.getParameter<std::string>("trk1Selection")},
    trk2_selection_{cfg.getParameter<std::string>("trk2Selection")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    //inputs
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("tracks"))),
    ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )}
  {
    produces<pat::CompositeCandidateCollection>();
  }

  ~ZToLLVBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:

  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;

  // mass hypotheses
  const double lep_mass_;
  const double lep_sigma_;
  const double trk_mass_;
  const double trk_sigma_;
  // "none" | "ditrack" (constrain m(KK)->phi) | "dilepton" (constrain m(mumu)->J/psi).
  // TwoTrackMassKinematicConstraint always constrains the FIRST TWO particles, so the
  // mode simply decides the ordering handed to the fitter.
  const std::string mass_constraint_;
  const double      constraint_mass_;
  const double v_mass_min_;   // di-track (V) mass window, applied EARLY (before cand build)
  const double v_mass_max_;

  // selections
  const StringCutObjectSelector<pat::CompositeCandidate> trk1_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> trk2_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;

  // inputs
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> tracks_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
};

void ZToLLVBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> tracks;
  evt.getByToken(tracks_, tracks);
  edm::Handle<TransientTrackCollection> ttracks;
  evt.getByToken(ttracks_, ttracks);

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);

  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());

  for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
    edm::Ptr<pat::CompositeCandidate> ll_ptr(dileptons, ll_idx);
    edm::Ptr<reco::Candidate> l1_ptr = ll_ptr->userCand("l1");
    edm::Ptr<reco::Candidate> l2_ptr = ll_ptr->userCand("l2");
    int l1_idx = ll_ptr->userInt("l1_idx");
    int l2_idx = ll_ptr->userInt("l2_idx");

    // per-dimuon lepton 4-vectors (hoisted OUT of the track loops)
    math::PtEtaPhiMLorentzVector l1_p4(l1_ptr->pt(), l1_ptr->eta(), l1_ptr->phi(), lep_mass_);
    math::PtEtaPhiMLorentzVector l2_p4(l2_ptr->pt(), l2_ptr->eta(), l2_ptr->phi(), lep_mass_);
    auto dilep_p4 = l1_p4 + l2_p4;

    for (size_t trk1_idx = 0; trk1_idx < tracks->size(); ++trk1_idx ) {
      edm::Ptr<pat::CompositeCandidate> trk1_ptr( tracks, trk1_idx );
      if (!trk1_selection_(*trk1_ptr)) continue;
      math::PtEtaPhiMLorentzVector trk1_p4(trk1_ptr->pt(), trk1_ptr->eta(), trk1_ptr->phi(), trk_mass_);

      for (size_t trk2_idx = trk1_idx + 1; trk2_idx < tracks->size(); ++trk2_idx) {
        edm::Ptr<pat::CompositeCandidate> trk2_ptr( tracks, trk2_idx );
        if (!trk2_selection_(*trk2_ptr)) continue;
        // V -> h+ h- : opposite charge tracks
        if ((trk1_ptr->charge() + trk2_ptr->charge()) != 0) continue;

        math::PtEtaPhiMLorentzVector trk2_p4(trk2_ptr->pt(), trk2_ptr->eta(), trk2_ptr->phi(), trk_mass_);
        auto ditrack_p4 = trk1_p4 + trk2_p4;
        const float m_ditrack = ditrack_p4.mass();
        // EARLY V-mass window cut: skip the (expensive) candidate build + 4-track vertex fit for
        // di-track pairs outside the rho/phi window. This is what keeps the combinatorics bounded
        // (the candidate-building string/map ops dominate otherwise).
        if (m_ditrack < v_mass_min_ || m_ditrack > v_mass_max_) continue;

        auto cand_p4 = dilep_p4 + ditrack_p4;
        pat::CompositeCandidate cand;
        cand.setP4(cand_p4);
        cand.setCharge( l1_ptr->charge() + l2_ptr->charge() + trk1_ptr->charge() + trk2_ptr->charge() );

        // save daughters - unfitted
        cand.addUserCand("l1", l1_ptr);
        cand.addUserCand("l2", l2_ptr);
        cand.addUserCand("trk1", trk1_ptr);
        cand.addUserCand("trk2", trk2_ptr);
        cand.addUserCand("dilepton", ll_ptr);

        cand.addUserInt("l1_idx", l1_idx);
        cand.addUserInt("l2_idx", l2_idx);
        cand.addUserInt("ll_idx" , ll_idx);
        cand.addUserInt("trk1_idx", trk1_idx);
        cand.addUserInt("trk2_idx", trk2_idx);
        cand.addUserFloat("trk1_mass", trk1_ptr->mass());
        cand.addUserFloat("trk2_mass", trk2_ptr->mass());

        // pre-fit handles for the cff window cuts
        cand.addUserFloat("mll",        dilep_p4.mass());    // dilepton (Z lepton pair)
        cand.addUserFloat("m_ditrack",  ditrack_p4.mass());  // vector-meson candidate (rho/phi)
        cand.addUserFloat("ditrack_pt", ditrack_p4.pt());    // pT(hh): a Z->V gives an energetic V
        cand.addUserFloat("dilep_pt",   dilep_p4.pt());

        // Raw track kinematics + alternative mass hypotheses for the SAME pair. The general
        // track table is dropped from the output, so without these the offline analysis
        // cannot re-evaluate the pair. Diagnostic for the phi-independent 91 GeV structure:
        // a photon conversion (gamma->ee) or a Z->4l pair collapses to m_ee ~ 0 / m_mumu ~ 0
        // under the right hypothesis, while a genuine hadron pair does not.
        cand.addUserFloat("trk1_pt",  trk1_ptr->pt());
        cand.addUserFloat("trk1_eta", trk1_ptr->eta());
        cand.addUserFloat("trk1_phi", trk1_ptr->phi());
        cand.addUserFloat("trk2_pt",  trk2_ptr->pt());
        cand.addUserFloat("trk2_eta", trk2_ptr->eta());
        cand.addUserFloat("trk2_phi", trk2_ptr->phi());
        {
          math::PtEtaPhiMLorentzVector t1e(trk1_ptr->pt(), trk1_ptr->eta(), trk1_ptr->phi(), ELECTRON_MASS);
          math::PtEtaPhiMLorentzVector t2e(trk2_ptr->pt(), trk2_ptr->eta(), trk2_ptr->phi(), ELECTRON_MASS);
          math::PtEtaPhiMLorentzVector t1m(trk1_ptr->pt(), trk1_ptr->eta(), trk1_ptr->phi(), MUON_MASS);
          math::PtEtaPhiMLorentzVector t2m(trk2_ptr->pt(), trk2_ptr->eta(), trk2_ptr->phi(), MUON_MASS);
          cand.addUserFloat("m_ditrack_ee",   (t1e + t2e).mass());
          cand.addUserFloat("m_ditrack_mumu", (t1m + t2m).mass());
        }

        auto dr_info = min_max_dr({l1_ptr, l2_ptr, trk1_ptr, trk2_ptr});
        cand.addUserFloat("min_dr", dr_info.first);
        cand.addUserFloat("max_dr", dr_info.second);

        if ( !pre_vtx_selection_(cand) ) continue;

        // TwoTrackMassKinematicConstraint constrains the FIRST TWO particles, so when the
        // di-track (phi->KK) is to be constrained the TRACKS must be passed first. Ordering is
        // the only thing that selects what gets constrained.
        const std::vector<reco::TransientTrack> tt_lep_first =
            { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx), ttracks->at(trk1_idx), ttracks->at(trk2_idx) };
        const std::vector<double>  m_lep_first = { lep_mass_, lep_mass_, trk_mass_, trk_mass_ };
        const std::vector<float>   s_lep_first = { (float)lep_sigma_, (float)lep_sigma_, (float)trk_sigma_, (float)trk_sigma_ };
        const std::vector<reco::TransientTrack> tt_trk_first =
            { ttracks->at(trk1_idx), ttracks->at(trk2_idx), leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx) };
        const std::vector<double>  m_trk_first = { trk_mass_, trk_mass_, lep_mass_, lep_mass_ };
        const std::vector<float>   s_trk_first = { (float)trk_sigma_, (float)trk_sigma_, (float)lep_sigma_, (float)lep_sigma_ };

        KinVtxFitter fitter =
            (mass_constraint_ == "ditrack")
              ? KinVtxFitter(tt_trk_first, m_trk_first, s_trk_first, (ParticleMass) constraint_mass_)
          : (mass_constraint_ == "dilepton")
              ? KinVtxFitter(tt_lep_first, m_lep_first, s_lep_first, (ParticleMass) constraint_mass_)
              : KinVtxFitter(tt_lep_first, m_lep_first, s_lep_first);

        if (!fitter.success()) continue;

        cand.setVertex(
          reco::Candidate::Point(
            fitter.fitted_vtx().x(),
            fitter.fitted_vtx().y(),
            fitter.fitted_vtx().z()
          )
        );

        cand.addUserFloat("sv_chi2", fitter.chi2());
        cand.addUserFloat("sv_ndof", fitter.dof());
        cand.addUserFloat("sv_prob", fitter.prob());

        cand.addUserFloat("fitted_ditrack_mass",
                          (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());
        cand.addUserFloat("fitted_ditrack_pt",
                          (fitter.daughter_p4(2) + fitter.daughter_p4(3)).pt());
        cand.addUserFloat("fitted_mll",
                          (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());

        auto fit_p4 = fitter.fitted_p4();
        cand.addUserFloat("fitted_pt"  , fit_p4.pt());
        cand.addUserFloat("fitted_eta" , fit_p4.eta());
        cand.addUserFloat("fitted_phi" , fit_p4.phi());
        cand.addUserFloat("fitted_mass", fit_p4.mass());
        cand.addUserFloat("fitted_massErr",
                          sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
        cand.addUserFloat("fitted_rapidity", fit_p4.Rapidity());

        // prompt-signature variables (Z is prompt: cos2D ~ 1, l_xy ~ 0)
        cand.addUserFloat("cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, cand.p4()));
        cand.addUserFloat("fitted_cos_theta_2D",
                          cos_theta_2D(fitter, *beamspot, fit_p4));
        auto lxy = l_xy(fitter, *beamspot);
        cand.addUserFloat("l_xy", lxy.value());
        cand.addUserFloat("l_xy_unc", lxy.error());
        cand.addUserFloat("l_xy_sig", (lxy.error() > 0) ? lxy.value() / lxy.error() : -1.f);

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

        std::vector<std::string> dnames{ "l1", "l2", "trk1", "trk2" };
        for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_pt" , fitter.daughter_p4(idaughter).pt() );
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_eta", fitter.daughter_p4(idaughter).eta() );
          cand.addUserFloat("fitted_" + dnames[idaughter] + "_phi", fitter.daughter_p4(idaughter).phi() );
        }

        TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> cur2DIP1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("trk1_svip2d" , cur2DIP1.second.value());
        cand.addUserFloat("trk1_svip2d_err" , cur2DIP1.second.error());

        TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> cur2DIP2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("trk2_svip2d" , cur2DIP2.second.value());
        cand.addUserFloat("trk2_svip2d_err" , cur2DIP2.second.error());

        std::vector<float> isos = TrackerIsolation(tracks, cand, dnames );
        for (size_t idaughter = 0; idaughter < dnames.size(); idaughter++) {
          cand.addUserFloat(dnames[idaughter] + "_iso04", isos[idaughter]);
        }

        // V-candidate isolation: sum pT of OTHER tracks within dR<0.4 of the V (di-track)
        // direction, EXCLUDING the two V daughters. A real rho/phi from a Z is isolated;
        // combinatorial di-tracks sit in busy QCD environments -> strong bkg discriminator
        // if the candidate rate gets large. Stored (not cut) so the cut can be tuned offline.
        {
          auto v_fit = fitter.daughter_p4(2) + fitter.daughter_p4(3);
          float iso_sumpt = 0.f; int iso_n = 0;
          for (size_t k = 0; k < tracks->size(); ++k) {
            if (int(k) == (int)trk1_idx || int(k) == (int)trk2_idx) continue;
            edm::Ptr<pat::CompositeCandidate> tk(tracks, k);
            float dr = reco::deltaR(v_fit.eta(), v_fit.phi(), tk->eta(), tk->phi());
            if (dr < 0.4) { iso_sumpt += tk->pt(); ++iso_n; }
          }
          cand.addUserFloat("v_iso_sumpt", iso_sumpt);
          cand.addUserInt("v_iso_n", iso_n);
          cand.addUserFloat("v_iso", (v_fit.pt() > 0) ? iso_sumpt / v_fit.pt() : -1.f);
        }

        ret_val->push_back(cand);

      } // trk2
    } // trk1
  } // dilepton

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(ZToLLVBuilder);
