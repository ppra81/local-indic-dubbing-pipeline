# Demo Walkthrough

Use this guide when presenting the project.

## 1. Start The API

```bash
cd 01_indic_dubbing_pipeline
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m uvicorn dubbing_pipeline.api:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/live
```

## 2. Explain The Project In 30 Seconds

This is a local AI dubbing pipeline. It accepts text or audio, runs it through speech recognition, translation, and speech generation stages, then reports quality and timing metrics. The default mode uses stub backends, so the engineering pipeline works without large model downloads.

## 3. Show The Browser Console

Open `/live` and point out source and target language, translation backend, speech output backend, text input, audio upload, microphone recording, JSON result output, and generated audio or placeholder artifact.

## 4. Run A Text Demo

Use same-language settings for a dependency-free demo:

- Source language: `en-IN`
- Target language: `en-IN`
- Translation: `Identity`
- Speech output: `Placeholder`

Enter:

```text
Today we are testing a local AI dubbing pipeline.
```

Click **Dub text**.

## 5. Explain The Output

The result includes source and target language, segment text, selected backends, WER and CER metrics, per-stage latency, and output artifact path.

## 6. CLI Demo

```bash
python -m dubbing_pipeline.cli run --source-text "namaste, aaj hum local speech system test kar rahe hain" --source-language hi-IN --target-language en-IN --reference-text "namaste, aaj hum local speech system test kar rahe hain" --output-dir outputs/demo_stub --asr-backend stub --translation-backend stub --tts-backend stub
```

## 7. API Demo

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/backends
```

## 8. Portfolio Talking Points

- The project is local-first and open-source.
- Stub mode proves the full contract without heavy models.
- Optional adapters support real local ASR, translation, and TTS.
- Metrics and artifacts are saved for reproducibility.
- The design can evolve toward streaming, queuing, and edge deployment.
