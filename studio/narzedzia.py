"""Narzędzia agenta czatu — działają wyłącznie w katalogu uczestnika (zasoby/<login>/).

Agent może: oglądać foldery, czytać pliki tekstowe i opisy wyników (.json), tworzyć i zmieniać notatki .md
(artefakty), tworzyć foldery, przenosić notatki .md, szukać w sieci (SearXNG na Sparku — zapytania formułuje
sam model, rozmowa nie wychodzi poza maszynę). Nie generuje mediów i nie rusza plików poza katalogiem uczestnika.
"""
import re
import json
import shutil
from pathlib import Path

import httpx

from . import store
from .config import CFG

SEARX_URL = (CFG.get("searx_url", "http://127.0.0.1:8888") or "").rstrip("/")   # pusty = bez wyszukiwania w sieci
TEKST = {".md", ".txt", ".json"}
MAX_ZNAKOW = 40000

SPEC = [
    {"type": "function", "function": {
        "name": "lista_plikow",
        "description": "Pokazuje zawartość folderu uczestnika (ścieżka względna, pusta = katalog główny: ujecia/, artefakty/, rozmowy/, wgrane/).",
        "parameters": {"type": "object", "properties": {"sciezka": {"type": "string"}}}}},
    {"type": "function", "function": {
        "name": "czytaj_plik",
        "description": "Czyta plik tekstowy uczestnika (.md, .txt, .json). Dla obrazu/dźwięku/wideo zwraca jego opis (prompt, model, ustawienia) z pliku .json obok.",
        "parameters": {"type": "object", "properties": {"sciezka": {"type": "string"}}, "required": ["sciezka"]}}},
    {"type": "function", "function": {
        "name": "zapisz_notatke",
        "description": "Tworzy albo nadpisuje notatkę .md uczestnika (artefakt, widoczny w innych obszarach Studia). Tylko gdy uczestnik o to prosi.",
        "parameters": {"type": "object", "properties": {"sciezka": {"type": "string", "description": "np. artefakty/pomysly.md"},
                                                       "tresc": {"type": "string"}}, "required": ["sciezka", "tresc"]}}},
    {"type": "function", "function": {
        "name": "zapisz_sekcje",
        "description": "Zapisuje JEDNĄ sekcję „## nagłówek” w istniejącej notatce .md (np. biblii utworu): podmienia jej treść albo dopisuje ją na końcu. Reszta pliku zostaje bez zmian. Tylko po zgodzie uczestnika.",
        "parameters": {"type": "object", "properties": {"sciezka": {"type": "string", "description": "np. artefakty/mgla-biblia.md"},
                                                       "naglowek": {"type": "string", "description": "nagłówek sekcji bez ##, np. Dźwięk"},
                                                       "tresc": {"type": "string", "description": "treść sekcji (bez nagłówka)"}},
                       "required": ["sciezka", "naglowek", "tresc"]}}},
    {"type": "function", "function": {
        "name": "zapisz_prompt",
        "description": "Zapisuje gotowy prompt do generacji w artefakty/prompty/<obszar>/ — uczestnik weźmie go z notatek w obszarze generacji. Tylko po zgodzie uczestnika. Treść = sam prompt (bez komentarzy, bez listy źródeł).",
        "parameters": {"type": "object", "properties": {"obszar": {"type": "string", "enum": ["obraz", "wideo", "sfx", "muzyka", "mowa"]},
                                                       "nazwa": {"type": "string", "description": "krótka nazwa, np. ujecie-3-piwnica"},
                                                       "jednostka": {"type": "string", "description": "czego dotyczy prompt, np. „ujęcie 3”, „karta postaci: Babka”, „temat muzyczny”"},
                                                       "tresc": {"type": "string"}}, "required": ["obszar", "nazwa", "tresc"]}}},
    {"type": "function", "function": {
        "name": "utworz_folder",
        "description": "Tworzy folder (i podfoldery) w artefakty/ uczestnika.",
        "parameters": {"type": "object", "properties": {"sciezka": {"type": "string"}}, "required": ["sciezka"]}}},
    {"type": "function", "function": {
        "name": "przenies_notatke",
        "description": "Przenosi albo zmienia nazwę notatki .md (w obrębie artefakty/).",
        "parameters": {"type": "object", "properties": {"z": {"type": "string"}, "do": {"type": "string"}}, "required": ["z", "do"]}}},
    {"type": "function", "function": {
        "name": "szukaj_w_sieci",
        "description": "Szuka w internecie (inspiracje, podobne realizacje, źródła). Zapytanie formułuj sam, krótko, bez danych osobowych i bez cytowania rozmowy.",
        "parameters": {"type": "object", "properties": {"zapytanie": {"type": "string"}}, "required": ["zapytanie"]}}},
]


# Opisy narzędzi dla modelu w rozmowach po angielsku i francusku (model czyta je po angielsku; nazwy narzędzi bez zmian).
OPISY_EN = {
    "lista_plikow": ("Shows the contents of the participant's folder (relative path, empty = root: ujecia/, artefakty/, rozmowy/, wgrane/).",
                     {}),
    "czytaj_plik": ("Reads the participant's text file (.md, .txt, .json). For an image/sound/video it returns its description (prompt, model, settings) from the .json file next to it.",
                    {}),
    "zapisz_notatke": ("Creates or overwrites the participant's .md note (an artifact, visible in other Studio areas). Only when the participant asks for it.",
                       {"sciezka": "e.g. artefakty/ideas.md"}),
    "zapisz_sekcje": ("Saves ONE section “## heading” in an existing .md note (e.g. the piece bible): replaces its content or appends it at the end. The rest of the file stays unchanged. Only with the participant's consent.",
                      {"sciezka": "e.g. artefakty/fog-biblia.md", "naglowek": "section heading without ##, e.g. Sound", "tresc": "section content (without the heading)"}),
    "zapisz_prompt": ("Saves a finished generation prompt in artefakty/prompty/<area>/ — the participant takes it from the notes in the generation area. Only with the participant's consent. Content = the prompt itself (no comments, no list of sources).",
                      {"nazwa": "short name, e.g. shot-3-cellar", "jednostka": "what the prompt is for, e.g. “shot 3”, “character sheet: Grandma”"}),
    "utworz_folder": ("Creates a folder (and subfolders) in the participant's artefakty/.", {}),
    "przenies_notatke": ("Moves or renames a .md note (within artefakty/).", {}),
    "szukaj_w_sieci": ("Searches the internet (inspirations, similar works, sources). Write the query yourself, short, with no personal data and without quoting the conversation.", {}),
}


def spec(jez: str = "pl") -> list[dict]:
    """SPEC w języku rozmowy: po polsku — oryginał; po angielsku i francusku — opisy angielskie."""
    if jez == "pl":
        return SPEC
    out = json.loads(json.dumps(SPEC))
    for t in out:
        fn = t["function"]
        opis, pola = OPISY_EN.get(fn["name"], (None, {}))
        if opis:
            fn["description"] = opis
        for k, v in pola.items():
            if k in fn["parameters"]["properties"]:
                fn["parameters"]["properties"][k]["description"] = v
    return out


def jako_json(t: str) -> str | None:
    """Tekst będący obiektem JSON (także w ``` albo z tekstem dookoła) → sformatowany JSON; inaczej None."""
    t = (t or "").strip()
    m = re.search(r"```[\w-]*\n(.*?)```", t, re.S)
    for x in (t, m.group(1) if m else None, t[t.find("{"):t.rfind("}") + 1] if "{" in t else None):
        if not x:
            continue
        try:
            o = json.loads(x)
        except ValueError:
            continue
        if isinstance(o, dict):                           # krótkie listy (bbox, palety) w jednej linii
            return re.sub(r"\[\n\s*([^\[\]{}]*?)\n\s*\]", lambda m: "[" + re.sub(r",\n\s*", ", ", m.group(1)) + "]",
                          json.dumps(o, ensure_ascii=False, indent=2))
    return None


def _korzen(login: str) -> Path:
    return store.user_dir(login).resolve()


def _sciezka(login: str, rel: str) -> Path:
    root = _korzen(login)
    p = (root / (rel or "").strip().lstrip("/\\")).resolve()
    if p != root and root not in p.parents:
        raise ValueError("ścieżka poza katalogiem uczestnika")
    return p


def _w_artefaktach(login: str, p: Path) -> bool:
    a = (_korzen(login) / "artefakty").resolve()
    return p == a or a in p.parents


# Teksty narzędzi: opis dla uczestnika (co agent robi) i wyniki, które czyta model — w języku rozmowy.
S = {
    "o_lista": {"pl": "przeglądam folder {p}", "en": "browsing folder {p}", "fr": "je parcours le dossier {p}"},
    "o_czytaj": {"pl": "czytam {p}", "en": "reading {p}", "fr": "je lis {p}"},
    "o_notatka": {"pl": "zapisuję notatkę {p}", "en": "saving note {p}", "fr": "j’enregistre la note {p}"},
    "o_sekcja": {"pl": "zapisuję sekcję „{n}” w {p}", "en": "saving section “{n}” in {p}", "fr": "j’enregistre la section « {n} » dans {p}"},
    "o_prompt": {"pl": "zapisuję prompt „{n}” do prompty/{o}/", "en": "saving prompt “{n}” to prompty/{o}/", "fr": "j’enregistre le prompt « {n} » dans prompty/{o}/"},
    "o_folder": {"pl": "tworzę folder {p}", "en": "creating folder {p}", "fr": "je crée le dossier {p}"},
    "o_przenies": {"pl": "przenoszę {z} → {d}", "en": "moving {z} → {d}", "fr": "je déplace {z} → {d}"},
    "o_szukaj": {"pl": "szukam w sieci: {q}", "en": "searching the web: {q}", "fr": "je cherche sur le web : {q}"},
    "nie_folder": {"pl": "to nie jest folder", "en": "this is not a folder", "fr": "ce n’est pas un dossier"},
    "pusto": {"pl": "(pusto)", "en": "(empty)", "fr": "(vide)"},
    "nie_plik": {"pl": "nie ma takiego pliku", "en": "no such file", "fr": "fichier introuvable"},
    "binarny": {"pl": "plik binarny bez opisu", "en": "binary file without a description", "fr": "fichier binaire sans description"},
    "zapisano": {"pl": "zapisano {p}", "en": "saved {p}", "fr": "enregistré {p}"},
    "brak_notatki": {"pl": "nie ma takiej notatki .md w artefakty/ (najpierw ją utwórz narzędziem zapisz_notatke)",
                     "en": "no such .md note in artefakty/ (create it first with the zapisz_notatke tool)",
                     "fr": "pas de note .md de ce nom dans artefakty/ (crée-la d’abord avec l’outil zapisz_notatke)"},
    "brak_naglowka": {"pl": "brak nagłówka", "en": "missing heading", "fr": "titre manquant"},
    "zapisano_sekcje": {"pl": "zapisano sekcję „{n}” w {p}", "en": "saved section “{n}” in {p}", "fr": "section « {n} » enregistrée dans {p}"},
    "nieznany_obszar": {"pl": "nieznany obszar", "en": "unknown area", "fr": "espace inconnu"},
    "utworzono": {"pl": "utworzono {p}/", "en": "created {p}/", "fr": "créé {p}/"},
    "tylko_md": {"pl": "przenosić można tylko notatki .md w obrębie artefakty/", "en": "only .md notes inside artefakty/ can be moved",
                 "fr": "on ne peut déplacer que des notes .md à l’intérieur de artefakty/"},
    "przeniesiono": {"pl": "przeniesiono do {p}", "en": "moved to {p}", "fr": "déplacé vers {p}"},
    "brak_wynikow": {"pl": "brak wyników", "en": "no results", "fr": "aucun résultat"},
    "nieznane": {"pl": "nieznane narzędzie", "en": "unknown tool", "fr": "outil inconnu"},
    "blad": {"pl": "błąd: {e}", "en": "error: {e}", "fr": "erreur : {e}"},
    "poza": {"pl": "ścieżka poza katalogiem uczestnika", "en": "path outside the participant’s folder", "fr": "chemin hors du dossier du participant"},
}
ZAPISANO = tuple(S[k][j].split("{")[0] for k in ("zapisano", "zapisano_sekcje") for j in ("pl", "en", "fr"))


def tx(klucz: str, jez: str = "pl", **kw) -> str:
    d = S[klucz]
    return (d.get(jez) or d["pl"]).format(**kw)


def udany_zapis(wynik: str) -> bool:
    return wynik.startswith(ZAPISANO)


def opis(nazwa: str, args: dict, jez: str = "pl") -> str:
    """Krótka informacja dla uczestnika, czego agent właśnie używa."""
    a = lambda k: args.get(k)
    return {
        "lista_plikow": lambda: tx("o_lista", jez, p=a("sciezka") or "/"),
        "czytaj_plik": lambda: tx("o_czytaj", jez, p=a("sciezka")),
        "zapisz_notatke": lambda: tx("o_notatka", jez, p=a("sciezka")),
        "zapisz_sekcje": lambda: tx("o_sekcja", jez, n=a("naglowek"), p=a("sciezka")),
        "zapisz_prompt": lambda: tx("o_prompt", jez, n=a("nazwa"), o=a("obszar")),
        "utworz_folder": lambda: tx("o_folder", jez, p=a("sciezka")),
        "przenies_notatke": lambda: tx("o_przenies", jez, z=a("z"), d=a("do")),
        "szukaj_w_sieci": lambda: tx("o_szukaj", jez, q=a("zapytanie")),
    }.get(nazwa, lambda: nazwa)()


async def wykonaj(login: str, nazwa: str, args: dict, jez: str = "pl", kontekst: dict | None = None) -> str:
    try:
        if nazwa == "lista_plikow":
            p = _sciezka(login, args.get("sciezka", ""))
            if not p.is_dir():
                return tx("nie_folder", jez)
            out = []
            for x in sorted(p.iterdir()):
                if x.name.endswith(".json") and (x.with_suffix("")).exists():
                    continue                       # plik opisu obok wyniku — pokazujemy sam wynik
                out.append(f"{x.name}/" if x.is_dir() else f"{x.name} ({x.stat().st_size // 1024} KB)")
            return "\n".join(out[:300]) or tx("pusto", jez)
        if nazwa == "czytaj_plik":
            p = _sciezka(login, args["sciezka"])
            if not p.is_file():
                return tx("nie_plik", jez)
            if p.suffix.lower() in TEKST:
                return p.read_text(encoding="utf-8", errors="replace")[:MAX_ZNAKOW]
            meta = p.with_suffix(p.suffix + ".json")
            return meta.read_text(encoding="utf-8")[:MAX_ZNAKOW] if meta.exists() else tx("binarny", jez)
        if nazwa == "zapisz_notatke":
            p = _sciezka(login, args["sciezka"])
            if p.suffix.lower() != ".md":
                p = p.with_suffix(".md")
            if not _w_artefaktach(login, p):
                p = _korzen(login) / "artefakty" / p.name
            p.parent.mkdir(parents=True, exist_ok=True)
            nowa = not p.exists()
            p.write_text(args.get("tresc") or "", encoding="utf-8")
            if nowa:
                store.add_asset(login, "tekst", "artefakt", p, p.name, "tekst", None, None, {"zrodlo": "agent"},
                                ujecie_id=store.default_ujecie(login)["id"])
            return tx("zapisano", jez, p=store.rel(p))
        if nazwa == "zapisz_sekcje":
            p = _sciezka(login, args["sciezka"])
            if p.suffix.lower() != ".md" or not _w_artefaktach(login, p) or not p.is_file():
                return tx("brak_notatki", jez)
            nagl = re.sub(r"^#+\s*", "", (args.get("naglowek") or "").strip())
            if not nagl:
                return tx("brak_naglowka", jez)
            t = p.read_text(encoding="utf-8")
            blok = f"## {nagl}\n{(args.get('tresc') or '').strip()}\n"
            m = re.search(rf"^##\s+{re.escape(nagl)}\s*$", t, re.M | re.I)
            if m:
                n = re.search(r"^#{1,2}\s", t[m.end():], re.M)
                koniec = m.end() + n.start() if n else len(t)
                t = t[:m.start()] + blok + ("\n" if n else "") + t[koniec:]
            else:
                t = t.rstrip() + "\n\n" + blok
            p.write_text(t, encoding="utf-8")
            return tx("zapisano_sekcje", jez, n=nagl, p=store.rel(p))
        if nazwa == "zapisz_prompt":
            ob = args.get("obszar")
            if ob not in ("obraz", "wideo", "sfx", "muzyka", "mowa"):
                return tx("nieznany_obszar", jez)
            folder = _korzen(login) / "artefakty" / "prompty" / ob
            folder.mkdir(parents=True, exist_ok=True)
            nm = store.slug(args.get("nazwa") or "prompt") or "prompt"
            p, i = folder / f"{nm}.md", 2
            while p.exists():
                p, i = folder / f"{nm}-{i}.md", i + 1
            t = (args.get("tresc") or "").strip()
            j = jako_json(t)
            if j:                                         # JSON (np. Ideogram) jako blok kodu — edytor notatek nie doda „\”
                t = "```json\n" + j + "\n```"
            p.write_text(t + "\n", encoding="utf-8")
            k = kontekst or {}                          # opis promptu: lista w obszarze filtruje po modelu i utworze
            store.add_asset(login, "tekst", "artefakt", p, p.name, "tekst", None, None,
                            {"zrodlo": "promptmaker", "obszar": ob, "model": k.get("model"), "biblia": k.get("biblia"),
                             "jednostka": (args.get("jednostka") or "").strip()[:80] or None},
                            ujecie_id=store.default_ujecie(login)["id"])
            return tx("zapisano", jez, p=store.rel(p))
        if nazwa == "utworz_folder":
            p = _sciezka(login, args["sciezka"])
            if not _w_artefaktach(login, p):
                p = _korzen(login) / "artefakty" / Path(args["sciezka"]).name
            p.mkdir(parents=True, exist_ok=True)
            return tx("utworzono", jez, p=store.rel(p))
        if nazwa == "przenies_notatke":
            z, do = _sciezka(login, args["z"]), _sciezka(login, args["do"])
            if z.suffix.lower() != ".md" or not _w_artefaktach(login, z) or not _w_artefaktach(login, do):
                return tx("tylko_md", jez)
            if do.suffix.lower() != ".md":
                do = do / z.name if do.is_dir() else do.with_suffix(".md")
            do.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(z), str(do))
            with store.db() as c:
                c.execute("UPDATE assets SET sciezka=?, nazwa=? WHERE sciezka=?", (store.rel(do), do.name, store.rel(z)))
            return tx("przeniesiono", jez, p=store.rel(do))
        if nazwa == "szukaj_w_sieci":
            async with httpx.AsyncClient(timeout=20) as c:
                r = await c.get(SEARX_URL + "/search", params={"q": args["zapytanie"], "format": "json", "language": "auto"})
            wyn = (r.json().get("results") or [])[:8]
            return json.dumps([{"tytul": x.get("title"), "adres": x.get("url"), "fragment": (x.get("content") or "")[:300]}
                               for x in wyn], ensure_ascii=False) if wyn else tx("brak_wynikow", jez)
        return tx("nieznane", jez)
    except Exception as e:
        return tx("blad", jez, e=e)
