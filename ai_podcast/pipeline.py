"""
AI Podcast Generation Pipeline
Orchestrates the full flow:
1. Script generation (LLM) -> structured HOST/GUEST chunks
2. TTS per chunk (Higgs or fallback) -> WAV files
3. Stitch chunks -> single voice track
4. Optionally mix with background music
5. Export final MP3
"""

from pathlib import Path

from config import OUTPUT_DIR, TEMP_DIR
from script_generator import generate_script
from tts_engine import generate_audio_for_chunks, get_tts
from audio_processor import build_episode


def run_pipeline(
    topic: str,
    output_name: str = "episode",
    approx_minutes: int = 10,
    music_path: Path | str | None = None,
    music_volume_db: float = -20.0,
) -> Path:
    """
    Full pipeline:
    1. Generate multi-speaker script via LLM
    2. Convert each chunk to audio via TTS
    3. Stitch audio, add optional music, export MP3
    Returns path to final MP3.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    run_dir = TEMP_DIR / output_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Generate script
    print("[1/4] Generating podcast script...")
    chunks = generate_script(topic, approx_minutes=approx_minutes)
    script_path = run_dir / "script.json"
    import json
    with open(script_path, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"      Generated {len(chunks)} chunks.")

    # Step 2: TTS per chunk
    print("[2/4] Converting script to audio (TTS)...")
    chunk_dir = run_dir / "chunks"
    audio_paths = generate_audio_for_chunks(chunks, chunk_dir)
    print(f"      Generated {len(audio_paths)} audio segments.")

    # Step 3 & 4: Stitch, add music, export
    print("[3/4] Stitching audio...")
    mp3_path = OUTPUT_DIR / f"{output_name}.mp3"
    music = Path(music_path) if music_path else None
    final = build_episode(
        audio_paths,
        mp3_path,
        music_path=music,
        music_volume_db=music_volume_db,
    )
    print("[4/4] Export complete.")
    print(f"      Output: {final}")
    return final
