"""Tests for MIDI playability heuristics."""

from __future__ import annotations

from pathlib import Path

import mido

from bgm_gacha_lab.playability import evaluate_piano_midi_playability


def _write_midi(path: Path, notes: list[tuple[int, int]]) -> None:
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)

    first = True
    for note, delta in notes:
        track.append(mido.Message("note_on", note=note, velocity=64, time=delta if first else delta))
        track.append(mido.Message("note_off", note=note, velocity=0, time=120))
        first = False

    midi.save(path)


def test_playability_for_simple_scale(tmp_path):
    midi_path = tmp_path / "scale.mid"
    _write_midi(midi_path, [(60, 0), (62, 120), (64, 120), (65, 120)])

    report = evaluate_piano_midi_playability(midi_path)

    assert report.note_count == 4
    assert report.max_simultaneous_notes == 1
    assert report.judgement == "playable"
    assert report.score > 80


def test_playability_flags_large_jumps(tmp_path):
    midi_path = tmp_path / "jumps.mid"
    _write_midi(midi_path, [(40, 0), (80, 120), (43, 120), (84, 120)])

    report = evaluate_piano_midi_playability(midi_path)

    assert report.large_jump_count >= 2
    assert report.score < 80
