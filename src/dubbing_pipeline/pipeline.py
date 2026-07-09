"""End-to-end dubbing orchestration."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
from uuid import uuid4

from .asr import create_asr_adapter
from .audio import get_audio_metadata
from .config import PipelineConfig
from .eval import evaluate_segments, evaluate_transcript
from .schemas import DubbingJobResult
from .storage import write_json
from .translate import create_translation_adapter
from .tts import create_tts_adapter
from .utils import ensure_directory

TTS_VOICES = {"hi-IN": "Hindi", "hi": "Hindi", "en-IN": "en", "en": "en"}


class DubbingPipeline:
    def run(
        self,
        source_text: str | None = None,
        audio_path: str | None = None,
        source_language: str = "hi-IN",
        target_language: str = "en-IN",
        reference_text: str | None = None,
        output_dir: str | Path = "outputs/demo_stub",
        asr_backend: str = "stub",
        translation_backend: str = "stub",
        tts_backend: str = "stub",
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
        glossary_path: str | Path | None = None,
    ) -> DubbingJobResult:
        if not source_text and not audio_path:
            raise ValueError("Provide source_text or audio_path")
        config = PipelineConfig(asr_backend, translation_backend, tts_backend, model_size, device, compute_type)
        output = ensure_directory(output_dir)
        started = perf_counter()
        latency: dict[str, float] = {}

        stage = perf_counter()
        audio_metadata = get_audio_metadata(audio_path) if audio_path else {"input_type": "text", "path": None}
        latency["audio_preprocessing"] = perf_counter() - stage

        stage = perf_counter()
        asr = create_asr_adapter(config.asr_backend, config.model_size, config.device, config.compute_type).transcribe(audio_path, source_text, source_language)
        latency["asr"] = perf_counter() - stage

        stage = perf_counter()
        translation = create_translation_adapter(config.translation_backend, glossary_path, config.device).translate(asr.text, asr.segments, source_language, target_language)
        latency["translation"] = perf_counter() - stage

        stage = perf_counter()
        tts_voice = TTS_VOICES.get(target_language)
        tts = create_tts_adapter(config.tts_backend).synthesize(translation.text, output, voice_id=tts_voice)
        latency["tts"] = perf_counter() - stage

        stage = perf_counter()
        evaluation = evaluate_transcript(reference_text, asr.text) if reference_text is not None else None
        if evaluation is not None:
            from .audio import create_segments_from_text
            evaluation.segment_metrics = evaluate_segments(create_segments_from_text(reference_text), asr.segments)
        latency["evaluation"] = perf_counter() - stage

        result_path = output / "result.json"
        result = DubbingJobResult(
            job_id=str(uuid4()), source_language=source_language, target_language=target_language,
            audio_metadata=audio_metadata, asr=asr, translation=translation, tts=tts,
            evaluation=evaluation, latency_seconds={key: round(value, 6) for key, value in latency.items()},
            total_latency_seconds=round(perf_counter() - started, 6), result_path=str(result_path),
        )
        write_json(result_path, result.model_dump(mode="json"))
        return result
