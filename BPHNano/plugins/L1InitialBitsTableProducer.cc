// Stores the uGT *initial* decision (before prescale and masks) of a configured list of L1 seeds as a singleton
// NanoAOD table. NanoAOD's L1TriggerResultsConverter stores only the final decision, which is 0 for seeds that are
// prescaled off; in the 2026 special low-PU runs that includes all L1_MinimumBiasHF* seeds, although their initial
// decisions are evaluated for every event. This lets the ZeroBias data be filtered offline by a minimum-bias seed.
// Seeds missing from the run's menu are stored as false (warning once per run).
// Also HFSummaryTableProducer (below): per-side HF activity for an offline HF-coincidence emulation.

#include <algorithm>
#include <array>
#include <cmath>
#include <memory>
#include <string>
#include <vector>

#include "CondFormats/DataRecord/interface/L1TUtmTriggerMenuRcd.h"
#include "CondFormats/L1TObjects/interface/L1TUtmTriggerMenu.h"
#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/L1TGlobal/interface/GlobalAlgBlk.h"
#include "DataFormats/NanoAOD/interface/FlatTable.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"

class L1InitialBitsTableProducer : public edm::stream::EDProducer<> {
public:
  explicit L1InitialBitsTableProducer(const edm::ParameterSet& params)
      : token_(consumes<GlobalAlgBlkBxCollection>(params.getParameter<edm::InputTag>("src"))),
        menuToken_(esConsumes<edm::Transition::BeginRun>()),
        name_(params.getParameter<std::string>("name")),
        seeds_(params.getParameter<std::vector<std::string>>("seeds")) {
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src", edm::InputTag("gtStage2Digis"));
    desc.add<std::string>("name", "L1i");
    desc.add<std::vector<std::string>>("seeds", {});
    descriptions.addWithDefaultLabel(desc);
  }

private:
  void beginRun(edm::Run const& run, edm::EventSetup const& setup) override {
    const auto& algos = setup.getData(menuToken_).getAlgorithmMap();
    index_.assign(seeds_.size(), -1);
    for (size_t i = 0; i < seeds_.size(); ++i) {
      auto it = algos.find(seeds_[i]);
      if (it != algos.end())
        index_[i] = it->second.getIndex();
      else
        edm::LogWarning("L1InitialBitsTableProducer") << seeds_[i] << " not in the L1 menu of run " << run.run();
    }
  }

  void produce(edm::Event& event, const edm::EventSetup&) override {
    const auto& blk = event.get(token_);
    const std::vector<bool>* word = blk.isEmpty(0) ? nullptr : &blk.at(0, 0).getAlgoDecisionInitial();
    auto table = std::make_unique<nanoaod::FlatTable>(1, name_, true);
    table->setDoc("uGT initial (pre-prescale) decisions of selected L1 seeds");
    for (size_t i = 0; i < seeds_.size(); ++i) {
      const bool pass = word && index_[i] >= 0 && static_cast<size_t>(index_[i]) < word->size() && word->at(index_[i]);
      // column name: drop the "L1_" prefix, e.g. L1i_MinimumBiasHF0_AND_BptxAND
      const std::string col = seeds_[i].rfind("L1_", 0) == 0 ? seeds_[i].substr(3) : seeds_[i];
      table->addColumnValue<bool>(col, pass, "initial decision of " + seeds_[i]);
    }
    event.put(std::move(table));
  }

  const edm::EDGetTokenT<GlobalAlgBlkBxCollection> token_;
  const edm::ESGetToken<L1TUtmTriggerMenu, L1TUtmTriggerMenuRcd> menuToken_;
  const std::string name_;
  const std::vector<std::string> seeds_;
  std::vector<int> index_;
};

// Per-event HF summary from PF candidates (pdgId 1 = HF hadron, 2 = HF EM), per side (P: eta > 0, M: eta < 0):
// maximum energy, energy sum, and counts above the configured energy thresholds. Offline analogue of the
// L1 HF minimum-bias counts (HF coincidence) that also works for 0-PU MC.
class HFSummaryTableProducer : public edm::global::EDProducer<> {
public:
  explicit HFSummaryTableProducer(const edm::ParameterSet& params)
      : token_(consumes<edm::View<reco::Candidate>>(params.getParameter<edm::InputTag>("src"))),
        name_(params.getParameter<std::string>("name")),
        thresholds_(params.getParameter<std::vector<double>>("thresholds")) {
    produces<nanoaod::FlatTable>();
  }

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    edm::ParameterSetDescription desc;
    desc.add<edm::InputTag>("src", edm::InputTag("packedPFCandidates"));
    desc.add<std::string>("name", "HF");
    desc.add<std::vector<double>>("thresholds", {3., 5., 10., 20.});
    descriptions.addWithDefaultLabel(desc);
  }

  void produce(edm::StreamID, edm::Event& event, const edm::EventSetup&) const override {
    std::array<float, 2> emax{{0.f, 0.f}}, esum{{0.f, 0.f}};
    std::vector<std::array<int, 2>> n(thresholds_.size(), {{0, 0}});
    for (const auto& c : event.get(token_)) {
      const int id = std::abs(c.pdgId());
      if (id != 1 && id != 2)
        continue;
      const int side = c.eta() > 0 ? 0 : 1;
      const float e = c.energy();
      emax[side] = std::max(emax[side], e);
      esum[side] += e;
      for (size_t t = 0; t < thresholds_.size(); ++t)
        if (e > thresholds_[t])
          ++n[t][side];
    }
    auto table = std::make_unique<nanoaod::FlatTable>(1, name_, true);
    table->setDoc("HF PF-candidate summary per side (P: eta>0, M: eta<0)");
    const char* sides[2] = {"P", "M"};
    for (int s = 0; s < 2; ++s) {
      table->addColumnValue<float>(std::string("emax") + sides[s], emax[s], "max HF candidate energy [GeV]", 12);
      table->addColumnValue<float>(std::string("esum") + sides[s], esum[s], "sum of HF candidate energies [GeV]", 12);
      for (size_t t = 0; t < thresholds_.size(); ++t)
        table->addColumnValue<uint16_t>("n" + std::to_string(int(thresholds_[t])) + sides[s],
                                        static_cast<uint16_t>(std::min(n[t][s], 65535)),
                                        "HF candidates with E > " + std::to_string(int(thresholds_[t])) + " GeV");
    }
    event.put(std::move(table));
  }

private:
  const edm::EDGetTokenT<edm::View<reco::Candidate>> token_;
  const std::string name_;
  const std::vector<double> thresholds_;
};

DEFINE_FWK_MODULE(L1InitialBitsTableProducer);
DEFINE_FWK_MODULE(HFSummaryTableProducer);
