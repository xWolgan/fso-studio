<!-- Karta modelu dla promptmakera. modele: qwen-image-2-1 -->
# Qwen-Image 2.1 (Alibaba Qwen) — tekst → obraz

## Czym jest i do czego się nadaje (w tym: czego NIE robi dobrze)
- Otwarte wagi z 20.09.2026, licencja Qwen Research (niekomercyjna); generator 7B (32 warstwy single-stream DiT), enkoder tekstu Qwen3-VL 8B [1][2] (oficjalne), [14] (nasza konfiguracja).
- Natywnie generuje w 2K (np. 2752×1536 dla 16:9); jeden model robi generację i edycję [1] (oficjalne). Edycja ma osobną kartę (`qwen-image-edycja.md`).
- Mocne strony: **długie, gęste opisy** (rodzina 2.0 deklaruje instrukcje do ~1K tokenów) [9] (oficjalne, wersja 2.0), **tekst w obrazie** z układem i typografią (plakaty, slajdy, infografiki, wykresy) [1][9][11] (oficjalne / społeczność), obrazy z przezroczystością (RGBA) [1] (oficjalne).
- Czego NIE robi dobrze / ryzyka:
  - dłonie i stopy — osobny wątek skarg na HF [16] (społeczność, sam tytuł wątku);
  - „szum, muł, przeprocesowanie” przy promptach przeładowanych terminami jakości i stylu [17] (społeczność, bez odpowiedzi autorów);
  - tekst w językach spoza zh/en — wielojęzyczność deklarowana ogólnie, **polskie znaki (ą, ę, ł, ż…) niepotwierdzone** żadnym testem [9][11][18];
  - wielkość, w jakiej Studio go uruchamia, to ~1 MP, czyli ok. ćwierć natywnej powierzchni 2K [14] (nasza konfiguracja); drobny tekst i detal mogą na tym tracić (niepotwierdzone).

## Co uczestnik ustawia w Studiu (pola, wejścia, parametry z naszego YAML — i jak wpływają na prompt)
Źródło: `modele/obraz/qwen-image-2-1.yaml` + `workflows/obraz/qwenimage21_tekst-na-obraz.api.json` [14] (nasza konfiguracja).
- **prompt** — jedno pole. Trafia do `TextEncodeQwenImage21` (Qwen3-VL 8B). Enkoder owija tekst w szablon czatu z systemem „Comprehend and analyze the provided prompt.” i potem tę część systemową odcina [3] (kod ComfyUI).
- **Brak pola negative promptu.** W workflow `negative_prompt` = pusty, a **CFG = 1** — przy CFG 1 ComfyUI w ogóle pomija gałąź negatywną [2][5] (oficjalne). Czego ma nie być, piszesz pozytywnie.
- **proporcje** — 16:9 (domyślnie), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16; **1,0 MP** (węzeł ResolutionSelector, wielokrotność 8). Proporcji **nie wpisuj do promptu** — oficjalny rozszerzacz zakazuje wpisywania proporcji, rozdzielczości i liczby pikseli do opisu [14] (nasza konfiguracja / oficjalny system prompt PE).
- **seed** — ten sam seed idzie do generatora i do rozszerzacza. Stały seed = porównywanie wersji promptu.
- **kroki** (zaawansowane) — 10–50, domyślnie 25; sampler euler/simple. Oficjalne przykłady: 40 kroków [1]; ComfyUI: dłonie „siadają” ok. 30 kroków, 40 kroków zmniejsza „mrowienie” w gęstych detalach [2] (oficjalne).
- **„model sam rozbudowuje prompt”** (zaawansowane, domyślnie WYŁ.) — przełącza na prompt przepisany przez Qwen3.5 9B PE-T2I (oficjalny rozszerzacz Qwena) z naszym system promptem (jeden akapit angielski, bez JSON), **z trybem myślenia** (`thinking: true`, `max_length` 8192, żeby rozumowanie nie ucięło odpowiedzi) [14] — jak w oficjalnym przykładzie karty PE (`enable_thinking=True`) [6]; domyślne szablony ComfyUI po korekcie z 30.09.2026 mają myślenie wyłączone [8], ale praktycy piszą, że bez niego PE daje słabsze prompty [7] (społeczność). Koszt: generacja trwa dłużej (szacunkowo +1–2 min na rozumowanie; niezmierzone). Wniosek: **gdy prompt pisze promptmaker, zostaw przełącznik wyłączony** — PE przepisze wszystko po swojemu (ustali kadr, wymyśli resztę sceny). Włączenie ma sens tylko jako „pokaż mi interpretację modelu” dla 3-słownego pomysłu.

## Format promptu (język, długość, struktura, znaczniki, negatyw, wagi)
Najlepszy wzorzec = to, co oficjalny rozszerzacz PE-T2I podaje modelowi. Jego zasady mamy w workflow (węzeł 459:475) [14] (nasza konfiguracja, tekst oparty na oficjalnym PE [6]):
- **Język: angielski.** PE zawsze pisze opis po angielsku, niezależnie od języka prośby; wyjątek: **tekst widoczny w obrazie zostaje w swoim języku i alfabecie** [6][14] (oficjalne). Qwen jest najmocniejszy w chińskim tekście [10] (oficjalne, Qwen-Image 1.0), ale uczestnik musi umieć przeczytać prompt, więc proza zawsze po angielsku.
- **Forma: jeden ciągły akapit prozy**, czas teraźniejszy, trzecia osoba, zdania oznajmujące. Opis gotowego obrazu „jak widzi go obserwator”, nie polecenie („create…”, „make sure…”, „you”) [14].
- **Długość:** PE celuje w **ok. 20 zdań, 400–500 słów** (~25 słów na zdanie) — tyle samo dla krótkiej i długiej prośby; gęsty kadr dłużej, cichy pojedynczy motyw krócej [14]. Starszy rozszerzacz Qwen-Image 1.0 celował w < 200 słów [12] — to inna wersja, nie stosuj.
- **Kolejność (wg PE)** [14]:
  1. **zdanie otwierające (~20 słów)**: orientacja + **styl** + **rzeczownik medium** (photograph / illustration / poster / page / scene / portrait / graphic…) + podmiot + tło i paleta. Medium nigdy nie może zniknąć.
  2. **tło i powierzchnia** zaraz po otwarciu (nie na końcu);
  3. **przejście przez kadr**: pas górny → lewa strona, środek, prawa → pas dolny. Albo, gdy kadr wypełnia jeden motyw: tło i jak opada → poza i miejsce w kadrze → głowa/twarz → ciało, każda część stroju i powierzchnia → co trzyma/czego dotyka → krawędzie;
  4. **8–14 określeń położenia** (upper-left, along the lower edge, behind the left shoulder…), sięgających rogów i krawędzi; ok. 1/3 zdań zaczyna się od określenia położenia;
  5. **każdy tekst w kadrze** w kolejności czytania (patrz niżej);
  6. **osobne zdanie o świetle**: źródło, kierunek, jakość, cienie i odblaski („The lighting is…”);
  7. **jedno zdanie zamykające** o całości: równowaga, paleta, styl, nastrój („The overall composition…”). Tylko jedno.
- **Tekst w obrazie** [14][6] (oficjalne):
  - dosłownie, **w prostych podwójnych cudzysłowach**, w oryginalnym alfabecie, znak po znaku z interpunkcją;
  - przy każdym napisie: gdzie stoi, grubość, kolor, wielkie/małe litery, względna wielkość („a bold black headline across the top reads "…"”);
  - złamanie wiersza opisz słowami („a second line reads…”), bez znaku nowej linii w cudzysłowie;
  - tekst, który nie ma być czytelny (daleki szyld, drobny druk) → nazwij „blurred / indistinct / too small to read”, nie wymyślaj liter;
  - **nie dodawaj napisów, których uczestnik nie chce** — ok. 1/3 obrazów nie ma żadnego tekstu.
- **Bez „wzmacniaczy jakości”**: „masterpiece”, „8K”, „highly detailed”, „award-winning” — PE ich zakazuje [14]. (Przykład z karty HF ma „8k”, ale to prompt demonstracyjny [1].)
- **Kolory z określeniem** (deep navy, muted olive, warm terracotta), **materiał zamiast samego rzeczownika** (coarse linen, weathered wood, paper fibre, visible brush strokes), **wyliczaj, nie streszczaj** („several items” = błąd), małe liczby słowami, wiek jako etap życia/dekada, przedmioty po klasie, nie po marce [14].
- **Negative prompt:** brak (CFG 1) [2][14]. Ograniczenia pozytywnie: „the street is empty except for…”, „the background is a flat, untextured off-white”.
- **Wagi `(słowo:1.3)` — NIE.** Tokenizer Qwen3-VL w ComfyUI ma `disable_weights=True`: nawiasy i liczby idą do modelu jako zwykły tekst [4] (kod ComfyUI). Unikaj też nawiasów jako ozdobnika.
- **Bez JSON, nagłówków, list, markdownu** — PE oddaje czysty akapit; JSON z `wh_ratio` to tylko format wyjścia rozszerzacza, nie wejścia generatora [6][14].
- **Przezroczystość (RGBA):** oficjalny wzór: zacznij „This is an RGBA image with transparency.”, opisz motyw, zakończ „The image has alpha channel and the background is transparent.” [1] (oficjalne). Czy Studio zapisuje kanał alfa w PNG — niepotwierdzone.

## Szkielet promptu
```
The image is a [orientacja: wide / vertical / square] [styl: hand-drawn / watercolour / flat-vector / archival / cinematic…] [medium: photograph / illustration / collage / poster / page…] of [podmiot], [tło i paleta: 2–3 kolory z określeniem].
[Tło i powierzchnia: z czego jest, faktura, jak daleko i jak ostro].
[Pas górny: co zajmuje górną krawędź]. [On the left side of the frame, … ]. [In the centre, … podmiot: poza, kierunek spojrzenia, wygląd, każdy element stroju z kolorem i materiałem]. [On the right side, … ]. [Across the lower third / along the bottom edge, … ].
[Napisy, w kolejności czytania: gdzie, krój/grubość, kolor, wielkość, reads "DOKŁADNY TEKST"].
[Faktura medium: ziarno / włókno papieru / pociągnięcia pędzla / raster / zabrudzenia — konkretnie, gdzie widoczne].
The lighting is [źródło], [kierunek], [jakość: hard/soft/flat], [cienie i odblaski].
The overall composition [równowaga/symetria], [paleta], [styl], [nastrój].
```

## Co działa
- **Kadr opisany przestrzennie** — określenia położenia na krawędziach i w rogach, a nie tylko w środku; to rdzeń oficjalnego PE [14].
- **Jedno słowo stylu w zdaniu otwierającym** (można powtórzyć w zamknięciu) zamiast rozsypanych przymiotników [14].
- **Materiał i faktura** dają konkret: „matte”, „brushed metal”, „frosted glass”, „grain”, „scuffs”, „paper fibre”, „visible brush strokes” [14].
- **Fizyczna spójność**: cienie od światła, odbicia zgodne ze sceną, skala obiektów spójna — PE wymaga tego jawnie; rzeczy niemożliwe opisz tak, jak obraz je pokazuje, resztę sceny trzymaj spójną [14].
- **Konkret zamiast ogólników**: zdania z podmiotem, pozą, źródłem światła, odniesieniem do filmu/obiektywu działają lepiej niż ogólny opis [19] (społeczność, recenzja sprzedawcy).
- **Dla wiersza:** nastrój tłumacz na światło, kolor, materię i rozmieszczenie — PE każe opisywać to, co widać, a nastrój zostawia na jedno zdanie zamykające [14].
- **Seed stały, zmieniaj jedną rzecz naraz** [2] (oficjalne).

## Biasy i pułapki
- **Dryf ku „profesjonalnemu” wykończeniu**: rodzina 2.x chwali się „bardziej fotorealistycznymi detalami, fakturą i światłem” [9][18] (oficjalne). Brak wskazania medium = najczęściej wypolerowana fotografia/rendering (niepotwierdzone testem, wniosek z [9]). Zawsze nazwij medium.
- **Przeładowanie stylu** („hyper-realistic, photorealistic detail, high contrast, dramatic volumetric lighting…” naraz) → zgłoszenia „noisy, muddy, overprocessed” [17] (społeczność). Jedno słowo stylu, jedno zdanie światła.
- **Wymyślanie napisów**: model chętnie stawia szyldy i etykiety — gdy obraz ma być bez tekstu, nie wspominaj o szyldach, ekranach, okładkach; opisz powierzchnie jako gładkie/puste [14].
- **Polskie znaki**: niepotwierdzone. Krótkie napisy, dokładnie w cudzysłowie; sprawdź wynik litera po literze, w razie błędu kilka seedów. Gdy napis jest kluczowy, rozważ w Studiu Ideogram 4 („napisy w obrazie”) [15] (nasza konfiguracja).
- **CFG**: nie jest wystawione uczestnikowi. Dla wiedzy: CFG ~2 lepiej trzyma gęsty prompt i drobny tekst, ale przeostrza krawędzie; CFG 5 psuje, 0,5 łamie obraz [2] (oficjalne). Odpowiedź na HF: w generacji można podnieść CFG i użyć negatywu, w edycji nie podnosić [13] (społeczność).
- **Liczby i zestawy przedmiotów**: wyliczaj każdy element osobno; „kilka”, „różne” = model improwizuje [14].
- **Twarze konkretnych osób / marki**: PE opisuje przedmioty po klasie; nazwisko lub marka tylko, gdy uczestnik to ustalił [14].

## Poza fotorealizmem
- **Medium w pierwszym zdaniu, rzeczownikiem**: „illustration”, „ink drawing”, „watercolour painting”, „collage”, „poster”, „page”, „sheet” — oficjalna lista stylów PE obejmuje watercolour, hand-drawn, flat-vector, isometric, retro, minimalist, 3D-rendered [14].
- **Kolaż / grafika**: przykładowy prompt z naszego workflow (oficjalny szablon ComfyUI) pokazuje działający słownik: „mixed-media graphic collage”, „flat vibrant planes”, „overlapping circles”, „dense micro-halftone dot matrices”, „vector topographic contour lines” [14]. Opisuj warstwy kolażu jak elementy kadru — każdy z położeniem.
- **Rysunek / malarstwo**: opisz narzędzie i ślad: „graphite hatching”, „visible brush strokes”, „pigment pooling at the edges”, „paper fibre showing through” (słownik materiałów z PE [14]; konkretne frazy malarskie — niepotwierdzone testem).
- **Taśma / archiwum / ziarno**: fakturę opisz jako to, co widać na obrazie (ziarno, rysy, przebarwienia, rozmyte krawędzie), plus jedno zdanie o świetle. Słownik filmowy (film stock, lens) działa jako konkret [19] (społeczność). Nie mieszaj z „crisp, razor-sharp”.
- **Abstrakcja**: kadr podzielony na regiony → opisuj regiony (pas górny, lewa, środek, prawa, dół) z kształtem, kolorem, krawędzią i fakturą; światło „flat even ambient light” [14].
- **Animacja / płaska grafika**: „flat-vector”, „cel-shaded”, „flat colour fills with thin outlines”; światło płaskie. Nie dodawaj obiektywu i głębi ostrości.
- Konflikt rejestrów (np. foto + kreskówka bez uzasadnienia) — świadomie i opisany przestrzennie („a hand-drawn figure pasted onto a black-and-white photograph”), inaczej model uśrednia.

## Ruch / czas / dźwięk
Nie dotyczy (obraz statyczny). Jeśli obraz ma być **pierwszą klatką wideo** w Studiu — ustaw proporcje jak wideo (zwykle 16:9), zostaw w kadrze miejsce na ruch, unikaj drobnego tekstu (wideo go rozmyje).

## Sprawdź przed wysłaniem
- [ ] Proza po angielsku; tekst w kadrze w swoim języku, w prostych `"…"`, dosłownie z polskimi znakami.
- [ ] Pierwsze zdanie: orientacja + styl + **medium** + podmiot + tło/paleta.
- [ ] Kadr przebiegnięty przestrzennie, określenia położenia sięgają rogów i krawędzi.
- [ ] Osobne zdanie o świetle; jedno zdanie zamykające.
- [ ] Brak: „masterpiece/8K/highly detailed”, wag `( :1.3)`, JSON, proporcji/rozdzielczości w tekście, poleceń „create/make sure”.
- [ ] Wykluczenia sformułowane pozytywnie (negatywu nie ma).
- [ ] Żadnych napisów, których uczestnik nie chciał.
- [ ] Przełącznik „model sam rozbudowuje prompt” — zalecaj WYŁ., gdy prompt jest już pełny.
- [ ] ~250–500 słów; mniej dla jednego cichego motywu.

## Źródła
[1] Qwen/Qwen-Image-2.1 — karta modelu — https://huggingface.co/Qwen/Qwen-Image-2.1 — oficjalne
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — oficjalne (ComfyUI)
[3] ComfyUI — comfy/text_encoders/qwen_image21.py (szablon czatu enkodera) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — oficjalne (kod)
[4] ComfyUI — comfy/text_encoders/qwen3vl.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — oficjalne (kod)
[5] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21: negatyw, resolution) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — oficjalne (kod)
[6] Qwen/Qwen-Image-2.1-PE-T2I — karta rozszerzacza — https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I — oficjalne
[7] ComfyUI Wiki — Qwen-Image 2.1 Prompt Enhancer Models Run in ComfyUI — https://comfyui-wiki.com/en/news/2026-09-22-qwen-image-2-1-prompt-enhancer — społeczność
[8] Comfy-Org/docs PR #1843 — correct the Qwen Image 2.1 prompt enhancer defaults — https://github.com/Comfy-Org/docs/pull/1843 — oficjalne (ComfyUI)
[9] Qwen-Image-2.0 Technical Report (arXiv 2605.10730) — https://arxiv.org/abs/2605.10730 — oficjalne (wersja 2.0)
[10] QwenLM/Qwen-Image — README (wcześniejsze wersje, zalecenia PE) — https://github.com/QwenLM/Qwen-Image — oficjalne
[11] Qwen-Image: Crafting with Native Text Rendering (blog 1.0) — https://qwenlm.github.io/blog/qwen-image/ — oficjalne (wersja 1.0)
[12] QwenLM/Qwen-Image — src/examples/tools/prompt_utils.py (rozszerzacz 1.0, < 200 słów) — https://github.com/QwenLM/Qwen-Image/blob/main/src/examples/tools/prompt_utils.py — oficjalne (wersja 1.0)
[13] HF dyskusja #14 — CFG i negatyw w domyślnym kodzie — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/14 — społeczność
[14] Nasza konfiguracja: modele/obraz/qwen-image-2-1.yaml; workflows/obraz/qwenimage21_tekst-na-obraz.api.json (węzły 459:452, 459:458, 459:471, 459:474, 459:475 = system prompt PE) — nasza konfiguracja
[15] Nasza konfiguracja: notatki własne (niepublikowane) (Ideogram 4 do napisów) — nasza konfiguracja
[16] HF dyskusja #29 — 手脚的问题就解决不了了? (dłonie i stopy) — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/29 — społeczność
[17] HF dyskusja #56 — Qwen 2.1 image quality issue — noisy and muddy results — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/56 — społeczność
[18] eesel — Qwen Image 2.1 review — https://www.eesel.ai/blog/qwen-image-2-1-review — społeczność
[19] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — społeczność (sprzedawca)
