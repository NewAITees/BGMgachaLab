# オープンソースAIで作曲しよう：MusicGenを使ったBGM自動生成 完全ガイド

## はじめに

「AIで音楽を作れる」と聞いたことはありますか？実は、Metaが公開しているオープンソースの音楽生成AI「MusicGen」を使えば、誰でも無料でオリジナルのBGMを生成できます。

このガイドでは、プログラミング初心者でも再現できるように、環境構築からBGM生成まで一から丁寧に解説します。

### このガイドで作れるもの

- ローファイ・チルホップ風のBGM
- カフェミュージック風のリラックス曲
- 作業用・勉強用の長時間BGM（10分以上も可能）

### 必要なもの

- パソコン（Windows/Mac/Linux）
- インターネット接続
- 約10GBの空きストレージ
- （推奨）NVIDIA GPUを搭載したPC

---

## 1. MusicGenとは何か

### Metaが開発したオープンソースの音楽生成AI

MusicGenは、Meta（旧Facebook）の研究チームが開発した**テキストから音楽を生成するAIモデル**です。

- **開発元**: Meta AI（facebookresearch）
- **ライブラリ名**: Audiocraft
- **モデル**: facebook/musicgen-stereo-medium
- **公開場所**: Hugging Face（誰でも無料でダウンロード可能）

### なぜMusicGenがすごいのか

1. **完全オープンソース**: 誰でも無料で使える
2. **高品質**: プロンプト（指示文）を入れるだけで、それらしい音楽が生成される
3. **ローカル実行**: クラウドサービスに依存せず、自分のPCで動く
4. **カスタマイズ可能**: 温度パラメータなどで生成のバリエーションを調整できる

---

## 2. 環境要件（これが一番重要！）

### Python バージョンの制限

**絶対に守ってください：Python 3.10〜3.12 を使用すること**

```
Python 3.10 ✅ 対応
Python 3.11 ✅ 対応
Python 3.12 ✅ 対応
Python 3.13 ❌ 非対応（PyTorchが未対応のため動作しません）
Python 3.9以下 ❌ 非対応
```

**なぜ3.13がダメなのか？**

MusicGenが依存しているPyTorchは、新しいPythonバージョンへの対応に時間がかかります。2024年末時点でPython 3.13はPyTorchが公式サポートしていないため、インストール自体が失敗します。

### ffmpegのインストール（必須）

Audiocraftライブラリは内部でffmpegを使用します。これがないと音声の読み書きでエラーになります。

#### Windows

1. [ffmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
2. または、Chocolateyを使用：
```powershell
choco install ffmpeg
```
3. または、Scoopを使用：
```powershell
scoop install ffmpeg
```

インストール確認：
```powershell
ffmpeg -version
```

#### macOS

Homebrewを使用：
```bash
brew install ffmpeg
```

インストール確認：
```bash
ffmpeg -version
```

#### Linux（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install ffmpeg
```

インストール確認：
```bash
ffmpeg -version
```

### ストレージ要件

- **MusicGenモデル**: 約3GB（初回実行時に自動ダウンロード）
- **PyTorch + 依存ライブラリ**: 約5GB
- **生成した音声ファイル**: 1分あたり約4MB（32kHz ステレオWAV）

**合計：最低10GBの空き容量を確保してください**

### GPUについて

#### GPU推奨（NVIDIA CUDA対応）

- 生成速度が10倍以上速い
- 6GB以上のVRAMがあると快適
- GeForce RTX 3060以上を推奨

#### CPUでも動作可能

- 動作はするが非常に遅い（30秒の曲に5〜10分かかることも）
- メモリ16GB以上を推奨
- 試しに使ってみる分には問題なし

---

## 3. 環境構築（ステップバイステップ）

### ステップ1：Pythonのインストール

#### すでにPythonが入っている場合

バージョンを確認：
```bash
python --version
```

3.13と表示された場合は、3.12をインストールする必要があります。

#### pyenvを使う方法（推奨）

pyenvを使うと複数のPythonバージョンを簡単に管理できます。

**macOS/Linux:**
```bash
# pyenvのインストール
curl https://pyenv.run | bash

# シェル設定に追加（bashの場合）
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Python 3.12のインストール
pyenv install 3.12.7
pyenv global 3.12.7

# 確認
python --version  # Python 3.12.7 と表示されればOK
```

**Windows:**
```powershell
# pyenv-winのインストール（PowerShell管理者モード）
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"

# 新しいPowerShellを開いて
pyenv install 3.12.7
pyenv global 3.12.7

# 確認
python --version
```

### ステップ2：uvのインストール（パッケージマネージャー）

uvはPythonのパッケージ管理ツールで、pipより高速で信頼性が高いです。

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

インストール確認：
```bash
uv --version
```

### ステップ3：プロジェクトの取得

#### GitHubからクローンする場合

```bash
git clone https://github.com/YOUR_USERNAME/BGMgachaLab.git
cd BGMgachaLab
```

#### 手動でファイルを配置する場合

1. GitHubからZIPをダウンロード
2. 解凍して任意のフォルダに配置
3. ターミナルでそのフォルダに移動

### ステップ4：依存パッケージのインストール

```bash
# プロジェクトディレクトリで実行
uv sync
```

このコマンドで以下が自動的にインストールされます：
- PyTorch（GPU/CPU自動判定）
- Audiocraft（MusicGen本体）
- Typer（CLI）
- Pydantic（設定管理）
- soundfile（WAV書き出し）

**注意：初回は5〜10分かかることがあります**

インストールに失敗した場合は、以下を試してください：

```bash
# キャッシュをクリアして再実行
uv cache clean
uv sync
```

### ステップ5：動作確認

```bash
uv run bgm-gacha --help
```

以下のようなヘルプが表示されればセットアップ完了です：

```
Usage: bgm-gacha [OPTIONS] COMMAND [ARGS]...

Generate lofi/chill BGM batches via MusicGen

Options:
  --help  Show this message and exit.
...
```

---

## 4. 初めてのBGM生成

### モデルの自動ダウンロード

初回実行時、MusicGenモデル（約3GB）が自動的にダウンロードされます。
これには数分〜十数分かかります（回線速度による）。

### 最初の30秒サンプルを生成

```bash
uv run bgm-gacha --preset night --num-samples 1 --duration 30
```

#### このコマンドの意味

- `--preset night`: 夜向けローファイのプリセットを使用
- `--num-samples 1`: 1曲だけ生成
- `--duration 30`: 30秒の長さ

#### 実行時の表示

```
Using preset 'night' with prompt: lofi chill hip hop beat, warm rhodes piano...
Output directory: outputs/night
Loading model 'facebook/musicgen-stereo-medium' on cuda ...
Starting generation: samples=1 batch_size=1 batches=1 prompt='lofi chill hip hop...'
Batch 1/1: generating 1 clips ...
  saved -> outputs/night/lofi_000.wav
Generation complete.
Generated files:
 - outputs/night/lofi_000.wav
```

### 生成されたファイルの確認

`outputs/night/lofi_000.wav` というファイルが生成されます。
お好みの音楽プレイヤーで再生してみてください。

---

## 5. プリセットの解説

BGMgachaLabには3つのプリセットが用意されています。

### night（夜向けローファイ）

```
lofi chill hip hop beat, warm rhodes piano, soft dusty drums,
vinyl crackle, mellow, no vocals, 75 bpm, smooth loop, night mood
```

落ち着いた夜の作業に最適。温かみのあるローズピアノが特徴。

### rainy（雨の日向け）

```
lofi chill beat for a rainy day, soft piano, gentle rain ambience,
vinyl noise, calm, no vocals, 72 bpm, background music
```

雨音のアンビエンスが含まれる静かなビート。

### cafe（カフェ風）

```
cozy coffee shop lofi, jazzy chords, soft drums, light crowd ambience,
tape hiss, 80 bpm, relaxed background
```

ジャズっぽいコードと軽いカフェの雰囲気。

---

## 6. パラメータの調整

### 温度（temperature）

生成のランダム性を制御します。

```bash
# 安定した生成（テンプレートに近い）
uv run bgm-gacha --preset cafe --temperature 0.8

# バリエーション豊かな生成
uv run bgm-gacha --preset cafe --temperature 1.2
```

- **0.8〜0.9**: 安定した、予測しやすい結果
- **1.0**: デフォルト
- **1.1〜1.3**: バリエーションが増える、実験的

### バッチサイズ（batch-size）

一度に生成するサンプル数です。

```bash
# 1曲ずつ生成（VRAM少なめ向け）
uv run bgm-gacha --preset night --num-samples 4 --batch-size 1

# 2曲ずつ生成（VRAM 8GB以上）
uv run bgm-gacha --preset night --num-samples 4 --batch-size 2
```

**注意**: バッチサイズを大きくするとVRAM使用量が増えます。
メモリ不足エラーが出たら1に戻してください。

### プロンプトの上書き

```bash
uv run bgm-gacha --preset cafe --prompt "jazzy piano techno, 120 bpm, energetic"
```

プリセットのプロンプトを完全に上書きします。

### ファイル名の指定

```bash
uv run bgm-gacha --preset night --tag "my_first_bgm"
```

`outputs/night/my_first_bgm_000.wav` として保存されます。

日本語やスペースは自動的に安全な文字に変換されます：
- "Midnight Keys" → `midnight_keys`
- "夜のBGM" → `_bgm`（日本語はアンダースコアに）

---

## 7. 長尺BGMの生成

### 10分の曲を生成する

```bash
uv run bgm-gacha --preset night --duration 600 --num-samples 1
```

`--duration 600` は600秒 = 10分です。

### 自動セグメント分割

150秒を超える長さを指定すると、自動的に複数のセグメントに分割して生成されます。
これは32ビットインデックスの制限によるRuntimeErrorを回避するためです。

```
Duration 600.0s exceeds safe limit; generating in 4 segments of ~150.0s
    segment 1/4 complete
    segment 2/4 complete
    segment 3/4 complete
    segment 4/4 complete
```

### セグメント長のカスタマイズ

```bash
# 120秒ごとに分割（よりスムーズなつなぎ目）
uv run bgm-gacha --preset night --duration 600 --max-segment-duration 120
```

---

## 8. 出力ファイルの管理

### デフォルトの出力先

- `outputs/night/` - nightプリセット
- `outputs/rainy/` - rainyプリセット
- `outputs/cafe/` - cafeプリセット

### カスタム出力先

```bash
uv run bgm-gacha --preset night --output-dir outputs/my_project
```

### ファイル形式

- **形式**: WAV（非圧縮）
- **サンプルレート**: 32kHz
- **チャンネル**: ステレオ（2ch）
- **ビット深度**: 32bit float

動画や配信で使う場合は、44.1kHzや48kHzにリサンプリングが必要な場合があります。
ffmpegで変換できます：

```bash
ffmpeg -i input.wav -ar 44100 output.wav
```

---

## 9. プロンプト設計のコツ

### 効果的なプロンプトの書き方

MusicGenは英語のプロンプトを理解します。以下の要素を含めると良い結果が得られます：

1. **ジャンル/スタイル**: lofi, techno, jazz, ambient
2. **楽器**: piano, synth, drums, bass
3. **テンポ**: 80 bpm, slow, fast
4. **ムード**: chill, energetic, melancholic
5. **その他の特徴**: vinyl crackle, no vocals

### 良いプロンプトの例

```
soft piano lofi beat, gentle rhodes chords, dusty drums, vinyl noise,
75 bpm, relaxed, no vocals, late night study music
```

```
energetic techno, pulsing synth bass, crisp hi-hats, 128 bpm,
driving rhythm, club atmosphere
```

### 避けるべきこと

- 日本語のプロンプト（英語で書く）
- 曖昧な表現（「いい感じの曲」など）
- 相反する指示（「静かで激しい」など）

---

## 10. トラブルシューティング

### よくあるエラーと解決策

#### 「No module named 'torch'」

PyTorchがインストールされていません。

```bash
uv sync
```

を再実行してください。

#### 「CUDA out of memory」

GPUのVRAMが不足しています。

**解決策:**
1. `--batch-size 1` にする
2. `--duration` を短くする
3. 他のGPUを使うアプリを閉じる
4. `--device cpu` でCPUモードにする（遅いが確実）

```bash
uv run bgm-gacha --preset night --batch-size 1 --device cpu
```

#### 「RuntimeError: index out of range」

長尺生成時のインデックス上限エラーです。
`--max-segment-duration 120` などを指定してセグメント分割してください。

```bash
uv run bgm-gacha --preset night --duration 600 --max-segment-duration 120
```

#### 「ffmpeg not found」

ffmpegがインストールされていません。
「2. 環境要件」のセクションを参照してインストールしてください。

#### 「Connection error」（モデルダウンロード時）

インターネット接続を確認してください。
プロキシ環境の場合は環境変数の設定が必要な場合があります。

#### Python 3.13でインストールできない

Python 3.12以下にダウングレードしてください。
pyenvを使うと簡単です：

```bash
pyenv install 3.12.7
pyenv global 3.12.7
```

---

## 11. 実践的な使用例

### 例1: 作業用BGMセットの作成

5曲×30秒のサンプルセットを作成：

```bash
uv run bgm-gacha --preset cafe --num-samples 5 --duration 30 --tag work_bgm
```

### 例2: テンポ違いのバリエーション

同じムードでテンポを変えて比較：

```bash
# 遅め
uv run bgm-gacha --preset night --prompt "lofi piano, 70 bpm, sleepy" --tag slow

# 速め
uv run bgm-gacha --preset night --prompt "lofi piano, 90 bpm, upbeat" --tag fast
```

### 例3: 10分の長尺BGM

```bash
uv run bgm-gacha --preset cafe --duration 600 --temperature 1.0 \
  --prompt "jazzy piano lofi, soft drums, 80 bpm, study music" \
  --tag study_session
```

### 例4: 複数ジャンルの一括生成

```bash
# ピアノテクノ
uv run bgm-gacha --preset night --duration 300 \
  --prompt "piano techno, 120 bpm, driving" --tag piano_techno

# アンビエント
uv run bgm-gacha --preset cafe --duration 300 \
  --prompt "ambient piano, slow pads, ethereal" --tag ambient_piano

# ジャズローファイ
uv run bgm-gacha --preset cafe --duration 300 \
  --prompt "jazz lofi, walking bass, brushed drums" --tag jazz_lofi
```

---

## 12. ライセンスと利用規約

### MusicGenのライセンス

MusicGenはMeta（Facebook）がオープンソースで公開していますが、商用利用には注意が必要です。

- **モデル自体**: CC-BY-NC 4.0（非商用）
- **学習データ**: 様々な音楽データで学習されている

**商用利用を検討している場合:**
1. Metaの公式ライセンス条項を確認
2. 生成物の利用範囲を確認
3. 必要に応じて法的アドバイスを受ける

### 個人利用・学習目的

- YouTubeの非収益化動画 → 基本的にOK
- 個人のポッドキャスト → 基本的にOK
- 学習・研究目的 → OK

### 商用利用

- 有料コンテンツでの使用 → ライセンス確認が必要
- 商用音楽ライブラリ → 注意が必要

**免責事項**: このガイドは法的アドバイスではありません。
商用利用の際は必ず公式ライセンスを確認してください。

---

## 13. 次のステップ

### もっと試してみる

1. **プロンプトを変えて実験**: 楽器やムードを変えてどう変わるか試す
2. **温度を調整**: 0.8〜1.3の範囲で好みを探す
3. **長尺に挑戦**: 5分、10分の曲を生成
4. **DAWでの加工**: 生成した曲をフェードイン/アウトやEQで仕上げる

### 参考リンク

- [Audiocraft GitHub](https://github.com/facebookresearch/audiocraft)
- [MusicGen on Hugging Face](https://huggingface.co/facebook/musicgen-stereo-medium)
- [uv公式ドキュメント](https://docs.astral.sh/uv/)

---

## まとめ

このガイドでは、MusicGenを使ったBGM自動生成の環境構築から実際の生成までを解説しました。

**重要なポイント:**

1. **Python 3.10〜3.12を使う**（3.13は非対応）
2. **ffmpegを必ずインストール**
3. **初回はモデルダウンロードで時間がかかる**
4. **GPUがあると快適、なくても動く**
5. **長尺は自動セグメント分割される**

オープンソースのAIで音楽が作れる時代です。ぜひ試してみてください！

---

*このドキュメントはBGMgachaLabプロジェクトの一部として作成されました。*
