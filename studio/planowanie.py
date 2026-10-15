"""Szacowanie czasu zadań i wybór maszyny: zadanie idzie tam, gdzie skończy się najwcześniej.

Czas zadania = mediana z historii (ten sam model, ta sama maszyna, te same tryby), przeskalowana
o długość klipu; brak historii → ten sam model na innej maszynie × mnożnik szybkości maszyn → wartość
domyślna obszaru. Do czasu dochodzi przeładowanie modelu (gdy maszyna ma w pamięci inny) i kara
za priorytet (obszar niżej na liście `priorytet` maszyny = maszyna mniej chętnie go bierze).
"""
import json
import statistics
import time

from . import store

DOMYSLNE_S = {"obraz": 25, "wideo": 120, "muzyka": 90, "mowa": 8, "sfx": 10, "tekst": 30}
DOMYSLNA_DLUGOSC = {"wideo": 5, "muzyka": 30, "sfx": 5}
_HIST = {"t": 0.0, "rows": []}


def historia() -> list[dict]:
    """Ukończone zadania z czasem pracy (odświeżane co minutę)."""
    if time.time() - _HIST["t"] > 60:
        with store.db() as c:
            rows = c.execute("""SELECT model, maszyna, wartosci, start, koniec FROM jobs
                                WHERE status='gotowe' AND start IS NOT NULL AND koniec IS NOT NULL
                                ORDER BY id DESC LIMIT 3000""").fetchall()
        _HIST["rows"] = [{"model": r["model"], "maszyna": r["maszyna"], "w": json.loads(r["wartosci"] or "{}"),
                          "s": r["koniec"] - r["start"]} for r in rows if r["koniec"] > r["start"]]
        _HIST["t"] = time.time()
    return _HIST["rows"]


def _podpis(model, w: dict) -> tuple:
    """Ustawienia, które zmieniają czas skokowo: parametry typu tryb (np. szybki/jakość, 480p/720p)."""
    return tuple(str(w.get(p["id"], p.get("domyslnie"))) for p in model.parametry if p["typ"] == "tryb")


def _dlugosc(model, w: dict) -> float | None:
    for p in model.parametry:
        if p["id"] == "dlugosc" or p["typ"] == "dlugosc":
            try:
                return float(w.get(p["id"], p.get("domyslnie")))
            except (TypeError, ValueError):
                return None
    return None


def szacuj(model, wartosci: dict, maszyna, maszyny: dict) -> float:
    """Szacowany czas zadania (s) na danej maszynie, bez przeładowania."""
    pod, dl = _podpis(model, wartosci), _dlugosc(model, wartosci)

    def skaluj(r):
        rd = _dlugosc(model, r["w"])
        return r["s"] * (dl / rd) if dl and rd else r["s"]

    hist = [r for r in historia() if r["model"] == model.id]
    for warunek, mnoznik in (
        (lambda r: r["maszyna"] == maszyna.id and _podpis(model, r["w"]) == pod, lambda r: 1.0),
        (lambda r: _podpis(model, r["w"]) == pod and r["maszyna"] in maszyny,
         lambda r: maszyna.mnoznik / maszyny[r["maszyna"]].mnoznik),
        (lambda r: r["maszyna"] == maszyna.id, lambda r: 1.0),
        (lambda r: r["maszyna"] in maszyny, lambda r: maszyna.mnoznik / maszyny[r["maszyna"]].mnoznik),
    ):
        proby = [skaluj(r) * mnoznik(r) for r in hist if warunek(r)][:15]
        if proby:
            return max(1.0, statistics.median(proby))
    baza = DOMYSLNE_S.get(model.obszar, 60) * maszyna.mnoznik
    if dl and model.obszar in DOMYSLNA_DLUGOSC:
        baza *= dl / DOMYSLNA_DLUGOSC[model.obszar]
    return baza


def kara_priorytetu(maszyna, obszar: str) -> float:
    if not maszyna.priorytet:
        return 0.0
    ranga = maszyna.priorytet.index(obszar) if obszar in maszyna.priorytet else len(maszyna.priorytet)
    return ranga * maszyna.kara_priorytetu


def zaplanuj(oczekujace: list[dict], maszyny: dict, modele: dict, umie) -> tuple[dict, dict]:
    """Symulacja w kolejności sprawiedliwej. Zwraca ({id maszyny: zadanie do uruchomienia teraz},
    {id zadania: (id maszyny, przewidywany start, przewidywany koniec)})."""
    teraz = time.time()
    wolna_od, ostatni = {}, {}
    for m in maszyny.values():
        ostatni[m.id] = m.ostatni_model
        if m.busy:
            jb = store.job(m.busy) or {}
            md = modele.get(jb.get("model"))
            koniec = (jb.get("start") or teraz) + (szacuj(md, json.loads(jb.get("wartosci") or "{}"), m, maszyny) if md else 60)
            wolna_od[m.id] = max(teraz + 5, koniec)
        else:
            wolna_od[m.id] = teraz
    teraz_uruchom, plan = {}, {}
    for job in oczekujace:
        model = modele.get(job["model"])
        if not model:
            continue
        w = json.loads(job["wartosci"] or "{}")
        best = None
        for m in maszyny.values():
            if not (m.ok and umie(m, model)):
                continue
            czas = szacuj(model, w, m, maszyny) + (m.przeladowanie if ostatni[m.id] != model.id else 0)
            ocena = wolna_od[m.id] + czas + kara_priorytetu(m, model.obszar)
            if best is None or ocena < best[0]:
                best = (ocena, m, czas)
        if not best:
            continue
        _, m, czas = best
        start = wolna_od[m.id]
        plan[job["id"]] = (m.id, start, start + czas)
        wolna_od[m.id] = start + czas
        ostatni[m.id] = model.id
        if start <= teraz and m.busy is None and m.id not in teraz_uruchom:
            teraz_uruchom[m.id] = job
    return teraz_uruchom, plan
