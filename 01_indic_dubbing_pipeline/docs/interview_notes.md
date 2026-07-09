# Interview notes

## What is ASR?

Automatic speech recognition converts an acoustic signal into text, commonly with timestamps and confidence information.

## What is TTS?

Text-to-speech synthesizes an audio waveform from text, ideally controlling voice, pronunciation, prosody, and duration.

## What are WER and CER?

WER is word-level edit distance divided by reference word count. CER applies the same calculation to normalized characters. Both capture substitutions, deletions, and insertions; CER is especially useful where tokenization is ambiguous. They assess transcription, not translation or voice naturalness.

## Why is Indic dubbing hard?

The system spans many scripts, phonologies, dialects, and uneven data coverage. Translation must preserve meaning while TTS must preserve pronunciation, emotion, speaker identity, and timing. Named entities and transliteration require explicit policy.

## Why are code-mixing and dialects hard?

Language can switch within a sentence, often written in a different script. Fixed language IDs, monolingual tokenizers, lexicons, and evaluation references then become unreliable. Dialect variation also creates valid outputs that literal metrics may penalize.

## Why does latency matter?

Interactive dubbing depends on end-to-end delay, not one model's speed. Tail latency, model loading, queueing, chunk boundaries, and audio playback buffering determine user experience. Real-time factor below one is necessary for sustained streaming.

## How would this become real-time?

Use streaming VAD and ASR, stable partial hypotheses, phrase-boundary incremental translation, streaming TTS, bounded queues, cached models, backpressure, and latency/quality monitoring. Revisions need a policy because already-played audio cannot be changed.

## How would this move to edge AI?

Choose compact models, export supported graphs to ONNX, apply dynamic/static quantization, and use ONNX Runtime or OpenVINO. Validate operator support and accuracy after conversion. Benchmark memory, thermal behavior, real-time factor, and cold start on the target device rather than relying on desktop throughput.

