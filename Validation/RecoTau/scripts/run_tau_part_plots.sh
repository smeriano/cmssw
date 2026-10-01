#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${CMSSW_BASE:-}" ]]; then
  echo "ERROR: run this script from an initialized CMSSW area (cmsenv)." >&2
  exit 2
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 HARVESTED_DQM.root [DQM_FOLDER] [OUTPUT_DIR] [plotter options]" >&2
  exit 2
fi

DQM_FILE="$1"
shift
DQM_FOLDER="DQMData/Run 1/HLT/Run summary/Tau/TauValidation/PFPuppiParT"
OUTPUT_DIR="TauValidationPlots/PFPuppiParT"
if [[ $# -gt 0 && "$1" != --* ]]; then DQM_FOLDER="$1"; shift; fi
if [[ $# -gt 0 && "$1" != --* ]]; then OUTPUT_DIR="$1"; shift; fi
PLOTTER="${CMSSW_BASE}/src/Validation/RecoTau/scripts/makePFPuppiParTPlots.py"

python3 "${PLOTTER}" "${DQM_FILE}" --folder "${DQM_FOLDER}" --output "${OUTPUT_DIR}" "$@"
