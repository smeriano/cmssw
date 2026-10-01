"""Strategy selector for the high-level HLT tau-validation workflow.

Call makeHLTTauValidationSequence("HPSDeepTau") for the existing tau-object
validator, or makeHLTTauValidationSequence("PFPuppiParT") when the 75e33 ParT
path and its PFPuppi jet-tag products are in the process.
"""

import FWCore.ParameterSet.Config as cms


def makeHLTTauValidationSequence(strategy="HPSDeepTau"):
    if strategy == "HPSDeepTau":
        from Validation.RecoTau.hltTauValidation_cff import hltTauValidationSequence
        return hltTauValidationSequence
    if strategy == "PFPuppiParT":
        from Validation.RecoTau.hltPFPuppiParTValidation_cff import hltPFPuppiParTValidationSequence
        return hltPFPuppiParTValidationSequence
    raise ValueError("Unknown HLT tau-validation strategy: {}".format(strategy))


def makeHLTTauPostProcessor(strategy="HPSDeepTau"):
    if strategy == "HPSDeepTau":
        from Validation.RecoTau.hltTauPostProcessor_cff import hltTauPostProcessor
        return hltTauPostProcessor
    if strategy == "PFPuppiParT":
        from Validation.RecoTau.hltPFPuppiParTValidation_cff import hltPFPuppiParTTauPostProcessor
        return hltPFPuppiParTTauPostProcessor
    raise ValueError("Unknown HLT tau-validation strategy: {}".format(strategy))
