"""Wypełnianie workflow ComfyUI (format API) wartościami z formularza.

Cel parametru to lista selektorów jak w narzędziu test_dymny.py:
  "@<id węzła>.<wejście>"  — jeden węzeł,   "<Klasa>.<wejście>" — wszystkie węzły tej klasy.
"""
import copy
import json
import math
import random

from .config import WORKFLOWS
from .registry import Model
from .i18n import K

# Nazwy opcji węzła ResolutionSelector (ComfyUI) dla naszych proporcji.
RESOLUTION_SELECTOR = {
    "1:1": "1:1 (Square)", "2:3": "2:3 (Portrait Photo)", "3:2": "3:2 (Photo)",
    "3:4": "3:4 (Portrait Standard)", "4:3": "4:3 (Standard)", "9:16": "9:16 (Portrait Widescreen)",
    "16:9": "16:9 (Widescreen)", "21:9": "21:9 (Ultrawide)",
}


def set_target(wf: dict, target: str, value):
    # id węzłów i nazwy klas nie zawierają kropki, nazwy wejść czasem tak (np. sampling_mode.seed)
    sel, _, inp = target.partition(".")
    if sel.startswith("@"):
        node = wf.get(sel[1:])
        if node is None:
            raise KeyError(f"brak węzła {sel[1:]} w workflow")
        node["inputs"][inp] = value
        return
    hit = False
    for n in wf.values():
        if n["class_type"] == sel and inp in n["inputs"]:
            n["inputs"][inp] = value
            hit = True
    if not hit:
        raise KeyError(f"brak węzła klasy {sel} z wejściem {inp}")


def detach(wf: dict, node_id: str):
    """Usuwa węzeł i odłącza wejścia, które z niego korzystały (tylko dla wejść opcjonalnych)."""
    wf.pop(node_id, None)
    for n in wf.values():
        for k in [k for k, v in n["inputs"].items() if isinstance(v, list) and str(v[0]) == node_id]:
            del n["inputs"][k]


def bypass(wf: dict, target: str):
    """Pomija węzeł: odbiorcy jego wyjścia dostają to, co węzeł miał na wejściu <target> = "<id>.<wejście>"."""
    node_id, _, inp = target.partition(".")
    node = wf.pop(node_id, None)
    if node is None:
        return
    src = node["inputs"].get(inp)
    for n in wf.values():
        for k, v in list(n["inputs"].items()):
            if isinstance(v, list) and len(v) == 2 and str(v[0]) == node_id:
                if src is None:
                    del n["inputs"][k]
                else:
                    n["inputs"][k] = src


def _podstaw(x, podst: dict):
    """Podstawia {id}, {i}, {n}, {plik} w szablonie węzła (napisy, listy, słowniki)."""
    if isinstance(x, str):
        for k, v in podst.items():
            x = x.replace(k, v)
        return x
    if isinstance(x, list):
        return [_podstaw(v, podst) for v in x]
    if isinstance(x, dict):
        return {_podstaw(k, podst): _podstaw(v, podst) for k, v in x.items()}
    return x


def dims(aspect: str, megapixels: float, multiple: int) -> tuple[int, int]:
    a, b = (float(x) for x in aspect.split(":"))
    px = megapixels * 1024 * 1024
    h = math.sqrt(px * b / a)
    w = h * a / b
    r = lambda v: max(multiple, int(round(v / multiple)) * multiple)
    return r(w), r(h)


def chosen(model: Model, values: dict, key: str, default):
    """Tryb może podmienić workflow (_workflow) albo endpoint usługi HTTP (_endpoint)."""
    out = default
    for p in model.parametry:
        if p["typ"] == "tryb":
            out = p["opcje_cele"].get(values.get(p["id"], p.get("domyslnie")), {}).get(key, out)
    return out


def build(model: Model, values: dict, uploads: dict) -> tuple[dict, dict]:
    """Zwraca (workflow API, ustawienia faktycznie użyte — do zapisania przy wyniku)."""
    wf = copy.deepcopy(json.loads((WORKFLOWS / chosen(model, values, "_workflow", model.workflow)).read_text(encoding="utf-8")))
    used = apply_params(model, values, lambda t, v: set_target(wf, t, v))

    for inp in model.wejscia:
        name = uploads.get(inp["id"])
        if inp.get("wiele"):
            names = (name if isinstance(name, list) else [name] if name else [])[: int(inp["wiele"])]
            for i, plik in enumerate(names):
                podst = {"{id}": f"{inp['id']}_{i}", "{i}": str(i), "{n}": str(i + 1), "{plik}": plik}
                for nid, node in inp.get("wezly", {}).items():
                    wf[_podstaw(nid, podst)] = _podstaw(copy.deepcopy(node), podst)
                for cel, zrodlo in inp.get("podlacz", {}).items():
                    set_target(wf, _podstaw(cel, podst), _podstaw(copy.deepcopy(zrodlo), podst))
            if names:
                used[inp["id"]] = names
            elif inp.get("wymagane"):
                raise ValueError(K("e_wymagane_wejscie", n=inp["id"]))
            continue
        if name:
            for t in inp["cel"]:
                set_target(wf, t, name)
            used[inp["id"]] = name
        elif inp.get("wymagane"):
            raise ValueError(K("e_wymagane_wejscie", n=inp["id"]))
        else:
            for nid in inp.get("jesli_brak_odlacz", []):
                detach(wf, nid)
            for t in inp.get("jesli_brak_pomin", []):
                bypass(wf, t)

    return wf, used


def build_fields(model: Model, values: dict) -> tuple[dict, dict]:
    """Dla usług HTTP: cel parametru to nazwa pola zapytania. Zwraca (pola, ustawienia użyte)."""
    fields = dict(model.stale or {})
    used = apply_params(model, values, lambda t, v: fields.__setitem__(t, v))
    if "cfg_scale" in fields and "instruction" in fields and not str(fields["instruction"] or "").strip():
        fields["cfg_scale"] = 1.0          # Breeze: bez instrukcji CFG ≠ 1 kończy się błędem usługi (brak gałęzi negatywnej)
    return fields, used


def apply_params(model: Model, values: dict, put) -> dict:
    used = {}
    for p in model.parametry:
        pid, typ = p["id"], p["typ"]
        v = values.get(pid, p.get("domyslnie"))
        if typ == "seed":
            v = int(v) if str(v or "").strip().lstrip("-").isdigit() and int(v) >= 0 else random.randint(1, int(p.get("max", 2**48)))
            for t in p["cel"]:
                put(t, v)
        elif typ == "proporcje":
            if p.get("cel_selektor"):
                for t in p["cel_selektor"]:
                    put(t, RESOLUTION_SELECTOR[v])
                for t in p.get("cel_megapiksele", []):
                    put(t, float(p.get("megapiksele", 1.0)))
            else:
                w, h = dims(v, float(p.get("megapiksele", 1.0)), int(p.get("wielokrotnosc", 16)))
                for t in p["cel_szerokosc"]:
                    put(t, w)
                for t in p["cel_wysokosc"]:
                    put(t, h)
                used["rozdzielczosc"] = f"{w}×{h}"
        elif typ == "dlugosc":
            # sekundy → klatki; klatki: "8n+1" oznacza, że liczba klatek musi mieć postać 8·n+1
            sec = float(v)
            if p.get("int"):
                sec = float(max(1, round(sec)))
            fps = float(values.get(p.get("fps_param", ""), p.get("fps", 24)))
            frames = max(1, round(sec * fps))
            a, b = 1, 0
            if p.get("klatki"):
                f = p["klatki"].replace(" ", "")
                a = int(f.split("n")[0] or 1)
                b = int(f.split("+")[1]) if "+" in f else 0
                frames = max(a + b, round((frames - b) / a) * a + b)
            for t in p.get("cel_klatki", []):
                put(t, frames)
            for t in p.get("cel_sekundy", []):
                put(t, sec)
            for t in p.get("cel_fps", []):
                put(t, fps)
            used["klatki"], used["fps"] = frames, fps
            used["dlugosc_s"] = round(frames / fps, 2)
        elif typ == "tryb":
            for t, tv in p["opcje_cele"].get(v, {}).items():
                if not t.startswith("_"):
                    put(t, tv)
        elif typ in ("liczba", "ulamek"):
            v = (int if typ == "liczba" else float)(v)
            for t in p["cel"]:
                put(t, v)
        elif typ in ("prompt", "tekst", "wybor", "przelacznik", "cechy"):
            if p.get("wymagane") and not str(v or "").strip():
                raise ValueError(K("e_puste", n=pid))
            if p.get("pomin_puste") and (v is None or str(v).strip() == ""):
                used[pid] = v
                continue                                   # pole opcjonalne API: nie wysyłamy pustego
            if p.get("wartosc_typ") and typ in ("tekst", "wybor"):
                try:
                    v = int(float(v)) if p["wartosc_typ"] == "int" else float(v)
                except (TypeError, ValueError):
                    raise ValueError(K("e_puste", n=pid))
            if typ == "przelacznik":
                v = bool(v) if not isinstance(v, str) else v.lower() in ("1", "true", "tak", "on")
            for t in p["cel"]:
                put(t, v if v is not None else "")
        used[pid] = v
    return used
