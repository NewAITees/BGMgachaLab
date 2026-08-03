# Generation Routes

## 概要
このリポジトリには、名前が似ていても中身が違う 3 本の生成ルートがある。

1. `Stable Audio (ComfyUI)` ルート（現行の標準）
2. `MusicGen` ルート（旧方式）
3. `MIDI-LLM` ルート

それぞれ「何を生成するか」が違う。

- `Stable Audio (ComfyUI)`: 音声そのものを生成する（現行の標準フロー）
- `MusicGen`: 音声そのものを生成する（旧方式、CLI）
- `MIDI-LLM`: 演奏データを生成する

## 0. Stable Audio (ComfyUI) ルート（現行の標準）

### 何をするルートか
ComfyUI Desktop上のノードワークフローで、短文プロンプトをLLMが詳細プロンプトに自動展開し、Stable Audio 3 で音声を生成する。

### 主な実装
- [workflows/comfy_desktop/stable_audio_3_bgm.json](/home/perso/analysis/BGMgachaLab/workflows/comfy_desktop/stable_audio_3_bgm.json)

### 使っているモデル
- `stable_audio_3_medium.safetensors`（生成本体）
- `t5gemma_b_b_ul2.safetensors`（テキストエンコーダ）
- `qwen3.5_2b_bf16.safetensors`（プロンプト自動展開用LLM）

### 入出力
- 入力: 短文プロンプト（英語）
- 出力: `mp3`

### 処理の流れ
`短文prompt -> (任意)LLMによる詳細プロンプト展開 -> Stable Audio 3 -> mp3`

### 向いている用途
- 現行の標準フロー。高品質なBGMをGUIベースで作りたい
- プロンプトを詳細に書かずLLMに展開させたい

### 制約
- VRAM崖に注意（24GB環境で尺160秒目安）。詳細は [docs/comfy_stable_audio_guide.md](/home/perso/analysis/BGMgachaLab/docs/comfy_stable_audio_guide.md) を参照

## 1. MusicGen ルート（旧方式）

### 何をするルートか
テキスト prompt から、そのまま聴ける音声を生成する。

### 主な実装
- [scripts/generate_piano_techno_set.py](/home/perso/analysis/BGMgachaLab/scripts/generate_piano_techno_set.py)
- [bgm_gacha_lab/generator.py](/home/perso/analysis/BGMgachaLab/bgm_gacha_lab/generator.py)
- [bgm_gacha_lab/config.py](/home/perso/analysis/BGMgachaLab/bgm_gacha_lab/config.py)

### 使っているモデル
- `facebook/musicgen-stereo-medium`

### 入出力
- 入力: テキスト prompt
- 出力: `wav`

### 処理の流れ
`prompt -> MusicGen -> wav`

### 代表例
- `outputs/piano_techno_set/*.wav`

### 向いている用途
- すぐ聴ける BGM を作りたい
- MIDI ではなく完成音に近いものが欲しい
- 長尺の作業用音源を直接出したい

## 2. MIDI-LLM ルート

### 何をするルートか
テキスト prompt から、まず MIDI を生成し、その後に譜面化や演奏可能性評価を行う。

### 主な実装
- [scripts/run_boogie_batch.py](/home/perso/analysis/BGMgachaLab/scripts/run_boogie_batch.py)
- [third_party/MIDI-LLM/generate_transformers.py](/home/perso/analysis/BGMgachaLab/third_party/MIDI-LLM/generate_transformers.py)
- [bgm_gacha_lab/text_to_midi.py](/home/perso/analysis/BGMgachaLab/bgm_gacha_lab/text_to_midi.py)
- [bgm_gacha_lab/score.py](/home/perso/analysis/BGMgachaLab/bgm_gacha_lab/score.py)
- [bgm_gacha_lab/playability.py](/home/perso/analysis/BGMgachaLab/bgm_gacha_lab/playability.py)

### 使っているモデル
- `slseanwu/MIDI-LLM_Llama-3.2-1B`

### 入出力
- 入力: テキスト prompt
- 出力: `mid`
- 後処理: `musicxml`

### 処理の流れ
`prompt -> MIDI-LLM -> mid -> musicxml`

### 代表例
- `outputs/boogie_jazzy_rock_variants_120/.../*.mid`
- `outputs/boogie_jazzy_rock_variants_120/.../*.musicxml`

### 向いている用途
- 演奏データとして編集したい
- 譜面にしたい
- 人が弾けるかを評価したい
- 生成後に別音源で鳴らしたい

## 3. どちらを使うべきか

### そのまま聴く音が欲しい場合（新規制作）
`Stable Audio (ComfyUI)` を使う。現行の標準フロー。

理由:
- 音質・プロンプト解釈の面で現行の第一候補
- LLMによるプロンプト自動展開が使える
- GUIベースでパラメータ調整がしやすい

### そのまま聴く音が欲しい場合（旧方式・CLIバッチ）
`MusicGen` を使う。

理由:
- 最初から `wav` が出る
- 音色込みで生成される
- `piano_techno_set` と同じ流れで扱える

### MIDI や譜面を扱いたい場合
`MIDI-LLM` を使う。

理由:
- `mid` を直接編集できる
- `musicxml` 化できる
- 演奏可能性評価と相性が良い

## 4. 今回の混乱ポイント
`piano_techno_set` は `mp3` ではなく `wav` 出力で、MusicGen ルートを使っている。

一方で、`boogie_jazzy_rock` や `easy_listening` のバッチは MIDI-LLM ルートなので、最初に出るのは音声ではなく `mid`。

見た目はどちらも「prompt から音楽を作る」処理だが、生成対象が違うので出力形式も違う。
