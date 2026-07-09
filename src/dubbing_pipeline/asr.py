"""Local ASR adapters with lazy optional imports."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .audio import create_segments_from_text
from .schemas import ASRResult, Segment

ASR_INSTALL_MESSAGE = "Install optional ASR dependencies with pip install -r requirements-asr.txt"


class BaseASRAdapter(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str | Path | None, source_text: str | None, language: str) -> ASRResult:
        raise NotImplementedError


class StubASRAdapter(BaseASRAdapter):
    def transcribe(self, audio_path: str | Path | None = None, source_text: str | None = None, language: str = "hi-IN") -> ASRResult:
        if source_text is None:
            source_text = f"[stub transcript for {Path(audio_path).name}]" if audio_path else ""
        return ASRResult(text=source_text, language=language, confidence=1.0, segments=create_segments_from_text(source_text), backend="stub", model_name="stub-asr")


class FasterWhisperASRAdapter(BaseASRAdapter):
    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8") -> None:
        self.model_size, self.device, self.compute_type = model_size, device, compute_type

    def transcribe(self, audio_path: str | Path | None, source_text: str | None = None, language: str = "hi-IN") -> ASRResult:
        if not audio_path:
            raise ValueError("faster-whisper requires --audio-path")
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(ASR_INSTALL_MESSAGE) from exc
        model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        raw_segments, info = model.transcribe(str(audio_path), language=language.split("-")[0])
        segments = [Segment(id=i, text=s.text.strip(), start=float(s.start), end=float(s.end), confidence=None) for i, s in enumerate(raw_segments)]
        text = " ".join(segment.text for segment in segments).strip()
        confidence = float(getattr(info, "language_probability", 0.0))
        return ASRResult(text=text, language=getattr(info, "language", language), confidence=confidence, segments=segments, backend="faster-whisper", model_name=self.model_size)


class WhisperASRAdapter(BaseASRAdapter):
    def __init__(self, model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8") -> None:
        self.model_size, self.device, self.compute_type = model_size, device, compute_type

    def transcribe(self, audio_path: str | Path | None, source_text: str | None = None, language: str = "hi-IN") -> ASRResult:
        if not audio_path:
            raise ValueError("whisper requires --audio-path")
        try:
            import whisper
        except ImportError as exc:
            raise RuntimeError(ASR_INSTALL_MESSAGE) from exc
        model = whisper.load_model(self.model_size, device=self.device)
        result = model.transcribe(str(audio_path), language=language.split("-")[0], fp16=self.compute_type == "float16")
        segments = [Segment(id=i, text=s["text"].strip(), start=float(s["start"]), end=float(s["end"]), confidence=None) for i, s in enumerate(result.get("segments", []))]
        return ASRResult(text=result["text"].strip(), language=result.get("language", language), confidence=None, segments=segments, backend="whisper", model_name=self.model_size)


def create_asr_adapter(backend: str, model_size: str, device: str, compute_type: str) -> BaseASRAdapter:
    if backend == "stub":
        return StubASRAdapter()
    if backend == "faster-whisper":
        return FasterWhisperASRAdapter(model_size, device, compute_type)
    if backend == "whisper":
        return WhisperASRAdapter(model_size, device, compute_type)
    raise ValueError(f"Unsupported ASR backend: {backend}")

