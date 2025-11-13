"""Tests for CLI interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from bgm_gacha_lab.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI --help command."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Generate BGM clips based on presets" in result.stdout
    assert "--preset" in result.stdout
    assert "--model-name" in result.stdout
    assert "--num-samples" in result.stdout
    assert "--device" in result.stdout


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_generate_default(mock_generate, mock_load_model):
    """Test generate command with default preset."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_generate.return_value = [Path("outputs/night/lofi_000.wav")]

    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert "night" in result.stdout.lower()
    mock_load_model.assert_called_once()
    mock_generate.assert_called_once_with(mock_model, pytest.approx(mock_generate.call_args[0][1], abs=0.1))


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_generate_with_preset(mock_generate, mock_load_model):
    """Test generate command with specified preset."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_generate.return_value = [Path("outputs/rainy/lofi_000.wav")]

    result = runner.invoke(app, ["--preset", "rainy"])

    assert result.exit_code == 0
    assert "rainy" in result.stdout.lower()
    mock_generate.assert_called_once()


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_generate_with_overrides(mock_generate, mock_load_model):
    """Test generate command with parameter overrides."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_generate.return_value = [
        Path("outputs/test/lofi_000.wav"),
        Path("outputs/test/lofi_001.wav"),
    ]

    result = runner.invoke(
        app,
        [
            "--preset",
            "night",
            "--num-samples",
            "2",
            "--batch-size",
            "1",
            "--duration",
            "10.0",
            "--temperature",
            "1.2",
        ],
    )

    assert result.exit_code == 0
    mock_generate.assert_called_once()

    # Check that config has the overrides
    config = mock_generate.call_args[0][1]
    assert config.num_samples == 2
    assert config.batch_size == 1
    assert config.duration == 10.0
    assert config.temperature == 1.2


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_generate_cpu_device(mock_generate, mock_load_model):
    """Test generate command with CPU device."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_generate.return_value = [Path("outputs/night/lofi_000.wav")]

    result = runner.invoke(app, ["--device", "cpu"])

    assert result.exit_code == 0
    mock_load_model.assert_called_once()
    # Check device argument
    assert mock_load_model.call_args[1]["device"] == "cpu"


def test_cli_generate_invalid_preset():
    """Test generate command with invalid preset."""
    result = runner.invoke(app, ["--preset", "invalid_preset"])

    assert result.exit_code != 0
    # Check for error output (could be in stdout or stderr)
    output = result.stdout + (result.stderr or "")
    assert "Unknown preset" in output or "invalid_preset" in output


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_output_display(mock_generate, mock_load_model):
    """Test that generated files are displayed."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_generate.return_value = [
        Path("outputs/night/lofi_000.wav"),
        Path("outputs/night/lofi_001.wav"),
        Path("outputs/night/lofi_002.wav"),
    ]

    result = runner.invoke(app, ["--preset", "night"])

    assert result.exit_code == 0
    assert "lofi_000.wav" in result.stdout
    assert "lofi_001.wav" in result.stdout
    assert "lofi_002.wav" in result.stdout


@patch("bgm_gacha_lab.cli.load_model")
@patch("bgm_gacha_lab.cli.generate_bgm")
def test_cli_custom_output_dir(mock_generate, mock_load_model, tmp_path):
    """Test generate command with custom output directory."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    output_dir = tmp_path / "custom_outputs"
    mock_generate.return_value = [output_dir / "lofi_000.wav"]

    result = runner.invoke(app, ["--output-dir", str(output_dir)])

    assert result.exit_code == 0
    config = mock_generate.call_args[0][1]
    assert config.output_dir == output_dir
