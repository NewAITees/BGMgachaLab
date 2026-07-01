#!/usr/bin/env python3
"""Generate the full streaming BGM variation matrix via MusicGen."""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bgm_gacha_lab.config import GenerationConfig
from bgm_gacha_lab.generator import generate_bgm, load_model


COMMON_CONSTRAINTS = (
    "streaming background music, easy-listening, not sleepy, controlled reverb, soft top "
    "end, streamer voice friendly, start with a clear gentle intro, gradually develop the "
    "arrangement, keep a stable middle section for talking-friendly background use, add a "
    "small late variation without changing the core mood, finish with a natural resolved "
    "ending, around four minutes"
)

AXES = [
    {
        "key": "jazz",
        "prompt": (
            "modern jazz, tasteful harmony, light swing influence, begin with a simple chord "
            "motif, let the groove enter gradually, lightly dusty texture"
        ),
        "temperature": 0.92,
    },
    {
        "key": "techno",
        "prompt": (
            "techno, soft pulse, restrained kick pattern, begin with a simple rhythmic bed, "
            "slowly let the groove settle in, controlled low-mid energy"
        ),
        "temperature": 0.98,
    },
    {
        "key": "ambient",
        "prompt": (
            "ambient, soft atmospheric drift, begin with warm pads, slowly widen the "
            "texture, dry-to-moderate ambience"
        ),
        "temperature": 0.94,
    },
    {
        "key": "dtm",
        "prompt": (
            "soft electronic arrangement, low-mid synth bed, soft transients, let the "
            "texture build in small steps, slightly worn texture"
        ),
        "temperature": 1.0,
    },
    {
        "key": "piano_centered",
        "prompt": (
            "piano-centered, rounded tone, grounded melodic focus, open with sparse piano, "
            "controlled room sound"
        ),
        "temperature": 0.9,
    },
    {
        "key": "piano_trio",
        "prompt": (
            "piano trio, warm upright bass, muted brushed drums, let bass and brushes join "
            "after the opening piano phrase, restrained drum texture"
        ),
        "temperature": 0.91,
    },
    {
        "key": "modern_classical",
        "prompt": (
            "modern classical, restrained repetition, elegant chamber motion, gradually "
            "expand repeating figures, controlled room sound"
        ),
        "temperature": 0.88,
    },
]


def build_variations() -> list[dict[str, object]]:
    variations: list[dict[str, object]] = []
    for size in (1, 2):
        for combo in itertools.combinations(AXES, size):
            keys = [axis["key"] for axis in combo]
            prompt_parts = [COMMON_CONSTRAINTS] + [str(axis["prompt"]) for axis in combo]
            temperature = round(sum(float(axis["temperature"]) for axis in combo) / len(combo), 2)
            variations.append(
                {
                    "tag": "__".join(keys),
                    "title": " + ".join(keys),
                    "prompt": ", ".join(prompt_parts),
                    "temperature": temperature,
                }
            )
    return variations


def main() -> None:
    variations = build_variations()

    print("=" * 80)
    print("Streaming BGM Full Matrix Generator")
    print("=" * 80)
    print(f"Total variations: {len(variations)}")
    print("Tracks per variation: 3")
    print("Duration per track: 240 seconds")
    print("=" * 80)
    print()

    model = load_model("facebook/musicgen-stereo-medium", device="cuda")

    for idx, variation in enumerate(variations, start=1):
        print()
        print("=" * 80)
        print(f"[{idx}/{len(variations)}] {variation['title']}")
        print("=" * 80)

        config = GenerationConfig(
            model_name="facebook/musicgen-stereo-medium",
            duration=240.0,
            num_samples=3,
            batch_size=1,
            temperature=float(variation["temperature"]),
            base_prompt=str(variation["prompt"]),
            output_dir=Path("outputs/streaming_bgm_full_matrix") / str(variation["tag"]),
            filename_prefix=str(variation["tag"]),
        )

        try:
            generated_files = generate_bgm(model, config)
            print(f"Successfully generated: {generated_files}")
        except Exception as exc:
            print(f"Error generating {variation['title']}: {exc}")
            print("Continuing with next variation...")

    print()
    print("=" * 80)
    print("Streaming BGM full matrix generation complete")
    print("Output directory: outputs/streaming_bgm_full_matrix/")
    print("=" * 80)


if __name__ == "__main__":
    main()
