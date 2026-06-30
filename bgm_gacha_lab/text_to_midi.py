"""Adapters for comparing multiple text-to-MIDI backends."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .playability import evaluate_piano_midi_playability
from .pianoplayer_eval import evaluate_with_pianoplayer
from .score import midi_to_musicxml


@dataclass(slots=True)
class TextToMidiRequest:
    """Normalized request shared by text-to-MIDI backends."""

    prompt: str
    output_dir: Path
    n_outputs: int = 1
    device: str = "cpu"


@dataclass(slots=True)
class BackendSpec:
    """Description of an external backend entrypoint."""

    key: str
    env_var: str
    default_relpath: str
    command_builder: Any
    notes: str

    def resolve_entrypoint(self, workspace: str | Path | None = None) -> Path:
        import os

        env_override = os.environ.get(self.env_var)
        if env_override:
            return Path(env_override).expanduser()
        if workspace is None:
            return Path(self.default_relpath)
        return Path(workspace) / self.default_relpath


def _build_midi_llm_command(entrypoint: Path, request: TextToMidiRequest) -> list[str]:
    return [
        "python",
        str(entrypoint),
        "--prompt",
        request.prompt,
        "--output_root",
        str(request.output_dir),
        "--n_outputs",
        str(request.n_outputs),
        "--no-synthesize",
    ]


def _build_text2midi_command(entrypoint: Path, request: TextToMidiRequest) -> list[str]:
    return [
        "python",
        str(entrypoint),
        "--prompt",
        request.prompt,
        "--output-dir",
        str(request.output_dir),
        "--n-outputs",
        str(request.n_outputs),
        "--device",
        request.device,
    ]


BACKENDS: dict[str, BackendSpec] = {
    "midi-llm": BackendSpec(
        key="midi-llm",
        env_var="MIDI_LLM_ENTRYPOINT",
        default_relpath="third_party/MIDI-LLM/generate_transformers.py",
        command_builder=_build_midi_llm_command,
        notes="Official Transformers inference script for MIDI-LLM.",
    ),
    "text2midi": BackendSpec(
        key="text2midi",
        env_var="TEXT2MIDI_ENTRYPOINT",
        default_relpath="third_party/Text2midi/infer.py",
        command_builder=_build_text2midi_command,
        notes="Expected to point at a local Text2midi inference script.",
    ),
}


def list_text_to_midi_backends() -> dict[str, dict[str, str]]:
    """Return the known backends and how they are resolved."""

    return {
        key: {
            "env_var": spec.env_var,
            "default_relpath": spec.default_relpath,
            "notes": spec.notes,
        }
        for key, spec in BACKENDS.items()
    }


def _collect_generated_midis(output_dir: Path) -> list[Path]:
    return sorted(
        [
            path
            for pattern in ("*.mid", "*.midi")
            for path in output_dir.rglob(pattern)
            if path.is_file()
        ]
    )


def _score_artifact(artifact: dict[str, Any]) -> float:
    """Compute a simple overall ranking score for one generated artifact."""

    score = float(artifact.get("playability", {}).get("score", 0.0))
    if artifact.get("musicxml_path"):
        score += 5.0

    pianoplayer = artifact.get("pianoplayer_evaluation")
    if pianoplayer:
        status = pianoplayer.get("status")
        if status == "ok":
            score += 10.0
        elif status == "unavailable":
            score += 0.0
        else:
            score -= 5.0

    return round(score, 2)


def _rank_artifacts(summary: dict[str, Any], *, top_k: int = 10) -> list[dict[str, Any]]:
    """Flatten all artifacts, rank them, and return the top entries."""

    ranked: list[dict[str, Any]] = []
    for backend, backend_result in summary.get("backends", {}).items():
        if backend_result.get("status") != "ok":
            continue
        for index, artifact in enumerate(backend_result.get("artifacts", []), start=1):
            row = {
                "backend": backend,
                "artifact_index": index,
                "midi_path": artifact.get("midi_path"),
                "musicxml_path": artifact.get("musicxml_path"),
                "playability": artifact.get("playability"),
                "pianoplayer_evaluation": artifact.get("pianoplayer_evaluation"),
                "overall_score": _score_artifact(artifact),
            }
            ranked.append(row)

    ranked.sort(
        key=lambda item: (
            item["overall_score"],
            item.get("playability", {}).get("score", 0.0),
            1 if item.get("musicxml_path") else 0,
        ),
        reverse=True,
    )
    return ranked[:top_k]


def run_text_to_midi_backend(
    backend: str,
    request: TextToMidiRequest,
    *,
    workspace: str | Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run an external backend script."""

    if backend not in BACKENDS:
        raise ValueError(f"Unknown backend '{backend}'. Available: {', '.join(BACKENDS)}")

    request.output_dir.mkdir(parents=True, exist_ok=True)
    spec = BACKENDS[backend]
    entrypoint = spec.resolve_entrypoint(workspace=workspace)
    if not entrypoint.exists():
        raise FileNotFoundError(
            f"Backend entrypoint not found for '{backend}': {entrypoint}. "
            f"Set {spec.env_var} or place the repo under {spec.default_relpath}."
        )

    command = spec.command_builder(entrypoint, request)
    return subprocess.run(command, check=check, text=True, capture_output=True)


def compare_text_to_midi_backends(
    prompt: str,
    backends: list[str],
    output_root: str | Path,
    *,
    workspace: str | Path | None = None,
    n_outputs: int = 1,
    device: str = "cpu",
    with_pianoplayer: bool = False,
    pianoplayer_hand_size: str = "M",
    top_k: int = 10,
) -> dict[str, Any]:
    """Run multiple backends and evaluate their outputs in a shared format."""

    output_dir = Path(output_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "prompt": prompt,
        "backends": {},
    }

    for backend in backends:
        backend_dir = output_dir / backend
        request = TextToMidiRequest(
            prompt=prompt,
            output_dir=backend_dir,
            n_outputs=n_outputs,
            device=device,
        )

        try:
            completed = run_text_to_midi_backend(
                backend,
                request,
                workspace=workspace,
                check=True,
            )
            midi_files = _collect_generated_midis(backend_dir)
            artifacts = []
            for midi_path in midi_files:
                playability = evaluate_piano_midi_playability(midi_path)
                artifact = {
                    "midi_path": str(midi_path),
                    "playability": playability.to_dict(),
                }
                try:
                    musicxml_path = midi_to_musicxml(midi_path)
                    artifact["musicxml_path"] = str(musicxml_path)
                    if with_pianoplayer:
                        artifact["pianoplayer_evaluation"] = evaluate_with_pianoplayer(
                            musicxml_path,
                            hand_size=pianoplayer_hand_size,
                        ).to_dict()
                except Exception as exc:  # pragma: no cover - environment dependent
                    artifact["musicxml_error"] = str(exc)
                artifacts.append(artifact)

            summary["backends"][backend] = {
                "status": "ok",
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "generated_count": len(midi_files),
                "artifacts": artifacts,
            }
        except Exception as exc:  # pragma: no cover - exercised via tests with monkeypatch
            summary["backends"][backend] = {
                "status": "error",
                "error": str(exc),
                "generated_count": 0,
                "artifacts": [],
            }

    top_candidates = _rank_artifacts(summary, top_k=top_k)
    summary_path = output_dir / "comparison_summary.json"
    top_path = output_dir / "top_candidates.json"
    summary["summary_path"] = str(summary_path)
    summary["top_candidates"] = top_candidates
    summary["top_candidates_path"] = str(top_path)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    top_path.write_text(json.dumps(top_candidates, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
