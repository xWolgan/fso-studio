"""Studio — serwer WWW (FastAPI). Uruchomienie: uvicorn studio.main:app --host <adres> --port 8100"""
import asyncio
import json
import time
import random
import re
import shutil
from pathlib import Path

import markdown as md
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import api, scheduler, store
from .config import CFG, OBSZARY, ROOT, ZASOBY
from .i18n import JEZYKI, K, L, przetlumacz, t
from .registry import MODELS, by_area, lokalnie, wariant

app = FastAPI(title="Studio")
from . import tekst, prompty, ustawienia  # noqa: E402
app.include_router(tekst.router)
app.include_router(prompty.router)
app.include_router(ustawienia.router)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
tpl = Jinja2Templates(directory=ROOT / "templates")
PORADNIKI = ROOT / "poradniki"

def aktywne() -> set[str]:
    """Obszary, w których ta instalacja ma choć jeden model do uruchomienia (reszta: „nieskonfigurowane”)."""
    return {o for o in OBSZARY if by_area(o)}


@app.on_event("startup")
async def startup():
    store.init()
    from .registry import odswiez_chmure
    odswiez_chmure()                              # modele wybrane w Ustawieniach
    asyncio.create_task(scheduler.loop())


JEDEN = store.norm_login(str(CFG.get("uzytkownik") or ""))   # tryb jednego użytkownika: bez logowania


def who(req: Request) -> str | None:
    return store.kto(req.cookies.get("login"))


def lang(req: Request) -> str:
    lg = req.cookies.get("lang")
    return lg if lg in JEZYKI else "pl"


def teksty(lg: str) -> dict:
    """Teksty interfejsu + etykiety wejść modeli („we.<id>”) — do opisu wyniku w każdym obszarze i w galerii."""
    out = t(lg)
    for m in MODELS.values():
        for i in m.wejscia:
            if i.get("etykieta") and "we." + i["id"] not in out:
                out["we." + i["id"]] = re.sub(r"\s*\(.*\)$", "", L(i["etykieta"], lg))
    return out


def page(req: Request, name: str, **ctx):
    lg = lang(req)
    return tpl.TemplateResponse(req, name, {"login": who(req), "lang": lg, "T": t(lg), "jezyki": JEZYKI,
                                            "T_json": json.dumps(teksty(lg), ensure_ascii=False),
                                            "obszary": OBSZARY, "aktywne": aktywne(), "jeden": bool(JEDEN), **ctx})


def need(req: Request) -> str:
    u = who(req)
    if not u:
        raise HTTPException(401, K("e_zaloguj"))
    return u


# --- strony ---

@app.get("/", response_class=HTMLResponse)
async def home(req: Request):
    if not who(req):
        return page(req, "login.html", blad=False)
    return page(req, "home.html")


@app.post("/login")
async def login(req: Request, login: str = Form(...)):
    u = store.norm_login(login)
    if not u:
        return page(req, "login.html", blad=True, wpisany=login)
    if not api.wpusc(u):
        return page(req, "login.html", zamkniete=True, wpisany=login)
    store.user_dir(u)
    r = RedirectResponse("/", status_code=303)
    r.set_cookie("login", u, max_age=60 * 60 * 24 * 30, samesite="lax")
    return r


@app.get("/wyloguj")
async def logout():
    r = RedirectResponse("/", status_code=303)
    r.delete_cookie("login")
    return r


@app.get("/jezyk/{lg}")
async def set_lang(req: Request, lg: str):
    r = RedirectResponse(req.headers.get("referer", "/"), status_code=303)
    r.set_cookie("lang", lg if lg in JEZYKI else "pl", max_age=60 * 60 * 24 * 365, samesite="lax")
    return r


@app.get("/ustawienia", response_class=HTMLResponse)
async def settings(req: Request):
    ustawienia._lokalnie(req)
    return page(req, "ustawienia.html", obszar="ustawienia")


@app.get("/galeria", response_class=HTMLResponse)
async def gallery(req: Request):
    if not who(req):
        return RedirectResponse("/", status_code=303)
    return page(req, "galeria.html")


@app.get("/tablica", response_class=HTMLResponse)
async def board(req: Request):
    if not who(req):
        return RedirectResponse("/", status_code=303)
    return page(req, "tablica.html")


@app.get("/{obszar}", response_class=HTMLResponse)
async def area(req: Request, obszar: str):
    if obszar not in OBSZARY:
        raise HTTPException(404)
    if obszar == "tekst":
        if not who(req):
            return RedirectResponse("/", status_code=303)
        models = [lokalnie({"id": m.id, "nazwa": m.nazwa_w(lang(req)), "opis": m.opis, "uwagi": m.uwagi, "licencja": m.licencja},
                           lang(req)) for m in by_area("tekst")]
        return page(req, "tekst.html", obszar="tekst", models_json=json.dumps(models, ensure_ascii=False))
    if not who(req):
        return RedirectResponse("/", status_code=303)
    models = []
    for m in by_area(obszar):
        d = m.public(lang(req))
        d["poradnik"] = (PORADNIKI / f"{m.poradnik or m.id}.md").exists()
        models.append(d)
    # stare id wariantów (ukrytych) → pozycja + odwrotna mapa wejść: „powtórz” przy dawnych wynikach
    aliasy = {}
    for m in MODELS.values():
        if m.nalezy_do and m.nalezy_do in MODELS and MODELS[m.nalezy_do].obszar == obszar:
            w = next((w for w in MODELS[m.nalezy_do].warianty if w["model"] == m.id), {})
            aliasy[m.id] = {"model": m.nalezy_do, "mapa": {v: k for k, v in w.get("mapa", {}).items()}}
    return page(req, "app.html", obszar=obszar, models_json=json.dumps(models, ensure_ascii=False),
                aliasy_json=json.dumps(aliasy, ensure_ascii=False),
                aktywny=obszar in aktywne())


# --- API: modele, poradniki ---

@app.get("/api/modele")
async def api_models(req: Request, obszar: str):
    return [m.public(lang(req)) for m in by_area(obszar)]


@app.get("/api/poradnik/{model_id}")
async def api_guide(req: Request, model_id: str):
    need(req)
    m = MODELS.get(model_id)
    if not m:
        raise HTTPException(404)
    lg = lang(req)
    name = m.poradnik or m.id
    kandydaci = [PORADNIKI / lg / f"{name}.md"] if lg != "pl" else []
    kandydaci += ([PORADNIKI / "en" / f"{name}.md"] if lg not in ("pl", "en") else []) + [PORADNIKI / f"{name}.md"]
    f = next((x for x in kandydaci if x.exists()), kandydaci[-1])
    if not f.exists():
        raise HTTPException(404, K("e_poradnik"))
    return {"html": md.markdown(f.read_text(encoding="utf-8"), extensions=["fenced_code", "tables"])}


# --- API: ujęcia ---

@app.get("/api/ujecia")
async def api_shots(req: Request):
    return store.ujecia(need(req))


@app.post("/api/ujecia")
async def api_shot_new(req: Request):
    u = need(req)
    d = await req.json()
    return store.create_ujecie(u, d.get("nazwa", ""))


@app.post("/api/ujecia/{uid}")
async def api_shot_rename(req: Request, uid: int):
    u = need(req)
    d = await req.json()
    r = store.rename_ujecie(uid, u, d.get("nazwa", ""))
    if not r:
        raise HTTPException(404)
    return r


# --- API: zadania ---

@app.post("/api/zadania")
async def api_submit(req: Request):
    u = need(req)
    d = await req.json()
    m = MODELS.get(d.get("model"))
    if not m:
        raise HTTPException(400, K("e_model"))
    if d.get("przez_api"):                              # długie zadanie lokalne → ten sam pomysł przez API (z budżetu)
        z = [x for x in api.zapasy(m) if x["model"] in MODELS and (d["przez_api"] is True or x["model"] == d["przez_api"])]
        if not z:
            raise HTTPException(400, K("e_brak_api"))
        m = MODELS[z[0]["model"]]
        d["wartosci"], d["wejscia"], _ = api.przenies(m, z[0]["mapa"], d.get("wartosci") or {}, d.get("wejscia") or {})
    wej = d.get("wejscia", {}) or {}
    for inp in m.wejscia:
        if inp.get("wymagane") and not wej.get(inp["id"]):
            raise HTTPException(400, K("e_brak_wejscia", n=inp["id"]))
        if wej.get(inp["id"]):
            for w in inp.get("wymaga", []):
                if not wej.get(w):
                    raise HTTPException(400, K("e_wymaga", a=inp["id"], b=w))
    if m.backend == "api":
        if not api.endpoint_dla(m, wej):
            raise HTTPException(400, K("e_zestaw_api"))
        if not api.dostepny(m):
            raise HTTPException(503, K("e_api_klucz"))
    else:
        try:
            wariant(m, wej)
        except ValueError as e:
            raise HTTPException(400, str(e))
    ile = max(1, min(4, int(d.get("ile", 1) or 1)))
    koszt = api.koszt_s(m, d.get("wartosci", {}) or {}) if m.backend == "api" else 0.0
    if koszt and store.spent(u) + koszt * ile > api.przydzial(u) + 0.01:
        zostalo = max(0, api.przydzial(u) - store.spent(u))
        raise HTTPException(402, K("e_budzet", k=f"{koszt * ile:g}", z=f"{zostalo:g}"))
    if store.waiting_count(u) + ile > store.LIMIT_CZEKAJACYCH:
        raise HTTPException(429, K("e_limit", n=store.LIMIT_CZEKAJACYCH))
    uj = d.get("ujecie") or store.default_ujecie(u)["id"]
    wartosci = dict(d.get("wartosci", {}))
    for p in m.parametry:
        if p.get("wymagane") and p["typ"] in ("prompt", "tekst") and not str(d.get("wartosci", {}).get(p["id"], "")).strip():
            raise HTTPException(400, K("e_puste_pole", n=p["id"]))
    seed_max = {p["id"]: int(p.get("max", 2**48)) for p in m.parametry if p["typ"] == "seed"}
    seed_ids = list(seed_max)
    base = None
    for sid in seed_ids:
        v = str(wartosci.get(sid, "")).strip()
        if v.isdigit():
            base = int(v)
    ids, grupa = [], None
    for i in range(ile):
        w = dict(wartosci)
        for sid in seed_ids:
            w[sid] = (base + i) if base is not None else random.randint(1, seed_max[sid])
        jid = store.add_job(u, m.obszar, m.id, w, d.get("wejscia", {}), uj, grupa, koszt,
                            round(api.koszt_usd(m, w), 4) if koszt else None)
        if grupa is None and ile > 1:
            grupa = jid
            store.update_job(jid, grupa=jid)
        ids.append(jid)
    return {"ids": ids}


@app.get("/api/zadania")
async def api_jobs(req: Request):
    u = need(req)
    lg = lang(req)
    order = scheduler.queue_order()
    out = []
    for j in store.jobs_visible(u):
        out.append({"id": j["id"], "model": j["model"], "nazwa": MODELS[j["model"]].nazwa_w(lg) if j["model"] in MODELS else j["model"],
                    "obszar": j["obszar"], "status": j["status"], "blad": przetlumacz(j["blad"], lg),
                    "postep": scheduler.progress_of(j), "maszyna": j["maszyna"],
                    "przed": store.queue_position(j["id"], order) if j["status"] == "czeka" else 0,
                    "eta": round(scheduler.PLAN[j["id"]][2] - time.time()) if j["status"] == "czeka" and j["id"] in scheduler.PLAN else None,
                    "wyniki": json.loads(j["wyniki"] or "[]"), "grupa": j["grupa"],
                    "czas": round((j["koniec"] or 0) - (j["start"] or 0), 1) if j["koniec"] and j["start"] else None,
                    "utworzone": j["utworzone"]})
    return out


@app.post("/api/zadania/{jid}/anuluj")
async def api_cancel(req: Request, jid: int):
    u = need(req)
    j = store.job(jid)
    if not j or j["login"] != u:
        raise HTTPException(404)
    if j["status"] == "w_toku" and j.get("maszyna") == "api":
        info = json.loads(j.get("api") or "null")
        if info and not await api.klient(MODELS[j["model"]].dostawca).cancel(info["cancel_url"]):
            raise HTTPException(409, K("e_nie_przerwiesz"))
    if j["status"] in ("czeka", "w_toku"):
        store.update_job(jid, status="anulowane")
    return {"ok": True}


@app.post("/api/zadania/{jid}/zamknij")
async def api_dismiss(req: Request, jid: int):
    u = need(req)
    j = store.job(jid)
    if not j or j["login"] != u:
        raise HTTPException(404)
    store.update_job(jid, zamkniete=1)
    return {"ok": True}


# --- API: zasoby ---

def public_asset(a: dict, lg: str = "pl") -> dict:
    meta = json.loads(a["meta"] or "{}")
    if meta.get("model") in MODELS:
        meta["nazwa_modelu"] = MODELS[meta["model"]].nazwa_w(lg)
    return {"id": a["id"], "login": a["login"], "rodzaj": a["rodzaj"], "zrodlo": a["zrodlo"], "nazwa": a["nazwa"],
            "obszar": a["obszar"], "model": a["model"], "ukryte": bool(a["ukryte"]), "wybrane": bool(a.get("wybrane")),
            "utworzone": a["utworzone"], "ujecie_id": a.get("ujecie_id"), "ujecie_nazwa": a.get("ujecie_nazwa", ""),
            "sciezka": "zasoby/" + a["sciezka"],
            "meta": meta, "url": f"/pliki/{a['id']}"}


@app.get("/api/zasoby")
async def api_assets(req: Request, kto: str = "ja", rodzaj: str | None = None, obszar: str | None = None,
                     ujecie: int | None = None, wybrane: int = 0, q: str = ""):
    u = need(req)
    return [public_asset(a, lang(req)) for a in store.list_assets(u, kto, rodzaj, obszar, ujecie, bool(wybrane), q)]


@app.get("/api/osoby")
async def api_people(req: Request):
    need(req)
    return store.logins()


@app.post("/api/zasoby")
async def api_upload(req: Request, plik: UploadFile = File(...), ujecie: int | None = Form(None)):
    u = need(req)
    name = Path(plik.filename or "plik").name
    ext = Path(name).suffix.lower()
    rodzaj = store.EXT_RODZAJ.get(ext)
    if not rodzaj:
        raise HTTPException(400, K("e_typ_pliku", n=ext))
    d, uid = store.ujecie_dir(u, ujecie)
    dest, i = d / name, 1
    while dest.exists():
        dest, i = d / f"{Path(name).stem}-{i}{ext}", i + 1
    with open(dest, "wb") as f:
        shutil.copyfileobj(plik.file, f)
    aid = store.add_asset(u, rodzaj, "wgrane", dest, dest.name, ujecie_id=uid)
    a = store.asset(aid)
    a["ujecie_nazwa"] = (store.ujecie(uid) or {}).get("nazwa", "")
    return public_asset(a, lang(req))


@app.post("/api/zasoby/{aid}/ukryj")
async def api_hide(req: Request, aid: int, ukryj: bool = True):
    store.set_flag(aid, need(req), "ukryte", ukryj)
    return {"ok": True}


@app.post("/api/zasoby/usun")
async def api_delete(req: Request):
    u = need(req)
    d = await req.json()
    done, skipped = store.delete_assets([int(x) for x in d.get("ids", [])][:200], u)
    return {"usuniete": done, "pominiete": skipped}


@app.post("/api/zasoby/{aid}/wybrane")
async def api_star(req: Request, aid: int, tak: bool = True):
    store.set_flag(aid, need(req), "wybrane", tak)
    return {"ok": True}


@app.post("/api/zasoby/{aid}/przenies")
async def api_move(req: Request, aid: int):
    u = need(req)
    d = await req.json()
    if not store.move_asset(aid, u, int(d.get("ujecie"))):
        raise HTTPException(400, K("e_przeniesc"))
    return {"ok": True}


@app.get("/pliki/{aid}")
async def file(req: Request, aid: int, pobierz: int = 0):
    u = need(req)
    a = store.asset(aid)
    if not a or (a["ukryte"] and a["login"] != u):
        raise HTTPException(404)
    p = ZASOBY / a["sciezka"]
    return FileResponse(p, filename=a["nazwa"] if pobierz else None)


# --- API: budżet i wycena ---

def _budzet(u: str) -> dict:
    przydzial, wydane = api.przydzial(u), store.spent(u)
    return {"przydzial": przydzial, "wydane": round(wydane, 1), "zostalo": round(max(0.0, przydzial - wydane), 1)}


@app.get("/api/budzet")
async def api_budget(req: Request):
    return _budzet(need(req))


@app.post("/api/wycena")
async def api_quote(req: Request):
    """Przed wysłaniem: koszt zadania API albo — dla modelu lokalnego z wersją w API — czas oczekiwania lokalnie
    i koszt alternatywy; GUI pyta wtedy uczestnika, czy czekać (za darmo), czy wysłać przez API (z budżetu)."""
    u = need(req)
    d = await req.json()
    m = MODELS.get(d.get("model"))
    if not m:
        raise HTTPException(400, K("e_model"))
    w, wej = d.get("wartosci", {}) or {}, d.get("wejscia", {}) or {}
    ile = max(1, min(4, int(d.get("ile", 1) or 1)))
    out = {"budzet": _budzet(u), "prog_s": api.PROG_ZADANIA_S, "api": m.backend == "api"}
    if m.backend == "api":
        out.update(koszt_s=api.koszt_s(m, w, ile), dostepne=api.dostepny(m) and bool(api.endpoint_dla(m, wej)))
        return out
    out.update(scheduler.eta_lokalnie(u, m, w) or {})        # eta_s (gotowe za), czas_s (samo zadanie), maszyna
    zapasy = []
    for x in api.zapasy(m):
        z = MODELS.get(x["model"])
        if not z or not api.dostepny(z):
            continue
        wz, wejz, pominiete = api.przenies(z, x["mapa"], w, wej)
        e = api.endpoint_dla(z, wejz)
        if not e:
            continue
        pominiete += [k for k in wejz if k in e.get("ignoruj", [])]
        zapasy.append({"model": z.id, "nazwa": z.nazwa_w(lang(req)), "koszt_s": api.koszt_s(z, wz, ile), "dlugosc_s": api.dlugosc(z, wz),
                       "czas_s": round(api.czas_api(z)), "pominiete": pominiete})
    out["zapasy"] = sorted(zapasy, key=lambda x: len(x["pominiete"]))[:3]   # kolejność z YAML; z pominiętymi wejściami — na koniec
    return out


@app.get("/api/tablica")
async def api_board(req: Request):
    need(req)
    return scheduler.tablica(lang(req))


@app.get("/api/stan")
async def api_state(req: Request):
    need(req)
    return {"maszyny": scheduler.machines_status()}


@app.exception_handler(HTTPException)
async def blad_http(req: Request, e: HTTPException):
    """Komunikaty „@klucz|…” (i18n.K) tłumaczone na język osoby, która je widzi."""
    from fastapi.responses import JSONResponse
    return JSONResponse({"detail": przetlumacz(e.detail, lang(req))}, status_code=e.status_code, headers=getattr(e, "headers", None))
