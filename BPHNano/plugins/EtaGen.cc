#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "TrackingTools/PatternTools/interface/ClosestApproachInRPhi.h"
#include "TrackingTools/PatternTools/interface/TSCBLBuilderNoMaterial.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TrajectoryState/interface/TrajectoryStateTransform.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include <Math/Functions.h>
#include <Math/SMatrix.h>
#include <Math/SVector.h>
#include "CommonTools/CandUtils/interface/AddFourMomenta.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include <memory>
#include <typeinfo>

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/ConsumesCollector.h"

#include "DataFormats/Common/interface/RefToPtr.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "DataFormats/GeometryVector/interface/GlobalPoint.h"

#include "helper.h"
#include <memory>
#include <tuple>  // For std::tuple

class EtaGen : public edm::global::EDProducer<> {

public:
  explicit EtaGen(const edm::ParameterSet &theParameters):
      genParticleToken_(consumes<reco::GenParticleCollection>(theParameters.getParameter<edm::InputTag>("genParticle")))
	{
          produces<pat::CompositeCandidateCollection>("EtaGenmatch");
  }

  ~EtaGen() override {}

  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions & descriptions) {}

private:
  const edm::EDGetTokenT<reco::GenParticleCollection> genParticleToken_;
};


int GetEtaGlobalIndex(const reco::Candidate *cand, const edm::Handle<reco::GenParticleCollection> &handle) {
    for (size_t j = 0; j < handle->size(); j++) {
        if (&(*handle)[j] == cand) return j;
    }
    return -1;
}

void EtaGen::produce(edm::StreamID, edm::Event &iEvent, edm::EventSetup const &iSetup) const {


  edm::Handle<reco::GenParticleCollection> genParticles;
  iEvent.getByToken(genParticleToken_, genParticles);
  if (!genParticles.isValid()) {
    edm::LogError("BplusToD0KstarGen") << "GenParticles not found!";
    return;
  }

  std::unique_ptr<pat::CompositeCandidateCollection> out(new pat::CompositeCandidateCollection());


  for (size_t i = 0; i < genParticles->size(); i++) {
    const reco::Candidate *eta = &(*genParticles)[i];
    int pdgid = eta->pdgId();
    if (abs(pdgid) != 221 && abs(pdgid) != 331)
      continue; 

    int status = eta->status();
    //if (status!=2) continue;

    // skip obvious intermediates or duplicates
    if (eta->numberOfDaughters() < 2)
      continue;

    std::vector<int> muonIdx;
    std::vector<int> pionIdx;

    for (size_t j = 0; j < eta->numberOfDaughters(); ++j) {
      const reco::Candidate *dau = eta->daughter(j);
      int dauId = abs(dau->pdgId());
      if (dauId == 13)
        muonIdx.push_back(GetEtaGlobalIndex(dau, genParticles));
      else if (dauId == 211)
        pionIdx.push_back(GetEtaGlobalIndex(dau, genParticles));
    }

    // Identify decay mode
    int decayMode;
    if (muonIdx.size() == 2 && pionIdx.size() == 0)
      decayMode = 0; //"2Mu";
    else if (muonIdx.size() == 4 && pionIdx.size() == 0)
      decayMode = 1; //"4Mu";
    else if (muonIdx.size() == 2 && pionIdx.size() == 2)
      decayMode = 2; //"2Mu2Pi";
    else
      decayMode = -1; // unknown

    // Build candidate
    pat::CompositeCandidate cand;
    cand.setP4(eta->p4());
    cand.addUserInt("idx_eta", GetEtaGlobalIndex(eta, genParticles));
    cand.addUserInt("pdgId_eta", pdgid);
    cand.addUserInt("nMu", muonIdx.size());
    cand.addUserInt("nPi", pionIdx.size());
    cand.addUserInt("isEtaPrime", (abs(pdgid) == 331));
    cand.addUserFloat("mass", eta->mass());
    cand.addUserInt("decayMode", decayMode);

    // Store daughter indices
    for (unsigned int k = 0; k < muonIdx.size(); ++k)
      cand.addUserInt(Form("idx_mu%d", k + 1), muonIdx[k]);
    if (muonIdx.size()<4){
      for (unsigned int k = muonIdx.size(); k < 4; ++k)
        cand.addUserInt(Form("idx_mu%d", k + 1), -1);
    }

    for (unsigned int k = 0; k < pionIdx.size(); ++k)
      cand.addUserInt(Form("idx_pi%d", k + 1), pionIdx[k]);
    if (pionIdx.size()<2){
      for (unsigned int k = pionIdx.size(); k < 2; ++k)
        cand.addUserInt(Form("idx_pi%d", k + 1), -1);
    }
    out->push_back(cand);
  }

  iEvent.put(std::move(out), "EtaGenmatch"); // Changed output label

}

DEFINE_FWK_MODULE(EtaGen);

