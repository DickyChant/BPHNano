//////////////////////////// LowPtEleMerger ////////////////////////////
// Build a "track-like" pat::CompositeCandidate collection + a parallel transient-track
// vector from the central LowPtElectron collection (finalLowPtElectrons), to feed the
// Upsilon->2mu2e 4-track KinematicVertexFit with ELECTRON legs instead of generic tracks
// (which exploded the combinatorics). LowPtElectrons are few per event, so no sorting /
// overlap-cleaning is needed. Each output candidate carries userInt("ele_idx") = its index
// into the input LowPtElectron collection, so the 2mu2e trk{1,2}_idx map straight onto the
// central LowPtElectron NanoAOD table (which is built from the same finalLowPtElectrons).

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Common/interface/View.h"   // finalLowPtElectrons is a RefVector -> read as a View

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "helper.h"   // TransientTrackCollection, ELECTRON_MASS

#include <memory>
#include <vector>

class LowPtEleMerger : public edm::global::EDProducer<> {
public:
  explicit LowPtEleMerger(const edm::ParameterSet &cfg):
    bFieldToken_(esConsumes<MagneticField, IdealMagneticFieldRecord>()),
    eleToken_(consumes<edm::View<pat::Electron>>(cfg.getParameter<edm::InputTag>("electrons"))),
    ele_selection_(cfg.getParameter<std::string>("electronSelection"))
  {
    produces<pat::CompositeCandidateCollection>("SelectedElectrons");
    produces<TransientTrackCollection>("SelectedTransientElectrons");
  }

  ~LowPtEleMerger() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions&) {}

private:
  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
  const edm::EDGetTokenT<edm::View<pat::Electron>> eleToken_;
  const StringCutObjectSelector<pat::Electron> ele_selection_;
};

void LowPtEleMerger::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &stp) const {

  const auto& bField = stp.getData(bFieldToken_);

  edm::Handle<edm::View<pat::Electron>> electrons;
  evt.getByToken(eleToken_, electrons);

  std::unique_ptr<pat::CompositeCandidateCollection> ele_out(new pat::CompositeCandidateCollection);
  std::unique_ptr<TransientTrackCollection>          trans_out(new TransientTrackCollection);

  for (size_t i = 0; i < electrons->size(); ++i) {
    const pat::Electron& ele = (*electrons)[i];
    if (!ele_selection_(ele)) continue;

    const auto gsf = ele.gsfTrack();
    if (gsf.isNull()) continue;
    const reco::TransientTrack eleTT((*gsf), &bField);   // GsfTrack is-a reco::Track
    if (!eleTT.isValid()) continue;

    pat::CompositeCandidate pcand;
    math::PtEtaPhiMLorentzVector p4(gsf->pt(), gsf->eta(), gsf->phi(), ELECTRON_MASS);
    pcand.setP4(p4);
    pcand.setCharge(gsf->charge());
    pcand.setVertex(reco::Candidate::Point(gsf->vx(), gsf->vy(), gsf->vz()));
    pcand.setPdgId(-11 * gsf->charge());                 // 11 for e-, -11 for e+
    pcand.addUserInt("ele_idx", (int)i);                 // index into the LowPtElectron table
    pcand.addUserFloat("dz",  gsf->dz());
    pcand.addUserFloat("dxy", gsf->dxy());

    ele_out->emplace_back(pcand);
    trans_out->emplace_back(eleTT);
  }

  evt.put(std::move(ele_out),   "SelectedElectrons");
  evt.put(std::move(trans_out), "SelectedTransientElectrons");
}

DEFINE_FWK_MODULE(LowPtEleMerger);
