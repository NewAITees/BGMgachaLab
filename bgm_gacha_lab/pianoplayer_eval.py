"""Optional PianoPlayer-based secondary evaluation for generated piano scores."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PianoPlayerReport:
    """Structured result for an optional PianoPlayer invocation."""

    status: str
    command: list[str]
    stdout: str
    stderr: str
    output_path: str | None
    hand_size: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "output_path": self.output_path,
            "hand_size": self.hand_size,
        }


def evaluate_with_pianoplayer(
    score_path: str | Path,
    *,
    hand_size: str = "M",
    output_dir: str | Path | None = None,
    executable: str = "pianoplayer",
    check: bool = False,
) -> PianoPlayerReport:
    """Run PianoPlayer if available and capture its output without hard-failing the pipeline."""

    score_file = Path(score_path)
    target_dir = Path(output_dir) if output_dir is not None else score_file.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{score_file.stem}.pianoplayer.musicxml"
    score_file = score_file.resolve()
    output_path = output_path.resolve()
    target_dir = target_dir.resolve()

    command = [
        executable,
        str(score_file),
        "--quiet",
        "--hand-size",
        hand_size,
        "-o",
        str(output_path),
    ]

    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=check, cwd=target_dir)
    except FileNotFoundError as exc:
        return PianoPlayerReport(
            status="unavailable",
            command=command,
            stdout="",
            stderr=str(exc),
            output_path=None,
            hand_size=hand_size,
        )
    except subprocess.CalledProcessError as exc:
        return PianoPlayerReport(
            status="error",
            command=command,
            stdout=exc.stdout or "",
            stderr=exc.stderr or str(exc),
            output_path=str(output_path) if output_path.exists() else None,
            hand_size=hand_size,
        )

    if completed.returncode != 0:
        return PianoPlayerReport(
            status="error",
            command=command,
            stdout=completed.stdout,
            stderr=completed.stderr,
            output_path=str(output_path) if output_path.exists() else None,
            hand_size=hand_size,
        )

    return PianoPlayerReport(
        status="ok",
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_path=str(output_path) if output_path.exists() else None,
        hand_size=hand_size,
    )
