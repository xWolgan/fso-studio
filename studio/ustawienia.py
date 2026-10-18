"""Strona Ustawienia: klucze dostawców, katalogi modeli i wybór modeli do obszarów.

Dostępna tylko z tego komputera (127.0.0.1) — klucze nie mogą być widoczne ani zmieniane z sieci.
Wartości kluczy nigdy nie wracają do przeglądarki (tylko: czy klucz jest i czy działa).
"""
from fastapi import APIRouter, HTTPException, Request

from . import dostawcy
from .i18n import K

router = APIRouter()
LOKALNE = {"127.0.0.1", "::1", "localhost"}


def _lokalnie(req: Request):
    # zapytanie przekazane przez proxy (Caddy, nginx…) wygląda na lokalne — takie odrzucamy
    przez_proxy = any(h in req.headers for h in ("x-forwarded-for", "x-real-ip", "forwarded", "x-forwarded-host"))
    if not req.client or req.client.host not in LOKALNE or przez_proxy:
        raise HTTPException(403, K("e_ustawienia_lokalnie"))


def _d(d: str) -> str:
    if d not in dostawcy.DOSTAWCY:
        raise HTTPException(404)
    return d


def _po_zmianie():
    from . import api
    from .registry import odswiez_chmure
    api._KLIENCI.clear()
    odswiez_chmure()


@router.get("/api/ustawienia")
async def stan(req: Request):
    _lokalnie(req)
    return {"dostawcy": _dostawcy(req), "limit_usd": dostawcy.ustawienia().get("limit_usd_miesiac"),
            "comfyui": _comfy_stan()}


def _comfy_stan() -> dict:
    from .komputer import DOMYSLNY
    from .registry import MODELS
    st = dostawcy.ustawienia().get("comfyui") or {}
    nazwa = lambda i: MODELS[i].nazwa if i in MODELS else i
    widoczne = lambda ids: [i for i in ids if i in MODELS and not MODELS[i].ukryty]
    return {"adres": st.get("adres") or "", "domyslny": DOMYSLNY, "info": st.get("info") or "", "ok": bool(st.get("ok")),
            "gotowe": [{"id": i, "nazwa": nazwa(i), "obszar": MODELS[i].obszar} for i in widoczne(st.get("dostepne") or [])],
            "braki": [{"id": i, "nazwa": nazwa(i), "obszar": MODELS[i].obszar, "czego": b[:6], "ile": len(b)}
                      for i, b in (st.get("braki") or {}).items() if i in widoczne([i])]}


@router.post("/api/ustawienia/comfyui")
async def comfyui(req: Request):
    """Zapis adresu ComfyUI i sprawdzenie, które modele lokalne da się uruchomić (pusty adres = wyłączenie)."""
    from . import komputer
    _lokalnie(req)
    adres = str((await req.json()).get("adres") or "").strip().rstrip("/")
    u = dostawcy.ustawienia()
    if not adres:
        u.pop("comfyui", None)
    else:
        if not adres.startswith(("http://", "https://")):
            raise HTTPException(400)
        u["comfyui"] = {"adres": adres, **(await komputer.sprawdz(adres))}
    dostawcy.zapisz_ustawienia(u)
    komputer.zastosuj(u.get("comfyui"))
    return _comfy_stan()


def _dostawcy(req: Request) -> list:
    from .registry import lokalnie
    lg = req.cookies.get("lang") if req.cookies.get("lang") in ("pl", "en", "fr") else "pl"
    out = []
    for d, x in dostawcy.DOSTAWCY.items():
        kat = dostawcy.katalog(d)
        out.append({"id": d, "nazwa": lokalnie(x["nazwa"], lg), "klucz_url": x["klucz_url"], "format": x.get("format"),
                    "adres": x.get("adres"), "adres_teraz": dostawcy.klucz(d) if x.get("adres") else None,   # adres nie jest tajny
                    "ma_klucz": bool(dostawcy.klucz(d)), "katalog_czas": (kat or {}).get("czas"),
                    "liczba": len((kat or {}).get("modele") or []), "wybrane": dostawcy.wybrane(d)})
    return out


@router.post("/api/ustawienia/klucz")
async def klucz(req: Request):
    _lokalnie(req)
    j = await req.json()
    d = _d(j.get("dostawca") or "")
    dostawcy.zapisz_klucz(d, j.get("klucz") or "")
    _po_zmianie()
    ok, info = await dostawcy.sprawdz(d) if dostawcy.klucz(d) else (False, "")
    return {"ok": ok, "info": info, "ma_klucz": bool(dostawcy.klucz(d))}


@router.post("/api/ustawienia/sprawdz")
async def sprawdz(req: Request):
    _lokalnie(req)
    d = _d((await req.json()).get("dostawca") or "")
    ok, info = await dostawcy.sprawdz(d)
    return {"ok": ok, "info": info}


@router.get("/api/ustawienia/katalog")
async def katalog(req: Request, dostawca: str, odswiez: int = 0):
    _lokalnie(req)
    d = _d(dostawca)
    kat = None if odswiez else dostawcy.katalog(d)
    if kat is None:
        try:
            kat = {"modele": await dostawcy.pobierz_katalog(d)}
        except Exception as e:
            raise HTTPException(502, K("e_katalog", m=str(e)[:200]))
    return {"modele": kat["modele"], "wybrane": dostawcy.wybrane(d)}


@router.post("/api/ustawienia/limit")
async def limit(req: Request):
    _lokalnie(req)
    v = (await req.json()).get("usd")
    try:
        v = max(0.0, float(v)) if v not in (None, "") else None
    except (TypeError, ValueError):
        raise HTTPException(400)
    u = dostawcy.ustawienia()
    u["limit_usd_miesiac"] = v
    dostawcy.zapisz_ustawienia(u)
    return {"usd": v}


@router.post("/api/ustawienia/wybor")
async def wybor(req: Request):
    _lokalnie(req)
    j = await req.json()
    d = _d(j.get("dostawca") or "")
    mid = str(j.get("id") or "")
    poz = next((m for m in (dostawcy.katalog(d) or {}).get("modele", []) if m["id"] == mid), None)
    media = d == "fal" or (d in ("openrouter", "openai", "gemini") and poz and poz["obszar"] != "tekst")
    if media and j.get("tak") and not dostawcy.schemat(d, mid):
        try:
            await dostawcy.pobierz_schemat(d, mid)          # parametry modelu → formularz w obszarze
        except Exception as e:
            raise HTTPException(502, K("e_katalog", m=str(e)[:200]))
    dostawcy.ustaw_wybor(d, mid, bool(j.get("tak")))
    _po_zmianie()
    return {"wybrane": dostawcy.wybrane(d)}
