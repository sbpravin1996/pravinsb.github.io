#!/usr/bin/env python3
"""
AI Podcast Generation Pipeline - CLI
Generate multi-speaker podcast episodes from a topic.
"""

import argparse
from pathlib import Path

from pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI podcast episodes: script -> TTS -> audio -> MP3"
    )
    parser.add_argument(
        "topic",
        type=str,
        help="Podcast topic (e.g. 'The future of renewable energy')",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="episode",
        help="Output filename (without .mp3). Default: episode",
    )
    parser.add_argument(
        "-m", "--minutes",
        type=int,
        default=10,
        help="Target episode length in minutes. Default: 10",
    )
    parser.add_argument(
        "--music",
        type=str,
        default=None,
        help="Path to background music file (optional)",
    )
    parser.add_argument(
        "--music-volume",
        type=float,
        default=-20.0,
        help="Background music volume in dB (negative = quieter). Default: -20",
    )

    args = parser.parse_args()

    run_pipeline(
        topic=args.topic,
        output_name=args.output,
        approx_minutes=args.minutes,
        music_path=args.music,
        music_volume_db=args.music_volume,
    )


if __name__ == "__main__":
    main()
