"""Katalog modeli Kie.ai z dokumentacji (Kie.ai nie ma katalogu w API).

Czyta https://docs.kie.ai/llms.txt, pobiera strony modeli (/market/...md), wyjmuje z nich opis OpenAPI
(POST /api/v1/jobs/createTask) i zapisuje modele/kie-katalog.json: nazwa modelu, obszar, pola formularza.
Uruchom ponownie, gdy Kie.ai doda modele:   python narzedzia/kie_katalog.py
"""
import json
import re
import sys
import time
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.dostawcy import pola_z_openapi  # noqa: E402

CEL = ROOT / "modele" / "kie-katalog.json"
OBSZARY = {"Video": "wideo", "Image": "obraz", "Music": "muzyka", "Audio": "muzyka"}


def obszar(kategoria: str, nazwa: str, model: str) -> str | None:
    rodzaj = next((v for k, v in OBSZARY.items() if kategoria.strip().startswith(k)), None)
    if not rodzaj:
        return None
    s = (nazwa + " " + model).lower()
    if rodzaj == "muzyka" and re.search(r"sound.?effect|sfx", s):
        return "sfx"
    if rodzaj == "muzyka" and re.search(r"tts|text.to.speech|dialogue|speech|voice", s):
        return "mowa"
    return rodzaj


def main():
    c = httpx.Client(timeout=60, follow_redirects=True)
    spis = c.get("https://docs.kie.ai/llms.txt").text
    strony = re.findall(r"^- ([^\[]*)\[([^\]]+)\]\((https://docs\.kie\.ai/market/[^)]+\.md)\)", spis, re.M)
    out, pominiete = [], 0
    for kategoria, tytul, url in strony:
        kat = kategoria.split(">")[0].strip()
        if not any(kat.startswith(k) for k in OBSZARY):
            continue
        try:
            md = c.get(url).text
            blok = re.search(r"```yaml\n(openapi:.*?)\n```", md, re.S)
            spec = yaml.safe_load(blok.group(1)) if blok else None
        except Exception as e:
            print("  ✗", url, e)
            continue
        post = ((spec or {}).get("paths", {}).get("/api/v1/jobs/createTask") or {}).get("post")
        if not post:
            pominiete += 1
            continue
        sch = post["requestBody"]["content"]["application/json"]["schema"]
        props = sch.get("properties", {})
        modele = (props.get("model") or {}).get("enum") or []
        wej = props.get("input")
        if not modele or not wej:
            pominiete += 1
            continue
        sztuczny = {"paths": {"/x": {"post": {"requestBody": {"content": {"application/json": {"schema": wej}}}}}},
                    "components": spec.get("components", {})}
        try:
            parametry, wejscia = pola_z_openapi(sztuczny, "x")
        except Exception as e:
            print("  ✗ pola", url, e)
            continue
        opis = re.sub(r"\s+", " ", post.get("summary") or post.get("description") or "")[:300]
        for m in modele:
            ob = obszar(kat, tytul, m)
            if ob:
                out.append({"id": m, "nazwa": tytul.strip(), "obszar": ob, "opis": opis, "strona": url,
                            "parametry": parametry, "wejscia": wejscia})
        print(f"  ✓ {tytul.strip()} — {', '.join(modele)}")
        time.sleep(0.2)
    widziane, wynik = set(), []
    for x in out:                                   # ta sama nazwa modelu z kilku stron — pierwsza wygrywa
        if x["id"] not in widziane:
            widziane.add(x["id"])
            wynik.append(x)
    CEL.write_text(json.dumps({"zrodlo": "https://docs.kie.ai/llms.txt", "czas": time.strftime("%Y-%m-%d"),
                               "modele": wynik}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"zapisano {len(wynik)} modeli → {CEL.relative_to(ROOT)} (pominięte strony bez createTask: {pominiete})")


if __name__ == "__main__":
    main()
