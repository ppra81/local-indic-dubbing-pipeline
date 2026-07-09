# Indic Dubbing Pipeline

A recruiter-readable ML systems prototype for local, open-source speech dubbing:

```text
audio/video/transcript -> preprocessing -> ASR -> translation -> TTS
                       -> timing + WER/CER + latency -> JSON / CLI / FastAPI
```

The project demonstrates adapter design, typed interfaces, artifact persistence, evaluation, observability, API delivery, CLI ergonomics, tests, and containerization. It never calls a paid API. Stub mode is the default and works without model downloads; real backends are explicitly selected and provisioned locally.

## Operating modes

| Mode | Flags | Requirements |
|---|---|---|
| Stub (default) | `stub / stub / stub` | Core Python dependencies only |
| Local ASR | `faster-whisper` or `whisper` | Optional ASR package and downloaded/cached model |
| Open-source full | Local ASR + `indictrans2` + `piper`/`espeak` | Local weights, enough RAM/VRAM, and TTS executable/voice |

Stub TTS writes `dubbed_audio.placeholder.txt`, making the pipeline contract testable without pretending that placeholder content is playable audio.

For same-language text-to-speech, use `--translation-backend identity`; the text and segment timing pass through unchanged. `hi-IN` automatically selects the local eSpeak Hindi voice.

## Quick start

Python 3.10+ is required.

### Windows PowerShell

```powershell
cd 01_indic_dubbing_pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
pytest -q
.\scripts\run_demo_stub.ps1
python -m dubbing_pipeline.cli check-backends
uvicorn dubbing_pipeline.api:app --reload
```

### Linux/macOS

```bash
cd 01_indic_dubbing_pipeline
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
export PYTHONPATH=src
pytest -q
sh scripts/run_demo_stub.sh
python -m dubbing_pipeline.cli check-backends
uvicorn dubbing_pipeline.api:app --reload
```

The API is then available at `http://localhost:8000`; interactive docs are at `/docs`.

For the browser test console, open `/live`. It accepts typed text, audio-file uploads, or microphone recordings; runs the selected local pipeline; displays metadata; and plays the returned artifact. Microphone operation is push-to-talk near-live processing rather than continuous streaming.

## CLI example

```powershell
python -m dubbing_pipeline.cli run `
  --source-text "namaste, aaj hum speech AI system samjhenge" `
  --source-language hi-IN --target-language en-IN `
  --reference-text "namaste, aaj hum speech AI system samjhenge" `
  --output-dir outputs/demo_stub `
  --asr-backend stub --translation-backend stub --tts-backend stub
```

Expected artifacts:

```text
outputs/demo_stub/
  dubbed_audio.placeholder.txt
  result.json
```

`result.json` contains normalized WER/CER, segment metrics, timing metadata, adapter/model identity, and per-stage/total latency.

## Optional local ASR

```powershell
python -m pip install -r requirements-asr.txt
python -m dubbing_pipeline.cli run --audio-path sample.wav --asr-backend faster-whisper --model-size tiny --device cpu --compute-type int8 --translation-backend stub --tts-backend stub
```

Use `--asr-backend whisper` for the reference implementation. The first use commonly downloads model weights; cache or pre-provision them for offline/reproducible environments. Start with `tiny`/`base`, CPU, and `int8` for faster-whisper. OpenAI Whisper generally uses `float32` on CPU. No OpenAI cloud API is used.

## Optional IndicTrans2

```powershell
python -m pip install -r requirements-translation.txt
python -m dubbing_pipeline.cli run --source-text "नमस्ते" --translation-backend indictrans2 --tts-backend stub
```

The adapter defaults to an AI4Bharat checkpoint identifier and may download it through Transformers. Pre-download an approved model for offline use. IndicTrans2 checkpoints can need significant RAM/VRAM; production integration should pin a checkpoint revision and apply its documented language tags/preprocessing. The current adapter is a professional integration seam, not a claim of checkpoint-independent translation behavior.

## Optional Piper or eSpeak-NG

Install the system executable and ensure it is on `PATH`:

- `--tts-backend piper` requires a local compatible voice `.onnx` model. Set `PIPER_MODEL` to its path before running (for example, `$env:PIPER_MODEL = "C:\\voices\\hi_IN.onnx"` in PowerShell).
- `--tts-backend espeak` uses `espeak-ng` and defaults to the `en` voice.

No voices are downloaded. Review Piper runtime licensing, each voice model's license, and eSpeak-NG licensing before distribution. See [open-source stack](docs/open_source_stack.md).

## Docker

Docker installs only core dependencies and starts the stub-capable API—no heavy model weights are included:

```bash
docker compose up --build
curl http://localhost:8000/health
```

## API

- `GET /health` — liveness
- `GET /backends` — local package/executable discovery
- `POST /evaluate/transcript` — dependency-free WER/CER
- `POST /dubbing/jobs/run` — synchronous prototype job
- `POST /dubbing/jobs/upload` — multipart audio recording/file job
- `POST /dubbing/jobs/text` — form-based text-to-dubbed-audio job
- `GET /dubbing/jobs/{job_id}/audio` — generated audio artifact
- `GET /live` — browser microphone test page

## Limitations

- Stub translation is a deterministic label plus optional exact glossary replacement, not semantic translation.
- IndicTrans2 checkpoints have model-specific preprocessing and language-code requirements.
- Segment timing is preserved, but translated speech is not duration-aligned or lip-synced.
- Audio/video preprocessing commands are constructed but not implicitly executed.
- WER/CER evaluate ASR only; translation and TTS need bilingual human/automatic quality metrics and listening tests.
- API jobs are synchronous and local-disk based; there is no queue, authentication, quota, or object storage.

## Note

The repository covers the complete inference path and the engineering around models: interchangeable ASR/translation/TTS runtimes, language metadata, segment timing, objective ASR evaluation, latency instrumentation, reproducible interfaces, failure messages, packaging, tests, and deployment. It also makes the central production tradeoffs explicit: code-mixing, dialect coverage, model provisioning, voice licensing, temporal alignment, tail latency, streaming, and edge optimization.

Next implementation milestones are checkpoint-specific IndicTrans2 processing, explicit FFmpeg/VAD workers, temporal alignment, speaker/voice controls, queued jobs, dataset-sliced evaluation, streaming, and ONNX/OpenVINO benchmarking. See [architecture](docs/architecture.md), [extension plan](docs/extension_plan.md), and [interview notes](docs/interview_notes.md).

## GitHub reader guide

- [Project explanation](docs/project_explanation.md)
- [Demo walkthrough](docs/demo_walkthrough.md)
- [API reference](docs/api_reference.md)
- [Architecture](docs/architecture.md)
- [Open-source stack](docs/open_source_stack.md)
- [Extension plan](docs/extension_plan.md)
- [Interview notes](docs/interview_notes.md)
- [GitHub release checklist](docs/github_release_checklist.md)
