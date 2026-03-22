"""
Configuration for the AI Podcast Pipeline.
Loads from .env; provides centralized settings for LLM, TTS, and paths.
Edit .env to swap providers (e.g. LLM_PROVIDER=openai, TTS_PROVIDER=pyttsx3).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# === Paths ===
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
TEMP_DIR = PROJECT_ROOT / os.getenv("TEMP_DIR", "temp")

# === LLM (Script Generation) ===
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# === TTS ===
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "higgs")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY", "")
HIGGS_API_URL = "https://api.deepinfra.com/v1/inference/bosonai/HiggsAudioV2.5"

# === Audio ===
SAMPLE_RATE = 44100
TARGET_FORMAT = "mp3"
BITRATE = "192k"
