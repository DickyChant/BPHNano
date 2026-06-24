//////////////////////////// ElectronMerger ////////////////////////////
// Build a selected pat::ElectronCollection + a PARALLEL transient-track vector from the
// standard MiniAOD electrons (slimmedElectrons), to feed DiElectronBuilder (the e+e- leg of
// Z->ee V). This is the electron analog of MuonTriggerSelector's AllMuons/AllTransientMuons:
// DiLeptonBuilder<pat::Electron> indexes the lepton collection and the transient-track
// collection in parallel (l1_idx into both), so the two outputs MUST stay index-aligned.
// (LowPtEleMerger emits CompositeCandidates for the *track* leg of 2mu2e; here we need the
// electrons themselves as the DILEPTON legs, hence pat::ElectronCollection.)

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/Common/interface/View.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "helper.h"   // TransientTrackCollection

#include <memory>
#include <vector>

class ElectronMerger : public edm::global::EDProducer<> {
public:
  explicit ElectronMerger(const edm::ParameterSet &cfg):
    bFieldToken_(esConsumes<MagneticField, IdealMagneticFieldRecord>()),
    eleToken_(consumes<edm::View<pat::Electron>>(cfg.getParameter<edm::InputTag>("electrons"))),
    ele_selection_(cfg.getParameter<std::string>("electronSelection")),
    id_name_(cfg.getParameter<std::string>("electronID")),
    id_min_(cfg.getParameter<double>("electronIDmin"))
  {
    produces<pat::ElectronCollection>("Electrons");
    produces<TransientTrackCollection>("TransientElectrons");
  }

  ~ElectronMerger() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions&) {}

private:
  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
  const edm::EDGetTokenT<edm::View<pat::Electron>> eleToken_;
  const StringCutObjectSelector<pat::Electron> ele_selection_;
  const std::string id_name_;   // embedded electron-ID name (empty = no ID cut)
  const double id_min_;         // pass threshold (cut-based WP returns 1.0/0.0 -> use 0.5)
};

void ElectronMerger::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &stp) const {

  const auto& bField = stp.getData(bFieldToken_);

  edm::Handle<edm::View<pat::Electron>> electrons;
  evt.getByToken(eleToken_, electrons);

  std::unique_ptr<pat::ElectronCollection>  ele_out(new pat::ElectronCollection);
  std::unique_ptr<TransientTrackCollection>  trans_out(new TransientTrackCollection);

  for (size_t i = 0; i < electrons->size(); ++i) {
    const pat::Electron& ele = (*electrons)[i];
    if (!ele_selection_(ele)) continue;
    if (!id_name_.empty() && ele.electronID(id_name_) < id_min_) continue;   // embedded WP, in C++

    const auto gsf = ele.gsfTrack();
    if (gsf.isNull()) continue;
    const reco::TransientTrack eleTT((*gsf), &bField);   // GsfTrack is-a reco::Track
    if (!eleTT.isValid()) continue;

    pat::Electron ecopy = ele;
    ecopy.addUserInt("ele_idx", (int)i);                 // original slimmedElectrons index
    ele_out->push_back(ecopy);
    trans_out->push_back(eleTT);
  }

  evt.put(std::move(ele_out),   "Electrons");
  evt.put(std::move(trans_out), "TransientElectrons");
}

DEFINE_FWK_MODULE(ElectronMerger);
