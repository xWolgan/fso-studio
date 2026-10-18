"""Dostawcy modeli w chmurze: klucze, katalogi modeli i wybór użytkownika (strona Ustawienia).

Każdy dostawca: klucz w sekrety.env (zmienna z `klucz_env`), sprawdzenie klucza, katalog modeli pobrany z jego API
(albo — HiggsField, Kie.ai — z opisów w repo, bo API nie ma katalogu). Pozycja katalogu:
  {id, nazwa, obszar, opis, cena, obraz_we, obslugiwany}
`obslugiwany` = Studio umie już ten model uruchomić (reszta jest widoczna, ale do wyboru „wkrótce”).
Katalog trafia do zasoby/katalog/<dostawca>.json (odświeżany przyciskiem), wybór — do zasoby/ustawienia.json.
"""
import asyncio
import json
import os
import re
import time
from pathlib import Path

import httpx
import yaml

from .config import MODELE, ROOT, ZASOBY

SEKRETY = Path(os.environ.get("STUDIO_SEKRETY", ROOT / "sekrety.env"))
USTAWIENIA = ZASOBY / "ustawienia.json"
KATALOGI = ZASOBY / "katalog"

DOSTAWCY = {
    "openrouter": {"nazwa": "OpenRouter", "klucz_env": "OPENROUTER_API_KEY", "klucz_url": "https://openrouter.ai/keys",
                   "chat": "https://openrouter.ai/api/v1"},
    "fal": {"nazwa": "fal.ai", "klucz_env": "FAL_KEY", "klucz_url": "https://fal.ai/dashboard/keys"},
    "higgsfield": {"nazwa": "HiggsField", "klucz_env": "HF_KEY", "klucz_url": "https://cloud.higgsfield.ai/api-keys",
                   "format": "key_id:secret"},
    "kie": {"nazwa": "Kie.ai", "klucz_env": "KIE_API_KEY", "klucz_url": "https://kie.ai/api-key"},
    "anthropic": {"nazwa": "Claude (Anthropic)", "klucz_env": "ANTHROPIC_API_KEY", "klucz_url": "https://console.anthropic.com/settings/keys",
                  "chat": "https://api.anthropic.com/v1"},
    "openai": {"nazwa": "ChatGPT (OpenAI)", "klucz_env": "OPENAI_API_KEY", "klucz_url": "https://platform.openai.com/api-keys",
               "chat": "https://api.openai.com/v1"},
    "gemini": {"nazwa": "Gemini (Google)", "klucz_env": "GEMINI_API_KEY", "klucz_url": "https://aistudio.google.com/apikey",
               "chat": "https://generativelanguage.googleapis.com/v1beta/openai"},
}
OBSZARY_CHMURY = ("tekst", "obraz", "wideo", "muzyka", "sfx", "mowa")
TIMEOUT = httpx.Timeout(60, connect=15)


# --- klucze ---

def klucz(d: str) -> str:
    return os.environ.get(DOSTAWCY[d]["klucz_env"], "").strip()


def zapisz_klucz(d: str, wartosc: str):
    """Zapis do sekrety.env (podmiana jednej linii, reszta pliku bez zmian) i od razu do środowiska procesu."""
    env = DOSTAWCY[d]["klucz_env"]
    wartosc = (wartosc or "").strip().replace("\n", "")
    linie = SEKRETY.read_text(encoding="utf-8").splitlines() if SEKRETY.exists() else []
    nowa = f"{env}={wartosc}"
    for i, l in enumerate(linie):
        if re.match(rf"^\s*(export\s+)?{env}\s*=", l):
            linie[i] = nowa
            break
    else:
        linie.append(nowa)
    SEKRETY.write_text("\n".join(linie) + "\n", encoding="utf-8")
    if wartosc:
        os.environ[env] = wartosc
    else:
        os.environ.pop(env, None)
    _KLIENCI.pop(d, None)


def naglowki(d: str) -> dict:
    k = klucz(d)
    if d == "fal" or d == "higgsfield":
        return {"Authorization": f"Key {k}"}
    if d == "anthropic":
        return {"x-api-key": k, "anthropic-version": "2023-06-01"}
    if d == "gemini":
        return {"x-goog-api-key": k}
    return {"Authorization": f"Bearer {k}"}


_KLIENCI: dict = {}


# --- sprawdzenie klucza ---

async def sprawdz(d: str) -> tuple[bool, str]:
    """(działa?, krótki opis) — najtańsze zapytanie, które wymaga ważnego klucza."""
    if not klucz(d):
        return False, "brak klucza"
    url = {"openrouter": "https://openrouter.ai/api/v1/key",
           "fal": "https://api.fal.ai/v1/models?limit=1",
           "kie": "https://api.kie.ai/api/v1/chat/credit",
           "anthropic": "https://api.anthropic.com/v1/models?limit=1",
           "openai": "https://api.openai.com/v1/models",
           "gemini": "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1"}.get(d)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            if d == "higgsfield":       # bez katalogu: zapytanie o nieistniejące zadanie — 404 = klucz przyjęty
                r = await c.get("https://api.higgsfield.ai/requests/00000000-0000-0000-0000-000000000000/status",
                                headers=naglowki(d))
                return (r.status_code not in (401, 403)), ("klucz przyjęty" if r.status_code not in (401, 403) else "klucz odrzucony")
            r = await c.get(url, headers=naglowki(d))
    except httpx.HTTPError as e:
        return False, f"brak połączenia ({type(e).__name__})"
    if r.status_code in (401, 403):
        return False, "klucz odrzucony"
    if r.status_code != 200:
        return False, f"odpowiedź {r.status_code}"
    if d == "kie":
        j = r.json()
        if j.get("code") != 200:
            return False, str(j.get("msg") or "klucz odrzucony")[:80]
        return True, f"kredyty: {j.get('data')}"
    if d == "openrouter":
        j = (r.json() or {}).get("data") or {}
        lim = j.get("limit_remaining")
        return True, "działa" + (f" · pozostało {lim:.2f} USD" if isinstance(lim, (int, float)) else "")
    return True, "działa"


# --- katalogi ---

def _poz(id_, nazwa, obszar, opis="", cena="", obraz_we=False, obslugiwany=False, **x):
    return {"id": id_, "nazwa": nazwa, "obszar": obszar, "opis": (opis or "")[:300], "cena": cena, "obraz_we": obraz_we,
            "obslugiwany": obslugiwany, **x}


def _usd_m(v) -> str:
    try:
        return f"{float(v) * 1e6:.2f}"
    except (TypeError, ValueError):
        return "?"


async def _openrouter(c) -> list:
    r = await c.get("https://openrouter.ai/api/v1/models", params={"output_modalities": "all"},
                    headers=naglowki("openrouter") if klucz("openrouter") else {})
    r.raise_for_status()
    out = []
    for m in r.json().get("data", []):
        a = m.get("architecture") or {}
        wy, we = a.get("output_modalities") or [], a.get("input_modalities") or []
        p = m.get("pricing") or {}
        if "video" in wy:
            ob = "wideo"
        elif "image" in wy:
            ob = "obraz"
        elif "speech" in wy:
            ob = "mowa"
        elif "audio" in wy:
            ob = "muzyka" if "lyria" in m["id"] else "mowa"
        elif wy == ["text"] or "text" in wy:
            ob = "tekst"
        else:
            continue
        if any(x in wy for x in ("embeddings", "rerank", "transcription")) and ob == "tekst":
            continue
        cena = f"{_usd_m(p.get('prompt'))} / {_usd_m(p.get('completion'))} USD za 1M tokenów" if ob == "tekst" else ""
        out.append(_poz(m["id"], m.get("name") or m["id"], ob, m.get("description"), cena, "image" in we,
                        obslugiwany=ob == "tekst", narzedzia="tools" in (m.get("supported_parameters") or [])))
    return out


FAL_KATEGORIE = {"text-to-image": "obraz", "image-to-image": "obraz", "text-to-video": "wideo", "image-to-video": "wideo",
                 "video-to-video": "wideo", "text-to-speech": "mowa", "speech-to-speech": "mowa", "text-to-audio": "sfx",
                 "audio-to-audio": "sfx", "video-to-audio": "sfx", "text-to-music": "muzyka"}


async def _fal(c) -> list:
    out, kursor = [], None
    for _ in range(40):                                   # stronicowanie (limit bezpieczeństwa)
        params = {"status": "active", "limit": 100} | ({"cursor": kursor} if kursor else {})
        for proba in range(6):                            # bez klucza fal ostro limituje — czekamy i ponawiamy
            r = await c.get("https://api.fal.ai/v1/models", params=params, headers=naglowki("fal") if klucz("fal") else {})
            if r.status_code != 429:
                break
            await asyncio.sleep(float(r.headers.get("retry-after") or 0) or 2 * (proba + 1))
        r.raise_for_status()
        j = r.json()
        for m in j.get("models", []):
            md = m.get("metadata") or {}
            kat = md.get("category") or ""
            ob = FAL_KATEGORIE.get(kat)
            if not ob:
                continue
            tagi = " ".join(md.get("tags") or []).lower() + " " + m["endpoint_id"].lower()
            if ob == "sfx" and ("music" in tagi or "song" in tagi):
                ob = "muzyka"
            out.append(_poz(m["endpoint_id"], md.get("display_name") or m["endpoint_id"], ob, md.get("description"),
                            obraz_we=kat.startswith("image"), kategoria=kat))
        kursor = j.get("next_cursor")
        if not j.get("has_more") or not kursor:
            break
    return out


async def _anthropic(c) -> list:
    r = await c.get("https://api.anthropic.com/v1/models", params={"limit": 1000}, headers=naglowki("anthropic"))
    r.raise_for_status()
    return [_poz(m["id"], m.get("display_name") or m["id"], "tekst", "",
                 obraz_we=bool(((m.get("capabilities") or {}).get("image_input"))), obslugiwany=True, narzedzia=True)
            for m in r.json().get("data", []) if not m.get("deprecated_at")]


async def _openai(c) -> list:
    r = await c.get("https://api.openai.com/v1/models", headers=naglowki("openai"))
    r.raise_for_status()
    out = []
    for m in r.json().get("data", []):
        i = m["id"]
        if re.search(r"embedding|moderation|whisper|transcribe|realtime|search|davinci|babbage|instruct|sora", i):
            continue
        if re.search(r"gpt-image|dall-e", i):
            ob = "obraz"
        elif "tts" in i:
            ob = "mowa"
        elif re.match(r"(gpt-|o\d|chatgpt)", i) and "audio" not in i:
            ob = "tekst"
        else:
            continue
        out.append(_poz(i, i, ob, obraz_we=ob == "tekst", obslugiwany=ob == "tekst", narzedzia=True))
    return out


async def _gemini(c) -> list:
    out, token = [], None
    for _ in range(10):
        r = await c.get("https://generativelanguage.googleapis.com/v1beta/models",
                        params={"pageSize": 1000} | ({"pageToken": token} if token else {}), headers=naglowki("gemini"))
        r.raise_for_status()
        j = r.json()
        for m in j.get("models", []):
            i = m["name"].removeprefix("models/")
            metody = m.get("supportedGenerationMethods") or m.get("supported_actions") or []
            if re.search(r"embedding|aqa|robotics|computer-use", i):
                continue
            if "veo" in i or "predictLongRunning" in metody:
                ob = "wideo"
            elif "lyria" in i:
                ob = "muzyka"
            elif "tts" in i:
                ob = "mowa"
            elif "image" in i or "imagen" in i:
                ob = "obraz"
            elif "generateContent" in metody:
                ob = "tekst"
            else:
                continue
            out.append(_poz(i, m.get("displayName") or i, ob, m.get("description"), obraz_we=ob == "tekst",
                            obslugiwany=ob == "tekst", narzedzia=True))
        token = j.get("nextPageToken")
        if not token:
            break
    return out


def _z_repo(dostawca: str) -> list:
    """HiggsField / Kie.ai: modele opisane w repo (modele/*/*.yaml z `dostawca:`) — te Studio już umie uruchomić."""
    out = []
    for f in sorted(Path(MODELE).glob("*/*.yaml")):
        y = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if y.get("backend") == "api" and y.get("dostawca") == dostawca and not y.get("ukryty"):
            opis = y.get("opis") or {}
            out.append(_poz(y["id"], y["nazwa"], y["obszar"], opis.get("pl") if isinstance(opis, dict) else str(opis),
                            obslugiwany=True, z_repo=True))
    return out


async def pobierz_katalog(d: str) -> list:
    if d in ("higgsfield", "kie"):
        kat = _z_repo(d)
    else:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            kat = await {"openrouter": _openrouter, "fal": _fal, "anthropic": _anthropic, "openai": _openai,
                         "gemini": _gemini}[d](c)
    kat.sort(key=lambda x: (OBSZARY_CHMURY.index(x["obszar"]), not x["obslugiwany"], x["nazwa"].lower()))
    KATALOGI.mkdir(parents=True, exist_ok=True)
    (KATALOGI / f"{d}.json").write_text(json.dumps({"czas": time.time(), "modele": kat}, ensure_ascii=False), encoding="utf-8")
    return kat


def katalog(d: str) -> dict | None:
    p = KATALOGI / f"{d}.json"
    if d in ("higgsfield", "kie"):            # opisy z repo — zawsze aktualne
        return {"czas": time.time(), "modele": _z_repo(d)}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


# --- wybór użytkownika ---

def ustawienia() -> dict:
    try:
        return json.loads(USTAWIENIA.read_text(encoding="utf-8"))
    except Exception:
        return {"wybrane": {}}


def zapisz_ustawienia(u: dict):
    USTAWIENIA.parent.mkdir(parents=True, exist_ok=True)
    USTAWIENIA.write_text(json.dumps(u, ensure_ascii=False, indent=1), encoding="utf-8")


def wybrane(d: str) -> list[str]:
    return list((ustawienia().get("wybrane") or {}).get(d) or [])


def ustaw_wybor(d: str, model_id: str, tak: bool):
    u = ustawienia()
    w = u.setdefault("wybrane", {}).setdefault(d, [])
    if tak and model_id not in w:
        w.append(model_id)
    if not tak and model_id in w:
        w.remove(model_id)
    zapisz_ustawienia(u)


def wybrane_pozycje() -> list[tuple[str, dict]]:
    """(dostawca, pozycja katalogu) dla wybranych i obsługiwanych modeli, których dostawca ma klucz."""
    out = []
    for d in DOSTAWCY:
        if not klucz(d):
            continue
        ids = wybrane(d)
        if not ids:
            continue
        kat = {m["id"]: m for m in (katalog(d) or {}).get("modele", [])}
        for i in ids:
            if i in kat and kat[i]["obslugiwany"]:
                out.append((d, kat[i]))
    return out


def id_studia(d: str, model_id: str) -> str:
    """Id modelu w Studiu (bezpieczne w adresach i nazwach plików)."""
    return f"{d}--" + re.sub(r"[^0-9a-z._-]+", "-", model_id.lower()).strip("-")[:80]
