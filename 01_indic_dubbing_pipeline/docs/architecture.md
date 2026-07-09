# Architecture

```text
audio/video/transcript
        |
        v
preprocessing metadata --> ASR --> translation --> TTS --> artifacts
                              |          |           |
                              +---- timing metadata -+
                              |
                              +--> WER/CER + per-stage latency --> result.json / API
```

`DubbingPipeline` is the orchestration boundary. Adapters isolate model-specific concerns and return stable Pydantic contracts. Stub adapters make control flow, persistence, metrics, CLI, and API testable without weights or system binaries. Optional adapters load dependencies only when selected.

The prototype reports source metadata but deliberately does not execute FFmpeg implicitly. A production preprocessing worker would explicitly run mono/16 kHz conversion, VAD, SNR checks, silence handling, and chunking before ASR.

Jobs are synchronous for clarity. A production service would enqueue immutable job specifications, store artifacts in object storage, and expose job state separately.

