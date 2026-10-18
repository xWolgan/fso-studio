"""Prompty systemowe jako materiał do badania: każdą część można obejrzeć, zduplikować, edytować
i wybrać jako obowiązującą — osobno w każdej sekcji.

Oryginały: gui/prompty/*.md i gui/prompty/tematy/*.md (edytuje prowadzący; komentarze <!-- --> nie idą do modelu).
Kopie uczestnika: zasoby/<login>/prompty/<id>.md + kopie.json (lista) + wybor.json (sekcja → id kopii).
Udostępnione kopie widzą inni — mogą je obejrzeć i zduplikować (nie używają cudzej kopii wprost).

Sekcje: proces, lustro, poczatek, temat:<klucz>, promptmaker, medium:<obszar>, model:<karta>, pomoc, zasady.
Języki: oryginał polski w gui/prompty/, tłumaczenia w gui/prompty/en/ i gui/prompty/fr/ (te same ścieżki);
brak tłumaczenia → angielski, potem polski. Rozmowa ma swój język (r["jezyk"], z interfejsu przy jej założeniu).
Karty modeli: gui/prompty/modele/<karta>.md, pierwsza linia „<!-- Karta modelu dla promptmakera. modele: id1, id2 -->”.
Biblia utworu: artefakty/*biblia*.md uczestnika; tematy rozpoznawane po nagłówkach „## …”.
"""
import json
import re
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from . import store
from .config import ROOT
from .i18n import JEZYKI, K

router = APIRouter()
PROMPTY = ROOT / "prompty"
STALE = {   # sekcja → (plik oryginału, {język: nazwa})
    "proces": ("proces.md", {"pl": "wspólne: sposób rozmowy", "en": "shared: how to talk", "fr": "commun : manière de converser"}),
    "lustro": ("majeutyka.md", {"pl": "lustro: jak prowadzi", "en": "mirror: how it leads", "fr": "miroir : comment il guide"}),
    "poczatek": ("lustro-poczatek.md", {"pl": "lustro: rozmowa początkowa", "en": "mirror: opening conversation", "fr": "miroir : conversation d’ouverture"}),
    "promptmaker": ("promptmaker.md", {"pl": "promptmaking: jak pracuje", "en": "promptmaking: how it works", "fr": "promptmaking : comment il travaille"}),
    "pomoc": ("pomoc.md", {"pl": "pomoc do Studia", "en": "Studio help", "fr": "aide du Studio"}),
    "zasady": ("zasady.md", {"pl": "zasady twarde", "en": "hard rules", "fr": "règles strictes"}),
}
MEDIA = ("obraz", "wideo", "sfx", "muzyka", "mowa")
NAZWY_MEDIOW = {"obraz": {"pl": "obraz", "en": "image", "fr": "image"}, "wideo": {"pl": "wideo", "en": "video", "fr": "vidéo"},
                "sfx": {"pl": "dźwięk", "en": "sound", "fr": "son"}, "muzyka": {"pl": "muzyka", "en": "music", "fr": "musique"},
                "mowa": {"pl": "mowa", "en": "speech", "fr": "voix"}}
PRZEDROSTKI = {"medium": {"pl": "medium: ", "en": "medium: ", "fr": "médium : "},
               "model": {"pl": "karta modelu: ", "en": "model card: ", "fr": "fiche modèle : "},
               "temat": {"pl": "temat: ", "en": "topic: ", "fr": "thème : "},
               "wlasny": {"pl": "temat własny", "en": "topic: own", "fr": "thème : personnel"}}


def jezyk(req: Request) -> str:
    lg = req.cookies.get("lang")
    return lg if lg in JEZYKI else "pl"


def plik(rel: str, jez: str = "pl") -> Path:
    """Plik promptu w danym języku (gui/prompty/<jez>/<rel>); brak → angielski → polski oryginał."""
    for j in ([jez] if jez != "pl" else []) + (["en"] if jez not in ("pl", "en") else []):
        p = PROMPTY / j / rel
        if p.exists():
            return p
    return PROMPTY / rel


def _need(req: Request) -> str:
    u = store.kto(req.cookies.get("login"))
    if not u:
        raise HTTPException(401, K("e_zaloguj"))
    return u


def czysc(t: str) -> str:
    return re.sub(r"<!--.*?-->", "", t, flags=re.S).strip()


def _aliasy(t: str) -> list[str]:
    m = re.search(r"nagłówki w biblii:\s*(.+?)-->", t, re.S)
    return [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []


def _naglowek(t: str) -> str | None:
    m = re.search(r"^#\s+(.+)$", czysc(t), re.M)
    return m.group(1).strip() if m else None


def aliasy_wszystkie(rel: str) -> list[str]:
    """Nagłówki biblii rozpoznawane dla pliku we wszystkich językach (biblia może być pisana w dowolnym)."""
    out = []
    for p in [PROMPTY / rel] + [PROMPTY / j / rel for j in JEZYKI if j != "pl"]:
        if p.exists():
            t = p.read_text(encoding="utf-8")
            out += _aliasy(t) or [x for x in [_naglowek(t)] if x]
    return list(dict.fromkeys(out))


def tematy(jez: str = "pl") -> list[dict]:
    out = []
    for p in sorted((PROMPTY / "tematy").glob("*.md")):
        if p.name.startswith("_"):
            continue
        pj = plik("tematy/" + p.name, jez)
        nazwa = _naglowek(pj.read_text(encoding="utf-8")) or p.stem
        out.append({"klucz": re.sub(r"^\d+-", "", p.stem), "nazwa": nazwa, "aliasy": aliasy_wszystkie("tematy/" + p.name) or [nazwa],
                    "plik": pj})
    return out


def karty() -> dict[str, str]:
    """id modelu ze Studia → nazwa pliku karty (bez .md)."""
    out = {}
    for p in sorted((PROMPTY / "modele").glob("*.md")):
        m = re.search(r"modele:\s*(.+?)-->", p.read_text(encoding="utf-8")[:500], re.S)
        for mid in (x.strip() for x in (m.group(1).split(",") if m else [])):
            if mid:
                out[mid] = p.stem
    return out


def _oryginal(sekcja: str, jez: str = "pl") -> Path:
    if sekcja in STALE:
        return plik(STALE[sekcja][0], jez)
    if sekcja.startswith("medium:") and sekcja[7:] in MEDIA:
        return plik(f"media/{sekcja[7:]}.md", jez)
    if sekcja.startswith("model:") and re.fullmatch(r"[0-9a-z._-]+", sekcja[6:]):
        if (PROMPTY / "modele" / f"{sekcja[6:]}.md").exists():
            return plik(f"modele/{sekcja[6:]}.md", jez)
    if sekcja.startswith("temat:"):
        k = sekcja[6:]
        for t in tematy(jez):
            if t["klucz"] == k:
                return t["plik"]
        if k == "_inny":
            return plik("tematy/_inny.md", jez)
    raise HTTPException(404, K("e_sekcja"))


def nazwa_sekcji(sekcja: str, jez: str = "pl") -> str:
    if sekcja in STALE:
        return STALE[sekcja][1].get(jez) or STALE[sekcja][1]["pl"]
    if sekcja == "temat:_inny":
        return PRZEDROSTKI["wlasny"][jez]
    if sekcja.startswith("medium:"):
        return PRZEDROSTKI["medium"][jez] + NAZWY_MEDIOW.get(sekcja[7:], {}).get(jez, sekcja[7:])
    if sekcja.startswith("model:"):
        return PRZEDROSTKI["model"][jez] + (_naglowek(_oryginal(sekcja, jez).read_text(encoding="utf-8")) or sekcja[6:])
    k = sekcja[6:]
    n = next((t["nazwa"] for t in tematy(jez) if t["klucz"] == k), k)
    return PRZEDROSTKI["temat"][jez] + n


# --- kopie uczestnika ---

def _dir(login: str) -> Path:
    return store.user_dir(login, "prompty")


def _czytaj_json(p: Path, dom):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return dom


def kopie(login: str) -> list[dict]:
    return _czytaj_json(_dir(login) / "kopie.json", [])


def _zapisz_kopie(login: str, ks: list[dict]):
    (_dir(login) / "kopie.json").write_text(json.dumps(ks, ensure_ascii=False, indent=1), encoding="utf-8")


def wybor(login: str) -> dict:
    return _czytaj_json(_dir(login) / "wybor.json", {})


def _zapisz_wybor(login: str, w: dict):
    (_dir(login) / "wybor.json").write_text(json.dumps(w, ensure_ascii=False, indent=1), encoding="utf-8")


def _kopia(login: str, kid: str) -> dict:
    if not re.fullmatch(r"[0-9a-z-]{6,40}", kid or ""):
        raise HTTPException(400, K("e_id"))
    k = next((k for k in kopie(login) if k["id"] == kid), None)
    if not k:
        raise HTTPException(404)
    return k


def tresc(login: str, sekcja: str, temat_nazwa: str | None = None, jez: str = "pl") -> str:
    """Obowiązująca treść sekcji dla uczestnika: wybrana kopia albo oryginał w języku rozmowy
    (bez komentarzy i bez tytułu „# …”)."""
    kid = wybor(login).get(sekcja)
    p = _dir(login) / f"{kid}.md" if kid else None
    t = p.read_text(encoding="utf-8") if p and p.exists() else _oryginal(sekcja, jez).read_text(encoding="utf-8")
    t = re.sub(r"\A#\s+[^\n]*\n", "", czysc(t)).strip()
    return t.replace("{temat}", temat_nazwa or "") if temat_nazwa is not None else t


def udostepnione(login: str) -> list[dict]:
    out = []
    for p in sorted(store.ZASOBY.glob("*/prompty/kopie.json")):
        kto = p.parent.parent.name
        if kto == login:
            continue
        for k in _czytaj_json(p, []):
            if k.get("udostepniona"):
                out.append({**k, "login": kto})
    return out


# --- biblia ---

def biblie(login: str) -> list[dict]:
    a = store.user_dir(login, "artefakty")
    return [{"sciezka": "artefakty/" + str(p.relative_to(a)).replace("\\", "/"), "nazwa": p.stem}
            for p in sorted(a.rglob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True) if "biblia" in p.name.lower()]


def plik_biblii(login: str, sciezka: str) -> Path | None:
    korzen = (store.ZASOBY / login).resolve()
    p = (korzen / (sciezka or "")).resolve()
    a = (korzen / "artefakty").resolve()
    return p if p.suffix == ".md" and a in p.parents and p.exists() else None


def _pasuje(naglowek: str, aliasy: list[str]) -> bool:
    n = naglowek.lower()
    return any(n.startswith(a.lower()) for a in aliasy)


def stan_biblii(login: str, sciezka: str, jez: str = "pl") -> dict:
    p = plik_biblii(login, sciezka)
    if not p:
        raise HTTPException(404, K("e_biblia"))
    nagl = [h.strip() for h in re.findall(r"^##\s+(.+)$", p.read_text(encoding="utf-8"), re.M)]
    ts = tematy(jez)
    pocz = aliasy_wszystkie(STALE["poczatek"][0])
    return {"sciezka": sciezka, "nazwa": p.stem,
            "tematy": [{"klucz": t["klucz"], "nazwa": t["nazwa"], "wypelniony": any(_pasuje(h, t["aliasy"]) for h in nagl)} for t in ts],
            "wlasne": [h for h in nagl if not any(_pasuje(h, t["aliasy"]) for t in ts) and not _pasuje(h, pocz)]}


def sekcje_rozmowy(r: dict) -> list[str]:
    s = ["proces"]
    if r.get("tryb") == "prompt":
        from .registry import MODELS
        m = MODELS.get(r.get("model_docelowy") or "")
        s.append("promptmaker")
        if m and m.obszar in MEDIA:
            s.append(f"medium:{m.obszar}")
            k = karty().get(m.id)
            if k:
                s.append(f"model:{k}")
        return s + ["zasady"]
    if r.get("tryb") == "lustro":
        s += ["lustro", f"temat:{r['temat']}" if r.get("temat") else "poczatek"]
    return s + ["pomoc", "zasady"]


# --- API ---

def _opis(login: str, sekcja: str, jez: str, inne: list[dict]) -> dict:
    return {"sekcja": sekcja, "nazwa": nazwa_sekcji(sekcja, jez), "wybrana": wybor(login).get(sekcja),
            "kopie": [{"id": k["id"], "nazwa": k["nazwa"], "udostepniona": bool(k.get("udostepniona"))}
                      for k in kopie(login) if k["sekcja"] == sekcja],
            "udostepnione": [{"login": k["login"], "id": k["id"], "nazwa": k["nazwa"]} for k in inne if k["sekcja"] == sekcja]}


@router.get("/api/prompty")
async def lista(req: Request, tryb: str = "rozmowa", temat: str = "", model: str = ""):
    u = _need(req)
    inne = udostepnione(u)
    return [_opis(u, s, jezyk(req), inne) for s in sekcje_rozmowy({"tryb": tryb, "temat": temat or None, "model_docelowy": model or None})]


@router.get("/api/promptmaker/modele")
async def modele_docelowe(req: Request):
    """Modele, dla których promptmaker pisze prompty — pogrupowane po obszarach; z informacją, czy jest karta."""
    _need(req)
    from .registry import by_area
    jez = jezyk(req)
    k = karty()
    return [{"obszar": o, "nazwa": NAZWY_MEDIOW[o][jez],
             "modele": [{"id": m.id, "nazwa": m.nazwa_w(jez), "karta": m.id in k} for m in by_area(o)]} for o in MEDIA]


@router.get("/api/prompty/tekst")
async def tekst(req: Request, sekcja: str, kopia: str = "", login: str = ""):
    u = _need(req)
    if not kopia:
        return {"tresc": _oryginal(sekcja, jezyk(req)).read_text(encoding="utf-8"), "nazwa": nazwa_sekcji(sekcja, jezyk(req))}
    kto = store.norm_login(login) or u
    k = _kopia(kto, kopia)
    if kto != u and not k.get("udostepniona"):
        raise HTTPException(404)
    return {"tresc": (_dir(kto) / f"{k['id']}.md").read_text(encoding="utf-8"), "nazwa": k["nazwa"]}


@router.post("/api/prompty/duplikuj")
async def duplikuj(req: Request):
    """Nowa kopia z oryginału albo z kopii (własnej lub udostępnionej) — od razu wybrana jako obowiązująca."""
    u = _need(req)
    d = await req.json()
    sekcja = d.get("sekcja") or ""
    _oryginal(sekcja)
    zrodlo = await tekst(req, sekcja, d.get("kopia") or "", d.get("login") or "")
    kid = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    (_dir(u) / f"{kid}.md").write_text(czysc(zrodlo["tresc"]) + "\n", encoding="utf-8")
    ks = kopie(u)
    ks.append({"id": kid, "sekcja": sekcja, "nazwa": (d.get("nazwa") or "").strip()[:80] or {"pl": "moja wersja", "en": "my version", "fr": "ma version"}[jezyk(req)] + f" {len(ks) + 1}",
               "z": d.get("login") or None, "udostepniona": False, "utworzona": time.time()})
    _zapisz_kopie(u, ks)
    w = wybor(u); w[sekcja] = kid; _zapisz_wybor(u, w)
    return {"id": kid}


@router.post("/api/prompty/kopia/{kid}")
async def zmien(req: Request, kid: str):
    u = _need(req)
    k = _kopia(u, kid)
    d = await req.json()
    if "tresc" in d:
        (_dir(u) / f"{kid}.md").write_text(d["tresc"] or "", encoding="utf-8")
    ks = kopie(u)
    for x in ks:
        if x["id"] == k["id"]:
            if "nazwa" in d:
                x["nazwa"] = (d["nazwa"] or "").strip()[:80] or x["nazwa"]
            if "udostepniona" in d:
                x["udostepniona"] = bool(d["udostepniona"])
    _zapisz_kopie(u, ks)
    return {"ok": True}


@router.post("/api/prompty/kopia/{kid}/usun")
async def usun(req: Request, kid: str):
    u = _need(req)
    _kopia(u, kid)
    _zapisz_kopie(u, [x for x in kopie(u) if x["id"] != kid])
    (_dir(u) / f"{kid}.md").unlink(missing_ok=True)
    _zapisz_wybor(u, {s: v for s, v in wybor(u).items() if v != kid})
    return {"ok": True}


@router.post("/api/prompty/wybierz")
async def wybierz(req: Request):
    u = _need(req)
    d = await req.json()
    sekcja, kid = d.get("sekcja") or "", d.get("id") or None
    _oryginal(sekcja)
    if kid:
        _kopia(u, kid)
    w = wybor(u)
    if kid:
        w[sekcja] = kid
    else:
        w.pop(sekcja, None)
    _zapisz_wybor(u, w)
    return {"ok": True}


@router.get("/api/biblie")
async def api_biblie(req: Request):
    return biblie(_need(req))


@router.get("/api/biblia")
async def api_biblia(req: Request, sciezka: str):
    return stan_biblii(_need(req), sciezka, jezyk(req))
