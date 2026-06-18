#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/PatCandidates/interface/Photon.h"
#include "FWCore/Framework/interface/Event.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

class PATPhotonRefSelector : public edm::stream::EDFilter<>
{
public:
  explicit PATPhotonRefSelector(const edm::ParameterSet &cfg)
      : src_(consumes<pat::PhotonCollection>(cfg.getParameter<edm::InputTag>("src"))),
        cut_(cfg.getParameter<std::string>("cut")),
        selector_(cut_)
  {
    produces<pat::PhotonCollection>();
  }

  bool filter(edm::Event &iEvent, const edm::EventSetup &) override
  {
    edm::Handle<pat::PhotonCollection> photons;
    iEvent.getByToken(src_, photons);

    std::unique_ptr<pat::PhotonCollection> out(new pat::PhotonCollection);
    for (const auto &pho : *photons)
    {
      if (selector_(pho))
      {
        out->push_back(pho);
      }
    }
    iEvent.put(std::move(out));
    // Return true if at least one photon was selected (change logic if needed)
    return true;
  }

private:
  edm::EDGetTokenT<pat::PhotonCollection> src_;
  std::string cut_;
  StringCutObjectSelector<pat::Photon, true> selector_;
};

DEFINE_FWK_MODULE(PATPhotonRefSelector);

