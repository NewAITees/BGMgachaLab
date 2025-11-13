"""Core MusicGen generation helpers."""

from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import List

from .compat import patch_torch_pytree
from .config import GenerationConfig

patch_torch_pytree()

from audiocraft.data.audio import audio_write
from audiocraft.models import MusicGen


def load_model(model_name: str, device: str = "cuda") -> MusicGen:
    """Load a MusicGen checkpoint on the requested device."""
    print(f"Loading model '{model_name}' on {device} ...")
    model = MusicGen.get_pretrained(model_name, device=device)
    return model


def _ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_bgm(model: MusicGen, config: GenerationConfig) -> List[Path]:
    """Generate lofi BGM clips according to *config*."""
    _ensure_output_dir(config.output_dir)
    generated_files: List[Path] = []

    total = config.num_samples
    batch_size = config.batch_size
    if total <= 0 or batch_size <= 0:
        raise ValueError("num_samples and batch_size must be positive")

    num_batches = ceil(total / batch_size)
    print(
        "Starting generation:",
        f"samples={config.num_samples}",
        f"batch_size={config.batch_size}",
        f"batches={num_batches}",
        f"prompt='{config.base_prompt[:60]}...'" if config.base_prompt else "prompt=<empty>",
    )

    model.set_generation_params(
        temperature=config.temperature,
        top_k=config.top_k,
        top_p=config.top_p,
        duration=config.duration,
        cfg_coef=config.cfg_coef,
    )

    produced = 0
    for batch_idx in range(num_batches):
        remaining = total - produced
        current_batch = min(batch_size, remaining)
        print(f"Batch {batch_idx + 1}/{num_batches}: generating {current_batch} clips ...")
        prompts = [config.base_prompt] * current_batch
        wavs = model.generate(prompts)
        wavs = wavs.detach().cpu()

        for tensor in wavs:
            clip_index = len(generated_files)
            # audio_write automatically adds .wav extension, so use stem only
            filename_stem = config.output_dir / f"lofi_{clip_index:03d}"
            audio_write(
                filename_stem,
                tensor,
                sample_rate=32000,
                strategy="loudness",
            )
            # audio_write adds .wav, so append the full path
            final_path = filename_stem.with_suffix(".wav")
            generated_files.append(final_path)
            produced += 1
            print(f"  saved -> {final_path}")

    print("Generation complete.")
    return generated_files
