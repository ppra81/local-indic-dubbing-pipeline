"""Audio metadata and explicit FFmpeg command construction.

Production preprocessing would add voice activity detection (VAD), conservative
silence removal, SNR-based quality filtering, mono conversion, sample-rate
conversion, and bounded chunking. Commands are only built here; callers decide
whether and when external tools may execute.
"""

from __future__ import annotations

import wave
from pathlib import Path

from .schemas import Segment


def get_audio_metadata(path: str | Path) -> dict[str, object]:
    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio input not found: {audio_path}")
    metadata: dict[str, object] = {"path": str(audio_path), "size_bytes": audio_path.stat().st_size}
    if audio_path.suffix.lower() == ".wav":
        try:
            with wave.open(str(audio_path), "rb") as wav:
                frames, rate = wav.getnframes(), wav.getframerate()
                metadata.update(
                    sample_rate=rate,
                    channels=wav.getnchannels(),
                    sample_width_bytes=wav.getsampwidth(),
                    duration_seconds=frames / rate if rate else 0.0,
                )
        except wave.Error:
            metadata["warning"] = "WAV header could not be parsed"
    return metadata


def estimate_duration_from_text(text: str, words_per_minute: float = 150.0) -> float:
    words = len(text.split())
    return round((words / words_per_minute) * 60.0, 3) if words else 0.0


def create_segments_from_text(text: str) -> list[Segment]:
    chunks = [part.strip() for part in text.replace("!", ".").replace("?", ".").split(".") if part.strip()]
    if not chunks and text.strip():
        chunks = [text.strip()]
    segments: list[Segment] = []
    cursor = 0.0
    for index, chunk in enumerate(chunks):
        duration = estimate_duration_from_text(chunk)
        segments.append(Segment(id=index, text=chunk, start=cursor, end=round(cursor + duration, 3)))
        cursor += duration
    return segments


def build_ffmpeg_extract_audio_command(video_path: str | Path, output_wav_path: str | Path, sample_rate: int = 16000) -> list[str]:
    return ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-ac", "1", "-ar", str(sample_rate), str(output_wav_path)]


def build_ffmpeg_resample_command(input_path: str | Path, output_path: str | Path, sample_rate: int = 16000) -> list[str]:
    return ["ffmpeg", "-y", "-i", str(input_path), "-ac", "1", "-ar", str(sample_rate), str(output_path)]

