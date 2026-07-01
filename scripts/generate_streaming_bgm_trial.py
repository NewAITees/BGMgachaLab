#!/usr/bin/env python3
"""Generate the initial streaming BGM trial set via MusicGen."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from bgm_gacha_lab.config import GenerationConfig
from bgm_gacha_lab.generator import generate_bgm, load_model


TRIAL_VARIATIONS: list[dict[str, Any]] = [
    {
        "title": "Jazz Piano Trio",
        "tag": "jazz_piano_trio",
        "temperature": 0.92,
        "prompt": (
            "streaming background music, easy-listening, modern jazz, piano trio, warm "
            "upright bass, muted brushed drums, rounded piano tone, start with a simple "
            "piano motif and light bass, gradually bring in a gentle groove, keep a stable "
            "middle section for talking-friendly background use, add a small harmonic "
            "variation in the later section without changing the core mood, finish with a "
            "soft resolved ending, tasteful harmony, gentle forward motion, lightly dusty "
            "texture, controlled room sound, soft top end, not sleepy, around four minutes"
        ),
    },
    {
        "title": "Techno Ambient DTM",
        "tag": "techno_ambient_dtm",
        "temperature": 0.98,
        "prompt": (
            "streaming background music, easy-listening, techno-leaning ambient, DTM "
            "production, soft pulse, low-mid synth bed, start with warm pads and a soft "
            "pulse, gradually layer the rhythm and harmony, keep a stable middle section "
            "with steady motion for talking-friendly background use, introduce a small "
            "texture change in the later section while keeping the same mood, finish with "
            "a smooth natural ending, warm low mids, light rhythmic motion, slightly worn "
            "texture, controlled space, dry-to-moderate ambience, focused but calm, around "
            "four minutes"
        ),
    },
    {
        "title": "Modern Classical Piano",
        "tag": "modern_classical_piano",
        "temperature": 0.88,
        "prompt": (
            "streaming background music, easy-listening, modern classical, piano-centered, "
            "grounded chamber atmosphere, start with sparse piano figures, gradually "
            "build soft repeating patterns, keep a stable middle section with restrained "
            "harmony for talking-friendly background use, add a slight melodic turn in the "
            "later section without becoming dramatic, finish with a quiet natural cadence, "
            "soft repeating figures, restrained harmony, elegant motion, controlled room "
            "sound, soft top end, refined and calm, around four minutes"
        ),
    },
]


def main() -> None:
    print("=" * 80)
    print("Streaming BGM Trial Generator")
    print("=" * 80)
    print(f"Total variations: {len(TRIAL_VARIATIONS)}")
    print("Tracks per variation: 3")
    print("Duration per track: 240 seconds")
    print("=" * 80)
    print()

    model = load_model("facebook/musicgen-stereo-medium", device="cuda")

    for idx, variation in enumerate(TRIAL_VARIATIONS, start=1):
        print()
        print("=" * 80)
        print(f"[{idx}/{len(TRIAL_VARIATIONS)}] {variation['title']}")
        print("=" * 80)

        config = GenerationConfig(
            model_name="facebook/musicgen-stereo-medium",
            duration=240.0,
            num_samples=3,
            batch_size=1,
            temperature=variation["temperature"],
            base_prompt=variation["prompt"],
            output_dir=Path("outputs/streaming_bgm_trial") / variation["tag"],
            filename_prefix=variation["tag"],
        )

        try:
            generated_files = generate_bgm(model, config)
            print(f"Successfully generated: {generated_files}")
        except Exception as exc:
            print(f"Error generating {variation['title']}: {exc}")
            print("Continuing with next variation...")

    print()
    print("=" * 80)
    print("Streaming BGM trial generation complete")
    print("Output directory: outputs/streaming_bgm_trial/")
    print("=" * 80)


if __name__ == "__main__":
    main()
