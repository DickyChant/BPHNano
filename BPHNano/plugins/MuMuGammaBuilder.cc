//////////////////////////// MuMuGammaBuilder ////////////////////////////
// dimuon + CONVERTED PHOTON  ->  eta(548)/eta'(958) -> mu+ mu- gamma.
//
// This is the NORMALISATION channel for the 2mu2e double-Dalitz search. CMS-BPH-24-001
// (arXiv:2605.00615) measures B(eta -> mu+mu-e+e-) as a ratio to eta -> mu+mu- gamma with the
// photon converting, because the two share the same final-state particles and most systematics
// cancel. B(eta' -> mu+mu- gamma) = 1.09e-4 is known, so the same trick gives the eta' search
// an absolute scale.
//
// The photon comes from "oniaPhotonCandidates:conversions", which is ALREADY PRESENT in the
// Parking MiniAOD (produced by OniaPhotonConversionProducer during PAT production, ~1.6
// converted photons per event, pT median ~0.8 GeV -- exactly the range an eta'/eta radiative
// decay populates). Nothing has to be re-run. Do NOT try to run that producer ourselves on
// MiniAOD: it dereferences a reco::PFCandidateCollection ('particleFlow') unconditionally,
// which MiniAOD does not contain.
//
// Each photon candidate carries (see OniaPhotonConversionProducer::makePhotonCandidate):
//   p4     = conv.refittedPair4Momentum()      the photon momentum
//   vertex = conv.conversionVertex().position() -> the CONVERSION RADIUS, the variable that
//            separates a real converted photon (beam pipe ~2-3 cm, first pixel layers
//            ~3-6 cm) from a prompt pair
//   userData "track0"/"track1" = the two conversion tracks
//
// NO combined vertex fit is attempted: the photon converts centimetres away from the dimuon
// vertex, so constraining all of it to one point is meaningless. The dimuon's own fit is used
// (that is where the resolution comes from) and the photon is added as a 4-vector -- the
// standard onia treatment for chi_c -> J/psi gamma.

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "helper.h"

#include <cmath>
#include <memory>
#include <vector>

class MuMuGammaBuilder : public edm::global::EDProducer<> {
public:
  explicit MuMuGammaBuilder(const edm::ParameterSet &cfg):
    dileptons_{consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("dileptons"))},
    photons_{consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("photons"))},
    beamspot_{consumes<reco::BeamSpot>(cfg.getParameter<edm::InputTag>("beamSpot"))},
    photon_selection_{cfg.getParameter<std::string>("photonSelection")},
    pre_sel_{cfg.getParameter<std::string>("preSelection")},
    post_sel_{cfg.getParameter<std::string>("postSelection")}
  { produces<pat::CompositeCandidateCollection>(); }

  ~MuMuGammaBuilder() override {}
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

private:
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> photons_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  const StringCutObjectSelector<pat::CompositeCandidate> photon_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> pre_sel_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_sel_;
};

void MuMuGammaBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &) const {

  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<pat::CompositeCandidateCollection> photons;
  evt.getByToken(photons_, photons);
  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  auto ret = std::make_unique<pat::CompositeCandidateCollection>();

  for (size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
    edm::Ptr<pat::CompositeCandidate> ll_ptr(dileptons, ll_idx);

    // use the dimuon's FITTED momentum when its vertex fit succeeded -- that is where the
    // mass resolution comes from
    const bool ll_ok = ll_ptr->hasUserInt("sv_ok") && ll_ptr->userInt("sv_ok");
    const float ll_mass = ll_ok ? ll_ptr->userFloat("fitted_mass") : (float)ll_ptr->mass();
    math::PtEtaPhiMLorentzVector ll_p4(
        ll_ok ? ll_ptr->userFloat("fitted_pt")  : (float)ll_ptr->pt(),
        ll_ok ? ll_ptr->userFloat("fitted_eta") : (float)ll_ptr->eta(),
        ll_ok ? ll_ptr->userFloat("fitted_phi") : (float)ll_ptr->phi(),
        ll_mass);

    for (size_t g_idx = 0; g_idx < photons->size(); ++g_idx) {
      edm::Ptr<pat::CompositeCandidate> g_ptr(photons, g_idx);
      if (!photon_selection_(*g_ptr)) continue;

      math::PtEtaPhiMLorentzVector g_p4(g_ptr->pt(), g_ptr->eta(), g_ptr->phi(), 0.);

      pat::CompositeCandidate cand;
      cand.setP4(ll_p4 + g_p4);
      cand.setCharge(ll_ptr->charge());

      cand.addUserCand("dilepton", ll_ptr);
      cand.addUserCand("gamma", g_ptr);
      cand.addUserInt("ll_idx", (int)ll_idx);
      cand.addUserInt("gamma_idx", (int)g_idx);
      cand.addUserInt("l1_idx", ll_ptr->hasUserInt("l1_idx") ? ll_ptr->userInt("l1_idx") : -1);
      cand.addUserInt("l2_idx", ll_ptr->hasUserInt("l2_idx") ? ll_ptr->userInt("l2_idx") : -1);

      // the dimuon: in a radiative decay m(mumu) is the Dalitz variable, not a resonance
      cand.addUserFloat("ll_mass", ll_mass);
      cand.addUserFloat("ll_massErr", ll_ok ? ll_ptr->userFloat("fitted_massErr") : -1.f);
      cand.addUserFloat("ll_pt", ll_p4.pt());
      cand.addUserFloat("ll_svprob", ll_ptr->hasUserFloat("sv_prob") ? ll_ptr->userFloat("sv_prob") : -1.f);

      // the photon, and above all WHERE IT CONVERTED
      cand.addUserFloat("gamma_pt", g_ptr->pt());
      cand.addUserFloat("gamma_eta", g_ptr->eta());
      cand.addUserFloat("gamma_phi", g_ptr->phi());
      const float gx = g_ptr->vx(), gy = g_ptr->vy(), gz = g_ptr->vz();
      cand.addUserFloat("gamma_vtx_r", std::sqrt(gx * gx + gy * gy));
      cand.addUserFloat("gamma_vtx_z", gz);
      cand.addUserFloat("dR_ll_gamma", reco::deltaR(ll_p4.eta(), ll_p4.phi(),
                                                    g_ptr->eta(), g_ptr->phi()));

      // the two conversion tracks, attached by OniaPhotonConversionProducer
      const reco::Track* t0 = g_ptr->userData<reco::Track>("track0");
      const reco::Track* t1 = g_ptr->userData<reco::Track>("track1");
      cand.addUserFloat("gamma_trk0_pt", t0 ? t0->pt() : -1.f);
      cand.addUserFloat("gamma_trk1_pt", t1 ? t1->pt() : -1.f);

      if (!pre_sel_(cand)) continue;
      if (!post_sel_(cand)) continue;
      ret->push_back(cand);
    }
  }
  evt.put(std::move(ret));
}

DEFINE_FWK_MODULE(MuMuGammaBuilder);
