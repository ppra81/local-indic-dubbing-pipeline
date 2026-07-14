import json
from pathlib import Path

from dubbing_pipeline.pipeline import DubbingPipeline


def test_stub_pipeline_writes_artifacts(tmp_path: Path):
    result = DubbingPipeline().run(source_text="Namaste world", reference_text="namaste world", output_dir=tmp_path)
    assert result.evaluation is not None and result.evaluation.wer == 0
    assert Path(result.result_path).exists()
    assert Path(result.tts.generated_audio_path).exists()
    saved = json.loads(Path(result.result_path).read_text(encoding="utf-8"))
    assert saved["status"] == "completed"
    assert set(saved["latency_seconds"]) == {"audio_preprocessing", "asr", "translation", "tts", "evaluation"}


def test_stub_translation_does_not_speak_metadata_label(tmp_path: Path):
    result = DubbingPipeline().run(
        source_text="नमस्ते, आज हम स्थानीय भाषण डबिंग प्रणाली का परीक्षण कर रहे हैं।",
        source_language="hi-IN",
        target_language="en-IN",
        tts_backend="stub",
        output_dir=tmp_path,
    )
    assert "translation of" not in result.translation.text
    assert result.translation.text == "hello, today we are testing the local speech dubbing system."


def test_pipeline_requires_input(tmp_path: Path):
    import pytest
    with pytest.raises(ValueError, match="source_text or audio_path"):
        DubbingPipeline().run(output_dir=tmp_path)


def test_hindi_identity_pipeline_selects_hindi_voice(tmp_path: Path):
    result = DubbingPipeline().run(
        source_text="नमस्ते", source_language="hi-IN", target_language="hi-IN",
        translation_backend="identity", tts_backend="stub", output_dir=tmp_path,
    )
    assert result.translation.text == "नमस्ते"
    assert result.translation.backend == "identity"
    assert result.tts.voice_id == "Hindi"
