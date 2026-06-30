"""Tests for text-to-MIDI backend orchestration."""

from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess

import mido

from bgm_gacha_lab.text_to_midi import (
    TextToMidiRequest,
    _rank_artifacts,
    compare_text_to_midi_backends,
    list_text_to_midi_backends,
    run_text_to_midi_backend,
)


def test_list_backends_contains_expected_keys():
    backends = list_text_to_midi_backends()

    assert "midi-llm" in backends
    assert "text2midi" in backends


def test_run_backend_raises_for_missing_entrypoint(tmp_path):
    request = TextToMidiRequest(prompt="test", output_dir=tmp_path / "out")

    try:
        run_text_to_midi_backend("midi-llm", request, workspace=tmp_path)
    except FileNotFoundError as exc:
        assert "Backend entrypoint not found" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")


def test_compare_backends_collects_midi_and_scores(monkeypatch, tmp_path):
    def fake_run(backend, request, **_kwargs):
        request.output_dir.mkdir(parents=True, exist_ok=True)
        midi_path = request.output_dir / f"{backend}.mid"
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(mido.Message("note_on", note=60, velocity=64, time=0))
        track.append(mido.Message("note_off", note=60, velocity=0, time=120))
        midi.save(midi_path)
        return CompletedProcess(args=["python"], returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("bgm_gacha_lab.text_to_midi.run_text_to_midi_backend", fake_run)
    monkeypatch.setattr(
        "bgm_gacha_lab.text_to_midi.midi_to_musicxml",
        lambda midi_path: Path(midi_path).with_suffix(".musicxml"),
    )
    monkeypatch.setattr(
        "bgm_gacha_lab.text_to_midi.evaluate_with_pianoplayer",
        lambda *args, **kwargs: type(
            "DummyReport",
            (),
            {"to_dict": lambda self: {"status": "ok", "hand_size": kwargs.get("hand_size", "M")}},
        )(),
    )

    summary = compare_text_to_midi_backends(
        prompt="simple piano etude",
        backends=["midi-llm", "text2midi"],
        output_root=tmp_path / "compare",
        workspace=tmp_path,
        with_pianoplayer=True,
    )

    assert summary["backends"]["midi-llm"]["status"] == "ok"
    assert summary["backends"]["text2midi"]["generated_count"] == 1
    assert summary["backends"]["midi-llm"]["artifacts"][0]["pianoplayer_evaluation"]["status"] == "ok"
    assert Path(summary["summary_path"]).exists()
    assert Path(summary["top_candidates_path"]).exists()
    assert len(summary["top_candidates"]) == 2


def test_rank_artifacts_returns_highest_scores_first():
    summary = {
        "backends": {
            "midi-llm": {
                "status": "ok",
                "artifacts": [
                    {
                        "midi_path": "a.mid",
                        "musicxml_path": "a.musicxml",
                        "playability": {"score": 70},
                        "pianoplayer_evaluation": {"status": "ok"},
                    },
                    {
                        "midi_path": "b.mid",
                        "playability": {"score": 95},
                    },
                ],
            },
            "text2midi": {
                "status": "ok",
                "artifacts": [
                    {
                        "midi_path": "c.mid",
                        "musicxml_path": "c.musicxml",
                        "playability": {"score": 80},
                        "pianoplayer_evaluation": {"status": "error"},
                    }
                ],
            },
        }
    }

    ranked = _rank_artifacts(summary, top_k=2)

    assert len(ranked) == 2
    assert ranked[0]["midi_path"] == "b.mid"
    assert ranked[0]["overall_score"] > ranked[1]["overall_score"]
