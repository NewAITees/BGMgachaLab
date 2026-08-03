"""ジャンル円環表とプロンプト補間ロジック。

複数のジャンルを円環状に配置し、位置(0〜len(GENRES)の浮動小数)を毎曲少しずつ
前進させることで、隣接ジャンルの特徴を線形補間しながら滑らかに
プロンプトを変化させる。同じ位置でも毎回まったく同じ文にならないよう、
ジャンルごとのランダム語彙プールから追加の記述語を混ぜ込む。

ジャンル一覧は genres.json を正本として読み込む。加えて pending_genres/ に
ジャンル定義ファイル(.json)を置くことで、外部から新しいジャンルを円環に
差し込める。差し込み位置は「現在の再生位置から円環上で最も遠い場所」に
挿入される。差し込まれたジャンルは、実際に一度生成に使われるまでは
genres.json へ反映されず、pending_genres/ のファイルも消されない。
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
GENRES_PATH = APP_DIR / "genres.json"
PENDING_DIR = APP_DIR / "pending_genres"
PENDING_DIR.mkdir(exist_ok=True)


@dataclass
class Genre:
    name: str
    instruments: list[str]
    mood: list[str]
    bpm_range: tuple[int, int]
    extra_vocab: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Genre:
        return cls(
            name=data["name"],
            instruments=list(data["instruments"]),
            mood=list(data["mood"]),
            bpm_range=tuple(data["bpm_range"]),  # type: ignore[arg-type]
            extra_vocab=list(data["extra_vocab"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "instruments": self.instruments,
            "mood": self.mood,
            "bpm_range": list(self.bpm_range),
            "extra_vocab": self.extra_vocab,
        }


def _load_genres() -> list[Genre]:
    data = json.loads(GENRES_PATH.read_text(encoding="utf-8"))
    return [Genre.from_dict(item) for item in data]


GENRES: list[Genre] = _load_genres()

# 差し込み済みだがまだ一度も生成に使われていないジャンル名 -> 出所ファイルパス。
# 一度生成に使われたら genres.json へ永続化し、このファイルは削除する。
_pending_file_by_name: dict[str, Path] = {}


def _save_genres() -> None:
    GENRES_PATH.write_text(
        json.dumps([g.to_dict() for g in GENRES], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _farthest_gap_index(current_position: float) -> int:
    """現在位置(0..len(GENRES))から円環上で最も遠い「隙間」のリストindexを返す。"""
    n = len(GENRES)
    if n == 0:
        return 0
    current_deg = (current_position / n) * 360.0
    best_index = 0
    best_dist = -1.0
    for k in range(n):
        gap_deg = ((k - 0.5) / n) * 360.0
        diff = abs((gap_deg - current_deg + 180) % 360 - 180)
        if diff > best_dist:
            best_dist = diff
            best_index = k
    return best_index


def insert_pending_genres(current_position: float) -> float:
    """pending_genres/ にある未処理のジャンル定義を円環へ差し込む。

    複数ある場合は、都度その時点で現在位置から最も遠い隙間に順番に挿入する。
    円環のジャンル数が変わっても現在位置の実角度がずれないよう、position を
    比例して再スケールして返す。
    """
    position = current_position
    pending_files = sorted(PENDING_DIR.glob("*.json"))
    for path in pending_files:
        if path.name in {p.name for p in _pending_file_by_name.values()}:
            continue
        try:
            genre = Genre.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError, KeyError):
            continue
        if any(g.name == genre.name for g in GENRES):
            # 既に(過去の実行で)取り込み済みの名前は二重挿入しない。
            continue

        n_before = len(GENRES)
        index = _farthest_gap_index(position)
        GENRES.insert(index, genre)
        n_after = len(GENRES)
        position = position * (n_after / n_before)
        _pending_file_by_name[genre.name] = path

    return position


def mark_genre_used(name: str) -> None:
    """このジャンルが実際に生成へ使われたら、genres.json へ永続化しpendingを消す。"""
    path = _pending_file_by_name.pop(name, None)
    if path is None:
        return
    _save_genres()
    path.unlink(missing_ok=True)


def advance_position(pos: float, step: float = 0.25, jitter: float = 0.3) -> float:
    """円環上の位置を単調前進させる。ジッターで進み幅にランダム性を持たせる。"""
    n = len(GENRES)
    actual_step = step * random.uniform(1 - jitter, 1 + jitter)
    return (pos + actual_step) % n


def _lerp(a: float, b: float, f: float) -> float:
    return a + (b - a) * f


@dataclass(frozen=True)
class PromptResult:
    prompt: str
    title: str
    bpm: int
    primary_genre: str
    secondary_genre: str
    blend_fraction: float
    position: float


def build_prompt(pos: float, duration_seconds: int = 120) -> PromptResult:
    """円環上の位置から、隣接ジャンルを補間したプロンプトを合成する。"""
    n = len(GENRES)
    i = int(pos) % n
    f = pos - int(pos)
    j = (i + 1) % n
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

    title = f"{g_i.name} — {extra_terms[0].title()}"

    return PromptResult(
        prompt=prompt,
        title=title,
        bpm=bpm,
        primary_genre=g_i.name,
        secondary_genre=g_j.name,
        blend_fraction=f,
        position=pos,
    )
