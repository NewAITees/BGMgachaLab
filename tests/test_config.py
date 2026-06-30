"""Tests for configuration and presets."""

from pathlib import Path

import pytest

from bgm_gacha_lab.config import (
    CAFE_PROMPT,
    NIGHT_PROMPT,
    PRESETS,
    RAINY_PROMPT,
    GenerationConfig,
    get_lofi_cafe_preset,
    get_lofi_night_preset,
    get_lofi_rainy_preset,
)


def test_generation_config_defaults():
    """Test GenerationConfig default values."""
    config = GenerationConfig()

    assert config.model_name == "facebook/musicgen-stereo-medium"
    assert config.duration == 30.0
    assert config.num_samples == 12
    assert config.batch_size == 1
    assert config.temperature == 1.0
    assert config.top_k == 250
    assert config.top_p == 0.0
    assert config.cfg_coef == 4.0
    assert config.base_prompt == ""
    assert config.output_dir == Path("outputs")


def test_generation_config_validation():
    """Test GenerationConfig validation."""
    # Valid config
    config = GenerationConfig(duration=60.0, num_samples=5, batch_size=2)
    assert config.duration == 60.0
    assert config.num_samples == 5
    assert config.batch_size == 2

    # Invalid duration (must be > 0)
    with pytest.raises(ValueError):
        GenerationConfig(duration=0)

    with pytest.raises(ValueError):
        GenerationConfig(duration=-10)

    # Invalid num_samples (must be > 0)
    with pytest.raises(ValueError):
        GenerationConfig(num_samples=0)

    # Invalid batch_size (must be > 0)
    with pytest.raises(ValueError):
        GenerationConfig(batch_size=0)


def test_generation_config_model_copy():
    """Test GenerationConfig.model_copy with overrides."""
    base = GenerationConfig(num_samples=10, duration=20.0)

    updated = base.model_copy(update={"num_samples": 5, "temperature": 1.5})

    assert updated.num_samples == 5
    assert updated.temperature == 1.5
    assert updated.duration == 20.0  # unchanged


def test_presets_exist():
    """Test that all expected presets exist."""
    assert "night" in PRESETS
    assert "rainy" in PRESETS
    assert "cafe" in PRESETS


def test_night_preset():
    """Test night preset configuration."""
    preset = get_lofi_night_preset()

    assert preset.base_prompt == NIGHT_PROMPT
    assert preset.output_dir == Path("outputs/night")
    assert "lofi" in preset.base_prompt.lower()
    assert "night" in preset.base_prompt.lower()


def test_rainy_preset():
    """Test rainy preset configuration."""
    preset = get_lofi_rainy_preset()

    assert preset.base_prompt == RAINY_PROMPT
    assert preset.output_dir == Path("outputs/rainy")
    assert "lofi" in preset.base_prompt.lower()
    assert "rainy" in preset.base_prompt.lower() or "rain" in preset.base_prompt.lower()


def test_cafe_preset():
    """Test cafe preset configuration."""
    preset = get_lofi_cafe_preset()

    assert preset.base_prompt == CAFE_PROMPT
    assert preset.output_dir == Path("outputs/cafe")
    assert "lofi" in preset.base_prompt.lower() or "cozy" in preset.base_prompt.lower()
    assert "cafe" in preset.base_prompt.lower() or "coffee" in preset.base_prompt.lower()


def test_presets_dict():
    """Test PRESETS dictionary structure."""
    assert PRESETS["night"] == get_lofi_night_preset()
    assert PRESETS["rainy"] == get_lofi_rainy_preset()
    assert PRESETS["cafe"] == get_lofi_cafe_preset()
