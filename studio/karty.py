"""Karty postaci i lokacji — sztywne, z biblii: jedna karta = jeden obraz (arkusz ze wszystkimi ujęciami).

Pola bierzemy z biblii (sekcje tematów „Postacie i ludzie” / „Świat i wnętrza”, podsekcje „### <nazwa>” z wierszami
„Tożsamość: …”, „Strój: …” itd.), styl z „Faktury obrazu”. LLM tylko tłumaczy pola na angielski — prompt składa
się ze stałego wzoru, więc karta nie zależy od tego, czy model zrozumie prompt systemowy.
"""
import json
import re

import httpx
from fastapi import APIRouter, HTTPException, Request

from . import narzedzia, prompty, store
from .i18n import K

router = APIRouter()

POLA = {   # klucz → nazwy wierszy w biblii (pl / en / fr)
    "tozsamosc": ["tożsamość", "tozsamosc", "identity", "identité", "wygląd"],
    "stroj": ["strój", "stroj", "outfit", "ubranie", "tenue", "costume"],
    "wyraz": ["wyraz twarzy", "wyraz", "expression", "facial expression"],
    "czynnosc": ["czynność", "czynnosc", "activity", "activité", "gest"],
    "uklad": ["układ", "uklad", "layout", "plan"],
    "materialy": ["materiały", "materialy", "materials", "matières", "matieres"],
    "swiatlo": ["światło", "swiatlo", "light", "lumière", "lumiere", "pora"],
}
POSTAC = ("tozsamosc", "stroj", "wyraz", "czynnosc")
LOKACJA = ("uklad", "materialy", "swiatlo")

WZOR_POSTACI = (
    "STYLE: {styl}\n"
    "VIEW: a single clean unlabelled character reference sheet on a plain seamless mid-grey studio backdrop, soft even "
    "frontal light, the same person in every panel. Top row: four full-body views at identical scale, feet on one ground "
    "line — front, three-quarter, left profile, back — eye-level straight-on camera, long lens, no perspective distortion. "
    "Bottom row: three head-and-shoulders close-ups — front, three-quarter, profile — with the same expression; and one "
    "full-figure observational shot of the person caught mid-movement of their characteristic activity, unaware of the camera.\n"
    "SUBJECT: {tozsamosc}\n"
    "OUTFIT: {stroj}\n"
    "EXPRESSION: {wyraz}\n"
    "ACTIVITY: {czynnosc} — hands empty, the gesture performed without any object."
)
WZOR_LOKACJI = (
    "STYLE: {styl}\n"
    "VIEW: a single clean unlabelled location reference sheet, a 2×2 grid of four panels showing the same empty place in "
    "the same light: top-left — wide establishing view from eye level, 24mm, the whole layout visible; top-right — reverse "
    "wide view from the opposite side; bottom-left — medium view of the main area; bottom-right — three close-up details "
    "of surfaces and materials. No people.\n"
    "SETTING: {uklad}. Materials: {materialy}.\n"
    "LIGHT: {swiatlo}"
)


def _need(req: Request) -> str:
    u = store.kto(req.cookies.get("login")) if hasattr(store, "kto") else store.norm_login(req.cookies.get("login", ""))
    if not u or not store.konto_istnieje(u):
        raise HTTPException(401, K("e_zaloguj"))
    return u


def _sekcje(t: str, poziom: str) -> list[tuple[str, str]]:
    """[(nagłówek, treść)] dla nagłówków danego poziomu („##” albo „###”)."""
    czesci = re.split(rf"^{poziom}\s+(.+)$", t, flags=re.M)
    return [(czesci[i].strip(), czesci[i + 1]) for i in range(1, len(czesci) - 1, 2)]


def _pola(tresc: str) -> dict:
    out = {}
    for linia in tresc.splitlines():
        m = re.match(r"^\s*[-*]?\s*\**([^:*]{2,30})\**\s*:\s*(.+)$", linia)
        if not m:
            continue
        nazwa = m.group(1).strip().lower()
        for k, aliasy in POLA.items():
            if nazwa in aliasy and k not in out:
                out[k] = m.group(2).strip().lstrip("*").strip()      # „**Wyraz twarzy:** …”
    return out


def z_biblii(tekst: str) -> dict:
    ludzie = prompty.aliasy_wszystkie("tematy/02-ludzie.md")
    swiat = prompty.aliasy_wszystkie("tematy/01-swiat.md")
    faktura = prompty.aliasy_wszystkie("tematy/04-faktura.md")
    wynik = {"postacie": [], "lokacje": [], "styl": ""}
    for nagl, tresc in _sekcje(tekst, "##"):
        rodzaj = "postacie" if prompty._pasuje(nagl, ludzie) else "lokacje" if prompty._pasuje(nagl, swiat) else None
        if prompty._pasuje(nagl, faktura) and not wynik["styl"]:
            wynik["styl"] = re.sub(r"\s+", " ", re.sub(r"^#+.*$", "", tresc, flags=re.M)).strip()[:600]
        if not rodzaj:
            continue
        for nazwa, t in _sekcje(tresc, "###"):
            pola = _pola(t)
            if not pola:
                pola = {"tozsamosc" if rodzaj == "postacie" else "uklad": re.sub(r"\s+", " ", t).strip()[:800]}
            wynik[rodzaj].append({"nazwa": nazwa, "pola": pola})
    return wynik


@router.get("/api/karty")
async def api_karty(req: Request, biblia: str = ""):
    u = _need(req)
    p = prompty.plik_biblii(u, biblia)
    return z_biblii(p.read_text(encoding="utf-8", errors="replace")) if p else {"postacie": [], "lokacje": [], "styl": ""}


async def _po_angielsku(pola: dict) -> dict:
    """Jedno krótkie zapytanie do LLM: przekład pól na zwięzły angielski (bez dopisywania czegokolwiek)."""
    from .tekst import _cele
    from .registry import by_area
    puste = {k: v for k, v in pola.items() if not str(v or "").strip()}
    do = {k: v for k, v in pola.items() if str(v or "").strip()}
    if not do:
        return pola
    czat = next(iter(by_area("tekst")), None)
    body = {"model": czat.stale.get("llm_model", czat.id) if czat else "x", "temperature": 0.1, "max_tokens": 1500,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content":
                          "Translate each value of the JSON object into concise, concrete English suitable for an image-generation "
                          "prompt. Keep every detail, add nothing, keep proper names. If a value is already English, tidy it only. "
                          "Answer with the JSON object only, same keys."},
                         {"role": "user", "content": json.dumps(do, ensure_ascii=False)}]}
    async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=10)) as c:
        for url, nagl, b in _cele(body):
            b = {k: v for k, v in b.items() if k != "stream"}
            try:
                r = await c.post(url + "/chat/completions", json=b, headers=nagl)
            except httpx.HTTPError:
                continue
            if r.status_code != 200:
                continue
            t = (r.json()["choices"][0]["message"].get("content") or "").strip()
            j = narzedzia.jako_json(t)
            if j:
                d = json.loads(j)
                return {**puste, **{k: str(d.get(k) or v) for k, v in do.items()}}
    raise HTTPException(502, K("e_json_llm"))


@router.post("/api/karty/prompt")
async def api_karta_prompt(req: Request):
    _need(req)
    d = await req.json()
    typ = d.get("typ")
    if typ not in ("postac", "lokacja"):
        raise HTTPException(400)
    klucze = POSTAC if typ == "postac" else LOKACJA
    pola = {k: str((d.get("pola") or {}).get(k) or "").strip() for k in klucze}
    pola["styl"] = str(d.get("styl") or "").strip()
    en = await _po_angielsku(pola)
    zast = {k: (en.get(k) or "").strip().rstrip(".") or "—" for k in (*klucze, "styl")}
    if not pola["styl"]:
        zast["styl"] = "neutral photographic reference, natural colours"
    wzor = WZOR_POSTACI if typ == "postac" else WZOR_LOKACJI
    prompt = wzor.format(**zast)
    # wiersze bez treści (np. nikt nie podał stroju) wypadają — nic nie dopisujemy
    prompt = "\n".join(l for l in prompt.splitlines() if not re.match(r"^[A-Z]+: —\.?$", l))
    return {"prompt": prompt}


@router.post("/api/karty/zapisz")
async def api_karta_zapisz(req: Request):
    u = _need(req)
    d = await req.json()
    typ = "karta postaci" if d.get("typ") == "postac" else "karta lokacji"
    nazwa = str(d.get("nazwa") or "").strip()[:60] or "bez-nazwy"
    wynik = await narzedzia.wykonaj(u, "zapisz_prompt", {"obszar": "obraz", "nazwa": f"karta-{nazwa}", "jednostka": f"{typ}: {nazwa}",
                                                         "tresc": d.get("prompt") or ""}, prompty.jezyk(req),
                                    {"model": d.get("model"), "biblia": d.get("biblia")})
    return {"ok": narzedzia.udany_zapis(wynik), "info": wynik}
