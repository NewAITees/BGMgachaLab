# Endless BGM Player

ComfyUI（Stable Audio 3）を裏で回し続け、ジャンル円環表に沿って少しずつ変化する
プロンプトで120秒のBGMを次々に生成し、クロスフェードで途切れなく再生し続ける
ローカルWebアプリ。

実体: [apps/endless_bgm_player/](/home/perso/analysis/BGMgachaLab/apps/endless_bgm_player)

## 前提

- ComfyUI Desktopが起動しており、`workflows/comfy_desktop/stable_audio_3_bgm.json` が
  読み込み可能な状態であること（モデル配置等は [docs/comfy_stable_audio_setup.md](./comfy_stable_audio_setup.md) 参照）
- 本アプリはComfyUIと**同じマシン**で実行する前提（HTTP API `http://127.0.0.1:18231` に直接アクセス）
- **注意**: このマシンのComfyUIはデフォルトポート `8188` ではなく `18231` で起動している（詳細は [AGENTS.md](/home/perso/analysis/BGMgachaLab/AGENTS.md)）

## 起動方法

```bash
uv run python apps/endless_bgm_player/main.py
```

ブラウザで `http://127.0.0.1:58317/` を開き、「START」を押すと生成・再生が始まる。

環境変数で調整可能:

| 変数 | 内容 | デフォルト |
|---|---|---|
| `COMFY_BASE_URL` | ComfyUIのbase URL | `http://127.0.0.1:18231` |
| `ENDLESS_BGM_PORT` | 本アプリの待ち受けポート | `58317`（一般的に使われないポート） |

## 仕組み

1. **ジャンル円環表**（`genres.json`）: Ambient Drift → Lofi Chillhop → Jazzy Cafe →
   Bossa Downtempo → Deep Chill House → Chill Techno → Nu Disco Groove → Synth Dreamscape →
   Acoustic Chill → Piano Nocturne → (Ambient Drift に戻る) の10ジャンルを円環状に配置
   （BPMは全ジャンル70以上）
2. 円環上の位置（0〜len(GENRES)の浮動小数）を**毎曲少しずつ前進**させ（デフォルト歩幅0.25、±30%のジッター）、
   隣接ジャンルの楽器・ムード・BPMを線形補間してプロンプトを合成
3. 同じ位置に戻ってきても毎回同じ文にならないよう、ジャンルごとの**ランダム語彙プール**から
   1〜3語を抽選して混ぜ込む
4. `tasks/lessons.md` の運用知見に従い、ComfyUIへは**1曲ずつ逐次投入**（並列投入はしない）。
   尺は120秒（VRAM崖の目安である160秒を十分に下回る安全域）
5. 生成（約20秒）は再生（120秒）よりずっと速いため、常に1〜2曲分のバッファを先読み生成
6. フロントエンドはWeb Audio APIで曲を厳密なタイミングでスケジュールし、
   **各曲の最後の15秒でクロスフェード**（前の曲がフェードアウトしつつ次の曲が重なって始まる）
7. 画面には「時計盤」のような円環UIがあり、**現在再生中のジャンルが常に固定位置（右側/3時の位置）に来るよう盤自体が回転**する演出。各ラベルの文字もその角度に沿って傾く
8. 生成したプロンプトから曲タイトルを合成し（例: `Ambient Drift — Muffled Kick`）、
   再生中の画面表示とファイル名（`outputs/endless_bgm_player/`配下）の両方に使う
9. SKIPボタンで再生中の曲を即座にフェードアウトして次の曲へ進める。STOPは生成・再生の両方を即時停止する

## 自由入力からのジャンル解釈（画面下部の「ジャンル追加」ボックス）

「ペルソナ風」「Max Cooperっぽい」のような自由なテキストを入力して「追加」を押すと、
ローカルのOllama（`http://127.0.0.1:11436`、モデル: `gemma4:e4b`）がそのテキストを
`instruments` / `mood` / `bpm_range` / `extra_vocab` を持つジャンル定義へ解釈し、
`POST /api/genres/inject` が呼ばれた時点で**即座に円環へ挿入**する（実体は
`genre_interpreter.py` と `genre_circle.insert_genre()`）。

- 実在の作曲家/アーティスト名を入力した場合も、本人の楽曲を模倣するのではなく
  「一般的な音楽的特徴（楽器編成・雰囲気・テンポ）」として解釈させている
- BPMは70〜190の範囲にクランプされる
- 挿入位置は**現在の再生位置から円環上で最も遠い場所**に自動で決まる
- ジャンル数の上限は**12個**（`MAX_GENRES`）。上限に達した状態でさらに追加すると、
  円環は拡張せず**「現在位置から最も遠く、かつ最も古く追加された」ジャンルと入れ替える**。
  ただし**まだ一度も実生成に使われていない(＝まだ再生されていない)ジャンルは入れ替え対象から除外**され、
  必ず一度は再生の機会を得られる
- 解釈結果のJSONは `apps/endless_bgm_player/pending_genres/` にも書き込まれるが、これは
  **アプリが読み込むことのないアーカイブ（記録）**。円環からジャンルが入れ替えで外れても
  ファイルは消えないので、定義を見返したり再利用したりする際の記録として残る
- 反映後に円環UIへ表示するには、画面の「⟳ 更新」ボタンを押す（`/api/genres`を再取得して
  円環だけを再描画する。ブラウザ全体のリロードは不要）

## 音量スライダー

START/SKIP/STOPボタンの下に音量スライダー（0〜100%、デフォルト80%）がある。
Web Audioの`masterGain`ノード（全トラックの個別gainノード → masterGain → destination の順に接続）
で一括制御しており、各曲のクロスフェード用エンベロープとは独立して機能する。

## BPM指定スライダー

画面上部のBPMスライダー（70〜190）を有効にすると、以降の生成はジャンル本来のBPMではなく
**スライダーの値を中心に上下に揺らいだBPM**（`random.gauss(target, 10)`を70〜190にクランプ）を使う。
ジャンルの楽器・ムード・語彙はそのまま円環由来のものを使う。無効にすると元のジャンル補間ベースのBPMに戻る。

設定値は `apps/endless_bgm_player/bpm_state.json` に永続化され、アプリ再起動後も復元される。
ブラウザ側もページ読み込み時に `GET /api/bpm` で現在値を取得し、チェックボックス/スライダーへ反映する。

## 制約・注意点

- ComfyUIサーバーがクラッシュ/ハングした場合は手動再起動が必要（詳細は
  [docs/comfy_stable_audio_guide.md](./comfy_stable_audio_guide.md) の「VRAMと尺の制約」参照）
- ジャンル円環の内容（楽器・ムード・BPM・語彙プール）は `apps/endless_bgm_player/genres.json`
  を編集することで自由にカスタマイズできる
- ジャンル数が変わった場合、開いたままのブラウザには自動反映されない。画面の「⟳ 更新」ボタンを
  押すか、ブラウザをリロードすること
