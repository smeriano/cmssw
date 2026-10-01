import FWCore.ParameterSet.Config as cms

def customisePFPuppiParTHarvesting(process):
    process.load("Validation.RecoTau.hltPFPuppiParTValidation_cff")

    process.hltPFPuppiParTHarvestingPath = cms.Path(
        process.hltPFPuppiParTTauPostProcessor
    )

    if hasattr(process, "schedule") and process.schedule is not None:
        schedule = list(process.schedule)
        endpath_names = set(process.endpaths_())
        insert_at = next(
            (i for i, path in enumerate(schedule)
             if path.label_() in endpath_names),
            len(schedule),
        )
        schedule.insert(insert_at, process.hltPFPuppiParTHarvestingPath)
        process.schedule = cms.Schedule(*schedule)

    return process