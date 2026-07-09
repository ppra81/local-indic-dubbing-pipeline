# Contributing

This project is a stub-first local AI dubbing prototype. Keep the default path lightweight and runnable without model downloads.

## Local Setup

```bash
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
pytest -q
```

## Development Rules

- Keep heavy model dependencies optional.
- Use clear errors when a local model, executable, or package is missing.
- Preserve the stable adapter interfaces for ASR, translation, and TTS.
- Add tests for new API, CLI, metric, or adapter behavior.
- Do not commit generated outputs, virtual environments, model weights, or local secrets.

## Adding A Backend

Add the backend behind an adapter, import optional packages lazily, expose availability through `/backends`, and document model or executable provisioning steps.
