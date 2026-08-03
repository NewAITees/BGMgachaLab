# ComfyUI + Stable Audio 3 BGM生成ガイド（現行の標準フロー）

## このガイドについて

BGMgachaLab の現在の標準生成フローは、**ComfyUI Desktop 上で Stable Audio 3 を動かす方式**です。
以前の `MusicGen`（`docs/blog_guide.md`）ベースのCLIフローは旧方式として残っていますが、
音質・プロンプト解釈・運用性の面で Stable Audio 3 + ComfyUI が現行の第一候補です。

このドキュメントでは、`workflows/comfy_desktop/stable_audio_3_bgm.json` を使った
生成手順とトラブルシューティングを解説します。
初回セットアップ（ComfyUI Desktop導入・モデル配置・ワークフロー読み込み）は
[docs/comfy_stable_audio_setup.md](./comfy_stable_audio_setup.md) を参照してください。

---

## 1. 全体構成

- **実行環境**: ComfyUI Desktop
- **ワークフローファイル**: [workflows/comfy_desktop/stable_audio_3_bgm.json](/home/perso/analysis/BGMgachaLab/workflows/comfy_desktop/stable_audio_3_bgm.json)
- **メインモデル**: `stable_audio_3_medium.safetensors`（`CheckpointLoaderSimple`）
- **テキストエンコーダ**: `t5gemma_b_b_ul2.safetensors`（`type: stable_audio`）
- **プロンプト補助LLM**: `qwen3.5_2b_bf16.safetensors`（`type: stable_diffusion`、`TextGenerate` ノードで使用）
- **サンプラー**: `lcm` / `steps: 8` / `cfg: 1`（LCM系の低ステップ設定）
- **出力**: MP3（`SaveAudioMP3`、`quality: V0`）

処理の流れは大きく2段階です。

1. ユーザーが短い説明文（例: "Tropical house track with marimba..."）を `52:31` に入力
2. `Enable_Reprompt` が `true` の場合、`52:28`（TextGenerate + Qwen3.5）がその短文を
   詳細な音楽プロンプト（ジャンル・楽器・リズム・ムード・BPM・尺）に自動展開してから Stable Audio 3 に渡す

---

## 2. 生成の実行

### 2.1 プロンプトを入力する

ノード `52:31`（`User: short description`）に、生成したいBGMの短い説明を英語で入力します。

例（ワークフロー内のデフォルト値）:
```
Tropical house track with marimba, steel drums, soft synths, smooth bass,
layered percussion, and light piano riffs for sunny chill dance vibes.
BPM: 110. Length: 150 seconds
```

### 2.2 尺を設定する

ノード `52:36`（`Float (Duration)`）で秒数を指定します。デフォルトは `150`。

**重要**: [3. VRAMと尺の制約](#3-vramと尺の制約重要実運用の知見) を必ず確認してから尺を伸ばしてください。

### 2.3 Reprompt（プロンプト自動展開）の有無

ノード `52:35`（`Boolean (Enable_Reprompt)`）:
- `true`: `52:31` の短文を Qwen3.5 が詳細プロンプトに展開してから使う（デフォルト）
- `false`: `52:31` の文章をそのまま Stable Audio 3 に渡す

Reprompt を使う場合、カテゴリ選択ノード `52:43`（`Custom Combo`）で
`Music` / `Instrument` / `SFX` / `One-shot` のいずれかを選び、
対応するシステムプロンプト（`52:49` にJSONで定義済み）が適用されます。

### 2.4 キューに投入する

ComfyUI上でキューを実行し、生成を開始します。
出力は `SaveAudioMP3`（`52:19`）によって `audio/stable_audio_3` プレフィックスでMP3保存されます。

---

## 3. VRAMと尺の制約（重要・実運用の知見）

`tasks/lessons.md`（2026-07-30）に記録された実地の知見です。

### 症状
API経由（`/prompt`）で生成する際、**尺が160〜170秒付近を境に生成が極端に遅くなり**、
ハング（`/system_stats` が500エラー）や完全な接続断（HTTP: 000、プロセスクラッシュ）に至ることがある。

### 原因
`system_stats` の `torch_vram_total` がGPU物理VRAM（24GB）を超える値を示しており、
Stable Audio 3 medium + LCM 8steps での音声潜在サイズがVRAM容量の壁を超えると、
`cudaMallocAsync` がシステムメモリ側にスピルし、極端な速度低下・タイムアウト・クラッシュを引き起こす。
**この劣化は線形ではなく崖状**に起きる。

### 対策（このワークフロー・24GB VRAM構成の場合）
- **尺は160秒以内に抑えるのが安全**の目安（160秒で15〜20秒/曲、170秒で崖）
- 長尺が必要な場合は、事前に短尺から段階的に伸ばして「崖」の位置を確認してから本生成する
- ネガティブプロンプト（`52:7`）の中身自体は速度低下の原因ではない（切り分け済み）

### 運用の学び
- ComfyUIサーバーがクラッシュ/ハングした場合、`/interrupt` や `/queue clear` はAPI応答不能状態では効かない。手動再起動が必要
- 再起動後は `/system_stats` がHTTP 200を返すことを確認してから次のジョブを投げる
- 複数曲をまとめて一度にキュー投入するより、**1曲ずつ「投入→完了確認→次を投入」の逐次方式**の方が安定し、原因切り分けもしやすい

---

## 4. トラブルシューティング

| 症状 | 対処 |
|---|---|
| 生成が極端に遅い / ハングする | 尺を160秒以下に短縮。[3章](#3-vramと尺の制約重要実運用の知見)参照 |
| `/system_stats` が500を返す | VRAM崖の可能性が高い。ComfyUIを手動再起動し、200が返るのを確認してから再実行 |
| HTTP: 000（接続断） | プロセスクラッシュ。Windows側で手動再起動が必要 |
| ノードがモデルを認識しない | ComfyUI起動ログでモデル探索パスを確認し、配置先ディレクトリを見直す |
| プロンプトが期待通り展開されない | `52:43` のカテゴリ選択と `52:49` のシステムプロンプトJSONを確認 |

---

## 5. MusicGenフロー（旧方式）との違い

| | Stable Audio 3 (ComfyUI) | MusicGen（旧方式） |
|---|---|---|
| 実行環境 | ComfyUI Desktop（GUI/ノードベース） | CLI（`uv run bgm-gacha`） |
| モデル | `stable_audio_3_medium` | `facebook/musicgen-stereo-medium` |
| プロンプト展開 | Qwen3.5によるLLM自動展開に対応 | 手書きプロンプトのみ |
| 出力形式 | MP3 | WAV |
| 長尺対応 | VRAM制約あり（160秒目安、崖状に悪化） | 150秒超で自動セグメント分割 |
| 位置づけ | **現行の標準フロー** | 旧フロー（`docs/blog_guide.md`参照） |

詳しいルート比較は [docs/generation_routes.md](/home/perso/analysis/BGMgachaLab/docs/generation_routes.md) も参照してください。
