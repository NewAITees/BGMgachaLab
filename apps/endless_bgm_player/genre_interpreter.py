"""自由入力テキストをジャンル定義(Genre)へ解釈するモジュール。

ローカルのOllama (http://127.0.0.1:11436) で稼働中のモデルに、
ジャンル名・ゲームタイトルの音楽スタイル・作曲家/アーティスト名などの
短い自由入力を渡し、Genre schema (instruments/mood/bpm_range/extra_vocab) の
JSONを生成させる。実在の作曲家名が入力された場合も、本人の楽曲を模倣するのではなく
音楽的特徴(楽器編成・雰囲気・テンポ)として言語的に解釈させる。
"""

from __future__ import annotations

import json

import httpx

from genre_circle import BPM_CEIL, BPM_FLOOR, Genre

OLLAMA_URL = "http://127.0.0.1:11436"
INTERPRET_MODEL = "gemma4:e4b"

SYSTEM_PROMPT = f"""You are a music genre designer for a background-music generator.
Given a short user description - it may be a genre name, a video game's music style,
or a composer/artist name - output ONLY a single JSON object with exactly these fields:

{{
  "name": short catchy genre label (2-4 words, English),
  "instruments": array of 4-6 short instrument/texture phrases (English),
  "mood": array of 3-5 short mood adjectives/phrases (English),
  "bpm_range": [min, max] integers, {BPM_FLOOR} <= min < max <= {BPM_CEIL},
  "extra_vocab": array of 5-8 short descriptive phrases for variety (English)
}}

If the input references a real composer/artist, interpret their general stylistic
characteristics (typical instrumentation, mood, tempo) rather than naming them
directly anywhere in the output. Output only the JSON object, no other text."""


class GenreInterpretationError(RuntimeError):
    pass


def interpret_genre_text(text: str, timeout: float = 60.0) -> Genre:
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": INTERPRET_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                "stream": False,
                "format": "json",
            },
            timeout=timeout,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        data = json.loads(content)
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise GenreInterpretationError(f"ジャンル解釈に失敗しました: {exc}") from exc

    try:
        name = str(data["name"]).strip()
        instruments = [str(x) for x in data["instruments"]]
        mood = [str(x) for x in data["mood"]]
        lo, hi = data["bpm_range"]
        extra_vocab = [str(x) for x in data["extra_vocab"]]
    except (KeyError, ValueError, TypeError) as exc:
        raise GenreInterpretationError(f"解釈結果の形式が不正です: {data}") from exc

    if not name or not instruments or not mood or not extra_vocab:
        raise GenreInterpretationError(f"解釈結果が不完全です: {data}")

    lo = max(BPM_FLOOR, min(BPM_CEIL, int(lo)))
    hi = max(lo + 5, min(BPM_CEIL, int(hi)))
    if hi <= lo:
        lo, hi = BPM_FLOOR, BPM_FLOOR + 20

    return Genre(
        name=name,
        instruments=instruments,
        mood=mood,
        bpm_range=(lo, hi),
        extra_vocab=extra_vocab,
    )
