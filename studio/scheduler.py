"""Dyspozytor: przydziela zadania maszynom według ról i prowadzi je do końca.

Kolejka sprawiedliwa (po kolei osobami), na maszynie jedno zadanie naraz (wspólna pamięć GPU),
maszyna musi mieć rolę obszaru zadania. Silniki: ComfyUI albo prosta usługa HTTP (backend: http).
Wybór maszyny: tam, gdzie zadanie skończy się najwcześniej (planowanie.py).
"""
import asyncio
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from . import store
from .backends.comfy import Comfy
from .backends.http import Service
from .config import CFG, ZASOBY
from .registry import MODELS, wariant
from .workflow import build, build_fields, chosen
from . import planowanie
from . import api
from .i18n import K


class Machine:
    def __init__(self, cfg: dict):
        self.id = cfg["id"]
        self.nazwa = cfg.get("nazwa") or cfg["id"]                    # na tablicy
        self.opis = cfg.get("opis") or ""
        self.role = set(cfg.get("role", []))
        self.comfy = Comfy(cfg["comfyui"])
        self.uslugi = {k: Service(v) for k, v in (cfg.get("uslugi") or {}).items()}
        self.busy: int | None = None
        self.ok = True
        self.mnoznik = float(cfg.get("mnoznik_czasu", 1.0))          # czas względem Sparka (Lenovo ~0,42)
        self.przeladowanie = float(cfg.get("przeladowanie_s", 30))    # koszt zmiany modelu w pamięci
        self.priorytet = list(cfg.get("priorytet") or [])             # obszary od najważniejszego
        self.kara_priorytetu = float(cfg.get("kara_priorytetu_s", 45))
        self.modele = cfg.get("modele")                               # opcjonalnie: tylko te modele (id)
        self.ostatni_model: str | None = None


def umie(m: "Machine", model) -> bool:
    if model.backend == "api":                                     # zadania API nie zajmują maszyn
        return False
    if model.obszar not in m.role:
        return False
    if m.modele is not None and model.id not in m.modele:
        return False
    if model.backend == "http":
        return (model.usluga or "") in m.uslugi
    return True


PLAN: dict[int, tuple] = {}   # id zadania -> (maszyna, przewidywany start, przewidywany koniec)


MACHINES: dict[str, Machine] = {m["id"]: Machine(m) for m in CFG["maszyny"]}


def progress_of(job: dict) -> float:
    m = MACHINES.get(job.get("maszyna") or "")
    if m and job.get("prompt_id"):
        return m.comfy.progress.get(job["prompt_id"], job.get("postep") or 0)
    return job.get("postep") or 0


async def run(job: dict, m: Machine):
    jid = job["id"]
    model = MODELS[job["model"]]
    t0 = time.time()
    store.update_job(jid, status="w_toku", maszyna=m.id, start=t0)
    m.ostatni_model = model.id
    try:
        if model.backend == "http":
            await run_http(job, m, model, t0)
            return
        wejscia = json.loads(job["wejscia"])
        pozycja = model
        model, wejscia = wariant(model, wejscia)          # jedna pozycja na model → właściwy wariant
        uploads, input_names = {}, {}
        # nazwy wejść w opisie wyniku — takie, jak na pozycji (np. klatka_start zamiast „obraz” wariantu)
        mapa = next((w.get("mapa", {}) for w in pozycja.warianty if w["model"] == model.id), {})
        nazwa_poz = {v: k for k, v in mapa.items()}
        for inp_id, val in wejscia.items():
            names, opisy = [], []
            for asset_id in (val if isinstance(val, list) else [val]):
                a = store.asset(int(asset_id))
                if not a:
                    raise ValueError(K("e_brak_zasobu", n=asset_id))
                path = ZASOBY / a["sciezka"]
                names.append(await m.comfy.upload(path, f"{a['login']}_{a['id']}{path.suffix}"))
                opisy.append({"id": a["id"], "nazwa": a["nazwa"], "autor": a["login"]})
            uploads[inp_id] = names if isinstance(val, list) else names[0]
            pid = nazwa_poz.get(inp_id, inp_id)
            if isinstance(val, list):
                for k, o in enumerate(opisy):
                    input_names[f"{pid} {k + 1}"] = o
            else:
                input_names[pid] = opisy[0]
        wf, used = build(model, json.loads(job["wartosci"]), uploads)
        if pozycja is not model:
            used["wariant"] = model.nazwa
        pid = await m.comfy.submit(wf)
        store.update_job(jid, prompt_id=pid)
        while True:
            await asyncio.sleep(1)
            h = await m.comfy.history(pid)
            if h and h.get("status", {}).get("completed"):
                break
            if h and h.get("status", {}).get("status_str") == "error":
                msgs = [x[1].get("exception_message", "") for x in h["status"].get("messages", [])
                        if x[0] == "execution_error"]
                raise RuntimeError(K("e_comfy", m="; ".join(msgs) or "?"))
            if (store.job(jid) or {}).get("status") == "anulowane":
                await m.comfy.interrupt()
                return
        files = await m.comfy.outputs(pid)
        if not files:
            raise RuntimeError(K("e_comfy_pliki"))
        seed = used.get("seed", "")
        order = [str(w["wezel"]) for w in model.wyjscia]
        dopiski = {str(w["wezel"]): w.get("dopisek", "") for w in model.wyjscia}
        files.sort(key=lambda f: order.index(f["wezel"]) if f["wezel"] in order else len(order))
        dests = []
        for f in files:
            dest, uid = store.result_path(job["login"], job.get("ujecie_id"), model.obszar, model.id, seed,
                                          Path(f["filename"]).suffix.lower(), dopiski.get(f["wezel"], ""))
            await m.comfy.download(f, dest)
            dests.append((dest, uid))
        finish(job, m, pozycja, used, input_names, t0, dests)
    except Exception as e:
        traceback.print_exc()
        store.update_job(jid, status="blad", koniec=time.time(), blad=str(e)[:800])
    finally:
        m.busy = None


def finish(job: dict, m: Machine, model, used: dict, input_names: dict, t0: float, dests: list):
    """Zapis wyników: plik opisu .json obok każdego pliku, wpis w bazie, zadanie gotowe."""
    jid = job["id"]
    dt = round(time.time() - t0, 1)
    ids = []
    for dest, uid in dests:
        meta = {"model": model.id, "nazwa_modelu": model.nazwa, "obszar": model.obszar,
                "ustawienia": used, "wejscia": input_names, "czas_s": dt, "maszyna": m.id,
                "data": datetime.now().isoformat(timespec="seconds"), "autor": job["login"], "zadanie": jid,
                "grupa": job.get("grupa")}
        dest.with_suffix(dest.suffix + ".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                                           encoding="utf-8")
        rodzaj = store.EXT_RODZAJ.get(dest.suffix.lower(), model.wyjscie)
        ids.append(store.add_asset(job["login"], rodzaj, "wynik", dest, dest.name, model.obszar, model.id,
                                   jid, meta, ujecie_id=uid))
    store.update_job(jid, status="gotowe", koniec=time.time(), postep=1, wyniki=json.dumps(ids))


async def run_http(job: dict, m: Machine, model, t0: float):
    svc = m.uslugi.get(model.usluga or "")
    if not svc:
        raise RuntimeError(K("e_usluga", m=m.id, u=model.usluga))
    values = json.loads(job["wartosci"])
    fields, used = build_fields(model, values)
    files, input_names = {}, {}
    wejscia = json.loads(job["wejscia"])
    for inp in model.wejscia:
        aid = wejscia.get(inp["id"])
        if not aid:
            if inp.get("wymagane"):
                raise ValueError(K("e_wymagane_wejscie", n=inp["id"]))
            continue
        a = store.asset(int(aid))
        if not a:
            raise ValueError(K("e_brak_zasobu", n=aid))
        cel = inp["cel"][0] if isinstance(inp["cel"], list) else inp["cel"]
        files[cel] = ZASOBY / a["sciezka"]
        input_names[inp["id"]] = {"id": a["id"], "nazwa": a["nazwa"], "autor": a["login"]}
        used[inp["id"]] = a["nazwa"]
    endpoint = chosen(model, values, "_endpoint", model.endpoint)
    r = await svc.call(endpoint, model.format, fields, files)
    if (store.job(job["id"]) or {}).get("status") == "anulowane":
        return
    seed = used.get("seed", "")
    dests = []

    def dest_for(ext):
        d = store.result_path(job["login"], job.get("ujecie_id"), model.obszar, model.id, seed, ext)
        dests.append(d)
        return d[0]
    keys = model.pliki or ["plik"]
    await svc.results(r, model.odpowiedz, keys, dest_for)
    if not dests:
        raise RuntimeError(K("e_usluga_pliki"))
    finish(job, m, model, used, input_names, t0, dests)


# --- zadania przez API (HiggsField): bez maszyn, kilka naraz, śledzone także po restarcie Studia ---

API_W_TOKU: set[int] = set()


def _plik_zasobu(aid: int):
    a = store.asset(aid)
    if not a:
        raise ValueError(K("e_brak_zasobu", n=aid))
    return ZASOBY / a["sciezka"], {"id": a["id"], "nazwa": a["nazwa"], "autor": a["login"]}


async def run_api(job: dict):
    jid = job["id"]
    model = MODELS[job["model"]]
    t0 = job.get("start") or time.time()
    try:
        hf = api.klient(model.dostawca)
        info = json.loads(job.get("api") or "null")
        if not info:
            store.update_job(jid, status="w_toku", maszyna="api", start=t0)
            endpoint, args, used, opisy = await api.przygotuj(hf, model, json.loads(job["wartosci"]),
                                                             json.loads(job["wejscia"]), _plik_zasobu)
            if (store.job(jid) or {}).get("status") == "anulowane":
                return
            info = await hf.submit(endpoint, args, api.idempotency(jid))
            info.update(used=used, wejscia=opisy)
            store.update_job(jid, api=json.dumps(info, ensure_ascii=False), prompt_id=info["request_id"])
        opoznienie = 3.0
        while True:
            await asyncio.sleep(opoznienie)
            opoznienie = min(opoznienie * 1.3, 10.0)
            d = await hf.status(info["status_url"])
            st = d.get("status")
            if (store.job(jid) or {}).get("status") == "anulowane":
                if st == "queued":
                    await hf.cancel(info["cancel_url"])
                return
            if st in ("queued", "in_progress"):
                store.update_job(jid, postep=0.05 if st == "queued" else 0.5)
                continue
            if st == "completed":
                break
            if st == "nsfw":
                raise RuntimeError(K("e_moderacja"))
            if st == "canceled":
                store.update_job(jid, status="anulowane", koniec=time.time())
                return
            raise RuntimeError(K("e_api_nieudane", m=str(d.get("error") or st)[:300]))
        url = api.wynik_url(d)
        if not url:
            raise RuntimeError(K("e_api_brak_pliku"))
        used = info.get("used") or {}
        if url.startswith("data:"):                    # wynik od razu w odpowiedzi (np. OpenRouter /images)
            typ = url[5:].split(";", 1)[0]
            ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp", "image/svg+xml": ".svg", "audio/mpeg": ".mp3",
                   "audio/mp3": ".mp3", "audio/wav": ".wav", "audio/x-wav": ".wav", "audio/ogg": ".ogg", "audio/flac": ".flac",
                   "audio/pcm": ".wav", "video/mp4": ".mp4"}.get(typ, ".bin")
        else:
            ext = Path(url.split("?")[0]).suffix.lower() or ".mp4"
        dest, uid = store.result_path(job["login"], job.get("ujecie_id"), model.obszar, model.id, used.get("seed", ""), ext)
        await hf.download(url, dest)
        nazwa = "api:" + (model.dostawca or "")
        finish(job, SimpleNamespace(id=nazwa), model, used, info.get("wejscia") or {}, t0, [(dest, uid)])
    except Exception as e:
        traceback.print_exc()
        store.update_job(jid, status="blad", koniec=time.time(), blad=str(e)[:800])
    finally:
        API_W_TOKU.discard(jid)


def start_api(pending: list[dict]):
    """Startuje oczekujące zadania API (do limitu równoległości dostawcy)."""
    for job in pending:
        model = MODELS[job["model"]]
        limit = int(api.DOSTAWCY.get(model.dostawca or "", {}).get("rownolegle", 10))
        if job["id"] in API_W_TOKU or len(API_W_TOKU) >= limit:
            continue
        API_W_TOKU.add(job["id"])
        asyncio.create_task(run_api(job))


LAST_START: dict[str, float] = {}   # login -> kiedy ostatnio ruszyło jego zadanie


def fair_order(pending: list[dict]) -> list[dict]:
    """Sprawiedliwa kolejność: po kolei osobami (round-robin), w obrębie osoby — według zgłoszenia."""
    by_user: dict[str, list[dict]] = {}
    for j in pending:
        by_user.setdefault(j["login"], []).append(j)
    running = {}
    for m in MACHINES.values():
        if m.busy:
            jb = store.job(m.busy)
            if jb:
                running[jb["login"]] = running.get(jb["login"], 0) + 1
    users = sorted(by_user, key=lambda u: (running.get(u, 0), LAST_START.get(u, 0), by_user[u][0]["id"]))
    out, i = [], 0
    while any(by_user[u] for u in users):
        for u in users:
            if by_user[u]:
                out.append(by_user[u].pop(0))
    return out


def queue_order() -> list[int]:
    return [j["id"] for j in fair_order(store.pending_jobs())]


async def loop():
    for m in MACHINES.values():
        asyncio.create_task(m.comfy.listen())
    for job in store.api_jobs_running():                # zadania API sprzed restartu: śledzimy dalej
        API_W_TOKU.add(job["id"])
        asyncio.create_task(run_api(job))
    tick = 0
    while True:
        if tick % 10 == 0:
            for m in MACHINES.values():
                m.ok = await m.comfy.alive()
        pending, pending_api = [], []
        for job in fair_order(store.pending_jobs()):
            if job["model"] not in MODELS:
                store.update_job(job["id"], status="blad", blad=K("e_model"))
            elif MODELS[job["model"]].backend == "api":
                pending_api.append(job)
            else:
                pending.append(job)
        try:
            teraz, plan = planowanie.zaplanuj(pending, MACHINES, MODELS, umie)
            PLAN.clear(); PLAN.update(plan)
        except Exception:
            traceback.print_exc()
            teraz = {}
        start_api(pending_api)
        for mid, job in teraz.items():
            m = MACHINES[mid]
            m.busy = job["id"]
            LAST_START[job["login"]] = time.time()
            asyncio.create_task(run(job, m))
        tick += 1
        await asyncio.sleep(1)


def eta_lokalnie(login: str, model, wartosci: dict) -> dict | None:
    """Nowe zadanie lokalne w symulacji kolejki (na końcu): {eta_s: za ile gotowe, czas_s: ile trwa samo, maszyna}."""
    pending = [j for j in fair_order(store.pending_jobs() + [
        {"id": 10**12, "login": login, "model": model.id, "wartosci": json.dumps(wartosci)}])
        if j["model"] in MODELS and MODELS[j["model"]].backend != "api"]
    try:
        _, plan = planowanie.zaplanuj(pending, MACHINES, MODELS, umie)
    except Exception:
        traceback.print_exc()
        return None
    if 10**12 not in plan:
        return None
    mid, start, koniec = plan[10**12]
    return {"eta_s": round(koniec - time.time()), "czas_s": round(koniec - start), "maszyna": mid}


def _opis(model, w: dict) -> str:
    """Krótko, bez promptu: długość, rozdzielczość, tryb."""
    out = []
    for p in model.parametry:
        if p["typ"] == "dlugosc":
            out.append(f"{w.get(p['id'], p.get('domyslnie'))} s")
        elif p["id"] in ("rozdzielczosc", "tryb"):
            out.append(str(w.get(p["id"], p.get("domyslnie"))))
    return " · ".join(x for x in out if x and x != "None")


def tablica(lg: str = "pl") -> dict:
    """Duży ekran: co się generuje gdzie, kolejka lokalna z przewidywaniem, API, ostatnio gotowe. Bez promptów."""
    teraz = time.time()

    def pozycja(j: dict) -> dict:
        md = MODELS.get(j["model"])
        w = json.loads(j.get("wartosci") or "{}")
        return {"id": j["id"], "login": j["login"], "model": md.nazwa_w(lg) if md else j["model"],
                "obszar": md.obszar if md else j.get("obszar"), "opis": _opis(md, w) if md else ""}

    maszyny = []
    for m in MACHINES.values():
        d = {"id": m.id, "nazwa": m.nazwa, "opis": m.opis, "ok": m.ok, "role": sorted(m.role), "zadanie": None}
        jb = store.job(m.busy) if m.busy else None
        if jb:
            md = MODELS.get(jb["model"])
            szac = planowanie.szacuj(md, json.loads(jb.get("wartosci") or "{}"), m, MACHINES) if md else None
            d["zadanie"] = pozycja(jb) | {"start": jb.get("start"), "koniec": (jb.get("start") or teraz) + szac if szac else None}
        maszyny.append(d)
    kolejka = []
    for j in fair_order([j for j in store.pending_jobs() if MODELS.get(j["model"]) and MODELS[j["model"]].backend != "api"]):
        p = PLAN.get(j["id"])
        kolejka.append(pozycja(j) | {"maszyna": p[0] if p else None, "start": p[1] if p else None, "koniec": p[2] if p else None})
    with store.db() as c:
        api_rows = [dict(r) for r in c.execute("SELECT * FROM jobs WHERE status IN ('czeka','w_toku') ORDER BY id").fetchall()
                    if MODELS.get(r["model"]) and MODELS[r["model"]].backend == "api"]
        gotowe = [dict(r) for r in c.execute("""SELECT * FROM jobs WHERE status='gotowe' AND koniec IS NOT NULL
                                               ORDER BY koniec DESC LIMIT 10""").fetchall()]
    w_api = [pozycja(j) | {"start": j.get("start"), "status": j["status"]} for j in api_rows]
    ostatnie = [pozycja(j) | {"maszyna": "api" if (j.get("maszyna") or "").startswith("api") else j.get("maszyna"),
                              "czas": round(j["koniec"] - j["start"]) if j.get("start") else None, "koniec": j["koniec"]}
                for j in gotowe]
    return {"teraz": teraz, "maszyny": maszyny, "kolejka": kolejka, "api": w_api, "ostatnie": ostatnie}


def machines_status() -> list[dict]:
    return [{"id": m.id, "role": sorted(m.role), "priorytet": m.priorytet, "ok": m.ok, "zajeta": m.busy,
             "model_w_pamieci": m.ostatni_model} for m in MACHINES.values()]
