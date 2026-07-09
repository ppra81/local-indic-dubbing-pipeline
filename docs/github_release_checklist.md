# GitHub Release Checklist

Use this checklist before publishing the repository.

## Files To Include

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `requirements*.txt`
- `Dockerfile`
- `docker-compose.yml`
- `src/`
- `tests/`
- `docs/`
- `examples/`
- `scripts/`

## Files To Exclude

- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `outputs/`
- downloaded model weights
- `.env`
- local secrets

## Validation

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
pytest -q
python -m dubbing_pipeline.cli check-backends
python -m uvicorn dubbing_pipeline.api:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/live
```

## Suggested GitHub Description

Stub-first local Indic speech dubbing pipeline with CLI, FastAPI, browser demo, ASR/translation/TTS adapters, WER/CER evaluation, latency metrics, artifact persistence, tests, and Docker support.
