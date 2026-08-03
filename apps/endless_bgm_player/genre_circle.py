"""ジャンル円環表とプロンプト補間ロジック。

8つのジャンルを円環状に配置し、位置(0〜8の浮動小数)を毎曲少しずつ
前進させることで、隣接ジャンルの特徴を線形補間しながら滑らかに
プロンプトを変化させる。同じ位置でも毎回まったく同じ文にならないよう、
ジャンルごとのランダム語彙プールから追加の記述語を混ぜ込む。
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Genre:
    name: str
    instruments: list[str]
    mood: list[str]
    bpm_range: tuple[int, int]
    extra_vocab: list[str]


GENRES: list[Genre] = [
    Genre(
        name="Ambient Drift",
        instruments=["soft evolving pads", "distant airy textures", "sparse chime accents"],
        mood=["ethereal", "spacious", "weightless"],
        bpm_range=(60, 70),
        extra_vocab=[
            "slow tape wobble",
            "field recording texture",
            "long reverb tail",
            "granular shimmer",
            "soft wind noise",
        ],
    ),
    Genre(
        name="Lofi Chillhop",
        instruments=["warm rhodes piano", "dusty boom-bap drums", "soft upright bass"],
        mood=["nostalgic", "mellow", "cozy"],
        bpm_range=(72, 80),
        extra_vocab=[
            "vinyl crackle",
            "tape hiss",
            "muffled kick",
            "lo-fi bitcrush",
            "rainy window ambience",
        ],
    ),
    Genre(
        name="Jazzy Cafe",
        instruments=["soft jazz piano chords", "brushed snare drums", "walking upright bass"],
        mood=["warm", "relaxed", "intimate"],
        bpm_range=(85, 95),
        extra_vocab=[
            "light cafe chatter",
            "soft ride cymbal swing",
            "muted trumpet accent",
            "gentle piano pedal noise",
            "coffee shop ambience",
        ],
    ),
    Genre(
        name="Bossa Downtempo",
        instruments=["nylon string guitar", "soft latin percussion", "airy flute accents"],
        mood=["breezy", "laid-back", "sun-warmed"],
        bpm_range=(90, 100),
        extra_vocab=[
            "shaker texture",
            "soft conga hits",
            "ocean breeze ambience",
            "warm analog saturation",
            "gentle guiro scrape",
        ],
    ),
    Genre(
        name="Deep Chill House",
        instruments=["warm sub bass", "soft four-on-the-floor kick", "mellow analog chords"],
        mood=["smooth", "hypnotic", "warm"],
        bpm_range=(100, 112),
        extra_vocab=[
            "soft filtered hi-hats",
            "deep vinyl warmth",
            "subtle sidechain pump",
            "warm analog hum",
            "distant vocal chop",
        ],
    ),
    Genre(
        name="Chill Techno",
        instruments=["minimal percussive pulse", "subtle arpeggiated synth", "understated kick pattern"],
        mood=["focused", "understated", "hypnotic"],
        bpm_range=(112, 122),
        extra_vocab=[
            "metallic percussion click",
            "soft modular blips",
            "subtle white noise sweep",
            "muted clap texture",
            "analog sequencer hum",
        ],
    ),
    Genre(
        name="Synth Dreamscape",
        instruments=["lush analog synth pads", "retro arpeggios", "soft glassy leads"],
        mood=["dreamy", "nostalgic-futuristic", "hazy"],
        bpm_range=(90, 100),
        extra_vocab=[
            "warm chorus shimmer",
            "retro cassette warble",
            "soft neon glow texture",
            "gentle synth swell",
            "vintage delay tail",
        ],
    ),
    Genre(
        name="Acoustic Chill",
        instruments=["soft acoustic guitar", "gentle felt piano", "light hand percussion"],
        mood=["organic", "intimate", "warm"],
        bpm_range=(70, 80),
        extra_vocab=[
            "room ambience",
            "soft finger noise on strings",
            "warm wood resonance",
            "gentle string squeak",
            "quiet room tone",
        ],
    ),
]

GENRE_COUNT = len(GENRES)


def advance_position(pos: float, step: float = 0.25, jitter: float = 0.3) -> float:
    """円環上の位置を単調前進させる。ジッターで進み幅にランダム性を持たせる。"""
    actual_step = step * random.uniform(1 - jitter, 1 + jitter)
    return (pos + actual_step) % GENRE_COUNT


def _lerp(a: float, b: float, f: float) -> float:
    return a + (b - a) * f


@dataclass(frozen=True)
class PromptResult:
    prompt: str
    bpm: int
    primary_genre: str
    secondary_genre: str
    blend_fraction: float
    position: float


def build_prompt(pos: float, duration_seconds: int = 120) -> PromptResult:
    """円環上の位置から、隣接ジャンルを補間したプロンプトを合成する。"""
    i = int(pos) % GENRE_COUNT
    f = pos - int(pos)
    j = (i + 1) % GENRE_COUNT
    g_i, g_j = GENRES[i], GENRES[j]

    bpm_i_mid = sum(g_i.bpm_range) / 2
    bpm_j_mid = sum(g_j.bpm_range) / 2
    bpm = round(_lerp(bpm_i_mid, bpm_j_mid, f))

    instruments = list(g_i.instruments)
    mood = list(g_i.mood)
    if f > 0.3:
        instruments = instruments + g_j.instruments[:2]
        mood = mood + g_j.mood[:1]

    vocab_pool = list(dict.fromkeys(g_i.extra_vocab + g_j.extra_vocab))
    extra_count = random.randint(1, 3)
    extra_terms = random.sample(vocab_pool, k=min(extra_count, len(vocab_pool)))

    genre_label = g_i.name if f < 0.5 else f"{g_i.name} drifting toward {g_j.name}"

    instrument_text = ", ".join(dict.fromkeys(instruments))
    mood_text = ", ".join(dict.fromkeys(mood))
    extra_text = ", ".join(extra_terms)

    prompt = (
        f"{genre_label} instrumental BGM track, {instrument_text}, "
        f"{mood_text} mood, {extra_text}, no vocals, "
        f"BPM: {bpm}. Length: {duration_seconds} seconds"
    )

    return PromptResult(
        prompt=prompt,
        bpm=bpm,
        primary_genre=g_i.name,
        secondary_genre=g_j.name,
        blend_fraction=f,
        position=pos,
    )
