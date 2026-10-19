"""Obszar Tekst: prywatne rozmowy z LLM (strumieniowo) i artefakty .md.

Rozmowy: zasoby/<login>/rozmowy/<id>.json — widzi je tylko autor (żadna galeria ich nie pokazuje).
Artefakty: zasoby/<login>/artefakty/<nazwa>.md — zwykłe zasoby (rodzaj „tekst”), widoczne w innych obszarach.
LLM: modele tekstowe wybrane w Ustawieniach (OpenRouter, Claude, ChatGPT, Gemini — endpointy czatu zgodne z OpenAI);
gdy wybrany nie odpowiada — pozostałe wybrane, a na końcu (opcjonalnie) lokalny LLM (`llm_url`).
"""
import asyncio
import json
import os
import re
import time
import traceback
from pathlib import Path

import httpx
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from . import store, narzedzia, prompty, zalaczniki
from .config import CFG, ROOT
from .registry import MODELS, by_area
from .i18n import JEZYKI, K, L, przetlumacz

router = APIRouter()
LLM_URL = (CFG.get("llm_url") or "").rstrip("/")   # lokalny LLM (opcjonalny zapas); pusty = tylko API
LLM_API = CFG.get("llm_api") or {}          # zewnętrzne API: model główny + zapasowe (llm_api.zapasowe)
PROMPTY = ROOT / "prompty"
HISTORIA_ZNAKOW = 60000           # ile ostatnich znaków rozmowy idzie do modelu


def _need(req: Request) -> str:
    u = store.kto(req.cookies.get("login"))
    if not u:
        raise HTTPException(401, K("e_zaloguj"))
    return u


def _plik(login: str, rid: str) -> Path:
    if not re.fullmatch(r"[0-9a-z-]{6,40}", rid):
        raise HTTPException(400, K("e_id"))
    return store.user_dir(login, "rozmowy") / f"{rid}.json"


def _czytaj(login: str, rid: str) -> dict:
    p = _plik(login, rid)
    if not p.exists():
        raise HTTPException(404)
    return json.loads(p.read_text(encoding="utf-8"))


def _zapisz(login: str, r: dict):
    r["zmienione"] = time.time()
    _plik(login, r["id"]).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")


S = {
    "studio_tytul": {"pl": "## Studio — jak jest zbudowane", "en": "## The Studio — how it is built", "fr": "## Le Studio — comment il est construit"},
    "studio_obszary": {"pl": "Obszary (każdy to osobna aplikacja, bez narzuconej kolejności): {o}.",
                       "en": "Areas (each a separate app, in no fixed order): {o}.",
                       "fr": "Espaces (chacun est une application à part, sans ordre imposé) : {o}."},
    "studio_opis": {"pl": "Każdy wynik trafia do bieżącego **ujęcia** (lewa kolumna; folder `zasoby/<login>/ujecia/<nr-nazwa>/`), "
                          "z plikiem opisu .json (prompt, model, ustawienia, czas). Pasek pod podglądem: szukanie w promptach, ★, porównanie (shift+klik), "
                          "usuwanie (Delete). Każde pole wejściowe przyjmuje plik „z zasobów” albo „z dysku”. Wszystko jest pobieralne. "
                          "Enter wysyła (czat) albo generuje (prompt); Shift+Enter to nowa linia.",
                    "en": "Every result goes into the current **shot** (left column; folder `zasoby/<login>/ujecia/<nr-name>/`), "
                          "with a .json description file (prompt, model, settings, time). The bar under the preview: search in prompts, ★, compare (shift+click), "
                          "delete (Delete). Every input field takes a file “from library” or “from disk”. Everything can be downloaded. "
                          "Enter sends (chat) or generates (prompt); Shift+Enter is a new line.",
                    "fr": "Chaque résultat va dans le **plan** en cours (colonne de gauche ; dossier `zasoby/<login>/ujecia/<nr-nom>/`), "
                          "avec un fichier de description .json (prompt, modèle, réglages, durée). La barre sous l’aperçu : recherche dans les prompts, ★, comparaison (maj+clic), "
                          "suppression (Suppr). Chaque champ d’entrée accepte un fichier « depuis les ressources » ou « depuis le disque ». Tout est téléchargeable. "
                          "Entrée envoie (chat) ou génère (prompt) ; Maj+Entrée fait un saut de ligne."},
    "studio_artefakty": {"pl": "Artefakty .md (folder `artefakty/`) są widoczne w innych obszarach i dla innych uczestników (można ukryć). "
                               "Rozmowy (`rozmowy/`) są prywatne. Do wiadomości w czacie można dołączyć pliki: tekst, PDF, obrazy.",
                         "en": "Artifacts .md (folder `artefakty/`) are visible in other areas and to other participants (can be hidden). "
                               "Conversations (`rozmowy/`) are private. Files can be attached to chat messages: text, PDF, images.",
                         "fr": "Les artefacts .md (dossier `artefakty/`) sont visibles dans les autres espaces et par les autres participants (on peut les masquer). "
                               "Les conversations (`rozmowy/`) sont privées. On peut joindre des fichiers aux messages du chat : texte, PDF, images."},
    "wejscia": {"pl": " Wejścia: {x}.", "en": " Inputs: {x}.", "fr": " Entrées : {x}."},
    "ustawienia": {"pl": " Ustawienia: {x}.", "en": " Settings: {x}.", "fr": " Réglages : {x}."},
    "uczestnik": {"pl": "Rozmawiasz z uczestnikiem o loginie „{l}”. Data: {d}. Język interfejsu uczestnika: polski.",
                  "en": "You are talking with the participant whose login is “{l}”. Date: {d}. The participant’s interface language: English.",
                  "fr": "Tu parles avec le participant dont l’identifiant est « {l} ». Date : {d}. Langue de l’interface du participant : français."},
    "docelowy": {"pl": "## Model docelowy\n**{n}** (`{i}`, obszar Studia: {o}). Prompt zapisujesz narzędziem `zapisz_prompt` z obszarem `{o}`.",
                 "en": "## Target model\n**{n}** (`{i}`, Studio area: {o}). You save the prompt with the `zapisz_prompt` tool, area `{o}`.",
                 "fr": "## Modèle cible\n**{n}** (`{i}`, espace du Studio : {o}). Tu enregistres le prompt avec l’outil `zapisz_prompt`, espace `{o}`."},
    "bez_karty": {"pl": " Dla tego modelu nie ma jeszcze karty — opieraj się na opisie modelu w Studiu (wyżej) i powiedz uczestnikowi, że format promptu jest niepewny.",
                  "en": " There is no model card for this model yet — rely on the model’s description in the Studio (above) and tell the participant the prompt format is uncertain.",
                  "fr": " Il n’y a pas encore de fiche pour ce modèle — appuie-toi sur sa description dans le Studio (plus haut) et dis au participant que le format du prompt est incertain."},
    "biblia": {"pl": "## Biblia utworu — aktualna treść pliku `{p}`\n\n{t}\n\n(Koniec biblii. Zapis do niej: narzędzie `zapisz_sekcje` z tą ścieżką.)",
               "en": "## Piece bible — current content of the file `{p}`\n\n{t}\n\n(End of the bible. To write to it: the `zapisz_sekcje` tool with this path.)",
               "fr": "## Bible de l’œuvre — contenu actuel du fichier `{p}`\n\n{t}\n\n(Fin de la bible. Pour y écrire : l’outil `zapisz_sekcje` avec ce chemin.)"},
    "scenopis": {"pl": "## Scenopis utworu — aktualna treść pliku `{p}`\n\n{t}\n\n(Koniec scenopisu. W promptmakingu: zapytaj, którego ujęcia dotyczy prompt, i weź jego opis ze scenopisu.)",
                 "en": "## Shot list of the piece — current content of the file `{p}`\n\n{t}\n\n(End of the shot list. In promptmaking: ask which shot the prompt is for and take its description from the shot list.)",
                 "fr": "## Découpage de l’œuvre — contenu actuel du fichier `{p}`\n\n{t}\n\n(Fin du découpage. En promptmaking : demande de quel plan il s’agit et prends sa description dans le découpage.)"},
    "temat": {"pl": "Temat tej rozmowy: **{n}**. Zapisy z tej rozmowy idą do biblii pod nagłówkiem `## {n}` (chyba że uczestnik wskaże inny).",
              "en": "Topic of this conversation: **{n}**. What you save from this conversation goes into the bible under the heading `## {n}` (unless the participant names another).",
              "fr": "Thème de cette conversation : **{n}**. Ce que tu enregistres ici va dans la bible sous le titre `## {n}` (sauf si le participant en indique un autre)."},
    "zgoda_uwaga": {"pl": "\n\nUWAGA: w ostatniej wiadomości uczestnik zgodził się na zapis. Zapis teraz zadziała — użyj narzędzia, nie przepraszaj za wcześniejsze odmowy.",
                    "en": "\n\nNOTE: in the last message the participant agreed to saving. Saving will work now — use the tool, don’t apologise for earlier refusals.",
                    "fr": "\n\nATTENTION : dans son dernier message, le participant a accepté l’enregistrement. L’enregistrement va fonctionner — utilise l’outil, ne t’excuse pas des refus précédents."},
    "wyniki": {"pl": "\n\n## Wyniki wyszukiwania do tej odpowiedzi (Studio wykonało je przed Twoją odpowiedzią)\nZapytanie: „{q}”\n{w}\n"
                     "Jeśli coś z tego jest naprawdę bliskie pomysłowi uczestnika — pokaż to rzeczowo z adresem. "
                     "Jeśli nic nie pasuje — powiedz krótko, że nic podobnego nie znalazłeś. Nie dopisuj niczego spoza tej listy.",
               "en": "\n\n## Search results for this reply (the Studio ran the search before your reply)\nQuery: “{q}”\n{w}\n"
                     "If something here is really close to the participant’s idea — show it factually, with its address. "
                     "If nothing fits — say briefly that you found nothing similar. Don’t add anything that is not on this list.",
               "fr": "\n\n## Résultats de recherche pour cette réponse (le Studio a lancé la recherche avant ta réponse)\nRequête : « {q} »\n{w}\n"
                     "Si quelque chose est vraiment proche de l’idée du participant — montre-le sobrement, avec son adresse. "
                     "Si rien ne correspond — dis brièvement que tu n’as rien trouvé de semblable. N’ajoute rien qui ne soit pas dans cette liste."},
    "niedostepne": {"pl": "to narzędzie nie jest dostępne w tym trybie rozmowy", "en": "this tool is not available in this conversation mode",
                    "fr": "cet outil n’est pas disponible dans ce mode de conversation"},
    "odmowa": {"pl": "ODMOWA: uczestnik nie zgodził się na zapis. Nic nie zapisano. Pokaż mu dokładnie to, co chcesz zapisać, i zapytaj jednym zdaniem, czy zapisać.",
               "en": "REFUSED: the participant has not agreed to saving. Nothing was saved. Show them exactly what you want to save and ask in one sentence whether to save it.",
               "fr": "REFUS : le participant n’a pas accepté l’enregistrement. Rien n’a été enregistré. Montre-lui exactement ce que tu veux enregistrer et demande-lui en une phrase s’il faut l’enregistrer."},
    "wstrzymany": {"pl": "zapis wstrzymany — czeka na Twoją zgodę", "en": "saving paused — waiting for your consent", "fr": "enregistrement suspendu — en attente de ton accord"},
    "zapisany_prompt": {"pl": "**Zapisany prompt:**", "en": "**Saved prompt:**", "fr": "**Prompt enregistré :**"},
    "nic_nie_zapisano": {"pl": "\n\n> ⚠ W tej odpowiedzi nic nie zostało zapisane — model tylko o tym napisał. Jeśli chcesz zapisu, napisz wprost „zapisz”.",
                         "en": "\n\n> ⚠ Nothing was saved in this reply — the model only wrote that it did. If you want it saved, say “save” explicitly.",
                         "fr": "\n\n> ⚠ Rien n’a été enregistré dans cette réponse — le modèle l’a seulement écrit. Si tu veux l’enregistrer, écris clairement « enregistre »."},
    "zal_poczatek": {"pl": "--- Załącznik „{n}” (treść) ---", "en": "--- Attachment “{n}” (content) ---", "fr": "--- Pièce jointe « {n} » (contenu) ---"},
    "zal_koniec": {"pl": "--- Koniec załącznika „{n}” ---", "en": "--- End of attachment “{n}” ---", "fr": "--- Fin de la pièce jointe « {n} » ---"},
    "zal_uciete": {"pl": "(ucięte po {n} znakach — reszta pliku nie trafiła do rozmowy)", "en": "(cut after {n} characters — the rest of the file is not in the conversation)",
                   "fr": "(coupé après {n} caractères — le reste du fichier n’est pas dans la conversation)"},
    "zal_pusty": {"pl": "[Załącznik „{n}”: nie udało się z niego wydobyć tekstu]", "en": "[Attachment “{n}”: no text could be extracted]",
                  "fr": "[Pièce jointe « {n} » : impossible d’en extraire le texte]"},
    "zal_obraz": {"pl": "[Obraz z załącznika: {n}]", "en": "[Image from attachment: {n}]", "fr": "[Image jointe : {n}]"},
    "zal_obraz_pominiety": {"pl": "[Obraz „{n}” — tu go nie widzisz (starsza wiadomość albo model bez obrazu); jeśli jest potrzebny, poproś o ponowne dołączenie]",
                            "en": "[Image “{n}” — you can’t see it here (older message or a model without vision); if needed, ask for it to be attached again]",
                            "fr": "[Image « {n} » — tu ne la vois pas ici (message plus ancien ou modèle sans vision) ; si besoin, demande de la joindre à nouveau]"},
    "zal_lokalny": {"pl": "[obraz — zapasowy model lokalny nie widzi obrazów; powiedz o tym uczestnikowi]",
                    "en": "[image — the local backup model can’t see images; tell the participant]",
                    "fr": "[image — le modèle local de secours ne voit pas les images ; dis-le au participant]"},
    "zal_bez_tekstu": {"pl": "(wiadomość bez tekstu — tylko załączniki)", "en": "(message without text — attachments only)", "fr": "(message sans texte — pièces jointes seulement)"},
    "adresy_spoza": {"pl": "Tych adresów nie było w wynikach wyszukiwania — mogą być nieprawdziwe: ",
                     "en": "These addresses were not in the search results — they may be false: ",
                     "fr": "Ces adresses ne figuraient pas dans les résultats de recherche — elles peuvent être fausses : "},
    "adresy_pamiec": {"pl": "Te adresy nie pochodzą z wyszukiwania (model podał je z pamięci) — mogą być nieprawdziwe: ",
                      "en": "These addresses do not come from a search (the model gave them from memory) — they may be false: ",
                      "fr": "Ces adresses ne viennent pas d’une recherche (le modèle les a données de mémoire) — elles peuvent être fausses : "},
}
OBSZARY_NAZWY = {"pl": {"tekst": "Tekst", "mowa": "Mowa", "muzyka": "Muzyka", "sfx": "SFX", "obraz": "Obraz", "wideo": "Wideo"},
                 "en": {"tekst": "Text", "mowa": "Speech", "muzyka": "Music", "sfx": "SFX", "obraz": "Image", "wideo": "Video"},
                 "fr": {"tekst": "Texte", "mowa": "Voix", "muzyka": "Musique", "sfx": "SFX", "obraz": "Image", "wideo": "Vidéo"}}


def tx(klucz: str, jez: str = "pl", **kw) -> str:
    d = S[klucz]
    return (d.get(jez) or d["pl"]).format(**kw) if kw else (d.get(jez) or d["pl"])


def jezyk_rozmowy(r: dict) -> str:
    return r.get("jezyk") if r.get("jezyk") in JEZYKI else "pl"


def wiedza_o_studiu(jez: str = "pl") -> str:
    """Opis Studia dla czatu-pomocnika, generowany z rejestru modeli (zawsze aktualny), w języku rozmowy."""
    nazwy = OBSZARY_NAZWY.get(jez, OBSZARY_NAZWY["pl"])
    linie = [tx("studio_tytul", jez), tx("studio_obszary", jez, o=", ".join(nazwy.values())),
             tx("studio_opis", jez), tx("studio_artefakty", jez), ""]
    for ob, nazwa in nazwy.items():
        ms = by_area(ob)
        if not ms:
            continue
        linie.append(f"### {nazwa}")
        for m in ms:
            opis = L(m.opis, jez)
            wej = ", ".join((L(i.get("etykieta"), jez) or i["id"]) for i in m.wejscia)
            par = ", ".join(p["id"] for p in m.parametry if p["typ"] not in ("prompt", "seed"))
            linie.append(f"- **{m.nazwa_w(jez)}** — {opis}" + (tx("wejscia", jez, x=wej) if wej else "") + (tx("ustawienia", jez, x=par) if par else ""))
        linie.append("")
    return "\n".join(linie)


def prompt_systemowy(login: str, r: dict) -> str:
    """Składa prompt z sekcji (każda: oryginał albo wybrana kopia uczestnika — patrz prompty.py).
    Kolejność: wspólne → lustro → początek/temat → pomoc → opis Studia → biblia → zasady twarde (na końcu)."""
    sekcje = prompty.sekcje_rozmowy(r)
    jez = jezyk_rozmowy(r)
    czesci = [prompty.tresc(login, s, r.get("temat_nazwa"), jez) for s in sekcje[:-1]]
    czesci.append(wiedza_o_studiu(jez))
    czesci.append(tx("uczestnik", jez, l=login, d=time.strftime("%Y-%m-%d")))
    if r.get("tryb") == "prompt":
        m = MODELS.get(r.get("model_docelowy") or "")
        if m:
            czesci.append(tx("docelowy", jez, n=m.nazwa_w(jez), i=m.id, o=m.obszar)
                          + ("" if any(s.startswith("model:") for s in sekcje) else tx("bez_karty", jez)))
    if r.get("tryb") in ("lustro", "prompt"):
        p = prompty.plik_biblii(login, r.get("biblia") or "")
        if p:                                         # czytana przy każdej wiadomości — widać też świeże zapisy
            czesci.append(tx("biblia", jez, p=r["biblia"], t=p.read_text(encoding="utf-8", errors="replace")[:20000]))
            sc = p.with_name(p.name.replace("-biblia.md", "-scenopis.md")) if p.name.endswith("-biblia.md") else None
            if sc and sc.exists():                    # scenopis (osobna notatka obok biblii) — też przy każdej wiadomości
                czesci.append(tx("scenopis", jez, p=r["biblia"].replace("-biblia.md", "-scenopis.md"),
                                 t=sc.read_text(encoding="utf-8", errors="replace")[:15000]))
        if r.get("temat"):
            czesci.append(tx("temat", jez, n=r.get("temat_nazwa") or r["temat"]))
    czesci.append(prompty.tresc(login, "zasady", None, jez))  # twarde zasady na samym końcu — model trzyma się ich najsilniej
    return "\n\n".join(czesci)


# Narzędzia dostępne w danym trybie (lustro pisze do biblii, promptmaking tylko zapisuje prompty).
NARZEDZIA_TRYBU = {
    "rozmowa": {"lista_plikow", "czytaj_plik", "zapisz_notatke", "utworz_folder", "przenies_notatke", "szukaj_w_sieci"},
    "lustro": {"lista_plikow", "czytaj_plik", "zapisz_notatke", "zapisz_sekcje", "szukaj_w_sieci"},
    "prompt": {"lista_plikow", "czytaj_plik", "zapisz_prompt", "szukaj_w_sieci"},
}
ZAPISUJACE = {"zapisz_notatke", "zapisz_sekcje", "zapisz_prompt"}


def _zgoda_na_zapis(r: dict) -> bool:
    """Zgoda sprawdzana w kodzie, nie tylko w prompcie (model potrafi zapisać bez pytania):
    uczestnik w ostatniej wiadomości prosi o zapis albo odpowiada „tak” na pytanie o zapis."""
    ws = r.get("wiadomosci") or []
    ostatnia = max((i for i, w in enumerate(ws) if w["rola"] == "user"), default=None)
    if ostatnia is None:
        return False
    u = ws[ostatnia]["tresc"]
    przed = next((w["tresc"] for w in reversed(ws[:ostatnia]) if w["rola"] == "assistant"), "")
    if re.search(r"\bnie\s+(za|do|w)?pisuj|\bnie\s+(za|do|w)?pisz\b|\bnie\s+(za|do|w)?pisywa|\bnie\s+(za|do|w)?pisać"
                 r"|\bnie\s+(do)?dawaj|\bnie\s+zmieniaj|\bdon'?t\s+(save|write|add|change|update)"
                 r"|\bn[e’']\s*(l[’']|les?\s+|la\s+)?(enregistre|sauvegarde|ajoute|écris|modifie)\s+pas|\bpas\s+d[’']enregistr"
                 r"|\bdo\s+not\s+(save|write|add|change|update)", u, re.I):
        return False                                      # „nie zapisuj”, ale nie „bo nie zapisałeś”
    if re.search(r"zapisz|zapisa[ćł]|zapisuj|zachowaj|wpisz|dopisz|uzupełnij|aktualizuj|dodaj\s+(to\s+|je\s+)?do\b"
                 r"|\bsave\b|\bstore\b|\bwrite\b|\bupdate\b|\badd\s+(it|this|that|them)?\s*to\b|\brecord\b"
                 r"|enregistr|sauvegard|ajoute\s+(ça\s+|le\s+|la\s+|les\s+)?(à|dans)|mets\s+(ça\s+)?à\s+jour|note\s+(ça|le|la)\b|inscris", u, re.I):
        return True
    pytanie = re.search(r"zapis|zachow|wpis|dopis|doda[ćm]|bibli|notat|\bsave|\bwrite|\badd\b|\bupdate|\brecord|\bbible|\bnote"
                        r"|enregistr|sauvegard|ajout|mettre à jour",
                        przed, re.I)
    return bool(pytanie and re.match(r"\s*(tak|ok|okej|okay|dobrze|dobra|zgoda|zgadzam|jasne|pewnie|proszę|śmiało|dawaj|zrób|"
                                     r"yes|yep|yeah|sure|please|go\s+ahead|do\s+it|"
                                     r"oui|ouais|d[’']accord|ok|vas-y|allez|volontiers|bien\s+sûr|carrément|parfait)\b", u, re.I))


def _tytul_biblii(sciezka: str) -> str:
    return re.sub(r"[-_ ]?biblia$", "", Path(sciezka).stem, flags=re.I).replace("-", " ").strip() or "biblia"


def _cel_u_dostawcy(d: str, api_model: str, body: dict, obrazy: bool) -> tuple[str, dict, dict]:
    """Zapytanie w formacie OpenAI do endpointu czatu dostawcy — tylko z parametrami, które dostawca przyjmuje."""
    from . import dostawcy
    mysl = bool((body.get("chat_template_kwargs") or {}).get("enable_thinking"))
    b = {k: v for k, v in body.items() if k != "chat_template_kwargs"}
    b["model"] = api_model
    if d == "lokalne":                                       # Ollama / LM Studio: bez klucza, bez opłat
        if not obrazy and any(isinstance(x.get("content"), list) for x in body.get("messages", [])):
            b["messages"] = [{**x, "content": zalaczniki.tylko_tekst(x["content"], S["zal_lokalny"]["pl"])} for x in body["messages"]]
        return dostawcy.adres_lokalny(), {}, b
    if not obrazy and any(isinstance(x.get("content"), list) for x in body.get("messages", [])):
        b["messages"] = [{**x, "content": zalaczniki.tylko_tekst(x["content"], S["zal_lokalny"]["pl"])} for x in body["messages"]]
    if d == "openrouter":
        b["reasoning"] = {"enabled": mysl}
        b["usage"] = {"include": True}
        b["provider"] = {"data_collection": "deny"}          # bez dostawców, którzy zbierają dane z rozmów
    elif d in ("anthropic", "openai"):
        b.pop("temperature", None)                           # nowsze modele przyjmują tylko domyślną temperaturę
    if b.get("stream") and d != "openrouter":
        b["stream_options"] = {"include_usage": True}
    return dostawcy.DOSTAWCY[d]["chat"], {"Authorization": f"Bearer {dostawcy.klucz(d)}"}, b


def _cele(body: dict) -> list[tuple[str, dict, dict]]:
    """Dokąd wysłać zapytanie: model wybrany w obszarze Tekst (u jego dostawcy, dwie próby), potem pozostałe modele
    tekstowe wybrane w Ustawieniach (zapas), na końcu opcjonalnie stare `llm_api` / lokalny LLM z config.yaml.
    Zwraca listę (adres, nagłówki, treść zapytania)."""
    from . import dostawcy
    cele = []
    mw = MODELS.get(body.get("model") or "")
    tekstowe = [m for m in by_area("tekst") if m.stale.get("chmura")]
    kolejka = ([mw] if mw and mw.stale.get("chmura") else []) + [m for m in tekstowe if m is not mw]
    for i, m in enumerate(kolejka):
        d = m.stale["dostawca"]
        if not dostawcy.klucz(d):
            continue
        cel = _cel_u_dostawcy(d, m.stale["api_model"], body, m.stale.get("obrazy", False))
        cele.append(cel)
        if i == 0:                                   # pierwszy model drugi raz (chwilowe 429 / pusta odpowiedź)
            cele.append(cel)
    klucz = os.environ.get(LLM_API.get("klucz_env", ""), "") if LLM_API else ""
    if klucz and LLM_API.get("model"):               # zgodność ze starym config.yaml (llm_api)
        b = {k: v for k, v in body.items() if k != "chat_template_kwargs"} | {"model": LLM_API["model"]}
        cele.append((LLM_API["url"].rstrip("/"), {"Authorization": f"Bearer {klucz}"}, b))
    if LLM_URL:                                      # lokalny LLM tylko, gdy jest w config.yaml (llm_url)
        lok = dict(body)
        if any(isinstance(x.get("content"), list) for x in body.get("messages", [])):
            lok["messages"] = [{**x, "content": zalaczniki.tylko_tekst(x["content"], S["zal_lokalny"]["pl"])} for x in body["messages"]]
        cele.append((LLM_URL, {}, lok))
    return cele


def _zapisz_uzycie(login: str, tryb: str, usage: dict):
    """Koszt tokenów API — do podglądu wydatków; nie schodzi z budżetu uczestnika."""
    try:
        store.add_llm_usage(login, tryb, int(usage.get("prompt_tokens") or 0), int(usage.get("completion_tokens") or 0),
                            float(usage.get("cost") or 0))
    except Exception:
        traceback.print_exc()


async def _zapytanie_do_researchu(c: httpx.AsyncClient, model: str, hist: list) -> str | None:
    """Krótkie, niestrumieniowe pytanie do modelu: czy w ostatniej wiadomości jest pomysł do sprawdzenia w sieci
    i jakim zapytaniem. Zwraca zapytanie albo None (np. gdy uczestnik tylko potwierdza albo pyta o Studio)."""
    rozmowa = "\n".join(f"{'UCZESTNIK' if w['role'] == 'user' else 'ROZMÓWCA'}: {w['content'][:1500]}" for w in reversed(hist[:6]))
    try:
        zapytanie = {
            "model": model, "temperature": 0.2, "max_tokens": 60, "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content":
                "Na podstawie ostatniej wiadomości uczestnika ułóż JEDNO krótkie zapytanie do wyszukiwarki (po angielsku albo w języku "
                "pomysłu, 4–9 słów), które pozwoli sprawdzić, czy ktoś już zrealizował podobny pomysł artystyczny (film, wideo, "
                "instalacja, dźwięk). Bez danych osobowych, bez cytowania wiersza w całości. Jeśli w ostatniej wiadomości nie ma "
                "nowego pomysłu artystycznego (np. tylko potwierdzenie, zgoda, pytanie techniczne) — odpowiedz dokładnie: BRAK. "
                "Odpowiedz samym zapytaniem albo słowem BRAK."},
                {"role": "user", "content": rozmowa}]}
        resp = None
        for url, nagl, b in _cele(zapytanie):
            try:
                resp = await c.post(url + "/chat/completions", timeout=120, json=b, headers=nagl)
                if resp.status_code == 200:
                    break
            except httpx.HTTPError:
                continue
        q =(resp.json()["choices"][0]["message"].get("content") or "").strip().strip('"„”').splitlines()[0][:150]
        return None if not q or q.upper().startswith("BRAK") else q
    except Exception:
        return None


# --- rozmowy ---

@router.get("/api/rozmowy")
async def lista(req: Request):
    u = _need(req)
    out = []
    for p in sorted(store.user_dir(u, "rozmowy").glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
            if not r.get("wiadomosci") and time.time() - p.stat().st_mtime > 3600:
                p.unlink()                                # pusta rozmowa sprzed godziny — sprzątamy (z niewysłanymi załącznikami)
                import shutil
                shutil.rmtree(zalaczniki.katalog(u, p.stem), ignore_errors=True)
                continue
            out.append({"id": r["id"], "tytul": r.get("tytul") or "—", "zmienione": r.get("zmienione"), "model": r.get("model"),
                        "pusta": not r.get("wiadomosci"),
                        "tryb": r.get("tryb"), "temat": r.get("temat"), "temat_nazwa": r.get("temat_nazwa"), "biblia": r.get("biblia"),
                        "model_docelowy": r.get("model_docelowy")})
        except Exception:
            continue
    return out


@router.post("/api/rozmowy")
async def nowa(req: Request):
    u = _need(req)
    d = await req.json() if req.headers.get("content-length") not in (None, "0") else {}
    rid = time.strftime("%Y%m%d-%H%M%S") + f"-{int(time.time() * 1000) % 1000:03d}"
    r = {"id": rid, "tytul": "", "model": d.get("model"), "utworzone": time.time(), "wiadomosci": [],
         "jezyk": prompty.jezyk(req)}
    if d.get("tryb") == "prompt":
        r["tryb"] = "prompt"
        md = MODELS.get(d.get("model_docelowy") or "")
        if d.get("biblia") and prompty.plik_biblii(u, d["biblia"]):
            r["biblia"] = d["biblia"]
        if md and md.obszar in prompty.MEDIA and r.get("biblia"):
            r.update(model_docelowy=md.id, tytul=f"{_tytul_biblii(r['biblia'])} · prompt · {md.nazwa_w(r['jezyk'])}")
    if d.get("tryb") == "lustro":
        r["tryb"] = "lustro"
        if d.get("biblia") and prompty.plik_biblii(u, d["biblia"]):
            r["biblia"] = d["biblia"]
        if d.get("temat") and r.get("biblia"):
            k = d["temat"]
            nazwa = (d.get("temat_nazwa") or "").strip()[:80] if k == "_inny" else next(
                (t["nazwa"] for t in prompty.tematy(r["jezyk"]) if t["klucz"] == k), None)
            if nazwa:
                r.update(temat=k, temat_nazwa=nazwa, tytul=f"{_tytul_biblii(r['biblia'])} · {nazwa}")
    _zapisz(u, r)
    return r


@router.post("/api/rozmowy/{rid}/biblia")
async def przypnij_biblie(req: Request, rid: str):
    u = _need(req)
    r = _czytaj(u, rid)
    b = (await req.json()).get("biblia") or None
    if b and not prompty.plik_biblii(u, b):
        raise HTTPException(404, K("e_biblia"))
    r["biblia"] = b
    _zapisz(u, r)
    return {"ok": True}


@router.get("/api/rozmowy/{rid}/prompt")
async def pelny_prompt(req: Request, rid: str):
    """Dokładnie to, co dostaje model jako prompt systemowy (bez wyników wyszukiwania doklejanych do pojedynczej odpowiedzi)."""
    u = _need(req)
    return {"prompt": prompt_systemowy(u, _czytaj(u, rid)), "sekcje": prompty.sekcje_rozmowy(_czytaj(u, rid))}


@router.get("/api/rozmowy/{rid}")
async def jedna(req: Request, rid: str):
    return _czytaj(_need(req), rid)


@router.post("/api/rozmowy/{rid}/tytul")
async def tytul(req: Request, rid: str):
    u = _need(req)
    r = _czytaj(u, rid)
    r["tytul"] = ((await req.json()).get("tytul") or "").strip()[:120]
    _zapisz(u, r)
    return {"ok": True}


@router.post("/api/rozmowy/{rid}/usun")
async def usun(req: Request, rid: str):
    u = _need(req)
    p = _plik(u, rid)
    if p.exists():
        p.unlink()
    import shutil
    shutil.rmtree(zalaczniki.katalog(u, rid), ignore_errors=True)
    return {"ok": True}


@router.post("/api/rozmowy/{rid}/wyslij")
async def wyslij(req: Request, rid: str):
    """Dopisuje wiadomość uczestnika i strumieniuje odpowiedź modelu (text/event-stream)."""
    u = _need(req)
    d = await req.json()
    r = _czytaj(u, rid)
    tresc = (d.get("tresc") or "").strip()
    zal = [o for o in (zalaczniki.opis(u, rid, n) for n in (d.get("zalaczniki") or [])[:20]) if o]
    m = MODELS.get(d.get("model") or r.get("model") or "")
    if not (tresc or zal) or not m or m.obszar != "tekst":
        raise HTTPException(400, K("e_pusta_wiad"))
    r["model"] = m.id
    r["tryb"] = d.get("tryb") if d.get("tryb") in ("rozmowa", "lustro", "prompt") else r.get("tryb", "rozmowa")
    if r["tryb"] == "prompt" and not r.get("model_docelowy"):
        raise HTTPException(400, K("e_promptmaking"))
    r["wiadomosci"].append({"rola": "user", "tresc": tresc, "czas": time.time(), **({"zalaczniki": zal} if zal else {})})
    if not r.get("tytul"):
        r["tytul"] = re.sub(r"\s+", " ", tresc)[:70] or ", ".join(z["nazwa"] for z in zal)[:70]
    _zapisz(u, r)

    jz = jezyk_rozmowy(r)
    etykiety = {k: tx("zal_" + k, jz) for k in ("poczatek", "koniec", "uciete", "pusty", "obraz", "obraz_pominiety")}
    hist, dl, z_obrazami = [], 0, 3               # obrazy widzi model w 3 ostatnich wiadomościach z obrazami
    for w in reversed(r["wiadomosci"]):
        tw = w["tresc"] or (tx("zal_bez_tekstu", jz) if w.get("zalaczniki") else "")
        obrazki = any(z["rodzaj"] == "obraz" or z.get("strony_obrazy") for z in w.get("zalaczniki") or [])
        content, ile = zalaczniki.dla_modelu(u, rid, tw, w.get("zalaczniki") or [], etykiety, z_obrazami > 0)
        z_obrazami -= 1 if obrazki else 0
        dl += ile
        if dl > HISTORIA_ZNAKOW and hist:
            break
        hist.append({"role": w["rola"], "content": content})
    msgs = [{"role": "system", "content": prompt_systemowy(u, r)}] + list(reversed(hist))
    body = {"model": m.stale.get("llm_model", m.id), "messages": msgs, "stream": True,
            "temperature": float(d.get("temperatura", 0.4 if r.get("tryb") in ("lustro", "prompt") else m.stale.get("temperatura", 0.7))),
            "chat_template_kwargs": {"enable_thinking": bool(d.get("mysl", False))}}
    # research w lustrze tylko wtedy, gdy obowiązujący prompt lustra o nim mówi (uczestnik może go wyciąć w swojej kopii)
    research = bool(narzedzia.SEARX_URL) and (r.get("tryb") != "lustro"
                                              or "szukaj_w_sieci" in prompty.tresc(u, "lustro", None, jezyk_rozmowy(r)))
    if m.stale.get("narzedzia", True):
        dozwolone = NARZEDZIA_TRYBU.get(r.get("tryb") or "rozmowa", NARZEDZIA_TRYBU["rozmowa"])
        body["tools"] = [t for t in narzedzia.spec(jezyk_rozmowy(r)) if t["function"]["name"] in dozwolone
                         and (research or t["function"]["name"] != "szukaj_w_sieci")]

    jez = jezyk_rozmowy(r)

    async def strumien():
        odp, mysl, uzyte, t0 = [], [], [], time.time()
        nowa_biblia = None
        zapisane_prompty = []                             # pokazujemy je zawsze, nawet gdy model ich nie wypisał
        zapisano_cos = False                              # czy w tej odpowiedzi naprawdę coś zapisano
        zgoda = _zgoda_na_zapis(r)
        if zgoda and body.get("tools"):                   # model po wcześniejszej odmowie potrafi już nawet nie próbować
            body["messages"][0]["content"] += tx("zgoda_uwaga", jez)
        dozwolone_teraz = {t["function"]["name"] for t in body.get("tools", [])}
        zrodla = ""                                       # wszystko, co zwróciło wyszukiwanie — do sprawdzenia adresów
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(900, connect=10)) as c:
                if r.get("tryb") == "lustro" and research:
                    # research PRZED odpowiedzią: model układa zapytanie, Studio szuka, wyniki idą do kontekstu —
                    # dzięki temu przywołuje tylko to, co naprawdę znalazł (bez źródeł z pamięci)
                    zap = await _zapytanie_do_researchu(c, body["model"], hist)
                    if zap:
                        info = narzedzia.opis("szukaj_w_sieci", {"zapytanie": zap}, jez)
                        uzyte.append(info)
                        yield "data: " + json.dumps({"n": info}, ensure_ascii=False) + "\n\n"
                        wynik = await narzedzia.wykonaj(u, "szukaj_w_sieci", {"zapytanie": zap}, jez)
                        zrodla += wynik
                        body["messages"][0]["content"] += tx("wyniki", jez, q=zap, w=wynik)
                cele = _cele(body)
                for _ in range(8):                                   # najwyżej 8 rund (narzędzia + ponowienia pustych odpowiedzi)
                    wywolania, koniec = {}, None
                    while True:                                      # błąd API → następny cel (bez przerwy w rozmowie)
                        url, nagl, b = cele[0]
                        b["messages"] = body["messages"]
                        resp_cm = c.stream("POST", url + "/chat/completions", json=b, headers=nagl)
                        try:
                            resp = await resp_cm.__aenter__()
                        except httpx.HTTPError as e:
                            if len(cele) > 1:
                                print(f"LLM {b.get('model')}: {e!r} — następny cel", flush=True)
                                cele.pop(0)
                                await asyncio.sleep(2)
                                continue
                            raise
                        if resp.status_code != 200:
                            tresc = (await resp.aread())[:300]
                            await resp_cm.__aexit__(None, None, None)
                            if resp.status_code in (400, 500) and b"tools" in tresc.lower() and b.get("tools"):
                                b.pop("tools", None)                 # model lokalny bez narzędzi — rozmowa bez nich
                                continue
                            if resp.status_code == 400 and b"easoning is mandatory" in tresc and (b.get("reasoning") or {}).get("enabled") is False:
                                b["reasoning"] = {"enabled": True}       # model, który zawsze „myśli” (np. GLM FlashX)
                                continue
                            if len(cele) > 1:
                                print(f"LLM {b.get('model')} {resp.status_code}: {tresc!r} — następny cel", flush=True)
                                cele.pop(0)
                                await asyncio.sleep(2)
                                continue
                            raise RuntimeError(K("e_llm", m=f"{resp.status_code}: {tresc!r}"))
                        break
                    try:
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: ") or line.strip() == "data: [DONE]":
                                continue
                            chunk = json.loads(line[6:])
                            if chunk.get("error"):                   # błąd dostawcy w środku strumienia
                                print(f"LLM {b.get('model')} błąd w strumieniu: {str(chunk['error'])[:200]}", flush=True)
                                koniec = koniec or "error"
                            koniec = (chunk.get("choices") or [{}])[0].get("finish_reason") or koniec
                            if chunk.get("usage") and nagl:
                                _zapisz_uzycie(u, r.get("tryb") or "rozmowa", chunk["usage"])
                            delta = (chunk.get("choices") or [{}])[0].get("delta") or {}
                            rozum = delta.get("reasoning_content") or delta.get("reasoning")
                            if rozum:
                                mysl.append(rozum)
                                yield "data: " + json.dumps({"r": rozum}, ensure_ascii=False) + "\n\n"
                            if delta.get("content"):
                                odp.append(delta["content"])
                                yield "data: " + json.dumps({"t": delta["content"]}, ensure_ascii=False) + "\n\n"
                            for tc in delta.get("tool_calls") or []:
                                w = wywolania.setdefault(tc.get("index", 0), {"id": "", "name": "", "args": ""})
                                w["id"] = tc.get("id") or w["id"]
                                fn = tc.get("function") or {}
                                w["name"] += fn.get("name") or ""
                                w["args"] += fn.get("arguments") or ""
                    finally:
                        await resp_cm.__aexit__(None, None, None)
                    if not wywolania and not "".join(odp).strip():   # strumień urwany albo pusty — nic nie przyszło
                        print(f"LLM {b.get('model')}: pusta odpowiedź (finish={koniec})"
                              + (" — następny cel" if len(cele) > 1 else ""), flush=True)
                        if len(cele) > 1:
                            cele.pop(0)
                            await asyncio.sleep(2)
                            continue
                        raise RuntimeError(K("e_llm_pusta"))
                    if not wywolania:
                        break
                    body["messages"].append({"role": "assistant", "content": "".join(odp) or None, "tool_calls": [
                        {"id": w["id"] or f"w{i}", "type": "function", "function": {"name": w["name"], "arguments": w["args"] or "{}"}}
                        for i, w in sorted(wywolania.items())]})
                    for i, w in sorted(wywolania.items()):
                        try:
                            args = json.loads(w["args"] or "{}")
                        except json.JSONDecodeError:
                            args = {}
                        if w["name"] not in dozwolone_teraz:
                            wynik = tx("niedostepne", jez)
                        elif w["name"] in ZAPISUJACE and not zgoda:
                            wynik = tx("odmowa", jez)
                            info = tx("wstrzymany", jez)
                            uzyte.append(info)
                            yield "data: " + json.dumps({"n": info, "zgoda": True}, ensure_ascii=False) + "\n\n"
                        else:
                            info = narzedzia.opis(w["name"], args, jez)
                            uzyte.append(info)
                            yield "data: " + json.dumps({"n": info}, ensure_ascii=False) + "\n\n"
                            wynik = await narzedzia.wykonaj(u, w["name"], args, jez,
                                                            {"model": r.get("model_docelowy"), "biblia": r.get("biblia")})
                        if w["name"] in ZAPISUJACE and narzedzia.udany_zapis(wynik):
                            zapisano_cos = True
                        if w["name"] == "zapisz_prompt" and narzedzia.udany_zapis(wynik):
                            zapisane_prompty.append(args.get("tresc") or "")
                        if w["name"] == "szukaj_w_sieci":
                            zrodla += wynik
                        if w["name"] == "zapisz_notatke" and narzedzia.udany_zapis(wynik) and "biblia" in wynik.lower():
                            sc = re.search(r"\S+/artefakty/\S+\.md", wynik)          # „login/artefakty/x.md” → „artefakty/x.md”
                            nowa_biblia = sc.group(0).split("/", 1)[-1] if sc else None
                        body["messages"].append({"role": "tool", "tool_call_id": w["id"] or f"w{i}", "content": wynik})
                    odp = []
                if not "".join(odp).strip() and not zapisane_prompty:   # wyczerpane rundy — nie zostawiamy samych kropek
                    raise RuntimeError(K("e_llm_pusta"))
        except httpx.ConnectError:                     # ani API (brak klucza / nie odpowiada), ani lokalny LLM
            yield "data: " + json.dumps({"blad": przetlumacz(K("e_brak_llm"), jez)}, ensure_ascii=False) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"blad": przetlumacz(str(e), jez)[:400]}, ensure_ascii=False) + "\n\n"
        finally:
            tekst = "".join(odp)
            for pr in zapisane_prompty:
                if pr.strip() and pr.strip()[:80] not in tekst:
                    blok = "\n\n" + tx("zapisany_prompt", jez) + "\n```\n" + pr.strip() + "\n```"
                    odp.append(blok)
                    tekst += blok
                    yield "data: " + json.dumps({"t": blok}, ensure_ascii=False) + "\n\n"
            if not zapisano_cos and re.search(r"\b(zapisa(łem|łam|no)|zapisane|zapisuję|dopisa(łem|łam|no|ne)|uzupełni(łem|łam)"
                                              r"|I(’|')ve saved|I saved|I(’|')ve added|I(’|')ve updated|saved (it|this|the)|has been saved"
                                              r"|j(’|')ai enregistré|j(’|')ai ajouté|j(’|')ai mis à jour|enregistré dans|c(’|')est enregistré)\b", tekst, re.I):
                uwaga = tx("nic_nie_zapisano", jez)
                odp.append(uwaga)
                tekst += uwaga
                yield "data: " + json.dumps({"t": uwaga}, ensure_ascii=False) + "\n\n"
            obce = [x.rstrip(".,;:!?") for x in re.findall(r"https?://[^\s)\]>\"'`]+", tekst)]
            obce = sorted({x for x in obce if x not in zrodla and x not in msgs[0]["content"]})   # adresy z biblii/karty modelu są znane
            if obce:                                      # adresy spoza wyników wyszukiwania — ostrzeżenie dla uczestnika
                uwaga = "\n\n> ⚠ " + tx("adresy_spoza" if zrodla else "adresy_pamiec", jez) + ", ".join(obce)
                odp.append(uwaga)
                yield "data: " + json.dumps({"t": uwaga}, ensure_ascii=False) + "\n\n"
            if odp:
                r2 = _czytaj(u, rid)
                if nowa_biblia and r2.get("tryb") == "lustro" and not r2.get("biblia"):
                    r2["biblia"] = nowa_biblia
                r2["wiadomosci"].append({"rola": "assistant", "tresc": "".join(odp), "czas": time.time(),
                                         "model": m.id, "mysl": "".join(mysl) or None, "narzedzia": uzyte or None,
                                         "czas_s": round(time.time() - t0, 1)})
                _zapisz(u, r2)
        yield "data: " + json.dumps({"koniec": True}) + "\n\n"

    return StreamingResponse(strumien(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


# --- artefakty .md ---

def _art_public(a: dict) -> dict:
    czesci = a["sciezka"].split("/")
    folder = "/".join(czesci[2:-1]) if len(czesci) > 3 and czesci[1] == "artefakty" else ""
    return {"id": a["id"], "nazwa": a["nazwa"], "folder": folder, "login": a["login"], "ukryte": bool(a["ukryte"]),
            "utworzone": a["utworzone"], "url": f"/pliki/{a['id']}"}


@router.get("/api/artefakty")
async def art_lista(req: Request, kto: str = "ja"):
    u = _need(req)
    return [_art_public(a) for a in store.list_assets(u, kto, "tekst", None, None, False, "")]


@router.get("/api/prompty-obszaru")
async def prompty_obszaru(req: Request, obszar: str, model: str = ""):
    """Zapisane prompty tylko dla tego obszaru (artefakty/prompty/<obszar>/): najpierw dla wybranego modelu, potem najnowsze."""
    u = _need(req)
    out = []
    for a in store.list_assets(u, "ja", "tekst", None, None, False, ""):
        if _art_public(a)["folder"] != f"prompty/{obszar}":
            continue
        try:
            meta = json.loads(a.get("meta") or "{}")
        except ValueError:
            meta = {}
        try:
            t = (store.ZASOBY / a["sciezka"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        podglad = re.sub(r"^```\w*\n|\n```\s*$", "", t.strip())[:220]
        m = meta.get("model")
        out.append({"id": a["id"], "nazwa": re.sub(r"\.md$", "", a["nazwa"]), "utworzone": a["utworzone"], "model": m,
                    "model_nazwa": (MODELS[m].nazwa_w(jezyk_rozmowy({"jezyk": prompty.jezyk(req)})) if m in MODELS else None),
                    "ten_model": bool(model and m == model), "biblia": (meta.get("biblia") or "").rsplit("/", 1)[-1].replace("-biblia.md", "") or None,
                    "jednostka": meta.get("jednostka"), "podglad": podglad})
    out.sort(key=lambda x: (not x["ten_model"], -x["utworzone"]))
    return out


@router.get("/api/artefakty/{aid}")
async def art_czytaj(req: Request, aid: int):
    u = _need(req)
    a = store.asset(aid)
    if not a or a["rodzaj"] != "tekst" or (a["ukryte"] and a["login"] != u):
        raise HTTPException(404)
    return {**_art_public(a), "tresc": (store.ZASOBY / a["sciezka"]).read_text(encoding="utf-8", errors="replace")}


@router.post("/api/artefakty")
async def art_nowy(req: Request):
    u = _need(req)
    d = await req.json()
    nazwa = store.slug(d.get("nazwa") or "notatka") or "notatka"
    folder = store.user_dir(u, "artefakty")
    p, i = folder / f"{nazwa}.md", 2
    while p.exists():
        p, i = folder / f"{nazwa}-{i}.md", i + 1
    p.write_text(d.get("tresc") or "", encoding="utf-8")
    uid = d.get("ujecie") or store.default_ujecie(u)["id"]
    aid = store.add_asset(u, "tekst", "artefakt", p, p.name, "tekst", None, None, {"zrodlo": d.get("zrodlo")}, ujecie_id=uid)
    return _art_public(store.asset(aid))


@router.post("/api/artefakty/{aid}")
async def art_zapisz(req: Request, aid: int):
    u = _need(req)
    a = store.asset(aid)
    if not a or a["rodzaj"] != "tekst" or a["login"] != u:
        raise HTTPException(404)
    (store.ZASOBY / a["sciezka"]).write_text((await req.json()).get("tresc") or "", encoding="utf-8")
    return {"ok": True}


@router.post("/api/artefakty/{aid}/nazwa")
async def art_nazwa(req: Request, aid: int):
    """Zmiana nazwy notatki. Biblia zostaje biblią (końcówka „-biblia”), rozmowy przypięte do niej idą za nią."""
    u = _need(req)
    a = store.asset(aid)
    if not a or a["rodzaj"] != "tekst" or a["login"] != u:
        raise HTTPException(404)
    stara = store.ZASOBY / a["sciezka"]
    nazwa = store.slug((await req.json()).get("nazwa") or "")
    if not nazwa:
        raise HTTPException(400, K("e_pusta_nazwa"))
    if "biblia" in stara.name.lower() and "biblia" not in nazwa:
        nazwa += "-biblia"
    nowa = stara.with_name(f"{nazwa}.md")
    if nowa == stara:
        return _art_public(a)
    if nowa.exists():
        raise HTTPException(409, K("e_nazwa_zajeta"))
    stara.rename(nowa)
    with store.db() as c:
        c.execute("UPDATE assets SET sciezka=?, nazwa=? WHERE id=?", (store.rel(nowa), nowa.name, aid))
    rel_stara, rel_nowa = a["sciezka"].split("/", 1)[1], store.rel(nowa).split("/", 1)[1]   # „artefakty/…”
    for p in store.user_dir(u, "rozmowy").glob("*.json"):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if r.get("biblia") == rel_stara:
            r["biblia"] = rel_nowa
            if r.get("tytul", "").startswith(_tytul_biblii(rel_stara)):
                r["tytul"] = _tytul_biblii(rel_nowa) + r["tytul"][len(_tytul_biblii(rel_stara)):]
            p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return _art_public(store.asset(aid))



# --- załączniki ---

@router.post("/api/rozmowy/{rid}/zalaczniki")
async def zal_dodaj(req: Request, rid: str, pliki: list[UploadFile] = File(...)):
    u = _need(req)
    _czytaj(u, rid)
    return [await zalaczniki.zapisz(u, rid, p) for p in pliki[:10]]


@router.get("/api/rozmowy/{rid}/zalaczniki/{nazwa}")
async def zal_plik(req: Request, rid: str, nazwa: str):
    u = _need(req)
    _plik(u, rid)
    return FileResponse(zalaczniki.plik(u, rid, nazwa))


@router.post("/api/rozmowy/{rid}/zalaczniki/{nazwa}/usun")
async def zal_usun(req: Request, rid: str, nazwa: str):
    u = _need(req)
    _plik(u, rid)
    if not any(nazwa == z["nazwa"] for w in _czytaj(u, rid)["wiadomosci"] for z in w.get("zalaczniki") or []):
        zalaczniki.usun(u, rid, nazwa)                # tylko niewysłane — wysłane zostają przy wiadomości
    return {"ok": True}



# --- opis → prompt w JSON (np. Ideogram 4: model rozumie tylko JSON; nasz workflow nie ma działającego „magic promptu”) ---

PROMPT_JSON = """Jesteś konwerterem promptów dla modelu generującego obrazy. Poniżej karta modelu — opisuje dokładnie, jakiego JSON-a model oczekuje.

{karta}

ZADANIE: zamień tekst uczestnika na JEDEN kompletny prompt w JSON zgodny z kartą (klucze, ich kolejność, bbox, palety #RRGGBB wielkimi literami).
- Tekst uczestnika może być zwykłym opisem, notatką albo niepełnym/zepsutym JSON-em — zachowaj jego treść i pomysł, uzupełnij brakujące pola, napraw błędy.
- Nie dodawaj postaci, przedmiotów ani napisów, których uczestnik nie opisał; dopowiadaj tylko to, czego wymaga format (styl, światło, tło, układ).
- Napisy do wyrysowania (pole "text") przepisuj ZNAK PO ZNAKU z tekstu uczestnika — nie tłumacz, nie skracaj, nie poprawiaj, nie zmieniaj końcówek (np. „premiera 22.10” zostaje „premiera 22.10”). Nie dziel słów; znak nowej linii tylko między słowami, gdy napis ma mieć kilka linii. Pozostałe pola opisowe po angielsku.
- Kadr ma proporcje {proporcje} — bbox liczony względem całego kadru.
- Odpowiedz WYŁĄCZNIE samym obiektem JSON: bez komentarza, bez ```."""


# LLM potrafi wstawić w łaciński napis cyrylicką literę, która wygląda tak samo (а, е, о…) — model obrazu narysuje ją źle
_PODROBKI = str.maketrans("АВЕКМНОРСТХаеорсухіјѕ", "ABEKMHOPCTXaeopcyxijs")


def _popraw_napisy(o):
    if isinstance(o, dict):
        return {k: (v.translate(_PODROBKI) if k == "text" and isinstance(v, str) and re.search(r"[A-Za-z]", v) else _popraw_napisy(v))
                for k, v in o.items()}
    if isinstance(o, list):
        return [_popraw_napisy(x) for x in o]
    return o


@router.post("/api/prompt-json")
async def prompt_json(req: Request):
    u = _need(req)
    d = await req.json()
    mid = d.get("model") or ""
    karta = prompty.karty().get(mid)
    opis = (d.get("opis") or "").strip()[:8000]
    if not opis or not karta or mid not in MODELS:
        raise HTTPException(400, K("e_json_model"))
    tekst_karty = prompty.plik(f"modele/{karta}.md", prompty.jezyk(req)).read_text(encoding="utf-8")
    czat = next(iter(by_area("tekst")), None)
    msgs = [{"role": "system", "content": PROMPT_JSON.format(karta=tekst_karty, proporcje=str(d.get("proporcje") or "16:9"))},
            {"role": "user", "content": opis}]
    async with httpx.AsyncClient(timeout=httpx.Timeout(240, connect=10)) as c:
        for proba in range(2):
            body = {"model": (czat.stale.get("llm_model", czat.id) if czat else "qwen-czat"), "messages": msgs, "temperature": 0.2,
                    "max_tokens": 4000, "chat_template_kwargs": {"enable_thinking": False}}
            odp = None
            for url, nagl, b in _cele(body):
                try:
                    r = await c.post(url + "/chat/completions", json=b, headers=nagl)
                except httpx.HTTPError:
                    continue
                if r.status_code == 200:
                    odp = r.json()
                    break
            if not odp:
                raise HTTPException(502, K("e_json_llm"))
            if odp.get("usage"):
                _zapisz_uzycie(u, "json", odp["usage"])
            tekst = odp["choices"][0]["message"].get("content") or ""
            j = narzedzia.jako_json(tekst)
            if j and "compositional_deconstruction" in j:
                return {"json": narzedzia.jako_json(json.dumps(_popraw_napisy(json.loads(j)), ensure_ascii=False))}
            msgs += [{"role": "assistant", "content": tekst[:6000]},
                     {"role": "user", "content": "To nie jest poprawny, kompletny obiekt JSON zgodny z kartą. Odpowiedz jeszcze raz — samym JSON-em."}]
    raise HTTPException(502, K("e_json_niepoprawny"))
