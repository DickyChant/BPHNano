//////////////////////////// UpsilonTo2Mu2EBuilder //////////////////////////////
// Upsilon -> mu+ mu- e+ e- : a dilepton (dimuon) + two charged tracks treated as
// electrons, vertexed with a common four-track KinematicVertexFit.
// This is a clone of EtaTo2L2PiBuilder (Y. Lai) with the two "track" daughters given
// the ELECTRON mass instead of the pion mass. The tracks are the generic charged-track
// collection (tracksBPH); the electron identity / ID is applied downstream by matching
// trk{1,2}_idx to the LowPtElectron table (kept in the output).

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
#include <array>
#include <tuple>
// ELECTRON_MASS / MUON_MASS / LEP_SIGMA come from helper.h

class UpsilonTo2Mu2EBuilder : public edm::global::EDProducer<> {

public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit UpsilonTo2Mu2EBuilder(const edm::ParameterSet &cfg):
    bFieldToken_{esConsumes<MagneticField, IdealMagneticFieldRecord>()},
    trk1_selection_{cfg.getParameter<std::string>("trk1Selection")},
    trk2_selection_{cfg.getParameter<std::string>("trk2Selection")},
    allow_ss_trk_pair_{cfg.getParameter<bool>("allowSameSignTrackPair")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    tracks_(consumes<pat::CompositeCandidateCollection>(cfg.getParameter<edm::InputTag>("tracks"))),
    ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracks") )},
    ttracks_low_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracksLow") )},
    ttracks_nom_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("transientTracksNominal") )},
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )}
  {
    produces<pat::CompositeCandidateCollection>();
  }

  ~UpsilonTo2Mu2EBuilder() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}

private:
  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
  const StringCutObjectSelector<pat::CompositeCandidate> trk1_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> trk2_selection_;
  const bool allow_ss_trk_pair_;
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> tracks_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_low_;
  const edm::EDGetTokenT<TransientTrackCollection> ttracks_nom_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
};

void UpsilonTo2Mu2EBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);
  edm::Handle<pat::CompositeCandidateCollection> tracks;
  evt.getByToken(tracks_, tracks);
  edm::Handle<TransientTrackCollection> ttracks;
  evt.getByToken(ttracks_, ttracks);
  edm::Handle<TransientTrackCollection> ttracks_low;
  evt.getByToken(ttracks_low_, ttracks_low);
  edm::Handle<TransientTrackCollection> ttracks_nom;
  evt.getByToken(ttracks_nom_, ttracks_nom);
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

    // two electron-candidate tracks
    for (size_t trk1_idx = 0; trk1_idx < tracks->size(); ++trk1_idx) {
      edm::Ptr<pat::CompositeCandidate> trk1_ptr(tracks, trk1_idx);
      if (!trk1_selection_(*trk1_ptr)) continue;

      for (size_t trk2_idx = trk1_idx + 1; trk2_idx < tracks->size(); ++trk2_idx) {
        edm::Ptr<pat::CompositeCandidate> trk2_ptr(tracks, trk2_idx);
        if (!trk2_selection_(*trk2_ptr)) continue;

        // Opposite-sign e pair unless a same-sign control sample was asked for. The 4-body
        // charge is stored, so the two categories separate offline. Same-sign is the standard
        // combinatorial control: no resonance can populate it.
        if (!allow_ss_trk_pair_ && (trk1_ptr->charge() + trk2_ptr->charge()) != 0) continue;

        pat::CompositeCandidate cand;
        math::PtEtaPhiMLorentzVector l1_p4(l1_ptr->pt(), l1_ptr->eta(), l1_ptr->phi(), MUON_MASS);
        math::PtEtaPhiMLorentzVector l2_p4(l2_ptr->pt(), l2_ptr->eta(), l2_ptr->phi(), MUON_MASS);
        math::PtEtaPhiMLorentzVector trk1_p4(trk1_ptr->pt(), trk1_ptr->eta(), trk1_ptr->phi(), ELECTRON_MASS);
        math::PtEtaPhiMLorentzVector trk2_p4(trk2_ptr->pt(), trk2_ptr->eta(), trk2_ptr->phi(), ELECTRON_MASS);
        auto cand_p4 = l1_p4 + l2_p4 + trk1_p4 + trk2_p4;
        cand.setP4(cand_p4);
        cand.setCharge(l1_ptr->charge() + l2_ptr->charge() + trk1_ptr->charge() + trk2_ptr->charge());

        cand.addUserCand("l1", l1_ptr);
        cand.addUserCand("l2", l2_ptr);
        cand.addUserCand("trk1", trk1_ptr);
        cand.addUserCand("trk2", trk2_ptr);
        cand.addUserCand("dilepton", ll_ptr);

        cand.addUserInt("l1_idx", l1_idx);
        cand.addUserInt("l2_idx", l2_idx);
        cand.addUserInt("ll_idx", ll_idx);
        // Index into whatever collection fed us. LowPtEleMerger stamps userInt("ele_idx")
        // (-> LowPtElectron table); generic TrackMerger tracks have no such UserInt, so fall
        // back to the position in the input collection (-> Track table). This is what lets the
        // same builder run on LowPtElectron legs and on generic tracks under the e-mass
        // hypothesis, for a like-for-like comparison.
        cand.addUserInt("trk1_idx", trk1_ptr->hasUserInt("ele_idx") ? trk1_ptr->userInt("ele_idx")
                                                                   : (int)trk1_idx);
        cand.addUserInt("trk2_idx", trk2_ptr->hasUserInt("ele_idx") ? trk2_ptr->userInt("ele_idx")
                                                                   : (int)trk2_idx);
        cand.addUserFloat("trk1_mass", ELECTRON_MASS);
        cand.addUserFloat("trk2_mass", ELECTRON_MASS);

        // which electron collection each leg came from: 0 = LowPtElectron, 1 = standard
        // Electron, -1 = generic track. Together with trk{1,2}_idx this picks the right
        // NanoAOD table row, and (src1,src2) defines the three fit categories:
        // (0,0) both soft, (0,1)/(1,0) mixed, (1,1) both standard.
        cand.addUserInt("trk1_src", trk1_ptr->hasUserInt("ele_src") ? trk1_ptr->userInt("ele_src") : -1);
        cand.addUserInt("trk2_src", trk2_ptr->hasUserInt("ele_src") ? trk2_ptr->userInt("ele_src") : -1);

        // per-leg conversion match (LowPtEleMerger stamps these; generic tracks do not)
        cand.addUserInt("trk1_conv_matched",
                        trk1_ptr->hasUserInt("conv_matched") ? trk1_ptr->userInt("conv_matched") : -1);
        cand.addUserInt("trk2_conv_matched",
                        trk2_ptr->hasUserInt("conv_matched") ? trk2_ptr->userInt("conv_matched") : -1);
        cand.addUserFloat("trk1_conv_r",
                          trk1_ptr->hasUserFloat("conv_r") ? trk1_ptr->userFloat("conv_r") : -1.f);
        cand.addUserFloat("trk2_conv_r",
                          trk2_ptr->hasUserFloat("conv_r") ? trk2_ptr->userFloat("conv_r") : -1.f);
        cand.addUserFloat("trk1_conv_dr",
                          trk1_ptr->hasUserFloat("conv_dr") ? trk1_ptr->userFloat("conv_dr") : -1.f);
        cand.addUserFloat("trk2_conv_dr",
                          trk2_ptr->hasUserFloat("conv_dr") ? trk2_ptr->userFloat("conv_dr") : -1.f);
        for (const char* v : {"lost_hits", "pass_conv_veto"}) {
          cand.addUserInt(std::string("trk1_") + v, trk1_ptr->hasUserInt(v) ? trk1_ptr->userInt(v) : -1);
          cand.addUserInt(std::string("trk2_") + v, trk2_ptr->hasUserInt(v) ? trk2_ptr->userInt(v) : -1);
        }
        // Both reconstructions of each leg, side by side (see LowPtEleMerger). has_low /
        // has_nominal say which exist; the per-combination fitted masses below are -1 when a
        // leg lacks the reconstruction that combination needs.
        for (const char* v : {"has_low", "has_nominal", "low_idx", "nominal_idx"}) {
          cand.addUserInt(std::string("trk1_") + v, trk1_ptr->hasUserInt(v) ? trk1_ptr->userInt(v) : -1);
          cand.addUserInt(std::string("trk2_") + v, trk2_ptr->hasUserInt(v) ? trk2_ptr->userInt(v) : -1);
        }
        for (const char* v : {"low_pt", "low_eta", "low_phi",
                              "nominal_pt", "nominal_eta", "nominal_phi"}) {
          cand.addUserFloat(std::string("trk1_") + v, trk1_ptr->hasUserFloat(v) ? trk1_ptr->userFloat(v) : -1.f);
          cand.addUserFloat(std::string("trk2_") + v, trk2_ptr->hasUserFloat(v) ? trk2_ptr->userFloat(v) : -1.f);
        }

        for (const char* v : {"sieie", "hoe"}) {
          cand.addUserFloat(std::string("trk1_") + v, trk1_ptr->hasUserFloat(v) ? trk1_ptr->userFloat(v) : -1.f);
          cand.addUserFloat(std::string("trk2_") + v, trk2_ptr->hasUserFloat(v) ? trk2_ptr->userFloat(v) : -1.f);
        }

        auto dr_info = min_max_dr({l1_ptr, l2_ptr, trk1_ptr, trk2_ptr});
        cand.addUserFloat("min_dr", dr_info.first);
        cand.addUserFloat("max_dr", dr_info.second);

        if (!pre_vtx_selection_(cand)) continue;

        KinVtxFitter fitter(
          { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx), ttracks->at(trk1_idx), ttracks->at(trk2_idx) },
          { MUON_MASS, MUON_MASS, ELECTRON_MASS, ELECTRON_MASS },
          { LEP_SIGMA, LEP_SIGMA, LEP_SIGMA, LEP_SIGMA }
          );
        if (!fitter.success()) continue;

        cand.setVertex(reco::Candidate::Point(
            fitter.fitted_vtx().x(), fitter.fitted_vtx().y(), fitter.fitted_vtx().z()));

        cand.addUserFloat("sv_chi2", fitter.chi2());
        cand.addUserFloat("sv_ndof", fitter.dof());
        cand.addUserFloat("sv_prob", fitter.prob());
        cand.addUserFloat("fitted_mee", (fitter.daughter_p4(2) + fitter.daughter_p4(3)).mass());
        cand.addUserFloat("fitted_mll", (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());

        auto fit_p4 = fitter.fitted_p4();
        cand.addUserFloat("fitted_pt", fit_p4.pt());
        cand.addUserFloat("fitted_eta", fit_p4.eta());
        cand.addUserFloat("fitted_phi", fit_p4.phi());
        cand.addUserFloat("fitted_mass", fit_p4.mass());
        cand.addUserFloat("fitted_massErr",
                          sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6, 6)));
        cand.addUserFloat("fitted_rapidity", fit_p4.Rapidity());

        // A SEPARATE two-track fit of just the e+e- pair. The 4-track vertex is dominated by
        // the two well-measured prompt muons and is pulled to the primary vertex regardless of
        // where the electrons originated, so it cannot reveal a conversion. Fitting the e legs
        // alone does: a converted photon gives a displaced ee vertex out at the beam pipe or
        // the pixel layers, a prompt double-Dalitz pair gives one at the collision point.
        KinVtxFitter ee_fitter(
          { ttracks->at(trk1_idx), ttracks->at(trk2_idx) },
          { ELECTRON_MASS, ELECTRON_MASS },
          { LEP_SIGMA, LEP_SIGMA }
          );
        if (ee_fitter.success()) {
          const auto& eevtx = ee_fitter.fitted_vtx();
          cand.addUserFloat("ee_vtx_x", eevtx.x());
          cand.addUserFloat("ee_vtx_y", eevtx.y());
          cand.addUserFloat("ee_vtx_z", eevtx.z());
          cand.addUserFloat("ee_vtx_r", std::sqrt(eevtx.x() * eevtx.x() + eevtx.y() * eevtx.y()));
          cand.addUserFloat("ee_svprob", ee_fitter.prob());
          cand.addUserFloat("ee_mass", ee_fitter.fitted_p4().mass());
        } else {
          cand.addUserFloat("ee_vtx_x", -999.f);
          cand.addUserFloat("ee_vtx_y", -999.f);
          cand.addUserFloat("ee_vtx_z", -999.f);
          cand.addUserFloat("ee_vtx_r", -1.f);
          cand.addUserFloat("ee_svprob", -1.f);
          cand.addUserFloat("ee_mass", -1.f);
        }

        // ------------------------------------------------------------------------------
        // The candidate mass under EVERY electron-object choice, each from its OWN 4-track
        // KinematicVertexFit so the mass carries a real fitted uncertainty:
        //   fitted_mass                    nominal (per leg: standard at/above the merger's
        //                                  pT threshold, LowPtElectron below it)
        //   fitted_mass_lowlow             both legs LowPtElectron
        //   fitted_mass_lownominal         leg1 LowPtElectron, leg2 standard
        //   fitted_mass_nominallow         leg1 standard,      leg2 LowPtElectron
        //   fitted_mass_nominalnominal     both legs standard
        // Each is -1 (with its error -1) when a leg does not have that reconstruction.
        {
          const bool t1_low = trk1_ptr->hasUserInt("has_low")     && trk1_ptr->userInt("has_low");
          const bool t1_nom = trk1_ptr->hasUserInt("has_nominal") && trk1_ptr->userInt("has_nominal");
          const bool t2_low = trk2_ptr->hasUserInt("has_low")     && trk2_ptr->userInt("has_low");
          const bool t2_nom = trk2_ptr->hasUserInt("has_nominal") && trk2_ptr->userInt("has_nominal");
          // Availability category, per leg and then combined:
          //   0 = only the LowPtElectron reconstruction exists
          //   1 = only the standard (slimmedElectron) reconstruction exists
          //   2 = both exist
          // ele_cat = trk1_ele_cat * 3 + trk2_ele_cat, so 0..8 -- nine categories.
          auto leg_cat = [](bool lo, bool no) { return (lo && no) ? 2 : (no ? 1 : 0); };
          const int c1 = leg_cat(t1_low, t1_nom), c2 = leg_cat(t2_low, t2_nom);
          cand.addUserInt("trk1_ele_cat", c1);
          cand.addUserInt("trk2_ele_cat", c2);
          cand.addUserInt("ele_cat", c1 * 3 + c2);

          const std::array<std::tuple<const char*, bool, bool>, 4> combos{{
            {"lowlow",         false, false},
            {"lownominal",     false, true },
            {"nominallow",     true,  false},
            {"nominalnominal", true,  true },
          }};
          for (const auto& c : combos) {
            const char* nm = std::get<0>(c);
            const bool n1 = std::get<1>(c), n2 = std::get<2>(c);
            const bool ok1 = n1 ? t1_nom : t1_low;
            const bool ok2 = n2 ? t2_nom : t2_low;
            float mval = -1.f, merr = -1.f;
            if (ok1 && ok2) {
              KinVtxFitter f2(
                { leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx),
                  (n1 ? ttracks_nom : ttracks_low)->at(trk1_idx),
                  (n2 ? ttracks_nom : ttracks_low)->at(trk2_idx) },
                { MUON_MASS, MUON_MASS, ELECTRON_MASS, ELECTRON_MASS },
                { LEP_SIGMA, LEP_SIGMA, LEP_SIGMA, LEP_SIGMA }
                );
              if (f2.success()) {
                mval = f2.fitted_p4().mass();
                merr = std::sqrt(f2.fitted_candidate().kinematicParametersError().matrix()(6, 6));
              }
            }
            cand.addUserFloat(std::string("fitted_mass_") + nm, mval);
            cand.addUserFloat(std::string("fitted_massErr_") + nm, merr);
          }
        }
        // ------------------------------------------------------------------------------

        cand.addUserFloat("cos_theta_2D", cos_theta_2D(fitter, *beamspot, cand.p4()));
        cand.addUserFloat("fitted_cos_theta_2D", cos_theta_2D(fitter, *beamspot, fit_p4));
        auto lxy = l_xy(fitter, *beamspot);
        cand.addUserFloat("l_xy", lxy.value());
        cand.addUserFloat("l_xy_unc", lxy.error());

        if (!post_vtx_selection_(cand)) continue;

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
        for (size_t i = 0; i < dnames.size(); i++) {
          cand.addUserFloat("fitted_" + dnames[i] + "_pt", fitter.daughter_p4(i).pt());
          cand.addUserFloat("fitted_" + dnames[i] + "_eta", fitter.daughter_p4(i).eta());
          cand.addUserFloat("fitted_" + dnames[i] + "_phi", fitter.daughter_p4(i).phi());
        }

        TrajectoryStateOnSurface tsos1 = extrapolator.extrapolate(ttracks->at(trk1_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> ip1 = signedTransverseImpactParameter(tsos1, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("trk1_svip2d", ip1.second.value());
        cand.addUserFloat("trk1_svip2d_err", ip1.second.error());
        TrajectoryStateOnSurface tsos2 = extrapolator.extrapolate(ttracks->at(trk2_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool, Measurement1D> ip2 = signedTransverseImpactParameter(tsos2, fitter.fitted_refvtx(), *beamspot);
        cand.addUserFloat("trk2_svip2d", ip2.second.value());
        cand.addUserFloat("trk2_svip2d_err", ip2.second.error());

        std::vector<float> isos = TrackerIsolation(tracks, cand, dnames);
        for (size_t i = 0; i < dnames.size(); i++)
          cand.addUserFloat(dnames[i] + "_iso04", isos[i]);

        ret_val->push_back(cand);
      }
    }
  }

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(UpsilonTo2Mu2EBuilder);
