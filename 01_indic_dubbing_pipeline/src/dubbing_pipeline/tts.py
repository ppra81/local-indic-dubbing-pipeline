"""Local TTS adapters. No model is downloaded automatically."""

from __future__ import annotations

import shutil
import subprocess
import wave
import os
from abc import ABC, abstractmethod
from pathlib import Path

from .audio import estimate_duration_from_text
from .schemas import TTSResult


class BaseTTSAdapter(ABC):
    @abstractmethod
    def synthesize(self, text: str, output_dir: str | Path, voice_id: str | None = None) -> TTSResult:
        raise NotImplementedError


class StubTTSAdapter(BaseTTSAdapter):
    def synthesize(self, text: str, output_dir: str | Path, voice_id: str | None = None) -> TTSResult:
        output_path = Path(output_dir) / "dubbed_audio.placeholder.txt"
        output_path.write_text("STUB TTS AUDIO ARTIFACT\n" + text + "\n", encoding="utf-8")
        return TTSResult(generated_audio_path=str(output_path), duration_seconds=estimate_duration_from_text(text), voice_id=voice_id or "stub-voice", sample_rate=16000, backend="stub")


def _wav_duration(path: Path) -> tuple[float, int]:
    with wave.open(str(path), "rb") as wav:
        rate = wav.getframerate()
        return (wav.getnframes() / rate if rate else 0.0, rate)


class PiperTTSAdapter(BaseTTSAdapter):
    def __init__(self, model_path: str | Path | None = None) -> None:
        self.model_path = Path(model_path) if model_path else None

    def synthesize(self, text: str, output_dir: str | Path, voice_id: str | None = None) -> TTSResult:
        executable = shutil.which("piper")
        if not executable:
            raise RuntimeError("Piper executable not found on PATH. Install Piper locally and provide a licensed voice model.")
        configured_model = os.environ.get("PIPER_MODEL")
        model = self.model_path or (Path(voice_id) if voice_id else None) or (Path(configured_model) if configured_model else None)
        if not model or not model.exists():
            raise RuntimeError("Piper requires an existing local voice model path. Set the PIPER_MODEL environment variable.")
        output_path = Path(output_dir) / "dubbed_audio.wav"
        subprocess.run([executable, "--model", str(model), "--output_file", str(output_path)], input=text, text=True, check=True, capture_output=True)
        duration, rate = _wav_duration(output_path)
        return TTSResult(generated_audio_path=str(output_path), duration_seconds=duration, voice_id=str(model), sample_rate=rate, backend="piper")


class EspeakTTSAdapter(BaseTTSAdapter):
    def synthesize(self, text: str, output_dir: str | Path, voice_id: str | None = None) -> TTSResult:
        executable = shutil.which("espeak-ng")
        if not executable:
            raise RuntimeError("espeak-ng executable not found on PATH. Install eSpeak-NG with your system package manager.")
        output_path = Path(output_dir) / "dubbed_audio.wav"
        voice = voice_id or "en"
        synthesis_text = text
        if voice.casefold() == "hindi" and any("\u0900" <= char <= "\u097f" for char in text):
            try:
                from indic_transliteration import sanscript
                from indic_transliteration.sanscript import transliterate
            except ImportError as exc:
                raise RuntimeError(
                    "Hindi eSpeak on Windows requires indic-transliteration; install requirements-tts.txt"
                ) from exc
            synthesis_text = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        subprocess.run([executable, "-v", voice, "-w", str(output_path), synthesis_text], check=True, capture_output=True, text=True)
        duration, rate = _wav_duration(output_path)
        return TTSResult(generated_audio_path=str(output_path), duration_seconds=duration, voice_id=voice, sample_rate=rate, backend="espeak")


def create_tts_adapter(backend: str) -> BaseTTSAdapter:
    if backend == "stub":
        return StubTTSAdapter()
    if backend == "piper":
        return PiperTTSAdapter()
    if backend == "espeak":
        return EspeakTTSAdapter()
    raise ValueError(f"Unsupported TTS backend: {backend}")
