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
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from comfy_client import ComfyClient
from genre_circle import GENRES, advance_position, build_prompt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("endless_bgm_player")

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR.parents[1] / "outputs" / "endless_bgm_player"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COMFY_BASE_URL = os.environ.get("COMFY_BASE_URL", "http://127.0.0.1:8188")
PORT = int(os.environ.get("ENDLESS_BGM_PORT", "58317"))

DURATION_SECONDS = 120
BUFFER_TARGET = 2  # 常に用意しておく先読み曲数
STEP = 0.25
JITTER = 0.3

class AppState:
    def __init__(self) -> None:
        self.running = asyncio.Event()
        self.position: float = 0.0
        # 生成済み本数と、フロントエンドが再生を開始した本数の差分でバッファ量を管理する。
        # (asyncio.Queueだと誰も.get()しないため、消費を明示的に追跡する必要がある)
        self.produced_count = 0
        self.consumed_count = 0
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
        if state.produced_count - state.consumed_count >= BUFFER_TARGET:
            await asyncio.sleep(1.0)
            continue

        result = build_prompt(state.position, duration_seconds=DURATION_SECONDS)
        logger.info("generating: pos=%.3f genre=%s bpm=%s", state.position, result.primary_genre, result.bpm)

        try:
            audio_bytes = await loop.run_in_executor(
                None, state.comfy_client.generate, result.prompt, DURATION_SECONDS
            )
        except Exception as exc:  # noqa: BLE001 - 生成失敗時もループを止めない
            logger.error("generation failed: %s", exc)
            await broadcast({"type": "error", "message": str(exc)})
            await asyncio.sleep(3.0)
            continue

        track_id = uuid.uuid4().hex
        filename = f"{track_id}.mp3"
        (OUTPUT_DIR / filename).write_bytes(audio_bytes)

        track = {
            "id": track_id,
            "url": f"/audio/{filename}",
            "prompt": result.prompt,
            "bpm": result.bpm,
            "primary_genre": result.primary_genre,
            "secondary_genre": result.secondary_genre,
            "blend_fraction": round(result.blend_fraction, 3),
            "position": round(result.position, 3),
            "duration": DURATION_SECONDS,
        }
        state.produced_count += 1
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
        "queued": state.produced_count - state.consumed_count,
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
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except ValueError:
                continue
            if message.get("type") == "track_started":
                state.consumed_count += 1
    except WebSocketDisconnect:
        state.websockets.discard(websocket)


app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
