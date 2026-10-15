<!-- Karta modelu dla promptmakera. modele: woosh, woosh-wideo -->
# Woosh (Sony AI, wagi publiczne 03.2026) — efekt z opisu i dźwięk do wideo

## Czym jest i do czego się nadaje
- Model fundamentowy **efektów dźwiękowych** Sony AI: **tekst → efekt** (Woosh-Flow / destylowany DFlow) i **wideo → zsynchronizowany dźwięk** z opcjonalnym opisem (VFlow / destylowany DVFlow) [5][6] (oficjalne).
- Wyjście: **mono, 48 kHz** (autoenkoder działa tylko na mono) [5] (oficjalne), WAV 24-bit; przy wideo także MP4 z podmienionym dźwiękiem [2][3] (nasza konfiguracja).
- Wersja publiczna trenowana na **Freesound (oryginalne opisy), AudioCaps (podpisy ludzkie), WavCaps (podpisy słabo etykietowane)**; wideo→dźwięk na VGGSound (podpisy z Qwen3-Omni albo oryginalne etykiety klas) [5] (oficjalne). Lepsza wersja „prywatna” (biblioteki Pro Sound Effects / BOOM) **nie jest dostępna** — Studio ma publiczną [3][8] (nasza konfiguracja / oficjalne).
- Mocne strony: krótkie, pojedyncze zdarzenia (pojazdy, silniki, oklaski, uderzenia), dźwięk przyklejony do ruchu w obrazie. W teście autorów wideo→dźwięk (FoleyBench) lepsza jakość/zgodność niż MMAudio, ale **gorsza synchronizacja** (DeSync 0,575 vs 0,400) [5] (oficjalne).
- **Czego NIE robi dobrze:**
  - **stereo, ruchu w panoramie** — tylko mono [5];
  - **długich ambientów** — trening na fragmentach **5 s** (tekst→efekt) [5]; Studio pozwala 1–10 s, >5 s = eksperyment [1] (nasza konfiguracja). Długie pejzaże → Stable Audio 3;
  - **pętli** — „idealne pętle” są dopiero w planach Sony [8] (oficjalne);
  - **precyzyjnego czasu, morfingu** — także w planach [8] (oficjalne);
  - **muzyki i mowy** — model do SFX; muzyka i mowa: inne modele Studia [3] (nasza konfiguracja);
  - modele destylowane (tryb „szybki”) wypadają gorzej od pełnych w większości metryk [5] (oficjalne).
  - Na efektach BBC (pomiar Stability) Woosh-Flow słabszy od SA3 small-SFX [11] (oficjalne, strona konkurencyjna).

## Co uczestnik ustawia w Studiu
**woosh (efekt z opisu)** [1][2] (nasza konfiguracja)
| Pole | Wartości | Wpływ |
|---|---|---|
| **prompt** | tekst (wymagany) | opis zdarzenia |
| **długość (s)** | 1–10, krok 0,5, domyślnie 5 | trening ok. 5 s; dłużej = eksperyment |
| **tryb** | szybki (DFlow, 4 kroki) / jakość (Flow, solver ODE) | szybki ~0,4 s, jakość ~12 s [3] |
| **siła opisu (CFG)** | 1–10, domyślnie 4,5 (zaawansowane) | wyżej = ściślej wg opisu |
| **seed** | liczba | warianty |

**woosh-wideo (dźwięk do wideo)** [1][2] (nasza konfiguracja)
| Pole | Wartości | Wpływ |
|---|---|---|
| **klip wideo** | wymagany | model widzi **8 s od „początku okna”**; wynik przycinany do długości klipu |
| **opis (opcjonalnie)** | tekst, może być pusty | podpowiada, *co* ma brzmieć; *kiedy* — wynika z obrazu |
| **początek okna (s)** | 0–60, krok 0,5 | klip > 8 s → kolejne okna osobnymi generacjami |
| **tryb** | szybki (DVFlow) / jakość (VFlow) | ~3 s / ~8 s [3] |
| **siła opisu (CFG)** | 1–10, domyślnie 3 (zaawansowane) | wpływ opisu względem obrazu |
| **seed** | liczba | warianty |

- **Brak pola negatywu** — API Woosh w Studiu go nie przyjmuje [1][2] (nasza konfiguracja). Nie dopisuj „no music” itp. do promptu (enkoder CLAP słabo rozumie negacje — niepotwierdzone dla Woosh, ostrożność).
- **Głośność**: bywa bardzo cicha (kroki na żwirze ok. −60 dB RMS); Studio nie normalizuje, tylko zapobiega przesterowi [2][3] (nasza konfiguracja).
- Licencja wag **CC-BY-NC** (niekomercyjna) [6] (oficjalne).

## Format promptu
- **Język: angielski — konieczny.** Enkoder tekstu to **RoBERTa-Large z Woosh-CLAP** [5] (oficjalne), angielski model językowy; podpisy treningowe po angielsku.
- **Twardy limit: 77 tokenów** (`max_sentence_tokens: 77`, nadmiar ucinany) [4] (oficjalne, konfiguracja wag) → praktycznie **do ok. 40–50 słów**; najważniejsze na początku. Zalecane: **8–25 słów**.
- **Styl: jedno zdanie opisujące zdarzenie dźwiękowe jak podpis AudioCaps/Freesound**: [źródło] + [akcja] (+ kontekst). Oficjalne przykłady: „Emergency vehicle driving with siren on”, „An engine humming and brakes squealing”, „Starting a motorcycle”, „A crowd applauds” [7] (oficjalne). AudioCaps to ludzkie podpisy klipów AudioSet [12] (oficjalne, zbiór danych).
- **Tekst nie jest przetwarzany** (`text_preprocessing: no_op`) [4] — interpunkcja i wielkość liter trafiają do modelu wprost; pisz normalnym zdaniem.
- **Brak** tagów, prefiksów (`TrackType` to Stable Audio — tu nie działa), wag, JSON, `Length:` — długość ustawia pole [1][2] (nasza konfiguracja); nic takiego nie występuje w dokumentacji Woosh [5][6][7].
- **Wideo + tekst**: podpisy V2A w treningu to naturalne zdania z Qwen3-Omni opisujące scenę i dźwięk, albo krótkie etykiety klas VGGSound [5] (oficjalne). Oficjalne przykłady opisów do wideo: „A propeller plane flies over a snowy landscape, its engine roaring.”, „A large audience in a formal hall gives a standing ovation with applause.” [7] — **opis widocznego źródła + jego dźwięk**.

## Szkielet promptu
Efekt z opisu (woosh):
```
[podmiot/źródło z materiałem] [czasownik akcji, z intensywnością/tempem], [drugie zdarzenie: "followed by…" / "while…"], [przestrzeń: in a large empty hall / outdoors / indoors], [odległość: close / in the distance]
```
Dźwięk do wideo (woosh-wideo):
```
[widoczne źródło] [czynność widoczna w kadrze], [jaki dźwięk wydaje: materiał, charakter], [tło akustyczne: wiatr / pogłos pomieszczenia — opcjonalnie]
```
albo minimalnie (etykieta jak VGGSound): `[źródło] [czynność]` — np. struktura „dog barking”.

## Co działa
- **Konkret: źródło + akcja** zamiast przymiotników — wszystkie przykłady autorów tak wyglądają [7] (oficjalne); poradnik Studia: 8–15 słów [13] (nasza konfiguracja).
- **Akcja + faktura + akustyka** w jednym zwrocie, np. struktura „fast metallic whoosh in a concrete stairwell” [10] (społeczność).
- **Dwa zdarzenia** łączone „and” / „followed by” (oficjalny przykład „An engine humming and brakes squealing” [7]); więcej niż 2–3 rozmywa wynik (niepotwierdzone).
- **Krótkie długości**: 1–5 s; dłuższe dźwięki zrób jako kilka generacji i sklej (wniosek z [5]).
- **Szybki tryb do szukania, jakość do finału** — destylowane modele są słabsze [5] (oficjalne); praktyka „scout DVFlow → finalize VFlow” [10] (społeczność).
- **CFG**: umiarkowane dla naturalnych faktur, wyżej dla stylizowanych / ściśle wg opisu [10] (społeczność). Destylacja była uczona dla CFG z zakresu 1–9; autorzy ewaluowali DFlow przy CFG 7 [5] (oficjalne). Domyślne 4,5 (tekst) i 3 (wideo) w Studiu — zostaw, chyba że wynik ignoruje opis (wtedy 5–7).
- **Seed**: kilka wariantów — dobre wyniki są losowe [3] (nasza konfiguracja).

## Biasy i pułapki
- **Ucięcie po 77 tokenach** — długi, poetycki opis traci końcówkę bez ostrzeżenia [4] (oficjalne).
- **Poezja i nastrój nie działają** — „długie, poetyckie opisy pomagają mniej niż konkretne źródło i działanie” [13] (nasza konfiguracja); enkoder CLAP był uczony na opisach zdarzeń akustycznych [5].
- **Polski prompt** — RoBERTa-Large to model angielski [5]; po polsku wynik będzie przypadkowy (niepotwierdzone testem, ale wynika z architektury).
- **Bardzo cichy wynik** — to nie błąd promptu [3] (nasza konfiguracja).
- **Wideo: synchronizacja dotyczy tego, co widać**; dźwięki spoza kadru (ambient, dalekie zdarzenia) model może pominąć — lepiej wygenerować je osobno (woosh lub Stable Audio 3) i zmiksować (wniosek, niepotwierdzone).
- **Wideo: tekst sprzeczny z obrazem** — model jest warunkowany obrazem *i* opisem [7]; skrajnie niezgodny opis (np. ptaki do kadru z silnikiem) da wynik niepewny; świadomy kontrapunkt lepiej robić przez osobną generację tekst→efekt (niepotwierdzone).
- **Wideo bez opisu**: działa (Studio: pusty opis = dźwięk tylko z obrazu) [3], ale używane modele VFlow/DVFlow są warunkowane obrazem **i** podpisem; autorzy mają osobne warianty „OV” tylko-wideo, których Studio nie używa [7] (oficjalne). Wniosek: przy niejednoznacznym obrazie (rysunek, abstrakcja, wygenerowane wideo) **opis warto dać**.
- **Okno 8 s**: dłuższy klip = kilka generacji z różnym „początkiem okna”; łączenie i crossfade w montażu [1][3] (nasza konfiguracja); społeczność dzieli klipy tak samo [14] (społeczność).

## Poza fotorealizmem
- Woosh to model **realistycznego foley/SFX** z danych Freesound/AudioCaps/WavCaps [5]; słownictwo obróbki (taśma, przester, filtr, glitch) **nie jest udokumentowane** dla Woosh — można próbować tagami typowymi dla Freesound („lo-fi”, „distorted”, „reversed”, „glitch”), skuteczność niepotwierdzona.
- Przetworzone / stylizowane brzmienia (taśma, granular, „8-bit”, tape stop) — **lepiej Stable Audio 3** (ma je w oficjalnych przykładach); Woosh użyj do surowego materiału, który uczestnik przetworzy w montażu.
- **Wideo nierealistyczne** (rysunek, animacja, kolaż): model widzi ruch, ale może źle rozpoznać źródło → opis tekstowy nazywający źródło i materiał dźwięku (nie styl obrazu — „drawing”, „animation” nic nie mówią o dźwięku) (wniosek, niepotwierdzone).
- Brak stereo → przestrzeń i ruch w panoramie dodaje się w montażu [5].

## Ruch / czas / dźwięk
- **Tekst→efekt**: długość z pola (1–10 s, najlepiej ≤5 s) [1][5]. Opis przebiegu prostymi czasownikami: „starts…”, „…then stops”, „passes by”, „approaches” (styl podpisów AudioCaps; skuteczność niepotwierdzona). Bez stereo — „left to right” nie zadziała [5].
- **Wideo→dźwięk**: czas i rytm zdarzeń bierze z ruchu w obrazie (cechy Synchformer, 24 kl./s) [2] (nasza konfiguracja); **w opisie nie podawaj czasów** („at 2 seconds”) — nie ma takiego sterowania (niepotwierdzone, brak w dokumentacji). Opis = *co* i *jakie*; obraz = *kiedy*.
- Opis do wideo: nazwij **widoczne** źródło i jego materiał („boots on wet snow”, nie „steps”), ewentualnie tło akustyczne miejsca.

## Sprawdź przed wysłaniem
- [ ] Angielski; jedno zdanie; 8–25 słów (twardo < 77 tokenów)
- [ ] Źródło + akcja na początku; materiał/faktura; przestrzeń i odległość (opcjonalnie)
- [ ] Bez nastroju, metafor, tagów, wag, `TrackType`, `Length:`
- [ ] Bez negacji („no music”) — Woosh nie ma negatywu
- [ ] Tekst→efekt: długość ≤5 s (dłużej tylko świadomie); ambient długi/stereo → zaproponuj Stable Audio 3
- [ ] Wideo: opis zgodny z tym, co widać; klip > 8 s → kolejne okna („początek okna”); bez podawania czasów
- [ ] Przypomnienie: wynik mono, często cichy — poziom w montażu; kilka seedów; licencja niekomercyjna

## Źródła
[1] Studio — `modele/sfx/woosh.yaml` i `woosh-wideo.yaml` — nasza konfiguracja
[2] Usługa Woosh na Sparku — notatki własne (niepublikowane) — nasza konfiguracja
[3] notatki własne (niepublikowane) (sekcja SFX) — nasza konfiguracja
[4] Konfiguracja wag Woosh — `~/sfx/Woosh/checkpoints/TextConditionerA/config.yaml` i `Woosh-CLAP/config.yaml` na Sparku (roberta-large, max_sentence_tokens: 77, text_preprocessing: no_op); pliki z wydania https://github.com/SonyResearch/Woosh/releases — oficjalne
[5] Woosh: A Sound Effects Foundation Model — raport techniczny (arXiv 2604.01929) — https://arxiv.org/html/2604.01929 — oficjalne
[6] GitHub — SonyResearch/Woosh (README, licencje) — https://github.com/SonyResearch/Woosh — oficjalne
[7] Woosh — strona projektu z przykładami — https://sonyresearch.github.io/Woosh/ — oficjalne
[8] Sony AI — Introducing Woosh — https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model — oficjalne
[9] GamesBeat — wywiad z zespołem Woosh — https://gamesbeat.com/sony-ai-releases-woosh-foundation-model-for-sound-effect-generation-exclusive-interview/ — oficjalne (wypowiedzi autorów)
[10] RunComfy — Woosh Sound Effect Generation in ComfyUI — https://www.runcomfy.com/comfyui-workflows/woosh-sound-effect-generation-in-comfyui-text2audio-videosync — społeczność
[11] Stable Audio 3 — praca techniczna, porównanie z Woosh-Flow — https://arxiv.org/html/2605.17991v1 — oficjalne (Stability)
[12] AudioCaps: Generating Captions for Audios in The Wild (NAACL 2019) — https://aclanthology.org/N19-1011/ — oficjalne (zbiór danych)
[13] Studio — poradnik `poradniki/woosh.md` — nasza konfiguracja
[14] Civitai — workflow Woosh wideo→dźwięk (podział na odcinki 8 s) — https://civitai.com/models/2627712 — społeczność
