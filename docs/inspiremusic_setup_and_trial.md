# InspireMusic Setup And Trial

## 目的
`InspireMusic` を既存の `MusicGen` 比較対象として評価するための最小手順をまとめる。

このメモの前提:
- 既存 repo の Python 環境はできるだけ汚さない
- まずは `ComfyUI` 連携ではなく、単体 CLI で音を確認する
- 最初の評価は `30秒` に限定する

## 位置づけ

`InspireMusic` は `MusicGen` より新しいローカル実行候補で、特に次の点が今回の用途に合う。

- long-form music generation
- text-to-music
- music continuation
- 48kHz stereo モデルあり

確認済みの注意点:
- 現状は `English text prompts` 前提
- 依存はやや重い
- まずは `fast mode` から始める方が安全

Primary references:
- GitHub: https://github.com/FunAudioLLM/FunMusic
- Hugging Face: https://huggingface.co/FunAudioLLM/InspireMusic-1.5B-Long
- Paper: https://arxiv.org/abs/2503.00084

## 推奨モデル

最初の試験では次のモデルだけを見る。

- `InspireMusic-1.5B-Long`

理由:
- `48kHz`
- `several minutes` の long-form 対応
- 今回の配信BGM評価に一番近い

補助候補:
- `InspireMusic-1.5B`
- `InspireMusic-Base`

## 導入方針

### 推奨
既存 repo とは別ディレクトリ、別環境で試す。

例:
- Windows 側の `ComfyUI` 近辺とは分離
- WSL 上の別作業ディレクトリで検証

理由:
- 依存が重い
- `flash-attn` や CUDA 条件の切り分けが必要
- 既存 `MusicGen` 環境を壊したくない

## 公式要件

Hugging Face model card にある要件:

- `Python>=3.8`
- `PyTorch>=2.0.1`
- `flash-attn==2.6.2/2.6.3`
- `CUDA>=11.2`
- `sox` or `ffmpeg`

## 導入手順の最小形

### 1. clone

```bash
git clone --recursive https://github.com/FunAudioLLM/InspireMusic.git
cd InspireMusic
git submodule update --recursive
```

### 2. 専用環境

公式は conda 前提。

```bash
conda create -n inspiremusic python=3.8
conda activate inspiremusic
conda install -y -c conda-forge pynini==2.1.5
pip install -r requirements.txt
pip install flash-attn --no-build-isolation
python setup.py install
```

### 3. 追加ツール

```bash
sudo apt-get install ffmpeg
sudo apt-get install sox libsox-dev
```

### 4. モデル取得

```bash
mkdir -p pretrained_models
git clone https://huggingface.co/FunAudioLLM/InspireMusic-1.5B-Long pretrained_models/InspireMusic-1.5B-Long
```

補足:
- `git lfs` が必要
- まずは `InspireMusic-1.5B-Long` のみ取得する

## 最小試験プラン

### Phase 1: fast mode, 30秒, 1曲

目的:
- とにかく動作確認
- CUDA / 重み / 依存関係 / 出力形式を確認

コマンド例:

```bash
python -m inspiremusic.cli.inference \
  --task text-to-music \
  -m "InspireMusic-1.5B-Long" \
  -g 0 \
  -t "Streaming background music, easy-listening instrumental jazz, muted brushed drums, warm upright bass, rounded piano tone, gentle intro, stable middle section, natural ending, soft top end, low-fatigue mix." \
  -c intro \
  -s 0.0 \
  -e 30.0 \
  -r "exp/inspiremusic" \
  -o output \
  -f wav \
  --fast True
```

### Phase 2: fast mode, 30秒, 3曲

目的:
- ばらつき確認
- `MusicGen` より構成が自然かを比較

評価観点:
- 冒頭が唐突でないか
- 高音が耳に刺さらないか
- 30秒でも曲として流れがあるか
- 後半にノイズが出ないか

### Phase 3: 通常モード, 30秒, 3曲

目的:
- `flow matching` を含む通常生成の質確認

### Phase 4: continuation

目的:
- 30秒の良い個体を伸ばしたとき、自然に繋がるか確認

## 30秒試験用プロンプト

すべて英語で使う。

### Prompt 1: jazz piano trio

`Streaming background music, easy-listening instrumental jazz piano trio, warm upright bass, muted brushed drums, rounded piano tone, start with a simple piano motif, gradually bring in a gentle groove, keep a stable middle section for talking-friendly background use, finish with a soft resolved ending, low-fatigue mix, soft top end, controlled room sound.`

### Prompt 2: techno ambient

`Streaming background music, easy-listening ambient techno, warm pads, soft pulse, low-mid synth bed, gradual development, stable central flow for talking-friendly background use, small late variation, smooth natural ending, warm low mids, dry-to-moderate ambience, soft top end, low-fatigue mix.`

### Prompt 3: modern classical piano

`Streaming background music, easy-listening modern classical piano, grounded chamber atmosphere, sparse piano figures, soft repeating patterns, restrained harmony, gradual development, stable middle section, quiet natural cadence, controlled room sound, soft top end, refined low-fatigue mix.`

## 今回の評価基準

`MusicGen` より良いと判断しやすい条件:

- 導入が自然
- 終わりが自然
- 後半で耳障りノイズが出にくい
- 30秒時点で構成感がある
- 高音の暴れが少ない

## 今回はまだやらないこと

- `ComfyUI` ノード化
- 3分以上の長尺一括生成
- 既存 repo への直接導入
- 既存 `MusicGen` スクリプトとの統合

## 次の実務手順

1. 別環境へ `InspireMusic` を導入
2. `fast mode` で 30秒 x 3本
3. 良ければ通常モード 30秒 x 3本
4. 良い個体だけ `continuation` で延長
