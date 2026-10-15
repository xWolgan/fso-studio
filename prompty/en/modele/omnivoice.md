<!-- Model card for the promptmaker. modele: omnivoice, omnivoice-projekt, omnivoice-klon -->
# OmniVoice (k2-fsa / Xiaomi) — speech, three entries in the Studio

## What it is and what it's good for
- A 0.6B TTS model, a non-autoregressive "diffusion language model", over 600 languages (646), 24 kHz mono output [7][11][13] (official). Polish: approx. 912 h of training data [11] (official); in our test **the best Polish among the local models** (word accuracy 0.93 according to Whisper), a sentence in approx. 1 s [3] (our configuration).
- Three entries in the Studio = three model modes [1][2] (our configuration):
  - **OmniVoice** (`omnivoice`) — text only, **no voice description**: "auto" mode, the model picks the voice itself, **a different one for every seed** [7][22] (official).
  - **voice design** (`omnivoice-projekt`) — a voice from a **closed list of traits** (gender, age, pitch, whisper, English accent) [8] (official), [1] (ours).
  - **voice clone** (`omnivoice-klon`) — a voice from a sample + its exact transcript [7] (official). This is the **most stable** mode — the model was trained mainly for cloning [9][16][35] (official).
- **What it does NOT do well:**
  - **emotion and direction via description** — there is no field for "sad, tense"; the authors: no data with such annotations [30] (official). Emotion is carried only by the sample (clone), the text and punctuation.
  - **free-form prose voice description** ("warm, tired, hoarse") — it knows only the list of traits [8] (official). For a rich description: Breeze (EN/ZH only) [1] (ours).
  - **very short utterances (1–2 s) without a sample** — unstable [9][16] (official).
  - **acoustics/texture of the recording** — by default the model "denoises", producing cleaner sound than the sample; reverb, tape, telephone from the sample don't carry over [25] (official).
  - **reliable pauses** — a period and a comma "usually" produce a pause, but not always [15] (official).
  - it sometimes: cuts off the last sound/word [18][19], repeats or skips a fragment [26], changes voice in the middle of a longer utterance [27], has uneven pace in ~10% of generations [28] (official/community) — hence: several seeds and shorter chunks.
- Weights license: CC-BY-NC — non-commercial only [12] (official).

## What the participant sets in the Studio
The Studio runs OmniVoice through the ComfyUI plugin **TTS Audio Suite 5.9.2**; 32 steps, guidance 2.0, t_shift 0.1, `denoise` on, text normalization **off** — the participant can't change these [2][5] (our configuration / plugin code).

| Entry | Field | Values | Effect on the prompt |
|---|---|---|---|
| all | **text to speak** | text | the only place for content; syntax — below |
| all | **language** | Polish (default), English, German, French, Spanish, Italian, Ukrainian, Czech, Russian, Chinese, Japanese | must be the language of the text; with the language given, the model works "slightly better" [7] (official) |
| omnivoice, clone | **speech rate** | 0.5–2.0, default 1.0 | >1 faster, <1 slower [10] (official). Slower (e.g. 0.9) is also a workaround for clipped endings [19] (official) |
| all | **seed** | empty = random | in auto mode seed = **a different voice**; note down the seed that fits [2][22] |
| design | **voice traits** | at most one from each group (gender, age, pitch, whisper, English accent) | this is the whole "voice description"; it can't be empty (the plugin returns an error) [1][5] |
| design | **voice sample text** (advanced) | default "To jest próbka nowego głosu. Mówię spokojnie i wyraźnie." | min. 10 characters [5]. The model first reads it in the new voice (the "wzorzec" file, i.e. the reference), **then clones that reference** and speaks the text with it [1][5] |
| clone | **voice sample** | audio file, required | 3–10 s of clean speech [7] (official) |
| clone | **sample transcript** | text, required | exactly what is heard in the sample; without it the plugin refuses, Studio: silence [1][5] |

- **Design mode in practice** [5] (plugin code): the traits only affect the reference; your text is already produced by cloning the reference. Therefore: (a) **the language of the sample text = the language selected in the "language" field** (the same language goes to both stages); (b) **the accent works only when the sample text and the text are in English** [8] (official) — with non-English text the "accent" group does nothing; (c) the sample text should yield 3–10 s of speech (1–2 sentences, approx. 50–150 characters) and end with a period — it is the reference for the clone [7][17].
- **The same voice across many lines:** design creates the voice from scratch every time (there is freedom within the traits) [21] (official). The reliable way: download the "wzorzec" (reference), upload it as the sample in **voice clone** with transcript = the sample text [21] (official).

## Prompt format
- **Language: language of the text = the "language" field.** Voice traits are in English, but the participant selects them with buttons — the promptmaker only says **which buttons** to click [1] (ours).
- **Voice description (design only):** only values from the list, comma-separated, one per group: `female, elderly, low pitch` [8] (official). Empty group = the model decides. Anything outside the list is ignored [8]. Translating from the "Speech" medium matrix: of the "Who" and "Texture" points only gender, age, pitch and whisper remain; the rest (timbre, hoarseness, character, situation) — **you have to tell the participant directly that this model won't accept it** — it can be achieved with a sample (clone) or by choosing Breeze (in English) [34][8].
- **Text to speak — syntax in OUR Studio** (TTS Audio Suite plugin) [4][5][6]:
  - **Non-verbal sounds in angle brackets:** `<laughter>`, `<sigh>` (and `<confirmation-en>`, `<question-en>`, `<question-ah>`, `<question-oh>`, `<question-ei>`, `<question-yi>`, `<surprise-ah>`, `<surprise-oh>`, `<surprise-wa>`, `<surprise-yo>`, `<dissatisfaction-hnn>`). The plugin converts them to native `[laughter]` etc. **Don't write `[laughter]` in square brackets** — in the Studio `[...]` is plugin syntax [4] (official for the plugin). (Note: the old guide `poradniki/omnivoice.md` gives `[laughter]` — that's wrong for the Studio.)
  - **Pause of exact length:** `[pause:1.5s]`, `[pause:500ms]`, `[pause:2]` (= seconds); aliases `wait`, `stop` [5][6]. The plugin splits the text at that point and inserts silence — **the pause is reliable**, unlike punctuation [5][15]. Note: the chunks between pauses are generated separately (intonation "starts over") [5].
  - **Switching the language of a fragment:** `[en:]` before the fragment, e.g. text in one language with an English quotation; aliases like `[English:]` [6] (official for the plugin). Not tested in the Studio (unconfirmed). Without a tag the model tries to handle mixed text on its own [32] (official), but pronunciation of foreign insertions can be weaker.
  - **Anything else in `[...]` disappears** — the plugin treats it as a character name (e.g. `[wzdycha]`, `[pauza]`, `[B EY1 S]`) and doesn't read it [5] (plugin code). Don't put stage directions in the text. The native pronunciation correction from the README (`[B EY1 S]`, pinyin) **doesn't work in the Studio** [5][7].
- **Punctuation = prosody:** period, comma, ellipsis, dash, question mark shape the phrase [1] (ours); pauses from punctuation are likely, not guaranteed [15] (official). Always end the text with a period/question mark/exclamation mark — missing final punctuation encourages clipping of the ending [18] (official/community).
- **Numbers, dates, abbreviations — written out in words.** Text normalization is off in the Studio [5]; the authors: digits may be read wrongly, "normalize them to words" [7][20] (official). Write them in the language of the text, with correct grammatical forms where the language inflects them (e.g. Polish "w tysiąc dziewięćset osiemdziesiątym pierwszym"). Expand abbreviations ("dr", "np.", "itd.", "e.g.") (inferred from the lack of normalization — not confirmed by testing).
- **Weights, JSON, negative, emotion tags** (`[happy]` etc.) — don't exist [7][30] (official).
- **Length:** no hard limit; above approx. 30 s of speech the model splits the text into chunks of approx. 15 s on its own [10] (official). In practice: **one stanza / paragraph per generation** — easier to fix, less risk of voice change and mistakes [27][28] (inferred from reports).

## Prompt skeleton
Design (the participant clicks the traits):
```
traits: [gender], [age], [pitch]{, whisper}{, [accent — English text only]}
sample text: [1–2 sentences in the language of the text, 3–10 s of speech, in the tone of the piece, ending with a period]
text: [line/sentence, punctuation = phrasing]{ <sigh>}{ [pause:Ns]} [further text, numbers in words].
```
Clone:
```
sample: [3–10 s of clean speech by this person, in the language of the text, silence at the end]
transcript: [word for word what is heard in the sample, with punctuation]
text: [as above]
```
Plain OmniVoice: only `text` + language + speech rate.

## What works
- **Clone instead of description** when the bible describes a specific timbre/emotion: a recording of a person (or the participant) in that state, 3–10 s [7][9]. Emotions: separate "sad", "angry" etc. samples and generating in chunks, each with a different sample — a workaround accepted by the authors [30] (official/community).
- **A sample with silence at the end**: trimmed so the speech ends before the end of the file — that's how the author fixed artifacts in short utterances [17] (official).
- **Design → reference → clone** for a series of lines in one voice [21] (official).
- **`[pause:…]` instead of relying on a period** where the pause is part of the form (caesura, enjambment, silence between lines) [5][15].
- **`<laughter>` is the most reliable**; the other tags were trained mainly on Chinese data — in languages with spaces they were sometimes skipped or read aloud (partly fixed in the code) [14] (official/community). For non-Chinese text: `<laughter>`, `<sigh>`, and treat the rest as an experiment.
- **Question/exclamation mark in Polish:** one user writing in Polish: "gotowi do ofiary ?" (a space before `?`/`!`) gave a correct ending, without the space — a "hanging" ending [18] (community, single test).
- **Several seeds** of the same text and pick one — randomness is high (pace, pauses, word stress) [28][19] (official).
- **Colloquial spelling in the text** (e.g. Polish "ide", "sie", "troche") produced rural/colloquial pronunciation in the author's work on the "Ludzie" voices — but in ElevenLabs, not in OmniVoice [33] (author's experience; unconfirmed for OmniVoice).

## Biases and pitfalls
- **Auto mode = random voice** for each seed; it can't be described [22]. If the bible says whose voice it is — steer toward design or clone.
- **The sample's accent carries over to text** in another language (a Polish sample → English text with a Polish accent and vice versa); it can't easily be removed [7][31] (official). Trap in the chain "voice from Breeze in English → OmniVoice clone in another language (e.g. Polish)": that language will get an English accent [7] (official) — unless that's the point.
- **Trait conflicts:** whisper and low pitch don't work with "child" (no such data) [24]; "whisper" doesn't work in clone mode [23] (official). Some combinations are ignored — simplify the list [8].
- **Wrong sample transcript** → words from the sample or cut-offs may appear in the result [29] (community); the plugin only adds final punctuation and trims long silences in the sample [10].
- **Clipping of the last sound** — caused by the training data; mitigated by: a period at the end, a slower speech rate, a calmer sample with silence [18][19] (official).
- **Line breaks are not pauses:** newline characters become spaces; missing punctuation between sentences encouraged repetitions and sentences "running together" [26] (official/community). End every line that should stand apart with a punctuation mark or `[pause:…]`.
- **The voice drifts in long text** (speaker change midway) — a data issue, not fixable with settings [27] (official). Shorter chunks, clone.
- **Word stress** has no control (stress marks U+0301 work "a bit" and spoil the rest — tests in Russian) [37] (community). Rarely needed in Polish; if a word sounds wrong — another seed or rephrasing.

## Beyond photorealism
"Non-naturalistic" speech in OmniVoice is mainly a matter of **choice of voice, rhythm and editing**, not description:
- **Whisper** (`whisper`) as the whole register of the voice (design) [8]; extreme pitches `very low pitch` / `very high pitch`, age `child` / `elderly` [8] (official).
- **A foreign accent as a device:** a clone of a sample in another language reading text in the participant's language carries over the sample's accent [7][31] (official) — e.g. a "voice from outside".
- **Mechanical rhythm / litany:** `[pause:…]` of equal lengths, speech rate 0.5 or 2.0 [5][10]; each chunk between pauses is generated separately, so intonation "resets" — this can be an effect (artistically unconfirmed).
- **Choir, layering, the same text in many voices:** several seeds in auto mode = several different voices [22] — the layers are assembled in editing.
- **Texture (tape, radio, telephone, reverb, lo-fi) — not in this model.** The model cleans the sound (denoise) and doesn't carry over the sample's acoustics [25] (official). Do it in the SFX area/editing; don't put it in the text or the traits.
- There is no emotion control via words — don't promise a "dark" or "lyrical" sound from the prompt [30].

## Motion / time / sound
- **The result's length follows from the text and speech rate** (estimated from the number of characters; punctuation adds time) [10][36] (official). A "duration" field exists in the model, but **the Studio doesn't expose it** (always auto) [2].
- Speech rate changes length without changing pitch; in clone mode the estimate is based on the sample's pace — slow sample = slower speech [36][19] (official).
- The model trims breaths and silence at the beginning/end (post-processing removes long silences, adds a short 0.1 s fade) [10] (official). A longer silence in the middle comes only from `[pause:…]`.
- Output: WAV 24 kHz mono, loudness not normalized [7][2].

## Check before sending
- [ ] The right entry: specific voice from a description → design; specific person/emotion → clone; "any voice" → OmniVoice.
- [ ] Language of the text = the "language" field (in design, also the sample text in that language).
- [ ] Traits only from the list, one per group, not empty; accent only with English; not "child + whisper".
- [ ] Non-verbal sounds as `<laughter>`, `<sigh>`; no other `[…]` apart from `[pause:…]` and `[en:]`.
- [ ] Numbers, dates, abbreviations in words; the text ends with a punctuation mark; lines separated by punctuation or `[pause:…]`.
- [ ] Clone: 3–10 s sample, same language, transcript word for word.
- [ ] One stanza/paragraph per generation; recommend 2–3 seeds to the participant.
- [ ] No stage directions, emotions or acoustics description in the text — say where to get them (sample, SFX, editing).

## Sources
[1] Studio: speech entry configuration — `modele/mowa/omnivoice.yaml`, `omnivoice-projekt.yaml`, `omnivoice-klon.yaml` — our configuration
[2] Studio: ComfyUI workflows — `workflows/mowa/omnivoice_*.api.json`; seed/field handling — `studio/workflow.py` — our configuration
[3] Speech tests — own notes (unpublished) — our configuration
[4] TTS Audio Suite 5.9.2, OmniVoice Native Tags Guide — https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md — official (plugin)
[5] TTS Audio Suite 5.9.2, code: `nodes/omnivoice/omnivoice_processor.py`, `utils/text/omnivoice_special_tags.py`, `utils/text/pause_processor.py`, `engines/adapters/omnivoice_adapter.py`, `utils/voice/designers.py` — https://github.com/diodiogod/TTS-Audio-Suite/tree/85da51e0 — official (plugin code, version on the Spark)
[6] TTS Audio Suite README (pauses, language switching) — https://github.com/diodiogod/TTS-Audio-Suite — official (plugin)
[7] k2-fsa/OmniVoice README — https://github.com/k2-fsa/OmniVoice — official
[8] OmniVoice — Voice Design attributes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md — official
[9] OmniVoice — Tips & Notes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/tips.md — official
[10] OmniVoice — Generation Parameters — https://github.com/k2-fsa/OmniVoice/blob/master/docs/generation-parameters.md — official
[11] OmniVoice — Supported Languages (Polish: 911.68 h) — https://github.com/k2-fsa/OmniVoice/blob/master/docs/languages.md — official
[12] Hugging Face — k2-fsa/OmniVoice (CC-BY-NC license) — https://huggingface.co/k2-fsa/OmniVoice — official
[13] Zhu et al., "OmniVoice: Towards Omnilingual Zero-Shot TTS with Diffusion Language Models", arXiv 2604.00688 — https://arxiv.org/abs/2604.00688 — official
[14] Issue #28 — non-verbal tags and spaces — https://github.com/k2-fsa/OmniVoice/issues/28 — official (author's reply) / community
[15] Issues #63 and #203 — pauses from punctuation not guaranteed — https://github.com/k2-fsa/OmniVoice/issues/63 , https://github.com/k2-fsa/OmniVoice/issues/203 — official (author's reply)
[16] Issue #118 — short utterances without a sample — https://github.com/k2-fsa/OmniVoice/issues/118 — official (author's reply)
[17] Issue #265 — silence at the end of the sample — https://github.com/k2-fsa/OmniVoice/issues/265 — official (author's reply)
[18] Issues #245 and #204 — clipped endings; Polish test with a space before "?" — https://github.com/k2-fsa/OmniVoice/issues/245 , https://github.com/k2-fsa/OmniVoice/issues/204 — official / community
[19] Issue #116 — last sound; workaround with a slower speech rate — https://github.com/k2-fsa/OmniVoice/issues/116 — official (author's reply)
[20] Issues #51 and #174 — numbers — https://github.com/k2-fsa/OmniVoice/issues/51 , https://github.com/k2-fsa/OmniVoice/issues/174 — official (author's reply)
[21] Issue #44 — consistent voice: save the design and clone — https://github.com/k2-fsa/OmniVoice/issues/44 — official (author's reply)
[22] Issue #255 — auto mode randomizes the voice — https://github.com/k2-fsa/OmniVoice/issues/255 — official (author's reply)
[23] Issue #119 — "whisper" has no effect in clone mode — https://github.com/k2-fsa/OmniVoice/issues/119 — official (author's reply)
[24] Issue #124 — whisper and low pitch vs "child" — https://github.com/k2-fsa/OmniVoice/issues/124 — official (author's reply)
[25] Issue #95 — denoise, sample acoustics don't carry over — https://github.com/k2-fsa/OmniVoice/issues/95 — official (author's reply)
[26] Issue #134 — missing periods and spaces → repetitions — https://github.com/k2-fsa/OmniVoice/issues/134 — community (confirmed with the author)
[27] Issues #206 and #176 — voice change midway — https://github.com/k2-fsa/OmniVoice/issues/206 , https://github.com/k2-fsa/OmniVoice/issues/176 — official (author's reply)
[28] Issue #248 — uneven pace (length estimation) — https://github.com/k2-fsa/OmniVoice/issues/248 — community
[29] Issue #21 — wrong sample transcript — https://github.com/k2-fsa/OmniVoice/issues/21 — community
[30] Issues #78, #177, #178 — no emotion control; workaround with samples — https://github.com/k2-fsa/OmniVoice/issues/78 , https://github.com/k2-fsa/OmniVoice/issues/178 — official (author's reply) / community
[31] Issue #47 — accent from the sample — https://github.com/k2-fsa/OmniVoice/issues/47 — official (author's reply)
[32] Issue #84 — mixed-language texts — https://github.com/k2-fsa/OmniVoice/issues/84 — official (author's reply)
[33] Channelers, "Ludzie" voices (ElevenLabs v3) — own notes (unpublished), `LUDZIE_uwagi_i_poprawki.md`, `LUDZIE_PL\05_babcia\05_babcia_prompt_i_tekst.md` — author's experience (different model)
[34] "Speech" medium template — `prompty/media/mowa.md` — our configuration
[35] Issue #144 — design less stable than clone — https://github.com/k2-fsa/OmniVoice/issues/144 — official (author's reply)
[36] OmniVoice — length estimation (`omnivoice/utils/duration.py`) — https://github.com/k2-fsa/OmniVoice/blob/master/omnivoice/utils/duration.py — official (code)
[37] Issues #129, #37, #65 — word stress (Russian) — https://github.com/k2-fsa/OmniVoice/issues/129 — community
