# BGMgachaLab

## プロジェクト概要
BGMgachaLab は `musicgen` ベースのジェネレーティブ BGM ツールで、CLI からプリセットを選んで複数トラックをバッチ生成できます。`compat.py` で torch/transformers の細かな差異を吸収しつつ、`generator.py` が MusicGen モデルのダウンロードと推論を自動処理。`config.py` と `tests/` 以下の 26 テストケースによりプリセットや CLI 仕様が守られているため、GPU/CPU どちらでも安定したサンプル生成と再現性の高いワークフローを提供します。

### 主な特徴
- `uv run bgm-gacha …` で即実行できるシンプルな CLI。
- `night`/`cafe` などのプリセットに加え、温度・長さ・バッチサイズなどを柔軟指定。
- `--prompt` でベースプロンプトを上書きし、`--tag` でファイル名プレフィックスも制御可能。
- 長尺（>150 秒）を指定すると自動的にセグメント分割し、32-bit index 制限による RuntimeError を回避。
- wav ファイルは `outputs/<preset>/` に自動整理され、命名衝突も防止済み。
- `tests/test_*.py` による包括的テストで設定・生成・CLI を網羅。

### 代表的なコマンド
```bash
# ヘルプ
uv run bgm-gacha --help

# 夜向けローファイを 5 本生成
uv run bgm-gacha --preset night --num-samples 5 --batch-size 2

# カフェプリセットを 60 秒・温度 1.2 で 10 本生成（プロンプト上書き & ファイル名指定）
uv run bgm-gacha --preset cafe --num-samples 10 --duration 60 --temperature 1.2 \
  --prompt "jazzy piano techno" --tag cafe_focus

# 10 分を 120 秒セグメントで書き出し
uv run bgm-gacha --preset night --duration 600 --num-samples 2 --max-segment-duration 120

# テスト
uv run pytest tests/ -v
```

## ピアノテクノ Chill 作業 BGM セット（各 10 分）
以下はピアノを軸にしたテクノ BGM を 10 パターン用意するためのリクエストプリセット例です。全曲 10 分（`--duration 600`）を想定し、集中を保ちながら眠くならないようテンポとテクスチャを調整しています。`--prompt` は MusicGen のテキスト条件、`--temperature` や `--tag`（ファイル名プレフィックス）を自由に調整してください。

| # | タイトル / ムード | 推奨テンポ | 推奨コマンド例 |
|---|------------------|------------|----------------|
| 1 | Midnight Keys Drive（都会的ドライブ感） | 122 BPM | `uv run bgm-gacha --preset night --duration 600 --temperature 1.0 --prompt "piano led techno groove, glossy synth pads, midnight city" --tag midnight_keys_drive`
| 2 | Neon Raindrops | 118 BPM | `uv run bgm-gacha --preset cafe --duration 600 --temperature 0.9 --prompt "soft piano arpeggio techno, gentle rain foley, chill focus" --tag neon_raindrops`
| 3 | Circuit Garden | 126 BPM | `uv run bgm-gacha --preset night --duration 600 --temperature 1.1 --prompt "percussive piano stabs with modular techno pulses, blooming pads" --tag circuit_garden`
| 4 | Moonlit Assembly | 112 BPM | `uv run bgm-gacha --preset cafe --duration 600 --temperature 0.85 --prompt "minimal piano ostinato, subtle 4-on-the-floor kick, airy ambience" --tag moonlit_assembly`
| 5 | Vapor Keys Relay | 128 BPM | `uv run bgm-gacha --preset night --duration 600 --temperature 1.2 --prompt "bright piano chords, retro techno bassline, hazy shimmer" --tag vapor_keys_relay`
| 6 | Aurora Loop | 116 BPM | `uv run bgm-gacha --preset cafe --duration 600 --temperature 0.95 --prompt "glacial piano motif, downtempo techno beat, long tails" --tag aurora_loop`
| 7 | Copper Wire Waltz | 120 BPM (3/4 feel) | `uv run bgm-gacha --preset night --duration 600 --temperature 1.05 --prompt "piano triplet arpeggios, swung techno percussion, analog hiss" --tag copper_wire_waltz`
| 8 | Gravity Sketch | 124 BPM | `uv run bgm-gacha --preset night --duration 600 --temperature 1.0 --prompt "tight piano plucks, rolling bass, focus friendly techno" --tag gravity_sketch`
| 9 | Driftwood Metro | 114 BPM | `uv run bgm-gacha --preset cafe --duration 600 --temperature 0.9 --prompt "loose piano chords, dub techno delay, cozy workspace vibe" --tag driftwood_metro`
|10 | Prism Bloom | 130 BPM | `uv run bgm-gacha --preset night --duration 600 --temperature 1.15 --prompt "energetic piano riffs, sidechained pads, uplifting techno" --tag prism_bloom`

Tips:
- 10 分を超える場合は自動で 150 秒前後のセグメントに分割されます。明示的に変えたいときは `--max-segment-duration 120` のように指定してください。
- 少し長めに生成しておき、不要部分は DAW でフェードアウトすると滑らかです。
- 同じ設定で響きを変えたいときは `--temperature` を少しずつ増減しつつ、`--tag` でプレフィックスを分けると整理がラクです。
- アウトプットフォルダを整理したいときは `--output-dir outputs/piano_techno_set` などを指定すると 10 曲すべてをまとめやすいです。
- `--tag` にスペースを入れた場合は自動的に `_` に変換されます。
