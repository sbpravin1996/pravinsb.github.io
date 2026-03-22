"""
Audio Processor Module
Uses FFmpeg (via pydub) to:
- Stitch TTS chunks into one continuous track
- Mix with optional background music (voice over music)
- Export to MP3 at configurable bitrate
Optimized for long-form (30+ min) audio; pydub streams when possible.
"""

from pathlib import Path

from pydub import AudioSegment

from config import BITRATE, SAMPLE_RATE, TARGET_FORMAT


def stitch_audio(paths: list[Path], output_path: Path) -> Path:
    """
    Concatenate audio segments in order into a single file.
    Normalizes format (WAV 44.1kHz) for consistency before stitching.
    """
    if not paths:
        raise ValueError("No audio paths to stitch")

    combined = None
    for p in paths:
        seg = AudioSegment.from_file(str(p))
        # Resample to target if needed (reduces issues with mixed formats)
        if seg.frame_rate != SAMPLE_RATE:
            seg = seg.set_frame_rate(SAMPLE_RATE)
        combined = seg if combined is None else combined + seg

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(str(output_path), format=output_path.suffix[1:], bitrate=BITRATE)
    return output_path


def add_background_music(
    voice_path: Path,
    music_path: Path,
    output_path: Path,
    music_volume_db: float = -20.0,
) -> Path:
    """
    Mix background music under the voice track.
    music_volume_db: how much to reduce music (negative = quieter). -20 is subtle.
    """
    voice = AudioSegment.from_file(str(voice_path))
    music = AudioSegment.from_file(str(music_path))

    # Normalize
    if voice.frame_rate != SAMPLE_RATE:
        voice = voice.set_frame_rate(SAMPLE_RATE)
    if music.frame_rate != SAMPLE_RATE:
        music = music.set_frame_rate(SAMPLE_RATE)

    # Reduce music volume
    music = music + music_volume_db

    # Loop or trim music to match voice length
    if len(music) < len(voice):
        # Loop music
        n_loops = (len(voice) // len(music)) + 1
        music = music * n_loops
    music = music[:len(voice)]

    # Overlay
    mixed = voice.overlay(music)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mixed.export(str(output_path), format=output_path.suffix[1:], bitrate=BITRATE)
    return output_path


def export_mp3(
    input_path: Path,
    output_path: Path | None = None,
    bitrate: str = BITRATE,
) -> Path:
    """
    Export audio to MP3. Input can be WAV or any pydub-supported format.
    """
    seg = AudioSegment.from_file(str(input_path))
    out = output_path or input_path.with_suffix(".mp3")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    seg.export(str(out), format="mp3", bitrate=bitrate)
    return out


def build_episode(
    chunk_paths: list[Path],
    output_path: Path,
    music_path: Path | None = None,
    music_volume_db: float = -20.0,
) -> Path:
    """
    Full pipeline: stitch chunks -> optionally add music -> export MP3.
    Returns path to final MP3.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Stitch voice chunks to temp WAV
    temp_voice = output_path.parent / "_voice_stitched.wav"
    stitch_audio(chunk_paths, temp_voice)

    if music_path and Path(music_path).exists():
        temp_mixed = output_path.parent / "_mixed.wav"
        add_background_music(temp_voice, Path(music_path), temp_mixed, music_volume_db)
        result = export_mp3(temp_mixed, output_path)
        temp_mixed.unlink(missing_ok=True)
    else:
        result = export_mp3(temp_voice, output_path)

    temp_voice.unlink(missing_ok=True)
    return result
