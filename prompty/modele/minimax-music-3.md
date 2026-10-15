<!-- Karta modelu dla promptmakera. modele: minimax-music-3 -->
# MiniMax Music 3 (MiniMax, otwarte wagi 08.2026)

## Czym jest i do czego się nadaje
- Hierarchiczny model autoregresyjny: **Global LLM 8B** (inicjalizowany z Qwen3-8B) planuje długą strukturę utworu, **Local LLM 0,6B** dopowiada szczegół akustyczny, potem flow matching + Flow-VAE. Warunkowany **tekstem piosenki** i **szczegółowym opisem muzyki**; utwory **do 5 min**, spójna forma (intro, zwrotka, refren, bridge, przerwa instrumentalna, outro) [4] (oficjalne).
- Opis jest czytany **w czasie** — model idzie za rozwojem utworu, nie tylko za globalnym stylem [4][6] (oficjalne). „Im konkretniej, tym bliżej” [6] (oficjalne).
- W Studiu: główny model do **utworów instrumentalnych** (priorytet warsztatów); 30 s ≈ 93 s liczenia (tryb szybki) [3] (nasza konfiguracja).
- **Czego NIE robi dobrze:**
  - tempo, tonacja, instrumentacja i budowa **nie są gwarantowane** — „wskazówki, nie twarde polecenia” [4] (oficjalne);
  - warstwa instrumentalna bywa **płaska**, nawet gdy w opisie są konkretne instrumenty; gęste, wysokie partie i warstwy wokalu „zlewają się”; słabo oddaje energię gatunku (np. stadionowy rock) [12] (społeczność);
  - rock/metal i starsze brzmienia akustyczne — mieszane opinie, „błotnisty” miks w gęstych aranżach; chwalony głównie w pop i elektronice [13] (społeczność);
  - **język polski — brak danych**: oficjalne dema tylko angielski, mandaryński, kantoński, francuski [7] (oficjalne); praktyk: inne języki „mniej przewidywalne” [11] (społeczność).

## Co uczestnik ustawia w Studiu
| Pole | Wartości | Dokąd trafia / wpływ na prompt |
|---|---|---|
| **opis** | tekst | `caption` — cały opis muzyki [1][2] (nasza konfiguracja) |
| **słowa / struktura** | tekst; domyślnie `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` (każdy w osobnej linii, puste linie między) | `lyrics` — znaczniki sekcji + ewentualne słowa [1] |
| **maks. długość (s)** | 10–300, krok 10, domyślnie 60 | `max_duration` — **górna granica**; model może skończyć wcześniej [1][8] |
| **tryb** | szybki (enkoder INT8, ~1,5 min / 30 s) / jakość (bf16, ~2,5 min / 30 s) | tylko jakość/czas, prompt bez zmian [1][3] |
| **seed** | liczba | inna wersja tego samego promptu [1][6] |

- **Brak pól BPM / tonacji** — tempo i tonację wpisujesz **w opis** [1] (nasza konfiguracja), [4] (oficjalne).
- Stałe: CFG 1,7 (stała modelu w ComfyUI to 1,5), top_k 50; dyfuzja 30 kroków, euler; dekodowanie kafelkowe włączone [2] (nasza konfiguracja), [9] (kod ComfyUI).
- **Negative promptu nie ma** (wyzerowane warunkowanie) [2] (nasza konfiguracja). Wykluczenia pisz w opisie jako fakt („no drums”, „no vocals”).
- Wyjście Studia: MP3 V0 [2]; model natywnie 32 kHz stereo [4] (oficjalne).

## Format promptu
- **Opis po angielsku.** Oficjalny „music-caption-rewriter” pisze opis po angielsku, „chyba że użytkownik wyraźnie chce inny język” [5] (oficjalne); cała biblioteka 1000 wzorcowych opisów jest po angielsku [5] (oficjalne).
- **Struktura: trzy nagłówki w tej kolejności** — `Global Metadata`, `Vocal Details`, `Arrangement` [4][5] (oficjalne). Wskazówka Studia: opis zaczyna się od „Global Metadata:” [1] (nasza konfiguracja). Oficjalny szablon ComfyUI pisze nagłówek z dwukropkiem i treścią w tym samym akapicie, akapity oddzielone pustą linią [10] (oficjalne); biblioteka MiniMax — nagłówek w osobnej linii i podpola [5] (oficjalne). Oba warianty są poprawne.
- **Podpola z oficjalnej biblioteki** (najbliższe danym treningowym) [5][6] (oficjalne / społeczność):
  - Global Metadata → `Basic Attributes:` (dokładnie w formie „bpm is 76. key is Bb, and scale is major. Gatunek / Podgatunek.”), `Global Emotional Progression:`, `Application Scenarios & Imagery:`, `Sonics & Production Profile:`;
  - Vocal Details → `Vocal Gender & Timbre:`, `Vocal Style:`, `Harmony/Backing Vocals:`, `Vocal FX:`;
  - Arrangement → `Instrument Lifecycle Description (Primary/Secondary Layering):` z „Primary: …” i „Secondary: …”, `Groove & Foundation Progression:`, `Embellishments, Textures & Spatial FX:`.
- **Długość opisu: ok. 250–450 słów** (domyślna wartość rewritera) [5] (oficjalne). Limit całego promptu: 5000 tokenów [4][9] (oficjalne).
- **Markdown nic nie daje**: ComfyUI usuwa `#` nagłówki, wypunktowania `-`/`*`, pogrubienia i zwija puste linie [9] (kod ComfyUI). Pisz zwykłymi zdaniami.
- **Słowa / struktura** — oficjalna lista znaczników: `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` [4][8] (oficjalne).
  - **Każdy znacznik w osobnej linii**; tekst w tej samej linii co znacznik może przepaść [6] (społeczność).
  - Wielkość liter nieistotna — ComfyUI i tak zamienia znaczniki na małe litery [9] (kod ComfyUI).
  - **Tylko znaczniki są poleceniami budowy**; słowa niosą wyłącznie treść i emocję. „Bębny wchodzą” wpisane w słowa nie zmieni bębnów — to idzie do Arrangement [8][10] (oficjalne), [11] (społeczność).
  - Powtarzaj sekcje zwykłymi znacznikami (`[Verse]` … `[Verse]`) jak w oficjalnym szablonie [10]; numerowanie `[Verse 1]` — porada społeczności [11], skuteczność niepotwierdzona.
- Wag, JSON-a, negatywu — brak w dokumentacji; nie używaj. Pole opisu wspiera „dynamic prompts” ComfyUI [8] — unikaj nawiasów klamrowych `{a|b}` (niepotwierdzone, czy działają przez API Studia).

## Szkielet promptu
Opis (po angielsku, zwykłe zdania, ~250–450 słów):
```
Global Metadata
Basic Attributes: bpm is [liczba]. key is [nuta], and scale is [major/minor]. [Gatunek] / [Podgatunek albo faktura].
Global Emotional Progression: [jak się otwiera] → [gdzie narasta / szczyt] → [jak się rozwiązuje lub nie].
Application Scenarios & Imagery: [scena/obraz, do którego należy muzyka — z biblii, bez cytowania wiersza].
Sonics & Production Profile: [szerokość stereo, pasmo (ciemne/jasne), dynamika (skompresowana/naturalna), przestrzeń, nośnik/nagranie].

Vocal Details
[INSTRUMENTAL: The piece is fully instrumental, no vocals. The lead melodic role is carried by [instrument/faktura].]
[PIOSENKA: Vocal Gender & Timbre: Singer A ([Male/Female]) … Vocal Style: … Harmony/Backing Vocals: … Vocal FX: …]

Arrangement
Instrument Lifecycle Description (Primary/Secondary Layering):
Primary: [instrument-kręgosłup, kiedy jest, jak się zmienia].
Secondary: [co wchodzi/wychodzi i kiedy].
Groove & Foundation Progression: [puls albo jego brak — np. no percussive groove, free time; jak gęstnieje].
Embellishments, Textures & Spatial FX: [faktury, szumy, pogłosy, przejścia].
[Intro: … / Instrumental sections: … / Solo: … / Outro: … — po zdaniu na każdy znacznik użyty w polu „słowa”]
```
Słowa / struktura — instrumental:
```
[Intro]

[Instrumental]

[Solo]

[Instrumental]

[Outro]
```
Słowa — piosenka: `[Verse]` + linie tekstu, `[Chorus]` + linie, … — znacznik zawsze sam w linii, pusta linia między sekcjami [8][10].

## Co działa
- **Opis jako oś czasu, nie lista sprzętu**: dla każdej sekcji napisz, co wchodzi, wychodzi, zmienia się, narasta [5][6] (oficjalne / społeczność).
- **Łuk energii jak opowieść** (napięcie, rozładowanie, oddech, kulminacja) daje lepszą formę niż statyczny opis [6] (społeczność).
- **Każdy znacznik z pola „słowa” ma swoje zdanie w Arrangement** — rozjazd znaczników i aranżu to najczęstsza przyczyna, że utwór nie trzyma budowy [11] (społeczność); oficjalny szablon ComfyUI opisuje „Intro: …, Verses: …, Instrumental sections: …, Bridge: …, Outro: …” [10] (oficjalne).
- **Application Scenarios & Imagery** — scena, do której należy muzyka, kotwiczy nastrój lepiej niż przymiotniki [6] (społeczność). Tu przenieś obraz z biblii utworu (bez treści wiersza — słowa nie trafiają do opisu [5]).
- **Nie wymyślaj precyzji**: dokładne BPM/tonacja tylko gdy naprawdę potrzebne; inaczej zakres lub słowo („unhurried”, „driving”) [5][6] (oficjalne / społeczność).
- **Wykluczenia i wymogi trzymaj w całym opisie** (instrumentalność, płeć głosu, zakazany instrument) — nie zaprzeczaj im w dalszych sekcjach [5] (oficjalne).
- **Fuzja dwóch stylów**: nazwij oba i napisz, jak dzielą aranż [6] (społeczność). Słowa emotional, epic, dark, cinematic to **modyfikatory, nie gatunki** [5] (oficjalne).
- **Seed** do wariantów; stały seed, gdy porównujesz zmianę opisu [8] (oficjalne).

## Biasy i pułapki
- **Biblia wzorców to piosenki**: w 1000 oficjalnych opisów nie ma ani jednego instrumentalu; dominuje Mandopop/C-pop, R&B, folk, pop-rock, ballady [5] (oficjalne; analiza indeksów). Model ciągnie ku **formie piosenki i balladzie** — instrumental trzeba mówić wprost.
- **Niewyspecyfikowany wokal** = najczęstsza przyczyna dryfu: zawsze wypełnij Vocal Details — przy instrumentalu napisz, że go nie ma, i nazwij instrument prowadzący [5] (oficjalne), [6] (społeczność). Nasza praktyka: „No vocals. Fully instrumental.” [3] (nasza konfiguracja).
- **Za krótka struktura = za krótki utwór**: maks. długość to sufit; model kończy, gdy „skończy się tekst”. Pięciominutowy utwór potrzebuje pełnej liczby sekcji [6][11] (społeczność). Ile sekund wypełnia domyślne 5 sekcji — nie wiadomo (do odsłuchu); dla dłuższych dodaj `[Instrumental]`/`[Solo]`/`[Bridge]` i opisz je w Arrangement.
- **Instrumenty nazwane ≠ słyszalne w miksie** [12] (społeczność): nie upychaj 8 instrumentów; 2–4 z jasnymi rolami Primary/Secondary.
- **Gęste wysokie warstwy się zlewają** [12] — przy wielu warstwach rozdziel je w czasie (sekcjami), nie wszystko naraz.
- **Długie utwory = długie czekanie** (proporcjonalnie, ~93 s na 30 s w trybie szybkim) [3] (nasza konfiguracja) — przy szkicach pracuj na 30–60 s.

## Poza fotorealizmem (w muzyce: poza konwencją — faktura, taśma, lo-fi, abstrakcja)
- **Lo-fi / taśma / winyl** — oficjalny szablon ComfyUI: „muddy warm texture, heavy vinyl crackle, tape hiss and wow-flutter pitch wobble, low-passed dusty mix, soft-clipped drums, everything slightly detuned” [10] (oficjalne). Pisz to w `Sonics & Production Profile` i w Embellishments.
- **Muzyka bez pulsu** — wzorce oficjalne: „There is no percussive groove or rhythmic foundation; the tempo is driven entirely by the rubato phrasing…”, „relies entirely on free-time atmospheric progression” [5] (oficjalne).
- **Ciemny ambient / drony / faktury** — oficjalne wzorce: „low-frequency synthesizer drone… present continuously”, „granular textures and wind-like noise sweeps”, „continuous layer of ambient noise resembling underwater static or hydrophone recordings”, „reverse reverb swells as transitional markers” [5] (oficjalne).
- **Przestrzeń i pasmo** jako narzędzie formy: „high frequencies significantly rolled off”, „cavernous, aquatic spatial feel”, „heavily compressed and saturated, wall-of-sound” [5] (oficjalne).
- **Archiwalność**: nazwij nośnik i jego wady (winyl, taśma, wow & flutter, wąskie pasmo) zamiast „old” [10] (oficjalne — słownictwo z szablonu); skuteczność „radio z lat 30.” itp. niepotwierdzona.
- Konkretna aparatura jest w bibliotece rzadka (przewaga popu) — eksperymentalne instrumentarium opisuj przez brzmienie i funkcję, nie samą nazwą (niepotwierdzone).

## Ruch / czas / dźwięk
- **Czas = znaczniki + Arrangement**: znaczniki wyznaczają sekcje, Arrangement mówi, co się w nich dzieje [4][8] (oficjalne).
- **Sekcja może zmienić lokalny aranż** (np. `[Solo]`) bez zmiany gatunku całości [5][6] (oficjalne / społeczność).
- **Długość**: ustaw „maks. długość” z zapasem i dobierz liczbę sekcji; model sam kończy utwór tokenem końca [6] (społeczność), [8] (oficjalne).
- **Wiersz mówiony na muzyce**: w bibliotece są wzorce spoken word („Cinematic Ambient / Spoken Word”): w Vocal Details „a deliberate, theatrical spoken-word delivery rather than singing… slow and measured, with distinct pauses” [5] (oficjalne). Tekst wiersza → pole „słowa” pod znacznikami `[Verse]`. Polska recytacja — niesprawdzona.
- **Piosenka po polsku**: brak oficjalnego wsparcia w dokumentach [7]; jeśli uczestnik chce — krótka próba 30 s, odsłuch wymowy (niepotwierdzone). Język śpiewu nazwij w Vocal Details (np. „sung in Polish”) — niepotwierdzone.

## Sprawdź przed wysłaniem
- [ ] Opis po angielsku, trzy części w kolejności Global Metadata → Vocal Details → Arrangement, zwykłe zdania (bez markdownu).
- [ ] Tempo i tonacja w opisie („bpm is …. key is …, and scale is ….”) — albo świadomie słowem, bez fałszywej precyzji.
- [ ] Vocal Details wypełnione: instrumental → „fully instrumental, no vocals” + instrument prowadzący.
- [ ] Każdy znacznik w osobnej linii, tylko z oficjalnej listy 9; brak poleceń muzycznych w słowach.
- [ ] Każdy użyty znacznik ma zdanie w Arrangement; Arrangement czyta się jak oś czasu.
- [ ] Liczba sekcji pasuje do „maks. długości”.
- [ ] Wymogi/wykluczenia nie są sobie przeczące w różnych częściach opisu.
- [ ] Bez nazwisk artystów (szablon medium), bez `{|}`, bez treści wiersza w opisie.

## Źródła
[1] Studio — `modele/muzyka/minimax-music-3.yaml` — modele/muzyka/minimax-music-3.yaml — nasza konfiguracja
[2] Studio — workflow `workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json` — workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json — nasza konfiguracja
[3] Testy i zalecenia audio (93 s / 30 s INT8; „No vocals. Fully instrumental.”) — notatki własne (niepublikowane) — nasza konfiguracja
[4] MiniMax-Music3 — README (architektura, znaczniki, Structured Caption, ograniczenia) — https://github.com/MiniMax-AI/MiniMax-Music3 (też https://huggingface.co/MiniMaxAI/MiniMax-Music3) — oficjalne
[5] MiniMax — skill „music-caption-rewriter” (SKILL.md, references/genre-router.md, indeksy i 1000 szablonów, m.in. dark-ambient-slowcore_0001, contemporary-classical-ambient-ballad_0001, cinematic-ambient-spoken-word_0001) — https://github.com/MiniMax-AI/MiniMax-Music3/tree/main/skills/music-caption-rewriter — oficjalne
[6] „Prompting MiniMax Music 3” — Space Hugging Face (multimodalart) — https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide — społeczność (oparty na oficjalnym skillu)
[7] MiniMax Music 3 — strona demo (języki i gatunki dem) — https://minimax-ai.github.io/music3-demo/ — oficjalne
[8] ComfyUI Docs — MiniMax Music 3 (tutorial) i węzeł MiniMaxMusic3TextEncode — https://docs.comfy.org/tutorials/audio/minimax/minimax-music-3 oraz https://docs.comfy.org/built-in-nodes/MiniMaxMusic3TextEncode.md — oficjalne
[9] ComfyUI — kod: budowa promptu (`comfy/ldm/minimax_music/prompt.py`) i stałe (`ar.py`: CFG 1.5, top_k 50, 5000 tokenów, 9000 klatek) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/ldm/minimax_music/prompt.py — oficjalne (implementacja)
[10] Comfy-Org — oficjalny szablon workflow „audio_minimax_music_3” (przykładowy opis lo-fi i notatki) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_minimax_music_3.json — oficjalne
[11] EarnGenix — „MiniMax Music 3 in ComfyUI: Generate a Full 5-Minute Song” — https://www.earngenix.com/workflows/minimax-music-3-comfyui — społeczność
[12] MindStudio — „MiniMax Music 3: The Open-Weight AI Music Model, Explained” — https://www.mindstudio.ai/blog/minimax-music-3-open-weight — społeczność
[13] AIReiter — „MiniMax Music 3.0 Review: API, Pricing & Local Setup” — https://aireiter.com/blog/minimax-music-3-0-review-api-pricing-local-setup — społeczność
