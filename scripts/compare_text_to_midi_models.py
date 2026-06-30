#!/usr/bin/env python3
"""Compare multiple text-to-MIDI backends with common post-processing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bgm_gacha_lab.text_to_midi import compare_text_to_midi_backends, list_text_to_midi_backends


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, help="Natural-language prompt for music generation.")
    parser.add_argument(
        "--backend",
        dest="backends",
        action="append",
        default=[],
        help="Backend key to run. Repeat to compare multiple backends.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs/text_to_midi_compare"),
        help="Directory where generated MIDI, MusicXML, and summary JSON are stored.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path("."),
        help="Workspace root used to resolve default backend script paths.",
    )
    parser.add_argument("--n-outputs", type=int, default=1, help="Number of outputs per backend.")
    parser.add_argument("--device", default="cpu", help="Execution device hint forwarded to backends.")
    parser.add_argument("--top-k", type=int, default=10, help="Number of top ranked pieces to keep.")
    parser.add_argument(
        "--with-pianoplayer",
        action="store_true",
        help="Run optional secondary evaluation with pianoplayer after MusicXML conversion.",
    )
    parser.add_argument(
        "--pianoplayer-hand-size",
        default="M",
        help="Hand size forwarded to pianoplayer when --with-pianoplayer is used.",
    )
    parser.add_argument(
        "--list-backends",
        action="store_true",
        help="Print supported backend metadata and exit.",
    )
    args = parser.parse_args()

    if args.list_backends:
        print(json.dumps(list_text_to_midi_backends(), indent=2, ensure_ascii=False))
        return

    backends = args.backends or ["midi-llm", "text2midi"]
    summary = compare_text_to_midi_backends(
        prompt=args.prompt,
        backends=backends,
        output_root=args.output_root,
        workspace=args.workspace,
        n_outputs=args.n_outputs,
        device=args.device,
        with_pianoplayer=args.with_pianoplayer,
        pianoplayer_hand_size=args.pianoplayer_hand_size,
        top_k=args.top_k,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
