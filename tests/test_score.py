"""Tests for symbolic score conversion helpers."""

from __future__ import annotations

import mido

from bgm_gacha_lab.score import midi_to_musicxml


def test_midi_to_musicxml_creates_output(tmp_path):
    midi_path = tmp_path / "example.mid"
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.Message("note_on", note=60, velocity=64, time=0))
    track.append(mido.Message("note_off", note=60, velocity=0, time=120))
    midi.save(midi_path)

    output_path = midi_to_musicxml(midi_path)

    assert output_path.exists()
    assert output_path.suffix == ".musicxml"
