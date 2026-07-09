import pytest

from dubbing_pipeline.config import PipelineConfig


def test_stub_defaults_are_valid():
    assert PipelineConfig().asr_backend == "stub"


def test_identity_translation_is_supported():
    assert PipelineConfig(translation_backend="identity").translation_backend == "identity"


def test_invalid_backend_rejected():
    with pytest.raises(ValueError, match="Invalid asr_backend"):
        PipelineConfig(asr_backend="cloud")


def test_float16_cpu_rejected():
    with pytest.raises(ValueError, match="float16"):
        PipelineConfig(compute_type="float16")
