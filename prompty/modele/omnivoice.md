<!-- Karta modelu dla promptmakera. modele: omnivoice, omnivoice-projekt, omnivoice-klon -->
# OmniVoice (k2-fsa / Xiaomi) — mowa, trzy pozycje w Studiu

## Czym jest i do czego się nadaje
- Model TTS 0,6B, nieautoregresyjny „dyfuzyjny model językowy”, ponad 600 języków (646), wyjście 24 kHz mono [7][11][13] (oficjalne). Polski: ok. 912 h danych treningowych [11] (oficjalne); w naszym teście **najlepszy polski spośród modeli lokalnych** (zgodność słów 0,93 wg Whispera), zdanie w ok. 1 s [3] (nasza konfiguracja).
- Trzy pozycje w Studiu = trzy tryby modelu [1][2] (nasza konfiguracja):
  - **OmniVoice** (`omnivoice`) — sam tekst, **bez opisu głosu**: tryb „auto”, model sam wybiera głos, **przy każdym seedzie inny** [7][22] (oficjalne).
  - **projektowanie głosu** (`omnivoice-projekt`) — głos z **zamkniętej listy cech** (płeć, wiek, wysokość, szept, akcent angielski) [8] (oficjalne), [1] (nasza).
  - **klonowanie głosu** (`omnivoice-klon`) — głos z próbki + jej dokładnej transkrypcji [7] (oficjalne). To **najstabilniejszy** tryb — model był trenowany głównie do klonowania [9][16][35] (oficjalne).
- **Czego NIE robi dobrze:**
  - **emocji i reżyserii opisem** — nie ma pola na „smutno, z napięciem”; autorzy: brak danych z takimi adnotacjami [30] (oficjalne). Emocję niesie tylko próbka (klon), tekst i interpunkcja.
  - **dowolnego opisu głosu prozą** („ciepły, zmęczony, zachrypnięty”) — zna tylko listę cech [8] (oficjalne). Do bogatego opisu: Breeze (tylko EN/ZH) [1] (nasza).
  - **bardzo krótkich wypowiedzi (1–2 s) bez próbki** — niestabilne [9][16] (oficjalne).
  - **akustyki/faktury nagrania** — domyślnie model „odszumia”, generuje czystszy dźwięk niż próbka; pogłos, taśma, telefon z próbki się nie przenoszą [25] (oficjalne).
  - **pewnych pauz** — kropka i przecinek „zwykle” dają pauzę, ale nie zawsze [15] (oficjalne).
  - zdarza mu się: urwać ostatnią głoskę/słowo [18][19], powtórzyć lub opuścić fragment [26], zmienić głos w środku dłuższej wypowiedzi [27], nierówne tempo w ~10% generacji [28] (oficjalne/społeczność) — stąd: kilka seedów i krótsze kawałki.
- Licencja wag: CC-BY-NC — tylko niekomercyjnie [12] (oficjalne).

## Co uczestnik ustawia w Studiu
Studio uruchamia OmniVoice przez wtyczkę ComfyUI **TTS Audio Suite 5.9.2**; kroki 32, guidance 2,0, t_shift 0,1, `denoise` włączone, normalizacja tekstu **wyłączona** — tego uczestnik nie zmienia [2][5] (nasza konfiguracja / kod wtyczki).

| Pozycja | Pole | Wartości | Wpływ na prompt |
|---|---|---|---|
| wszystkie | **tekst do wypowiedzenia** | tekst | jedyne miejsce na treść; składnia — niżej |
| wszystkie | **język** | Polish (domyślnie), English, German, French, Spanish, Italian, Ukrainian, Czech, Russian, Chinese, Japanese | musi być językiem tekstu; z podanym językiem model działa „nieco lepiej” [7] (oficjalne) |
| omnivoice, klon | **tempo mowy** | 0,5–2,0, domyślnie 1,0 | >1 szybciej, <1 wolniej [10] (oficjalne). Wolniej (np. 0,9) to też obejście ucinania końcówek [19] (oficjalne) |
| wszystkie | **seed** | puste = losowy | w trybie auto seed = **inny głos**; zapisz seed, który pasuje [2][22] |
| projekt | **cechy głosu** | z każdej grupy najwyżej jedna (płeć, wiek, wysokość, szept, akcent ang.) | to jest cały „opis głosu”; nie może być pusty (wtyczka zwraca błąd) [1][5] |
| projekt | **tekst próbki** (zaawansowane) | domyślnie „To jest próbka nowego głosu. Mówię spokojnie i wyraźnie.” | min. 10 znaków [5]. Model najpierw czyta go nowym głosem (plik „wzorzec”), **potem klonuje ten wzorzec** i nim mówi tekst [1][5] |
| klon | **próbka głosu** | plik dźwiękowy, wymagany | 3–10 s czystej mowy [7] (oficjalne) |
| klon | **transkrypcja próbki** | tekst, wymagany | dokładnie to, co słychać w próbce; bez niej wtyczka odmawia, Studio: cisza [1][5] |

- **Tryb projektowania w praktyce** [5] (kod wtyczki): cechy działają tylko na wzorzec; Twój tekst powstaje już klonowaniem wzorca. Dlatego: (a) **język tekstu próbki = język wybrany w polu „język”** (ten sam język idzie do obu etapów); (b) **akcent działa tylko, gdy tekst próbki i tekst są po angielsku** [8] (oficjalne) — przy polskim tekście grupa „akcent” nic nie robi; (c) tekst próbki ma dać 3–10 s mowy (1–2 zdania, ok. 50–150 znaków) i kończyć się kropką — to wzorzec do klonu [7][17].
- **Ten sam głos w wielu kwestiach:** projektowanie za każdym razem tworzy głos od nowa (jest swoboda w obrębie cech) [21] (oficjalne). Pewny sposób: pobierz „wzorzec”, wgraj go jako próbkę w **klonowaniu** z transkrypcją = tekst próbki [21] (oficjalne).

## Format promptu
- **Język: język tekstu = pole „język”.** Cechy głosu są po angielsku, ale wybiera je uczestnik przyciskami — promptmaker podaje tylko, **które przyciski** kliknąć [1] (nasza).
- **Opis głosu (tylko projekt):** wyłącznie wartości z listy, po przecinkach, jedna na grupę: `female, elderly, low pitch` [8] (oficjalne). Pusta grupa = model wybiera sam. Wszystko spoza listy jest ignorowane [8]. Przekład z matrycy medium „Mowa”: z punktów „Kto” i „Faktura” zostaje tylko płeć, wiek, wysokość, szept; resztę (barwa, chrypka, charakter, sytuacja) **trzeba powiedzieć uczestnikowi wprost, że ten model jej nie przyjmie** — można ją uzyskać próbką (klon) albo wybrać Breeze (po angielsku) [34][8].
- **Tekst do wypowiedzenia — składnia w NASZYM Studiu** (wtyczka TTS Audio Suite) [4][5][6]:
  - **Dźwięki niewerbalne w nawiasach ostrych:** `<laughter>`, `<sigh>` (oraz `<confirmation-en>`, `<question-en>`, `<question-ah>`, `<question-oh>`, `<question-ei>`, `<question-yi>`, `<surprise-ah>`, `<surprise-oh>`, `<surprise-wa>`, `<surprise-yo>`, `<dissatisfaction-hnn>`). Wtyczka zamienia je na natywne `[laughter]` itd. **Nie pisz `[laughter]` w nawiasach kwadratowych** — w Studiu `[...]` to składnia wtyczki [4] (oficjalne dla wtyczki). (Uwaga: stary poradnik `poradniki/omnivoice.md` podaje `[laughter]` — to błąd dla Studia.)
  - **Pauza o dokładnej długości:** `[pause:1.5s]`, `[pause:500ms]`, `[pause:2]` (= sekundy); aliasy `wait`, `stop` [5][6]. Wtyczka dzieli tekst w tym miejscu i wstawia ciszę — **pauza jest pewna**, w przeciwieństwie do interpunkcji [5][15]. Uwaga: kawałki między pauzami generują się osobno (intonacja „zaczyna się od nowa”) [5].
  - **Zmiana języka fragmentu:** `[en:]` przed fragmentem, np. polski tekst z angielskim cytatem; aliasy typu `[English:]` [6] (oficjalne dla wtyczki). Nie testowane w Studiu (niepotwierdzone). Bez znacznika model sam próbuje obsłużyć tekst mieszany [32] (oficjalne), ale wymowa obcych wtrąceń bywa słabsza.
  - **Wszystko inne w `[...]` znika** — wtyczka traktuje to jako nazwę postaci (np. `[wzdycha]`, `[pauza]`, `[B EY1 S]`) i tego nie czyta [5] (kod wtyczki). Didaskaliów nie wpisuj w tekst. Natywna korekta wymowy z README (`[B EY1 S]`, pinyin) **w Studiu nie działa** [5][7].
- **Interpunkcja = prozodia:** kropka, przecinek, wielokropek, myślnik, pytajnik kształtują frazę [1] (nasza); pauzy z interpunkcji są prawdopodobne, nie pewne [15] (oficjalne). Zawsze kończ tekst kropką/pytajnikiem/wykrzyknikiem — brak końcowej interpunkcji sprzyja ucinaniu końca [18] (oficjalne/społeczność).
- **Liczby, daty, skróty — słownie.** Normalizacja tekstu jest w Studiu wyłączona [5]; autorzy: cyfry mogą być czytane źle, „znormalizuj je do słów” [7][20] (oficjalne). Po polsku z właściwą odmianą („w tysiąc dziewięćset osiemdziesiątym pierwszym”). Skróty („dr”, „np.”, „itd.”) rozwiń (wniosek z braku normalizacji — niepotwierdzone testem).
- **Wagi, JSON, negatyw, tagi emocji** (`[happy]` itp.) — nie istnieją [7][30] (oficjalne).
- **Długość:** brak twardego limitu; powyżej ok. 30 s mowy model sam dzieli tekst na kawałki ok. 15 s [10] (oficjalne). Praktycznie: **jedna strofa / akapit na generację** — łatwiej poprawiać, mniej ryzyka zmiany głosu i pomyłek [27][28] (wniosek ze zgłoszeń).

## Szkielet promptu
Projektowanie (cechy klika uczestnik):
```
cechy: [płeć], [wiek], [wysokość]{, whisper}{, [akcent — tylko tekst angielski]}
tekst próbki: [1–2 zdania w języku tekstu, 3–10 s mowy, w tonie utworu, z kropką na końcu]
tekst: [wers/zdanie, interpunkcja = fraza]{ <sigh>}{ [pause:Ns]} [dalszy tekst, liczby słownie].
```
Klonowanie:
```
próbka: [3–10 s czystej mowy tej osoby, w języku tekstu, cisza na końcu]
transkrypcja: [słowo w słowo, co słychać w próbce, z interpunkcją]
tekst: [jak wyżej]
```
Sam OmniVoice: tylko `tekst` + język + tempo.

## Co działa
- **Klon zamiast opisu**, gdy biblia opisuje konkretną barwę/emocję: nagranie osoby (albo uczestnika) w tym stanie, 3–10 s [7][9]. Emocje: osobne próbki „smutna”, „zła” itd. i generowanie kawałkami, każdy z inną próbką — obejście zaakceptowane przez autorów [30] (oficjalne/społeczność).
- **Próbka z ciszą na końcu**: przycięta tak, by mowa kończyła się przed końcem pliku — autor naprawił tak artefakty krótkich wypowiedzi [17] (oficjalne).
- **Projekt → wzorzec → klon** dla serii kwestii jednym głosem [21] (oficjalne).
- **`[pause:…]` zamiast liczenia na kropkę** tam, gdzie pauza jest częścią formy (cezura, przerzutnia, cisza między wersami) [5][15].
- **`<laughter>` jest najpewniejszy**; pozostałe znaczniki trenowane głównie na chińskich danych — w językach ze spacjami bywały pomijane albo czytane na głos (część naprawiona w kodzie) [14] (oficjalne/społeczność). Dla polskiego: `<laughter>`, `<sigh>`, a resztę traktuj jako eksperyment.
- **Polski pytajnik/wykrzyknik:** jeden użytkownik po polsku: „gotowi do ofiary ?” (spacja przed `?`/`!`) dawało poprawne zakończenie, bez spacji — „zawieszenie” [18] (społeczność, pojedynczy test).
- **Kilka seedów** tego samego tekstu i wybór — losowość jest duża (tempo, pauzy, akcent wyrazu) [28][19] (oficjalne).
- **Zapis potoczny w tekście** (np. „ide”, „sie”, „troche”) dawał wiejską/potoczną wymowę w pracy autora nad głosami „Ludzie” — ale w ElevenLabs, nie w OmniVoice [33] (doświadczenie autora; dla OmniVoice niepotwierdzone).

## Biasy i pułapki
- **Tryb auto = losowy głos** przy każdym seedzie; nie da się go opisać [22]. Jeśli biblia mówi, czyj to głos — kieruj do projektu albo klonu.
- **Akcent z próbki przechodzi na tekst** w innym języku (polska próbka → angielski tekst z polskim akcentem i odwrotnie); nie da się go łatwo usunąć [7][31] (oficjalne). Pułapka łańcucha „głos z Breeze po angielsku → klon OmniVoice po polsku”: polszczyzna dostanie angielski akcent [7] (oficjalne) — chyba że o to chodzi.
- **Konflikt cech:** szept i niska wysokość nie działają z „child” (brak takich danych) [24]; „whisper” nie działa w trybie klonu [23] (oficjalne). Niektóre kombinacje są ignorowane — upraszczaj listę [8].
- **Zła transkrypcja próbki** → w wyniku mogą pojawić się słowa z próbki albo ucięcia [29] (społeczność); wtyczka dopisuje tylko końcową interpunkcję i wycina długie cisze w próbce [10].
- **Ucinanie ostatniej głoski** — wina danych treningowych; łagodzi: kropka na końcu, wolniejsze tempo, spokojniejsza próbka z ciszą [18][19] (oficjalne).
- **Łamanie wierszy nie jest pauzą:** znaki nowej linii stają się spacjami; brak interpunkcji między zdaniami sprzyjał powtórzeniom i „zlewaniu” zdań [26] (oficjalne/społeczność). Każdy wers, który ma się oddzielić, zakończ znakiem albo `[pause:…]`.
- **Głos dryfuje w długim tekście** (zmiana mówcy w środku) — błąd danych, nie do naprawienia ustawieniem [27] (oficjalne). Krótsze kawałki, klon.
- **Akcent wyrazowy** nie ma sterowania (znaki akcentu U+0301 działają „trochę” i psują resztę — testy po rosyjsku) [37] (społeczność). Po polsku rzadko potrzebne; jeśli słowo źle brzmi — inny seed albo przeformułowanie.

## Poza fotorealizmem
Mowa „nie-naturalistyczna” w OmniVoice to głównie sprawa **wyboru głosu, rytmu i montażu**, nie opisu:
- **Szept** (`whisper`) jako cały rejestr głosu (projekt) [8]; skrajne wysokości `very low pitch` / `very high pitch`, wiek `child` / `elderly` [8] (oficjalne).
- **Obcy akcent w polszczyźnie jako środek:** klon próbki w innym języku czytający polski tekst przenosi akcent próbki [7][31] (oficjalne) — np. „głos z zewnątrz”.
- **Rytm mechaniczny / litania:** `[pause:…]` o równych długościach, tempo 0,5 albo 2,0 [5][10]; każdy kawałek między pauzami generuje się osobno, więc intonacja „resetuje się” — to może być efekt (niepotwierdzone artystycznie).
- **Chór, nakładanie, ten sam tekst wieloma głosami:** kilka seedów w trybie auto = kilka różnych głosów [22] — warstwy składa montaż.
- **Faktura (taśma, radio, telefon, pogłos, lo-fi) — nie w tym modelu.** Model czyści dźwięk (denoise) i nie przenosi akustyki próbki [25] (oficjalne). Zrób w obszarze SFX/montażu; nie wpisuj tego w tekst ani cechy.
- Nie istnieje sterowanie emocją słowami — nie obiecuj „mrocznego”, „lirycznego” brzmienia z promptu [30].

## Ruch / czas / dźwięk
- **Długość wyniku wynika z tekstu i tempa** (szacowana z liczby znaków; interpunkcja dolicza czas) [10][36] (oficjalne). Pole „czas trwania” istnieje w modelu, ale **Studio go nie wystawia** (zawsze auto) [2].
- Tempo zmienia długość bez zmiany wysokości; w klonie szacunek opiera się na tempie próbki — wolna próbka = wolniejsza mowa [36][19] (oficjalne).
- Oddechy, ciszę na początku/końcu model przycina (post-processing usuwa długie cisze, dodaje krótkie wyciszenie 0,1 s) [10] (oficjalne). Dłuższą ciszę w środku daje tylko `[pause:…]`.
- Wynik: WAV 24 kHz mono, głośność nienormalizowana [7][2].

## Sprawdź przed wysłaniem
- [ ] Właściwa pozycja: konkretny głos z opisu → projekt; konkretna osoba/emocja → klon; „byle głos” → OmniVoice.
- [ ] Język tekstu = pole „język” (w projekcie także tekst próbki w tym języku).
- [ ] Cechy tylko z listy, jedna na grupę, nie puste; akcent tylko przy angielskim; nie „child + whisper”.
- [ ] Dźwięki niewerbalne jako `<laughter>`, `<sigh>`; żadnych innych `[…]` poza `[pause:…]` i `[en:]`.
- [ ] Liczby, daty, skróty słownie; tekst kończy się znakiem interpunkcyjnym; wersy oddzielone interpunkcją lub `[pause:…]`.
- [ ] Klon: próbka 3–10 s, ten sam język, transkrypcja słowo w słowo.
- [ ] Jedna strofa/akapit na generację; poleć uczestnikowi 2–3 seedy.
- [ ] Brak didaskaliów, emocji i opisu akustyki w tekście — powiedz, gdzie je uzyskać (próbka, SFX, montaż).

## Źródła
[1] Studio: konfiguracja pozycji mowy — `modele/mowa/omnivoice.yaml`, `omnivoice-projekt.yaml`, `omnivoice-klon.yaml` — nasza konfiguracja
[2] Studio: workflowy ComfyUI — `workflows/mowa/omnivoice_*.api.json`; obsługa seeda/pól — `studio/workflow.py` — nasza konfiguracja
[3] Testy mowy — notatki własne (niepublikowane) — nasza konfiguracja
[4] TTS Audio Suite 5.9.2, OmniVoice Native Tags Guide — https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md — oficjalne (wtyczka)
[5] TTS Audio Suite 5.9.2, kod: `nodes/omnivoice/omnivoice_processor.py`, `utils/text/omnivoice_special_tags.py`, `utils/text/pause_processor.py`, `engines/adapters/omnivoice_adapter.py`, `utils/voice/designers.py` — https://github.com/diodiogod/TTS-Audio-Suite/tree/85da51e0 — oficjalne (kod wtyczki, wersja na Sparku)
[6] TTS Audio Suite README (pauzy, zmiana języka) — https://github.com/diodiogod/TTS-Audio-Suite — oficjalne (wtyczka)
[7] k2-fsa/OmniVoice README — https://github.com/k2-fsa/OmniVoice — oficjalne
[8] OmniVoice — Voice Design attributes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md — oficjalne
[9] OmniVoice — Tips & Notes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/tips.md — oficjalne
[10] OmniVoice — Generation Parameters — https://github.com/k2-fsa/OmniVoice/blob/master/docs/generation-parameters.md — oficjalne
[11] OmniVoice — Supported Languages (Polish: 911,68 h) — https://github.com/k2-fsa/OmniVoice/blob/master/docs/languages.md — oficjalne
[12] Hugging Face — k2-fsa/OmniVoice (licencja CC-BY-NC) — https://huggingface.co/k2-fsa/OmniVoice — oficjalne
[13] Zhu i in., „OmniVoice: Towards Omnilingual Zero-Shot TTS with Diffusion Language Models”, arXiv 2604.00688 — https://arxiv.org/abs/2604.00688 — oficjalne
[14] Issue #28 — znaczniki niewerbalne a spacje — https://github.com/k2-fsa/OmniVoice/issues/28 — oficjalne (odp. autora) / społeczność
[15] Issue #63 i #203 — pauzy z interpunkcji niegwarantowane — https://github.com/k2-fsa/OmniVoice/issues/63 , https://github.com/k2-fsa/OmniVoice/issues/203 — oficjalne (odp. autora)
[16] Issue #118 — krótkie wypowiedzi bez próbki — https://github.com/k2-fsa/OmniVoice/issues/118 — oficjalne (odp. autora)
[17] Issue #265 — cisza na końcu próbki — https://github.com/k2-fsa/OmniVoice/issues/265 — oficjalne (odp. autora)
[18] Issue #245 i #204 — ucinanie końca; polski test ze spacją przed „?” — https://github.com/k2-fsa/OmniVoice/issues/245 , https://github.com/k2-fsa/OmniVoice/issues/204 — oficjalne / społeczność
[19] Issue #116 — ostatnia głoska; obejście wolniejszym tempem — https://github.com/k2-fsa/OmniVoice/issues/116 — oficjalne (odp. autora)
[20] Issue #51 i #174 — liczby — https://github.com/k2-fsa/OmniVoice/issues/51 , https://github.com/k2-fsa/OmniVoice/issues/174 — oficjalne (odp. autora)
[21] Issue #44 — stały głos: zapisz projekt i klonuj — https://github.com/k2-fsa/OmniVoice/issues/44 — oficjalne (odp. autora)
[22] Issue #255 — tryb auto losuje głos — https://github.com/k2-fsa/OmniVoice/issues/255 — oficjalne (odp. autora)
[23] Issue #119 — „whisper” bez efektu w klonie — https://github.com/k2-fsa/OmniVoice/issues/119 — oficjalne (odp. autora)
[24] Issue #124 — szept i niska wysokość a „child” — https://github.com/k2-fsa/OmniVoice/issues/124 — oficjalne (odp. autora)
[25] Issue #95 — denoise, akustyka próbki się nie przenosi — https://github.com/k2-fsa/OmniVoice/issues/95 — oficjalne (odp. autora)
[26] Issue #134 — brak kropek i spacje → powtórzenia — https://github.com/k2-fsa/OmniVoice/issues/134 — społeczność (potwierdzone z autorem)
[27] Issue #206 i #176 — zmiana głosu w trakcie — https://github.com/k2-fsa/OmniVoice/issues/206 , https://github.com/k2-fsa/OmniVoice/issues/176 — oficjalne (odp. autora)
[28] Issue #248 — nierówne tempo (szacowanie długości) — https://github.com/k2-fsa/OmniVoice/issues/248 — społeczność
[29] Issue #21 — błędna transkrypcja próbki — https://github.com/k2-fsa/OmniVoice/issues/21 — społeczność
[30] Issue #78, #177, #178 — brak sterowania emocją; obejście próbkami — https://github.com/k2-fsa/OmniVoice/issues/78 , https://github.com/k2-fsa/OmniVoice/issues/178 — oficjalne (odp. autora) / społeczność
[31] Issue #47 — akcent z próbki — https://github.com/k2-fsa/OmniVoice/issues/47 — oficjalne (odp. autora)
[32] Issue #84 — teksty mieszanojęzyczne — https://github.com/k2-fsa/OmniVoice/issues/84 — oficjalne (odp. autora)
[33] Channelers, głosy „Ludzie” (ElevenLabs v3) — notatki własne (niepublikowane), `LUDZIE_uwagi_i_poprawki.md`, `LUDZIE_PL\05_babcia\05_babcia_prompt_i_tekst.md` — doświadczenie autora (inny model)
[34] Szablon medium „Mowa” — `prompty/media/mowa.md` — nasza konfiguracja
[35] Issue #144 — projektowanie mniej stabilne niż klon — https://github.com/k2-fsa/OmniVoice/issues/144 — oficjalne (odp. autora)
[36] OmniVoice — szacowanie długości (`omnivoice/utils/duration.py`) — https://github.com/k2-fsa/OmniVoice/blob/master/omnivoice/utils/duration.py — oficjalne (kod)
[37] Issue #129, #37, #65 — akcent wyrazowy (rosyjski) — https://github.com/k2-fsa/OmniVoice/issues/129 — społeczność
