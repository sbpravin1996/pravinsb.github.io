# AI Podcast Generation Pipeline

Generate full podcast episodes from a topic using:
- **LLM** for script generation (multi-speaker dialogue)
- **Higgs 2.5** TTS (via DeepInfra) for high-quality voice
- **FFmpeg** (pydub) for stitching, background music, MP3 export

Scalable, modular design. Easy to swap LLM or TTS backends.

---

## Prerequisites

- Python 3.10+
- **FFmpeg** installed and on PATH ([ffmpeg.org](https://ffmpeg.org))
- **Ollama** (for local script generation) or OpenAI API key
- **DeepInfra API key** for Higgs 2.5 TTS ([deepinfra.com](https://deepinfra.com))

---

## Setup

```bash
cd ai_podcast
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure:

```env
# Script generation (Ollama local)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2

# TTS (Higgs 2.5 via DeepInfra)
TTS_PROVIDER=higgs
DEEPINFRA_API_KEY=your_token
```

---

## Example Run

```bash
# Basic: 10-min episode on a topic
python main.py "The future of electric vehicles"

# Custom output name and length (30 min)
python main.py "AI in healthcare" -o healthcare_ep1 -m 30

# With background music
python main.py "Space exploration" --music path/to/ambient.mp3
```

Output: `output/episode.mp3` (or your `-o` name).

---

## Module Overview

| Module | Purpose |
|--------|---------|
| `config.py` | Central config from .env |
| `script_generator.py` | LLM generates HOST/GUEST dialogue; parse to chunks |
| `tts_engine.py` | Swappable TTS (Higgs, pyttsx3, edge-tts) |
| `audio_processor.py` | Stitch chunks, mix music, export MP3 |
| `pipeline.py` | Orchestrates full flow |
| `main.py` | CLI entry point |

---

## Swapping Voice Models

Set `TTS_PROVIDER` in `.env`:

- `higgs` – Higgs 2.5 via DeepInfra (default, best quality)
- `pyttsx3` – Local, offline, no API key
- `edge` – Microsoft Edge TTS (install `edge-tts`)

Or implement a new `TTSBackend` in `tts_engine.py`.

---

## Long-Form (30+ Minutes)

The pipeline is optimized for long episodes:
- Chunks are processed sequentially to manage memory
- Stitching uses pydub (streams when possible)
- Use `-m 30` or higher for target length

---

## Optional: Background Music

Provide a WAV or MP3 file. It will be mixed under the voice at -20 dB (adjust with `--music-volume`).
