"""Klient ComfyUI: wgrywanie wejść, wysłanie workflow, postęp (WebSocket), pobranie wyników."""
import asyncio
import json
import uuid
from pathlib import Path

import httpx
import websockets


class Comfy:
    def __init__(self, url: str):
        self.url = url.rstrip("/")
        self.client_id = str(uuid.uuid4())
        self.progress: dict[str, float] = {}     # prompt_id -> 0..1
        self.http = httpx.AsyncClient(timeout=120)

    async def alive(self) -> bool:
        try:
            r = await self.http.get(self.url + "/system_stats", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    async def upload(self, path: Path, name: str) -> str:
        """Wgrywa plik do katalogu input ComfyUI; zwraca nazwę do użycia w węźle."""
        with open(path, "rb") as f:
            r = await self.http.post(self.url + "/upload/image",
                                     files={"image": (name, f)}, data={"overwrite": "true", "subfolder": "fso"})
        r.raise_for_status()
        d = r.json()
        return f"{d['subfolder']}/{d['name']}" if d.get("subfolder") else d["name"]

    async def submit(self, wf: dict) -> str:
        r = await self.http.post(self.url + "/prompt", json={"prompt": wf, "client_id": self.client_id})
        d = r.json()
        if r.status_code != 200 or d.get("node_errors"):
            err = d.get("error", {})
            msg = err.get("message", "") if isinstance(err, dict) else str(err)
            details = "; ".join(f"{nid}: {[e.get('message') for e in ne.get('errors', [])]}"
                                for nid, ne in (d.get("node_errors") or {}).items())
            raise RuntimeError(f"ComfyUI odrzucił workflow: {msg} {details}".strip())
        return d["prompt_id"]

    async def history(self, prompt_id: str) -> dict | None:
        r = await self.http.get(f"{self.url}/history/{prompt_id}")
        return r.json().get(prompt_id)

    async def outputs(self, prompt_id: str) -> list[dict]:
        """Pliki wynikowe: [{filename, subfolder, type, kind}]."""
        h = await self.history(prompt_id) or {}
        files = []
        for node_id, node_out in (h.get("outputs") or {}).items():
            for kind in ("images", "gifs", "videos", "audio"):
                for f in node_out.get(kind, []):
                    if f.get("type") == "output":
                        files.append({**f, "kind": kind, "wezel": str(node_id)})
        return files

    async def download(self, f: dict, dest: Path):
        params = {"filename": f["filename"], "subfolder": f.get("subfolder", ""), "type": f.get("type", "output")}
        async with self.http.stream("GET", self.url + "/view", params=params) as r:
            r.raise_for_status()
            with open(dest, "wb") as out:
                async for chunk in r.aiter_bytes():
                    out.write(chunk)

    async def interrupt(self):
        await self.http.post(self.url + "/interrupt")

    async def listen(self):
        """Nasłuch postępu przez WebSocket (działa w tle; wznawia się po zerwaniu)."""
        ws_url = self.url.replace("http", "ws", 1) + f"/ws?clientId={self.client_id}"
        while True:
            try:
                async with websockets.connect(ws_url, max_size=None, ping_interval=20) as ws:
                    async for raw in ws:
                        if not isinstance(raw, str):
                            continue
                        m = json.loads(raw)
                        d = m.get("data", {})
                        if m.get("type") == "progress" and d.get("prompt_id") and d.get("max"):
                            self.progress[d["prompt_id"]] = d["value"] / d["max"]
            except Exception:
                await asyncio.sleep(3)
