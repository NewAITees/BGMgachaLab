"""Core MusicGen generation helpers."""

from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import List

from .compat import patch_torch_pytree
from .config import GenerationConfig

patch_torch_pytree()

from audiocraft.data.audio import audio_write  # noqa: E402
from audiocraft.models import MusicGen  # noqa: E402
import torch  # noqa: E402


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

    def _segment_durations(total_duration: float) -> List[float]:
        max_segment = max(1e-6, min(config.max_segment_duration, total_duration))
        segments = max(1, ceil(total_duration / max_segment))
        durations: List[float] = []
        for idx in range(segments):
            if idx < segments - 1:
                durations.append(max_segment)
            else:
                remaining = total_duration - max_segment * (segments - 1)
                durations.append(remaining if remaining > 0 else max_segment)
        return durations

    segment_durations = _segment_durations(config.duration)
    multi_segment = len(segment_durations) > 1
    if multi_segment:
        print(
            f"Duration {config.duration}s exceeds safe limit; generating in {len(segment_durations)} segments of ~{segment_durations[0]:.1f}s",
        )

    if not segment_durations:
        segment_durations = [config.duration]

    if len(segment_durations) == 1:
        model.set_generation_params(
            temperature=config.temperature,
            top_k=config.top_k,
            top_p=config.top_p,
            duration=segment_durations[0],
            cfg_coef=config.cfg_coef,
        )

    produced = 0
    for batch_idx in range(num_batches):
        remaining = total - produced
        current_batch = min(batch_size, remaining)
        print(f"Batch {batch_idx + 1}/{num_batches}: generating {current_batch} clips ...")
        prompts = [config.base_prompt] * current_batch

        if not multi_segment:
            wavs = model.generate(prompts).detach().cpu()
        else:
            target_samples = int(config.duration * config.sample_rate)
            buffers = [None] * current_batch
            for idx, seg_duration in enumerate(segment_durations):
                model.set_generation_params(
                    temperature=config.temperature,
                    top_k=config.top_k,
                    top_p=config.top_p,
                    duration=seg_duration,
                    cfg_coef=config.cfg_coef,
                )
                seg_wavs = model.generate(prompts).detach().cpu()
                for clip_idx, tensor in enumerate(seg_wavs):
                    if buffers[clip_idx] is None:
                        buffers[clip_idx] = tensor
                    else:
                        buffers[clip_idx] = torch.cat((buffers[clip_idx], tensor), dim=-1)
                print(f"    segment {idx + 1}/{len(segment_durations)} complete")
            wavs = []
            for buf in buffers:
                if buf is None:
                    continue
                trimmed = buf[..., :target_samples]
                # pad if generation undershoots the requested samples
                if trimmed.shape[-1] < target_samples:
                    pad_amount = target_samples - trimmed.shape[-1]
                    pad_tensor = torch.zeros(trimmed.shape[0], pad_amount)
                    trimmed = torch.cat((trimmed, pad_tensor), dim=-1)
                wavs.append(trimmed)

        for tensor in wavs:
            clip_index = len(generated_files)
            # audio_write automatically adds .wav extension, so use stem only
            filename_stem = config.output_dir / f"{config.filename_prefix}_{clip_index:03d}"
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
