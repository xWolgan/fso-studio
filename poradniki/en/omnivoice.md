# OmniVoice — how to prompt

## How the model listens
A speech model (k2-fsa) for over 600 languages — it **speaks Polish well** too (word accuracy of 0.93 in our test). Three ways of working: plain synthesis, **voice design** from a list of attributes (no recording) and **voice cloning** from a short recording. It reads the text exactly as written — punctuation shapes the phrase.

## Voice design (attributes from a list)
Attributes separated by commas, **one attribute from each category**:
- gender: male / female
- age: child, teenager, young adult, middle-aged, elderly
- pitch: very low pitch, low pitch, moderate pitch, high pitch, very high pitch
- style: whisper
- English accent: American, British, Australian, Canadian, Indian… (only with English text)

Example: `female, middle-aged, low pitch` or `male, elderly, whisper`. In this mode the model **doesn't understand** prose descriptions ("a warm, tired voice").

In the Studio, the sample text (the "voice sample text" field) must be in the language chosen in the "language" field: the model first reads it in the new voice, then clones that recording and uses it to speak your text. So the accent only works with English text. Each run designs the voice from scratch — to keep the same voice across many lines, download the "reference" and use it for cloning.

## Voice cloning
- A **3–10 s** recording, clean speech, ideally with a moment of silence at the end. Longer slows things down and can make the clone worse.
- **Sample transcript** — exactly what can be heard in the recording (without it the Studio won't generate anything).
- A recording in the **same language** the clone is supposed to speak — otherwise an accent appears.
- Reverb, tape, telephone sound don't carry over from the sample — the model "cleans up" the sound.

## Text: pronunciation, pauses, non-verbal sounds
- Punctuation = phrasing and pauses (full stop, comma, dash, ellipsis) — a pause from punctuation is likely, not certain. Always end the text with a full stop, question mark or exclamation mark (otherwise the model is more likely to clip the ending).
- **Non-verbal sounds in angle brackets:** `<laughter>`, `<sigh>` (and e.g. `<question-en>`, `<surprise-ah>`, `<dissatisfaction-hnn>` — in Polish the most reliable are `<laughter>` and `<sigh>`). **Don't write `[laughter]`** — in the Studio square brackets mean something else.
- **A pause of exact length:** `[pause:1.5s]`, `[pause:500ms]` — more reliable than a full stop.
- **Switching the language of a fragment:** `[en:]` before a fragment in English.
- **Any other `[…]` disappears** (the Studio treats it as a character name) — don't type stage directions like `[sighs]`. The phonetic notation from the model's documentation (`[B EY1 S]`) doesn't work in the Studio.
- **Write numbers, dates and abbreviations out in words** (text normalisation is turned off).

## What it's sensitive to / pitfalls
- Attributes not on the list are ignored; whisper and low pitch don't work with "child".
- Emotion can't be set by a description — it's carried only by the sample (clone), the text and the punctuation.
- Without a sample and without attributes (plain synthesis) the model picks a **different voice** for every seed.
- A new line is not a pause — separate lines of verse with punctuation or `[pause:…]`.
- It's worth splitting a very long text into paragraphs (separate generations) — easier to fix, less risk of the voice changing midway.

## Parameters that really change the result
- **speech rate** 0.5–2.0 (>1 faster, <1 slower; slightly slower helps when the model clips endings). The Studio doesn't expose a fixed length in seconds.
- **seed** — results vary a lot; try 2–3 and save the one that works.

## Licence
CC-BY-NC — non-commercial only.

## Sources (accessed 2026-10-05)
- k2-fsa/OmniVoice (README): https://github.com/k2-fsa/OmniVoice
- OmniVoice — voice design: https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md
- TTS Audio Suite — OmniVoice Tags Guide (tag syntax in the Studio): https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md
- Polish test: our own, on the Spark.
