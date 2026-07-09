# Extension plan

1. Add explicit FFmpeg execution and preprocessing policies with integration tests.
2. Add checkpoint-specific IndicTrans2 language tags and batching.
3. Align translated segments to target speech duration; support pause and speaking-rate controls.
4. Add speaker diarization, voice selection, source separation, and loudness mixing.
5. Move synchronous jobs to a queue with object storage and idempotency keys.
6. Benchmark representative language, dialect, noise, gender, and code-mixing slices.
7. Export supported models to ONNX/OpenVINO, quantize, and measure edge real-time factor.
8. Add streaming VAD/ASR, incremental translation, and sentence-level TTS for real-time use.

