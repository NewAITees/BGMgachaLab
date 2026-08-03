"""ComfyUI HTTP API クライアント。

`workflows/comfy_desktop/stable_audio_3_bgm.json` をテンプレートとして読み込み、
プロンプト文・尺・シードだけを差し替えて `/prompt` に投入する。
`tasks/lessons.md` の運用知見に従い、1リクエストずつ逐次実行する前提。
"""

from __future__ import annotations

import copy
import json
import random
import time
import uuid
from pathlib import Path
from typing import Any

import httpx

WORKFLOW_PATH = (
    Path(__file__).resolve().parents[2] / "workflows" / "comfy_desktop" / "stable_audio_3_bgm.json"
)

PROMPT_TEXT_NODE = "52:31"
DURATION_NODE = "52:36"
SEED_NODE = "52:3"
ENABLE_REPROMPT_NODE = "52:35"


class ComfyGenerationError(RuntimeError):
    pass


class ComfyClient:
    def __init__(self, base_url: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = uuid.uuid4().hex
        self._http = httpx.Client(base_url=self.base_url, timeout=timeout)
        self._workflow_template: dict[str, Any] = json.loads(
            WORKFLOW_PATH.read_text(encoding="utf-8")
        )

    def build_workflow(self, prompt_text: str, duration_seconds: int) -> dict[str, Any]:
        workflow = copy.deepcopy(self._workflow_template)
        workflow[PROMPT_TEXT_NODE]["inputs"]["value"] = prompt_text
        workflow[DURATION_NODE]["inputs"]["value"] = duration_seconds
        workflow[SEED_NODE]["inputs"]["seed"] = random.randint(0, 2**48 - 1)
        # LLMによる再展開は行わず、円環由来のプロンプトをそのまま使う。
        workflow[ENABLE_REPROMPT_NODE]["inputs"]["value"] = False
        return workflow

    def submit(self, prompt_text: str, duration_seconds: int) -> str:
        workflow = self.build_workflow(prompt_text, duration_seconds)
        response = self._http.post(
            "/prompt", json={"prompt": workflow, "client_id": self.client_id}
        )
        response.raise_for_status()
        return response.json()["prompt_id"]

    def wait_for_result(
        self, prompt_id: str, poll_interval: float = 1.0, timeout: float = 180.0
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            response = self._http.get(f"/history/{prompt_id}")
            response.raise_for_status()
            history = response.json()
            entry = history.get(prompt_id)
            if entry:
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise ComfyGenerationError(f"ComfyUI generation failed: {status}")
                if entry.get("outputs"):
                    return entry["outputs"]
            time.sleep(poll_interval)
        raise TimeoutError(f"ComfyUI generation timed out for prompt_id={prompt_id}")

    @staticmethod
    def _find_audio_info(outputs: dict[str, Any]) -> dict[str, Any]:
        for node_output in outputs.values():
            if isinstance(node_output, dict) and node_output.get("audio"):
                return node_output["audio"][0]
        raise ComfyGenerationError(f"No audio output found in ComfyUI response: {outputs}")

    def fetch_audio(self, outputs: dict[str, Any]) -> bytes:
        audio_info = self._find_audio_info(outputs)
        params = {
            "filename": audio_info["filename"],
            "subfolder": audio_info.get("subfolder", ""),
            "type": audio_info.get("type", "output"),
        }
        response = self._http.get("/view", params=params)
        response.raise_for_status()
        return response.content

    def generate(self, prompt_text: str, duration_seconds: int) -> bytes:
        prompt_id = self.submit(prompt_text, duration_seconds)
        outputs = self.wait_for_result(prompt_id)
        return self.fetch_audio(outputs)
