"""Dependency-free ASR error metrics."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence

from .schemas import EvaluationResult, Segment


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(char if char.isalnum() or char.isspace() else " " for char in text)
    return re.sub(r"\s+", " ", text).strip()


def levenshtein_distance(reference: Sequence[object], hypothesis: Sequence[object]) -> int:
    if len(reference) < len(hypothesis):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for row, ref_item in enumerate(reference, start=1):
        current = [row]
        for col, hyp_item in enumerate(hypothesis, start=1):
            current.append(min(current[-1] + 1, previous[col] + 1, previous[col - 1] + (ref_item != hyp_item)))
        previous = current
    return previous[-1]


def _safe_rate(reference: Sequence[object], hypothesis: Sequence[object]) -> float:
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein_distance(reference, hypothesis) / len(reference)


def word_error_rate(reference: str, hypothesis: str) -> float:
    return _safe_rate(normalize_text(reference).split(), normalize_text(hypothesis).split())


def character_error_rate(reference: str, hypothesis: str) -> float:
    return _safe_rate(list(normalize_text(reference)), list(normalize_text(hypothesis)))


def evaluate_transcript(reference: str, hypothesis: str) -> EvaluationResult:
    return EvaluationResult(reference=reference, hypothesis=hypothesis, wer=word_error_rate(reference, hypothesis), cer=character_error_rate(reference, hypothesis))


def evaluate_segments(reference_segments: list[Segment], hypothesis_segments: list[Segment]) -> list[dict[str, object]]:
    hypotheses = {segment.id: segment for segment in hypothesis_segments}
    return [
        {
            "segment_id": reference.id,
            "reference": reference.text,
            "hypothesis": hypotheses.get(reference.id).text if reference.id in hypotheses else "",
            "wer": word_error_rate(reference.text, hypotheses.get(reference.id).text if reference.id in hypotheses else ""),
            "cer": character_error_rate(reference.text, hypotheses.get(reference.id).text if reference.id in hypotheses else ""),
        }
        for reference in reference_segments
    ]

