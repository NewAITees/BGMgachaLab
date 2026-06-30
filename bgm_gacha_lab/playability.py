"""Playability heuristics for solo-piano MIDI files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

import mido


@dataclass(slots=True)
class PlayabilityReport:
    """Heuristic report for whether a piano MIDI looks playable by a human."""

    note_count: int
    max_simultaneous_notes: int
    large_jump_count: int
    out_of_range_count: int
    mean_notes_per_onset: float
    score: float
    judgement: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_count": self.note_count,
            "max_simultaneous_notes": self.max_simultaneous_notes,
            "large_jump_count": self.large_jump_count,
            "out_of_range_count": self.out_of_range_count,
            "mean_notes_per_onset": self.mean_notes_per_onset,
            "score": self.score,
            "judgement": self.judgement,
        }


def _collect_note_onsets(midi_path: Path) -> list[tuple[float, list[int]]]:
    midi = mido.MidiFile(midi_path)
    absolute_time = 0.0
    grouped: dict[float, list[int]] = {}

    for message in midi:
        absolute_time += message.time
        if message.type == "note_on" and message.velocity > 0:
            bucket = round(absolute_time, 3)
            grouped.setdefault(bucket, []).append(int(message.note))

    return sorted(grouped.items(), key=lambda item: item[0])


def evaluate_piano_midi_playability(
    midi_path: str | Path,
    *,
    min_pitch: int = 21,
    max_pitch: int = 108,
    max_reasonable_chord: int = 6,
    large_jump_threshold: int = 12,
) -> PlayabilityReport:
    """Score a MIDI using simple piano-focused heuristics."""

    path = Path(midi_path)
    onsets = _collect_note_onsets(path)
    notes = [pitch for _, pitches in onsets for pitch in pitches]

    if not notes:
        return PlayabilityReport(
            note_count=0,
            max_simultaneous_notes=0,
            large_jump_count=0,
            out_of_range_count=0,
            mean_notes_per_onset=0.0,
            score=0.0,
            judgement="empty",
        )

    max_simultaneous = max(len(pitches) for _, pitches in onsets)
    out_of_range_count = sum(1 for note in notes if note < min_pitch or note > max_pitch)

    melodic_centers = [round(mean(pitches)) for _, pitches in onsets if pitches]
    large_jump_count = 0
    for previous, current in zip(melodic_centers, melodic_centers[1:]):
        if abs(current - previous) > large_jump_threshold:
            large_jump_count += 1

    onset_sizes = [len(pitches) for _, pitches in onsets]
    mean_notes_per_onset = mean(onset_sizes)

    score = 100.0
    if max_simultaneous > max_reasonable_chord:
        score -= (max_simultaneous - max_reasonable_chord) * 10.0
    score -= large_jump_count * 7.5
    score -= out_of_range_count * 8.0
    score = max(0.0, min(score, 100.0))

    if score >= 80:
        judgement = "playable"
    elif score >= 55:
        judgement = "challenging"
    else:
        judgement = "impractical"

    return PlayabilityReport(
        note_count=len(notes),
        max_simultaneous_notes=max_simultaneous,
        large_jump_count=large_jump_count,
        out_of_range_count=out_of_range_count,
        mean_notes_per_onset=round(mean_notes_per_onset, 3),
        score=round(score, 2),
        judgement=judgement,
    )
