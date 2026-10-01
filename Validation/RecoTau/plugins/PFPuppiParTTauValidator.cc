// DQM validation for the HLT PFPuppi + ParticleTransformer tau strategy.
// The candidate is a PF jet and the score is a JetTag value; this is kept
// separate from TauValidator, whose inputs are reco::PFTau / pat::Tau.

#include "DQMServices/Core/interface/DQMEDAnalyzer.h"
#include "DQMServices/Core/interface/DQMStore.h"
#include "DataFormats/BTauReco/interface/JetTag.h"
#include "DataFormats/Common/interface/Handle.h"
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/Exception.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "PhysicsTools/JetMCUtils/interface/JetMCTag.h"

#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

class PFPuppiParTTauValidator : public DQMEDAnalyzer {
public:
  explicit PFPuppiParTTauValidator(const edm::ParameterSet&);
  void analyze(const edm::Event&, const edm::EventSetup&) override;
  void bookHistograms(DQMStore::IBooker&, edm::Run const&, edm::EventSetup const&) override;
  static void fillDescriptions(edm::ConfigurationDescriptions&);

private:
  edm::EDGetTokenT<reco::GenJetCollection> genTauToken_;
  edm::EDGetTokenT<edm::View<reco::Jet>> jetsToken_;
  edm::EDGetTokenT<reco::JetTagCollection> jetTagsToken_;
  edm::EDGetTokenT<edm::TriggerResults> triggerResultsToken_;
  const double genPtMin_, genEtaMax_, jetPtMin_, jetEtaMax_, scoreCut_, matchDR_;
  const std::string folder_, triggerPath_;
  std::vector<std::string> decayModes_;

  MonitorElement *genPt_{}, *genEta_{}, *genMass_{};
  MonitorElement *genMatchedPt_{}, *genMatchedEta_{}, *genMatchedMass_{};
  MonitorElement *jetPt_{}, *jetEta_{}, *jetMass_{}, *jetScore_{};
  MonitorElement *jetMatchedPt_{}, *jetMatchedEta_{}, *jetMatchedMass_{}, *jetMatchedScore_{};
  MonitorElement *fakeJetPt_{}, *fakeJetEta_{}, *fakeJetScore_{};
  MonitorElement *responsePt_{}, *scoreVsPt_{};
  MonitorElement *pathDenominator_{}, *pathAccepted_{};
  std::vector<MonitorElement*> genPtByDM_, genMatchedPtByDM_;
};

PFPuppiParTTauValidator::PFPuppiParTTauValidator(const edm::ParameterSet& cfg)
    : genTauToken_(consumes<reco::GenJetCollection>(cfg.getParameter<edm::InputTag>("genTauCollection"))),
      jetsToken_(consumes<edm::View<reco::Jet>>(cfg.getParameter<edm::InputTag>("jets"))),
      jetTagsToken_(consumes<reco::JetTagCollection>(cfg.getParameter<edm::InputTag>("jetTags"))),
      triggerResultsToken_(consumes<edm::TriggerResults>(cfg.getParameter<edm::InputTag>("triggerResults"))),
      genPtMin_(cfg.getParameter<double>("genPtMin")),
      genEtaMax_(cfg.getParameter<double>("genEtaMax")),
      jetPtMin_(cfg.getParameter<double>("jetPtMin")),
      jetEtaMax_(cfg.getParameter<double>("jetEtaMax")),
      scoreCut_(cfg.getParameter<double>("scoreCut")),
      matchDR_(cfg.getParameter<double>("genMatchDR")),
      folder_(cfg.getParameter<std::string>("outFolder")),
      triggerPath_(cfg.getParameter<std::string>("triggerPath")),
      decayModes_(cfg.getParameter<std::vector<std::string>>("decayModes")) {
  if (matchDR_ <= 0. || scoreCut_ < 0. || scoreCut_ > 1.)
    throw cms::Exception("Configuration") << "genMatchDR must be positive and scoreCut must be in [0,1]";
}

void PFPuppiParTTauValidator::bookHistograms(DQMStore::IBooker& booker,
                                             const edm::Run&,
                                             const edm::EventSetup&) {
  booker.setCurrentFolder(folder_);
  genPt_ = booker.book1D("genTau_pt", "Generated visible tau;p_{T} [GeV];", 100, 0., 500.);
  genEta_ = booker.book1D("genTau_eta", "Generated visible tau;#eta;", 60, -3., 3.);
  genMass_ = booker.book1D("genTau_mass", "Generated visible tau;m [GeV];", 80, 0., 4.);
  genMatchedPt_ = booker.book1D("genTauMatched_pt", "Matched generated visible tau;p_{T} [GeV];", 100, 0., 500.);
  genMatchedEta_ = booker.book1D("genTauMatched_eta", "Matched generated visible tau;#eta;", 60, -3., 3.);
  genMatchedMass_ = booker.book1D("genTauMatched_mass", "Matched generated visible tau;m [GeV];", 80, 0., 4.);

  jetPt_ = booker.book1D("recoJet_pt", "PFPuppi jet;p_{T} [GeV];", 100, 0., 500.);
  jetEta_ = booker.book1D("recoJet_eta", "PFPuppi jet;#eta;", 60, -3., 3.);
  jetMass_ = booker.book1D("recoJet_mass", "PFPuppi jet;m [GeV];", 80, 0., 80.);
  jetScore_ = booker.book1D("recoJet_score", "ParT TauvsAll score;score;Jets", 100, 0., 1.);
  jetMatchedPt_ = booker.book1D("recoJetMatched_pt", "PFPuppi jet matched to a gen tau;p_{T} [GeV];", 100, 0., 500.);
  jetMatchedEta_ = booker.book1D("recoJetMatched_eta", "PFPuppi jet matched to a gen tau;#eta;", 60, -3., 3.);
  jetMatchedMass_ = booker.book1D("recoJetMatched_mass", "PFPuppi jet matched to a gen tau;m [GeV];", 80, 0., 80.);
  jetMatchedScore_ = booker.book1D("recoJetMatched_score", "Matched PFPuppi jet;ParT score;Jets", 100, 0., 1.);
  fakeJetPt_ = booker.book1D("fakeJet_pt", "Selected PFPuppi jets not matched to a gen tau;p_{T} [GeV];", 100, 0., 500.);
  fakeJetEta_ = booker.book1D("fakeJet_eta", "Selected PFPuppi jets not matched to a gen tau;#eta;", 60, -3., 3.);
  fakeJetScore_ = booker.book1D("fakeJet_score", "Selected PFPuppi jets not matched to a gen tau;ParT score;Jets", 100, 0., 1.);
  responsePt_ = booker.book2D("responsePt", "PFPuppi jet / gen tau;p_{T}^{gen} [GeV];p_{T}^{jet}/p_{T}^{gen}", 100, 0., 500., 60, 0., 3.);
  scoreVsPt_ = booker.book2D("score_vs_pt", "ParT score vs jet p_{T};score;p_{T} [GeV]", 100, 0., 1., 100, 0., 500.);

  // A single bin-count pair is sufficient for an event-level path efficiency.
  pathDenominator_ = booker.book1D("pathDenominator", "Events with at least two gen taus;event;", 1, 0., 1.);
  pathAccepted_ = booker.book1D("pathAccepted", "Events passing the ParT double-tau path;event;", 1, 0., 1.);

  booker.setCurrentFolder(folder_ + "/GenDecayModes");
  for (const auto& dm : decayModes_) {
    genPtByDM_.push_back(booker.book1D("genTau_" + dm + "_pt", "Generated visible tau, " + dm + ";p_{T} [GeV];", 100, 0., 500.));
    genMatchedPtByDM_.push_back(booker.book1D("genTauMatched_" + dm + "_pt", "Matched generated visible tau, " + dm + ";p_{T} [GeV];", 100, 0., 500.));
  }
}

void PFPuppiParTTauValidator::analyze(const edm::Event& event, const edm::EventSetup&) {
  const auto genTaus = event.getHandle(genTauToken_);
  if (!genTaus.isValid()) {
    edm::LogWarning("PFPuppiParTTauValidator") << "Missing gen-tau collection; skipping event";
    return;
  }

  std::vector<const reco::GenJet*> selectedGen;
  for (const auto& tau : *genTaus) {
    if (tau.pt() < genPtMin_ || std::abs(tau.eta()) > genEtaMax_) continue;
    selectedGen.push_back(&tau);
    genPt_->Fill(tau.pt()); genEta_->Fill(tau.eta()); genMass_->Fill(tau.mass());
    const auto dm = JetMCTagUtils::genTauDecayMode(tau);
    const auto found = std::find(decayModes_.begin(), decayModes_.end(), dm);
    if (found != decayModes_.end()) genPtByDM_[std::distance(decayModes_.begin(), found)]->Fill(tau.pt());
  }

  // Fill the trigger denominator before reading HLT-only products. A failed
  // HLT path can legitimately leave its jet-tag product unavailable.
  if (selectedGen.size() >= 2) {
    pathDenominator_->Fill(0.5);
    const auto results = event.getHandle(triggerResultsToken_);
    if (results.isValid()) {
      const auto& names = event.triggerNames(*results);
      const auto index = names.triggerIndex(triggerPath_);
      if (index < results->size() && results->accept(index)) pathAccepted_->Fill(0.5);
    }
  }

  const auto jetTags = event.getHandle(jetTagsToken_);
  const auto jets = event.getHandle(jetsToken_);
  if (!jetTags.isValid() || !jets.isValid()) {
    LogDebug("PFPuppiParTTauValidator") << "Jet or JetTag collection absent, likely because the HLT path did not run";
    return;
  }

  std::vector<const reco::Jet*> selectedJets;
  std::vector<double> scores;
  for (std::size_t i = 0; i < jets->size(); ++i) {
    const auto jetRef = jets->refAt(i);
    const auto& jet = jets->at(i);
    const double score = (*jetTags)[jetRef];
    if (jet.pt() < jetPtMin_ || std::abs(jet.eta()) > jetEtaMax_) continue;
    selectedJets.push_back(&jet);
    scores.push_back(score);
    jetPt_->Fill(jetRef->pt()); jetEta_->Fill(jetRef->eta()); jetMass_->Fill(jetRef->mass());
    jetScore_->Fill(score); scoreVsPt_->Fill(score, jetRef->pt());
  }

  for (std::size_t i = 0; i < selectedGen.size(); ++i) {
    const auto& tau = *selectedGen[i];
    bool matched = false;
    const reco::Jet* bestJet = nullptr;
    double bestDR = matchDR_;
    for (std::size_t j = 0; j < selectedJets.size(); ++j) {
      if (scores[j] < scoreCut_) continue;
      const double dr = reco::deltaR(tau, *selectedJets[j]);
      if (dr < bestDR) { matched = true; bestDR = dr; bestJet = selectedJets[j]; }
    }
    if (!matched) continue;
    genMatchedPt_->Fill(tau.pt()); genMatchedEta_->Fill(tau.eta()); genMatchedMass_->Fill(tau.mass());
    jetMatchedPt_->Fill(bestJet->pt()); jetMatchedEta_->Fill(bestJet->eta());
    jetMatchedMass_->Fill(bestJet->mass());
    // The score is filled below through the nearest selected jet lookup.
    for (std::size_t j = 0; j < selectedJets.size(); ++j) {
      if (selectedJets[j] == bestJet) { jetMatchedScore_->Fill(scores[j]); break; }
    }
    if (tau.pt() > 0.) responsePt_->Fill(tau.pt(), bestJet->pt() / tau.pt());
    const auto dm = JetMCTagUtils::genTauDecayMode(tau);
    const auto found = std::find(decayModes_.begin(), decayModes_.end(), dm);
    if (found != decayModes_.end()) genMatchedPtByDM_[std::distance(decayModes_.begin(), found)]->Fill(tau.pt());
  }

  for (std::size_t j = 0; j < selectedJets.size(); ++j) {
    if (scores[j] < scoreCut_) continue;
    bool matched = false;
    for (const auto* tau : selectedGen) {
      if (reco::deltaR(*tau, *selectedJets[j]) < matchDR_) { matched = true; break; }
    }
    if (!matched) {
      fakeJetPt_->Fill(selectedJets[j]->pt()); fakeJetEta_->Fill(selectedJets[j]->eta());
      fakeJetScore_->Fill(scores[j]);
    }
  }

}

void PFPuppiParTTauValidator::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("genTauCollection", edm::InputTag("tauGenJetsSelectorAllHadrons"));
  desc.add<edm::InputTag>("jets", edm::InputTag("hltAK4PFPuppiJets"));
  desc.add<edm::InputTag>("jetTags", edm::InputTag("hltParticleTransformerDiscriminatorsJetTags", "TauvsAll"));
  desc.add<edm::InputTag>("triggerResults", edm::InputTag("TriggerResults", "", "HLTX"));
  desc.add<double>("genPtMin", 30.);
  desc.add<double>("genEtaMax", 2.1);
  desc.add<double>("jetPtMin", 30.);
  desc.add<double>("jetEtaMax", 2.1);
  desc.add<double>("scoreCut", 0.11645);
  desc.add<double>("genMatchDR", 0.3);
  desc.add<std::string>("triggerPath", "HLT_DoubleMediumPFPuppiParTTauh30_eta2p1");
  desc.add<std::string>("outFolder", "HLT/Tau/TauValidation/PFPuppiParT");
  desc.add<std::vector<std::string>>("decayModes", {"oneProng0Pi0", "oneProng1Pi0", "oneProng2Pi0", "oneProngOther", "threeProng0Pi0", "threeProng1Pi0", "threeProngOther", "rare", "unknown"});
  descriptions.addWithDefaultLabel(desc);
}

DEFINE_FWK_MODULE(PFPuppiParTTauValidator);
