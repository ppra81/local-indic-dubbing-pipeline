"""Translation adapters, including a deterministic offline fallback."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path

from .schemas import Segment, TranslationResult

TRANSLATION_INSTALL_MESSAGE = "Install optional translation dependencies with pip install -r requirements-translation.txt"
INDICTRANS_LANGUAGE_CODES = {"hi-IN": "hin_Deva", "en-IN": "eng_Latn", "hi": "hin_Deva", "en": "eng_Latn"}


def load_glossary(path: str | Path | None) -> dict[str, str]:
    if not path:
        return {}
    with Path(path).open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        raise ValueError("Glossary must be a JSON object containing string-to-string mappings")
    return data


def apply_glossary(text: str, glossary: dict[str, str]) -> str:
    result = text
    for source in sorted(glossary, key=len, reverse=True):
        result = result.replace(source, glossary[source])
    return result


class BaseTranslationAdapter(ABC):
    @abstractmethod
    def translate(self, text: str, segments: list[Segment], source_language: str, target_language: str) -> TranslationResult:
        raise NotImplementedError


class IdentityTranslationAdapter(BaseTranslationAdapter):
    """Preserve text and timings for same-language TTS."""

    def translate(self, text: str, segments: list[Segment], source_language: str, target_language: str) -> TranslationResult:
        if source_language != target_language:
            raise ValueError("Identity translation requires source_language and target_language to match")
        return TranslationResult(
            text=text, source_language=source_language, target_language=target_language,
            segments=[segment.model_copy() for segment in segments], backend="identity", model_name="identity-pass-through",
        )


class StubTranslationAdapter(BaseTranslationAdapter):
    def __init__(self, glossary: dict[str, str] | None = None) -> None:
        self.glossary = glossary or {}

    def _translate(self, text: str, source_language: str, target_language: str) -> str:
        translated = apply_glossary(text, self.glossary)
        return f"[{target_language} translation of {source_language}]: {translated}"

    def translate(self, text: str, segments: list[Segment], source_language: str, target_language: str) -> TranslationResult:
        translated_segments = [segment.model_copy(update={"text": self._translate(segment.text, source_language, target_language)}) for segment in segments]
        return TranslationResult(text=self._translate(text, source_language, target_language), source_language=source_language, target_language=target_language, segments=translated_segments, backend="stub", model_name="deterministic-glossary-stub")


class IndicTrans2TranslationAdapter(BaseTranslationAdapter):
    """Optional Hugging Face IndicTrans2 adapter.

    A local model directory or Hugging Face model ID must be supplied. The latter
    may download weights, so production callers should pre-provision/cache models.
    """

    def __init__(self, model_name: str = "ai4bharat/indictrans2-indic-en-dist-200M", device: str = "cpu", glossary: dict[str, str] | None = None) -> None:
        self.model_name, self.device, self.glossary = model_name, device, glossary or {}
        self._tokenizer = None
        self._model = None
        self._processor = None

    def _load(self) -> None:
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(TRANSLATION_INSTALL_MESSAGE) from exc
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, trust_remote_code=True).to(self.device)
        except (OSError, PermissionError, ModuleNotFoundError) as exc:
            message = str(exc).lower()
            if "gated repo" in message or "401" in message or "unauthorized" in message or "restricted" in message:
                raise RuntimeError(
                    "IndicTrans2 model access was denied. Accept the model terms at "
                    "https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M, then run "
                    "'.\\.venv\\Scripts\\hf.exe auth login' with a read token and restart the API."
                ) from exc
            if "transformers.onnx" in message:
                raise RuntimeError(
                    "IndicTrans2 requires transformers==4.32.1; reinstall with "
                    "'.\\.venv\\Scripts\\python.exe -m pip install -r requirements-translation.txt'."
                ) from exc
            raise RuntimeError(f"IndicTrans2 model could not be loaded: {exc}") from exc

        try:
            from IndicTransToolkit.processor import IndicProcessor
            self._processor = IndicProcessor(inference=True)
        except ImportError:
            self._processor = None

    def _language_code(self, language: str) -> str:
        try:
            return INDICTRANS_LANGUAGE_CODES[language]
        except KeyError as exc:
            raise ValueError(f"IndicTrans2 language is not configured: {language}") from exc

    def _preprocess(self, text: str, source_language: str, target_language: str) -> str:
        source_code, target_code = self._language_code(source_language), self._language_code(target_language)
        text = apply_glossary(text, self.glossary)
        if source_code == "hin_Deva" and not re.search(r"[\u0900-\u097F]", text):
            raise ValueError(
                "Hindi IndicTrans2 input must use Devanagari script. Enter Hindi such as "
                "'नमस्ते, आज हम डबिंग का परीक्षण कर रहे हैं।' Romanized or English text is not Hindi input."
            )
        if self._processor is not None:
            return self._processor.preprocess_batch([text], src_lang=source_code, tgt_lang=target_code)[0]
        if source_code == "hin_Deva":
            from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
            from indicnlp.tokenize import indic_tokenize
            text = IndicNormalizerFactory().get_normalizer("hi").normalize(text)
            text = " ".join(indic_tokenize.trivial_tokenize(text, "hi"))
        else:
            from sacremoses import MosesPunctNormalizer, MosesTokenizer
            text = " ".join(MosesTokenizer(lang="en").tokenize(MosesPunctNormalizer(lang="en").normalize(text), escape=False))
        return f"{source_code} {target_code} {text.strip()}"

    def _postprocess(self, text: str, target_language: str) -> str:
        target_code = self._language_code(target_language)
        if self._processor is not None:
            return self._processor.postprocess_batch([text], lang=target_code)[0]
        if target_code == "eng_Latn":
            from sacremoses import MosesDetokenizer
            return MosesDetokenizer(lang="en").detokenize(text.split())
        return text

    def _translate_one(self, text: str, source_language: str, target_language: str) -> str:
        if self._model is None:
            self._load()
        prepared = self._preprocess(text, source_language, target_language)
        inputs = self._tokenizer(prepared, return_tensors="pt").to(self.device)
        output = self._model.generate(**inputs, use_cache=True, min_length=0, max_length=256, num_beams=5, num_return_sequences=1)
        decoded = self._tokenizer.batch_decode(output, skip_special_tokens=True, clean_up_tokenization_spaces=True)[0]
        return self._postprocess(decoded, target_language)

    def translate(self, text: str, segments: list[Segment], source_language: str, target_language: str) -> TranslationResult:
        if target_language not in ("en-IN", "en"):
            raise ValueError("The configured IndicTrans2 checkpoint supports Indic-to-English only; choose target en-IN")
        translated_segments = [segment.model_copy(update={"text": self._translate_one(segment.text, source_language, target_language)}) for segment in segments]
        translated_text = " ".join(segment.text for segment in translated_segments) if translated_segments else self._translate_one(text, source_language, target_language)
        return TranslationResult(text=translated_text, source_language=source_language, target_language=target_language, segments=translated_segments, backend="indictrans2", model_name=self.model_name)


def create_translation_adapter(backend: str, glossary_path: str | Path | None = None, device: str = "cpu") -> BaseTranslationAdapter:
    glossary = load_glossary(glossary_path)
    if backend == "identity":
        return IdentityTranslationAdapter()
    if backend == "stub":
        return StubTranslationAdapter(glossary)
    if backend == "indictrans2":
        return IndicTrans2TranslationAdapter(device=device, glossary=glossary)
    raise ValueError(f"Unsupported translation backend: {backend}")
