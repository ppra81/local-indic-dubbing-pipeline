"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys

from .api import backend_status
from .config import ASR_BACKENDS, COMPUTE_TYPES, DEVICES, MODEL_SIZES, TRANSLATION_BACKENDS, TTS_BACKENDS
from .pipeline import DubbingPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open-source Indic dubbing pipeline")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run a synchronous dubbing job")
    run.add_argument("--source-text")
    run.add_argument("--audio-path")
    run.add_argument("--source-language", default="hi-IN")
    run.add_argument("--target-language", default="en-IN")
    run.add_argument("--reference-text")
    run.add_argument("--output-dir", default="outputs/demo_stub")
    run.add_argument("--asr-backend", choices=ASR_BACKENDS, default="stub")
    run.add_argument("--translation-backend", choices=TRANSLATION_BACKENDS, default="stub")
    run.add_argument("--tts-backend", choices=TTS_BACKENDS, default="stub")
    run.add_argument("--model-size", choices=MODEL_SIZES, default="tiny")
    run.add_argument("--device", choices=DEVICES, default="cpu")
    run.add_argument("--compute-type", choices=COMPUTE_TYPES, default="int8")
    run.add_argument("--glossary-path")
    commands.add_parser("check-backends", help="Report optional local backend availability")
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    if args.command == "check-backends":
        print(json.dumps(backend_status(), indent=2))
        return
    values = vars(args)
    values.pop("command")
    result = DubbingPipeline().run(**values)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
