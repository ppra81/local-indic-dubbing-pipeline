#!/usr/bin/env sh
set -eu
export PYTHONPATH=src
python -m dubbing_pipeline.cli run \
  --source-text "namaste, aaj hum speech AI system samjhenge" \
  --source-language hi-IN --target-language en-IN \
  --reference-text "namaste, aaj hum speech AI system samjhenge" \
  --output-dir outputs/demo_stub \
  --asr-backend stub --translation-backend stub --tts-backend stub

