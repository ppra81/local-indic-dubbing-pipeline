# Project Explanation

## Plain-English Summary

Indic Dubbing Pipeline is a local AI prototype that turns speech or text into a dubbed output. It demonstrates the engineering path for a speech-to-speech system:

```text
audio or text -> speech recognition -> translation -> speech generation -> metrics and artifacts
```

The first version runs in stub mode by default, so the full system can be tested without downloading large AI models. Optional local backends can be enabled later for real speech recognition, translation, and text-to-speech.

## What Problem It Solves

Dubbing systems need more than one model. A practical system must coordinate speech-to-text, translation, text-to-speech, timing metadata, quality metrics, latency measurements, saved artifacts, API access, and CLI access.

## Key Terms

- **Speech recognition (ASR):** Converts audio into text.
- **Translation:** Converts text from one language to another.
- **Text-to-speech (TTS):** Converts text into generated speech.
- **WER:** Word error rate, a speech recognition quality metric.
- **CER:** Character error rate, useful when scripts and tokenization are complex.
- **Latency:** How long each pipeline stage takes.
- **Stub backend:** A deterministic fake backend used to test the system without heavy dependencies.
- **Adapter:** A small class that hides backend-specific details behind a stable interface.

## Why It Is Useful As A Portfolio Project

The project shows production-minded ML engineering:

- typed schemas
- interchangeable model backends
- local-first operation
- optional dependency handling
- CLI and API delivery
- artifact persistence
- latency and quality metrics
- test coverage
- Docker support
- clear extension path toward real-time dubbing

## What Makes Indic Dubbing Hard

Indic speech systems must handle multiple scripts, dialects, code-mixing, named entities, pronunciation differences, and uneven model coverage. A production system also needs timing alignment so translated speech fits the source audio naturally.

## Current Scope

The default implementation is intentionally lightweight. It proves the pipeline contract, API, CLI, metrics, and output structure. Real local backends can be selected when their packages, model weights, and system executables are installed.
