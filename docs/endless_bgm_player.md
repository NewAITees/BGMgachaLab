# Endless BGM Player

ComfyUI（Stable Audio 3）を裏で回し続け、ジャンル円環表に沿って少しずつ変化する
プロンプトで120秒のBGMを次々に生成し、クロスフェードで途切れなく再生し続ける
ローカルWebアプリ。

実体: [apps/endless_bgm_player/](/home/perso/analysis/BGMgachaLab/apps/endless_bgm_player)

## 前提

- ComfyUI Desktopが起動しており、`workflows/comfy_desktop/stable_audio_3_bgm.json` が
  読み込み可能な状態であること（モデル配置等は [docs/comfy_stable_audio_setup.md](./comfy_stable_audio_setup.md) 参照）
- 本アプリはComfyUIと**同じマシン**で実行する前提（HTTP API `http://127.0.0.1:8188` に直接アクセス）

## 起動方法

```bash
uv run python apps/endless_bgm_player/main.py
```

ブラウザで `http://127.0.0.1:58317/` を開き、「START」を押すと生成・再生が始まる。

環境変数で調整可能:

| 変数 | 内容 | デフォルト |
|---|---|---|
| `COMFY_BASE_URL` | ComfyUIのbase URL | `http://127.0.0.1:8188` |
| `ENDLESS_BGM_PORT` | 本アプリの待ち受けポート | `58317`（一般的に使われないポート） |

## 仕組み

1. **ジャンル円環表**（`genre_circle.py`）: Ambient Drift → Lofi Chillhop → Jazzy Cafe →
   Bossa Downtempo → Deep Chill House → Chill Techno → Synth Dreamscape → Acoustic Chill
   → (Ambient Drift に戻る) の8ジャンルを円環状に配置
2. 円環上の位置（0〜8の浮動小数）を**毎曲少しずつ前進**させ（デフォルト歩幅0.25、±30%のジッター）、
   隣接ジャンルの楽器・ムード・BPMを線形補間してプロンプトを合成
3. 同じ位置に戻ってきても毎回同じ文にならないよう、ジャンルごとの**ランダム語彙プール**から
   1〜3語を抽選して混ぜ込む
4. `tasks/lessons.md` の運用知見に従い、ComfyUIへは**1曲ずつ逐次投入**（並列投入はしない）。
   尺は120秒（VRAM崖の目安である160秒を十分に下回る安全域）
5. 生成（約20秒）は再生（120秒）よりずっと速いため、常に1〜2曲分のバッファを先読み生成
6. フロントエンドはWeb Audio APIで曲を厳密なタイミングでスケジュールし、
   **各曲の最後の15秒でクロスフェード**（前の曲がフェードアウトしつつ次の曲が重なって始まる）
7. 画面には「時計盤」のような円環UIがあり、**現在再生中のジャンルが常に固定位置（右側/3時の位置）に来るよう盤自体が回転**する演出

## 制約・注意点

- ComfyUIサーバーがクラッシュ/ハングした場合は手動再起動が必要（詳細は
  [docs/comfy_stable_audio_guide.md](./comfy_stable_audio_guide.md) の「VRAMと尺の制約」参照）
- ジャンル円環の内容（楽器・ムード・BPM・語彙プール）は `apps/endless_bgm_player/genre_circle.py`
  を編集することで自由にカスタマイズできる
