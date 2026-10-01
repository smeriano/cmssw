import FWCore.ParameterSet.Config as cms

def customisePFPuppiParT(process):
    process.load("Validation.RecoTau.hltPFPuppiParTValidation_cff")

    from Validation.RecoTau.hltPFPuppiParTValidation_cff import (
        setPFPuppiParTSeedMatchingDR,
    )
    setPFPuppiParTSeedMatchingDR(process, radius=0.3)

    process.hltPFPuppiParTValidationEndPath = cms.EndPath(
        process.hltPFPuppiParTValidationSequence
    )

    if hasattr(process, "schedule") and process.schedule is not None:
        schedule = list(process.schedule)
        endpath_names = set(process.endpaths_())
        insert_at = next(
            (i for i, path in enumerate(schedule)
             if path.label_() in endpath_names),
            len(schedule),
        )
        schedule.insert(insert_at, process.hltPFPuppiParTValidationEndPath)
        process.schedule = cms.Schedule(*schedule)

    return process