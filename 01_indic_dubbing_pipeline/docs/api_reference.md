# API Reference

Base URL:

```text
http://127.0.0.1:8000
```

## GET /health

Returns service status.

Example response:

```json
{
  "status": "ok"
}
```

## GET /backends

Reports which optional local packages or executables are available.

Backend groups:

- `asr`
- `translation`
- `tts`

## POST /evaluate/transcript

Computes transcript quality metrics.

Example request:

```json
{
  "reference": "hello world",
  "hypothesis": "hello word"
}
```

Returns word error rate and character error rate.

## POST /dubbing/jobs/run

Runs a synchronous dubbing job from JSON.

## POST /dubbing/jobs/text

Runs text input through translation and TTS.

Form fields:

- `text`
- `source_language`
- `target_language`
- `translation_backend`
- `tts_backend`

## POST /dubbing/jobs/upload

Uploads an audio file and runs a dubbing job.

Accepted audio extensions:

- `.wav`
- `.mp3`
- `.m4a`
- `.ogg`
- `.webm`
- `.flac`

## GET /dubbing/jobs/{job_id}/audio

Returns the generated audio artifact or placeholder artifact.

## GET /live

Returns the browser test console for text, audio upload, and microphone demos.
