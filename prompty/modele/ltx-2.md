<!-- Karta modelu dla promptmakera. modele: ltx-2-3, ltx-2-5 -->
# LTX-2.3 i LTX-2.5 (Lightricks): wideo z dźwiękiem

## Czym jest i do czego się nadaje (w tym: czego NIE robi dobrze)

- Jeden model (22B, DiT) generuje **obraz i dźwięk naraz**, w jednym przebiegu. Dźwięk (ambient, efekty, mowa, śpiew, muzyka) wynika z promptu, więc prompt opisuje też to, co słychać [12][13][14] (oficjalne).
- **LTX-2.3** (marzec 2026). Enkoder tekstu Gemma 3 12B [2][12][5]. Jedna ciągła scena na generację. Ma wariant **obraz + nagranie → wideo**: obraz rusza się do podanego dźwięku, np. mówi albo śpiewa [1].
- **LTX-2.5** (sierpień 2026). Własny, dotrenowany enkoder Gemma 4 12B, który lepiej utrzymuje złożone prompty (kilka postaci, ruch kamery, światło) [11][13][18] (oficjalne). Nowość to **natywne wieloujęcie**: 2–4 ujęcia połączone cięciami w jednej generacji [3][6] (oficjalne). W Studiu nie ma tu wejścia dźwięku [1].
- Najlepiej wychodzą: kinowe kadry z jednym głównym podmiotem, wyraźny język kamery, spójne światło, dobrze opisany dźwięk, atmosfera (mgła, deszcz, odbicia), drobne gesty i mimika [3][4] (oficjalne). Według 2.3 Prompt Guide dobrze wychodzi też stylizacja: „painterly, noir, analog film, pixelated animation” [4] (oficjalne).
- **Słabo wychodzi:**
  - napisy i logotypy (pisownia nie jest pewna, także w 2.5) [3][4];
  - chaotyczna fizyka (taniec jest OK) [4];
  - zatłoczone kadry z wieloma postaciami lub akcjami, mieszana logika światła [3][4] (oficjalne);
  - przypisywanie kwestii postaciom przy kilku mówiących [14] (oficjalne);
  - wymowa w językach słabo reprezentowanych w danych [14] (oficjalne);
  - dryf w scenach dłuższych niż ok. 20 s [14] (oficjalne);
  - trwałość obiektów: rzeczy się pojawiają i znikają [34] (społeczność).
- **Ograniczenie dźwięku (2.3):** gdy w dźwięku nie ma mowy, jakość dźwięku bywa niższa [12] (oficjalne).

## Co uczestnik ustawia w Studiu (pola, wejścia, parametry z naszego YAML — i jak wpływają na prompt)

Jedna pozycja na model. Wariant Studio wybiera samo, na podstawie podanych wejść [1] (nasza konfiguracja):

| Wejścia | LTX-2.3 | LTX-2.5 |
|---|---|---|
| nic | tekst → wideo | tekst → wideo |
| `klatka_start` | obraz → wideo | obraz → wideo |
| `klatka_start` + `klatka_koniec` | pierwsza i ostatnia klatka | pierwsza i ostatnia klatka |
| `klatka_start` + `dzwiek` | obraz + nagranie → wideo | — (brak) |

Parametry [1][2] (nasza konfiguracja):

- **prompt.** Jedno pole. **Nie ma pola negatywnego.** Workflowy mają wpisany na stałe negatyw („pc game, … cartoon, childish, ugly”), ale wszystkie samplery działają przy **CFG = 1** (model destylowany), więc negatyw nie działa. Tak samo jest w oficjalnych zaleceniach: „distilled… CFG=1” [11][12]. Negatyw zaczyna działać dopiero przy CFG > 1 [27] (społeczność). Wszystko, czego model ma unikać, trzeba więc zapisać w samym prompcie, jako opis tego, co ma być.
- **proporcje:** 16:9 (domyślnie), 21:9, 4:3, 1:1, 3:4, 9:16; ok. 0,9 MP, wymiary podzielne przez 32.
  - W LTX-2.3 (obraz, obraz + nagranie) i w obu wariantach „klatki” obrazy są **przycinane do środka** do wybranych proporcji. Proporcje mają więc pasować do obrazu, inaczej zniknie część kadru.
  - LTX-2.5 obraz → wideo nie przycina obrazu przed modelem. Co się dzieje przy niezgodnych proporcjach, nie wiadomo; najlepiej, żeby się zgadzały.
- **długość:** 1–20 s (domyślnie 10). **fps:** 24 albo 25.
  - Długie ujęcie wymaga dłuższego, bogatszego opisu: „A short prompt for a long video often results in the model rushing through the described action” [4] (oficjalne).
  - Reguła kciuka: **jedno główne działanie na 2–3 s** [5] (oficjalne, blog).
  - Długi klip z krótkim promptem to też ryzyko „plansz końcowych” i logotypów w ostatnich klatkach. Błąd naprawił upscaler v1.1, którego używamy [28] (społeczność + odpowiedź Lightricks).
  - W wariancie z nagraniem długość przycina nagranie [1].
- **rozbudowa** („model sam rozbudowuje prompt”; ustawienie zaawansowane, domyślnie wyłączone; nie ma go w wariancie LTX-2.3 „klatki”). Wbudowany LLM przepisuje prompt **na angielski akapit w stylu napisów treningowych** [7][8][9][10]:
  - 2.3: Gemma 3 12B (ten sam model co enkoder);
  - 2.5: Gemma 4 E2B (ok. 1–2 min dłużej) [13].
- **seed.** Przy tym samym seedzie zmieniaj jedną rzecz naraz [5].
- **Dwa etapy** (połowa rozdzielczości, potem upscaler ×2) mają tylko warianty tekst → wideo, obraz → wideo i obraz + nagranie [2].
  - Warianty „klatki” robią jeden przebieg od razu w pełnej rozdzielczości, bez upscalera [2] (nasza konfiguracja; zgodne z [13]). Na prompt to nie wpływa.
- **Obraz startowy** przechodzi przez `LTXVPreprocess` (lekka kompresja, ma upodobnić kadr do klatki wideo) [2] (nasza konfiguracja).

## Format promptu

- **Język: angielski.**
  - Napisy treningowe i oba enhancery piszą po angielsku. Enhancer 2.5 ma wprost polecenie: „If the user wrote in another language, produce the English caption” [8][9] (oficjalne, kod).
  - Enkoder jest wielojęzyczny [14], ale jakości opisu po polsku nikt nie zbadał (**nie ustalono**). Opis piszemy po angielsku.
- **Kwestie mówione** zapisz w cudzysłowie, **w języku, w którym mają paść** (polski po polsku). Nazwij język i akcent [3][4][8] (oficjalne).
  - Jakość polskiej mowy: **nie ustalono**; nie znaleziono żadnych testów.
  - Akcent i wymowa w innych językach bywają niepewne [29] (społeczność).
  - Model nie tłumaczy kwestii [3] (oficjalne, dotyczy Dub-It).
- **Struktura:** **jeden płynny akapit, czas teraźniejszy**, chronologicznie od początku do końca ujęcia [3][4][6] (oficjalne).
  - Bez list, punktorów, nagłówków i etykiet typu „Audio:”/„Visual:”: enhancer 2.5 ma je zakazane [8] (oficjalne, kod).
  - Wyjątek: przy dialogach, wielu beatach albo precyzyjnym timingu oficjalny przewodnik dopuszcza **styl scenariuszowy**: nagłówek sceny, „Reporter: "…"” [3][4] (oficjalne).
  - Nasze karty nie używają tagów ani etykiet sekcji z `media/wideo.md`: tę samą treść zapisujemy prozą, w tej samej kolejności.
- **Sześć elementów (oba modele)** [3][4][6] (oficjalne):
  1. Ujęcie: plan, kategoria, terminologia filmowa.
  2. Scena: światło, paleta, faktury, atmosfera.
  3. Akcja jako sekwencja, każde zdanie z czasownikiem ruchu („walks, turns, exhales, reaches”).
  4. Postaci: wiek, włosy, strój, cechy szczególne; emocja wyłącznie przez objawy fizyczne.
  5. Kamera: jak i **kiedy** się rusza, opisana względem podmiotu, plus to, jak podmiot wygląda **po** ruchu.
  6. Dźwięk: ambient, efekty, muzyka, mowa, śpiew.
- **Kolejność:**
  - LTX-2.3: blog o trzymaniu się promptu radzi zaczynać od **głównej akcji w jednym zdaniu**, potem szczegóły ruchu, wygląd, otoczenie, na końcu kamera i światło [5] (oficjalne, blog).
  - Kierunek stylu najlepiej podać **na samym początku** [7][15] (oficjalne). Enhancer 2.3 zaczyna od „Style: <styl>, …” [7][10]; to jedyny „znacznik”, jaki widać w kodzie.
  - LTX-2.5: napisy treningowe zaczynają się od akcji albo detalu wizualnego. W prozę wplecione są trzy rzeczy: **plan** (jeden z: extreme wide / wide / medium / medium close-up / close-up / extreme close-up), **ruch kamery** (zawsze; brak ruchu = „the camera remains static”) i **punkt widzenia** (front-facing / side view / over-the-shoulder / top-down / low-angle / high-angle) [8] (oficjalne, kod enhancera).
- **Długość:**
  - 2.5: oficjalnie „4–8 descriptive sentences” na proste ujęcie, więcej przy scenach złożonych, „provided every sentence adds concrete visual or audio detail” [3][6]. Enhancer 2.5 celuje w **150–220 słów** [8].
  - 2.3: źródła się różnią. Prompt Guide mówi „długie, szczegółowe prompty wygrywają” [4], a blog o trzymaniu się promptu każe trzymać się w 200 słowach [5] (oba oficjalne).
  - Praktycznie: **ok. 80–220 słów**, proporcjonalnie do długości klipu.
- **Bez wag, bez JSON, bez „(word:1.2)”.** Tokenizery Gemma 3 i Gemma 4 w ComfyUI mają `disable_weights=True` — nawiasy i liczby trafiają do modelu jako zwykły tekst (kod ComfyUI: `comfy/text_encoders/lt.py`, `gemma4.py`). Liczb i stopni („pans at 2 degrees per second”) też nie: to przykład błędu „over-constrained” [4] (oficjalne).
- **Negacje w treści:** oficjalny przykład używa ich w opisie dźwięku („a low male vocal drone…, no instruments, no music”) [3] (oficjalne). Blog o animacji 2D radzi „no gradients, no shadows” dla płaskiej grafiki [15] (oficjalne, blog). Używaj oszczędnie: najpierw opis tego, co jest.

## Szkielet promptu

Tekst → wideo, jedno ujęcie (oba modele):
```
[styl/medium/faktura — pierwsza fraza]. [plan] of [podmiot: wiek, wygląd, strój — tylko to, co widać], [punkt widzenia], in [miejsce: materiały, faktury]. [światło: źródło, kierunek, barwa; jedna logika] and [paleta]. [akcja 1, czas teraźniejszy], as [ruch kamery względem podmiotu, tempo]. Then [akcja 2 / zmiana], [jak podmiot wygląda po ruchu kamery]. [dźwięk tła — konkretne źródła], [efekt przypięty do akcji]; [kto] says in [język, barwa, tempo, głośność], "[kwestia]". [muzyka albo jej brak; pogłos/przestrzeń].
```

Obraz → wideo:
```
[2.5: jedno zdanie zakotwiczenia zgodne z obrazem: plan, podmiot, miejsce]. [co zaczyna się ruszać i jak — chronologicznie: początkowo…, chwilę później…], [ruch kamery albo „the camera remains static”]. [co się zmienia w świetle/materii]. [dźwięk: źródła zsynchronizowane z ruchem; mowa w cudzysłowie].
```

Pierwsza i ostatnia klatka:
```
[jak przechodzimy od stanu z pierwszej klatki do stanu z ostatniej: kolejne fazy zmiany], [ruch kamery łączący oba kadry], [światło/czas]. [dźwięk w trakcie przejścia].
```

Obraz + nagranie (tylko 2.3):
```
[styl], [plan, punkt widzenia]. [podmiot] [jak wykonuje dźwięk z nagrania: usta, oddech, gest, mimika — w rytmie nagrania], [drobne ruchy ciała/tła], [kamera].
```

Wieloujęcie (tylko 2.5, tekst → wideo):
```
[ujęcie 1: plan, kadr, podmiot z identyfikatorem, akcja, dźwięk]. A hard cut transitions to [ujęcie 2: nowy plan, kąt, kto w kadrze — ten sam identyfikator], [akcja]; [dźwięk: co trwa / co się zmienia przez cięcie]. [ewent. ujęcie 3 analogicznie].
```

## Co działa

- **Ruch kamery ze znanego słownictwa:** „follows, tracks, pans across, circles around, tilts upward, pushes in / pulls back, overhead view, handheld movement, over-the-shoulder, wide establishing shot, static frame” [3][4]. Do tego „slow dolly in”, „handheld tracking” [4] (oficjalne).
- **Emocja przez ciało:** zamiast „sad” pisz „his eyebrows angle downward and his lips are pressed together” [8]. Zamiast „tense confrontation” pisz „two men stand three feet apart, both leaning forward with clenched fists” [5] (oficjalne).
- **Dosłownie, nie metaforycznie:** opisuj to, co kamera fizycznie widzi [5] (oficjalne, blog). Metaforę z wiersza trzeba przełożyć na materię, ruch, światło i dźwięk.
- **Spójniki czasu:** „Initially…, A moment later…, Simultaneously…” [3][8] oraz „as / then / while” [7][35] (oficjalne + społeczność).
- **Dialog pocięty na frazy z didaskaliami** (2.3): „…says in a slow voice, "…" He pauses and looks to the side, then continues, "…"”. Pauzy wpisane w tekst („a beat of silence”, „she pauses”) model faktycznie wykonuje [3][4] (oficjalne).
- **Dźwięk przypięty do źródła w kadrze:**
  - Najpierw tło przestrzeni, potem efekty przypięte do akcji, która je wywołuje [30]; konkret zamiast ogólnika („soft footsteps on tile”, nie „ambient sound”) [7] (oficjalne).
  - Sygnał, który działa, to ruchomy obiekt z przypiętym dźwiękiem; przymiotniki nastroju nie działają [33] (społeczność).
- **Dźwięk opisywany na bieżąco obok akcji, nie dopisany na końcu** [10] (oficjalne, prompt systemowy I2V 2.3).
- **Jakość dźwięku:** w 2.3 opis akustyki, barwy głosu i ambientu ma większy wpływ niż wcześniej [4] (oficjalne). Pomaga dopisek typu „The audio is crisp with faint room tone” [4]. Ciszę wypełnia ton pomieszczenia („quiet room tone”) [30] (społeczność).
- **Słownictwo branżowe przy wyraźnej hierarchii:** zacznij od głównej dziedziny (np. animacja), drugą dodaj jako kwalifikator materiału, trzecią tylko jako światło lub gradację. Mieszanie na równych prawach sprawia, że model „uśrednia” [16] (oficjalne, blog).
- **Ujęcie statyczne:** napisz „A static shot of …” jako **pierwszą frazę** [19] (społeczność; skuteczność w 2.5 niepewna, patrz pułapki).

## Biasy i pułapki

- **Domyślny fotorealizm.** „AI video generation defaults to photorealism” [15] (oficjalne). Dłuższy klip w stylu 2D dryfuje w stronę realizmu [15].
- **Enhancer („rozbudowa”) przesuwa estetykę i treść:**
  - Enhancer 2.3: przy braku stylu „Default to cinematic-realistic” [7]. Do tego „Restrained language”: kolory zwykłe, bez intensyfikatorów [7].
  - Enhancer 2.5 ma wpisane „cinematic, film-grade color…, beautiful natural lighting, crisp fine detail” i zachęca do ruchu kamery („Camera movement is expected and good”) [8][9] (oficjalne, kod). To kłóci się z zasadą promptmakera „nie dokładamy ładności”.
  - Społeczność: przy włączonym enhancerze 2.5 bywają wyniki zupełnie niezwiązane z promptem [17]. Dochodzą niechciane cechy demograficzne postaci; Gemma 3 trzymała się promptu lepiej [18] (społeczność).
  - Wniosek: **domyślnie „rozbudowa” wyłączona**. Oficjalnie enhancer pomaga najmniej, gdy prompt już ma właściwą strukturę [3].
  - Nasze workflowy mają dwie luki [2] (nasza konfiguracja). W LTX-2.3 obraz + nagranie enhancer **nie dostaje obrazu**, więc pisze jak do tekst → wideo i może zmyślić wygląd sprzeczny z obrazem. W LTX-2.5 „klatki” widzi **tylko pierwszą klatkę** i ma zakaz cięć.
- **Najazd kamery.** W 2.5 (i 2.3) klipy często same „wjeżdżają” w twarz. Prośby o statyczną kamerę słabo pomagają: wg jednego z użytkowników ok. 2 na 50 prób bez zoomu. Inny pisze, że 2.5 radzi sobie lepiej niż 2.3. Bliskie plany dominują [19] (społeczność). LoRA kamery nie ma w Studiu.
- **Bez opisu ruchu kamery model robi własny dryf** albo losowe zmiany kąta [5] (oficjalne, blog). Kamerę określaj zawsze, także jako „static”.
- **Mowa bez pytania.** 2.3 czasem „czyta prompt na głos” albo mówi bełkot, gdy mowy nie zamówiono [24] (społeczność). Gdy ma być cisza głosowa, opisz dokładnie, co słychać: źródła, „no one speaks” (**niepotwierdzone**, czy pomaga).
- **Muzyka sama się dokleja.** Bez wskazania model może dograć własną ścieżkę [30][33]. Zalecenie hosta to „no music” [30], ale w 2.3 użytkownicy nie umieli jej wyłączyć promptem [26] (społeczność). Jeśli muzyka ma być dodana potem: wpisz „no music” i licz się z koniecznością odcięcia ścieżki w montażu.
- **Głośność i odległość głosu** („whisper”, „from a distance”) w 2.3 słabo sterowalne wg użytkowników [25] (społeczność). Oficjalna lista słów podaje jednak „Whisper · Mutter · Shout · Scream” [3]. Wynik nie jest pewny.
- **Napisy w kadrze.** 2.3 potrafi sam dodać napisy, często z błędami [27]. Cudzysłów oznacza mowę, nie napis [30] (społeczność). Oficjalnie: tekst w kadrze krótki i duży, pisownia niegwarantowana, ważne napisy i logotypy dodaj w montażu [3] (oficjalne). Dla nas: tekstu w kadrze raczej nie zamawiaj.
- **Sprzeczności** („a still, peaceful lake with dramatic waves crashing”; „running quickly… in slow motion”) gubią model [4][5] (oficjalne). Zwolnienie opisz skutkiem: „suspended in slow motion, each step drawn out” [5].
- **Przeładowanie:** pięć akcji w jednym klipie kończy się kompresją albo pominięciem środkowych [5] (oficjalne, blog). Krótka forma: jedno, najwyżej dwa zdarzenia.
- **I2V w 2.5: tożsamość postaci z obrazu bywa zmieniona.** Użytkownicy podają, że 2.3 trzymał twarz lepiej [20] (społeczność).
- **I2V w 2.3:** opis niezgodny z obrazem „may cause scene cuts” [10] (oficjalne, prompt systemowy).
- **Prompt przeniesiony z innego modelu** (tagi, listy ujęć z Kling/Seedance/H3) działa słabiej. Przepisz go na akapit LTX [3] (oficjalne).

## Poza fotorealizmem

- **Zasada główna (oficjalne, blog o 2D [15]):**
  - deklaracja stylu jako **pierwsza fraza** promptu, powtórzona w treści;
  - przy nawrocie realizmu: „not photorealistic, no realistic textures, 2D only”;
  - najsilniejsza kotwica to **obraz startowy w docelowym stylu** (zrobiony w obszarze Obraz albo narysowany), bo prompt opisuje wtedy już tylko ruch;
  - **krótkie klipy (2–4 s)** chronią przed dryfem do realizmu.
- **Słownik z oficjalnego przewodnika** [3][4]:
  - Animation: stop-motion, 2D / 3D animation, claymation, hand-drawn;
  - Stylized: comic book, 8-bit pixel, surreal, minimalist, painterly, illustrated;
  - Cinematic: film noir, experimental film, arthouse, documentary;
  - Film Characteristics: **film grain, lens flares, pixelated edges, jittery stop-motion**.
- **Rysunek / animacja 2D** [15][16] (oficjalne, blogi):
  - „hand-drawn linework”, „ink-and-paint style”, „cel-shaded flat color”, „limited animation with held frames”;
  - płasko: „flat vector illustration style, solid color fills with clean outlines, no gradients, no shadows”;
  - akwarela / książka obrazkowa: „watercolor illustration style, soft painted textures, muted pastel palette, gentle hand-drawn lines”;
  - słowa o tempie pomagają w stylu: „gentle, calming motion”; „exaggerated” zwalnia z realistycznych proporcji;
  - **nie mieszaj słownika 2D i 3D** w jednym ujęciu [16].
- **Taśma, ziarno, archiwum (restauracja)** [16] (oficjalne, blog 2.3):
  - „coarse silver-halide grain, black-and-white 16mm”, „fine grain, Kodachrome-tight”;
  - „telecine flicker, gate weave, edge halation”;
  - nazwy taśm („Ektachrome”, „Portra”, „Fuji Reala”); pilnuj anachronizmów.
  - VHS i wideo analogowe: brak źródła oficjalnego (**niepotwierdzone**).
- **Malarskość, noir, kino analogowe:** wymienione jako mocne strony 2.3 [4] (oficjalne).
- **Kolaż, abstrakcja, czysta faktura bez podmiotu:** brak źródeł (**nie ustalono**).
  - Model jest strojony pod „cinematic, single-subject scenes” [3]. Praktycznie najpewniejsza droga to obraz startowy (kolaż, abstrakcja) plus prompt opisujący wyłącznie ruch materii i kamery. To wniosek z [15], nie test.
- **Enhancer przy stylizacji szkodzi** (domyślny „cinematic-realistic” / „film-grade”) [7][8]. Przy stylizacji „rozbudowa” wyłączona.
- **Wzorce animacji** opisane liczbami klatek („anticipation frame at frame one… snap to release pose at frame six”) pochodzą z bloga [16]. Kłóci się to z ostrzeżeniem przed liczbami [4]; traktuj je jako **niepotwierdzone**.

## Ruch / czas / dźwięk

- **Ruch:** jedna ciągła akcja z wyraźnym początkiem i końcem; jedno główne działanie na 2–3 s [5]. Pauzy i „beat” wpisuj w tekst [3].
- **Kamera:** nazwij ruch, tempo i moment („as she turns, the camera slowly pushes in”). Opisz kadr po ruchu [3][4].
- **I2V (różnica 2.3 / 2.5):**
  - 2.3: opisuj **ruch i zmianę**, nie powtarzaj tego, co już widać na obrazie; „describe the transition from stillness to motion” [4][10] (oficjalne).
  - 2.5: enhancer zaczyna od zdania zgodnego z obrazem (plan, podmiot, miejsce, światło), potem prowadzi akcję chronologicznie, **jednym ujęciem, bez cięć** [9] (oficjalne, kod). Wieloujęcie z klatką startową tylko wtedy, gdy cięcie od obrazu jest zamierzone [3].
  - Oba: w nowym prompcie nie zmieniaj wyglądu podmiotu z obrazu.
  - Technicznie I2V wstawia obraz jako pierwszą klatkę latentną i ją zamraża; poza tym przepływ jest taki sam jak T2V [23] (oficjalne, odpowiedź Lightricks).
- **Pierwsza i ostatnia klatka:**
  - opisz **przejście**: co dzieje się między klatkami, z ruchem kamery i dźwiękiem [13] (oficjalne);
  - obie klatki o tych samych proporcjach [13]; najlepiej, żeby ostatnia była edycją pierwszej i zmiany następowały po kolei, nie wszystkie naraz [33] (społeczność);
  - siła obu klatek w naszych workflowach to 0,7, więc trzymają kadr „miękko” [2] (nasza konfiguracja).
- **Wieloujęcie (tylko 2.5)** [3][6][32]:
  - 2–4 ujęcia [3] (oficjalne); przy 10 s raczej najwyżej 3 [32] (host API, **niepotwierdzone** oficjalnie);
  - każde cięcie nazwane prozą („A hard cut transitions to…”, „The view cuts to a close-up of…”, „A match cut connects…”, „The image dissolves into…”);
  - po cięciu na nowo: plan, kąt, kto w kadrze, światło;
  - **ten sam identyfikator** postaci lub przedmiotu (strój, kolor);
  - przy każdym cięciu napisz, co z dźwiękiem: trwa, cichnie czy się zmienia;
  - każde ujęcie ma zadanie (ogólny → detal → reakcja).
  - Bez nazwanego cięcia model zrobi jedno ujęcie z ruchem kamery [32] (społeczność).
  - Lip-sync i intymna scena: lepiej jedno ujęcie [3].
- **Dźwięk generowany (tekst/obraz → wideo):**
  - warstwy: głos z przodu, efekty przy akcjach, tło pod spodem [30];
  - w każdej kwestii: kto mówi, język, akcent, barwa, tempo; jedna osoba na kwestię [30] (społeczność); kwestia krótsza niż czas klipu;
  - przy śpiewie: „sings”; nazwij gatunek, nastrój i instrumenty muzyki albo jej brak [3][8];
  - akcent wyrazowy wielkimi literami nie działa; opisz, gdzie pauza i które słowo mocniej [29] (społeczność).
- **Obraz + nagranie (tylko LTX-2.3):**
  - Nasz workflow **zamraża dźwięk** (maska szumu 0) [2][22], więc model go nie zmienia, tylko animuje obraz.
  - W prompcie **nie opisuj innej ścieżki**. Opisz wizualną interpretację nagrania: kto wykonuje, jak (usta, oddech, gest), kamera, tło [4] (oficjalne).
  - Wg hosta API dla 2.5 Pro: „describes the look and the performance, not the words” [31]. Twarz ostra, dobrze oświetlona, frontalnie, z widocznymi ustami; kadr taki jak końcowy, bo model nie przekadrowuje [31] (społeczność/host).
  - Śpiew: wyraźny wokal prowadzący; wokale z dużym pogłosem bywają brane za chórki i postać ich nie śpiewa; dużo zależy od seeda [22] (społeczność, test na 2.5).
  - Zewnętrzne audio i śpiew wychodzą lepiej w 2.3 niż w 2.5 [21] (społeczność). W Studiu jest tylko 2.3, więc to się zgadza.
  - **Polska mowa pewniej:** nagranie głosu w obszarze Mowa (np. OmniVoice), potem ten wariant. To wniosek z [29] i [14], nie test.

## Sprawdź przed wysłaniem

- [ ] Angielski akapit, czas teraźniejszy, bez list, nagłówków i etykiet („Audio:”) — chyba że to celowy styl scenariuszowy.
- [ ] Styl / medium / faktura w **pierwszej frazie**, dosłownie z biblii; bez „cinematic, beautiful, 8k”, jeśli biblia tego nie mówi.
- [ ] Plan, punkt widzenia i ruch kamery nazwane (albo „the camera remains static” / „A static shot of…” na początku).
- [ ] Akcja chronologiczna; ok. 1 działanie na 2–3 s ustawionej długości; pauzy wpisane.
- [ ] Emocje jako objawy fizyczne; metafory przełożone na materię, światło, ruch, dźwięk.
- [ ] Dźwięk opisany konkretnie (źródła w kadrze, przestrzeń); muzyka albo jej brak powiedziane wprost; mowa w cudzysłowie, z językiem i sposobem mówienia, jedna osoba na kwestię.
- [ ] Brak zamówionego tekstu w kadrze; brak sprzeczności (spokój kontra fale, szybko kontra zwolnienie).
- [ ] I2V: 2.3 tylko ruch i zmiana; 2.5 zdanie zakotwiczenia zgodne z obrazem, potem ruch; proporcje w Studiu = proporcje obrazu.
- [ ] Klatki: opisane przejście między stanami; obie klatki w tych samych proporcjach.
- [ ] Obraz + nagranie (2.3): opis wykonania i wizualnej interpretacji, bez nowej ścieżki dźwiękowej.
- [ ] Wieloujęcie (2.5): 2–4 cięcia nazwane prozą, ponowne ustalenie kadru, te same identyfikatory, ciągłość dźwięku.
- [ ] Zostaw „rozbudowę” wyłączoną (zwłaszcza przy stylizacji); jeśli uczestnik ją włączy, niech sprawdzi podgląd przepisanego promptu.
- [ ] Brak negatywu w Studiu (CFG 1): czego nie chcemy, tego nie nazywamy; opisujemy to, co ma być.

## Źródła

[1] Studio FSO — konfiguracja modeli: `modele/wideo/ltx-2-3*.yaml`, `ltx-2-5*.yaml` — nasza konfiguracja
[2] Studio FSO — workflowy ComfyUI: `workflows/wideo/ltx_23_*.api.json`, `ltx_25_*.api.json` (CFG 1, negatyw stały, Gemma 3 12B fp8 / Gemma 4 12B + E2B, upscaler 2.3 v1.1, maska audio 0, przycinanie obrazów) — nasza konfiguracja
[3] LTX Docs — Prompting Guide (LTX-2.5; multi-shot, enhancer, przykłady, słownik) — https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide — oficjalne
[4] LTX Blog — LTX-2.3 Prompt Guide (10.03.2026) — https://ltx.io/blog/ltx-2-3-prompt-guide — oficjalne
[5] LTX Blog — How To Improve LTX-2.3 Prompt Adherence (13.05.2026) — https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence — oficjalne (blog)
[6] LTX Blog — LTX-2.5 Prompt Guide (10.08.2026) — https://ltx.io/blog/ltx-2-5-prompt-guide — oficjalne
[7] Lightricks/LTX-2 — gemma3_t2v_system_prompt.txt (enhancer LTX-2.x / Gemma 3) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma3_t2v_system_prompt.txt — oficjalne (kod)
[8] Lightricks/LTX-2 — gemma4_t2v_system_prompt.txt (enhancer LTX-2.5) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_t2v_system_prompt.txt — oficjalne (kod)
[9] Lightricks/LTX-2 — gemma4_i2v_system_prompt.txt (enhancer LTX-2.5, I2V) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_i2v_system_prompt.txt — oficjalne (kod)
[10] ComfyUI — comfy_extras/nodes_textgen.py (węzeł TextGenerateLTX2Prompt; prompt systemowy I2V Gemma 3; wybór T2V/I2V zależnie od obrazu) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_textgen.py — oficjalne (kod ComfyUI)
[11] Hugging Face — Lightricks/LTX-2.5 (karta modelu) — https://huggingface.co/Lightricks/LTX-2.5 — oficjalne
[12] Hugging Face — Lightricks/LTX-2.3 README — https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md — oficjalne
[13] ComfyUI Docs — LTX-2.5 tutorial — https://docs.comfy.org/tutorials/video/ltx/ltx-2-5 — oficjalne (ComfyUI)
[14] LTX-2: Efficient Joint Audio-Visual Foundation Model (arXiv 2601.03233; napisy treningowe, ograniczenia) — https://arxiv.org/html/2601.03233v1 — oficjalne (praca)
[15] LTX Blog — How To Generate 2D Animation With AI Video Models (26.04.2026) — https://ltx.io/blog/how-to-generate-2d-animation-with-ai-video-models — oficjalne (blog)
[16] LTX Blog — Domain-Specific Prompting for LTX-2.3: VFX, Animation & More (04.08.2026) — https://ltx.io/blog/domain-specific-prompting — oficjalne (blog)
[17] HF LTX-2.5 dyskusja #36 — Prompt Enhancement Produces Unrelated Generations — https://huggingface.co/Lightricks/LTX-2.5/discussions/36 — społeczność
[18] HF LTX-2.5 dyskusja #9 — LTX Gemma API Text Encode (odpowiedź LTX: własny Gemma 4; uwagi o enhancerze) — https://huggingface.co/Lightricks/LTX-2.5/discussions/9 — społeczność + oficjalna odpowiedź
[19] HF LTX-2.5 dyskusja #54 — Zooming in — https://huggingface.co/Lightricks/LTX-2.5/discussions/54 — społeczność
[20] HF LTX-2.5 dyskusja #30 — The character consistency in i2v — https://huggingface.co/Lightricks/LTX-2.5/discussions/30 — społeczność
[21] HF LTX-2.5 dyskusja #57 — Don't Use LTX 2.5 For Music Videos! Stick To LTX 2.3 — https://huggingface.co/Lightricks/LTX-2.5/discussions/57 — społeczność
[22] HF LTX-2.5 dyskusja #44 — custom audio lipsync (zamrożony latent audio; zależność od materiału i seeda) — https://huggingface.co/Lightricks/LTX-2.5/discussions/44 — społeczność
[23] HF LTX-2.5 dyskusja #48 — Are I2V & T2V workflows actually different? (odpowiedź LTX) — https://huggingface.co/Lightricks/LTX-2.5/discussions/48 — oficjalna odpowiedź
[24] HF LTX-2.3 dyskusja #45 — Model reading the prompt out loud — https://huggingface.co/Lightricks/LTX-2.3/discussions/45 — społeczność
[25] HF LTX-2.3 dyskusja #52 — Why is it impossible to control the volume of speaking characters? — https://huggingface.co/Lightricks/LTX-2.3/discussions/52 — społeczność
[26] HF LTX-2.3 dyskusja #25 — How to kill the music — https://huggingface.co/Lightricks/LTX-2.3/discussions/25 — społeczność
[27] HF LTX-2.3 dyskusja #5 — Subtitles and Removal (negatyw wymaga CFG > 1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/5 — społeczność
[28] HF LTX-2.3 dyskusja #13 — spatial-upscaler-x2-1.0 causes unwanted text/overlay (naprawione w v1.1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/13 — społeczność + oficjalna odpowiedź
[29] HF Forum — LTX 2.3 problem with dialogs (akcent wyrazowy, wymowa) — https://discuss.huggingface.co/t/ltx-2-3-problem-with-dialogs/176649 — społeczność
[30] Runware — LTX-2.5 Pro: Native audio — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/native-audio — społeczność (host API)
[31] Runware — LTX-2.5 Pro: Audio-driven characters — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/audio-driven — społeczność (host API)
[32] Runware — LTX-2.5 Pro: Multi-shot — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/multi-shot — społeczność (host API)
[33] fal — How To Use LTX-2.5: Prompts & Workflows — https://fal.ai/learn/tools/how-to-use-ltx-2-5 — społeczność (host API)
[34] HF LTX-2.5 dyskusja #38 — object permanence/consistency — https://huggingface.co/Lightricks/LTX-2.5/discussions/38 — społeczność
[35] RunDiffusion — LTX-2 Prompt Guide (spójniki czasu, czas teraźniejszy) — https://www.rundiffusion.com/ltx-2-prompt-guide — społeczność
