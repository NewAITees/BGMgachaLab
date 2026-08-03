"""Endless BGM Player - ComfyUI(Stable Audio 3)で終わらないBGMを生成し続けるアプリ。

起動:
    uv run python apps/endless_bgm_player/main.py

環境変数:
    COMFY_BASE_URL   ComfyUI の base URL (デフォルト: http://127.0.0.1:8188)
    ENDLESS_BGM_PORT このアプリ自体が待ち受けるポート (デフォルト: 58317)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from comfy_client import ComfyClient
from genre_circle import GENRES, advance_position, build_prompt, insert_pending_genres, mark_genre_used

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("endless_bgm_player")

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR.parents[1] / "outputs" / "endless_bgm_player"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFY_BASE_URL = os.environ.get("COMFY_BASE_URL", "http://127.0.0.1:18231")
PORT = int(os.environ.get("ENDLESS_BGM_PORT", "58317"))

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "track"


DURATION_SECONDS = 120
BUFFER_TARGET = 2  # 先読みは最大2曲。生成(約20秒)は再生(120秒)より十分速いので、これで途切れない
STEP = 0.25
JITTER = 0.3

class AppState:
    def __init__(self) -> None:
        self.running = asyncio.Event()
        self.position: float = 0.0
        # 生成済みだがまだクライアントが再生開始していない曲。
        # 新規接続したクライアントにはまずこのリストを送ってから配信に加える。
        self.pending_tracks: list[dict[str, Any]] = []
        self.websockets: set[WebSocket] = set()
        self.comfy_client: ComfyClient | None = None
        self.generation_task: asyncio.Task[None] | None = None


state = AppState()


async def broadcast(message: dict[str, Any]) -> None:
    dead: set[WebSocket] = set()
    for ws in state.websockets:
        try:
            await ws.send_json(message)
        except Exception:  # noqa: BLE001 - 切断されたソケットは後で片付ける
            dead.add(ws)
    state.websockets -= dead


async def generation_loop() -> None:
    loop = asyncio.get_running_loop()
    assert state.comfy_client is not None
    while True:
        await state.running.wait()
        if len(state.pending_tracks) >= BUFFER_TARGET:
            await asyncio.sleep(1.0)
            continue

        # pending_genres/ に外部から差し込まれたジャンルがあれば円環に反映する。
        state.position = insert_pending_genres(state.position)

        result = build_prompt(state.position, duration_seconds=DURATION_SECONDS)
        logger.info(
            "generating: pos=%.3f genre=%s bpm=%s title=%s",
            state.position,
            result.primary_genre,
            result.bpm,
            result.title,
        )

        try:
            audio_bytes = await loop.run_in_executor(
                None, state.comfy_client.generate, result.prompt, DURATION_SECONDS
            )
        except Exception as exc:  # noqa: BLE001 - 生成失敗時もループを止めない
            logger.error("generation failed: %s", exc)
            await broadcast({"type": "error", "message": str(exc)})
            await asyncio.sleep(3.0)
            continue

        # 生成に成功して初めて、差し込みジャンルを永続化してpendingファイルを消す。
        mark_genre_used(result.primary_genre)

        track_id = uuid.uuid4().hex
        filename = f"{slugify(result.title)}_{track_id[:8]}.mp3"
        (OUTPUT_DIR / filename).write_bytes(audio_bytes)

        track = {
            "id": track_id,
            "url": f"/audio/{filename}",
            "title": result.title,
            "prompt": result.prompt,
            "bpm": result.bpm,
            "primary_genre": result.primary_genre,
            "secondary_genre": result.secondary_genre,
            "blend_fraction": round(result.blend_fraction, 3),
            "position": round(result.position, 3),
            "duration": DURATION_SECONDS,
        }
        state.pending_tracks.append(track)
        await broadcast({"type": "track_ready", "track": track})

        state.position = advance_position(state.position, step=STEP, jitter=JITTER)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state.comfy_client = ComfyClient(base_url=COMFY_BASE_URL)
    state.generation_task = asyncio.create_task(generation_loop())
    yield
    if state.generation_task:
        state.generation_task.cancel()


app = FastAPI(title="Endless BGM Player", lifespan=lifespan)
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(str(APP_DIR / "static" / "index.html"))


@app.get("/api/genres")
async def api_genres() -> list[dict[str, Any]]:
    return [{"name": g.name, "bpm_range": g.bpm_range} for g in GENRES]


@app.get("/api/state")
async def api_state() -> dict[str, Any]:
    return {
        "running": state.running.is_set(),
        "position": round(state.position, 3),
        "queued": len(state.pending_tracks),
    }


@app.post("/api/start")
async def api_start() -> dict[str, Any]:
    state.running.set()
    return {"running": True}


@app.post("/api/stop")
async def api_stop() -> dict[str, Any]:
    state.running.clear()
    return {"running": False}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    state.websockets.add(websocket)
    # 接続前に生成済みで、まだ誰も再生していない曲をまとめて追いつかせる。
    for track in state.pending_tracks:
        await websocket.send_json({"type": "track_ready", "track": track})
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except ValueError:
                continue
            if message.get("type") == "track_started":
                track_id = message.get("id")
                state.pending_tracks = [t for t in state.pending_tracks if t["id"] != track_id]
    except WebSocketDisconnect:
        state.websockets.discard(websocket)


app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


def _is_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def _open_app_window(url: str) -> None:
    """起動後、ブラウザのタブではなく独立したアプリウィンドウとして開く。"""
    time.sleep(1.5)

    if sys.platform == "win32":
        edge_candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for exe in edge_candidates:
            if Path(exe).exists():
                subprocess.Popen([exe, f"--app={url}", "--window-size=760,900"])  # noqa: S603
                return
        webbrowser.open_new(url)
        return

    if _is_wsl():
        # WSL上ではWindows側のブラウザをcmd.exe経由で起動する。
        for browser in ("msedge", "chrome"):
            try:
                subprocess.Popen(  # noqa: S603, S607
                    ["cmd.exe", "/c", "start", "", browser, f"--app={url}", "--window-size=760,900"]
                )
                return
            except OSError:
                continue
        try:
            subprocess.Popen(["cmd.exe", "/c", "start", "", url])  # noqa: S603, S607
            return
        except OSError:
            logger.warning("could not launch a Windows browser window from WSL; open %s manually", url)
        return

    webbrowser.open_new(url)


if __name__ == "__main__":
    import uvicorn

    display_host = "127.0.0.1"
    threading.Thread(
        target=_open_app_window, args=(f"http://{display_host}:{PORT}/",), daemon=True
    ).start()

    uvicorn.run(app, host="0.0.0.0", port=PORT)
