# Generation Routes

## 概要
このリポジトリには、名前が似ていても中身が違う 2 本の生成ルートがある。

1. `MusicGen` ルート
2. `MIDI-LLM` ルート

両者は「何を生成するか」が違う。

- `MusicGen`: 音声そのものを生成する
- `MIDI-LLM`: 演奏データを生成する

## 1. MusicGen ルート

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

### そのまま聴く音が欲しい場合
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
