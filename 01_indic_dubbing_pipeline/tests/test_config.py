import pytest

from dubbing_pipeline.config import OFFLINE_ENV_VAR, PipelineConfig, offline_mode_enabled


def test_stub_defaults_are_valid():
    assert PipelineConfig().asr_backend == "stub"


def test_offline_mode_is_default(monkeypatch):
    monkeypatch.delenv(OFFLINE_ENV_VAR, raising=False)
    assert offline_mode_enabled() is True


def test_offline_mode_can_be_disabled(monkeypatch):
    monkeypatch.setenv(OFFLINE_ENV_VAR, "0")
    assert offline_mode_enabled() is False


def test_identity_translation_is_supported():
    assert PipelineConfig(translation_backend="identity").translation_backend == "identity"


def test_invalid_backend_rejected():
    with pytest.raises(ValueError, match="Invalid asr_backend"):
        PipelineConfig(asr_backend="cloud")


def test_float16_cpu_rejected():
    with pytest.raises(ValueError, match="float16"):
        PipelineConfig(compute_type="float16")
