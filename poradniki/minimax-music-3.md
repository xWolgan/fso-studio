# MiniMax Music 3 — jak promptować

## Jak model słucha
Otwarty model muzyczny MiniMax (sierpień 2026): z **tekstu** i **opisu brzmienia** robi spójny utwór do 5 minut (32 kHz, stereo). Opis może być zwykłą prozą albo **ustrukturyzowanym opisem** w trzech sekcjach. Znaczniki sekcji i opisy to wskazówki, nie gwarancje — tempo, tonacja i budowa nie zawsze zostaną dokładnie zachowane.

## Struktura
**Opis ustrukturyzowany (trzy sekcje):**
1. **Global metadata** — gatunek, podgatunek, BPM, tonacja, skala, przebieg emocjonalny, sytuacja słuchania, profil produkcji.
2. **Vocal details** — płeć, barwa, sposób śpiewu, harmonie, chórki, efekty (przy utworze instrumentalnym — pomiń albo napisz wprost, że brak wokalu).
3. **Arrangement** — instrumenty główne i dodatkowe, jak zmieniają się w sekcjach, groove, bas, perkusja, faktury, przestrzeń.

Wzór z karty modelu: „Genre: acoustic pop. BPM: 96. Key: C major. Warm and intimate…” / „Vocals: soft female lead…” / „Arrangement: fingerpicked guitar and soft piano; brushed drums…”.

**Tekst:** znaczniki `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` — **każdy w osobnej linii**, bez słów w tej samej linii. Utwór instrumentalny: sekcje `[Instrumental]` / `[Solo]`.

## Na co jest wrażliwy / pułapki
- Tekst w tej samej linii co znacznik — źle parsowany.
- Długi utwór = długie generowanie (na Sparku ok. 93 s na 30 s muzyki w trybie szybkim).

## Przykład (struktura, instrumentalnie)
- Opis: „Genre: ambient electronica. BPM: 80. Key: D minor. Slowly brightening, from tension to calm. Vocals: none, purely instrumental. Arrangement: analog synth drones, sparse plucked bass, distant processed field recordings, slowly opening filter, wide stereo reverb.”
- Tekst:
```
[Intro]
[Instrumental]
[Solo]
[Outro]
```

## Parametry, które realnie zmieniają wynik
- **Tryb**: szybki (enkoder INT8) / pełna jakość (bf16, ok. 146 s na 30 s). **Długość**, **seed**.

## Źródła (dostęp 2026-10-05)
- Hugging Face — MiniMaxAI/MiniMax-Music3: https://huggingface.co/MiniMaxAI/MiniMax-Music3
- MiniMax — Music 3.0 (blog): https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model
- ComfyUI — MiniMax Music 3: https://blog.comfy.org/p/minimax-music-3-state-of-the-art
- Prompting MiniMax Music 3 (Space): https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide
