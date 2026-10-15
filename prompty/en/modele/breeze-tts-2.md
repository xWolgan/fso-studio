<!-- Model card for the promptmaker. modele: breeze-tts-2 -->
# Breeze TTS 2 (BreezeBlue, open weights 08.2026) — EN / ZH speech, voice from a description

## What it is and what it's good for
- A TTS model of about 3B, **English and Chinese only** in a single model; 24 kHz mono output [4][6] (official). **Does not speak Polish or any other language** — for Polish (and other languages) use OmniVoice [1] (our configuration).
- Strength: **controlling the voice with a free-form natural-language description** [4][6] (official). Three modes, selected by which fields are filled in [4][5] (official / code):
  - **Voice Design** — instruction only, no sample: a new voice from a character description;
  - **Voice Clone** — sample + exact transcript, **no instruction**: timbre, rhythm, emotion and style from the sample;
  - **Voice Direction** — sample + transcript + instruction: the voice from the sample, while the instruction directs tone, emotion, pace, delivery.
- Vocal events in the text (EN): `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)` [4][6] (official).
- In our test: word accuracy 1.00 (Whisper) for plain, designed and directed modes; a sentence of 5–9 s of speech takes 7–15 s to compute [3] (our configuration). The service accepts **one request at a time** — queue [3].
- **What it does NOT do well:**
  - **Polish** or other languages (the hosted "multilingual" version with 51 languages is a **different model**, not the one in the Studio) [13] (official);
  - **Polish (or other foreign) proper names / unusual words** in English text — a tester: brands, abbreviations, chemical names mispronounced; no phonetic dictionary, phonetic spelling helps ("Kree-Pal") [17] (community);
  - **ambient acoustics** (room, telephone, tape) — environment descriptions are not among the documented control categories [7][16] (official; no confirmation that it works);
  - **an identical voice across different texts from the seed alone** — the seed repeats a result only for identical input [9] (official);
  - rarely: the ending fading out, a garbled word with a given seed (reported on a GPU without BF16; the vendor points to the hardware) [8] (community/official).
- Licence: weights and outputs for research/non-commercial use only [4] (official).

## What the participant sets in the Studio
The Studio calls the Breeze service (`/v1/audio/speech`), basic mode (eager) [1][3] (our configuration). An empty text field **is not sent** — the service then uses its default behaviour [2] (our configuration / Studio code); for the instruction this means "no instruction" (in the official API `instruction` defaults to `None`) [5] (code).

| Field | Values | Effect on the prompt |
|---|---|---|
| **text to speak** | EN/ZH text | content + vocal events |
| **voice and manner of speaking** (instruction) | text; **empty by default** | **without a sample** = voice description (Design); **with a sample** = direction (Direction). **Empty + sample = pure clone** [4][5]. Empty without a sample = plain mode (`tts_plain`, the model picks the voice) [5] |
| **voice sample** (optional) | file | together with a transcript or not at all — otherwise an error [5] |
| **sample transcript** | text | word for word, including repetitions in the recording [4] (official) |
| **instruction strength (CFG)** (advanced) | 0.5–4, default 1.0 | how strongly the model sticks to the instruction; see below |
| **seed** | empty = random | variants; same seed + identical fields = repetition [9] |

- **The default instruction is empty:** sample + transcript without an instruction = **pure clone** (CFG 1.0) — as the vendor recommends [8] (official). Any instruction text you type turns the clone into direction.
- **CFG:** the README recommends **4** for Design and Direction ("strengthens instruction adherence") [4] (official) — the Studio allows up to 4. Hosted service documentation: start voice design at 2–4, expressive passages 1–3, continuous narration 1–2 [10][11] (official, hosted version). At CFG 1.0 the model doesn't compute the no-instruction branch, so the description works more weakly [5] (code). **CFG ≠ 1 without an instruction = service error** (the no-instruction template has no negative branch) [5] (code) — for a pure clone leave it at 1.0.

## Prompt format
- **Language: English** (English text → English instruction). "Match the instruction language to the text language"; instructions are not translated [4][10] (official). For Chinese — the instruction in Chinese.
- The prompt for the participant has 2–3 parts: **instruction** (the "voice and manner of speaking" field), **text**, optionally **sample + transcript**.
- **Instruction in Design mode (voice description):** concise, "telegraphic" or in full sentences. Descriptions in the vendor's benchmark are **110–250 characters**: gender and age, accent, role/persona, delivery (pace, pitch, texture), emotion/style [15] (official). The hosted service accepts up to 500 characters of description; "more detail doesn't guarantee a better voice" [11] (official). Components (any of them) [11]:
  1. role and situation (who is speaking, where),
  2. base voice — age, gender, pitch, accent, in plain words,
  3. **one or two** audible texture features (gravelly, breathy, velvety, light rasp),
  4. habitual pace and articulation,
  5. emotional centre of gravity — not the emotion of every sentence.
  Style examples from the vendor's materials: "A warm, thoughtful young woman with a clear voice and a calm, reflective delivery." [4]; "Mature nomadic storyteller. Weathered, resonant speaking voice with rhythmic pacing" [7] (official).
- **Instruction in Direction mode (with a sample):** **2–3 decisions** from these dimensions: situation, intention (reassures, warns, conceals), emotion with intensity ("restrained panic"), rhythm and emphasis (pace, pauses, breath), physical state described through sound [10] (official, hosted). README example: "Speak slowly with a restrained, serious tone." [4]. Don't change identity in it (age, gender, accent) — that's what the sample/design does [10].
- **"Speech" medium matrix → Breeze:** recording situation, who, texture, character, attitude to what they say, manner of speaking — all of it can be expressed in English [21]. The author's experience (descriptions of about 1000 characters) comes from ElevenLabs [20]; for Breeze aim at about 150–500 characters (benchmark/hosted limit) — longer descriptions unconfirmed.
- **Events in the text:** English — round brackets, at the point of the sound: `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)` [4] (official); Chinese — square brackets `[笑]`, `[叹气]`, `[咳嗽]`, `[清嗓子]` [4]. Don't mix syntaxes in one request [12]. The longer list from the hosted documentation (`(gasps)`, `(whispers)`, `(sobs)`, `(pause)`…, there in the form `(sighs)`, `(laughs)`) applies to the multilingual model — **unconfirmed in our model**; risk that the tag gets read aloud [12][16].
- **Square brackets in English text** — don't use them (the model prepends an internal speaker prefix `[S0]`; the effect of your own `[...]` is unknown) [5] (code; unconfirmed). The "[Voice: …]" format from one review is not documented by the vendor [17] (community, doubtful).
- **Weights, negative, JSON** — don't exist. Numbers and abbreviations: the documentation is silent — spell them out in words (unconfirmed, as a precaution).
- **Text length:** generation limit about **120 s of speech**, in practice less (context budget, especially with a long sample) — leave a margin [9] (official). Split longer passages at paragraph/sentence boundaries; the vendor advises keeping coherent passages together, not chopping them into single sentences [9].

## Prompt skeleton
Voice design (no sample):
```
instruction (EN): [role/situation]. [gender], [age], [accent or "neutral accent"]. [1–2 texture features], [pitch/register]. [habitual pace and articulation]; [emotional centre].
text (EN): [sentence], [pause via comma/ellipsis]… {(sigh)} [sentence].
CFG: 4 (README recommendation; weaker: 2–3)
```
Direction (with a sample):
```
sample: [clean speech of one person, no music] + transcript: [word for word]
instruction (EN): [intention/situation] + [emotion with intensity] + [rhythm/breath/physical state]{; at the word '[word]', [change]}.
text (EN): [...]
CFG: 4 (README recommendation; gentler: 1.5–3)
```
Pure clone: sample + transcript, **empty instruction**, CFG 1.0.

## What works
- **A role description instead of a list of adjectives** — the vendor's benchmark scores "Role Fit": how convincingly the voice realises the whole described role [15] (official).
- **A change mid-line:** point to a trigger word: "At the word 'Wait', suddenly shift to terrified, breathless alarm" [7] (official). Vendor's evaluation: what counts is the initial state, the point of change and the end state [16].
- **Physical state through audible symptoms:** "heavily out of breath and gasping", trembling, fatigue, stuttering — the benchmark requires concrete markers, not a general emotion [7][16] (official).
- **Precise emotional nuance** ("restrained", "conflicted", "resentful") — scored separately from the general emotion [16] (official).
- **English accent with a stated degree** ("a gentle Southern lilt", "Japanese-accented English") [7][16] (official).
- **A series of lines in one voice:** design the voice → save the result → use it as the sample (with an exact transcript) for all subsequent lines; same parameters; join with 0.2–0.3 s of silence and match loudness [9][14] (official). The vendor normalises samples to −18 LUFS and uses a clip of up to 30 s ending on a complete sentence [9][14] (official, hosted version).
- **Sample:** clean, one person, no background and no loops, min. 3 s; a tester: 6 s gave a stable timbre [4][14][17]. Optimal length for the local model — not established.
- **Several seeds** — with rare defects, one attempt isn't enough [8] (community).

## Biases and pitfalls
- **Polish (or any non-EN/ZH) text** → the model doesn't support it; don't try "text in the participant's language with an English instruction" [1][4].
- **Any instruction with a clone** (even "Speak clearly and naturally.") turns the clone into direction and may change the sample's delivery [1][8].
- **Contradiction between sample and instruction** (e.g. a female sample, "deep male voice") is already Direction in conflict — the vendor attributed such bad results to inconsistent input [8] (official).
- **An inaccurate transcript** (e.g. the sample repeats a sentence and the transcript doesn't) spoils the result [8] (official).
- **Cross-lingual cloning** (a sample in a language other than the EN/ZH text) — a reported "collapse" of the output [8] (community); keep the sample in English for English text.
- **Breeze → OmniVoice chain (voice from a description, then Polish or another language):** OmniVoice carries the sample's accent over to the other language, so an English sample will give Polish (or other speech) with an English accent [18] (official OmniVoice); this chain hasn't been tested in the Studio yet [19] (our configuration).
- **Sibilants and bandwidth:** a tester heard harsh "s/t" and a lack of "air" (24 kHz), loudness about −18 LUFS — to be corrected in editing [17] (community).

## Beyond photorealism
- **Non-human and stylised voices can be described** — the vendor's benchmark includes e.g. "Non-human, mechanical-spectral. Low engine thrum, metallic distorted whisper.", "Booming resonant, massive mechanical scale.", creatures, characters from animation and comics [7][15] (official). This is the main route to "non-photorealistic" speech in this model.
- **Speaking conventions:** archaic narrator, rhythmic fairy-tale storyteller, recitation, hypnotic rhythm ("hypnotic and persuasive rhythm"), theatricality [7] (official).
- **Whisper, shout, breathlessness, crying** — as a Direction instruction (categories: acoustic attributes, physiological state) [16] (official).
- **Medium texture (tape, radio, telephone, reverb)** — undocumented; don't promise it. If the piece bible wants it: the prompt describes the voice, and the texture goes to the SFX area/editing [7][16].
- Singing: undocumented for the open model (`(singing)` only in the hosted list) [12] — unconfirmed.

## Motion / time / sound
- Length = text length × pace given in the instruction ("slowly", "brisk pace"); the Studio has no length or tempo field [1][4].
- Pauses: punctuation and the instruction ("emotional pauses", "measured pauses") [10][11] (official); the `(pause)` tag is unconfirmed in this model [12]. Exact silences — in editing.
- Max. about 120 s per generation, realistically less [9]. Output: 24 kHz mono WAV [2][4].
- Dialogue: one line (one voice) per request, joined in editing [13] (official, hosted).

## Check before sending
- [ ] Text in English (or Chinese), instruction in the same language; no words in other languages (e.g. Polish), or spelled phonetically.
- [ ] Mode is clear: Design (instruction = voice description) / Direction (sample + direction) / pure clone (empty instruction, CFG 1.0).
- [ ] Description: role + base voice + 1–2 texture features + pace + emotional centre, about 150–500 characters, no contradictions.
- [ ] Direction: 2–3 decisions, no identity change; a mid-line change via "at the word '…'".
- [ ] Events only `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)`; no `[...]` in English text.
- [ ] Sample with an exact transcript (both fields or neither); CFG 4 for description/direction (README recommendation), 1.0 with an empty instruction.
- [ ] Text under about 1–1.5 min of speech; several seeds.

## Sources
[1] Studio: `modele/mowa/breeze-tts-2.yaml` — our configuration
[2] Studio: `studio/backends/http.py` (empty fields are not sent), `studio/workflow.py` (seed, field values) — our configuration
[3] Breeze tests and API — own notes (unpublished) — our configuration
[4] breezeblue-ai/breeze-tts README (commit 58ec70c, the version on the Spark) — https://github.com/breezeblue-ai/breeze-tts — official
[5] breeze-tts, template and API code — https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/templates.py , https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/api.py — official (code)
[6] Hugging Face — BreezeBlue/Breeze-TTS-2 — https://huggingface.co/BreezeBlue/Breeze-TTS-2 — official
[7] BreezeBlue — Introducing Breeze TTS 2 (Design/Direction examples) — https://breezeblue.ai/breeze-tts-2 — official
[8] Issue #14 — defects with certain seeds; vendor's reply: pure clone without instruction and CFG 1, sample/instruction conflict — https://github.com/breezeblue-ai/breeze-tts/issues/14 — community / official (vendor's reply)
[9] Issue #25 — long texts (~120 s), voice consistency, joining fragments — https://github.com/breezeblue-ai/breeze-tts/issues/25 — official (vendor's reply)
[10] BreezeBlue Docs — Voice instruction prompting — https://docs.breezeblue.ai/guides/voice-instruction-prompting — official (hosted service)
[11] BreezeBlue Docs — Voice Design prompting — https://docs.breezeblue.ai/guides/voice-design-prompting — official (hosted service)
[12] BreezeBlue Docs — Audio tags — https://docs.breezeblue.ai/guides/audio-tags — official (hosted service, multilingual model)
[13] BreezeBlue Docs — Text to Speech (breeze-tts-2 vs multilingual models, dialogues) — https://docs.breezeblue.ai/guides/text-to-speech — official (hosted service)
[14] BreezeBlue Docs — Voice clone (sample: min. 3 s, clip up to 30 s, −18 LUFS) — https://docs.breezeblue.ai/guides/voice-clone — official (hosted service)
[15] TTS Voice Design Benchmark (set of 1000 descriptions) — https://huggingface.co/datasets/BreezeBlue/TTS-Voice-Design-Benchmark , https://github.com/breezeblue-ai/tts-voice-design-benchmark — official
[16] TTS Voice Direction Benchmark (categories: emotion, accent, physical state, variation, events) — https://github.com/breezeblue-ai/TTS-Voice-Direction-Benchmark — official
[17] CrePal — Breeze TTS 2 Review for AI Video Voiceovers — https://crepal.ai/blog/?p=9183 — community (single review)
[18] k2-fsa/OmniVoice README (accent in cross-lingual cloning) — https://github.com/k2-fsa/OmniVoice — official
[19] Plan: test of the Breeze → OmniVoice clone chain — own notes (unpublished) — our configuration
[20] Channelers, "Ludzie" voices (ElevenLabs v3) — own notes (unpublished), `ludzie_matryca.md` — author's experience (different model)
[21] "Speech" medium template — `prompty/media/mowa.md` — our configuration
