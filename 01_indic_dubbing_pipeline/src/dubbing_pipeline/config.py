"""Configuration validation and supported backend names."""

from __future__ import annotations

import os
from dataclasses import dataclass

ASR_BACKENDS = ("stub", "faster-whisper", "whisper")
TRANSLATION_BACKENDS = ("identity", "stub", "indictrans2")
TTS_BACKENDS = ("stub", "piper", "espeak")
MODEL_SIZES = ("tiny", "base", "small")
DEVICES = ("cpu", "cuda")
COMPUTE_TYPES = ("int8", "float16", "float32")
OFFLINE_ENV_VAR = "DUBBING_PIPELINE_OFFLINE"


def offline_mode_enabled() -> bool:
    """Default to offline operation; opt in to network-capable model loading explicitly."""
    return os.environ.get(OFFLINE_ENV_VAR, "1").lower() not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class PipelineConfig:
    asr_backend: str = "stub"
    translation_backend: str = "stub"
    tts_backend: str = "stub"
    model_size: str = "tiny"
    device: str = "cpu"
    compute_type: str = "int8"

    def __post_init__(self) -> None:
        choices = {
            "asr_backend": (self.asr_backend, ASR_BACKENDS),
            "translation_backend": (self.translation_backend, TRANSLATION_BACKENDS),
            "tts_backend": (self.tts_backend, TTS_BACKENDS),
            "model_size": (self.model_size, MODEL_SIZES),
            "device": (self.device, DEVICES),
            "compute_type": (self.compute_type, COMPUTE_TYPES),
        }
        for name, (value, allowed) in choices.items():
            if value not in allowed:
                raise ValueError(f"Invalid {name}={value!r}; choose one of: {', '.join(allowed)}")
        if self.device == "cpu" and self.compute_type == "float16":
            raise ValueError("float16 compute is intended for CUDA; use int8 or float32 on CPU")
