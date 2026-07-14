from fastapi.testclient import TestClient
import os
import pytest

from dubbing_pipeline.api import app

client = TestClient(app)


def test_health_and_backends():
    assert client.get("/health").json() == {"status": "ok", "offline": "true"}
    response = client.get("/backends")
    assert response.status_code == 200
    assert response.json()["asr"][0] == {"name": "stub", "available": True}


def test_evaluate_endpoint():
    response = client.post("/evaluate/transcript", json={"reference": "Hello!", "hypothesis": "hello"})
    assert response.status_code == 200
    assert response.json()["wer"] == 0


def test_run_stub_job(tmp_path):
    response = client.post("/dubbing/jobs/run", json={"source_text": "namaste", "output_dir": str(tmp_path)})
    assert response.status_code == 200
    assert response.json()["asr"]["backend"] == "stub"


def test_live_page_is_available():
    response = client.get("/live")
    assert response.status_code == 200
    assert "Start recording" in response.text
    assert "f.append('asr_backend','stub')" in response.text
    assert 'value="indictrans2" selected' in response.text
    assert 'value="espeak" selected' in response.text


def test_upload_rejects_unsupported_file():
    response = client.post("/dubbing/jobs/upload", files={"audio": ("unsafe.exe", b"data")})
    assert response.status_code == 415


def test_text_dubbing_endpoint_with_stub(tmp_path, monkeypatch):
    from dubbing_pipeline import api
    monkeypatch.setattr(api, "LIVE_OUTPUT_ROOT", tmp_path.resolve())
    response = client.post("/dubbing/jobs/text", data={"text": "hello", "translation_backend": "stub", "tts_backend": "stub"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["asr"]["text"] == "hello"
    assert payload["audio_url"].endswith("/audio")


def test_text_dubbing_reports_model_access_error(tmp_path, monkeypatch):
    from dubbing_pipeline import api
    from dubbing_pipeline.translate import IndicTrans2TranslationAdapter

    monkeypatch.setattr(api, "LIVE_OUTPUT_ROOT", tmp_path.resolve())
    monkeypatch.setattr(
        IndicTrans2TranslationAdapter,
        "_load",
        lambda self: (_ for _ in ()).throw(RuntimeError("IndicTrans2 model access was denied")),
    )
    response = client.post(
        "/dubbing/jobs/text",
        data={"text": "namaste", "translation_backend": "indictrans2", "tts_backend": "stub"},
    )
    assert response.status_code == 400
    assert "access was denied" in response.json()["detail"]


def test_indictrans_rejects_non_devanagari_hindi_before_inference():
    from dubbing_pipeline.translate import IndicTrans2TranslationAdapter

    adapter = IndicTrans2TranslationAdapter()
    with pytest.raises(ValueError, match="Devanagari"):
        adapter._preprocess("Hello, this is already English", "hi-IN", "en-IN")


@pytest.mark.skipif(os.environ.get("RUN_LOCAL_MODEL_TESTS") != "1", reason="requires cached IndicTrans2 model")
def test_indictrans_translates_user_sports_sentence():
    from dubbing_pipeline.audio import create_segments_from_text
    from dubbing_pipeline.translate import IndicTrans2TranslationAdapter

    text = "हेलो, यह हमारी वार्षिक खेल प्रतियोगिता का पहला आधिकारिक अभ्यास है।"
    adapter = IndicTrans2TranslationAdapter()
    result = adapter.translate(text, create_segments_from_text(text), "hi-IN", "en-IN")
    assert "annual sports competition" in result.text.lower()
    assert "translation of" not in result.text
