<!-- Karta modelu dla promptmakera. modele: ace-step-1-5-xl -->
# ACE-Step 1.5 XL sft (ACE Studio × StepFun, 2026)

## Czym jest i do czego się nadaje
- Model muzyczny z dwoma „mózgami”: **planista LM** (w Studiu Qwen 4B, `qwen_4b_ace15`) zamienia opis + tekst na kody semantyczne (melodia, aranż, część barwy), a **DiT** (tu wariant **XL sft**, 4B, 50 kroków, CFG 7) robi z nich dźwięk [4] (oficjalne), [2] (nasza konfiguracja).
- Wariant **sft** wg autorów: wolniejszy od turbo, „lepszy w detalu i rozumieniu opisu”, minimalnie mniej czysty [4] (oficjalne). Studio: 30 s utworu w ok. 20 s — najszybszy z trzech modeli muzycznych [3] (nasza konfiguracja).
- Umie: piosenki z wyraźną dykcją, utwory instrumentalne, 50+ języków śpiewu (w tym **polski** — w oficjalnych przykładach są 3 piosenki po polsku) [6][7] (oficjalne). Nasz test: dykcja polska **0,97** na sft (turbo tylko 0,60) [3] (nasza konfiguracja).
- **Czego NIE robi dobrze:**
  - wyniki „jak z automatu” — bardzo zależne od seeda i długości; „zgrubna synteza wokalu bez niuansu”; słabsza wierność stylowi w niektórych gatunkach [11] (oficjalne);
  - sztywny, „siatkowy” rytm, płaska dynamika, mało kontrastu zwrotka/refren, przewidywalne melodie (test XL) [12] (społeczność);
  - **ambient w stylu Eno**, wczesna elektronika „à la Kraftwerk” — praktyk: „porażka”, dryf w stronę generycznej, „tandetnej” muzyki z biblioteki [13] (społeczność);
  - wykluczanie instrumentów („bez gitary”) działa słabo; ok. połowa utworów mało zróżnicowana, część generacji to szum — relacja jednego użytkownika [16] (społeczność);
  - **metrum stałe 4/4** w Studiu (patrz niżej) — walc 3/4, 6/8 niedostępne [2] (nasza konfiguracja).

## Co uczestnik ustawia w Studiu
| Pole | Wartości | Dokąd trafia / wpływ na prompt |
|---|---|---|
| **styl (tagi)** | tekst | `tags` = **caption**; idzie do LM i do enkodera tekstu 0,6B **dosłownie** [1][8] (nasza konfiguracja / kod ComfyUI) |
| **słowa** | tekst, domyślnie `[Instrumental]` | `lyrics` — tekst + znaczniki sekcji; „scenariusz w czasie” [1][4] |
| **długość (s)** | 10–240, krok 5, domyślnie 60 | jednocześnie długość latentu i `duration` dla LM (LM generuje 5 kodów/s) [1][8] |
| **tempo (BPM)** (zaaw.) | 40–200, domyślnie **100** | `bpm` — **zawsze wysyłane** [1][2] |
| **tonacja** (zaaw.) | tekst, domyślnie **„E minor”** | `keyscale` — **zawsze wysyłane** [1][2] |
| **język śpiewu** (zaaw.) | en, pl, de, fr, es, it, ja, zh; domyślnie **en** | `language` — trafia tylko do enkodera tekstu piosenki [1][8] |
| **seed** | liczba | wspólny dla LM i DiT [2] |

- Stałe w workflow: metrum `4` (= 4/4), LM: cfg 2.0, temperature 0.85, top_p 0.9; DiT: 50 kroków, CFG 7, euler/simple, shift 3 — jak oficjalny szablon ComfyUI [2][9] (nasza konfiguracja / oficjalne).
- **Negative promptu nie ma** (gałąź negatywna DiT to wyzerowane warunkowanie) [2] (nasza konfiguracja).
- W ComfyUI LM **nie przepisuje opisu** (to robi tylko oficjalne Gradio): BPM, tonacja, metrum i długość wchodzą jako gotowe metadane w bloku `<think>`, opis i tekst idą 1:1 [8] (kod ComfyUI). Co napiszesz — to model dostanie.
- **Konsekwencja:** BPM 100 i E minor polecą zawsze, nawet jeśli uczestnik ich nie ruszy. Promptmaker **zawsze podaje** BPM i tonację zgodne z opisem — sprzeczność („slow ballad” + 160 BPM) myli model [4] (oficjalne).

## Format promptu
- **Opis (caption) po angielsku.** Wszystkie 200 oficjalnych przykładów ma opis po angielsku — także piosenki po polsku/chińsku/koreańsku; język śpiewu nazywa się w opisie słowami, np. „A clear female vocal delivers a melancholic melody in Polish” [7] (oficjalne).
- **Forma:** model przyjmuje słowa-klucze, tagi po przecinkach albo prozę — „format nie wpływa istotnie” [4] (oficjalne). Oficjalne przykłady to **akapit prozy 22–112 słów (mediana ~31)** opisujący przebieg [7] (oficjalne). Etykieta Studia „tagi” nie wymusza tagów — proza jest w porządku.
- **Wymiary opisu** (oficjalna tabela): gatunek, emocja/atmosfera, instrumenty, faktura barwy (warm, crisp, muddy, airy, punchy, raw), epoka, styl produkcji (lo-fi, live recording, bedroom), wokal, rytm, wskazówki budowy (building intro, fade-out ending) [4] (oficjalne).
- **NIE wpisuj BPM, tonacji, metrum do opisu** — od tego są osobne pola [4] (oficjalne).
- **Tonacja — format z przykładów:** `C major`, `E minor`, `F# minor`, `Bb major` (litera + major/minor) [7] (oficjalne). Najstabilniejsze: C, G, D, Am, Em; rzadkie bywają ignorowane [4] (oficjalne).
- **BPM:** 60–180 działa dobrze; skrajne niestabilne. Orientacyjnie: wolne 60–80, średnie 90–120, szybkie 130–180 [4] (oficjalne). Model traktuje BPM jako kotwicę (wyjdzie np. 118 zamiast 120) [4].
- **Tekst (lyrics)** — składnia [4][5][7] (oficjalne):
  - znacznik sekcji w nawiasach kwadratowych, **sam w linii**: `[Intro]`, `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`; dynamiczne: `[Build]`, `[Drop]`, `[Breakdown]`; instrumentalne: `[Instrumental]`, `[Guitar Solo]`, `[Piano Interlude]`, `[Instrumental Break]`; specjalne: `[Fade Out]`, `[Silence]`;
  - **jedno dookreślenie po myślniku**: `[Chorus - anthemic]`, `[Bridge - whispered]`, `[Intro - piano]`. Oficjalnie zalecane jedno; piętrzenie dookreśleń (przykład z przewodnika: pięć naraz) = ryzyko, że model **zaśpiewa treść znacznika** [4];
  - znaczniki wokalu (osobna linia): `[whispered]`, `[falsetto]`, `[raspy vocal]`, `[spoken word]`, `[harmonies]`, `[ad-lib]` [4];
  - **pusta linia między sekcjami** [4][5];
  - `(tekst w nawiasie)` = chórek/echo; **WIELKIE LITERY** = mocniej, krzyk [4][5];
  - przedłużanie samogłosek („Feeeling”) — niestabilne, raczej unikaj [4].
- Wag `(słowo:1.2)`, JSON-a ani negatywu — brak w dokumentacji; nie używaj.
- **Uwaga na wersje:** to **ACE-Step 1.5** (2026). Poradniki do ACE-Step v1 (3.5B, 2025) mają inny pipeline — nie mieszaj [10] (oficjalne).

## Szkielet promptu
Opis (pole „styl”), po angielsku, 1 akapit ~30–80 słów:
```
[gatunek/tradycja albo jej brak] with [główny instrument/źródło] and [2–3 instrumenty drugiego planu]. [Wokal: brak → "Instrumental, no vocals." / jest → płeć, barwa, sposób, "in Polish"]. [Przebieg: jak się zaczyna → co narasta/znika → jak się kończy]. [Faktura i nagranie: np. warm / raw / lo-fi / close-miked / room ambience / tape saturation]. [Nastrój — krótko, na końcu].
```
Pola osobne: `BPM: [liczba zgodna z opisem]`, `tonacja: [X major/minor]`, `długość: [s]`, `język: [pl/en…]`.

Słowa — piosenka:
```
[Intro - (jeden instrument z opisu)]

[Verse 1]
[linia 6–10 sylab]
[linia 6–10 sylab]

[Chorus - (jedno słowo charakteru)]
[linia]
[linia]

[Outro - fade out]
```
Słowa — utwór instrumentalny (wersja z przebiegiem):
```
[Intro - (instrument/faktura)]

[Main Theme - (instrument)]

[Breakdown - (co zostaje)]

[Outro - fade out]
```

## Co działa
- **Konkret zamiast przymiotników**: „sad piano ballad with female breathy vocal” > „a sad song” [4] (oficjalne). Łącz kilka wymiarów (styl + emocja + instrumenty + barwa) [4].
- **Opis = „ogólny portret”, słowa = „scenopis”** — mają opowiadać to samo: instrumenty z opisu ↔ znaczniki solówek; emocja z opisu ↔ znaczniki energii [4] (oficjalne). Przykład konfliktu: opis „violin solo”, w tekście `[Guitar Solo - electric]` → gorszy wynik [4].
- **Sprzeczne style zamień na rozwój w czasie**: „Start with soft strings, middle becomes noisy dynamic rock, end turns to …” zamiast mieszać naraz [4] (oficjalne).
- **Powtórzenie słowa wzmacnia** element w mieszanym stylu [4] (oficjalne).
- **Ilość szczegółu = ilość kontroli**: mniej opisu → więcej niespodzianek, więcej opisu → mniej swobody [4] (oficjalne).
- **Sylaby**: 6–10 na linię; odpowiadające sobie linie zwrotek ±1–2 sylaby — model dopasowuje sylaby do bitów [4][5] (oficjalne).
- **Jedna metafora na piosenkę**, bez piętrzenia przymiotników („neon skies, electric hearts”) — przeciw „AI-owemu” tekstowi [4] (oficjalne). Dotyczy tekstu pisanego od zera; wiersz uczestnika zostaje dosłowny.
- **Znaczniki budowy nawet bez słów** dają mapę energii [5] (oficjalne) — ale w instrumentalu patrz pułapki niżej.
- **Pisz pod rytm**: krótkie frazy, powtórzenia, słowa o wyraźnym akcencie są stabilniejsze niż długie zdania; zmieniaj najpierw opis, potem po jednej sekcji tekstu [15] (społeczność).
- **Generuj kilka seedów** i wybieraj; przy strojeniu jednego parametru trzymaj seed stały [4][5] (oficjalne).
- Oficjalny szablon ComfyUI XL sft: opis jako proza z detalami produkcji („warm and analog-sounding, with subtle tape saturation and a slight room ambience”), znaczniki z opisem instrumentu `[Intro – Rhodes piano and brushed drums]` [9] (oficjalne).

## Biasy i pułapki
- **Domyślne BPM 100 / E minor** — jeśli nie pasują do opisu, model dostaje sprzeczne sygnały [1][4]. Zawsze ustaw.
- **Metrum 4/4 na sztywno** — nie obiecuj walca ani 6/8; „waltz” w opisie przy 4/4 to konflikt (wniosek z [2][4]).
- **Instrumental przecieka wokalizą:** gołe znaczniki `[Verse]`/`[Chorus]` bez słów mogą dać nucenie/wokalizę [14] (społeczność). Bezpieczniej: `[Instrumental]` (oficjalne [4]) albo znaczniki z nazwą instrumentu (`[Main Theme - piano]`), a w opisie wyraźnie „instrumental, no vocals” (na początku lub końcu opisu) [14] (społeczność).
- Społeczność: **słowa sugerujące piosenkę** („pop”, „ballad”, „song”) w instrumentalu ciągną w stronę wokalu; przy orkiestrze dopisz „no choir” [14] (społeczność). Ta sama porada: puste pole słów bywa pewniejsze niż znaczniki — w Studiu pole ma domyślnie `[Instrumental]`; czy puste przechodzi — niesprawdzone.
- Język śpiewu w instrumentalu: Studio nie ma opcji „instrumental/unknown”; język idzie tylko do enkodera tekstu [8] — przy `[Instrumental]` zostaw domyślny (wpływ niepotwierdzony).
- **Za dużo dookreśleń w znaczniku** → zaśpiewane jako tekst [4] (oficjalne).
- **Rzadkie tonacje, skrajne BPM, długie utwory** (>4 min) — mniej stabilne; 30–60 s i 2–4 min najstabilniejsze [4] (oficjalne). Studio i tak kończy na 240 s.
- **Gacha**: zmiana jednego słowa daje zupełnie inny utwór — trudno iterować drobnymi krokami [13] (społeczność), [11] (oficjalne).
- **Nazwiska artystów** autorzy dopuszczają („reminiscent of …”) [4], ale szablon medium Studia każe opisać, co się z nich bierze — trzymaj się szablonu.
- Słaby w niektórych gatunkach (np. chiński rap) [11] (oficjalne); ambient/eksperyment — patrz wyżej [13].

## Poza fotorealizmem (w muzyce: poza konwencją — faktura, taśma, lo-fi, abstrakcja)
- Działające słownictwo produkcji z oficjalnych tabel: **lo-fi, live recording, bedroom pop, studio-polished, high-fidelity**; barwa: **warm, crisp, muddy, airy, punchy, lush, raw** — „wpływają na miks i barwę” [4] (oficjalne).
- **Taśma/analog**: „subtle tape saturation”, „analog-sounding”, „slight room ambience” — z oficjalnego szablonu [9] (oficjalne).
- **Epoka brzmienia** jako skrót: „80s synth-pop”, „vintage soul”, „90s grunge” [4] (oficjalne) — dla archiwalności nazwij epokę i nośnik.
- **Abstrakcja / ambient / drony**: słabo udokumentowane i w praktyce zawodne [13] (społeczność). Jeśli uczestnik chce abstrakcji, rozważ MiniMax Music 3 lub krótkie próby z kilkoma seedami; opisuj konkretne źródła dźwięku (np. „bowed cymbal, sine drones, field recording of wind”), nie „ambient” ogólnie (niepotwierdzone).
- Nietypowe instrumenty („long-tail”) lepiej rozumie większy LM — w Studiu jest największy, 4B [4] (oficjalne), [2] (nasza konfiguracja).

## Ruch / czas / dźwięk
- **Długość** ustawia pole „długość” (LM dostaje dokładnie tyle sekund) [8]. Model „może trochę odbiegać” [4].
- **Ilość tekstu do długości:** oficjalne przykłady 124–240 s mają typowo intro, 2–3 zwrotki, refreny, bridge, outro [7] (oficjalne). Przy 30–60 s daj jedną zwrotkę i refren albo sam tekst krótkiego wiersza (proporcja niepotwierdzona — odsłuchaj, czy nie gna).
- **Przebieg w czasie** zapisuj dwa razy zgodnie: w opisie słowami („builds slowly, ends with a fade-out”) i znacznikami w słowach (`[Build]`, `[Breakdown]`, `[Outro - fade out]`) [4] (oficjalne).
- **Wiersz mówiony na muzyce:** znacznik `[spoken word]` („rap/recytacja”) [4] (oficjalne); w opisie „spoken-word delivery over …”. Skuteczność dla polskiej recytacji — niesprawdzona.
- **Wiersz śpiewany po polsku:** wpisz tekst dosłownie, ustaw język `pl`, w opisie „vocal … in Polish” [7] (oficjalne). Długie wersy wiersza możesz za zgodą uczestnika łamać na krótsze linie w naturalnych pauzach (6–10 sylab) [4] — słów nie zmieniaj.

## Sprawdź przed wysłaniem
- [ ] Opis po angielsku, bez BPM/tonacji/metrum w treści.
- [ ] Pola BPM i tonacja ustawione i **zgodne** z opisem (np. wolny utwór ≠ 100 BPM z domyślnych).
- [ ] Nic nie wymaga metrum innego niż 4/4.
- [ ] Instrumental: w opisie „instrumental, no vocals” (+„no choir” przy orkiestrze); w słowach `[Instrumental]` albo znaczniki z instrumentem — nie gołe `[Verse]`/`[Chorus]`.
- [ ] Piosenka: każdy znacznik w osobnej linii, max jedno dookreślenie, pusta linia między sekcjami; język śpiewu w polu i nazwany w opisie.
- [ ] Instrumenty/energia w znacznikach nie przeczą opisowi.
- [ ] Ilość tekstu pasuje do długości.
- [ ] Bez nazwisk artystów; bez wag i negatywu.
- [ ] Zaproponuj 2–3 seedy zamiast przepisywania promptu po pierwszym wyniku.

## Źródła
[1] Studio — `modele/muzyka/ace-step-1-5-xl.yaml` — modele/muzyka/ace-step-1-5-xl.yaml — nasza konfiguracja
[2] Studio — workflow `workflows/muzyka/ace_step_1_5_xl.api.json` — workflows/muzyka/ace_step_1_5_xl.api.json — nasza konfiguracja
[3] Testy na Sparku (dykcja PL sft 0,97 / turbo 0,60; 30 s w ~20 s) — notatki własne (niepublikowane) — nasza konfiguracja
[4] ACE-Step 1.5 Ultimate Guide (Tutorial) — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md — oficjalne
[5] ACE-Step 1.5 — A Musician's Guide — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md — oficjalne
[6] ACE-Step 1.5 README (50+ języków, 10 s – 10 min) — https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md — oficjalne
[7] Oficjalne przykłady text2music (200 plików; m.in. example_27, example_40, example_41 po polsku) — https://github.com/ace-step/ACE-Step-1.5/tree/main/examples/text2music — oficjalne
[8] ComfyUI — kod enkodera ACE 1.5 (szablony promptu LM, metadane w `<think>`, język) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/ace15.py — oficjalne (implementacja)
[9] Comfy-Org — szablon workflow ACE-Step 1.5 XL sft — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_ace_step1_5_xl_sft.json — oficjalne
[10] ComfyUI Docs — ACE-Step v1.5 (oraz osobna strona v1) — https://docs.comfy.org/tutorials/audio/ace-step/ace-step-v1-5 — oficjalne
[11] ACE-Step 1.5 — strona projektu, sekcja Limitations — https://ace-step.github.io/ace-step-v1.5.github.io/ — oficjalne
[12] GitHub Issue #1114 „Technical Feedback on ACE-Step 1.5 XL” — https://github.com/ace-step/ACE-Step-1.5/issues/1114 — społeczność
[13] „Release and test: Ace-Step 1.5” (test praktyka, ambient/Eno) — https://jurn.link/dazposer/index.php/2026/02/04/release-and-test-ace-step-1-5/ — społeczność
[14] Z.Tools — „Instrumental prompts for ACE-Step: keeping the vocals out” — https://z.tools/blog/ace-step-instrumental-prompts — społeczność
[15] Hacker News — „Ace-Step 1.5 prompt tips” — https://news.ycombinator.com/item?id=46948483 — społeczność
[16] GitHub Discussion #1071 „What were you able to do with XL models…” (anegdotyczne relacje użytkowników) — https://github.com/ace-step/ACE-Step-1.5/discussions/1071 — społeczność
