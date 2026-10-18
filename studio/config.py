"""Ustawienia Studia: ścieżki i maszyny robocze (z pliku config.yaml obok katalogu studio/)."""
from pathlib import Path
import os
import yaml

ROOT = Path(__file__).resolve().parent.parent          # katalog gui/
CONFIG_FILE = Path(os.environ.get("STUDIO_CONFIG", ROOT / "config.yaml"))

_DEFAULT = {
    "zasoby": str(ROOT / "zasoby"),
    "baza": str(ROOT / "zasoby" / "studio.db"),
    "maszyny": [],
    "uzytkownik": "ja",     # jeden użytkownik, bez logowania; pusty = logowanie po imieniu (praca w grupie)
}


def _sekrety():
    """Klucze z sekrety.env obok katalogu studio/ (KLUCZ=wartość), gdy nie ustawiono ich już w środowisku
    (np. przez systemd) — dzięki temu Studio działa tak samo po zwykłym `uvicorn` i na Windowsie."""
    p = Path(os.environ.get("STUDIO_SEKRETY", ROOT / "sekrety.env"))
    if not p.exists():
        return
    for linia in p.read_text(encoding="utf-8").splitlines():
        linia = linia.strip()
        if linia and not linia.startswith("#") and "=" in linia:
            k, v = linia.split("=", 1)
            os.environ.setdefault(k.strip().removeprefix("export ").strip(), v.strip().strip('"').strip("'"))


_sekrety()


def load() -> dict:
    cfg = dict(_DEFAULT)
    if CONFIG_FILE.exists():
        cfg.update(yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {})
    return cfg


CFG = load()
ZASOBY = Path(CFG["zasoby"]).expanduser()
BAZA = Path(CFG["baza"]).expanduser()
MODELE = ROOT / "modele"
WORKFLOWS = ROOT / "workflows"
OBSZARY = ["tekst", "mowa", "muzyka", "sfx", "obraz", "wideo"]
