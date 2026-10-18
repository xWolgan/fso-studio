"""Generacja przez zewnętrzne API (HiggsField) i budżet uczestnika.

Model z `backend: api` w YAML: `dostawca`, `endpointy` (wybór wg podanych wejść), `cena` (USD za sekundę wyniku).
Budżet liczony w sekundach: koszt w USD / cena jednej sekundy „jednostki” (Kling/WAN 720p) — config.yaml → `budzet`.
Generacje lokalne nie schodzą z budżetu.

HiggsField (docs.higgsfield.ai): POST https://api.higgsfield.ai/<endpoint> → {request_id, status_url, cancel_url};
GET status_url → status queued | in_progress | completed | failed | nsfw | canceled; wynik: video.url / images[] / audio.url.
Pliki wejściowe: POST /files/generate-upload-url → PUT na upload_url → public_url. Klucz: zmienna HF_KEY („id:sekret”).
"""
import asyncio
import os
import random
from pathlib import Path

import httpx

from . import store
from .config import CFG
from .workflow import apply_params
from .i18n import K

BUDZET = CFG.get("budzet") or {}
USD_ZA_SEKUNDE = float(BUDZET.get("usd_za_sekunde", 0.042))     # „sekunda budżetu” = sekunda Kling/WAN 720p
PROG_ZADANIA_S = float(BUDZET.get("prog_zadania_s", 600))      # zadanie lokalne dłuższe niż to → propozycja API
CZAS_API_S = 180.0                                              # czas generacji w API, gdy brak historii
DOSTAWCY = {"higgsfield": {"klucz_env": "HF_KEY", "rownolegle": 10, "nazwa": "HiggsField"},
            "fal": {"klucz_env": "FAL_KEY", "rownolegle": 10, "nazwa": "fal.ai"}}
DOSTAWCY.update(CFG.get("api") or {})

TYPY_PLIKOW = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif",
               ".wav": "audio/wav", ".mp3": "audio/mpeg", ".mp4": "video/mp4"}


# --- budżet ---

NOWE_KONTA = BUDZET.get("nowe_konta")     # {miejsc, sekund}: tyle nowych loginów jeszcze wejdzie; brak = logowanie otwarte


def przydzial(login: str) -> float:
    osoby = BUDZET.get("osoby") or {}
    if login in osoby:
        return float(osoby[login])
    nowe = store.nowe_konta()
    if login in nowe:
        return float(nowe[login])
    return float(BUDZET.get("sekund", 1000))


def wpusc(login: str) -> bool:
    """Czy login może wejść: istniejące konto zawsze; nowe — tylko na wolne miejsce (gdy lista jest zamykana)."""
    if store.konto_istnieje(login) or login in (BUDZET.get("osoby") or {}) or not NOWE_KONTA:
        return True
    return store.zajmij_miejsce(login, float(NOWE_KONTA.get("sekund", 0)), int(NOWE_KONTA.get("miejsc", 0)))


def _wartosc(model, values: dict, pid: str):
    p = next((x for x in model.parametry if x["id"] == pid), None)
    return values.get(pid, p.get("domyslnie") if p else None)


def dlugosc(model, values: dict) -> int:
    """Długość wyniku w sekundach — tak, jak pójdzie do API (zaokrąglona i przycięta do zakresu modelu)."""
    p = next((x for x in model.parametry if x["typ"] == "dlugosc"), None)
    if not p:
        return 5
    try:
        s = float(values.get(p["id"], p.get("domyslnie", 5)))
    except (TypeError, ValueError):
        s = float(p.get("domyslnie", 5))
    return int(min(float(p.get("max", 15)), max(float(p.get("min", 1)), round(s))))


def koszt_usd(model, values: dict, ile: int = 1) -> float:
    c = model.cena or {}
    tabela = {str(k): float(v) for k, v in (c.get("usd_s") or {}).items()}
    if not tabela:
        return 0.0
    wg = c.get("wg")
    klucz = "|".join(str(_wartosc(model, values, x)) for x in (wg if isinstance(wg, list) else [wg])) if wg else "*"
    return tabela.get(klucz, max(tabela.values())) * dlugosc(model, values) * ile


def koszt_s(model, values: dict, ile: int = 1) -> float:
    """Koszt w sekundach budżetu."""
    return round(koszt_usd(model, values, ile) / USD_ZA_SEKUNDE, 1)


def dostepny(model) -> bool:
    d = DOSTAWCY.get(model.dostawca or "")
    return bool(d and os.environ.get(d.get("klucz_env", "")))


def endpoint_dla(model, wejscia: dict) -> dict | None:
    """Pierwszy endpoint, którego warunki spełniają podane wejścia (gdy: wszystkie, gdy_ktores: choć jedno).
    Endpoint z listą `wejscia` odpada, gdy podano coś spoza niej (i spoza `ignoruj`) — nic nie ginie po cichu."""
    podane = {k for k, v in (wejscia or {}).items() if v not in (None, "", [])}
    for e in model.endpointy:
        if not set(e.get("gdy", [])) <= podane or (e.get("gdy_ktores") and not podane & set(e["gdy_ktores"])):
            continue
        if "wejscia" in e and podane - set(e["wejscia"]) - set(e.get("ignoruj", [])):
            continue
        return e
    return None


# --- alternatywy płatne dla modeli lokalnych ---

def zapasy(model) -> list[dict]:
    """`zapas_api` z YAML: id modelu API albo lista (id lub {model, mapa: {wejście lokalne: wejście API}})."""
    z = model.zapas_api or []
    z = z if isinstance(z, list) else [z]
    return [{"model": x, "mapa": {}} if isinstance(x, str) else {"model": x["model"], "mapa": x.get("mapa") or {}}
            for x in z]


def przenies(cel, mapa: dict, wartosci: dict, wejscia: dict) -> tuple[dict, dict, list]:
    """Ustawienia i wejścia zadania lokalnego → model API: (wartości, wejścia, pominięte wejścia).
    Wartość spoza opcji modelu API przepada (zostaje domyślna)."""
    wej, pominiete = {}, []
    po_id = {i["id"]: i for i in cel.wejscia}
    for k, v in (wejscia or {}).items():
        if v in (None, "", []):
            continue
        k2 = mapa.get(k, k)
        inp = po_id.get(k2)
        if not inp or k2 in wej:
            pominiete.append(k)
            continue
        if inp.get("wiele"):
            wej[k2] = v if isinstance(v, list) else [v]
        else:
            if isinstance(v, list) and len(v) > 1:
                pominiete.append(k)
            wej[k2] = v[0] if isinstance(v, list) else v
    vals = {}
    for p in cel.parametry:
        if p["id"] not in (wartosci or {}):
            continue
        v = wartosci[p["id"]]
        opcje = p.get("opcje") or list(p.get("opcje_cele") or {})
        if opcje and str(v) not in {str(o) for o in opcje}:
            continue
        vals[p["id"]] = v
    return vals, wej, pominiete


def czas_api(model) -> float:
    """Typowy czas generacji modelu w API (mediana ostatnich gotowych zadań)."""
    with store.db() as c:
        r = c.execute("""SELECT koniec - start FROM jobs WHERE model=? AND status='gotowe' AND maszyna LIKE 'api%'
                         AND koniec > start ORDER BY id DESC LIMIT 15""", (model.id,)).fetchall()
    t = sorted(x[0] for x in r)
    return t[len(t) // 2] if t else CZAS_API_S


# --- HiggsField ---

class Higgsfield:
    BASE = "https://api.higgsfield.ai"

    def __init__(self, klucz: str):
        self.http = httpx.AsyncClient(base_url=self.BASE, timeout=httpx.Timeout(120, connect=15),
                                      headers={"Authorization": f"Key {klucz}", "Content-Type": "application/json"})
        self.pliki = httpx.AsyncClient(timeout=httpx.Timeout(600, connect=15), follow_redirects=True)

    @staticmethod
    def _blad(r: httpx.Response) -> str:
        try:
            d = r.json()
            return str(d.get("detail") or d.get("error") or d.get("message") or d)[:300]
        except Exception:
            return r.text[:300]

    async def upload(self, path: Path) -> str:
        typ = TYPY_PLIKOW.get(path.suffix.lower())
        if not typ:
            raise ValueError(K("e_api_typ", t=path.suffix, n=path.name))
        r = await self.http.post("/files/generate-upload-url", json={"content_type": typ})
        if r.status_code != 200:
            raise RuntimeError(K("e_api_wysylka", m=f"{r.status_code}: {self._blad(r)}"))
        d = r.json()
        r2 = await self.pliki.put(d["upload_url"], content=path.read_bytes(),
                                  headers=d.get("upload_headers") or {"Content-Type": typ})
        if r2.status_code >= 300:
            raise RuntimeError(K("e_api_wysylka", m=f"{path.name}, {r2.status_code}"))
        return d["public_url"]

    async def submit(self, endpoint: str, args: dict, idem: str) -> dict:
        r = await self.http.post("/" + endpoint, json=args, headers={"Idempotency-Key": idem})
        if r.status_code >= 300:
            if r.status_code in (401, 403):
                raise RuntimeError(K("e_api_dostep"))
            if r.status_code == 402:
                raise RuntimeError(K("e_api_srodki"))
            raise RuntimeError(K("e_api_odrzucilo", m=f"{r.status_code}: {self._blad(r)}"))
        d = r.json()
        return {k: d.get(k) for k in ("request_id", "status_url", "cancel_url")}

    async def status(self, status_url: str) -> dict:
        for proba in range(5):
            try:
                r = await self.http.get(status_url)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (401, 404):
                    raise RuntimeError(K("e_api_stan"))
            except httpx.HTTPError:
                pass
            await asyncio.sleep(3 * (proba + 1))
        raise RuntimeError(K("e_api_stan"))

    async def cancel(self, cancel_url: str) -> bool:
        try:
            r = await self.http.post(cancel_url)
            return r.status_code < 300
        except httpx.HTTPError:
            return False

    async def download(self, url: str, dest: Path):
        async with self.pliki.stream("GET", url) as r:
            if r.status_code != 200:
                raise RuntimeError(K("e_api_pobranie", m=r.status_code))
            with open(dest, "wb") as f:
                async for chunk in r.aiter_bytes(1 << 20):
                    f.write(chunk)


# --- fal.ai ---

class Fal(Higgsfield):
    """fal.ai — kolejka (queue.fal.run): submit → status → wynik. Interfejs jak Higgsfield (status znormalizowany:
    queued | in_progress | completed | failed; przy completed dołączony wynik). Pliki wejściowe: przez magazyn fal.ai
    (initiate → PUT), a gdy się nie uda — jako data URI."""
    BASE = "https://queue.fal.run"

    async def upload(self, path: Path) -> str:
        typ = TYPY_PLIKOW.get(path.suffix.lower())
        if not typ:
            raise ValueError(K("e_api_typ", t=path.suffix, n=path.name))
        try:
            r = await self.http.post("https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
                                     json={"content_type": typ, "file_name": path.name})
            if r.status_code == 200:
                d = r.json()
                r2 = await self.pliki.put(d["upload_url"], content=path.read_bytes(), headers={"Content-Type": typ})
                if r2.status_code < 300:
                    return d["file_url"]
        except httpx.HTTPError:
            pass
        import base64
        return f"data:{typ};base64," + base64.b64encode(path.read_bytes()).decode()

    async def submit(self, endpoint: str, args: dict, idem: str) -> dict:
        r = await self.http.post("/" + endpoint, json=args)
        if r.status_code >= 300:
            if r.status_code in (401, 403):
                raise RuntimeError(K("e_api_dostep"))
            if r.status_code == 402:
                raise RuntimeError(K("e_api_srodki"))
            raise RuntimeError(K("e_api_odrzucilo", m=f"{r.status_code}: {self._blad(r)}"))
        d = r.json()
        return {"request_id": d.get("request_id"), "status_url": d.get("status_url"), "cancel_url": d.get("cancel_url"),
                "response_url": d.get("response_url")}

    async def status(self, status_url: str) -> dict:
        d = None
        for proba in range(5):                       # fal odpowiada 200 albo 202 (w kolejce / w toku)
            try:
                r = await self.http.get(status_url)
                if r.status_code in (200, 202):
                    d = r.json()
                    break
                if r.status_code in (401, 404):
                    raise RuntimeError(K("e_api_stan"))
            except httpx.HTTPError:
                pass
            await asyncio.sleep(3 * (proba + 1))
        if d is None:
            raise RuntimeError(K("e_api_stan"))
        st = d.get("status")
        if st == "IN_QUEUE":
            return {"status": "queued"}
        if st == "IN_PROGRESS":
            return {"status": "in_progress"}
        if st == "COMPLETED":
            if d.get("error"):
                return {"status": "failed", "error": d.get("error")}
            wynik = await self.http.get(d.get("response_url") or status_url.rsplit("/status", 1)[0])
            if wynik.status_code != 200:
                return {"status": "failed", "error": self._blad(wynik)}
            return {"status": "completed", **wynik.json()}
        return {"status": "failed", "error": d.get("error") or st}

    async def cancel(self, cancel_url: str) -> bool:
        try:
            r = await self.http.put(cancel_url)
            return r.status_code < 300
        except httpx.HTTPError:
            return False


_KLIENCI: dict[str, Higgsfield] = {}


def klient(dostawca: str) -> Higgsfield:
    if dostawca not in _KLIENCI:
        d = DOSTAWCY.get(dostawca)
        klucz = os.environ.get((d or {}).get("klucz_env", ""), "")
        if not klucz:
            raise RuntimeError(f"brak klucza API dostawcy {dostawca}")
        _KLIENCI[dostawca] = (Fal if dostawca == "fal" else Higgsfield)(klucz)
    return _KLIENCI[dostawca]


def wynik_url(d: dict) -> str | None:
    for k in ("video", "audio", "image", "audio_file", "audio_url"):
        if isinstance(d.get(k), dict) and d[k].get("url"):
            return d[k]["url"]
        if isinstance(d.get(k), str) and d[k].startswith("http"):
            return d[k]
    for k in ("videos", "images", "audios"):
        if d.get(k):
            return d[k][0].get("url")
    return None


async def przygotuj(hf: Higgsfield, model, values: dict, wejscia: dict, plik_zasobu) -> tuple[str, dict, dict, dict]:
    """Zapytanie do API: (endpoint, argumenty, ustawienia użyte, opis wejść). plik_zasobu(id) → (Path, opis)."""
    e = endpoint_dla(model, wejscia)
    if not e:
        raise ValueError(K("e_api_tryb"))
    args = {k: v for k, v in (model.stale or {}).items() if k not in ("chmura", "api_model", "dostawca")}
    used = apply_params(model, values, lambda t, v: args.__setitem__(t, v))
    fmt = {}
    for p in model.parametry:
        if p["typ"] == "tryb":
            for k, v in p["opcje_cele"].get(values.get(p["id"], p.get("domyslnie")), {}).items():
                if k.startswith("_"):
                    fmt[k[1:]] = v
        elif p["typ"] == "dlugosc":
            for t in p.get("cel_sekundy", []):
                args[t] = dlugosc(model, values)
            used["dlugosc_s"] = dlugosc(model, values)
            used.pop("klatki", None), used.pop("fps", None)
        elif p["typ"] == "seed":
            for t in p["cel"]:
                args[t] = int(args[t]) % int(p.get("max", 2**31 - 1)) or 1     # API: tylko niezerowy seed
                used[p["id"]] = args[t]
    endpoint = e["endpoint"].format(**fmt)
    for k in e.get("pomin", []):
        args.pop(k, None)
    dozwolone = e.get("wejscia")
    opisy = {}
    for inp in model.wejscia:
        val = wejscia.get(inp["id"])
        if val in (None, "", []) or (dozwolone is not None and inp["id"] not in dozwolone):
            continue
        urls = []
        for i, aid in enumerate(val if isinstance(val, list) else [val]):
            path, opis = plik_zasobu(int(aid))
            urls.append(await hf.upload(path))
            opisy[f"{inp['id']} {i + 1}" if isinstance(val, list) else inp["id"]] = opis
        args[inp["cel"]] = urls if inp.get("wiele") else urls[0]
    used["dostawca"] = DOSTAWCY.get(model.dostawca, {}).get("nazwa", model.dostawca)
    used["endpoint"] = endpoint
    return endpoint, args, used, opisy


def idempotency(job_id: int) -> str:
    return f"fso-{job_id}-{random.randint(1, 10**9)}"
