<!-- Karta modelu dla promptmakera. modele: minimax-h3, minimax-h3-fl2va, minimax-h3-referencje, minimax-h3-klatki, fasth3-v2 -->
# MiniMax H3 (+ FastH3 V2) — wideo z dźwiękiem stereo

## Czym jest i do czego się nadaje
- Otwarty model „omni”: obraz + **dźwięk stereo 32 kHz** (dialog, śpiew, efekty, muzyka) w jednym przebiegu, 24 kl./s, 4–15 s [3][5] (oficjalne).
- Dwa checkpointy: **FL2VA** (0, 1 lub 2 obrazy: tekst → wideo, pierwsza / ostatnia / obie klatki) i **Ref2VA** (referencje: ≤ 9 obrazów, ≤ 3 wideo po 2–15 s (łącznie ≤ 15 s), ≤ 3 dźwięki po 2–15 s (łącznie ≤ 15 s), razem ≤ 12 plików) [3] (oficjalne).
- Enkoder tekstu: **Qwen3-VL-32B** (warstwa 50). Widzi też obrazy i (przy 2 kl./s) klatki wideo referencji; **dźwięków referencyjnych NIE widzi** — trafiają tylko do generatora [3][12] (oficjalne / kod).
- H3 był uczony na bardzo szczegółowych opisach w stałym formacie („Context-IR”). W chmurze MiniMax przepisuje prompt za użytkownika; **w otwartych wagach tego nie ma — to Ty jesteś tym przepisywaczem** i piszesz od razu w formacie IR [3] (oficjalne), [18] (społeczność).
- Mocne: wieloujęciowość z cięciami w zadanym czasie, ruch kamery, dźwięk zsynchronizowany z akcją, łączenie wielu referencji w jedną scenę, płynne przejście pierwsza→ostatnia klatka [1][3] (oficjalne), [26][31] (społeczność).
- **Czego NIE robi dobrze:**
  - twarzy w planach ogólnych (zniekształcone; plany średnie i bliskie OK) [26] (społeczność);
  - ciszy i pauz — w „pustych” miejscach potrafi mamrotać / bełkotać [17][23] (społeczność);
  - głośnego tła pod dialogiem (ambient cichnie, gdy ktoś mówi; zwłaszcza Ref2VA) [24] (społeczność);
  - pewnego głosu zza kadru (usta postaci często i tak się ruszają) [27] (społeczność);
  - rozdzielenia akcentów dwóch mówiących (akcent „przecieka” na drugą postać) [30] (społeczność);
  - mrugania (postacie prawie nie mrugają) [22] (społeczność);
  - płynnej animacji 2D (wychodzi „na dwójkach”, 12 kl./s) [16] (społeczność);
  - pewnego tekstu w kadrze (kruche; lepiej dodać w montażu) [31] (społeczność).

## Co uczestnik ustawia w Studiu
Jedna pozycja „MiniMax H3” — wariant wybiera się sam wg podanych plików [L1] (nasza konfiguracja):
- **nic** → tekst → wideo (T2VA, checkpoint FL2VA);
- **pierwsza klatka** → I2VA; **ostatnia** → L2VA; **obie** → FL2VA;
- **jakakolwiek inspiracja** (obrazy do 9, wideo do 3, dźwięki do 3) → **Ref2VA**; wtedy **pierwsza/ostatnia klatka są ignorowane** [L1].
Osobna pozycja „MiniMax H3 · klatki kluczowe” i „FastH3 V2” — niżej.

Pola wspólne [L1][L2]:
- **prompt** — jedno pole, trafia **bez żadnej obróbki** do węzła ComfyUI (Studio nic nie dokleja). **Linii wyrównania z obrazem nie ma w workflow — musisz ją napisać sam** (patrz Format) [11][L2] (kod / nasza konfiguracja).
- **Brak negative promptu.** Wagi są „CFG-distilled”, workflow używa `BasicGuider` (bez gałęzi negatywnej) [3][6][L2] (oficjalne).
- **proporcje** 16:9 (domyślnie), 21:9, 4:3, 1:1, 3:4, 9:16 [L1].
- **rozdzielczość** 480p (0,4 MP, 16:9 = 864×480, domyślnie) / 720p (0,9 MP, 1280×736) [L1][13]. Natywnie krótszy bok 768 px [3]. Na 480p model trzyma strukturę promptu (ujęcia, kamera, rozmieszczenie) zwykle lepiej niż na 768p [20] (społeczność), ale twarze w dalszych planach są słabsze [26] (społeczność). 720p FL2VA/I2VA: rzadko „zaciemnienie kadru jak przesłona” zależne od seedu [28] (społeczność) — zmień seed.
- **długość** 1–15 s (domyślnie 10), krok 0,5 s; klatki przyciągane do siatki 17n+5 przy 24 kl./s (5 s → 124 kl.) [L1][L2]. Oficjalnie 4–15 s [3]; zakres treningowy ok. 124–362 kl. (≈5–15 s), krótsze „nietestowane” [11] (kod). **Ustawiaj ≥ 5 s.**
- **tryb**: szybki = LoRA turbo (FL2VA 8 kroków, Ref2VA i klatki 4 kroki) / jakość = 20 kroków [L1][L2]. Turbo: „nieco słabszy dźwięk i ruch” [7] (oficjalne).
- **seed** — porównując wersje promptu, trzymaj seed stały i zmieniaj jedną rzecz [31] (społeczność).

Ref2VA (inspiracje) — szczegóły z kodu [11][L1][L2]:
- Znaczniki w kolejności plików, numeracja osobna dla typu: `<Picture 1..9>`, `<Video 1..3>`, `<Audio 1..3>`. Studio pokazuje znacznik przy każdym pliku.
- **Dźwięk z pliku wideo nie jest używany** (Studio podaje tylko obraz wideo) → `<Audio n>` to wyłącznie pliki dźwiękowe. Nie pisz „dźwięk z `<Video 1>`”.
- Wideo-referencja dłuższe niż klip jest obcinane do długości klipu; obrazy-referencje są zmniejszane do rozdzielczości generacji (drobny tekst/detal z referencji przepada na 480p).

Klatki kluczowe (`minimax-h3-klatki`) [L1][L2][8][13]:
- Checkpoint Ref2VA + 1–3 obrazy przypięte do sekund `czas1..3` (muszą mieścić się w długości). Opcjonalna referencja = `<Picture 1>`.
- **Klatek kluczowych enkoder tekstu nie widzi** — nie mają znaczników. Nie pisz `<Picture 2>` dla klatki kluczowej; opisz słowami, co ma być widać w danej sekundzie, i ustaw tam cięcie lub punkt akcji [8] (oficjalne).

## Format promptu
- **Język: angielski** dla całego opisu; **dosłownie w oryginale tylko kwestie/teksty śpiewane (w `<d>`) i napisy widoczne w kadrze** [1][2] (oficjalne); pracownik MiniMax: „poza treścią do wygenerowania i dialogami wszystko po angielsku” [15]. Opis po chińsku/polsku bywa czytany na głos jako kwestia [15] (społeczność).
- **Długość: długo i szczegółowo.** Oficjalne przykłady 150–1000 słów; Ref2VA `detailed_description` zwykle **350–500 słów** [2][3] (oficjalne). Krótkie prompty bez referencji to typowa przyczyna złego wyniku [18][31] (społeczność). Limitu znaków w ComfyUI praktycznie brak [12] (kod). Heurystyka (niepotwierdzone): 1 ujęcie ~120–200 słów, 2–4 ujęcia ~250–450.
- **Bez wag** `(word:1.3)` — tokenizer H3 ma wagi wyłączone, nawiasy staną się tekstem [12] (kod). **Bez JSON, bez list tagów.** Pełne zdania, czas teraźniejszy.
- **Nie nazywaj tego, czego ma nie być** (przy CFG 1 słowo „text” w „no text” dodaje tekst). Pisz pozytywnie: „the sign above the door is blank” [6] (oficjalne). Uwaga: oficjalne szablony Comfy same zawierają „no subtitles…” [13] — mimo to trzymaj się zasady pozytywnej.

**Tryby FL2VA (bez inspiracji)** — 1. linia = instrukcja, potem pusta linia, potem 3 pola rozdzielone pustymi liniami, w tej kolejności [1] (oficjalne):
- T2VA (bez obrazów): brak linii instrukcji.
- I2VA (tylko pierwsza klatka), dosłownie:
  `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.` (tak samo w promptach społeczności [14])
- FL2VA (obie), dosłownie (bez nawiasów ostrych — tak w oryginale); `S.SS` = długość klipu z 2 miejscami, `N` = numer ostatniego ujęcia:
  `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA (tylko ostatnia klatka — w węźle jest wtedy `<Picture 1>` [11]):
  `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
- Pola: `integrated_multimodal_description:` (obraz, akcja, ujęcia, mówiący, dialog, śpiew, dźwięk diegetyczny wzdłuż osi czasu) · `overall_soundscape:` (1–4 zdania: ambient, odgłosy akcji, oddechy, śmiech; bez dialogów; `N/A` tylko przy całkowitej ciszy) · `non_diegetic_music:` (1–3 zdania: instrumenty, tempo, rytm, dynamika — bez słów nastroju; `N/A`, gdy brak) [1].

**Ref2VA (inspiracje)** — sześć sekcji w tej kolejności, wszystko po angielsku [2] (oficjalne):
`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`.
- `<Subject N>` = treść wyciągnięta z referencji (osoba, miejsce, rekwizyt, styl, ruch); `<Picture N>` osobno tylko gdy obraz jest konkretną klatką/kotwicą kadru lub storyboardem; `<Video N>` tylko dla relacji całego wideo (edycja, kontynuacja, struktura kamery/montażu); `<Audio N>` = sygnał kopiowany lub referencja [2].
- `summary`: jedno zdanie-akapit z prefiksem typu w nawiasach: `[reference generation]`, `[keyframe completion]`, `[video editing]`, `[video continuation]`, `[audio reuse]`, `[audio reference]`, łączone ` + ` [2].
- `retention_analysis`: jedna linia na etykietę; obraz/wideo: `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`; dźwięk: `fully_copy` / `partially_copy` / `reference` / `weak_reference`. Bez `(Sx)` w tej sekcji [2].
- `detailed_description`: 1–2 zdania stylu PRZED `[Shot 1]`, potem ujęcia; etykiety wstawiaj przy pierwszym pojawieniu się i tam, gdzie działają („the shot begins from <Picture 1>”) [2].
- Format nie musi być kopiowany słowo w słowo — ważna spójność etykiet i jasne relacje [25] (społeczność, odpowiedź na HF). Comfy: „Ref2VA jest bardzo wrażliwy na sformułowania; precyzyjne znaczniki i jawne przypisanie, która referencja steruje czym” [13] (oficjalne).

**Wspólne znaczniki** [1][2] (oficjalne):
- Ujęcia: `[Shot 1]` bez czasu; dalej `[Shot 2] At 00:03.500, the camera cuts to …` — czasy rosnące i < długości klipu. Cięcia: „the camera cuts to / the shot cuts to / transitions to / changes to / switches to”; przenikanie/ściemnienie tylko gdy chciane.
- Mówiący: stały ID `(S1)`, `(S2)` we wszystkich ujęciach; wspólnie `(S1,S2)`; postać, która nie mówi — bez ID. Przy pierwszym wystąpieniu opisz głos (wiek, płeć, barwa, tempo, akcent) POZA `<d>`.
- Dialog/śpiew: `<d>[Language] dokładne słowa.</d>` — w środku tylko tag języka i słowa. Kończ kwestię kropką/?/! przed `</d>` [2]; brak kropki sprzyja mamrotaniu po kwestii [17] (społeczność).
- Głos zza kadru: dokładnie `says in an off-screen voiceover:` + po `</d>` „while his/her lips remain completely closed” [1].
- Kwestia przez cięcie: `<scenetrans>` w obu miejscach + „continues seamlessly across the cut” [1]. Znacznik ucięcia: przewodnik pisze `<cutoff>`, a tokenizer ma `<|cutoff|>` [1][12] — niejasne; **nie używaj**.
- Napis w kadrze: w angielskim cudzysłowie, dosłownie, w oryginale: `a hand-painted sign reading "…"` [1].

## Szkielet promptu
T2VA / I2VA / FL2VA / L2VA (linię instrukcji wstaw tylko gdy są klatki):
```
[linia instrukcji — dosłownie wg trybu]

integrated_multimodal_description: [Shot 1] [styl/medium], [plan i kompozycja otwarcia], [podmiot: wygląd, ubiór, pozycja w kadrze], [miejsce, światło, faktura, kluczowe rekwizyty]. [ruch kamery: typ + amplituda + tempo jako zdanie]. [akcja: start → rozwinięcie → wynik], [dźwięk diegetyczny przy akcji]. [opis głosu] (S1) says: <d>[Language] [kwestia].</d> [co robi po kwestii, usta zamknięte]. [Shot 2] At 00:0[s].[ms], the camera cuts to [nowa informacja: miejsce/stan/punkt widzenia/czas], [ruch kamery], [akcja], [dźwięk].

overall_soundscape: [ciągły ambient], [odgłosy akcji w kolejności], [dźwięki niewerbalne].

non_diegetic_music: [instrumenty], [tempo], [rytm], [zmiana dynamiki] | N/A
```
Ref2VA (inspiracje):
```
subject_definitions:
<Subject 1> is [kto/co] in <Picture 1>, [cechy do zachowania].
<Subject 2> is [miejsce/styl/ruch] from <Picture 2> / <Video 1>, [cechy].
<Audio 1> is the voice-timbre reference for <Subject 1> (S1). | <Audio 1> is [ambient/muzyka/kwestia] [rola].

summary:
[typ zadania + typ zadania] [1 akapit: co się dzieje, które etykiety za co odpowiadają].

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): [marker] - [co zostaje].
<Audio 1>: [marker] - [co jest kopiowane / do czego referencja].

detailed_description:
The target video is in [styl/medium, paleta, światło, faktura].
[Shot 1] [jak w T2VA, z etykietami przy pierwszym pojawieniu się] … <Subject 1> (S1) says: <d>[Language] [kwestia].</d> …
[Shot 2] At 00:0[s].[ms], the shot cuts to …

overall_soundscape:
[…]

non_diegetic_music:
[…] | N/A
```
Klatki kluczowe: szkielet Ref2VA; jeśli jest referencja — `<Subject 1> is [kto] in <Picture 1>`; summary `[keyframe completion]` (+ `reference generation`, jeśli jest referencja); w `detailed_description` cięcia lub kluczowe momenty dokładnie w sekundach `czas1..3` („At 00:05.000 … the composition shows [opis klatki słowami]”). Bez referencji: pomiń `subject_definitions` i `retention_analysis` albo zostaw je z opisem słownym (niepotwierdzone — brak przykładu w źródłach).

## Co działa
- **Najpierw cała scena, potem ujęcia**; styl i kompozycja otwarcia na początku `[Shot 1]` [1][6] (oficjalne).
- **Każde cięcie = nowa informacja** (miejsce, stan, punkt widzenia, czas); jeśli zmienia się tylko kadr — ruch kamery zamiast cięcia [1] (oficjalne).
- **Kamera jako czynność, nie cel**: „keep him in frame” nie działa; „the camera pulls out with large amplitude, matching his walking speed” działa [31] (społeczność). Jedna dominująca kamera i jedna główna akcja na ujęcie — zwłaszcza w wyższej rozdzielczości [20][31] (społeczność).
- **I2VA: kotwica → start akcji → rozwinięcie → wynik**; zachowaj tożsamość, ubiór, kolory, układ z obrazu [1]. **FL2VA: jedno ciągłe ujęcie**, opisuj ścieżkę między stanami, nie dwa statyczne obrazy; ostatnia klatka osiągnięta pod koniec [1] (oficjalne). Element, który ma się ruszać mimo podobnych klatek (liście, woda), nazwij jako jedyny animowany i opisz jego drogę i powrót [21] (społeczność).
- **Ostatnia klatka poprzedniego klipu jako pierwsza** = kontynuacja ujęcia [L1].
- **Opisz dźwięk w każdej chwili** — także „ciszę” jako cichy ambient (szum lodówki, wiatr); słowo „silently” przy czynnościach bez mowy; po kwestii „closes her lips” [17][23] (społeczność). Niechciana mowa w cichym ujęciu → wypisz jawnie oba pola dźwięku i generuj ponownie [6] (oficjalne).
- `non_diegetic_music: N/A` skutecznie wyłącza muzykę (czasem i tak przecieka, ~20%) [31] (społeczność).
- **Akcent przez tag języka**: `<d>[French] English words</d>` dał francuski akcent tam, gdzie opis „with a French accent” nie działał [19] (społeczność).
- **Mruganie, drobne gesty** — wpisz jawnie z czasem („she blinks slowly at 00:02”) [22] (społeczność).
- **Referencje**: każdej przypisz rolę (tożsamość / styl / ruch / kamera / głos) — „jawne przypisania działają dużo lepiej” [7] (oficjalne). Gdy referencje niosą wygląd, w opisie skup się na nowej akcji [31] (społeczność).
- **Głos referencyjny**: krótkie nagranie (~4 s) i wprost „`<Audio 1>` is the voice-timbre reference for `<Subject 1>` (S1)” — dłuższe sprzyjało bełkotowi na starcie [17] (społeczność, pojedyncze źródło).
- **Kwestia, która trafia do złej osoby** → wygeneruj ją narzędziem głosowym i podaj jako `<Audio n>` tego mówiącego; przy wielu mówiących wiąż kwestie z widocznymi zdarzeniami, nie z timecode’em [6] (oficjalne).

## Biasy i pułapki
- **Brak linii instrukcji przy klatkach** — Studio jej nie dopisuje (stary poradnik Studia twierdzi inaczej — błędnie) [11][L2].
- **Zły format dialogu**: poprawnie `<d>[Polish] …</d>`, nie `<d>Polish: …</d>` [1][2] (oficjalne).
- **Bełkot / „przerywnik” w pierwszych ~0,5 s**, zwłaszcza Ref2VA; zależny od seedu; zamiana `<d>` na cudzysłów pomagała części osób, innym nie [17] (społeczność). Generuj kilka seedów.
- **Za długa kwestia w za krótkim czasie** albo **za dużo wolnego czasu** po krótkiej kwestii → pośpiech, powtórki, wypełniacze [31][35] (społeczność). Brak oficjalnej normy słów/s — dopasuj długość klipu do kwestii, zostaw oddech.
- **Narrator nazwany jak postać w kadrze** („the man”) → model rusza ustami tej postaci. Lepiej „Female narrator voice, saying: …” albo osobny opis głosu bez odniesienia do widocznej osoby [27] (społeczność). Nadal zawodne.
- **Przeciek akcentu/głosu** między dwoma mówiącymi [30] (społeczność) → różnicuj głosy mocno (płeć, wiek, barwa), a krytyczne głosy dawaj jako `<Audio n>`.
- **Ambient przykryty dialogiem** [24] (społeczność) → ważne tło dodaj w montażu albo ujęcie bez dialogu.
- **Bias „reklamy TV”/połysku** przy krótkich, ogólnych promptach (pojedyncza opinia) [18] (społeczność) → zawsze nazwij medium i fakturę na początku.
- **Twarze w planie ogólnym** [26]; **rumieńce/czerwone policzki narastające w Ref2VA** [29] (społeczność) → plany średnie/bliskie dla twarzy.
- **Postać nie mówi, a jej ID jest** → mowa się pojawi; ID tylko dla tych, którzy wydają głos [1].
- **Pomieszane języki** (polskie nazwy własne w opisie, polski opis akcji) → bełkot lub czytanie opisu na głos [15][35] (społeczność). Polskie słowa tylko w `<d>` i w cudzysłowie napisu.

## Poza fotorealizmem
- **Słowo stylu na samym początku `[Shot 1]`** (Ref2VA: zdanie stylu przed `[Shot 1]`). Oficjalna lista: `Cinematic`, `live-action`, `2D-animated`, `3D CG`, `claymation`, `watercolor`, `vintage film` [1][2] (oficjalne).
- **Najmocniejsza dźwignia: obraz.** W I2VA/FL2VA styl jest „wyprowadzany z obrazu referencyjnego” [1] (oficjalne) → zrób klatkę w docelowej technice (rysunek, kolaż, akwarela) innym modelem Studia i podaj jako pierwszą klatkę albo `<Picture n>` z rolą stylu (`weak_reference` / `attribute_transfer`) [2].
- **Rysunek/animacja odręczna** — słownik z oficjalnego skilla MiniMax: crayon, chalk, colored pencil, pastel, rough brush; lines slightly jittering, uneven smudging, frayed edges, a redrawn-every-frame feel; „flat hand-drawn animation” w przestrzeni live-action [4] (oficjalne). Akwarela/komiks (przykład API): „keep the watercolour texture, visible ink outlines, off-register paper grain” [34] (społeczność). Animacja 2D i tak wyjdzie zwykle 12 kl./s („na dwójkach”) [16] — dla odręcznego charakteru to zaleta.
- **Papier / stop-motion** [4] (oficjalne): visible paper fibers, folds, seams, cut edges, visible thickness; frame-by-frame, hand-manipulated motion: small stepped movements, tiny pauses, slight rebounds, pieces sliding and settling; physical shadows; layered paper diorama. Zamiast „no smooth CG” pisz pozytywnie o ruchu skokowym.
- **Kolaż** [4] (oficjalne): flat bold color fields, black-and-white halftone photographic cut-outs, colored cardstock accents, torn edges, soft paper shadows; pieces pop in, slide into place, press flat, pause, lock. Dźwięk: paper rustle, scissors, tape peel, page flip [4].
- **Taśma / film / archiwum**: `vintage film` (oficjalne [1]); z przykładów API (bez potwierdzenia lokalnie): „35 mm film look with fine grain, soft highlight halation”, „1990s film grain, scanlines, chromatic aberration, light leaks”, „VHS tracking artifacts” [13][33] (społeczność/vendor).
- **Komiks/tusz**: „bold comic-book ink style, heavy linework, limited palette” — szablon Comfy Ref2VA [13] (oficjalne Comfy).
- **Mieszanie**: live-action + elementy rysowane działa jako opis „hand-drawn luminous animation in a live-action space”, z wyraźnym kontaktem rysunku z realną dłonią/przedmiotem [4][33].
- **Abstrakcja, czysta faktura, malarstwo materii** — brak źródeł; nie wiadomo, jak model reaguje (niepotwierdzone). Bezpieczniej przez klatkę/referencję w tej technice.
- `embedding:minimaxh3_…` (style społeczności) — w naszej instalacji nie potwierdzono plików; **nie używaj** [6].

## Ruch / czas / dźwięk
- **Kamera = typ + amplituda + tempo**, jako naturalne zdanie w ujęciu, nie etykiety na końcu [1] (oficjalne). Typy: Zoom In/Out (ogniskowa), Push In/Pull Out (jazda), Pan Left/Right, Truck Left/Right, Tilt Up/Down, Pedestal Up/Down, Arc Shot, Tracking Shot, Static Shot, Shake Slightly/Strongly, POV, Roll Clockwise/Counterclockwise. Amplituda: `with small amplitude` / `with large amplitude`; tempo: `at slow speed` / `at fast speed`; średnie pomijaj [1]. „Dolly in/out” nie ma w słowniku [1] — używaj push in / pull out.
- **Czas**: cięcia `At MM:SS.mmm`; pierwsze ujęcie bez czasu; wszystkie czasy < długości klipu [1]. Ciasno upakowane timecody to częsty błąd [31] (społeczność); próg „nie gęściej niż co ~2–3 s” — niepotwierdzone. FL2VA — najlepiej 1 ujęcie [1].
- **Długość**: ≥ 5 s (zakres treningowy ~5–15 s) [3][11]. Dialog: jeden mówiący i jedna kwestia na klip, gdy liczy się jakość mowy [35] (społeczność); „1–2 krótkie kwestie na 5–8 s” — heurystyka, niepotwierdzone.
- **Dźwięk — gdzie co pisać** [1] (oficjalne): dialog, śpiew, muzyka słyszana w scenie (radio, ktoś gra) i efekty związane z konkretną akcją → w ujęciu, w chwili zdarzenia; tło i odgłosy całego klipu → `overall_soundscape`; muzyka tylko dla widza → `non_diegetic_music` (instrumenty, tempo, rytm, dynamika; bez „smutna/radosna”).
- **Polski dialog**: polski NIE jest wśród 11 stabilnie wspieranych języków (ar, zh, en, fr, de, it, ja, ko, pt, ru, es); „inne języki w różnym stopniu” [3] (oficjalne). Zapis: `<d>[Polish] …</d>` (analogia do `[English]`/`[Chinese]` [1][2]; tag `[Polish]` niepotwierdzony testem). Krótko, prosto, bez skrótowców i rzadkich nazw własnych [35]. Plan B: nagrać/wygenerować kwestię narzędziem głosowym Studia i podać jako `<Audio n>` (Ref2VA) z `fully_copy`/`partially_copy`, wpisując w `<d>` dokładnie te słowa [2][6] (oficjalne) — albo podłożyć głos w montażu.
- **Polskie napisy w kadrze**: w cudzysłowie, dosłownie [1]; renderowanie tekstu kruche, polskie znaki niepotwierdzone → napisy raczej w montażu [31].
- **Śpiew**: tekst piosenki też w `<d>[Language] …</d>` [6] (oficjalne).

## FastH3 V2 (`fasth3-v2`) — różnice
- Destylat DMD2 od FastVideo; ten sam enkoder, VAE i **ten sam format promptu** (T2VA/I2VA/FL2VA/L2VA) [9][10] (oficjalne).
- Tylko pola: klatki pierwsza/ostatnia, proporcje, rozdzielczość, długość, seed; **brak trybu i brak inspiracji** — Ref2VA nie był destylowany [9][L1].
- Karta HF: destylowany tylko T2VA, „FL2VA nie był destylowany” [10]; Comfy pokazuje I2V z klatkami jako działające [9] → z klatkami spodziewaj się słabszej wierności (niepotwierdzone u nas).
- Słabszy w trudnym ruchu, drobnym detalu i części dźwięku [9][10][32]. Prompty: prostszy ruch, jedno główne zdarzenie, mniej cięć. Na Sparku zwykle wolniejszy od H3 w trybie szybkim [L3] — do porównań.

## Sprawdź przed wysłaniem
1. Tryb wg plików: nic / pierwsza / ostatnia / obie / inspiracje / klatki kluczowe → właściwa linia instrukcji albo format 6-sekcyjny.
2. Linia instrukcji dosłownie, potem pusta linia; `S.SS` = długość klipu, `N` = numer ostatniego ujęcia.
3. Całość po angielsku; po polsku tylko w `<d>[Polish] …</d>` i w cudzysłowie napisu.
4. Styl/medium na początku `[Shot 1]` (Ref2VA: przed `[Shot 1]`).
5. `[Shot 1]` bez czasu; kolejne `At MM:SS.mmm` rosnąco i < długości; cięcie = nowa informacja.
6. Każdy mówiący ma stały `(Sx)` i opis głosu; kwestie kończą się kropką; po kwestii usta zamknięte / „silently”.
7. Oba pola dźwięku wypełnione (`N/A` świadomie); brak dialogów w `overall_soundscape`.
8. Zero negacji typu „no …”, zero wag i JSON.
9. Znaczniki referencji zgodne z numeracją plików w Studiu; każdy ma rolę; brak `<Picture n>` dla klatek kluczowych; brak „dźwięku z `<Video n>`”.
10. Długość ≥ 5 s i pasująca do ilości dialogu; twarze nie w planie ogólnym.

## Źródła
[1] MiniMax — Video Prompt Writing Guide (T2VA/I2VA/FL2VA/L2VA) — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md — oficjalne
[2] MiniMax — Full-Reference Mode (Ref2VA) Guide — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md — oficjalne
[3] MiniMax H3 — karta modelu (README) — https://huggingface.co/MiniMaxAI/MiniMax-H3 — oficjalne
[4] MiniMax H3 — skills (h3-prompt-writing, handdrawn-live-video-generator, papercraft-stop-motion-explainer, paper-collage-explainer-generator) — https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills — oficjalne
[5] MiniMax — blog „MiniMax H3” — https://www.minimax.io/blog/minimax-h3 — oficjalne
[6] ComfyUI — MiniMax H3 Prompt Guide — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide — oficjalne (Comfy)
[7] ComfyUI — MiniMax H3 native workflows — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native — oficjalne (Comfy)
[8] ComfyUI — MiniMax H3 multiframe — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe — oficjalne (Comfy)
[9] ComfyUI — FastVideo FastH3 — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo — oficjalne (Comfy)
[10] FastVideo — FastH3-8-Step-V2 (karta HF) — https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2 — oficjalne
[11] ComfyUI — kod węzłów H3 (nodes_minimax_h3.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py — oficjalne (kod)
[12] ComfyUI — kod enkodera H3 (text_encoders/minimax.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py — oficjalne (kod)
[13] Comfy-Org — szablony workflow H3 (t2v, r2v, multiframe_reference) — https://github.com/Comfy-Org/workflow_templates/tree/main/templates — oficjalne (Comfy)
[14] HF #47 „The actual correct system prompt for IT2V” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/47 — społeczność
[15] HF #32 prompty po chińsku (odpowiedź członka org. MiniMaxAI + użytkownicy) — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/32 — oficjalne/społeczność
[16] HF #74 „Anime style videos have half the FPS” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/74 — społeczność
[17] HF #76 „Weird gibberish / clipped voice at the very start” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/76 — społeczność
[18] HF #83 „Very bad prompt adherence” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/83 — społeczność
[19] HF #84 „Getting different Accents” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/84 — społeczność
[20] HF #65 „Prompt adherence varies depending on the resolution” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/65 — społeczność
[21] HF #81 „Question about prompting on static elements” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/81 — społeczność
[22] HF #96 mruganie — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/96 — społeczność
[23] HF #106 bełkot postaci — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/106 — społeczność
[24] HF #82 „Ref2VA environmental audio feels too quiet” — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/82 — społeczność
[25] HF #71 pytania o przewodnik Ref2VA — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/71 — społeczność
[26] Comfy-Org HF #30 „Why MiniMax H3 Ruins Faces on Wide Shots?” — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30 — społeczność
[27] Comfy-Org HF #44 „problem with off-screen voiceover” — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/44 — społeczność
[28] Comfy-Org HF #67 „FL2VA / I2VA: mid-clip blackout” — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/67 — społeczność
[29] Comfy-Org HF #55 „Ref2VA: red/blush patches” — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/55 — społeczność
[30] ComfyUI issue #15454 „voice/accent conditioning can leak between subjects” — https://github.com/Comfy-Org/ComfyUI/issues/15454 — społeczność
[31] Aireiter — „MiniMax H3 Prompt Review: What Works, What Breaks” — https://aireiter.com/blog/minimax-h3-prompt-review — społeczność
[32] Kombitz — „FastH3 V2: 8-Step MiniMax H3 in ComfyUI” — https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/ — społeczność
[33] fal.ai — „MiniMax H3 Prompting Guide + 44 Video Examples” (API) — https://fal.ai/learn/devs/minimax-h3-prompting-guide — społeczność/vendor
[34] Atlas Cloud — „I Studied 45 Official Prompts” (API) — https://www.atlascloud.ai/blog/tips/minimax-h3-prompt-guide — społeczność
[35] Seedance.tv — „MiniMax H3 Gibberish Fix” — https://www.seedance.tv/blog/minimax-h3-gibberish-fix — społeczność
[L1] Studio: gui/modele/wideo/minimax-h3*.yaml, fasth3-v2.yaml — nasza konfiguracja
[L2] Studio: gui/workflows/wideo/h3_wideo, h3_referencje_lista, h3_klatki-kluczowe, fasth3_wideo (.api.json) — nasza konfiguracja
[L3] notatki własne (niepublikowane) (pomiary na Sparku) — nasza konfiguracja
