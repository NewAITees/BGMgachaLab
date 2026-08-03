# AGENTS.md

## ComfyUI 接続情報（重要）

このマシン（ホスト名: `DESKTOP-FN1SN9S`）で動作しているComfyUIは、デフォルトポートの `8188` ではなく、
**`http://127.0.0.1:18231`** で起動している。

ComfyUI連携のツール・スクリプト・アプリを書く/実行するときは、必ずこのポートを使うこと。
`8188` を決め打ちで試したり、他プロジェクト（例: `ComfyUI_playground` は `15434`）のポート設定を
流用したりしないこと。それらは別のComfyUIインスタンス、または別の起動設定を指している可能性がある。

疎通確認:
```bash
curl http://127.0.0.1:18231/system_stats
```

`apps/endless_bgm_player/main.py` は環境変数 `COMFY_BASE_URL` のデフォルト値をこのポートにしている。
