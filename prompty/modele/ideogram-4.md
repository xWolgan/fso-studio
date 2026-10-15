<!-- Karta modelu dla promptmakera. modele: ideogram-4 -->
# Ideogram 4 (otwarte wagi, 9,3B) — tekst → obraz, prompt w JSON

## Czym jest i do czego się nadaje (w tym: czego NIE robi dobrze)
- Model tekst→obraz od Ideogram, wytrenowany od zera, 9,3B parametrów, DiT z jednym strumieniem; enkoder tekstu to Qwen3-VL-8B-Instruct, VAE z FLUX.2 [10][9][2] (oficjalne / nasza konfiguracja).
- Trenowany **wyłącznie na podpisach w strukturze JSON**, które wyczerpująco opisują każdy element obrazu. Zwykła proza „nie zadziała i prawdopodobnie wywoła ostrzeżenie bezpieczeństwa” [4][14] (oficjalne).
- Mocne strony: napisy w obrazie (wynik OCR dla angielskiego 0,97) [14], **kontrola palety przez hex** [4], **rozmieszczenie elementów przez bbox** [4], plakat, okładka, typografia, layout [15][27] (oficjalne / społeczność). Według społeczności ludzie nie wyglądają „plastikowo”, a kontrola położenia jest bardzo precyzyjna [20] (społeczność).
- Słabe strony:
  - Wbudowany w wagi filtr bezpieczeństwa daje fałszywe alarmy: zamiast obrazu pojawia się szary obraz z napisem „Image blocked by safety filter”. W ComfyUI nie da się go wyłączyć [4][15][21] (oficjalne / społeczność).
  - Nie daje przezroczystości ani kanału alfa. Rysuje szachownicę, która ją tylko udaje [23] (społeczność).
  - W layoucie (mIoU 0,69) i rozumowaniu przestrzennym (0,76) wypada najsłabiej spośród własnych benchmarków [14] (oficjalne).
  - Długi tekst się psuje. Polskie znaki diakrytyczne bywają gubione albo podwajane [26] (społeczność, nie zweryfikowaliśmy tego u nas).
  - Wyniki są mało zróżnicowane [29] (społeczność).
  - Nie edytuje obrazów, nie przyjmuje obrazu na wejściu (w naszym Studiu to tylko tekst→obraz) [2] (nasza konfiguracja).
- Licencja wag: Ideogram 4 Non-Commercial (kod: Apache-2.0) [10] (oficjalne). Uwaga: nasz YAML podaje „Ideogram Open Model” [1] — rozbieżność w konfiguracji, nie w karcie.

## Co uczestnik ustawia w Studiu (pola, wejścia, parametry z naszego YAML — i jak wpływają na prompt)
- **prompt**: trafia **dosłownie** do `CLIPTextEncode` (enkoder `qwen3vl_8b_int8_convrot`, typ `ideogram4`) [1][2] (nasza konfiguracja).
  - **U nas nie działa magic prompt.** Podgraf „magic prompt” w workflowie tylko składa tekst instrukcji systemowej do podglądu i nie uruchamia żadnego LLM [2]. Promptmaker sam pełni więc rolę magic promptu i musi oddać **kompletny, poprawny JSON**.
  - Przycisk „szablon” wstawia szkielet w wariancie nie-fotograficznym (`art_style`) [1].
- **proporcje**: 16:9 (domyślnie), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16, przy 1,0 MP. Boki są zaokrąglane do wielokrotności 16 [1][2] (nasza konfiguracja).
  - Bbox liczy się w skali 0–1000 **na każdej osi** względem kadru. Przy zmianie proporcji ramki rozciągają się razem z nim [5][3].
  - Model natywnie obsługuje 256–2048 px i proporcje do 6:1 [7]. Najwyższą jakość autorzy podają dla 2048×2048 [10]. Nasze 1 MP może osłabiać drobny tekst (niepotwierdzone).
- **profil**: szybki = Turbo (12 kroków), domyślny = Default (20), jakość = Quality (48) [1][2].
  - Według dokumentacji przez większość kroków działa CFG 7, a na końcu kilka kroków „polerujących” z CFG 3 [7] (oficjalne).
  - U nas `CFGOverride` ustawia cfg 3 od 70% do 100% przebiegu [2] (nasza konfiguracja).
  - Przy drobnych napisach używaj profilu „jakość” [12] (oficjalne).
- **seed**: ma duży wpływ także na to, czy włączy się fałszywa blokada filtra [21] (społeczność).
- **Negative promptu nie ma.** Gałąź negatywna to `ConditioningZeroOut` (wyzerowany tekst) plus osobny model bezwarunkowy w `DualModelGuider` [2][8] (nasza konfiguracja / oficjalne). Wykluczenia z hostowanego Ideogram.ai tu nie działają [12].

## Format promptu
- **Prawidłowy JSON**: podwójne cudzysłowy dla kluczy i stringów, bez komentarzy, bez znaczników ```. Wewnątrz prozy cytaty zapisuj apostrofami (`'NAPIS'`) [5] (oficjalne).
- **Proza po angielsku, napisy w oryginale.** Pola opisowe (`high_level_description`, `style_description`, `background`, `desc`) zawsze po angielsku. Tylko pole `text` jest w języku napisu, np. po polsku, z diakrytykami wpisanymi wprost, a nie jako `\u0105` [5][6][4] (oficjalne).
- **Klucze i ich kolejność są ściśle określone** (CaptionVerifier ostrzega o nieznanych kluczach, brakach i złej kolejności) [4][6] (oficjalne):
  - poziom główny: `high_level_description`, `style_description`, `compositional_deconstruction`. Inne klucze są nieznane, także `aspect_ratio` (go nie dodawaj; tylko magic prompt v1 go zwraca, a to jest sprzeczne ze schematem [22][5]);
  - `style_description` dla fotografii: `aesthetics`, `lighting`, `photo`, `medium`, `color_palette`;
  - `style_description` dla nie-fotografii: `aesthetics`, `lighting`, `medium`, `art_style`, `color_palette`. **Dokładnie jedno z `photo` / `art_style`, nigdy oba**;
  - `compositional_deconstruction`: `background`, a potem `elements`;
  - element `obj`: `type`, `bbox`, `desc`, `color_palette`;
  - element `text`: `type`, `bbox`, `text`, `desc`, `color_palette`.
- **Pola obowiązkowe:** `compositional_deconstruction` z `background` i `elements` [4]. `high_level_description` jest „mocno zalecane” [4]. W hostowanym Ideogramie bez niego JSON jest traktowany jak tekst [11], więc **zawsze je dawaj**.
- **`style_description` zawsze wypełniaj**: „model nie ma domyślnego stylu” [12]. Bez niego dryfuje w stronę fotografii (zob. Biasy).
- **`medium`**: przykłady oficjalne to `photograph`, `illustration`, `3d_render`, `painting`, `graphic_design` (lista otwarta, „etc.”) [4]. W przykładzie ComfyUI pada też np. „Mixed-media digital collage” [2].
- **bbox**: `[y_min, x_min, y_max, x_max]`, liczby całkowite 0–1000, początek w lewym górnym rogu, **najpierw y** [4][18].
- **Kolory**: wyłącznie `#RRGGBB` WIELKIMI literami. Do 16 w `style_description`, do 5 na element. `color_palette` jest zawsze ostatnim kluczem w swoim bloku [4][6] (oficjalne).
- **Długość**:
  - enkoder przyjmuje do 2048 tokenów [9];
  - `high_level_description` ma maks. 50 słów, 1 zdanie (najwyżej 2) [5][12];
  - `desc` elementu ma 30–60 słów [5];
  - hostowany poradnik zaleca ≤5 elementów dla najlepszej jakości [12], choć oficjalny pełny przykład ma 17 elementów [4]. Dla nas: 2–6 elementów.
- **Wagi**: składnia typu `(słowo:1.3)` nie istnieje. Akcent wyrażasz bboxem, paletą i kolejnością elementów (niepotwierdzone, że wagi szkodzą, ale nie ma ich w schemacie [4]).

## Szkielet promptu
Wariant nie-fotograficzny (domyślny dla warsztatów):
```json
{
  "high_level_description": "[medium/technika] of [główny podmiot + działanie], [układ kadru w 3–6 słowach], [nastrój jako fakt fizyczny].",
  "style_description": {
    "aesthetics": "[2–5 konkretnych cech wyglądu: faktura, kontrast, gęstość, pustka]",
    "lighting": "[źródło światła + kierunek + twardość; dla grafiki np. płaskie/równe]",
    "medium": "[illustration | painting | graphic_design | 3d_render | inne medium jednym wyrażeniem]",
    "art_style": "[technika i materiał: narzędzie, podłoże, ślad ręki, druk/ziarno, ograniczenia palety]",
    "color_palette": ["[#TŁO]", "[#CIEŃ]", "[#ŚWIATŁO]", "[#AKCENT]"]
  },
  "compositional_deconstruction": {
    "background": "[powłoka sceny: podłoże/ściana/niebo/atmosfera; dla grafiki: powierzchnia arkusza]",
    "elements": [
      {"type": "obj", "bbox": [y1, x1, y2, x2], "desc": "[tożsamość podmiotu] — [główne cechy] — [jeden wyróżnik]", "color_palette": ["[#..]"]},
      {"type": "text", "bbox": [y1, x1, y2, x2], "text": "[DOSŁOWNY NAPIS\nDRUGA LINIA]", "desc": "[wielkość, położenie, jedna kategoria kroju, jedna grubość, kolor, technika]", "color_palette": ["[#..]"]}
    ]
  }
}
```
Wariant fotograficzny: w `style_description` zamiast `art_style` daj `"photo": "[aparat/obiektyw/materiał filmowy/ziarno]"` **przed** `medium`, a `medium` ustaw na `"photograph"` [4].

## Co działa
- **Bbox przy każdym głównym elemencie.**
  - Dodanie bboxa usunęło blokadę filtra w zgłoszonym przypadku [19] (społeczność).
  - Bez bboxów model spłaszcza scenę do widoku z boku [25] (społeczność).
  - Pomijaj bbox tylko przy masach, których nie da się policzyć (tłum, pole kwiatów, gwiazdy) [5] (oficjalne).
- **Kształt bboxa przelicz na proporcje.** `[0,0,500,500]` jest kwadratem tylko w kadrze 1:1. Dla obiektu okrągłego czy kwadratowego potrzeba `(x2-x1)/(y2-y1) ≈ W/H`. Błędy kształtu dają duplikaty i złą skalę [5] (oficjalne). Przy 16:9 przybliżenie najwyżej do pasa albo kadr ogólny [28] (społeczność).
- **Jeden podmiot = jeden element.** Części ciała czy przedmiotu opisuj w jego `desc`, nie jako osobne elementy [5].
- **Podłoże zawsze w `background`.** Podłoga, ziemia, woda, kałuże i odbicia nie mogą być elementem `obj`. Inaczej model „zakopuje” postać w pasie podłogi [5][12] (oficjalne).
- **Niczego nie opisuj podwójnie.** Każda rzecz występuje albo w `background`, albo jako element [5].
- **Kolejność elementów zbliżona do kolejności czytania.** Jeśli element odwołuje się do innego („pod napisem…”), ten drugi musi stać wcześniej [18] (społeczność/dostawca). Duże obiekty związane ze ścianą (tło) wpisz w `background` i dodatkowo jako pierwszy element [5].
- **Konkret zamiast nastroju.** Słowa „moody”, „vibrant”, „luminous” czy „stunning” ważą mało albo szkodzą. Lepiej działa źródło i kierunek światła, kolor jako hex i materiał [12][5] (oficjalne).
- **Jedna wartość zamiast wyboru.** Bez „or”, „such as”, „various”, „implied”, „maybe”. W typografii jedna kategoria kroju, jedna grubość i jeden styl [5] (oficjalne).
- **Paleta**:
  - dodaj kolor tła (ciemne tło = ciemny hex w palecie) oraz parę światło/cień [4];
  - hex wyznacza kierunek, a kolor opisany słowami jest tylko interpretacją [18];
  - paleta silnie steruje obrazem, ale nie ustala koloru każdego piksela [11];
  - dla efektu druku wystarczą 3–4 kolory spotowe [13] (oficjalne).
- **Tekst**:
  - każdy osobny blok to osobny element `text`, a dosłowne brzmienie wpisujesz w `text`, nie w `desc` [4][18];
  - nazwa wpisana w `desc` obiektu jest tylko „zgadywana” [18];
  - w jednym napisie najwyżej 5–7 słów [12];
  - długie hasło łam przez `\n` na granicach słów [5];
  - małe liczby zapisuj słownie [12] (oficjalne, hostowane 4.0).
- **Blokada filtra (szary obraz z napisem):**
  - zmień seed [21];
  - dodaj albo popraw bboxy [19][20];
  - dopisz szczegóły w JSON [12].
  - Nie skracaj promptu do prozy (oficjalne / społeczność).
- **Iteracja**: zmieniaj tylko potrzebne pole, a resztę JSON zostaw. Mimo to cały obraz może się przesunąć [18].

## Biasy i pułapki
- **Domyślnie dryfuje w fotografię.** Instrukcja magic promptu v1 każe przy braku wskazań wybierać `photograph` i „estetykę iPhone’a” [5]. Hostowany poradnik mówi, że model nie ma domyślnego stylu [12]. Jeśli chcesz czegoś innego, **zawsze** jawnie ustaw `medium` i `art_style`.
- **Czasowniki „Paint/Draw/Illustrate” nie oznaczają medium**, tylko „pokaż”. O medium decyduje rzeczownik (watercolor, ink drawing…) [5].
- **Sam „zaludnia” puste sceny.** Tak wytrenowano podpisy, które opisywały wszystko [10][5]. Gdy chodzi o pustkę, napisz to wprost („minimal, single subject, empty negative space”), bo to słowa, które v1 traktuje jako wyłączenie zaludniania [5].
- **Słowo „warm”** w opisie gradacji fotografii daje bursztynowy „AI-look”. Lepiej nazwij źródło światła (świeca, sodowa latarnia) [5] (oficjalne, reguła magic promptu).
- **Zmyślone efekty**: nie dopisuj „glitch”, „digital artifacts” ani „dissolved”, jeśli nie są celem [5].
- **Filtr bezpieczeństwa** w lokalnym ComfyUI blokował 53–93% prozatorskich promptów zależnie od seeda, także dla jeziora o świcie [21]. Fałszywe alarmy zdarzają się też przy JSON [20]. U nas krótka proza dała szary obraz z błędnie wypisanym komunikatem [3] (społeczność / nasza konfiguracja).
- **Przykład z oficjalnej dokumentacji bez bboxa** (żaglówka) według zgłoszenia zawsze się blokuje [19] (społeczność).
- **16:9 jako obrócony portret**: zgłoszono kadr wyglądający jak obrócony portret. Pomaga spójne z proporcją ustawienie bboxów [24] (społeczność, słabe źródło).
- **Pierwszy plan i tło się nie łączą** [29]. Raz zgłoszono też upór przy stylu anime w scenach fantasy mimo prośby o fotografię [20] (społeczność, pojedyncze relacje).
- **Polskie znaki w napisach** mogą znikać albo się podwajać [26] (społeczność). Duży napis jest pewniejszy niż mały (angielski: ok. 97% vs ok. 90%) [12]. Polskiego u nas nie testowaliśmy.
- **Przezroczyste tło nie działa** (VAE bez alfy) [23]. Do wycinania jest osobne narzędzie Studia „usuwanie tła” [32] (nasza konfiguracja).
- **Pełny przykład oficjalny zawiera znak wodny agencji** jako element `text` [4]. Model zna więc podpisy ze znakami wodnymi i może je dorysować przy „archiwalnych/prasowych” opisach (niepotwierdzone).
- **Prompty z hostowanego Ideogram.ai** (style codes, negative prompt, magic prompt produkcyjny) **nie przenoszą się 1:1**. Magic prompt w repozytorium „nie jest tym z produkcji” [4].

## Poza fotorealizmem
- Mechanizm: `art_style` zamiast `photo`, `medium` ≠ `photograph` [4]. Dokumentacja i ComfyUI pokazują: ilustrację miękką i współczesną, tusz z akwarelą, flat vector [14], plakat graficzny [11], kolaż mixed-media [2].
- **Opisuj technikę i materiał, nie nazwiska.** Hostowany poradnik zaleca nazwać medium oraz artystę lub nurt [12]. Na naszych warsztatach unikamy jednak naśladowania stylów „na skróty” [31], więc nazwę zastąp opisem śladu:
  - narzędzie: rapidograf, węgiel, pędzel na sucho;
  - podłoże: papier czerpany, tektura, płótno;
  - sposób nakładania: laserunek, impast, wycinanka;
  - ograniczenie palety.
- **Rysunek, ilustracja**: `medium: "illustration"`. W `art_style` opisz narzędzie, kreskę i wypełnienie. Wiele technik ręcznych v1 zalicza do ilustracji: tusz, akwarela, olej, wektor, pixel art [5].
- **Malarskość**: `medium: "painting"` [4]. Faktura (impast, laserunek, ślad pędzla) wpisz w `art_style`/`aesthetics`.
- **Druk, ziarno, risograf, półton**:
  - opisz zniszczoną fakturę druku (półton risografu, ząbek papieru, przesunięcia pasowania), 3–4 kolory spotowe, bez 3D i bez gradientów [13] (oficjalne, hostowane);
  - według v1 efekty medium (ziarno, faktura papieru, półton, risograf) **nie należą do `background`**, tylko do opisu ogólnego i stylu [5];
  - oficjalny przykład wizytówki ma jednak „subtle paper texture” w `background` [4];
  - reguła dla nas: fizyczna powierzchnia arkusza może być w `background`, a technika i ziarno idą do `art_style`/`aesthetics`/HLD.
- **Taśma, film, archiwum**:
  - w wariancie foto pole `photo` przyjmuje materiał i ziarno, np. „vintage grainy 35mm film… halftone scan… light leaks” w przykładzie ComfyUI [2], a także opis aparatu w stylu „Hasselblad medium format, slightly desaturated” [12];
  - v1 zakazuje rozmycia ruchu i „kinowego” gradingu w zwykłych zdjęciach, chyba że to zamierzone [5].
- **Kolaż**: przykład w naszym workflowie używa `medium: "Mixed-media digital collage"`, fotograficznych wycinanek z białą obwódką, podartego papieru i stempli. Każdy wycinek jest osobnym `obj` z bboxem [2] (nasza konfiguracja / ComfyUI). Mieszanie tradycji wymaga wyraźnej granicy między nimi [13].
- **Abstrakcja**: brak źródeł (nie wiadomo, jak model sobie radzi). Propozycja (niepotwierdzona): elementy `obj` jako nazwane kształty i plamy z bboxem i własną paletą, `medium: "painting"` lub `"graphic_design"`. Unikaj słów „implied/suggested”, bo v1 każe opisywać konkretnie [5].
- **Anime/komiks** działa w JSON (`medium: "anime illustration"`) [29][28], ale nie jest celem warsztatów.

## Ruch / czas / dźwięk
- Nie dotyczy: pojedynczy obraz. Obraz może posłużyć jako pierwsza lub ostatnia klatka dla modeli wideo w Studiu (H3, LTX, WAN) [33] (nasza konfiguracja). Wtedy ustaw proporcje zgodne z wideo, zwykle 16:9, i zostaw w kadrze miejsce na ruch (niepotwierdzone jako metoda; to decyzja uczestnika).

## Sprawdź przed wysłaniem
- [ ] JSON się parsuje, nie ma znaczników ``` ani komentarzy i ma tylko 3 klucze główne (bez `aspect_ratio`).
- [ ] `high_level_description` ma ≤50 słów, po angielsku i zaczyna się od podmiotu.
- [ ] `style_description` jest wypełnione: dokładnie jedno z `photo`/`art_style`, z kolejnością kluczy jak w schemacie, a `medium` jest jawne.
- [ ] Proza jest po angielsku. Napisy w `text` są dosłowne, z polskimi znakami wpisanymi wprost, ≤5–7 słów, z łamaniem przez `\n`.
- [ ] Hexy są WIELKIMI literami `#RRGGBB`: ≤16 w stylu, ≤5 na element, z kolorem tła i parą światło/cień, a `color_palette` jest ostatnim kluczem.
- [ ] Główne elementy mają bbox `[y1,x1,y2,x2]` w zakresie 0–1000, kształty są przeliczone na proporcje kadru, a podłoże jest w `background`.
- [ ] Jeden podmiot to jeden element, nic nie jest opisane podwójnie, nie ma słów „or/such as/various/implied” ani pustych przymiotników nastroju.
- [ ] Nie ma oczekiwań wobec negative promptu ani przezroczystości.
- [ ] Do drobnych napisów profil „jakość”. Przy szarym obrazie z „blocked” zmień seed i bboxy.

## Źródła
[1] Konfiguracja modelu w Studiu — modele/obraz/ideogram-4.yaml — nasza konfiguracja
[2] Workflow ComfyUI Studia — workflows/obraz/ideogram4_tekst-na-obraz.api.json (węzły 98:24, 98:155, 98:10, 98:147, 98:157, podgraf 134, przykład kolażu) — nasza konfiguracja
[3] Poradnik Studia + test na Sparku 2026-10-04 — poradniki/ideogram-4.md — nasza konfiguracja
[4] Ideogram 4 — Prompting Guide — https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md — oficjalne
[5] Magic prompt system prompt v1 — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/magic_prompt_system_prompts/v1.txt — oficjalne (identyczny z tym w naszym workflowie)
[6] CaptionVerifier — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/caption_verifier.py — oficjalne
[7] Inference (presety samplera) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/inference.md — oficjalne
[8] Pipeline (asymetryczne CFG, gałąź bezwarunkowa) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/pipeline.md — oficjalne
[9] Model architecture (max 2048 tokenów tekstu) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/model_architecture.md — oficjalne
[10] README repozytorium — https://github.com/ideogram-oss/ideogram4 — oficjalne
[11] Ideogram Docs — JSON Prompting (Ideogram 4.0) — https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0 — oficjalne (produkt hostowany)
[12] How to JSON prompt for Ideogram 4.0 (18.06.2026) — https://ideogram.ai/blog/ideogram-4-json-prompting/ — oficjalne (produkt hostowany)
[13] The Ideogram 4.0 prompt guide — https://ideogram.ai/blog/claude-mcp/ — oficjalne (produkt hostowany)
[14] Ideogram 4.0 Technical Details — https://ideogram.ai/blog/ideogram-4.0/ — oficjalne
[15] ComfyUI — Ideogram 4.0 Day-0 Support — https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui — oficjalne (ComfyUI)
[16] ComfyUI Docs — Ideogram v4 — https://docs.comfy.org/tutorials/image/ideogram/ideogram-v4 — oficjalne (ComfyUI)
[17] ComfyUI Docs — BuildJsonPromptIdeogram — https://docs.comfy.org/built-in-nodes/BuildJsonPromptIdeogram — oficjalne (ComfyUI)
[18] Runware — Ideogram 4.0 structured prompts — https://runware.ai/docs/models/ideogram-4-0/guides/structured-prompts — społeczność (dostawca API)
[19] GitHub issue #13 „Prompting documentation bug” (bbox usuwa blokadę) — https://github.com/ideogram-oss/ideogram4/issues/13 — społeczność
[20] GitHub issues #5 i #12 (fałszywe alarmy, bboxy, jakość ludzi, dryf w anime) — https://github.com/ideogram-oss/ideogram4/issues/5 , https://github.com/ideogram-oss/ideogram4/issues/12 — społeczność
[21] GitHub issue #14 (pomiar blokad w ComfyUI vs seed) — https://github.com/ideogram-oss/ideogram4/issues/14 — społeczność
[22] GitHub issue #33 (sprzeczność: `aspect_ratio` w v1 vs schemat) — https://github.com/ideogram-oss/ideogram4/issues/33 — społeczność
[23] GitHub issue #35 (brak przezroczystości) — https://github.com/ideogram-oss/ideogram4/issues/35 — społeczność
[24] GitHub issue #21 (obrócony kadr 16:9) — https://github.com/ideogram-oss/ideogram4/issues/21 — społeczność
[25] r/StableDiffusion „Ideogram 4 compared with Krea 2 in natural language prompting” (snapshot) — https://reddit.sentinel-team.org/posts/1ursrrv/snapshots/2026-07-09T23%3A35%3A57.68774Z — społeczność
[26] invideo — Best AI model for text in images (08.2026) — https://invideo.io/blog/best-ai-model-text-in-images/ — społeczność
[27] GoEnhance — Ideogram 4.0 review — https://www.goenhance.ai/blog/ideogram-4-review — społeczność
[28] EvoLinkAI — awesome-ideogram-4.0-prompts — https://github.com/EvoLinkAI/awesome-ideogram-4.0-prompts — społeczność
[29] ipentec — Ideogram 4.0 の画像生成結果 — https://www.ipentec.com/document/ai-image/image-generation-ideogram-4-model — społeczność
[30] Hugging Face — ideogram-ai/ideogram-4-nf4 — https://huggingface.co/ideogram-ai/ideogram-4-nf4 — oficjalne
[31] Zasady rozmowy w Studiu — prompty/proces.md — nasza konfiguracja
[32] Opis Studia dla uczestników (usuwanie tła w obszarze Obraz) — notatki własne (niepublikowane) — nasza konfiguracja
[33] README Studia (modele wideo z pierwszą/ostatnią klatką) — README.md — nasza konfiguracja
