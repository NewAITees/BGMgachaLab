"""Typer-based CLI entrypoints."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .config import PRESETS
from .generator import generate_bgm, load_model

app = typer.Typer(help="Generate lofi/chill BGM batches via MusicGen")


def _sanitize_prefix(value: str) -> str:
    """Sanitize filename prefixes to filesystem-friendly slugs."""

    cleaned = value.strip().lower()
    if not cleaned:
        return "lofi"
    safe_chars = []
    for ch in cleaned:
        if ch.isalnum() or ch in {"-", "_"}:
            safe_chars.append(ch)
        else:
            safe_chars.append("_")
    sanitized = "".join(safe_chars).strip("_")
    return sanitized or "lofi"


@app.command()
def generate(
    preset: str = typer.Option(
        "night",
        "--preset",
        help="Preset prompt to use (night, rainy, cafe, ...)",
    ),
    model_name: Optional[str] = typer.Option(None, "--model-name"),
    num_samples: Optional[int] = typer.Option(None, "--num-samples"),
    duration: Optional[float] = typer.Option(None, "--duration"),
    batch_size: Optional[int] = typer.Option(None, "--batch-size"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir"),
    temperature: Optional[float] = typer.Option(None, "--temperature"),
    top_k: Optional[int] = typer.Option(None, "--top-k"),
    top_p: Optional[float] = typer.Option(None, "--top-p"),
    cfg_coef: Optional[float] = typer.Option(None, "--cfg-coef"),
    prompt: Optional[str] = typer.Option(
        None,
        "--prompt",
        help="Override the base text prompt for MusicGen.",
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        help="Override output filename prefix (defaults to preset's prefix).",
    ),
    max_segment_duration: Optional[float] = typer.Option(
        None,
        "--max-segment-duration",
        help="Force per-call generation duration before segments are stitched (seconds).",
    ),
    device: str = typer.Option("cuda", "--device"),
) -> None:
    """Generate BGM clips based on presets or explicit overrides."""

    if preset not in PRESETS:
        raise typer.BadParameter(
            f"Unknown preset '{preset}'. Available presets: {', '.join(PRESETS)}"
        )

    base_config = PRESETS[preset]
    overrides = {}
    if model_name is not None:
        overrides["model_name"] = model_name
    if num_samples is not None:
        overrides["num_samples"] = num_samples
    if duration is not None:
        overrides["duration"] = duration
    if batch_size is not None:
        overrides["batch_size"] = batch_size
    if output_dir is not None:
        overrides["output_dir"] = output_dir
    if temperature is not None:
        overrides["temperature"] = temperature
    if top_k is not None:
        overrides["top_k"] = top_k
    if top_p is not None:
        overrides["top_p"] = top_p
    if cfg_coef is not None:
        overrides["cfg_coef"] = cfg_coef
    if prompt is not None:
        overrides["base_prompt"] = prompt
    if tag is not None:
        overrides["filename_prefix"] = _sanitize_prefix(tag)
    if max_segment_duration is not None:
        overrides["max_segment_duration"] = max_segment_duration

    config = base_config.model_copy(update=overrides)

    print(f"Using preset '{preset}' with prompt: {config.base_prompt}")
    print(f"Output directory: {config.output_dir}")

    model = load_model(config.model_name if model_name is None else model_name, device=device)
    generated = generate_bgm(model, config)

    print("Generated files:")
    for path in generated:
        print(f" - {path}")


if __name__ == "__main__":
    app()
