"""Tests for optional PianoPlayer evaluation wrapper."""

from __future__ import annotations

import subprocess

from bgm_gacha_lab.pianoplayer_eval import evaluate_with_pianoplayer


def test_pianoplayer_unavailable_returns_soft_failure(tmp_path):
    score_path = tmp_path / "example.musicxml"
    score_path.write_text("<score-partwise/>", encoding="utf-8")

    report = evaluate_with_pianoplayer(score_path, executable="missing-pianoplayer")

    assert report.status == "unavailable"
    assert report.output_path is None


def test_pianoplayer_successful_run(monkeypatch, tmp_path):
    score_path = tmp_path / "example.musicxml"
    score_path.write_text("<score-partwise/>", encoding="utf-8")
    output_path = tmp_path / "example.pianoplayer.musicxml"
    output_path.write_text("<score-partwise/>", encoding="utf-8")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("bgm_gacha_lab.pianoplayer_eval.subprocess.run", fake_run)

    report = evaluate_with_pianoplayer(score_path, output_dir=tmp_path)

    assert report.status == "ok"
    assert report.output_path == str(output_path)


def test_pianoplayer_nonzero_exit_is_error(monkeypatch, tmp_path):
    score_path = tmp_path / "example.musicxml"
    score_path.write_text("<score-partwise/>", encoding="utf-8")

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 2, stdout="", stderr="bad args")

    monkeypatch.setattr("bgm_gacha_lab.pianoplayer_eval.subprocess.run", fake_run)

    report = evaluate_with_pianoplayer(score_path, output_dir=tmp_path)

    assert report.status == "error"
    assert "bad args" in report.stderr
