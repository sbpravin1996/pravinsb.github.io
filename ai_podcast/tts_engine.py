"""
TTS Engine Module
Swappable text-to-speech backends. Primary: Higgs 2.5 via DeepInfra.
Converts text chunks to audio files for stitching.
"""

import base64
import io
import os
from abc import ABC, abstractmethod
from pathlib import Path

from config import DEEPINFRA_API_KEY, HIGGS_API_URL, TTS_PROVIDER
from pydub import AudioSegment


class TTSBackend(ABC):
    """Abstract TTS backend. Implement for Higgs, Coqui, edge-tts, etc."""

    @abstractmethod
    def synthesize(self, text: str, output_path: Path, voice_id: str | None = None) -> Path:
        """Generate audio from text. Save to output_path. Return path."""
        pass

    def get_voice_for_speaker(self, speaker: str) -> str | None:
        """Map speaker name to voice ID. Override for multi-voice."""
        return None


class HiggsTTSBackend(TTSBackend):
    """
    Higgs 2.5 TTS via DeepInfra API.
    High-quality, natural prosody. Supports multiple languages.
    API docs: https://deepinfra.com/bosonai/HiggsAudioV2.5
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or DEEPINFRA_API_KEY or os.getenv("DEEPINFRA_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPINFRA_API_KEY required for Higgs TTS")

    def synthesize(self, text: str, output_path: Path, voice_id: str | None = None) -> Path:
        import requests

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {"input": text}
        if voice_id:
            payload["voice_id"] = voice_id

        resp = requests.post(
            HIGGS_API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # DeepInfra returns base64 audio or audio URL
        if "audio" in data and data["audio"]:
            audio_b64 = data["audio"]
            if isinstance(audio_b64, str):
                audio_bytes = base64.b64decode(audio_b64)
            else:
                audio_bytes = audio_b64
            # Assume WAV or MP3; pydub can auto-detect from bytes
            seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
        elif "results" in data and data["results"]:
            # Some APIs return results[0].audio
            r = data["results"][0]
            if "audio" in r:
                audio_bytes = base64.b64decode(r["audio"])
                seg = AudioSegment.from_file(io.BytesIO(audio_bytes))
            else:
                raise ValueError("Unexpected Higgs API response format")
        else:
            # Fallback: check for audio_url (some APIs return URL)
            if "audio_url" in data and data["audio_url"]:
                import requests
                r = requests.get(data["audio_url"], timeout=60)
                r.raise_for_status()
                seg = AudioSegment.from_file(io.BytesIO(r.content))
            else:
                raise ValueError(f"Higgs API did not return audio. Response keys: {list(data.keys())}")

        ext = output_path.suffix or ".wav"
        seg.export(str(output_path), format=ext[1:])
        return output_path


class Pyttsx3Backend(TTSBackend):
    """Fallback: pyttsx3 for local, offline TTS. Lower quality but no API key."""

    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()

    def synthesize(self, text: str, output_path: Path, voice_id: str | None = None) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine.save_to_file(text, str(output_path))
        self.engine.runAndWait()
        return output_path


class EdgeTTSBackend(TTSBackend):
    """Microsoft Edge TTS - high quality, free, requires internet."""

    def __init__(self, default_voice: str = "en-US-GuyNeural"):
        self.default_voice = default_voice

    def synthesize(self, text: str, output_path: Path, voice_id: str | None = None) -> Path:
        import edge_tts
        import asyncio

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        voice = voice_id or self.default_voice

        async def _run():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

        asyncio.run(_run())
        return output_path


def get_tts() -> TTSBackend:
    """Factory: returns configured TTS backend based on config."""
    prov = (TTS_PROVIDER or "higgs").lower()
    if prov == "higgs":
        return HiggsTTSBackend()
    if prov == "pyttsx3":
        return Pyttsx3Backend()
    if prov == "edge":
        return EdgeTTSBackend()
    raise ValueError(f"Unknown TTS_PROVIDER: {TTS_PROVIDER}")


def generate_audio_for_chunks(
    chunks: list[dict],
    output_dir: Path,
    tts: TTSBackend | None = None,
) -> list[Path]:
    """
    Convert each script chunk to audio. Each speaker can have a different voice.
    Returns list of paths to generated audio files in order.
    """
    tts = tts or get_tts()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    # Map speakers to voice IDs (optional; Higgs supports voice_id)
    voice_map = {
        "HOST": tts.get_voice_for_speaker("HOST"),
        "GUEST": tts.get_voice_for_speaker("GUEST"),
    }

    for i, chunk in enumerate(chunks):
        speaker = chunk.get("speaker", "HOST")
        text = chunk.get("text", "").strip()
        if not text:
            continue
        voice = voice_map.get(speaker.upper())
        out_path = output_dir / f"chunk_{i:04d}_{speaker}.wav"
        tts.synthesize(text, out_path, voice_id=voice)
        paths.append(out_path)

    return paths
