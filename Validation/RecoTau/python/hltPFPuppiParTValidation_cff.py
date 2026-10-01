import FWCore.ParameterSet.Config as cms
from DQMServices.Core.DQMEDHarvester import DQMEDHarvester

hltPFPuppiParTTauValidation = cms.EDProducer(
    "PFPuppiParTTauValidator",
    genTauCollection=cms.InputTag("tauGenJetsSelectorAllHadrons"),
    jets=cms.InputTag("hltAK4PFPuppiJets"),
    jetTags=cms.InputTag("hltParticleTransformerDiscriminatorsJetTags", "TauvsAll"),
    triggerResults=cms.InputTag("TriggerResults", "", "HLTX"),
    # Denominator follows the nominal HLT threshold for turn-on efficiency.
    genPtMin=cms.double(30.0),
    genEtaMax=cms.double(2.1),
    jetPtMin=cms.double(30.0),
    jetEtaMax=cms.double(2.1),
    scoreCut=cms.double(0.11645),
    # This is gen-visible-tau to HLT-jet matching. The HLT filter's
    # seed-matching radius is a separate setting on TauTagFilter.
    genMatchDR=cms.double(0.3),
    triggerPath=cms.string("HLT_DoubleMediumPFPuppiParTTauh30_eta2p1"),
    outFolder=cms.string("HLT/Tau/TauValidation/PFPuppiParT"),
    decayModes=cms.vstring(
        "oneProng0Pi0", "oneProng1Pi0", "oneProng2Pi0", "oneProngOther",
        "threeProng0Pi0", "threeProng1Pi0", "threeProngOther", "rare", "unknown"
    ),
)

# The inclusive module uses the PR's nominal working point. Additional clones
# make the efficiency/fake-rate curve without rebuilding the event products.
hltPFPuppiParTTauValidation_score0p00 = hltPFPuppiParTTauValidation.clone(
    scoreCut=0.0,
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p00",
)
hltPFPuppiParTTauValidation_score0p05 = hltPFPuppiParTTauValidation.clone(
    scoreCut=0.05,
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p05",
)
hltPFPuppiParTTauValidation_score0p10 = hltPFPuppiParTTauValidation.clone(
    scoreCut=0.10,
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p10",
)
hltPFPuppiParTTauValidation_score0p11645 = hltPFPuppiParTTauValidation.clone(
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p11645",
)
hltPFPuppiParTTauValidation_score0p15 = hltPFPuppiParTTauValidation.clone(
    scoreCut=0.15,
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p15",
)
hltPFPuppiParTTauValidation_score0p20 = hltPFPuppiParTTauValidation.clone(
    scoreCut=0.20,
    outFolder="HLT/Tau/TauValidation/PFPuppiParT/Score0p20",
)

hltPFPuppiParTValidationSequence = cms.Sequence(
    hltPFPuppiParTTauValidation
    + hltPFPuppiParTTauValidation_score0p00
    + hltPFPuppiParTTauValidation_score0p05
    + hltPFPuppiParTTauValidation_score0p10
    + hltPFPuppiParTTauValidation_score0p11645
    + hltPFPuppiParTTauValidation_score0p15
    + hltPFPuppiParTTauValidation_score0p20
)


def setPFPuppiParTSeedMatchingDR(process, radius=0.3):
    """Set TauTagFilter's seed-match radius independently of genMatchDR."""
    module = "hltDoublePFJets30ParTTauhTagMediumWPL2DoubleTau"
    if not hasattr(process, module):
        raise RuntimeError(
            "Load the HLT_75e33 configuration containing " + module + " before setting its matchingdR"
        )
    getattr(process, module).matchingdR = cms.double(radius)
    return process


_partHistograms = (
    "Efficiency_vs_pt 'Tau efficiency vs p_{T}' genTauMatched_pt genTau_pt",
    "Efficiency_vs_eta 'Tau efficiency vs #eta' genTauMatched_eta genTau_eta",
    "FakeRate_vs_pt 'Jet fake rate vs p_{T}' fakeJet_pt recoJet_pt",
    "FakeRate_vs_eta 'Jet fake rate vs #eta' fakeJet_eta recoJet_eta",
    "ScoreMatched 'ParT score for matched jets' recoJetMatched_score recoJet_score",
    "ScoreFake 'ParT score for fake jets' fakeJet_score recoJet_score",
    "EventPathEfficiency 'Double-tau path efficiency' pathAccepted pathDenominator",
)

hltPFPuppiParTTauPostProcessor = DQMEDHarvester(
    "DQMGenericClient",
    subDirs=cms.untracked.vstring(
        "HLT/Tau/TauValidation/PFPuppiParT/",
        "HLT/Tau/TauValidation/PFPuppiParT/Score*",
    ),
    efficiency=cms.vstring(),
    efficiencyProfile=cms.untracked.vstring(*_partHistograms),
    resolution=cms.vstring(),
    resolutionProfile=cms.untracked.vstring(
        "PtResponse 'Jet/gen tau p_{T} response' responsePt rms",
    ),
    verbose=cms.untracked.uint32(1),
    outputFileName=cms.untracked.string(""),
)