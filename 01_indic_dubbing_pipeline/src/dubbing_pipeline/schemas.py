"""Typed data contracts shared by the CLI, API, and adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Segment(BaseModel):
    id: int
    text: str
    start: float = 0.0
    end: float = 0.0
    confidence: float | None = None


class ASRResult(BaseModel):
    text: str
    language: str
    confidence: float | None = None
    segments: list[Segment] = Field(default_factory=list)
    backend: str
    model_name: str


class TranslationResult(BaseModel):
    text: str
    source_language: str
    target_language: str
    segments: list[Segment] = Field(default_factory=list)
    backend: str
    model_name: str


class TTSResult(BaseModel):
    generated_audio_path: str
    duration_seconds: float
    voice_id: str
    sample_rate: int
    backend: str


class EvaluationResult(BaseModel):
    reference: str
    hypothesis: str
    wer: float
    cer: float
    segment_metrics: list[dict[str, Any]] = Field(default_factory=list)


class DubbingJobResult(BaseModel):
    job_id: str
    status: str = "completed"
    source_language: str
    target_language: str
    audio_metadata: dict[str, Any] = Field(default_factory=dict)
    asr: ASRResult
    translation: TranslationResult
    tts: TTSResult
    evaluation: EvaluationResult | None = None
    latency_seconds: dict[str, float] = Field(default_factory=dict)
    total_latency_seconds: float
    result_path: str


class DubbingRunRequest(BaseModel):
    source_text: str | None = None
    audio_path: str | None = None
    source_language: str = "hi-IN"
    target_language: str = "en-IN"
    reference_text: str | None = None
    output_dir: str = "outputs/api_job"
    asr_backend: str = "stub"
    translation_backend: str = "stub"
    tts_backend: str = "stub"
    model_size: str = "tiny"
    device: str = "cpu"
    compute_type: str = "int8"
    glossary_path: str | None = None


class TranscriptEvaluationRequest(BaseModel):
    reference: str
    hypothesis: str

