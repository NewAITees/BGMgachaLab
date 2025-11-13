"""Tests for BGM generation logic."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import torch

from bgm_gacha_lab.config import GenerationConfig
from bgm_gacha_lab.generator import _ensure_output_dir, generate_bgm, load_model


@pytest.fixture
def mock_model():
    """Create a mock MusicGen model."""
    model = MagicMock()
    model.generate.return_value = torch.randn(1, 1, 32000 * 30)  # 30s audio at 32kHz
    return model


@pytest.fixture
def test_config(tmp_path):
    """Create a test configuration."""
    return GenerationConfig(
        num_samples=2,
        batch_size=1,
        duration=5.0,
        output_dir=tmp_path / "test_outputs",
        base_prompt="test lofi beat",
    )


def test_ensure_output_dir(tmp_path):
    """Test output directory creation."""
    output_dir = tmp_path / "nested" / "output"
    assert not output_dir.exists()

    _ensure_output_dir(output_dir)

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_ensure_output_dir_existing(tmp_path):
    """Test that existing directory doesn't raise error."""
    output_dir = tmp_path / "existing"
    output_dir.mkdir(parents=True, exist_ok=True)

    _ensure_output_dir(output_dir)

    assert output_dir.exists()


@patch("bgm_gacha_lab.generator.audio_write")
def test_generate_bgm_single_sample(mock_audio_write, mock_model, test_config):
    """Test generating a single BGM sample."""
    test_config.num_samples = 1
    test_config.batch_size = 1

    generated = generate_bgm(mock_model, test_config)

    assert len(generated) == 1
    assert all(isinstance(p, Path) for p in generated)
    mock_model.set_generation_params.assert_called_once()
    mock_model.generate.assert_called_once()
    mock_audio_write.assert_called_once()


@patch("bgm_gacha_lab.generator.audio_write")
def test_generate_bgm_multiple_samples(mock_audio_write, mock_model, test_config):
    """Test generating multiple BGM samples."""
    test_config.num_samples = 3
    test_config.batch_size = 1

    generated = generate_bgm(mock_model, test_config)

    assert len(generated) == 3
    assert mock_model.generate.call_count == 3
    assert mock_audio_write.call_count == 3


@patch("bgm_gacha_lab.generator.audio_write")
def test_generate_bgm_batched(mock_audio_write, mock_model, test_config):
    """Test batch generation."""
    test_config.num_samples = 5
    test_config.batch_size = 2

    # Mock generate to return different batch sizes
    def generate_side_effect(prompts):
        batch_size = len(prompts)
        return torch.randn(batch_size, 1, 32000 * 5)

    mock_model.generate.side_effect = generate_side_effect

    generated = generate_bgm(mock_model, test_config)

    assert len(generated) == 5
    # 5 samples / 2 batch_size = 3 batches (2+2+1)
    assert mock_model.generate.call_count == 3


@patch("bgm_gacha_lab.generator.audio_write")
def test_generate_bgm_sets_params(mock_audio_write, mock_model, test_config):
    """Test that generation parameters are set correctly."""
    test_config.temperature = 1.2
    test_config.top_k = 300
    test_config.top_p = 0.9
    test_config.cfg_coef = 5.0

    generate_bgm(mock_model, test_config)

    mock_model.set_generation_params.assert_called_once_with(
        temperature=1.2,
        top_k=300,
        top_p=0.9,
        duration=test_config.duration,
        cfg_coef=5.0,
    )


def test_generate_bgm_invalid_samples(mock_model):
    """Test that invalid num_samples raises validation error."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        GenerationConfig(num_samples=0)


def test_generate_bgm_invalid_batch_size(mock_model):
    """Test that invalid batch_size raises validation error."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        GenerationConfig(batch_size=-1)


@patch("bgm_gacha_lab.generator.MusicGen")
def test_load_model_cuda(mock_musicgen_class):
    """Test loading model on CUDA."""
    mock_model = MagicMock()
    mock_musicgen_class.get_pretrained.return_value = mock_model

    result = load_model("facebook/musicgen-small", device="cuda")

    mock_musicgen_class.get_pretrained.assert_called_once_with(
        "facebook/musicgen-small", device="cuda"
    )
    assert result == mock_model


@patch("bgm_gacha_lab.generator.MusicGen")
def test_load_model_cpu(mock_musicgen_class):
    """Test loading model on CPU."""
    mock_model = MagicMock()
    mock_musicgen_class.get_pretrained.return_value = mock_model

    result = load_model("facebook/musicgen-small", device="cpu")

    mock_musicgen_class.get_pretrained.assert_called_once_with(
        "facebook/musicgen-small", device="cpu"
    )
    assert result == mock_model
