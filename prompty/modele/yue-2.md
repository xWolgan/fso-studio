<!-- Karta modelu dla promptmakera. modele: yue-2, yue-2-cover -->
# YuE 2 (YuE2-3B, m-a-p / HKUST, 09.2026) — tekst na muzykę i cover z nagrania

## Czym jest i do czego się nadaje
- **Model piosenek** (lyrics-to-song), 3B, architektura AR–NAR z flow matching. Najpierw pisze **partyturę w notacji ABC** (melodia + akordy), potem z niej tokeny muzyki i dźwięk 48 kHz stereo [4][5] (oficjalne).
- Tryby planowania: **full** (melodia + akordy; domyślny dla nowych utworów), **melody** (sama melodia, akompaniament swobodniej; zalecany do coverów), **off** (bez partytury) [4][5] (oficjalne). Studio: „YuE 2” = full z planowaniem ABC; „YuE 2 · cover” = melody z partyturą odczytaną z nagrania [1][2] (nasza konfiguracja).
- **Cover** = nagranie → SheetSage2 → melodia w ABC → YuE2 z **nowym stylem i tekstem**. Nagranie **nie jest** warunkowaniem dźwiękowym: nie przenosi barwy, głosu ani miksu, tylko melodię [6][9] (oficjalne).
- Mocne: forma piosenki, aranże „często przekonujące”, bliskie ludzkiej produkcji (EN, FR, PT-BR, ID) [13] (społeczność); autorzy: konkurencyjny z Suno v5/v6 na WildSongBench (pomiar autorów) [4] (oficjalne).
- **Czego NIE robi dobrze:**
  - **utworów instrumentalnych „z pudełka”**: oficjalny przepis na instrumental przenosi nuty partii Vocal do partii Ins **przed** renderem — Studio tego **nie robi** [7] (oficjalne), [2] (nasza konfiguracja) → ryzyko głosu/wokalizy (patrz pułapki);
  - wokal: niemal we wszystkich językach „rozpoznawalnie syntetyczny” [13] (społeczność); wymowa (PER) gorsza niż Suno v6, samogłoski trzeba sprawdzać uchem [14] (społeczność);
  - **polski — brak oficjalnego wsparcia**: oficjalnie dokumentowane EN i ZH (ComfyUI wymienia też japoński) [9] (oficjalne); praktycy: dema EN/ZH/JA/ES, „inne języki mogą działać” [14]; MindStudio wymienia polski wśród testowanych bez oceny jakości [13] (społeczność);
  - brak wejścia „referencja audio”, BPM, negatywu, wyrównania fonemów [5] (oficjalne).

## Co uczestnik ustawia w Studiu
**YuE 2 (tekst na muzykę)** [1][2] (nasza konfiguracja):
| Pole | Wartości | Dokąd trafia / wpływ |
|---|---|---|
| **styl** | tekst | `style` → i planista partytury (ABC), i generator; w prompcie modelu to sekcja `[Tags]` [2][10] |
| **słowa / struktura** | tekst; domyślnie `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` | `lyrics` → sekcja `[Lyrics]` [2][10] |
| **maks. długość (s)** | 10–300, domyślnie 60 | górna granica; utwór może skończyć się wcześniej [9] |
| **seed** | liczba | wspólny dla partytury i dźwięku [2] |

**YuE 2 · cover z nagrania** [1][3] (nasza konfiguracja):
| Pole | Wartości | Dokąd trafia / wpływ |
|---|---|---|
| **nagranie (melodia)** | plik dźwiękowy, wymagany | SheetSage2 w trybie `melody` → ABC (sama melodia) [3][11] |
| **styl** | tekst | docelowe brzmienie (nie oryginału!) [6] |
| **słowa / struktura** | tekst; domyślnie jak wyżej | tekst do zaśpiewania na odczytaną melodię [6] |
| **maks. długość (s)** | 10–360, domyślnie 120 | górna granica [9] |
| **seed** | liczba | |

- Stałe: partytura — temperature 0,7, top_p 0,9, top_k 30, maks. 8192 tokeny ABC; muzyka — temperature 1, top_p 0,95, top_k 100, repetition 1,2; CFG 1,0 (= bez guidance); render 32 kroki [2][3] (nasza konfiguracja) — wartości domyślne węzłów ComfyUI [11] (oficjalne).
- **Partytury (ABC) uczestnik w Studiu nie widzi i nie edytuje** — choć model to umożliwia [4] (oficjalne), [1] (nasza konfiguracja).
- **Negatywu brak**; przy CFG 1,0 gałąź negatywna nie jest liczona [10] (kod ComfyUI).

## Format promptu
- **Styl: jedna linia, deskryptory po przecinkach, po angielsku.** Kolejność z oficjalnego przewodnika ComfyUI: **Język + Gatunek + Charakter wokalu + Tempo + Instrumenty + Cechy muzyczne** [9] (oficjalne). Oficjalne przykłady:
  - „English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM” [5] (oficjalne);
  - „Instrumental, expressive chamber string ensemble, lyrical violin melody, warm viola and cello accompaniment, G major, 96 BPM, a repeated opening phrase followed by a short gentle ending, natural concert hall acoustics, no vocals, no singing, no choir, no spoken words.” [7] (oficjalne).
- **Tempo, tonacja (i metrum) w stylu** — nie ma osobnych pól; partytura zapisuje tempo i metrum, styl ma je opisywać zgodnie [5] (oficjalne).
- **Styl krótko**: długi prompt automatycznie **zmniejsza budżet długości** (kontekst 24 576 tokenów = prompt + partytura + muzyka po 25 tokenów/s) [9][10] (oficjalne). Oficjalne style mają ~15–35 słów.
- **Słowa: tylko to, co ma być zaśpiewane**, + znaczniki sekcji w nawiasach kwadratowych, każdy w osobnej linii, **pusta linia między sekcjami** [5][9] (oficjalne). Polecenia muzyczne — wyłącznie w stylu [9].
- **Znaczniki — co jest udokumentowane dla YuE2:**
  - przewodniki: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` [9] (oficjalne);
  - w oficjalnym kodzie instrumentalnym: planowanie z `[Intro]`, `[Verse]`, `[Chorus]`, `[Outro]`, a końcowe znaczniki biorą się z nazw sekcji partytury (`% verse`, `% chorus`, `% bridge`, `% interlude` → `[Verse]`, `[Chorus]`, `[Bridge]`, `[Interlude]`) [7][8] (oficjalne);
  - `[Instrumental]` i `[Solo]` (domyślne w Studiu) **nie występują w dokumentacji YuE2** — działają technicznie (test API Studia) [12] (nasza konfiguracja), ale ich znaczenie dla modelu niepotwierdzone.
- **Nawiasy z didaskaliami w słowach** (np. „(instrumental theme)”) — nie: w słowach tylko słowa do zaśpiewania [9], a w instrumentalu oficjalnie słowa muszą być **puste albo same znaczniki** [7] (oficjalne). Tekst w nawiasie może zostać zaśpiewany (wniosek).
- **Uwaga na wersje:** YuE (v1, 2025; osobne modele 7B + 1B, inny pipeline) to inny model — nie używaj poradników do v1 [15] (oficjalne). Wszystko tu dotyczy YuE2-3B.

## Szkielet promptu
Piosenka — styl:
```
[Język: English / Polish], [gatunek], [głos: płeć, barwa, sposób], [N BPM], [tonacja jeśli ważna], [2–4 instrumenty], [cecha melodii/frazowania], [przestrzeń/nagranie]
```
Piosenka — słowa:
```
[Verse]
[wers]
[wers]

[Chorus]
[wers]
[wers]

[Bridge]
[wers]

[Outro]
[wers]
```
Instrumental — styl (oficjalny wzór otwarcia i zamknięcia):
```
Instrumental, [gatunek/faktura], [instrument prowadzący + rola], [akompaniament], [tonacja], [N BPM], [przebieg: jak się zaczyna i kończy], [przestrzeń/nagranie], no vocals, no singing, no choir, no spoken words.
```
Instrumental — słowa: same znaczniki (np. domyślne Studia albo `[Intro]` / `[Verse]` / `[Interlude]` / `[Outro]`), bez żadnych słów.

## Co działa
- **Styl i słowa rozdzielnie** — styl = brzmienie, słowa = tekst + sekcje [5][9] (oficjalne).
- **Język na początku stylu** („English, …”) — tak wyglądają wszystkie oficjalne przykłady piosenek [5][9] (oficjalne). Dla polskiego: „Polish, …” przez analogię (niepotwierdzone).
- **Wykluczenia jako lista na końcu stylu** („no guitar”, „no vocals”) — oficjalny przykład stylu jazzowego zawiera „no guitar”, przepis instrumentalny cztery „no …” [7][8] (oficjalne).
- **Krótki akapit stylu lepszy niż sterta tagów** [14] (społeczność).
- **Stały seed** przy porównywaniu zmian stylu; ten sam seed na innym sprzęcie/wersji może dać inny wynik [4][8] (oficjalne).
- **Cover**: najprościej zachować oryginalny tekst i zmienić tylko styl; mocniejsza reinterpretacja — zmień oba [6] (oficjalne).
- **Zmiana języka tekstu w coverze**: adaptuj do śpiewu (sylaby, akcenty, długie samogłoski na długich nutach, oddechy), nie tłumacz słowo w słowo [8] (oficjalne).

## Biasy i pułapki
- **Instrumental bywa zaśpiewany.** Model jest z natury piosenkowy; oficjalny instrumental działa dzięki przeniesieniu melodii z partii Vocal do Ins, a autorzy i tak piszą, że „nie gwarantuje braku głosu” [7] (oficjalne). Studio tego kroku nie ma [2] → **zawsze styl zaczynaj od „Instrumental,” i kończ „no vocals, no singing, no choir, no spoken words.”** [7], słowa bez słów; odsłuchaj; przy głosie zmień seed. Czy studyjny instrumental YuE nie śpiewa — wciąż do odsłuchu [12] (nasza konfiguracja).
- **Budżet długości**: za długi styl/tekst skraca utwór; za niska „maks. długość” urywa w pół frazy [9] (oficjalne). Długość wyznacza głównie partytura i tekst — krótki tekst = krótki utwór [9] (oficjalne).
- **Wymowa** — sprawdzaj każdą wersję; samogłoski i frazowanie „wymagają ludzkiego ucha” [14] (społeczność). Polski nieudokumentowany → krótka próba przed długim utworem.
- **Odchylenia od partytury**: dokładna realizacja nut i długości nie jest gwarantowana [7][8] (oficjalne).
- **Słaby w hindi/urdu** [13] (społeczność) — sygnał, że języki spoza głównych danych wypadają gorzej (wniosek).

## Cover z nagrania — zasady
- **Styl opisuje brzmienie docelowe, nie oryginał** [6] (oficjalne).
- **Nowy tekst blisko frazowania i liczby sylab oryginału** — lepsze dopasowanie do melodii [6][9] (oficjalne). Sekcje i kolejność tekstu zgodne z kolejnością w nagraniu [6][16] (oficjalne).
- **Nagranie**: błędy transkrypcji przechodzą do coveru [16] (oficjalne) — wybieraj fragment z wyraźną, jedną linią melodyczną (wniosek). SheetSage2 w trybie melody bierze melodię wokalu albo prowadzącą melodię instrumentalną [8] (oficjalne).
- **Maks. długość ≥ długość melodii z nagrania** — partytura obejmuje całe nagranie; za niski limit urwie utwór (wniosek z [9]). Domyślne 120 s; oficjalny szablon ComfyUI ma 360 [11] (oficjalne).
- **Cover instrumentalny**: oficjalnie także wymaga przeniesienia Vocal → Ins [17] (oficjalne) — w Studiu go nie ma, więc melodia zaśpiewana w oryginale najpewniej wróci jako głos/wokaliza (wniosek). Jeśli uczestnik chce instrumentalu z melodii — uprzedź i odsłuchajcie.
- Cover nie zachowuje głosu wykonawcy ani falowej postaci nagrania; to nowa realizacja tej samej melodii [5][17] (oficjalne).

## Poza fotorealizmem (w muzyce: poza konwencją — faktura, taśma, lo-fi, abstrakcja)
- Dokumentacja YuE2 **nie opisuje** stylów lo-fi, taśmy ani abstrakcji. Jedyne oficjalne słownictwo przestrzeni: „natural concert hall acoustics”, „spacious modern harmony” [7][8] (oficjalne).
- Opisy faktur/nośnika („tape-saturated”, „lo-fi home recording”, „vinyl crackle”) — niepotwierdzone; jeśli są potrzebne, krótko na końcu stylu i porównaj z wersją bez nich (ten sam seed).
- Do abstrakcji, dronów i faktur bez melodii lepiej nadaje się MiniMax Music 3 (bogate oficjalne wzorce ambientu) — YuE2 zawsze planuje **melodię i akordy** [4][5] (oficjalne).
- Mocna strona do „poszukiwania formy”: ta sama melodia w różnych stylach (cover), albo ta sama piosenka z inną harmonią — model po to jest zbudowany [4] (oficjalne); w Studiu tylko przez cover i zmianę stylu.

## Ruch / czas / dźwięk
- **Forma** = znaczniki sekcji + partytura; tempo i metrum w stylu (np. „88 BPM”) [5][9] (oficjalne).
- **Długość**: „maks. długość” to sufit; YuE2 kończy utwór sam, gdy skończy plan [9] (oficjalne). Dla 30–60 s: jedna zwrotka + refren albo krótki wiersz.
- **Wiersz śpiewany**: tekst dosłownie pod `[Verse]`/`[Chorus]`; długie wersy ewentualnie łam w pauzach (za zgodą uczestnika). Recytacja / spoken word — brak w dokumentacji YuE2 (nie wiadomo).
- Wyjście FLAC 48 kHz stereo [1] (nasza konfiguracja).

## Sprawdź przed wysłaniem
- [ ] Styl: jedna linia po angielsku, zaczyna się od języka (piosenka) albo „Instrumental,” (instrumental); tempo w BPM w stylu.
- [ ] Instrumental: styl kończy „no vocals, no singing, no choir, no spoken words.”; w słowach **żadnych** słów ani nawiasów — same znaczniki.
- [ ] Piosenka: w słowach tylko tekst do zaśpiewania + znaczniki `[Verse]`/`[Chorus]`/`[Bridge]`/`[Outro]` w osobnych liniach, puste linie między sekcjami.
- [ ] Styl krótki (ok. 15–35 słów), bez sprzeczności.
- [ ] Cover: styl = docelowe brzmienie; tekst o zbliżonej liczbie sylab i kolejności sekcji; maks. długość ≥ długość nagrania.
- [ ] Polski śpiew → uprzedź, że nieudokumentowany; zaproponuj krótką próbę.
- [ ] Przypomnij o odsłuchu (głos w instrumentalu, wymowa) i o 2–3 seedach.

## Źródła
[1] Studio — `modele/muzyka/yue-2.yaml` i `yue-2-cover.yaml` — modele/muzyka/yue-2.yaml, modele/muzyka/yue-2-cover.yaml — nasza konfiguracja
[2] Studio — workflow `workflows/muzyka/yue2_tekst-na-muzyke.api.json` — workflows/muzyka/yue2_tekst-na-muzyke.api.json — nasza konfiguracja
[3] Studio — workflow `workflows/muzyka/yue2_cover-z-nagrania.api.json` — workflows/muzyka/yue2_cover-z-nagrania.api.json — nasza konfiguracja
[4] YuE2 — README (tryby full/melody/off, cover, edycja partytury) — https://github.com/multimodal-art-projection/YuE/blob/main/README.md oraz karta https://huggingface.co/m-a-p/YuE2-3B — oficjalne
[5] YuE2 — Generation guide + przykład `examples/song.json` + referencja „generation-and-covers” (pola żądania, brak BPM/negatywu, CFG) — https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/generation-and-covers.md — oficjalne
[6] Comfy-Org — szablon „audio_yue2_music_cover” (notatki: styl, tekst, sylaby, jak działa cover) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json — oficjalne
[7] YuE2 — skill instrumentalny (SKILL.md, README, `assets/example-style.txt`, `scripts/instrumental.py`) — https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental — oficjalne
[8] YuE2 — skill „yue2-music” (SKILL.md, references/abc-editing.md: nazwy sekcji w partyturze, adaptacja tekstu) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/SKILL.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/abc-editing.md — oficjalne
[9] ComfyUI Docs — „YuE2 Music Generation Guide” + szablon „audio_yue2_text2music” (kolejność elementów stylu, budżet długości, języki) — https://docs.comfy.org/tutorials/audio/yue2/yue2 , https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_text2music.json — oficjalne
[10] ComfyUI — kod enkodera YuE2 (`[Tags]`/`[Lyrics]`, kontekst 24 576, 25 tokenów/s, CFG) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/yue2.py — oficjalne (implementacja)
[11] ComfyUI Docs — węzły YuE2GenerateABC, YuE2GenerateMusic, SheetSage2AudioToABC — https://docs.comfy.org/built-in-nodes/YuE2GenerateABC.md , https://docs.comfy.org/built-in-nodes/YuE2GenerateMusic.md , https://docs.comfy.org/built-in-nodes/SheetSage2AudioToABC.md — oficjalne
[12] FSO — PROGRESS.md (5.10: test API; „czy YuE instrumentalnie nie śpiewa” — do odsłuchu) i docs/audio.md — notatki własne (niepublikowane) — nasza konfiguracja
[13] MindStudio — „YuE2: How to Run This Open-Source Music Generation Model Locally” — https://www.mindstudio.ai/blog/yue2-open-music-generation-model — społeczność
[14] YuE2 AI (serwis nieoficjalny; uwagi o językach i wymowie) — https://yue2ai.org/ — społeczność
[15] YuE (v1) — strona projektu — https://map-yue.github.io/ — oficjalne (poprzednia wersja)
[16] YuE2 — „Cover a recording” — https://github.com/multimodal-art-projection/YuE/blob/main/docs/covers.md — oficjalne
[17] YuE2 — skill instrumentalny, cover (`references/cover.md`) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/instrumental/references/cover.md — oficjalne
