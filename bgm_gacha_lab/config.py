"""Configuration presets and utilities for BGMgachaLab."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field


class GenerationConfig(BaseModel):
    """Runtime configuration for a MusicGen batch."""

    model_config = ConfigDict(validate_assignment=True)

    model_name: str = Field(default="facebook/musicgen-stereo-medium")
    duration: float = Field(default=30.0, gt=0, description="Clip length in seconds")
    num_samples: int = Field(default=12, gt=0)
    batch_size: int = Field(default=1, gt=0)
    temperature: float = Field(default=1.0, gt=0)
    top_k: int = Field(default=250)
    top_p: float = Field(default=0.0, ge=0, le=1)
    cfg_coef: float = Field(default=4.0, ge=0)
    base_prompt: str = Field(default="")
    output_dir: Path = Field(default=Path("outputs"))
    filename_prefix: str = Field(default="lofi")
    sample_rate: int = Field(default=32000, gt=0)
    max_segment_duration: float = Field(
        default=150.0,
        gt=0,
        description="Maximum per-call duration in seconds before audio is stitched",
    )


NIGHT_PROMPT = (
    "lofi chill hip hop beat, warm rhodes piano, soft dusty drums, vinyl crackle, "
    "mellow, no vocals, 75 bpm, smooth loop, night mood"
)

RAINY_PROMPT = (
    "lofi chill beat for a rainy day, soft piano, gentle rain ambience, vinyl noise, "
    "calm, no vocals, 72 bpm, background music"
)

CAFE_PROMPT = (
    "cozy coffee shop lofi, jazzy chords, soft drums, light crowd ambience, tape hiss, "
    "80 bpm, relaxed background"
)


def get_lofi_night_preset() -> GenerationConfig:
    return GenerationConfig(
        base_prompt=NIGHT_PROMPT,
        output_dir=Path("outputs/night"),
    )


def get_lofi_rainy_preset() -> GenerationConfig:
    return GenerationConfig(
        base_prompt=RAINY_PROMPT,
        output_dir=Path("outputs/rainy"),
    )


def get_lofi_cafe_preset() -> GenerationConfig:
    return GenerationConfig(
        base_prompt=CAFE_PROMPT,
        output_dir=Path("outputs/cafe"),
    )


PRESETS: Dict[str, GenerationConfig] = {
    "night": get_lofi_night_preset(),
    "rainy": get_lofi_rainy_preset(),
    "cafe": get_lofi_cafe_preset(),
}
