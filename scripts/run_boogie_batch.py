#!/usr/bin/env python3
"""Run the standard boogie batch with no arguments required."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from bgm_gacha_lab.pianoplayer_eval import evaluate_with_pianoplayer
from bgm_gacha_lab.playability import evaluate_piano_midi_playability
from bgm_gacha_lab.score import midi_to_musicxml
from bgm_gacha_lab.text_to_midi import _rank_artifacts


def run_generation(
    prompts_file: Path,
    n_outputs: int,
    max_tokens: int,
    output_root: Path,
) -> Path:
    command = [
        "python",
        "third_party/MIDI-LLM/generate_transformers.py",
        "--prompts_file",
        str(prompts_file),
        "--n_outputs",
        str(n_outputs),
        "--max_tokens",
        str(max_tokens),
        "--no-synthesize",
        "--output_root",
        str(output_root),
    ]
    subprocess.run(command, check=True)
    sessions = [path for path in output_root.iterdir() if path.is_dir()]
    if not sessions:
        raise RuntimeError(f"No generation session was created under {output_root}")
    return max(sessions, key=lambda path: path.stat().st_mtime)


def post_process(session_dir: Path, hand_size: str, top_k: int) -> tuple[Path, Path]:
    exe = str(Path(".venv/bin/pianoplayer").resolve())
    summary = {
        "session_dir": str(session_dir),
        "backends": {
            "midi-llm": {
                "status": "ok",
                "artifacts": [],
            }
        },
    }

    for midi_path in sorted(session_dir.rglob("*.mid")):
        artifact = {"midi_path": str(midi_path)}
        musicxml_path = midi_to_musicxml(midi_path)
        artifact["musicxml_path"] = str(musicxml_path)
        artifact["playability"] = evaluate_piano_midi_playability(midi_path).to_dict()
        artifact["pianoplayer_evaluation"] = evaluate_with_pianoplayer(
            musicxml_path,
            hand_size=hand_size,
            executable=exe,
        ).to_dict()
        summary["backends"]["midi-llm"]["artifacts"].append(artifact)

    summary["top_candidates"] = _rank_artifacts(summary, top_k=top_k)
    summary_path = session_dir.parent / "comparison_summary.json"
    top_path = session_dir.parent / "top_candidates.json"
    summary["summary_path"] = str(summary_path)
    summary["top_candidates_path"] = str(top_path)

    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    top_path.write_text(
        json.dumps(summary["top_candidates"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary_path, top_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompts-file",
        type=Path,
        default=Path("outputs/boogie_jazzy_rock_prompt_variants.txt"),
        help="Prompt list file. Default is the prepared boogie/jazzy rock variant set.",
    )
    parser.add_argument(
        "--n-outputs",
        type=int,
        default=10,
        help="Number of outputs to generate per prompt. Default: 10.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2046,
        help="Maximum tokens to generate per output. Default: 2046.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("outputs/boogie_jazzy_rock_variants_120"),
        help="Root directory for generation and evaluation outputs. Default: outputs/boogie_jazzy_rock_variants_120.",
    )
    parser.add_argument(
        "--hand-size",
        default="M",
        choices=["XXS", "XS", "S", "M", "L", "XL", "XXL"],
        help="Hand size forwarded to pianoplayer. Default: M.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="How many top candidates to keep in top_candidates.json. Default: 10.",
    )
    args = parser.parse_args()

    session_dir = run_generation(
        args.prompts_file,
        args.n_outputs,
        args.max_tokens,
        args.output_root,
    )
    summary_path, top_path = post_process(session_dir, args.hand_size, args.top_k)

    print(f"Generation session: {session_dir}")
    print(f"Summary JSON: {summary_path}")
    print(f"Top candidates JSON: {top_path}")


if __name__ == "__main__":
    main()
