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
                        obslugiwany=ob in ("tekst", "obraz", "wideo") or "speech" in wy,
                        narzedzia="tools" in (m.get("supported_parameters") or []),
                        glosy=m.get("supported_voices") or [], mowa_api="speech" in wy))
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
                            obraz_we=kat.startswith("image"), obslugiwany=True, kategoria=kat))
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
        out.append(_poz(i, i, ob, obraz_we=ob == "tekst", obslugiwany=ob in ("tekst", "obraz", "mowa"), narzedzia=True))
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
                            obslugiwany=ob in ("tekst", "obraz"), narzedzia=True))
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


def _kie() -> list:
    """Kie.ai: katalog zebrany z dokumentacji (narzedzia/kie_katalog.py → modele/kie-katalog.json)."""
    try:
        dane = json.loads((Path(MODELE) / "kie-katalog.json").read_text(encoding="utf-8"))
    except Exception:
        return []
    return [_poz(m["id"], m["nazwa"], m["obszar"], m.get("opis"), obslugiwany=True, parametry=m["parametry"],
                 wejscia=m["wejscia"]) for m in dane.get("modele", [])]


async def pobierz_katalog(d: str) -> list:
    if d == "kie":
        kat = _kie()
    elif d == "higgsfield":
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
        return {"czas": time.time(), "modele": _z_repo(d) if d == "higgsfield" else _kie()}
    try:
        kat = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    for m in kat.get("modele", []):                   # obsługa zależy od wersji Studia, nie od chwili pobrania katalogu
        if d == "openrouter":
            m["obslugiwany"] = m["obszar"] in ("tekst", "obraz", "wideo") or bool(m.get("mowa_api"))
        elif d == "openai":
            m["obslugiwany"] = m["obszar"] in ("tekst", "obraz", "mowa")
        elif d == "gemini":
            m["obslugiwany"] = m["obszar"] in ("tekst", "obraz")
        else:
            m["obslugiwany"] = m["obszar"] == "tekst" if d == "anthropic" else True
    return kat


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


# --- fal.ai: opis parametrów (OpenAPI) → pola formularza Studia ---

SCHEMATY = KATALOGI / "schematy"
WEJSCIA_PLIKOW = (("image", "obraz"), ("video", "wideo"), ("audio", "dzwiek"))
POMIJANE = {"sync_mode", "enable_safety_checker", "safety_tolerance", "output_format", "webhook_url", "num_images"}


def _rozwin(schemat: dict, sch: dict) -> dict:
    """$ref / allOf / anyOf z jednym typem → zwykły opis pola."""
    if "$ref" in sch:
        return _rozwin(schemat, schemat["components"]["schemas"][sch["$ref"].split("/")[-1]])
    for k in ("allOf", "anyOf", "oneOf"):
        if k in sch:
            czesci = [_rozwin(schemat, x) for x in sch[k]]
            enumy = [x for x in czesci if x.get("enum")]
            proste = [x for x in czesci if x.get("type") not in (None, "null", "object")]
            baza = {kk: vv for kk, vv in sch.items() if kk != k}
            return {**(enumy[0] if enumy else proste[0] if proste else {}), **baza}
    return sch


def pola_z_openapi(schemat: dict, endpoint_id: str) -> tuple[list, list]:
    """(parametry, wejścia) z OpenAPI fal.ai dla endpointu."""
    sciezka = next((v for k, v in schemat.get("paths", {}).items() if k.rstrip("/").endswith(endpoint_id)
                    and "post" in v), None) or next(v for v in schemat.get("paths", {}).values() if "post" in v)
    wej = _rozwin(schemat, sciezka["post"]["requestBody"]["content"]["application/json"]["schema"])
    wymagane = set(wej.get("required") or [])
    kolejnosc = wej.get("x-fal-order-properties") or wej.get("x-apidog-orders") or list(wej.get("properties", {}))
    kolejnosc += [k for k in wej.get("properties", {}) if k not in kolejnosc]
    parametry, wejscia = [], []
    for nazwa in kolejnosc:
        if nazwa not in wej.get("properties", {}) or nazwa in POMIJANE:
            continue
        p = _rozwin(schemat, wej["properties"][nazwa])
        typ, dom, tytul = p.get("type"), p.get("default"), p.get("title") or nazwa.replace("_", " ")
        if dom is None and (p.get("enum") or typ in ("boolean", "integer", "number")) and p.get("examples"):
            dom = p["examples"][0]                 # Kie.ai: zamiast `default` podaje przykłady
        opis = (p.get("description") or "")[:300]
        wym = nazwa in wymagane
        plik = next((r for slowo, r in WEJSCIA_PLIKOW if slowo in nazwa and (nazwa.endswith("_url") or nazwa.endswith("_urls"))), None)
        if not plik and nazwa in ("input_url", "input_urls", "reference_image", "reference_images", "first_frame", "last_frame"):
            plik = "obraz"
        if plik:
            wiele = typ == "array" or nazwa.endswith("_urls")
            wejscia.append({"id": nazwa, "typ": plik, "cel": nazwa, "etykieta": {"pl": tytul, "en": tytul},
                            "wiele": int(p.get("maxItems") or 4) if wiele else None, "wymagane": wym, "opis": opis})
            continue
        baza = {"id": nazwa, "etykieta": {"pl": tytul, "en": tytul}, "pomoc": opis, "cel": [nazwa], "pomin_puste": not wym}
        if nazwa == "prompt" or (nazwa in ("text", "input", "lyrics") and not any(x["typ"] == "prompt" for x in parametry)
                                 and "prompt" not in wej.get("properties", {})):
            parametry.append({**baza, "id": "prompt", "typ": "prompt", "wymagane": wym, "opcjonalny": not wym})   # Studio: prompt = „prompt”
        elif nazwa == "seed":
            parametry.append({**baza, "typ": "seed", "max": 2**31 - 1})
        elif p.get("enum"):
            opcje = [str(x) for x in p["enum"]]
            zast = next((x for x in ("auto", "none", "default") if x in opcje), opcje[0])
            parametry.append({**baza, "typ": "wybor", "opcje": opcje, "domyslnie": str(dom) if dom is not None else zast,
                              "wartosc_typ": "int" if typ == "integer" else "float" if typ == "number" else None})
        elif typ == "boolean":
            parametry.append({**baza, "typ": "przelacznik", "domyslnie": bool(dom)})
        elif typ in ("integer", "number") and p.get("minimum") is not None and p.get("maximum") is not None:
            parametry.append({**baza, "typ": "liczba" if typ == "integer" else "ulamek", "min": p["minimum"], "max": p["maximum"],
                              "domyslnie": dom if dom is not None else p["minimum"],
                              **({"krok": (p["maximum"] - p["minimum"]) / 100} if typ == "number" else {})})
        elif typ in ("integer", "number", "string"):
            parametry.append({**baza, "typ": "tekst", "domyslnie": "" if dom is None else str(dom), "wymagane": wym,
                              "wartosc_typ": {"integer": "int", "number": "float"}.get(typ)})
        # obiekty i listy złożone (np. LoRA) — pomijane
    parametry.sort(key=lambda x: 0 if x["typ"] == "prompt" else 2 if x["typ"] == "seed" else 1)   # prompt na górze, seed na dole
    return parametry, wejscia


def _plik_schematu(d: str, model_id: str) -> Path:
    return SCHEMATY / (id_studia(d, model_id) + ".json")


def _et(pl, en, fr=None):
    return {"pl": pl, "en": en, "fr": fr or en}


async def _schemat_openrouter(model_id: str) -> dict:
    """OpenRouter nie opisuje parametrów modeli mediów — stały formularz wg rodzaju (obraz / wideo / mowa)."""
    poz = next((m for m in (katalog("openrouter") or {}).get("modele", []) if m["id"] == model_id), None)
    if not poz:
        raise RuntimeError("model spoza katalogu — odśwież listę")
    prompt = {"id": "prompt", "typ": "prompt", "cel": ["prompt"], "wymagane": True}
    wybor = lambda i, cel, et, opcje, dom, **x: {"id": i, "typ": "wybor", "cel": [cel], "etykieta": et, "opcje": opcje,
                                                "domyslnie": dom if dom in opcje else opcje[0], **x}
    if poz["obszar"] == "obraz":
        domyslna = {"": _et("domyślna", "default", "par défaut")}      # „” = nie wysyłamy — decyduje model
        par = [prompt, wybor("aspect_ratio", "aspect_ratio", _et("proporcje", "aspect ratio", "proportions"),
                             ["", "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "4:5", "5:4", "21:9"], "",
                             pomin_puste=True, etykiety_opcji=domyslna),
               wybor("resolution", "resolution", _et("rozdzielczość", "resolution", "résolution"), ["", "1K", "2K", "4K"], "",
                     pomin_puste=True, etykiety_opcji=domyslna)]
        wej = [{"id": "input_references", "typ": "obraz", "cel": "input_references", "wiele": 4,
                "etykieta": _et("obrazy referencyjne", "reference images", "images de référence")}] if poz.get("obraz_we") else []
        return {"parametry": par, "wejscia": wej, "endpoint": "images", "cena": ""}
    if poz["obszar"] == "wideo":
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get("https://openrouter.ai/api/v1/videos/models", headers=naglowki("openrouter"))
            r.raise_for_status()
        v = next((x for x in r.json().get("data", []) if x["id"] == model_id or x.get("canonical_slug") == model_id), {})
        dl = [str(x) for x in v.get("supported_durations") or [5]]
        par = [prompt, wybor("duration", "duration", _et("długość (s)", "length (s)", "durée (s)"), dl, dl[0], wartosc_typ="int")]
        if v.get("supported_resolutions"):
            par.append(wybor("resolution", "resolution", _et("rozdzielczość", "resolution", "résolution"), v["supported_resolutions"],
                             "720p"))
        if v.get("supported_aspect_ratios"):
            par.append(wybor("aspect_ratio", "aspect_ratio", _et("proporcje", "aspect ratio", "proportions"), v["supported_aspect_ratios"],
                             "16:9"))
        par.append({"id": "generate_audio", "typ": "przelacznik", "cel": ["generate_audio"], "domyslnie": True,
                    "etykieta": _et("z dźwiękiem", "with sound", "avec son")})
        wej = [{"id": "first_frame", "typ": "obraz", "cel": "first_frame", "etykieta": _et("pierwsza klatka", "first frame", "première image")},
               {"id": "last_frame", "typ": "obraz", "cel": "last_frame", "etykieta": _et("ostatnia klatka", "last frame", "dernière image")},
               {"id": "input_references", "typ": "obraz", "cel": "input_references", "wiele": 4,
                "etykieta": _et("obrazy referencyjne", "reference images", "images de référence")}]
        return {"parametry": par, "wejscia": wej, "endpoint": "videos", "cena": ""}
    if poz.get("mowa_api"):
        glosy = poz.get("glosy") or []
        par = [{**prompt, "cel": ["input"]}]
        if glosy:
            par.append(wybor("voice", "voice", _et("głos", "voice", "voix"), glosy, glosy[0]))
        par.append({"id": "instructions", "typ": "tekst", "cel": ["instructions"], "pomin_puste": True,
                    "etykieta": _et("jak mówić (ton, tempo)", "how to speak (tone, pace)", "comment parler (ton, rythme)")})
        return {"parametry": par, "wejscia": [], "endpoint": "audio/speech", "cena": "", "stale": {"response_format": "mp3"}}
    raise RuntimeError("tego rodzaju modelu Studio jeszcze nie obsługuje")


GLOSY_OPENAI = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer", "verse", "marin", "cedar"]
GLOSY_TTS1 = ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"]


def _schemat_openai_gemini(d: str, model_id: str) -> dict:
    """ChatGPT: obraz (images/generations) i mowa (audio/speech); Gemini: obraz (images/generations, zgodny z OpenAI)."""
    poz = next((m for m in (katalog(d) or {}).get("modele", []) if m["id"] == model_id), None)
    if not poz:
        raise RuntimeError("model spoza katalogu — odśwież listę")
    prompt = {"id": "prompt", "typ": "prompt", "cel": ["prompt"], "wymagane": True}
    domyslna = {"": _et("domyślna", "default", "par défaut")}
    if poz["obszar"] == "obraz" and d == "openai":
        rozm = ["1024x1024", "1792x1024", "1024x1792"] if "dall-e" in model_id else ["auto", "1024x1024", "1536x1024", "1024x1536"]
        par = [prompt, {"id": "size", "typ": "wybor", "cel": ["size"], "opcje": rozm, "domyslnie": rozm[0],
                        "etykieta": _et("rozmiar", "size", "taille")}]
        if "gpt-image" in model_id:
            par.append({"id": "quality", "typ": "wybor", "cel": ["quality"], "opcje": ["auto", "low", "medium", "high"],
                        "domyslnie": "auto", "etykieta": _et("jakość", "quality", "qualité")})
        stale = {"n": 1} | ({"response_format": "b64_json"} if "dall-e" in model_id else {})
        return {"parametry": par, "wejscia": [], "endpoint": "images/generations", "cena": "", "stale": stale}
    if poz["obszar"] == "obraz":                          # gemini
        par = [prompt, {"id": "aspect_ratio", "typ": "wybor", "cel": ["aspect_ratio"], "pomin_puste": True,
                        "opcje": ["", "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "21:9"], "domyslnie": "",
                        "etykiety_opcji": domyslna, "etykieta": _et("proporcje", "aspect ratio", "proportions")}]
        return {"parametry": par, "wejscia": [], "endpoint": "images/generations", "cena": "",
                "stale": {"n": 1, "response_format": "b64_json"}}
    if poz["obszar"] == "mowa" and d == "openai":
        glosy = GLOSY_TTS1 if model_id.startswith("tts-1") else GLOSY_OPENAI
        par = [{**prompt, "cel": ["input"]}, {"id": "voice", "typ": "wybor", "cel": ["voice"], "opcje": glosy, "domyslnie": "coral",
                                               "etykieta": _et("głos", "voice", "voix")}]
        if not model_id.startswith("tts-1"):
            par.append({"id": "instructions", "typ": "tekst", "cel": ["instructions"], "pomin_puste": True,
                        "etykieta": _et("jak mówić (ton, tempo)", "how to speak (tone, pace)", "comment parler (ton, rythme)")})
        return {"parametry": par, "wejscia": [], "endpoint": "audio/speech", "cena": "", "stale": {"response_format": "mp3"}}
    raise RuntimeError("tego rodzaju modelu Studio jeszcze nie obsługuje")


async def pobierz_schemat(d: str, model_id: str) -> dict:
    """Parametry modelu mediów → zapis obok katalogu. fal.ai: z OpenAPI endpointu + cena; OpenRouter, ChatGPT, Gemini:
    stały formularz wg rodzaju modelu."""
    if d in ("openrouter", "openai", "gemini"):
        out = await _schemat_openrouter(model_id) if d == "openrouter" else _schemat_openai_gemini(d, model_id)
        SCHEMATY.mkdir(parents=True, exist_ok=True)
        _plik_schematu(d, model_id).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        return out
    async with httpx.AsyncClient(timeout=TIMEOUT) as c:
        h = naglowki("fal") if klucz("fal") else {}
        r = await c.get("https://api.fal.ai/v1/models", params={"endpoint_id": model_id, "expand": "openapi-3.0"}, headers=h)
        r.raise_for_status()
        m = (r.json().get("models") or [None])[0]
        if not m or not m.get("openapi"):
            raise RuntimeError("brak opisu parametrów")
        parametry, wejscia = pola_z_openapi(m["openapi"], model_id)
        cena = ""
        try:
            rc = await c.get("https://api.fal.ai/v1/models/pricing", params={"endpoint_id": model_id}, headers=h)
            if rc.status_code == 200:
                pr = (rc.json().get("prices") or [None])[0]
                if pr:
                    cena = f"{pr.get('unit_price')} {pr.get('currency', 'USD')} / {pr.get('unit')}"
        except httpx.HTTPError:
            pass
    out = {"parametry": parametry, "wejscia": wejscia, "cena": cena, "kategoria": (m.get("metadata") or {}).get("category")}
    SCHEMATY.mkdir(parents=True, exist_ok=True)
    _plik_schematu(d, model_id).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def schemat(d: str, model_id: str) -> dict | None:
    try:
        return json.loads(_plik_schematu(d, model_id).read_text(encoding="utf-8"))
    except Exception:
        return None
