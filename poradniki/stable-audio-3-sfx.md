# Stable Audio 3 small-SFX — jak promptować

## Jak model słucha
Mały (459M), wyspecjalizowany model **efektów dźwiękowych** od Stability AI. Działa w **stereo**, efekty do ok. 2 minut, bardzo szybko (10 s efektu w 1–2 s na Sparku). Lubi opisy rzeczowe, jak z karty biblioteki dźwięków: źródło, działanie, charakter nagrania.

## Struktura opisu (kolejność wg Stability AI)
1. **Źródło** — dokładnie jaki przedmiot, instrument lub syntezator brzmi.
2. **Działanie** — jak dźwięk powstaje, jak długo trwa, jak wygasa (krótki/długi ogon).
3. **Produkcja / charakter** — ustawienie mikrofonu, akustyka pomieszczenia, obróbka.

Autorzy zalecają też znacznik **`TrackType: SFX`**, który zwykle daje bardziej sensowne efekty.

## Na co jest wrażliwy / pułapki
- **Ustaw krótką długość** — większość efektów jest krótka; długi czas przy krótkim zdarzeniu daje ciszę albo powtórzenia.
- Opisz materiał, wielkość uderzenia i długość ogona — to najbardziej zmienia wynik.

## Przykłady (z przewodnika Stability AI)
- „A blunt, powerful 'thud' made by slamming a wooden desk drawer shut. It has a pronounced low-mid body, making it feel heavy, and is given a touch of analog distortion for aggressive character.”
- „A classic, natural recording of 14-inch hi-hats played tightly closed. Zero ring and a very fast decay.”
- „A massive sub-bass note that mimics a vinyl record or tape machine being turned off.”

## Parametry, które realnie zmieniają wynik
- **Długość** (1–120 s; to prawdziwe sterowanie długością — dobierz do zdarzenia: uderzenie 1–3 s, akcja 3–6 s, ambient 6–15 s i więcej) i **seed** (generacja trwa 1–2 s — rób warianty seedem).
- Studio używa destylowanego modelu small-SFX (8 kroków, CFG 1), więc **nie ma pola negatywu** — czego ma nie być, tego po prostu nie opisuj. Głośność nie jest normalizowana.

## Źródła (dostęp 2026-10-05)
- Stability AI — Stable Audio 3 prompting (GitHub): https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md
- Stability AI — Stable Audio 3.0 Prompt Guide: https://stability.ai/guides/stable-audio-3-prompt-guide
- ComfyUI — Stable Audio 3: https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3
