"""ComfyUI na tym komputerze — ustawiany w Ustawieniach (adres), bez edycji config.yaml.

Sprawdzenie: ComfyUI podaje swoje węzły (/object_info) i pliki modeli (/models/<katalog>); Studio porównuje je z tym,
czego potrzebuje każdy model lokalny (workflowy z modele/*/*.yaml) i włącza tylko te, które da się uruchomić.
Wynik trafia do zasoby/ustawienia.json → "comfyui" i od razu do dyspozytora jako maszyna „komputer”.
"""
import json
import re
import time
from pathlib import Path

import httpx
import yaml

from .config import MODELE, WORKFLOWS

ROZSZERZENIA = (".safetensors", ".gguf", ".ckpt", ".pt", ".pth", ".bin", ".sft")
DOMYSLNY = "http://127.0.0.1:8188"


def _workflowy(o) -> list[str]:
    if isinstance(o, dict):
        return [x for v in o.values() for x in _workflowy(v)]
    if isinstance(o, list):
        return [x for v in o for x in _workflowy(v)]
    return [o] if isinstance(o, str) and o.endswith(".api.json") else []


def _potrzeby(rel: str) -> tuple[set, set] | None:
    """(pliki modeli, klasy węzłów) z workflowu; None, gdy workflowu nie ma w repo."""
    p = Path(WORKFLOWS) / rel
    if not p.exists():
        return None
    wf = json.loads(p.read_text(encoding="utf-8"))
    pliki, klasy = set(), set()
    for n in wf.values():
        if not isinstance(n, dict):
            continue
        klasy.add(n.get("class_type", ""))
        for v in (n.get("inputs") or {}).values():
            if isinstance(v, str) and v.lower().endswith(ROZSZERZENIA):
                pliki.add(v.replace("\\", "/"))
    return pliki, klasy


async def sprawdz(adres: str) -> dict:
    """Pyta ComfyUI i zwraca {ok, info, gpu, dostepne: [id], braki: {id: [czego brakuje]}}."""
    adres = adres.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60, connect=5)) as c:
            st = (await c.get(adres + "/system_stats")).json()
            wezly = set((await c.get(adres + "/object_info")).json())
            pliki = set()
            for kat in (await c.get(adres + "/models")).json():
                r = await c.get(f"{adres}/models/{kat}")
                if r.status_code == 200:
                    for f in r.json():
                        f = str(f).replace("\\", "/")
                        pliki.update({f, f.rsplit("/", 1)[-1]})
    except Exception as e:
        return {"ok": False, "info": f"ComfyUI nie odpowiada ({type(e).__name__}) — czy jest uruchomione pod tym adresem?"}
    dev = (st.get("devices") or [{}])[0]
    nazwa_gpu = re.sub(r"^\w+:\d+\s*", "", dev.get("name") or "").split(" : ")[0].strip()   # „cuda:0 NVIDIA … : cudaMallocAsync”
    gpu = f"{nazwa_gpu} · {round((dev.get('vram_total') or 0) / 2**30)} GB".strip(" ·")

    dostepne, braki, warianty = [], {}, {}
    for f in sorted(Path(MODELE).glob("*/*.yaml")):
        y = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if y.get("backend", "comfyui") != "comfyui":
            continue
        if y.get("warianty") and not y.get("workflow"):
            warianty[y["id"]] = [w["model"] for w in y["warianty"]]
            continue
        brak = []
        for rel in sorted(set(_workflowy(y))):
            pot = _potrzeby(rel)
            if pot is None:
                brak.append(f"workflow {rel}")
                continue
            brak += sorted(f"plik {p}" for p in pot[0] if p not in pliki and p.rsplit("/", 1)[-1] not in pliki)
            brak += sorted(f"węzeł {k}" for k in pot[1] if k and k not in wezly)
        if brak:
            braki[y["id"]] = brak
        else:
            dostepne.append(y["id"])
    for wid, ws in warianty.items():                  # pozycja z wariantami: dostępna, gdy choć jeden wariant działa
        if any(w in dostepne for w in ws):
            dostepne.append(wid)
        else:
            braki[wid] = sorted({b for w in ws for b in braki.get(w, [])})
    return {"ok": True, "info": f"działa · {gpu} · gotowe modele: {len([d for d in dostepne if d not in sum(warianty.values(), [])])}",
            "gpu": gpu, "dostepne": dostepne, "braki": braki, "czas": time.time()}


def zastosuj(stan: dict | None):
    """Stan z Ustawień → maszyna „komputer” w dyspozytorze i dostępność modeli w rejestrze (bez restartu)."""
    from . import registry, scheduler
    from .registry import MODELS
    scheduler.MACHINES.pop("komputer", None)
    registry.KOMPUTER.clear()
    if not stan or not stan.get("adres") or not stan.get("dostepne"):
        return
    ids = set(stan["dostepne"])
    role = sorted({MODELS[i].obszar for i in ids if i in MODELS})
    registry.KOMPUTER.update(ids)
    scheduler.MACHINES["komputer"] = scheduler.Machine({"id": "komputer", "nazwa": stan.get("gpu") or "ComfyUI",
                                                        "comfyui": stan["adres"], "role": role, "modele": sorted(ids),
                                                        "przeladowanie_s": 20})
