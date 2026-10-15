"""Załączniki do wiadomości w czacie (obszar Tekst): tekst, dokumenty, PDF, obrazy.

Pliki: zasoby/<login>/rozmowy/zalaczniki/<id rozmowy>/<nazwa> — prywatne, jak rozmowy.
Obok: <nazwa>.txt (wydobyty tekst), dla PDF bez warstwy tekstowej — <nazwa>.s<N>.jpg (strony jako obrazy, pdftoppm).
Do modelu: tekst doklejony do wiadomości uczestnika; obrazy jako części image_url (model API widzi obrazy;
lokalny zapasowy model — nie, wtedy dostaje tylko informację, że obraz był).
"""
import base64
import re
import subprocess
import zipfile
from html import unescape
from pathlib import Path

from fastapi import HTTPException, UploadFile

from . import store
from .i18n import K

TEKSTOWE = {".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".srt", ".vtt", ".html", ".htm", ".xml",
            ".yaml", ".yml", ".py", ".js", ".css", ".rtf", ".tex", ".fountain"}
DOKUMENTY = {".docx", ".odt", ".pdf"}
OBRAZY = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
MAX_BAJTOW = 25 * 1024 * 1024        # jeden plik
MAX_OBRAZ = 8 * 1024 * 1024          # obraz wysyłany do modelu
MAX_ZNAKOW = 60000                   # tekst jednego załącznika do modelu
MAX_STRON_SKAN = 6                   # PDF bez tekstu: ile stron jako obrazy


def katalog(login: str, rid: str) -> Path:
    return store.user_dir(login, "rozmowy", "zalaczniki", rid)


def _bezpieczna(nazwa: str) -> str:
    p = Path(nazwa or "plik").name
    stem = re.sub(r"[^\w.\- ]+", "_", Path(p).stem, flags=re.U).strip(" .")[:80] or "plik"
    return stem + Path(p).suffix.lower()


def _z_xml(xml: str, akapit: str) -> str:
    xml = re.sub(akapit, "\n", xml)
    xml = re.sub(r"<w:tab/>|<text:tab/>", "\t", xml)
    return unescape(re.sub(r"<[^>]+>", "", xml)).strip()


def _tekst(p: Path) -> tuple[str, list[str]]:
    """(tekst, strony-jako-obrazy) z pliku."""
    ext = p.suffix.lower()
    if ext in TEKSTOWE:
        raw = p.read_bytes()
        for kod in ("utf-8", "cp1250", "latin-1"):
            try:
                t = raw.decode(kod)
                break
            except UnicodeDecodeError:
                continue
        if ext in (".html", ".htm"):
            t = unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style).*?</\1>", "", t)))
        return t, []
    if ext == ".docx":
        with zipfile.ZipFile(p) as z:
            return _z_xml(z.read("word/document.xml").decode("utf-8", "replace"), r"</w:p>"), []
    if ext == ".odt":
        with zipfile.ZipFile(p) as z:
            return _z_xml(z.read("content.xml").decode("utf-8", "replace"), r"</text:p>|</text:h>"), []
    if ext == ".pdf":
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(p), "-"], capture_output=True, timeout=120)
        t = r.stdout.decode("utf-8", "replace").strip()
        if len(re.sub(r"\s+", "", t)) >= 15:
            return t, []
        # skan bez warstwy tekstowej → kilka pierwszych stron jako obrazy
        subprocess.run(["pdftoppm", "-jpeg", "-r", "110", "-l", str(MAX_STRON_SKAN), str(p), str(p) + ".s"],
                       capture_output=True, timeout=180)
        return "", sorted(x.name for x in p.parent.glob(p.name + ".s*.jpg"))
    return "", []


async def zapisz(login: str, rid: str, plik: UploadFile) -> dict:
    nazwa = _bezpieczna(plik.filename)
    ext = Path(nazwa).suffix.lower()
    if ext not in TEKSTOWE | DOKUMENTY | set(OBRAZY):
        raise HTTPException(400, K("e_zal_typ", n=ext or nazwa))
    d = katalog(login, rid)
    p, i = d / nazwa, 2
    while p.exists():
        p, i = d / f"{Path(nazwa).stem}-{i}{ext}", i + 1
    dane = await plik.read()
    if len(dane) > MAX_BAJTOW or (ext in OBRAZY and len(dane) > MAX_OBRAZ):
        raise HTTPException(400, K("e_zal_rozmiar", n=nazwa, mb=(MAX_OBRAZ if ext in OBRAZY else MAX_BAJTOW) // (1024 * 1024)))
    p.write_bytes(dane)
    opis = {"nazwa": p.name, "rodzaj": "obraz" if ext in OBRAZY else "pdf" if ext == ".pdf" else "tekst", "bajty": len(dane)}
    if ext not in OBRAZY:
        try:
            t, strony = _tekst(p)
        except Exception:
            p.unlink(missing_ok=True)
            raise HTTPException(400, K("e_zal_odczyt", n=p.name))
        (d / (p.name + ".txt")).write_text(t, encoding="utf-8")
        opis.update(znaki=len(t), strony_obrazy=strony)
    return opis


def plik(login: str, rid: str, nazwa: str) -> Path:
    p = (katalog(login, rid) / Path(nazwa).name)
    if not p.is_file():
        raise HTTPException(404)
    return p


def usun(login: str, rid: str, nazwa: str):
    d = katalog(login, rid)
    n = Path(nazwa).name
    for x in [d / n, d / (n + ".txt"), *d.glob(n + ".s*.jpg")]:
        x.unlink(missing_ok=True)


def _data_url(p: Path) -> str | None:
    mime = OBRAZY.get(p.suffix.lower())
    if not mime or p.stat().st_size > MAX_OBRAZ:
        return None
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def dla_modelu(login: str, rid: str, tresc: str, zal: list[dict], etykiety: dict, z_obrazami: bool):
    """Treść wiadomości uczestnika dla modelu: tekst + załączniki (tekst doklejony, obrazy jako image_url).
    Zwraca (content, liczba znaków)."""
    if not zal:
        return tresc, len(tresc)
    d = katalog(login, rid)
    tekst, obrazy = tresc, []
    for z in zal:
        n = z["nazwa"]
        if z["rodzaj"] == "obraz":
            obrazy.append((n, d / n))
            continue
        t = (d / (n + ".txt")).read_text(encoding="utf-8") if (d / (n + ".txt")).exists() else ""
        if t:
            ciecie = len(t) > MAX_ZNAKOW
            tekst += (f"\n\n{etykiety['poczatek'].format(n=n)}\n{t[:MAX_ZNAKOW]}\n"
                      + (etykiety["uciete"].format(n=MAX_ZNAKOW) + "\n" if ciecie else "") + etykiety["koniec"].format(n=n))
        for s in z.get("strony_obrazy") or []:
            obrazy.append((f"{n} · {s.rsplit('.s', 1)[-1].removesuffix('.jpg')}", d / s))
        if not t and not z.get("strony_obrazy"):
            tekst += "\n\n" + etykiety["pusty"].format(n=n)
    if not obrazy:
        return tekst, len(tekst)
    if not z_obrazami:
        return tekst + "".join("\n\n" + etykiety["obraz_pominiety"].format(n=n) for n, _ in obrazy), len(tekst)
    czesci = [{"type": "text", "text": tekst}]
    for n, p in obrazy:
        url = _data_url(p) if p.exists() else None
        if url:
            czesci.append({"type": "text", "text": etykiety["obraz"].format(n=n)})
            czesci.append({"type": "image_url", "image_url": {"url": url}})
    return czesci, len(tekst) + 2000 * len(obrazy)


def tylko_tekst(content, etykieta: str):
    """Dla lokalnego modelu (bez obrazów): części image_url → informacja tekstowa."""
    if isinstance(content, str):
        return content
    out = []
    for c in content:
        if c.get("type") == "text":
            out.append(c["text"])
        else:
            out.append(etykieta)
    return "\n".join(out)


def opis(login: str, rid: str, nazwa: str) -> dict | None:
    """Opis załącznika odtworzony z dysku (klient podaje tylko nazwy)."""
    d = katalog(login, rid)
    p = d / Path(nazwa).name
    if not p.is_file() or p.name.endswith(".txt") and (d / p.name[:-4]).is_file():
        return None
    ext = p.suffix.lower()
    o = {"nazwa": p.name, "rodzaj": "obraz" if ext in OBRAZY else "pdf" if ext == ".pdf" else "tekst", "bajty": p.stat().st_size}
    if ext not in OBRAZY:
        t = d / (p.name + ".txt")
        o.update(znaki=len(t.read_text(encoding="utf-8")) if t.exists() else 0,
                 strony_obrazy=sorted(x.name for x in d.glob(p.name + ".s*.jpg")))
    return o
