<!-- Karta modelu dla promptmakera. modele: breeze-tts-2 -->
# Breeze TTS 2 (BreezeBlue, wagi otwarte 08.2026) — mowa EN / ZH, głos z opisu

## Czym jest i do czego się nadaje
- Model TTS ok. 3B, **tylko angielski i chiński** w jednym modelu; wyjście 24 kHz mono [4][6] (oficjalne). **Nie mówi po polsku** — do polskiego OmniVoice [1] (nasza konfiguracja).
- Mocna strona: **sterowanie głosem wolnym opisem w języku naturalnym** [4][6] (oficjalne). Trzy tryby, wybierane tym, które pola są wypełnione [4][5] (oficjalne / kod):
  - **Voice Design** — sama instrukcja, bez próbki: nowy głos z opisu postaci;
  - **Voice Clone** — próbka + dokładna transkrypcja, **bez instrukcji**: barwa, rytm, emocja i styl z próbki;
  - **Voice Direction** — próbka + transkrypcja + instrukcja: głos z próbki, a instrukcja reżyseruje ton, emocję, tempo, podanie.
- Zdarzenia głosowe w tekście (EN): `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)` [4][6] (oficjalne).
- W naszym teście: zgodność słów 1,00 (Whisper) dla trybu zwykłego, projektowanego i reżyserowanego; zdanie 5–9 s mowy liczy się 7–15 s [3] (nasza konfiguracja). Usługa przyjmuje **jedno zapytanie naraz** — kolejka [3].
- **Czego NIE robi dobrze:**
  - **polskiego** ani innych języków (hostowana wersja „multilingual” z 51 językami to **inny model**, nie ten w Studiu) [13] (oficjalne);
  - **polskich nazw własnych / nietypowych słów** w tekście angielskim — tester: marki, skróty, nazwy chemiczne źle wymawiane; brak słownika fonetycznego, pomaga zapis fonetyczny („Kree-Pal”) [17] (społeczność);
  - **akustyki otoczenia** (pomieszczenie, telefon, taśma) — opisy otoczenia nie są wśród udokumentowanych kategorii sterowania [7][16] (oficjalne; brak potwierdzenia, że działa);
  - **identycznego głosu między różnymi tekstami samym seedem** — seed powtarza wynik tylko dla identycznego wejścia [9] (oficjalne);
  - rzadko: wygaszanie końcówki, przekręcone słowo przy danym seedzie (zgłoszenie z GPU bez BF16; producent wskazuje sprzęt) [8] (społeczność/oficjalne).
- Licencja: wagi i wyniki tylko badawczo/niekomercyjnie [4] (oficjalne).

## Co uczestnik ustawia w Studiu
Studio woła usługę Breeze (`/v1/audio/speech`), tryb podstawowy (eager) [1][3] (nasza konfiguracja). Puste pole tekstowe **nie jest wysyłane** — usługa użyje wtedy swojego domyślnego zachowania [2] (nasza konfiguracja / kod Studia); dla instrukcji oznacza to „brak instrukcji” (w oficjalnym API `instruction` domyślnie `None`) [5] (kod).

| Pole | Wartości | Wpływ na prompt |
|---|---|---|
| **tekst do wypowiedzenia** | tekst EN/ZH | treść + zdarzenia głosowe |
| **głos i sposób mówienia** (instrukcja) | tekst; **domyślnie puste** | **bez próbki** = opis głosu (Design); **z próbką** = reżyseria (Direction). **Puste + próbka = czysty klon** [4][5]. Puste bez próbki = tryb zwykły (`tts_plain`, głos dobiera model) [5] |
| **próbka głosu** (opcjonalnie) | plik | razem z transkrypcją albo wcale — inaczej błąd [5] |
| **transkrypcja próbki** | tekst | słowo w słowo, także powtórzenia w nagraniu [4] (oficjalne) |
| **siła instrukcji (CFG)** (zaawansowane) | 0,5–4, domyślnie 1,0 | jak mocno model trzyma się instrukcji; patrz niżej |
| **seed** | puste = losowy | warianty; ten sam seed + identyczne pola = powtórzenie [9] |

- **Domyślna instrukcja jest pusta:** próbka + transkrypcja bez instrukcji = **czysty klon** (CFG 1,0) — tak zaleca producent [8] (oficjalne). Każdy wpisany tekst instrukcji zamienia klon w reżyserię.
- **CFG:** README zaleca **4** dla Design i Direction („wzmacnia trzymanie się instrukcji”) [4] (oficjalne) — Studio pozwala do 4. Dokumentacja usługi hostowanej: projekt głosu zacznij od 2–4, fragmenty ekspresyjne 1–3, ciągła narracja 1–2 [10][11] (oficjalne, wersja hostowana). Przy CFG 1,0 model nie liczy gałęzi bez instrukcji, więc opis działa słabiej [5] (kod). **CFG ≠ 1 bez instrukcji = błąd usługi** (szablon bez instrukcji nie ma gałęzi negatywnej) [5] (kod) — przy czystym klonie zostaw 1,0.

## Format promptu
- **Język: angielski** (tekst po angielsku → instrukcja po angielsku). „Dopasuj język instrukcji do języka tekstu”; instrukcje nie są tłumaczone [4][10] (oficjalne). Po chińsku — instrukcja po chińsku.
- Prompt dla uczestnika ma 2–3 części: **instrukcja** (pole „głos i sposób mówienia”), **tekst**, ewentualnie **próbka + transkrypcja**.
- **Instrukcja w trybie Design (opis głosu):** zwięzła, „telegraficzna” lub pełnymi zdaniami. Opisy w benchmarku producenta mają **110–250 znaków**: płeć i wiek, akcent, rola/persona, podanie (tempo, wysokość, faktura), emocja/styl [15] (oficjalne). Usługa hostowana przyjmuje do 500 znaków opisu; „więcej szczegółów nie gwarantuje lepszego głosu” [11] (oficjalne). Składniki (dowolne) [11]:
  1. rola i sytuacja (kto mówi, gdzie),
  2. głos bazowy — wiek, płeć, wysokość, akcent, zwykłymi słowami,
  3. **jedna–dwie** słyszalne cechy faktury (gravelly, breathy, velvety, light rasp),
  4. nawykowe tempo i artykulacja,
  5. emocjonalny środek ciężkości — nie emocja każdego zdania.
  Przykłady stylu z materiałów producenta: „A warm, thoughtful young woman with a clear voice and a calm, reflective delivery.” [4]; „Mature nomadic storyteller. Weathered, resonant speaking voice with rhythmic pacing” [7] (oficjalne).
- **Instrukcja w trybie Direction (z próbką):** **2–3 decyzje** z wymiarów: sytuacja, intencja (uspokaja, ostrzega, ukrywa), emocja z natężeniem („restrained panic”), rytm i akcenty (tempo, pauzy, oddech), stan fizyczny opisany przez dźwięk [10] (oficjalne, hostowane). Przykład README: „Speak slowly with a restrained, serious tone.” [4]. Nie zmieniaj w niej tożsamości (wieku, płci, akcentu) — to robi próbka/projekt [10].
- **Matryca medium „Mowa” → Breeze:** sytuacja nagrania, kto, faktura, charakter, stosunek do tego, co mówi, sposób mówienia — wszystko da się wyrazić po angielsku [21]. Doświadczenie autora (ok. 1000 znaków opisu) pochodzi z ElevenLabs [20]; dla Breeze celuj w ok. 150–500 znaków (benchmark/limit hostowany) — dłuższy opis niepotwierdzony.
- **Zdarzenia w tekście:** angielski — nawiasy okrągłe, w miejscu dźwięku: `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)` [4] (oficjalne); chiński — kwadratowe `[笑]`, `[叹气]`, `[咳嗽]`, `[清嗓子]` [4]. Nie mieszaj składni w jednym zapytaniu [12]. Dłuższa lista z dokumentacji hostowanej (`(gasps)`, `(whispers)`, `(sobs)`, `(pause)`…, tam w formie `(sighs)`, `(laughs)`) dotyczy modelu multilingual — **w naszym modelu niepotwierdzona**; ryzyko, że znacznik zostanie przeczytany na głos [12][16].
- **Nawiasy kwadratowe w tekście angielskim** — nie używaj (model dokleja wewnętrzny prefiks mówcy `[S0]`; skutek własnych `[...]` nieznany) [5] (kod; niepotwierdzone). Format „[Voice: …]” z jednej recenzji nie jest udokumentowany przez producenta [17] (społeczność, wątpliwe).
- **Wagi, negatyw, JSON** — nie istnieją. Liczby i skróty: dokumentacja milczy — pisz słownie (niepotwierdzone, ostrożność).
- **Długość tekstu:** limit generacji ok. **120 s mowy**, w praktyce mniej (budżet kontekstu, zwłaszcza z długą próbką) — zostaw zapas [9] (oficjalne). Dłuższe fragmenty dziel na granicach akapitów/zdań; producent radzi trzymać spójne fragmenty razem, nie siekać na pojedyncze zdania [9].

## Szkielet promptu
Projekt głosu (bez próbki):
```
instrukcja (EN): [rola/sytuacja]. [płeć], [wiek], [akcent albo „neutral accent”]. [1–2 cechy faktury], [wysokość/rejestr]. [nawykowe tempo i artykulacja]; [emocjonalny środek].
tekst (EN): [zdanie], [pauza przecinkiem/wielokropkiem]… {(sigh)} [zdanie].
CFG: 4 (zalecenie README; słabiej: 2–3)
```
Reżyseria (z próbką):
```
próbka: [czysta mowa jednej osoby, bez muzyki] + transkrypcja: [słowo w słowo]
instrukcja (EN): [intencja/sytuacja] + [emocja z natężeniem] + [rytm/oddech/stan fizyczny]{; at the word '[słowo]', [zmiana]}.
tekst (EN): [...]
CFG: 4 (zalecenie README; delikatniej: 1,5–3)
```
Czysty klon: próbka + transkrypcja, **instrukcja pusta**, CFG 1,0.

## Co działa
- **Opis roli zamiast listy przymiotników** — benchmark producenta ocenia „Role Fit”: jak przekonująco głos realizuje całą opisaną rolę [15] (oficjalne).
- **Zmiana w trakcie kwestii:** wskaż słowo-spust: „At the word 'Wait', suddenly shift to terrified, breathless alarm” [7] (oficjalne). Ocena producenta: liczy się stan początkowy, miejsce zmiany i stan końcowy [16].
- **Stan fizyczny przez słyszalne objawy:** „heavily out of breath and gasping”, drżenie, zmęczenie, zacinanie — benchmark wymaga konkretnych markerów, nie ogólnej emocji [7][16] (oficjalne).
- **Precyzyjny niuans emocji** („restrained”, „conflicted”, „resentful”) — oceniany osobno od ogólnej emocji [16] (oficjalne).
- **Akcent angielski z opisem stopnia** („a gentle Southern lilt”, „Japanese-accented English”) [7][16] (oficjalne).
- **Seria kwestii jednym głosem:** zaprojektuj głos → zapisz wynik → używaj go jako próbki (z dokładną transkrypcją) we wszystkich kolejnych; te same parametry; łącz z 0,2–0,3 s ciszy i wyrównaj głośność [9][14] (oficjalne). Producent normalizuje próbki do −18 LUFS i używa fragmentu do 30 s kończącego się na pełnym zdaniu [9][14] (oficjalne, wersja hostowana).
- **Próbka:** czysta, jedna osoba, bez tła i bez zapętleń, min. 3 s; tester: 6 s dało stabilną barwę [4][14][17]. Optimum długości dla lokalnego modelu — nieustalone.
- **Kilka seedów** — przy wadach rzadkich jedna próba nie wystarcza [8] (społeczność).

## Biasy i pułapki
- **Polski tekst** → model go nie obsługuje; nie próbuj „polskiego z angielską instrukcją” [1][4].
- **Jakakolwiek instrukcja przy klonie** (nawet „Speak clearly and naturally.”) zamienia klon w reżyserię i może zmieniać podanie próbki [1][8].
- **Sprzeczność próbki i instrukcji** (np. kobieca próbka, „deep male voice”) to już Direction w konflikcie — producent przypisał takie złe wyniki niezgodnemu wejściu [8] (oficjalne).
- **Niedokładna transkrypcja** (np. próbka powtarza zdanie, a transkrypcja nie) psuje wynik [8] (oficjalne).
- **Klon międzyjęzykowy** (próbka w innym języku niż EN/ZH tekst) — zgłoszony „collapse” wyniku [8] (społeczność); trzymaj próbkę po angielsku dla tekstu angielskiego.
- **Łańcuch Breeze → OmniVoice (głos z opisu, potem polski):** OmniVoice przenosi akcent próbki na inny język, więc angielska próbka da polszczyznę z angielskim akcentem [18] (oficjalne OmniVoice); test tego łańcucha w Studiu jeszcze nie zrobiony [19] (nasza konfiguracja).
- **Sybilanty i pasmo:** tester słyszał ostre „s/t” i brak „powietrza” (24 kHz), głośność ok. −18 LUFS — do korekty w montażu [17] (społeczność).

## Poza fotorealizmem
- **Głosy nie-ludzkie i stylizowane da się opisać** — benchmark producenta zawiera m.in. „Non-human, mechanical-spectral. Low engine thrum, metallic distorted whisper.”, „Booming resonant, massive mechanical scale.”, stwory, postaci z animacji i komiksu [7][15] (oficjalne). To główna droga do mowy „nie fotorealistycznej” w tym modelu.
- **Konwencje mówienia:** archaiczny narrator, opowiadacz baśni z rytmem, recytacja, hipnotyczny rytm („hypnotic and persuasive rhythm”), teatralność [7] (oficjalne).
- **Szept, krzyk, zadyszka, płacz** — jako instrukcja Direction (kategorie: acoustic attributes, physiological state) [16] (oficjalne).
- **Faktura nośnika (taśma, radio, telefon, pogłos)** — nieudokumentowana; nie obiecuj. Jeśli biblia tego chce: prompt opisuje głos, a faktura idzie do obszaru SFX/montażu [7][16].
- Śpiew: nieudokumentowany dla otwartego modelu (`(singing)` tylko w liście hostowanej) [12] — niepotwierdzone.

## Ruch / czas / dźwięk
- Długość = długość tekstu × tempo podane w instrukcji („slowly”, „brisk pace”); pola długości ani tempa w Studiu nie ma [1][4].
- Pauzy: interpunkcja i instrukcja („emotional pauses”, „measured pauses”) [10][11] (oficjalne); znacznik `(pause)` niepotwierdzony w tym modelu [12]. Dokładne cisze — w montażu.
- Maks. ok. 120 s na generację, realnie mniej [9]. Wynik: WAV 24 kHz mono [2][4].
- Dialog: jedna kwestia (jeden głos) na zapytanie, łączenie w montażu [13] (oficjalne, hostowane).

## Sprawdź przed wysłaniem
- [ ] Tekst po angielsku (lub chińsku), instrukcja w tym samym języku; brak polskich słów albo zapis fonetyczny.
- [ ] Tryb jasny: Design (instrukcja = opis głosu) / Direction (próbka + reżyseria) / czysty klon (instrukcja pusta, CFG 1,0).
- [ ] Opis: rola + głos bazowy + 1–2 cechy faktury + tempo + emocjonalny środek, ok. 150–500 znaków, bez sprzeczności.
- [ ] Reżyseria: 2–3 decyzje, bez zmiany tożsamości; zmiana w trakcie przez „at the word '…'”.
- [ ] Zdarzenia tylko `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)`; żadnych `[...]` w tekście angielskim.
- [ ] Próbka z dokładną transkrypcją (oba pola albo żadne); CFG 4 dla opisu/reżyserii (zalecenie README), 1,0 przy pustej instrukcji.
- [ ] Tekst poniżej ok. 1–1,5 min mowy; kilka seedów.

## Źródła
[1] Studio: `modele/mowa/breeze-tts-2.yaml` — nasza konfiguracja
[2] Studio: `studio/backends/http.py` (puste pola nie są wysyłane), `studio/workflow.py` (seed, wartości pól) — nasza konfiguracja
[3] Testy i API Breeze — notatki własne (niepublikowane) — nasza konfiguracja
[4] breezeblue-ai/breeze-tts README (commit 58ec70c, wersja na Sparku) — https://github.com/breezeblue-ai/breeze-tts — oficjalne
[5] breeze-tts, kod szablonów i API — https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/templates.py , https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/api.py — oficjalne (kod)
[6] Hugging Face — BreezeBlue/Breeze-TTS-2 — https://huggingface.co/BreezeBlue/Breeze-TTS-2 — oficjalne
[7] BreezeBlue — Introducing Breeze TTS 2 (przykłady Design/Direction) — https://breezeblue.ai/breeze-tts-2 — oficjalne
[8] Issue #14 — defekty przy seedach; odpowiedź producenta: czysty klon bez instrukcji i CFG 1, konflikt próbka/instrukcja — https://github.com/breezeblue-ai/breeze-tts/issues/14 — społeczność / oficjalne (odp. producenta)
[9] Issue #25 — długie teksty (~120 s), spójność głosu, łączenie fragmentów — https://github.com/breezeblue-ai/breeze-tts/issues/25 — oficjalne (odp. producenta)
[10] BreezeBlue Docs — Voice instruction prompting — https://docs.breezeblue.ai/guides/voice-instruction-prompting — oficjalne (usługa hostowana)
[11] BreezeBlue Docs — Voice Design prompting — https://docs.breezeblue.ai/guides/voice-design-prompting — oficjalne (usługa hostowana)
[12] BreezeBlue Docs — Audio tags — https://docs.breezeblue.ai/guides/audio-tags — oficjalne (usługa hostowana, model multilingual)
[13] BreezeBlue Docs — Text to Speech (modele breeze-tts-2 vs multilingual, dialogi) — https://docs.breezeblue.ai/guides/text-to-speech — oficjalne (usługa hostowana)
[14] BreezeBlue Docs — Voice clone (próbka: min. 3 s, fragment do 30 s, −18 LUFS) — https://docs.breezeblue.ai/guides/voice-clone — oficjalne (usługa hostowana)
[15] TTS Voice Design Benchmark (zbiór 1000 opisów) — https://huggingface.co/datasets/BreezeBlue/TTS-Voice-Design-Benchmark , https://github.com/breezeblue-ai/tts-voice-design-benchmark — oficjalne
[16] TTS Voice Direction Benchmark (kategorie: emocja, akcent, stan fizyczny, wariacja, zdarzenia) — https://github.com/breezeblue-ai/TTS-Voice-Direction-Benchmark — oficjalne
[17] CrePal — Breeze TTS 2 Review for AI Video Voiceovers — https://crepal.ai/blog/?p=9183 — społeczność (pojedyncza recenzja)
[18] k2-fsa/OmniVoice README (akcent przy klonie międzyjęzykowym) — https://github.com/k2-fsa/OmniVoice — oficjalne
[19] Plan: test łańcucha Breeze → klon OmniVoice — notatki własne (niepublikowane) — nasza konfiguracja
[20] Channelers, głosy „Ludzie” (ElevenLabs v3) — notatki własne (niepublikowane), `ludzie_matryca.md` — doświadczenie autora (inny model)
[21] Szablon medium „Mowa” — `prompty/media/mowa.md` — nasza konfiguracja
