//////////////////////////// LowPtEleMerger ////////////////////////////
// Build a "track-like" pat::CompositeCandidate collection + parallel transient-track vectors
// from the OR of the two electron collections, to feed the 2mu2e 4-track
// KinematicVertexFit with ELECTRON legs instead of generic tracks (which exploded the
// combinatorics).
//
// ONE PASS, ONE COLLECTION. "electrons" (LowPtElectron) and "electrons2" (the standard
// slimmedElectrons) are OR'ed into a single output; a physical electron reconstructed in both
// appears exactly ONCE. This matters: the two collections overlap in pT -- LowPtElectron
// reconstructs ~0.5-15 GeV while slimmedElectrons in parking MiniAOD reaches down to ~3 GeV --
// and without de-duplication the same track is picked up twice, giving a same-sign "pair" with
// m(ee) = 2*m_e that swamps every real candidate.
//
// De-duplication is KINEMATIC (dR and relative pT). Matching gsfTrack refs does NOT work: the
// two collections' gsfTracks live in different products (lowPtGsfEleGsfTracks vs
// electronGsfTracks), so the ProductID never matches even for the same physical object.
//
// BOTH reconstructions are kept for every electron, not just the winner:
//   userInt  ("has_low"/"has_nominal")           which reconstructions exist
//   userInt  ("low_idx"/"nominal_idx")           index into the respective input collection
//   userFloat("low_pt|eta|phi", "nominal_...")   the two reconstructions' kinematics
// and two extra transient-track collections are emitted, index-aligned with the candidates:
//   "SelectedTransientElectronsLow"      the LowPtElectron gsf track
//   "SelectedTransientElectronsNominal"  the standard-electron gsf track
// so the downstream builder can REFIT the candidate with either choice per leg and report a
// fitted mass and error for each combination. Where a reconstruction is missing its slot is
// filled with the available one and the has_* flag is 0.
//
// The NOMINAL choice (the candidate's own p4 and "SelectedTransientElectrons") switches on
// pT: at or above "nominalPtThreshold" the standard electron is used, below it the
// LowPtElectron, falling back to whichever exists.
//
// IDENTIFICATION is stamped PER RECONSTRUCTION, not just for the winner, because the two
// collections carry different discriminants and an analysis may want either:
//   low_id / low_unbiased / low_ptbiased   the LowPtGsfElectron BDT scores
//   nominal_mva_iso / nominal_mva_noiso    the standard electron MVA (name varies by era, so
//                                          it is looked up defensively and left at -999 if absent)
//   {low,nominal}_{sieie,hoe,lost_hits,pass_conv_veto}   cut-based inputs for each reco
//   nominal_{einvminuspinv,deta_seed,dphi_in,r9}         the rest of the cut-based ID inputs
// Anything unavailable is -999 (floats) / -1 (ints) rather than throwing. Set the untracked
// parameter dumpIdNames=True to print, once, every userFloat and electronID the input
// collections actually carry -- the reliable way to discover era-specific names.
//
// Each output candidate also carries userInt("ele_idx") = the index into the collection the
// nominal choice came from, and userInt("ele_src") = 0 (LowPtElectron) or 1 (standard), so
// trk{1,2}_idx + trk{1,2}_src point at the right NanoAOD table row.

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/EgammaCandidates/interface/Conversion.h"
#include "DataFormats/EgammaCandidates/interface/ConversionFwd.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "CommonTools/Egamma/interface/ConversionTools.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "helper.h"   // TransientTrackCollection, ELECTRON_MASS

#include <algorithm>
#include <atomic>
#include <cmath>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

class LowPtEleMerger : public edm::global::EDProducer<> {
public:
  explicit LowPtEleMerger(const edm::ParameterSet &cfg):
    bFieldToken_(esConsumes<MagneticField, IdealMagneticFieldRecord>()),
    eleToken_(consumes<edm::View<pat::Electron>>(cfg.getParameter<edm::InputTag>("electrons"))),
    ele2Tag_(cfg.getParameter<edm::InputTag>("electrons2")),
    use_ele2_(!cfg.getParameter<edm::InputTag>("electrons2").label().empty()),
    ele2Token_(use_ele2_ ? consumes<edm::View<pat::Electron>>(ele2Tag_)
                         : edm::EDGetTokenT<edm::View<pat::Electron>>()),
    convToken_(consumes<reco::ConversionCollection>(cfg.getParameter<edm::InputTag>("conversions"))),
    dump_id_names_(cfg.getUntrackedParameter<bool>("dumpIdNames", false)),
    ele_selection_(cfg.getParameter<std::string>("electronSelection")),
    nominal_pt_(cfg.getParameter<double>("nominalPtThreshold")),
    match_dr_(cfg.getParameter<double>("overlapDeltaR")),
    match_dpt_(cfg.getParameter<double>("overlapRelPt"))
  {
    produces<pat::CompositeCandidateCollection>("SelectedElectrons");
    produces<TransientTrackCollection>("SelectedTransientElectrons");
    produces<TransientTrackCollection>("SelectedTransientElectronsLow");
    produces<TransientTrackCollection>("SelectedTransientElectronsNominal");
  }

  ~LowPtEleMerger() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions&) {}

private:
  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
  const edm::EDGetTokenT<edm::View<pat::Electron>> eleToken_;
  const edm::InputTag ele2Tag_;
  const bool use_ele2_;
  const edm::EDGetTokenT<edm::View<pat::Electron>> ele2Token_;
  const edm::EDGetTokenT<reco::ConversionCollection> convToken_;
  const bool dump_id_names_;
  const StringCutObjectSelector<pat::Electron> ele_selection_;
  const double nominal_pt_, match_dr_, match_dpt_;
};

namespace {
  // one reconstruction of one physical electron
  struct Reco {
    bool ok = false;
    int idx = -1;
    const pat::Electron* ele = nullptr;
    reco::GsfTrackRef gsf;
    float pt() const { return gsf->pt(); }
    float eta() const { return gsf->eta(); }
    float phi() const { return gsf->phi(); }
  };
  struct Merged { Reco low, nom; };
}

void LowPtEleMerger::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &stp) const {

  const auto& bField = stp.getData(bFieldToken_);

  edm::Handle<edm::View<pat::Electron>> electrons;
  evt.getByToken(eleToken_, electrons);
  edm::Handle<edm::View<pat::Electron>> electrons2;
  if (use_ele2_) evt.getByToken(ele2Token_, electrons2);

  // Photon conversions, for a PER-ELECTRON conversion tag. The NanoAOD LowPtElectron table
  // does carry convVtxRadius, but that branch is filled per EVENT -- every LowPtElectron in
  // an event shares one value -- so it cannot say which leg came from a conversion. Matching
  // each gsfTrack to the conversion collection here fixes that, and keeps the matched
  // conversion's own vertex radius, which is the quantity that separates a converted photon
  // (beam pipe ~2-3 cm, first pixel layers ~3-6 cm) from a prompt e+e- pair.
  edm::Handle<reco::ConversionCollection> conversions;
  evt.getByToken(convToken_, conversions);

  // ---- collect the two collections, then OR them into one list of physical electrons ----
  std::vector<Merged> merged;

  auto collect = [&](const edm::View<pat::Electron>& coll, bool is_nominal) {
    for (size_t i = 0; i < coll.size(); ++i) {
      const pat::Electron& ele = coll[i];
      if (!ele_selection_(ele)) continue;
      const auto gsf = ele.gsfTrack();
      if (gsf.isNull()) continue;

      Reco r; r.ok = true; r.idx = (int)i; r.ele = &ele; r.gsf = gsf;

      if (is_nominal) {                      // standard electrons seed the list
        Merged m; m.nom = r; merged.push_back(m);
        continue;
      }
      for (auto& m : merged) {               // LowPtElectron: attach to its counterpart if any
        if (!m.nom.ok) continue;
        if (reco::deltaR2(r.eta(), r.phi(), m.nom.eta(), m.nom.phi()) < match_dr_ * match_dr_ &&
            std::abs(r.pt() - m.nom.pt()) < match_dpt_ * m.nom.pt()) {
          if (!m.low.ok) m.low = r;
          r.ok = false;
          break;
        }
      }
      if (r.ok) { Merged m; m.low = r; merged.push_back(m); }
    }
  };
  if (use_ele2_ && electrons2.isValid()) collect(*electrons2, true);
  collect(*electrons, false);

  // --- defensive accessor: a missing ID must not throw. Checks electronIDs first (where the
  // LowPt BDT and the MVA/cut-based WPs live) then userFloats (the raw MVA values). ---------
  auto eid = [](const pat::Electron* e, const std::initializer_list<const char*>& names,
                float dflt) -> float {
    if (!e) return dflt;
    for (const char* n : names)
      if (e->isElectronIDAvailable(n)) return e->electronID(n);
    for (const char* n : names)
      if (e->hasUserFloat(n)) return e->userFloat(n);
    return dflt;
  };

  if (dump_id_names_) {
    // One flag PER COLLECTION, and only fire on a NON-EMPTY one: most parking events have no
    // electron at all, so dumping on the first event processed just prints "EMPTY".
    static std::atomic<bool> dumped_low{false}, dumped_nom{false};
    auto show = [](const char* tag, const edm::View<pat::Electron>& c,
                   std::atomic<bool>& flag) {
      if (c.empty()) return;
      bool expected = false;
      if (!flag.compare_exchange_strong(expected, true)) return;
      const pat::Electron& e = c[0];
      std::ostringstream u, d;
      for (const auto& n : e.userFloatNames()) u << " " << n;
      for (const auto& n : e.electronIDs())    d << " " << n.first;
      edm::LogPrint("LowPtEleMerger") << tag << " n=" << c.size() << " userFloats:" << u.str();
      edm::LogPrint("LowPtEleMerger") << tag << " electronIDs:" << d.str();
    };
    show("[LowPtElectron]", *electrons, dumped_low);
    if (use_ele2_ && electrons2.isValid()) show("[slimmedElectrons]", *electrons2, dumped_nom);
  }

  auto ele_out   = std::make_unique<pat::CompositeCandidateCollection>();
  auto trans_out = std::make_unique<TransientTrackCollection>();
  auto trans_low = std::make_unique<TransientTrackCollection>();
  auto trans_nom = std::make_unique<TransientTrackCollection>();

  for (const auto& m : merged) {
    // NOMINAL choice: standard reconstruction at/above the threshold, LowPtElectron below it,
    // falling back to whichever exists.
    bool use_nom;
    if (m.nom.ok && m.low.ok) use_nom = (m.nom.pt() >= nominal_pt_);
    else                      use_nom = m.nom.ok;
    const Reco& sel = use_nom ? m.nom : m.low;
    if (!sel.ok) continue;

    const reco::TransientTrack selTT((*sel.gsf), &bField);
    if (!selTT.isValid()) continue;
    const reco::TransientTrack lowTT(*(m.low.ok ? m.low.gsf : sel.gsf), &bField);
    const reco::TransientTrack nomTT(*(m.nom.ok ? m.nom.gsf : sel.gsf), &bField);

    pat::CompositeCandidate pcand;
    math::PtEtaPhiMLorentzVector p4(sel.pt(), sel.eta(), sel.phi(), ELECTRON_MASS);
    pcand.setP4(p4);
    pcand.setCharge(sel.gsf->charge());
    pcand.setVertex(reco::Candidate::Point(sel.gsf->vx(), sel.gsf->vy(), sel.gsf->vz()));
    pcand.setPdgId(-11 * sel.gsf->charge());
    pcand.addUserInt("ele_idx", sel.idx);          // index into the collection actually used
    pcand.addUserInt("ele_src", use_nom ? 1 : 0);  // 0 = LowPtElectron, 1 = standard
    pcand.addUserFloat("dz",  sel.gsf->dz());
    pcand.addUserFloat("dxy", sel.gsf->dxy());

    // both reconstructions, kept side by side
    pcand.addUserInt("has_low",     m.low.ok ? 1 : 0);
    pcand.addUserInt("has_nominal", m.nom.ok ? 1 : 0);
    pcand.addUserInt("low_idx",     m.low.ok ? m.low.idx : -1);
    pcand.addUserInt("nominal_idx", m.nom.ok ? m.nom.idx : -1);
    pcand.addUserFloat("low_pt",      m.low.ok ? m.low.pt()  : -1.f);
    pcand.addUserFloat("low_eta",     m.low.ok ? m.low.eta() : -999.f);
    pcand.addUserFloat("low_phi",     m.low.ok ? m.low.phi() : -999.f);
    pcand.addUserFloat("nominal_pt",  m.nom.ok ? m.nom.pt()  : -1.f);
    pcand.addUserFloat("nominal_eta", m.nom.ok ? m.nom.eta() : -999.f);
    pcand.addUserFloat("nominal_phi", m.nom.ok ? m.nom.phi() : -999.f);

    // GEOMETRIC conversion matching. The ref-based
    // ConversionTools::matchesConversion(GsfTrackRef, Conversion) does NOT work in MiniAOD --
    // the conversion's track refs and the electron's gsfTrack live in different products, so
    // it silently never matches (measured 0% on every leg). Compare momenta instead.
    int   conv_matched = 0;
    float conv_r = -1.f;   // -1 = no conversion matched to this electron
    float best_dr = 1e9f;
    if (conversions.isValid()) {
      for (const auto& conv : *conversions) {
        if (conv.nTracks() < 2) continue;
        const float r = std::sqrt(conv.conversionVertex().position().perp2());
        if (r < 0.f || r > 60.f) continue;              // inside the tracker
        for (const auto& pin : conv.tracksPin()) {
          const float dr = reco::deltaR(sel.gsf->eta(), sel.gsf->phi(), pin.eta(), pin.phi());
          if (dr > 0.1f) continue;
          if (std::abs(sel.gsf->pt() - pin.rho()) > 0.5f * pin.rho()) continue;
          if (dr < best_dr) { best_dr = dr; conv_matched = 1; conv_r = r; }
        }
      }
    }
    pcand.addUserFloat("conv_dr", conv_matched ? best_dr : -1.f);
    pcand.addUserInt("conv_matched", conv_matched);
    pcand.addUserFloat("conv_r", conv_r);

    // Quality handles stamped straight off the pat::Electron. Needed because the standard legs
    // are read as slimmedElectrons, NOT via finalElectrons: the NanoAOD Electron table depends
    // on slimmedElectronsWithUserData -> updatedJetsPuppi, i.e. the whole jet sequence, which
    // is far too heavy for a slim parking ntuple and only supplies jet-based isolation we do
    // not use. Both collections are pat::Electron, so these work for either source.
    pcand.addUserInt("lost_hits", sel.gsf->hitPattern().numberOfLostHits(
                                    reco::HitPattern::MISSING_INNER_HITS));
    pcand.addUserInt("pass_conv_veto", sel.ele->passConversionVeto() ? 1 : 0);
    pcand.addUserFloat("sieie", sel.ele->full5x5_sigmaIetaIeta());
    pcand.addUserFloat("hoe",   sel.ele->hcalOverEcal());

    // ---- identification, stamped separately for each reconstruction --------------------
    auto stamp_quality = [&](const char* pfx, const Reco& r) {
      std::string P(pfx);
      pcand.addUserInt(P + "lost_hits", r.ok ? (int)r.gsf->hitPattern().numberOfLostHits(
                                 reco::HitPattern::MISSING_INNER_HITS) : -1);
      pcand.addUserInt(P + "pass_conv_veto", r.ok ? (r.ele->passConversionVeto() ? 1 : 0) : -1);
      pcand.addUserFloat(P + "sieie", r.ok ? r.ele->full5x5_sigmaIetaIeta() : -999.f);
      pcand.addUserFloat(P + "hoe",   r.ok ? r.ele->hcalOverEcal()          : -999.f);
    };
    stamp_quality("low_",     m.low);
    stamp_quality("nominal_", m.nom);

    // LowPtGsfElectron BDT scores. VERIFIED by dumping a real 2025 parking MiniAOD: these are
    // electronIDs, NOT userFloats -- reading them with userFloat() silently yields nothing.
    const pat::Electron* le = m.low.ok ? m.low.ele : nullptr;
    pcand.addUserFloat("low_id",       eid(le, {"ID"},       -999.f));
    pcand.addUserFloat("low_unbiased", eid(le, {"unbiased"}, -999.f));
    pcand.addUserFloat("low_ptbiased", eid(le, {"ptbiased"}, -999.f));

    // Standard-electron MVA. BPH-24-001 uses the NO-ISOLATION discriminant, so that is the one
    // to cut on; the iso value is kept alongside for reference. Names carry the training
    // campaign, so the Run-3 (RunIIIWinter22) spelling is tried first and Fall17 V2 second --
    // both are present in the parking MiniAOD, which is reprocessed with the full EGamma suite.
    const pat::Electron* ne = m.nom.ok ? m.nom.ele : nullptr;
    pcand.addUserFloat("nominal_mva_noiso", eid(ne,
        {"ElectronMVAEstimatorRun2RunIIIWinter22NoIsoV1Values",
         "ElectronMVAEstimatorRun2Fall17NoIsoV2Values",
         "ElectronMVAEstimatorRun2Fall17NoIsoV1Values"}, -999.f));
    pcand.addUserFloat("nominal_mva_iso", eid(ne,
        {"ElectronMVAEstimatorRun2RunIIIWinter22IsoV1Values",
         "ElectronMVAEstimatorRun2Fall17IsoV2Values",
         "ElectronMVAEstimatorRun2Summer18ULIdIsoValues"}, -999.f));

    // Working points of the same no-isolation MVA, as flags.
    pcand.addUserInt("nominal_mva_noiso_wp80", (int)eid(ne,
        {"mvaEleID-RunIIIWinter22-noIso-V1-wp80", "mvaEleID-Fall17-noIso-V2-wp80"}, -1.f));
    pcand.addUserInt("nominal_mva_noiso_wp90", (int)eid(ne,
        {"mvaEleID-RunIIIWinter22-noIso-V1-wp90", "mvaEleID-Fall17-noIso-V2-wp90"}, -1.f));

    // Cut-based ID packed as a level: 0 fails veto, 1 veto, 2 loose, 3 medium, 4 tight, -1 if
    // unavailable. CAVEAT: the standard cut-based WPs INCLUDE an isolation cut, and the VID
    // nested bitmap that would let it be removed is not embedded in MiniAOD. For a genuinely
    // isolation-free selection use nominal_mva_noiso; this is here for cross-checks.
    int cb = -1;
    if (ne) {
      cb = 0;
      const char* lv[4][2] = {{"cutBasedElectronID-RunIIIWinter22-V1-veto",   "cutBasedElectronID-Fall17-94X-V2-veto"},
                              {"cutBasedElectronID-RunIIIWinter22-V1-loose",  "cutBasedElectronID-Fall17-94X-V2-loose"},
                              {"cutBasedElectronID-RunIIIWinter22-V1-medium", "cutBasedElectronID-Fall17-94X-V2-medium"},
                              {"cutBasedElectronID-RunIIIWinter22-V1-tight",  "cutBasedElectronID-Fall17-94X-V2-tight"}};
      for (int k = 0; k < 4; ++k)
        if (eid(ne, {lv[k][0], lv[k][1]}, 0.f) > 0.5f) cb = k + 1;
    }
    pcand.addUserInt("nominal_cutbased", cb);

    // Remaining cut-based ID inputs for the standard leg (always computable off pat::Electron).
    if (ne) {
      const float ecal = ne->ecalEnergy();
      pcand.addUserFloat("nominal_einvminuspinv",
                         ecal > 0.f ? (1.f - ne->eSuperClusterOverP()) / ecal : -999.f);
      pcand.addUserFloat("nominal_deta_seed", ne->deltaEtaSuperClusterTrackAtVtx());
      pcand.addUserFloat("nominal_dphi_in",   ne->deltaPhiSuperClusterTrackAtVtx());
      pcand.addUserFloat("nominal_r9",        ne->full5x5_r9());
    } else {
      pcand.addUserFloat("nominal_einvminuspinv", -999.f);
      pcand.addUserFloat("nominal_deta_seed",     -999.f);
      pcand.addUserFloat("nominal_dphi_in",       -999.f);
      pcand.addUserFloat("nominal_r9",            -999.f);
    }

    ele_out->emplace_back(pcand);
    trans_out->emplace_back(selTT);
    trans_low->emplace_back(lowTT);
    trans_nom->emplace_back(nomTT);
  }

  evt.put(std::move(ele_out),   "SelectedElectrons");
  evt.put(std::move(trans_out), "SelectedTransientElectrons");
  evt.put(std::move(trans_low), "SelectedTransientElectronsLow");
  evt.put(std::move(trans_nom), "SelectedTransientElectronsNominal");
}

DEFINE_FWK_MODULE(LowPtEleMerger);
