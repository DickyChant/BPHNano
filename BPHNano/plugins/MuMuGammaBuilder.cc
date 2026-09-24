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
// Two masses are stored. `mass` is the dimuon fit plus the photon as a 4-vector (the onia
// treatment for chi_c -> J/psi gamma). `fitted_mass` is a 3-body fit in Kirill Ivanov's style
// (see produce()): the conversion pair is first fitted to its own vertex, and that photon --
// one neutral particle starting at the conversion point -- is then fitted to a common vertex
// with the two muons. The electrons are never forced onto the muon vertex, so the fit does not
// carry the bias of a 4-track mu mu e e fit of a conversion.

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include <atomic>
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "RecoVertex/KinematicFitPrimitives/interface/KinematicParticleFactoryFromTransientTrack.h"
#include "RecoVertex/KinematicFitPrimitives/interface/VirtualKinematicParticleFactory.h"
#include "RecoVertex/KinematicFit/interface/KinematicParticleVertexFitter.h"
#include "RecoVertex/KinematicFit/interface/KinematicParticleFitter.h"
#include "RecoVertex/KinematicFit/interface/MassKinematicConstraint.h"
#include "RecoVertex/KinematicFit/interface/KinematicConstrainedVertexFitter.h"
#include "RecoVertex/KinematicFit/interface/ColinearityKinematicConstraint.h"
#include "TVectorD.h"
#include "TMatrixDSym.h"
#include "TMath.h"
#include "FWCore/Utilities/interface/Exception.h"
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
    post_sel_{cfg.getParameter<std::string>("postSelection")},
    throw_on_missing_{parse_policy(cfg.getParameter<std::string>("missingPhotons"))},
    muon_ttracks_{consumes<std::vector<reco::TransientTrack>>(cfg.getParameter<edm::InputTag>("muonTransientTracks"))},
    ttb_token_{esConsumes<TransientTrackBuilder, TransientTrackRecord>(edm::ESInputTag("", "TransientTrackBuilder"))},
    veto_flags_{cfg.getParameter<int>("photonVetoFlags")},
    kirill_{cfg.getParameter<bool>("kirillFit")},
    conversion_fit_pset_{cfg.getParameter<edm::ParameterSet>("conversionFitParameters")}
  {
    produces<pat::CompositeCandidateCollection>();
    // Per-event record of whether the photon input existed, so an analysis can see -- and
    // correct the normalisation for -- events where mu mu gamma was impossible rather than
    // merely empty. One row per event (singleton table).
    produces<nanoaod::FlatTable>("photonStatus");
  }

  ~MuMuGammaBuilder() override {}
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

private:
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> photons_;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;
  const StringCutObjectSelector<pat::CompositeCandidate> photon_selection_;
  static bool parse_policy(const std::string& p) {
    if (p == "skip")  return false;
    if (p == "throw") return true;
    throw cms::Exception("Configuration") << "MuMuGammaBuilder: missingPhotons must be 'skip' or "
                                             "'throw', got '" << p << "'";
  }
  const StringCutObjectSelector<pat::CompositeCandidate> pre_sel_;
  const StringCutObjectSelector<pat::CompositeCandidate> post_sel_;
  const bool throw_on_missing_;
  // 3-body fit (Kirill Ivanov's BsToJpsiGamma recipe, see produce())
  const edm::EDGetTokenT<std::vector<reco::TransientTrack>> muon_ttracks_;
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> ttb_token_;
  const int veto_flags_;
  const bool kirill_;   // also run Kirill's own conversion fit, stored as *_kirill
  const edm::ParameterSet conversion_fit_pset_;
};

namespace {
// Force a track covariance to be positive definite by shifting its eigenvalues (modified
// Cholesky), replacing nan/inf entries first -- they segfault the eigen-decomposition.
// Ported verbatim in logic from Kirill Ivanov's Xb_frame (branch BsToJpsiGamma); a
// non-positive-definite covariance makes the kinematic fit fail or throw.
reco::Track fix_track(const reco::Track& tk, double delta = 1e-8) {
  reco::TrackBase::CovarianceMatrix cov = tk.covariance();
  TMatrixDSym m(cov.kRows);
  for (unsigned i = 0; i < cov.kRows; ++i)
    for (unsigned j = 0; j < cov.kRows; ++j) {
      if (std::isnan(cov(i, j)) || std::isinf(cov(i, j))) cov(i, j) = 1e-6;
      m(i, j) = cov(i, j);
    }
  TVectorD eig(cov.kRows);
  m.EigenVectors(eig);
  double min_eig = 1;
  for (unsigned i = 0; i < cov.kRows; ++i) min_eig = std::min(min_eig, eig(i));
  if (min_eig < 0)
    for (unsigned i = 0; i < cov.kRows; ++i) cov(i, i) -= min_eig - delta;
  return reco::Track(tk.chi2(), tk.ndof(), tk.referencePoint(), tk.momentum(), tk.charge(), cov,
                     tk.algo(), (reco::TrackBase::TrackQuality)tk.qualityMask());
}

constexpr float kElectronMass = 0.000510999f, kMuonMass = 0.1056584f;

struct PhotonFit {
  bool ok = false;
  RefCountedKinematicParticle particle;     // the photon at its conversion vertex
  RefCountedKinematicTree tree;             // keeps the particle's tree alive with it
  // 1 = fitted; otherwise the stage that failed: 0 conversion tracks missing, -1 transient
  // track invalid, -2 ee vertex fit threw, -3 ee vertex fit invalid, -4 ee vertex chi2 < 0,
  // -5 zero-mass constraint threw, -6 zero-mass constraint invalid (-5/-6: Kirill's fit only)
  int status = 0;
  float prob = -1.f, vx = 0.f, vy = 0.f, vz = 0.f, pt = -1.f, eta = 0.f, phi = 0.f;
  math::XYZTLorentzVector trk0, trk1;       // for the muon-overlap check
};

struct ThreeBodyFit {
  int ok = 0;
  float mass = -1.f, massErr = -1.f, prob = -1.f, pt = -1.f, eta = 0.f, phi = 0.f;
  float x = 0.f, y = 0.f, z = 0.f;
};
}  // namespace

void MuMuGammaBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &setup) const {

  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  edm::Handle<pat::CompositeCandidateCollection> photons;
  evt.getByToken(photons_, photons);
  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);

  auto ret = std::make_unique<pat::CompositeCandidateCollection>();

  // oniaPhotonCandidates:conversions is DECLARED in every Run-3 parking MiniAOD version
  // (checked on all 39 era x processing versions, 2022C through 2026D) but is not written in
  // every event: on Run2022C PromptReco an event with a dimuon had no such product, and the
  // unchecked handle threw ProductNotFound, killing the job. No photons -> no candidates.
  auto status = std::make_unique<nanoaod::FlatTable>(1, "EtaPrimeToMuMuGammaInput", true);
  status->addColumnValue<bool>("photonsPresent", photons.isValid(),
                               "oniaPhotonCandidates:conversions existed in this event");
  status->addColumnValue<int>("nPhotons", photons.isValid() ? (int)photons->size() : -1,
                              "number of input conversions (-1: collection absent)");
  evt.put(std::move(status), "photonStatus");

  if (!photons.isValid()) {
    // missingPhotons='throw' restores the strict behaviour -- use it to AUDIT a dataset.
    if (throw_on_missing_)
      throw cms::Exception("ProductNotFound") << "MuMuGammaBuilder: photon collection absent "
          "(missingPhotons='throw'); set missingPhotons='skip' to tolerate it";
    static std::atomic<bool> warned{false};
    bool expected = false;
    if (warned.compare_exchange_strong(expected, true))
      edm::LogWarning("MuMuGammaBuilder") << "photon collection absent in this event (first "
          "occurrence; further ones are silent) -- emitting no mu mu gamma candidates for it. "
          "Per-event status is in EtaPrimeToMuMuGammaInput_photonsPresent.";
    evt.put(std::move(ret));
    return;
  }

  // ------------------------------------------------------------------------------------------
  // Kirill Ivanov's converted-photon recipe (Xb_frame, branch BsToJpsiGamma):
  //   1. fit the conversion's two tracks to a common vertex, so the photon becomes ONE
  //      kinematic particle carrying its own (displaced) conversion vertex,
  //   2. fit mu+ mu- gamma to a common vertex with the photon as that particle ("3 tracks").
  // The electrons are never forced onto the muon vertex, which is what biases a 4-track
  // mu mu e e fit of a conversion (its eta peak lands ~27 MeV high, the eta' ~50 MeV high).
  //
  // Step 1 is done two ways and both results are stored, side by side:
  //  colinear (fitted_mass, svprob, gamma_fit_*): the fit CMS conversion reconstruction runs
  //     itself (ConversionVertexFinder: Lagrange vertex fit with a PhiTheta colinearity
  //     constraint, parameters from allConversions_cfi). On 2025D data it converges for
  //     99.8% of the conversions and reproduces the stored conversion vertex and refitted
  //     pair momentum. The pair comes out at ~2 m_e, so no zero-mass step follows: forcing
  //     that tightly constrained mass to 0 drags the momentum through the covariance (a
  //     median 0.5 rad off in the test), and a 1 MeV photon mass moves m(mu mu gamma) ~1 keV.
  //  Kirill's own (*_kirill, if kirillFit): a plain 2-track vertex fit followed by a
  //     zero-mass constraint. It fails for ~41% of the conversions (82% beyond r = 20 cm):
  //     the sequential fitter does not converge on two tracks tangent at the vertex.
  // His J/psi mass constraint on the dimuon is deliberately NOT ported: here m(mumu) is the
  // Dalitz variable, not a resonance.
  //
  // Step 1 depends only on the photon, so it runs once per photon, and only for photons that
  // reach a candidate. Step 2 gets a FRESH copy of the photon without its tree each time: the
  // vertex fitter writes its refitted particle back into an input particle's tree
  // (FinalTreeBuilder: replaceCurrentParticle), so a photon shared by two dimuons would enter
  // the second fit already refitted to the first one.
  // ------------------------------------------------------------------------------------------
  const auto& ttb = setup.getData(ttb_token_);
  edm::Handle<std::vector<reco::TransientTrack>> mu_tt;
  evt.getByToken(muon_ttracks_, mu_tt);
  KinematicParticleFactoryFromTransientTrack factory;
  VirtualKinematicParticleFactory vfactory;
  // A fitted particle keeps a pointer to the constraint that made it: the constraints must
  // live as long as the photon particles.
  MassKinematicConstraint zero_mass(0.f, 1e-6f);
  ColinearityKinematicConstraint colinearity(ColinearityKinematicConstraint::PhiTheta);
  KinematicConstrainedVertexFitter colinear_fitter;
  colinear_fitter.setParameters(conversion_fit_pset_);

  auto fit_photon = [&](const reco::Track& t0, const reco::Track& t1, bool colinear, PhotonFit& f) {
    f.trk0 = math::XYZTLorentzVector(t0.px(), t0.py(), t0.pz(), t0.p());
    f.trk1 = math::XYZTLorentzVector(t1.px(), t1.py(), t1.pz(), t1.p());
    std::vector<RefCountedKinematicParticle> ee;
    try {
      reco::TransientTrack e0 = ttb.build(fix_track(t0)), e1 = ttb.build(fix_track(t1));
      if (!e0.isValid() || !e1.isValid()) { f.status = -1; return; }
      float sig = kElectronMass * 1e-6f, chi = 0.f, ndf = 0.f;
      ee = {factory.particle(e0, kElectronMass, chi, ndf, sig), factory.particle(e1, kElectronMass, chi, ndf, sig)};
    } catch (const std::exception&) { f.status = -1; return; }
    RefCountedKinematicTree tree;
    try {
      if (colinear) {
        tree = colinear_fitter.fit(ee, &colinearity);
      } else {
        KinematicParticleVertexFitter vfit;
        tree = vfit.fit(ee);
      }
    } catch (const std::exception&) { f.status = -2; return; }   // VertexException
    if (!tree->isValid()) { f.status = -3; return; }
    tree->movePointerToTheTop();
    if (tree->currentDecayVertex()->chiSquared() < 0) { f.status = -4; return; }
    if (!colinear) {
      try {
        KinematicParticleFitter cfit;
        tree = cfit.fit(&zero_mass, tree);
      } catch (const std::exception&) { f.status = -5; return; }
      if (!tree->isValid()) { f.status = -6; return; }
      tree->movePointerToTheTop();
    }
    auto vtx = tree->currentDecayVertex();
    f.tree = tree;
    f.particle = tree->currentParticle();
    f.prob = TMath::Prob(vtx->chiSquared(), (int)vtx->degreesOfFreedom());
    f.vx = vtx->position().x(); f.vy = vtx->position().y(); f.vz = vtx->position().z();
    const auto mom = f.particle->currentState().globalMomentum();
    f.pt = mom.perp(); f.eta = mom.eta(); f.phi = mom.phi();
    f.status = 1;
    f.ok = true;
  };
  std::vector<PhotonFit> gcol(photons->size()), gkir(photons->size());
  std::vector<char> gfitted(photons->size(), 0);
  auto photon_fits = [&](size_t g) {
    if (!gfitted[g]) {
      gfitted[g] = 1;
      const reco::Track* t0 = (*photons)[g].userData<reco::Track>("track0");
      const reco::Track* t1 = (*photons)[g].userData<reco::Track>("track1");
      if (t0 && t1) {
        fit_photon(*t0, *t1, true, gcol[g]);
        if (kirill_) fit_photon(*t0, *t1, false, gkir[g]);
      }
    }
  };

  auto fit_3body = [&](int i1, int i2, const PhotonFit& gf) {
    ThreeBodyFit b;
    if (!gf.ok || !mu_tt.isValid() || i1 < 0 || i2 < 0 || i1 >= (int)mu_tt->size() || i2 >= (int)mu_tt->size())
      return b;
    // a conversion leg that IS one of the muons would double-count a track
    for (int mi : {i1, i2}) {
      const auto& mt = (*mu_tt)[mi].track();
      for (const auto* et : {&gf.trk0, &gf.trk1})
        if (reco::deltaR(mt.eta(), mt.phi(), et->eta(), et->phi()) < 1e-3 &&
            std::abs(mt.pt() - et->pt()) < 0.01 * mt.pt()) return b;
    }
    try {
      float sig = kMuonMass * 1e-6f, chi = 0.f, ndf = 0.f;
      float gchi = gf.particle->chiSquared(), gndf = gf.particle->degreesOfFreedom();
      std::vector<RefCountedKinematicParticle> parts{
          factory.particle((*mu_tt)[i1], kMuonMass, chi, ndf, sig),
          factory.particle((*mu_tt)[i2], kMuonMass, chi, ndf, sig),
          vfactory.particle(gf.particle->currentState(), gchi, gndf, nullptr)};   // no tree: see above
      KinematicParticleVertexFitter bfit;
      RefCountedKinematicTree bt = bfit.fit(parts);
      if (!bt->isValid()) return b;
      bt->movePointerToTheTop();
      auto bv = bt->currentDecayVertex();
      if (!bv->vertexIsValid() || bv->chiSquared() < 0) return b;
      auto bp = bt->currentParticle();
      b.mass = bp->currentState().mass();
      const double c66 = bp->currentState().kinematicParametersError().matrix()(6, 6);
      b.massErr = c66 > 0 ? std::sqrt(c66) : -1.f;
      b.prob = TMath::Prob(bv->chiSquared(), (int)bv->degreesOfFreedom());
      const auto m3 = bp->currentState().globalMomentum();
      b.pt = m3.perp(); b.eta = m3.eta(); b.phi = m3.phi();
      b.x = bv->position().x(); b.y = bv->position().y(); b.z = bv->position().z();
      b.ok = 1;
    } catch (const std::exception&) {
      b = ThreeBodyFit();
    }
    return b;
  };

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
    const int i1 = ll_ptr->hasUserInt("l1_idx") ? ll_ptr->userInt("l1_idx") : -1;
    const int i2 = ll_ptr->hasUserInt("l2_idx") ? ll_ptr->userInt("l2_idx") : -1;

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
      cand.addUserInt("l1_idx", i1);
      cand.addUserInt("l2_idx", i2);

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

      // pi0 veto (Kirill): OniaPhotonConversionProducer flag bit 16 = this photon pairs with
      // another PF photon inside the wide pi0 window (110-160 MeV). Configurable as a mask.
      const int flags = g_ptr->hasUserInt("flags") ? g_ptr->userInt("flags") : 0;
      cand.addUserInt("gamma_flags", flags);
      if (veto_flags_ && (flags & veto_flags_)) continue;

      // Stored, never required, so the fit efficiencies stay measurable; the fitted values
      // are -1 when a fit fails.
      photon_fits(g_idx);
      const PhotonFit& gf = gcol[g_idx];
      cand.addUserInt("gamma_fit_status", gf.status);
      cand.addUserFloat("gamma_fit_prob", gf.prob);
      cand.addUserFloat("gamma_fit_vtx_r", gf.ok ? std::hypot(gf.vx, gf.vy) : -1.f);
      cand.addUserFloat("gamma_fit_vtx_z", gf.ok ? gf.vz : -999.f);
      cand.addUserFloat("gamma_fit_pt", gf.pt);
      const ThreeBodyFit b = fit_3body(i1, i2, gf);
      cand.addUserInt("sv_ok", b.ok);
      cand.addUserFloat("fitted_mass", b.mass);
      cand.addUserFloat("fitted_massErr", b.massErr);
      cand.addUserFloat("svprob", b.prob);
      cand.addUserFloat("fitted_pt", b.pt);
      cand.addUserFloat("fitted_eta", b.eta);
      cand.addUserFloat("fitted_phi", b.phi);
      cand.addUserFloat("vtx_x", b.x);
      cand.addUserFloat("vtx_y", b.y);
      cand.addUserFloat("vtx_z", b.z);
      // Kirill's own conversion fit, in parallel (status -9: kirillFit off, nothing run)
      const PhotonFit& kf = gkir[g_idx];
      const ThreeBodyFit k = fit_3body(i1, i2, kf);
      cand.addUserInt("gamma_fit_status_kirill", kirill_ ? kf.status : -9);
      cand.addUserFloat("gamma_fit_prob_kirill", kf.prob);
      cand.addUserInt("sv_ok_kirill", k.ok);
      cand.addUserFloat("fitted_mass_kirill", k.mass);
      cand.addUserFloat("fitted_massErr_kirill", k.massErr);
      cand.addUserFloat("svprob_kirill", k.prob);

      if (!post_sel_(cand)) continue;
      ret->push_back(cand);
    }
  }
  evt.put(std::move(ret));
}

DEFINE_FWK_MODULE(MuMuGammaBuilder);
