"""Helpers for converting symbolic music into score-oriented formats."""

from __future__ import annotations

from pathlib import Path

from music21 import converter


def midi_to_musicxml(midi_path: str | Path, output_path: str | Path | None = None) -> Path:
    """Convert a MIDI file to MusicXML using music21."""

    midi_file = Path(midi_path)
    target = Path(output_path) if output_path is not None else midi_file.with_suffix(".musicxml")
    score = converter.parse(str(midi_file))
    score.write("musicxml", fp=str(target))
    return target
