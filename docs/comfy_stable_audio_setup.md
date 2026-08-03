# ComfyUI + Stable Audio 3 セットアップ（初回のみ）

このドキュメントは [docs/comfy_stable_audio_guide.md](./comfy_stable_audio_guide.md) の使い方から
セットアップ手順を切り出したものです。**新しい環境からゼロで構築する場合のみ**参照してください。

> このプロジェクトの実行環境（Windows/RTX 4090）では既にセットアップ済みです（`tasks/lessons.md` 2026-07-30 の実地運用記録を参照）。同一環境で作業する場合は本ドキュメントを読む必要はありません。

---

## 1. ComfyUI Desktop の導入

1. ComfyUI Desktop をインストールする（Windows/RTX 4090 環境での運用実績あり）
2. 起動後、モデル配置先（`models/checkpoints/`、`models/text_encoders/` 等、環境依存）を確認する

## 2. 必要モデルの配置

| モデル | 用途 | 配置先の目安 |
|---|---|---|
| `stable_audio_3_medium.safetensors` | メイン生成モデル | `models/checkpoints/` |
| `t5gemma_b_b_ul2.safetensors` | Stable Audio用テキストエンコーダ | `models/text_encoders/` |
| `qwen3.5_2b_bf16.safetensors` | プロンプト自動展開用LLM | `models/text_encoders/` または `models/llm/`（環境依存） |

**注意**: 実際の配置ディレクトリ名はComfyUIのバージョンとノードパック構成によって変わります。
ノードがモデルを認識しない場合は、ComfyUI起動ログで探索パスを確認してください。

## 3. ワークフローの読み込み

1. ComfyUI Desktop を起動
2. `workflows/comfy_desktop/stable_audio_3_bgm.json` を開く（ドラッグ&ドロップ、またはメニューから読み込み）
3. 各ノードの `ckpt_name` / `clip_name` が実際に配置したファイル名と一致しているか確認

セットアップが終わったら [docs/comfy_stable_audio_guide.md](./comfy_stable_audio_guide.md) の「生成の実行」に進んでください。
