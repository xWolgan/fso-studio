"""Klient prostych usług HTTP (poza ComfyUI): Woosh (SFX), Breeze TTS (mowa EN/ZH).

Każda usługa przyjmuje jedno zapytanie naraz i odpowiada synchronicznie, więc postępu nie ma —
dyspozytor czeka na odpowiedź. Rodzaje odpowiedzi:
  json_plik — JSON z kluczami ścieżek do plików na maszynie (np. {"plik": ..., "wideo": ...}),
              pliki pobierane przez GET <usługa>/plik?path=...
  pcm16     — surowy strumień PCM s16le mono; częstotliwość z nagłówka X-Sample-Rate → zapis WAV.
"""
import wave
from pathlib import Path

import httpx


class Service:
    def __init__(self, url: str):
        self.url = url.rstrip("/")
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(900, connect=10))

    async def alive(self) -> bool:
        try:
            r = await self.http.get(self.url + "/health", timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    async def call(self, endpoint: str, fmt: str, fields: dict, files: dict[str, Path]) -> httpx.Response:
        fields = {k: v for k, v in fields.items() if v is not None and v != ""}   # puste pola = domyślne usługi
        handles = {k: (p.name, open(p, "rb")) for k, p in files.items()}
        try:
            if fmt == "json" and not handles:
                r = await self.http.post(self.url + endpoint, json=fields)
            else:
                data = {k: ("true" if v is True else "false" if v is False else str(v)) for k, v in fields.items()}
                r = await self.http.post(self.url + endpoint, data=data, files=handles or None)
        finally:
            for _, f in handles.values():
                f.close()
        if r.status_code == 409:
            raise RuntimeError("usługa jest zajęta innym zapytaniem")
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail", r.text)
            except Exception:
                detail = r.text
            raise RuntimeError(f"usługa odpowiedziała {r.status_code}: {str(detail)[:400]}")
        return r

    async def results(self, r: httpx.Response, kind: str, keys: list[str], dest_for) -> list[Path]:
        """Zapisuje wyniki; dest_for(ext) zwraca ścieżkę docelową dla pliku o danym rozszerzeniu."""
        if kind == "pcm16":
            rate = int(r.headers.get("X-Sample-Rate", "24000"))
            dest = dest_for(".wav")
            with wave.open(str(dest), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(rate)
                w.writeframes(r.content)
            return [dest]
        d = r.json()
        out = []
        for k in keys:
            src = d.get(k)
            if not src:
                continue
            dest = dest_for(Path(src).suffix.lower())
            async with self.http.stream("GET", self.url + "/plik", params={"path": src}) as resp:
                resp.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in resp.aiter_bytes():
                        f.write(chunk)
            out.append(dest)
        return out
