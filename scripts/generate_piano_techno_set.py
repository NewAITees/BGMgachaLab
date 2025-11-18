#!/usr/bin/env python3
"""Generate the Piano Techno Chill Work BGM Set (10 patterns, 10 minutes each)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import bgm_gacha_lab
sys.path.insert(0, str(Path(__file__).parent.parent))

from bgm_gacha_lab.config import GenerationConfig
from bgm_gacha_lab.generator import load_model, generate_bgm


# 10パターンの設定定義（README.mdの表に基づく）
PIANO_TECHNO_PATTERNS: List[Dict[str, Any]] = [
    {
        "title": "Midnight Keys Drive",
        "bpm": 122,
        "preset": "night",
        "temperature": 1.0,
        "prompt": "piano led techno groove, glossy synth pads, midnight city",
        "tag": "midnight_keys_drive",
    },
    {
        "title": "Neon Raindrops",
        "bpm": 118,
        "preset": "cafe",
        "temperature": 0.9,
        "prompt": "soft piano arpeggio techno, gentle rain foley, chill focus",
        "tag": "neon_raindrops",
    },
    {
        "title": "Circuit Garden",
        "bpm": 126,
        "preset": "night",
        "temperature": 1.1,
        "prompt": "percussive piano stabs with modular techno pulses, blooming pads",
        "tag": "circuit_garden",
    },
    {
        "title": "Moonlit Assembly",
        "bpm": 112,
        "preset": "cafe",
        "temperature": 0.85,
        "prompt": "minimal piano ostinato, subtle 4-on-the-floor kick, airy ambience",
        "tag": "moonlit_assembly",
    },
    {
        "title": "Vapor Keys Relay",
        "bpm": 128,
        "preset": "night",
        "temperature": 1.2,
        "prompt": "bright piano chords, retro techno bassline, hazy shimmer",
        "tag": "vapor_keys_relay",
    },
    {
        "title": "Aurora Loop",
        "bpm": 116,
        "preset": "cafe",
        "temperature": 0.95,
        "prompt": "glacial piano motif, downtempo techno beat, long tails",
        "tag": "aurora_loop",
    },
    {
        "title": "Copper Wire Waltz",
        "bpm": 120,
        "preset": "night",
        "temperature": 1.05,
        "prompt": "piano triplet arpeggios, swung techno percussion, analog hiss",
        "tag": "copper_wire_waltz",
    },
    {
        "title": "Gravity Sketch",
        "bpm": 124,
        "preset": "night",
        "temperature": 1.0,
        "prompt": "tight piano plucks, rolling bass, focus friendly techno",
        "tag": "gravity_sketch",
    },
    {
        "title": "Driftwood Metro",
        "bpm": 114,
        "preset": "cafe",
        "temperature": 0.9,
        "prompt": "loose piano chords, dub techno delay, cozy workspace vibe",
        "tag": "driftwood_metro",
    },
    {
        "title": "Prism Bloom",
        "bpm": 130,
        "preset": "night",
        "temperature": 1.15,
        "prompt": "energetic piano riffs, sidechained pads, uplifting techno",
        "tag": "prism_bloom",
    },
]


def main() -> None:
    """Generate all 10 piano techno patterns."""
    print("=" * 80)
    print("Piano Techno Chill Work BGM Set Generator")
    print("=" * 80)
    print(f"Total patterns: {len(PIANO_TECHNO_PATTERNS)}")
    print("Duration per pattern: 600 seconds (10 minutes)")
    print("=" * 80)
    print()

    # モデルを一度だけロード（全パターンで共有）
    model = load_model("facebook/musicgen-stereo-medium", device="cuda")

    # 各パターンを順次生成
    for idx, pattern in enumerate(PIANO_TECHNO_PATTERNS, start=1):
        print()
        print("=" * 80)
        print(f"[{idx}/{len(PIANO_TECHNO_PATTERNS)}] {pattern['title']} ({pattern['bpm']} BPM)")
        print("=" * 80)

        # GenerationConfig を作成
        config = GenerationConfig(
            model_name="facebook/musicgen-stereo-medium",
            duration=600.0,  # 10分
            num_samples=1,  # 1曲のみ生成
            batch_size=1,  # batch_size=1 (32ビット制限対策)
            temperature=pattern["temperature"],
            base_prompt=pattern["prompt"],
            output_dir=Path("outputs/piano_techno_set"),
            filename_prefix=pattern["tag"],
        )

        try:
            # BGM生成
            generated_files = generate_bgm(model, config)
            print(f"✓ Successfully generated: {generated_files}")
        except Exception as e:
            print(f"✗ Error generating {pattern['title']}: {e}")
            print("Continuing with next pattern...")
            continue

    print()
    print("=" * 80)
    print("All patterns generation complete!")
    print(f"Output directory: outputs/piano_techno_set/")
    print("=" * 80)


if __name__ == "__main__":
    main()
