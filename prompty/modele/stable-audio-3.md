<!-- Karta modelu dla promptmakera. modele: stable-audio-3 -->
# Stable Audio 3 small-SFX (Stability AI, 05.2026)

## Czym jest i do czego się nadaje
- Mały (ok. 0,5–0,6 mld parametrów) model dyfuzyjny **tekst → efekt / ambient / foley / one-shot**, **stereo 44,1 kHz**, długość 1 s – 2 min [6][7] (oficjalne), [3] (nasza konfiguracja).
- Końcowe etapy treningu small-SFX: **wyselekcjonowany podzbiór Freesound** (nagrania terenowe, foley, sound design); small-music dostał osobno AudioSparx, bo dane SFX psuły spójność muzyki [6] (oficjalne). Wniosek: model najlepiej rozumie opisy w stylu **tytułów, tagów i opisów z Freesound** [4][6] (oficjalne).
- Mocne strony: pojedyncze zdarzenia (uderzenia, kroki, drzwi, szkło), faktury i ambienty, przetworzony sound design (tape stop, przestery, filtry), ruch w panoramie stereo [4][9] (oficjalne).
- W teście Stability na efektach BBC (5 s) small-SFX wyprzedził Woosh-Flow (FAD 0,395 vs 0,580; CLAP 0,351 vs 0,277) — pomiar producenta [6] (oficjalne).
- **Czego NIE robi dobrze:**
  - **muzyki** — tabela trybów: small-sfx = tylko „Samples/SFX”, nie Music ani Stems [4] (oficjalne) → muzyka: inne modele Studia [3] (nasza konfiguracja);
  - **zrozumiałej mowy i śpiewu** — rodzina SA3 nie robi zrozumiałych wokali [4][5] (oficjalne);
  - **miksowania wielu źródeł naraz** — praktyk ocenia, że stary Stable Audio Open 1.0 lepiej wykonuje polecenie „zmiksuj” dźwięki [13] (społeczność);
  - **precyzyjnego czasu zdarzeń** (np. „uderzenie dokładnie w 3. sekundzie”) — sterowanie w czasie jest poza zakresem modelu [6] (oficjalne);
  - jakość ogólnie: opinie mieszane — „rozsądne wyniki, błyskawicznie”, ale gorzej niż SA Open 1.0 [13]; inny użytkownik: „ok. 10% lepiej niż 1.0”; pojedyncze skargi na szum [14] (społeczność).

## Co uczestnik ustawia w Studiu
| Pole | Wartości | Wpływ na prompt |
|---|---|---|
| **prompt** | tekst | jedyny opis; trafia do enkodera T5Gemma [1][2] (nasza konfiguracja) |
| **długość (s)** | 1–120, domyślnie 10 | to jest **prawdziwe sterowanie długością**: ComfyUI liczy z niej warunek `seconds_total` (liczba całkowita — ułamki są ucinane) [1][12] (nasza konfiguracja / kod ComfyUI). Dobierz do zdarzenia (patrz niżej) |
| **seed** | liczba | wyniki silnie zależą od ziarna — generuj warianty [3] (nasza konfiguracja) |

- Jeden tryb: model **destylowany** small-SFX, 8 kroków, **CFG 1**, sampler lcm [1][2] (nasza konfiguracja). **Brak trybu „jakość” i brak pola negatywu** — checkpoint base według karty HF jest „pretrenowany, przeznaczony do fine-tuningu; do generowania używaj Small SFX” [8] (oficjalne), więc Studio go nie wystawia. Przy CFG 1 gałąź negatywna i tak nie byłaby liczona [12][17].
- Oficjalny przykład dla modelu destylowanego używa samplera pingpong; Studio używa lcm (jak oficjalny szablon ComfyUI) [2][7] — na prompt to nie wpływa.
- Wyjście: FLAC stereo; **głośność nie jest normalizowana** [1][3] (nasza konfiguracja).
- Studio **nie rozszerza promptu** przez LLM (świadomie, inaczej niż szablon medium) [3] (nasza konfiguracja) — prompt promptmakera trafia do modelu 1:1.

## Format promptu
- **Język: angielski.** Karta modelu: język English; dane treningowe to angielskie metadane Freesound/AudioSparx [6][7] (oficjalne). Polskie słowa najwyżej jako nazwa własna — przetłumacz wszystko.
- **Prefiks `TrackType: SFX,`** na początku — oficjalnie zalecany dla efektów i sampli; w pracy technicznej autorzy piszą, że takie prefiksy „znacząco poprawiają jakość” (tam w kontekście modeli z danymi AudioSparx) [4][5][6] (oficjalne). Osobnego testu dla small-SFX brak — stosuj, ale to nie zaklęcie.
- **Struktura (kolejność Stability):** 1) **źródło** (dokładny przedmiot / materiał / instrument / syntezator) → 2) **akcja** (jak dźwięk powstaje, ile trwa, jak wygasa — atak, wybrzmienie, ogon) → 3) **produkcja i charakter** (mikrofon i jego odległość, pomieszczenie, obróbka) [4][5] (oficjalne).
- **Długość tekstu:** oficjalny szablon SFX (Comfy-Org/Stability) każe pisać **1–2 gęste zdania**, techniczny, konkretny język, bez redundancji [9] (oficjalne). Limit enkodera: **256 tokenów**, dalej ucinane [6] (oficjalne) — w praktyce nigdy nie dochodź blisko.
- **Styl:** w treningu pola metadanych łączono **przecinkami**, losowo tasowano i w połowie przypadków zamieniano na małe litery; część opisów Freesound to podpisy przepisane przez LLM [6] (oficjalne). Zatem działa zarówno zdanie naturalne, jak i ciąg fraz po przecinkach; wielkość liter i kolejność tagów nie są krytyczne.
- **`Length: N seconds`** na końcu — konwencja oficjalnego szablonu i przykładów ComfyUI [9][10] (oficjalne). W Studiu długość i tak ustawia pole „długość”; jeśli dopisujesz, **musi być zgodna z polem**. Wpływ samego tekstu na small-SFX — niepotwierdzony.
- **Wagi `(słowo:1.3)`, JSON, znaczniki sekcji** — brak w dokumentacji; nie używaj.
- **Negatywu nie ma** — czego ma nie być, nie opisuj; w razie potrzeby nazwij pozytywnie to, co ma być („dry, isolated”).
- **BPM** — to słownictwo muzyczne (AudioSparx, tryb Music/Instrument) [4][9]; small-SFX muzyki nie robi. Dla efektów rytmicznych (np. tykanie zegara) opisz tempo słowami („steady, once per second”) — skuteczność niepotwierdzona.

## Szkielet promptu
```
TrackType: SFX, [źródło: konkretny przedmiot + materiał], [akcja: jak powstaje dźwięk, tempo/intensywność], [przebieg w czasie: atak, wybrzmienie, ogon / narastanie, zanikanie], [przestrzeń: wnętrze/plener, sucho/pogłosowo, rodzaj pomieszczenia], [perspektywa: close-up / distant / approaching / passing left to right], [nagranie i obróbka: mikrofon, taśma, filtr, przester, odwrócenie]. Length: [N] seconds
```
Pejzaż (ambient):
```
TrackType: SFX, [miejsce/środowisko] ambience, [warstwa stała: tło/szum], [2–3 zdarzenia tła, rzadkie/częste], [odległość warstw], [pora/pogoda jako dźwięk, nie nastrój], [charakter nagrania: field recording, stereo]. Length: [N] seconds
```

## Co działa
- **Precyzja materiału i fizyki**: „wooden desk drawer”, „thin glass”, „hard boot on dry leaves”, „14-inch hi-hats played tightly closed” — oficjalne przykłady zawsze nazywają materiał, siłę i długość ogona [4][5][9] (oficjalne).
- **Opis ewolucji w czasie** w szablonie SFX: atak, wybrzmienie, ruch, przejścia — np. „starts with a suck-back of ambient noise, followed by a supersonic crack… that disappears into the distance” [9] (oficjalne).
- **Słownictwo przestrzeni** z szablonu: indoor/outdoor, cave / open field / underwater, dry / reverberant, close-up / distant, echoing / muffled [9] (oficjalne).
- **Ruch i stereo** (model jest stereo): „passing”, „approaching”, „doppler effect”, „sound moving from left to right stereo field”, „footsteps approaching then fading away” [9][10] (oficjalne).
- **Sekwencje**: oficjalny przykład „Rapid sequence of three impacts: metal hit, glass break, wood crack, spaced evenly” [9] (oficjalne) — krótkie, policzalne sekwencje można opisać; dokładnego rozmieszczenia w czasie nie oczekuj.
- **Mikrofon i nagranie** jako część opisu: „close-mic”, „recorded with a small-diaphragm condenser mic”, „ribbon mic”, „recorded in a dead room with no room reflections” [4][9] (oficjalne; część przykładów z szablonu One-shot).
- **Długość dopasowana do zdarzenia** (oficjalny szablon): uderzenia, kliknięcia 1–3 s; akcje średnie (kroki, przesuwanie, przejścia) 3–6 s; ambienty 6–15 s (przykłady ambientów do 45–120 s) [9] (oficjalne). Stability: wyniki są lepsze, gdy długość pasuje do opisanego dźwięku [4] (oficjalne).
- **Warianty seedem**, nie przepisywaniem promptu — generacja trwa 1–2 s [3] (nasza konfiguracja).
- **Warstwy osobno**: zamiast „deszcz + kroki + syrena” w jednym prompcie, wygeneruj każdą warstwę osobno i zmiksuj w montażu (wniosek z [13]; oficjalny przykład „Layered soundscape: rain, thunder, footsteps, and distant sirens” [9] pokazuje, że da się, ale jakość miksu bywa słabsza).

## Biasy i pułapki
- **Za długa długość dla krótkiego zdarzenia** → cisza, dopełnienie albo powtórzenia [18] (nasza konfiguracja); trening dodawał ciszę za nagraniem, by oddzielić długość od treści [6] (oficjalne).
- **Słowa nastroju zamiast dźwięku** („melancholijny”, „samotność”) — model uczony na metadanych bibliotek dźwięków; nastrój przetłumacz na zjawisko akustyczne (odległość, pogłos, rzadkość zdarzeń, filtr) [4][6] (wniosek z oficjalnych).
- **Dryf ku muzyce/tonowi** przy słowach typu „cinematic”, „epic”, „drone” — szablon używa ich świadomie dla sound designu [9]; jeśli chcesz surowe nagranie, nie dodawaj ich (niepotwierdzone jako bias, ostrożność).
- **Głośność**: Studio nie normalizuje [3] (nasza konfiguracja) — uprzedź uczestnika, że poziomy wyrówna się w montażu.
- **Małe zróżnicowanie między seedami** przy tym samym prompcie (obserwacja dla muzyki SA3) [15] (społeczność) — jeśli warianty są zbyt podobne, zmień jeden element opisu (perspektywę, materiał).
- **Brak pętli**: nie ma parametru pętli ani dokumentacji pętli dla SA3 (nie znaleziono). Pętlę robi się w montażu (crossfade) — patrz niżej.

## Poza fotorealizmem
Słownictwo obróbki i „taśmy” jest w oficjalnych przykładach, więc model je zna [4][9] (oficjalne):
- **taśma / winyl / archiwum**: „tape stop”, „tape-saturated”, „vinyl crackle”, „dusty”, „lo-fi”, „1950s” (przykłady z szablonów SFX/One-shot/Instrument) [9];
- **przetworzenie**: „processed with resonant band-pass filter”, „slightly distorted”, „bit-crushing”, „pitch-shifted”, „reversed”, „granular texture”, „glitchy digital distortion”, „long dark wooden room reverb” [9];
- **stylizacja medium**: „8-bit style”, „retro arcade”, „soft futuristic interface sounds” są w przykładach [9]; „cartoon”, „hand-drawn” — niepotwierdzone;
- **abstrakcja / faktura**: opisuj zjawisko fizyczne, nie znaczenie — „metal scraping slowly in a dark tunnel”, „heavy timber under immense structural tension, swaying slowly” [9];
- **perspektywy nietypowe**: „underwater”, „interior perspective”, „muffled” [9]; mikrofony specjalne („contact microphone”, „hydrophone”) to typowe tagi Freesound — skuteczność niepotwierdzona.
- Jak robić „rysunek/animację” w dźwięku: uproszczenie i przesada fizyki (krótki, suchy, bez tła: „dry, isolated, no background”) — wniosek, niepotwierdzone.

## Ruch / czas / dźwięk
- Ruch źródła: approaching / receding / passing / doppler / left-to-right stereo [9][10] (oficjalne).
- Przebieg: atak (sharp transient / slow attack), wybrzmienie (fast decay / long shimmering decay / reverb tail), narastanie (slow build) [4][9] (oficjalne).
- **Pętla (ambient)**: generuj dłużej niż potrzeba (np. 30–60 s), bez zdarzeń wyróżniających się na początku i końcu („steady, continuous, no sudden events” — niepotwierdzone), pętlę zamykaj długim crossfade'em w montażu; Studio nie ma trybu pętli [1] (nasza konfiguracja).
- Długość pola = długość wyniku; max 120 s [1][7].

## Sprawdź przed wysłaniem
- [ ] Prompt po angielsku, zaczyna się od `TrackType: SFX,`
- [ ] Nazwane źródło **i materiał**, akcja, przebieg w czasie, przestrzeń, perspektywa
- [ ] 1–2 zdania, bez nastrojów i metafor z wiersza (przetłumaczone na zjawiska akustyczne)
- [ ] Pole „długość” pasuje do zdarzenia (uderzenie 1–3 s, akcja 3–6 s, ambient 6–15 s+); jeśli dopisano `Length: N seconds` — zgodne z polem
- [ ] Jedno zdarzenie / jedna warstwa na prompt (warstwy → osobne generacje)
- [ ] Bez muzyki, mowy, BPM, wag, JSON
- [ ] Przypomnienie: kilka seedów; głośność do wyrównania w montażu

## Źródła
[1] Studio — `modele/sfx/stable-audio-3.yaml` — nasza konfiguracja
[2] Studio — `workflows/sfx/stable_audio_3_tekst-na-efekt.api.json` — nasza konfiguracja
[3] notatki własne (niepublikowane) (sekcja SFX) — nasza konfiguracja
[4] Stability AI — Stable Audio 3 prompting guide (GitHub) — https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md — oficjalne
[5] Stability AI — Stable Audio 3.0 Prompt Guide — https://stability.ai/guides/stable-audio-3-prompt-guide — oficjalne
[6] Stable Audio 3 — praca techniczna (arXiv 2605.17991) — https://arxiv.org/html/2605.17991v1 — oficjalne
[7] Hugging Face — stabilityai/stable-audio-3-small-sfx — https://huggingface.co/stabilityai/stable-audio-3-small-sfx — oficjalne
[8] Hugging Face — stabilityai/stable-audio-3-small-sfx-base — https://huggingface.co/stabilityai/stable-audio-3-small-sfx-base — oficjalne
[9] Comfy-Org — szablon „audio_stable_audio_3_medium” (kategorie reprompt: SFX, One-shot, Instrument; odczytany z pakietu comfyui-workflow-templates na Sparku) — https://github.com/Comfy-Org/workflow_templates — oficjalne (szablon pisany dla SA3 Medium; przykłady efektów przenoszą się na small-SFX)
[10] Comfy blog — Stable Audio 3.0 Day-0 Support — https://blog.comfy.org/p/stable-audio-3-day-0-support — oficjalne
[11] ComfyUI docs — Stable Audio 3 — https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3 — oficjalne
[12] ComfyUI — `comfy/samplers.py` (pominięcie gałęzi negatywnej przy CFG 1) i `comfy/model_base.py` (StableAudio3: `seconds_total` z długości latentu) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py — oficjalne (kod)
[13] jurn.link — How to install Stable Audio 3.0 small-SFX… — https://jurn.link/dazposer/index.php/2026/05/22/how-to-install-stable-audio-3-0-small-sfx-safetensors-and-run-it-in-comfyui/ — społeczność
[14] r/StableDiffusion (snapshot) — Stable Audio 3.0 Day-0 Support in ComfyUI — https://reddit.sentinel-team.org/posts/1tj7afx/snapshots/2026-05-21T18%3A20%3A48.87163Z — społeczność
[15] Dubspot — Stable Audio 3 review — https://blog.dubspot.com/stable-audio-3-review — społeczność
[16] fal.ai — Stable Audio 3 Small SFX Base (parametry API) — https://fal.ai/models/fal-ai/stable-audio-3/small/sfx/base/text-to-audio/llms.txt — społeczność/usługa
[17] ComfyUI notes — Conditioning Zero Out (CFG 1 a negatyw) — https://comfyui.nomadoor.net/en/notes/conditioning-zero-out/ — społeczność
[18] Studio — poradnik `poradniki/stable-audio-3-sfx.md` — nasza konfiguracja
