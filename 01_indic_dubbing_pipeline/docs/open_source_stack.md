# Open-source stack

## ASR

- **faster-whisper** uses CTranslate2 and is usually the practical CPU/GPU serving choice.
- **openai-whisper** is the reference Python implementation and provides a useful compatibility fallback.
- Both require local model weights. Selecting them can trigger a model download unless weights are already cached. Whisper code and model licenses must be reviewed for the deployment.

## Translation

AI4Bharat IndicTrans2 provides Indic-to-Indic and Indic/English translation checkpoints. Check each selected checkpoint's model card and license. The adapter imports Transformers lazily; weights can require substantial RAM/VRAM. Pre-download an approved checkpoint for controlled/offline deployment. Language tagging and model-specific preprocessing may need adjustment for a chosen checkpoint.

The translation requirements pin Transformers 4.51.3 because the checkpoint imports the legacy `transformers.onnx` module removed in Transformers 5.x, while its current tokenizer requires a modern 4.x tokenizer base. The adapter uses the official `IndicTransToolkit` when installed. Because its PyPI package requires a C++ compiler on Windows, a focused pure-Python Hindi/English preprocessing fallback is included for the configured Indic-to-English checkpoint.

## TTS

- **Piper** is a lightweight local neural TTS runtime. It requires a Piper executable plus a compatible `.onnx` voice model and configuration. Voice/model licenses vary and must be checked individually.
- **eSpeak-NG** is a compact system synthesizer. It is less natural but useful for integration and edge tests. Review its GPL licensing implications for distribution.

No TTS model or binary is downloaded by this project. The default creates a text placeholder artifact.

## Why optional adapters?

Lazy imports keep API startup and tests independent of large ML stacks. This separates control-plane reliability from model provisioning, reduces Docker size, and gives missing dependencies actionable errors.
