"""Rejestr modeli: każdy model to plik modele/<obszar>/<id>.yaml.

Dodanie modelu = dopisanie pliku. Typy parametrów (prompt, proporcje, seed, liczba, wybor, tryb,
obraz/wideo/dzwiek jako wejście) mają wspólne komponenty w GUI i wspólną obsługę w workflow.py.
"""
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from .config import CFG, MODELE, OBSZARY
from .i18n import K


@dataclass
class Model:
    id: str
    nazwa: str
    obszar: str
    backend: str
    workflow: str | None
    wyjscie: str
    opis: dict = field(default_factory=dict)
    licencja: str = ""
    uwagi: dict = field(default_factory=dict)
    wejscia: list = field(default_factory=list)
    parametry: list = field(default_factory=list)
    kolejnosc: int = 100
    poradnik: str | None = None
    # backend: http — usługa z config (maszyny[].uslugi), endpoint, format zapytania, rodzaj odpowiedzi
    usluga: str | None = None
    endpoint: str | None = None
    format: str = "json"
    odpowiedz: str = "json_plik"
    stale: dict = field(default_factory=dict)
    pliki: list = field(default_factory=list)
    # kolejność plików wynikowych ComfyUI wg węzłów zapisu; pierwszy = główny wynik; dopisek trafia do nazwy pliku
    wyjscia: list = field(default_factory=list)   # [{wezel: "6"}, {wezel: "5", dopisek: "wzorzec"}]
    # jedna pozycja na model: lista wariantów wybieranych wg wypełnionych wejść (pierwszy pasujący)
    #   [{model: <id wariantu>, gdy: [wejścia, które muszą być podane], mapa: {wejście tu: wejście w wariancie}}]
    warianty: list = field(default_factory=list)
    ukryty: bool = False          # wariant pod inną pozycją: nie ma go na liście, ale działa (historia, „powtórz”)
    nalezy_do: str | None = None  # id pozycji, do której należy ukryty wariant
    # backend: api — zewnętrzny dostawca (api.py): endpointy wg wejść, cena w USD za sekundę wyniku
    dostawca: str | None = None
    endpointy: list = field(default_factory=list)
    cena: dict = field(default_factory=dict)
    zapas_api: str | list | None = None  # model lokalny: modele API do zaproponowania przy długim zadaniu (api.zapasy)
    nazwy: dict = field(default_factory=dict)   # nazwa w innych językach, gdy `nazwa` ma polskie słowa: {en, fr}

    def nazwa_w(self, lang: str = "pl") -> str:
        return self.nazwa if lang == "pl" else (self.nazwy.get(lang) or self.nazwy.get("en") or self.nazwa)

    def public(self, lang: str = "pl") -> dict:
        """To, co widzi przeglądarka (bez celów w workflow)."""
        strip = lambda items: [{k: v for k, v in p.items() if not k.startswith("cel") and k != "opcje_cele"}
                               | ({"opcje": list(p["opcje_cele"].keys())} if "opcje_cele" in p else {})
                               for p in items]
        strip_inp = lambda items: [{k: v for k, v in p.items() if not k.startswith("cel") and k not in ("wezly", "podlacz")}
                                   for p in items]
        return self._public_fix(lokalnie({"id": self.id, "nazwa": self.nazwa_w(lang), "obszar": self.obszar, "opis": self.opis,
                         "licencja": self.licencja, "uwagi": self.uwagi, "wyjscie": self.wyjscie,
                         "wejscia": strip_inp(self.wejscia), "parametry": strip(self.parametry),
                         "api": self.backend == "api", "cena": self.cena or None, "zapas_api": self.zapas_api}, lang))

    def _public_fix(self, d: dict) -> dict:
        for p in d["parametry"]:
            if "domyslnie_j" in p:
                p["domyslnie"] = p.pop("domyslnie_j")
        return d


def lokalnie(x, lang: str):
    """Słowniki {pl, en, fr} → tekst w języku lang (rekurencyjnie) — przeglądarka dostaje tylko swój język."""
    if isinstance(x, dict):
        if x and set(x) <= {"pl", "en", "fr"}:
            return x.get(lang) or (x.get("en") if lang != "pl" else None) or x.get("pl") or x.get("en") or ""
        if {"pl", "en"} <= set(x):                       # np. opcja {v, pl, en, fr}: zostaje tylko bieżący język
            jest = lang if x.get(lang) else ("en" if lang != "pl" and x.get("en") else "pl")
            return {k: (lokalnie(v, lang) if k not in ("pl", "en", "fr") else v) for k, v in x.items()
                    if k not in ("pl", "en", "fr") or k == jest} | ({lang: x[jest]} if jest != lang else {})
        return {k: lokalnie(v, lang) for k, v in x.items()}
    if isinstance(x, list):
        return [lokalnie(v, lang) for v in x]
    return x


def load_all() -> dict[str, Model]:
    models = {}
    for f in sorted(Path(MODELE).glob("*/*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        if d.get("obszar") not in OBSZARY:
            continue
        m = Model(id=d["id"], nazwa=d["nazwa"], obszar=d["obszar"], backend=d.get("backend", "comfyui"),
                  workflow=d.get("workflow"), wyjscie=d.get("wyjscie", d["obszar"]), opis=d.get("opis", {}),
                  licencja=d.get("licencja", ""), uwagi=d.get("uwagi", {}), wejscia=d.get("wejscia", []),
                  parametry=d.get("parametry", []), kolejnosc=d.get("kolejnosc", 100),
                  poradnik=d.get("poradnik"), usluga=d.get("usluga"), endpoint=d.get("endpoint"),
                  format=d.get("format", "json"), odpowiedz=d.get("odpowiedz", "json_plik"),
                  stale=d.get("stale", {}), pliki=d.get("pliki", []), wyjscia=d.get("wyjscia", []),
                  warianty=d.get("warianty", []), ukryty=bool(d.get("ukryty")),
                  dostawca=d.get("dostawca"), endpointy=d.get("endpointy", []), cena=d.get("cena", {}),
                  zapas_api=d.get("zapas_api"), nazwy=d.get("nazwy") or {})
        for p in m.parametry:                       # domyślna wartość zależna od języka (np. tekst próbki głosu)
            if isinstance(p.get("domyslnie"), dict):
                p["domyslnie_j"] = p["domyslnie"]
                p["domyslnie"] = p["domyslnie"].get("pl") or next(iter(p["domyslnie"].values()))
        m._parametry_z = d.get("parametry_z")
        models[m.id] = m
    for m in models.values():
        if m._parametry_z and m._parametry_z in models and not m.parametry:
            m.parametry = models[m._parametry_z].parametry
        if not m.workflow and m.warianty:
            m.workflow = models[m.warianty[-1]["model"]].workflow
        for w in m.warianty:
            if w["model"] in models:
                models[w["model"]].nalezy_do = m.id
    return models


def wariant(model: Model, wejscia: dict) -> tuple[Model, dict]:
    """Dla pozycji z wariantami: wybiera wariant wg podanych wejść i przemianowuje wejścia na jego nazwy."""
    if not model.warianty:
        return model, wejscia
    podane = {k for k, v in wejscia.items() if v not in (None, "", [])}
    for w in model.warianty:
        if set(w.get("gdy", [])) <= podane:
            wm = MODELS[w["model"]]
            ids = {i["id"] for i in wm.wejscia}
            mapa = w.get("mapa", {})
            return wm, {mapa.get(k, k): v for k, v in wejscia.items() if k in podane and mapa.get(k, k) in ids}
    raise ValueError(K("e_wariant"))


MODELS = load_all()


def odswiez_chmure():
    """Modele wybrane w Ustawieniach (dostawcy w chmurze) → pozycje w MODELS; wywoływane na starcie i po każdej zmianie.
    Na razie: modele tekstowe (rozmowa przez API zgodne z OpenAI u dostawcy)."""
    from . import dostawcy
    for k in [k for k, m in MODELS.items() if m.stale.get("chmura")]:
        del MODELS[k]
    for i, (d, poz) in enumerate(dostawcy.wybrane_pozycje()):
        if poz.get("z_repo"):
            continue                                   # HiggsField / Kie.ai: modele z YAML, już w MODELS
        if poz["obszar"] != "tekst":
            continue
        mid = dostawcy.id_studia(d, poz["id"])
        nazwa_d = dostawcy.DOSTAWCY[d]["nazwa"]
        opis = (poz.get("opis") or "").strip()
        MODELS[mid] = Model(id=mid, nazwa=poz["nazwa"], obszar="tekst", backend="llm", workflow=None, wyjscie="tekst",
                            opis={"pl": f"{nazwa_d}. {opis}".strip(), "en": f"{nazwa_d}. {opis}".strip()},
                            licencja={"pl": "API — warunki dostawcy", "en": "API — provider terms"}, kolejnosc=10 + i,
                            stale={"chmura": True, "dostawca": d, "api_model": poz["id"], "obrazy": bool(poz.get("obraz_we")),
                                   "narzedzia": bool(poz.get("narzedzia", True)), "temperatura": 0.7})


def uruchamialny(m: Model) -> bool:
    """Czy ta instalacja umie uruchomić model: API — jest klucz dostawcy; ComfyUI/usługa — jest maszyna z tą rolą
    (i tą usługą); config.yaml → modele_wylaczone: [id, …] ukrywa wybrane. Bez tego inna instalacja widziałaby
    modele, których nie ma (np. bez karty graficznej — tylko modele przez API)."""
    if m.id in (CFG.get("modele_wylaczone") or []):
        return False
    if m.backend == "api":
        from . import api, dostawcy
        return api.dostepny(m) and m.id in dostawcy.wybrane(m.dostawca or "")   # wybrany w Ustawieniach
    if m.backend in ("comfyui", "http"):
        for x in CFG.get("maszyny") or []:
            if m.obszar not in (x.get("role") or []) or (x.get("modele") is not None and m.id not in x["modele"]):
                continue
            if m.backend == "http" and (m.usluga or "") not in (x.get("uslugi") or {}):
                continue
            return True
        return False
    if m.backend == "llm":
        return bool(m.stale.get("chmura"))          # tekst: tylko modele wybrane w Ustawieniach
    return True


def by_area(area: str) -> list[Model]:
    return sorted((m for m in MODELS.values() if m.obszar == area and not m.ukryty and uruchamialny(m)),
                  key=lambda m: (m.kolejnosc, m.nazwa))
