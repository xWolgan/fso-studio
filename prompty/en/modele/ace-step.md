<!-- Model card for the promptmaker. modele: ace-step-1-5-xl -->
# ACE-Step 1.5 XL sft (ACE Studio × StepFun, 2026)

## What it is and what it's good for
- A music model with two "brains": a **LM planner** (in the Studio Qwen 4B, `qwen_4b_ace15`) turns the description + lyrics into semantic codes (melody, arrangement, part of the timbre), and a **DiT** (here the **XL sft** variant, 4B, 50 steps, CFG 7) turns them into sound [4] (official), [2] (our configuration).
- The **sft** variant according to the authors: slower than turbo, "better at detail and at understanding the description", marginally less clean [4] (official). Studio: 30 s of music in about 20 s — the fastest of the three music models [3] (our configuration).
- Can do: songs with clear diction, instrumental pieces, 50+ singing languages (including **Polish** — the official examples include 3 songs in Polish) [6][7] (official). Our test: Polish diction **0.97** on sft (turbo only 0.60) [3] (our configuration).
- **What it does NOT do well:**
  - "slot-machine" results — highly dependent on seed and length; "coarse vocal synthesis without nuance"; weaker style fidelity in some genres [11] (official);
  - stiff, "grid-locked" rhythm, flat dynamics, little verse/chorus contrast, predictable melodies (XL test) [12] (community);
  - **Eno-style ambient**, early electronics "à la Kraftwerk" — a practitioner: "a failure", drift towards generic, "cheesy" library music [13] (community);
  - excluding instruments ("no guitar") works poorly; about half of the tracks lack variety, some generations are noise — one user's report [16] (community);
  - **fixed 4/4 time signature** in the Studio (see below) — 3/4 waltz, 6/8 unavailable [2] (our configuration).

## What the participant sets in the Studio
| Field | Values | Where it goes / effect on the prompt |
|---|---|---|
| **style (tags)** | text | `tags` = **caption**; goes to the LM and to the 0.6B text encoder **verbatim** [1][8] (our configuration / ComfyUI code) |
| **lyrics** | text, default `[Instrumental]` | `lyrics` — text + section tags; "a script in time" [1][4] |
| **length (s)** | 10–240, step 5, default 60 | both the latent length and `duration` for the LM (the LM generates 5 codes/s) [1][8] |
| **tempo (BPM)** (adv.) | 40–200, default **100** | `bpm` — **always sent** [1][2] |
| **key** (adv.) | text, default **"E minor"** | `keyscale` — **always sent** [1][2] |
| **singing language** (adv.) | en, pl, de, fr, es, it, ja, zh; default **en** | `language` — goes only to the lyrics text encoder [1][8] |
| **seed** | number | shared by LM and DiT [2] |

- Fixed in the workflow: time signature `4` (= 4/4), LM: cfg 2.0, temperature 0.85, top_p 0.9; DiT: 50 steps, CFG 7, euler/simple, shift 3 — as in the official ComfyUI template [2][9] (our configuration / official).
- **There is no negative prompt** (the DiT's negative branch is zeroed conditioning) [2] (our configuration).
- In ComfyUI the LM **does not rewrite the description** (only the official Gradio does): BPM, key, time signature and length go in as ready-made metadata in the `<think>` block, description and lyrics go through 1:1 [8] (ComfyUI code). What you write is what the model gets.
- **Consequence:** BPM 100 and E minor will always be sent, even if the participant doesn't touch them. The promptmaker **always provides** a BPM and key consistent with the description — a contradiction ("slow ballad" + 160 BPM) confuses the model [4] (official).

## Prompt format
- **Description (caption) in English.** All 200 official examples have the description in English — including songs in Polish/Chinese/Korean; the singing language is named in words in the description, e.g. "A clear female vocal delivers a melancholic melody in Polish" [7] (official).
- **Form:** the model accepts keywords, comma-separated tags or prose — "the format doesn't significantly matter" [4] (official). The official examples are **a paragraph of prose of 22–112 words (median ~31)** describing how the piece unfolds [7] (official). The Studio label "tags" doesn't enforce tags — prose is fine.
- **Description dimensions** (official table): genre, emotion/atmosphere, instruments, timbre texture (warm, crisp, muddy, airy, punchy, raw), era, production style (lo-fi, live recording, bedroom), vocals, rhythm, structure hints (building intro, fade-out ending) [4] (official).
- **Do NOT put BPM, key or time signature in the description** — there are separate fields for that [4] (official).
- **Key — format from the examples:** `C major`, `E minor`, `F# minor`, `Bb major` (letter + major/minor) [7] (official). Most stable: C, G, D, Am, Em; rare ones are sometimes ignored [4] (official).
- **BPM:** 60–180 works well; extremes are unstable. Roughly: slow 60–80, medium 90–120, fast 130–180 [4] (official). The model treats BPM as an anchor (you may get e.g. 118 instead of 120) [4].
- **Lyrics** — syntax [4][5][7] (official):
  - section tag in square brackets, **on its own line**: `[Intro]`, `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]`; dynamic: `[Build]`, `[Drop]`, `[Breakdown]`; instrumental: `[Instrumental]`, `[Guitar Solo]`, `[Piano Interlude]`, `[Instrumental Break]`; special: `[Fade Out]`, `[Silence]`;
  - **one modifier after a dash**: `[Chorus - anthemic]`, `[Bridge - whispered]`, `[Intro - piano]`. Officially one is recommended; stacking modifiers (example from the guide: five at once) = risk that the model **sings the content of the tag** [4];
  - vocal tags (on a separate line): `[whispered]`, `[falsetto]`, `[raspy vocal]`, `[spoken word]`, `[harmonies]`, `[ad-lib]` [4];
  - **a blank line between sections** [4][5];
  - `(text in brackets)` = backing vocals/echo; **CAPITAL LETTERS** = louder, shouting [4][5];
  - stretching vowels ("Feeeling") — unstable, better avoid [4].
- Weights `(word:1.2)`, JSON or a negative — absent from the documentation; don't use them.
- **Watch the versions:** this is **ACE-Step 1.5** (2026). Guides for ACE-Step v1 (3.5B, 2025) have a different pipeline — don't mix them [10] (official).

## Prompt skeleton
Description ("style" field), in English, 1 paragraph ~30–80 words:
```
[genre/tradition or its absence] with [main instrument/source] and [2–3 secondary instruments]. [Vocals: none → "Instrumental, no vocals." / present → gender, timbre, delivery, "in Polish"]. [Progression: how it starts → what builds/disappears → how it ends]. [Texture and recording: e.g. warm / raw / lo-fi / close-miked / room ambience / tape saturation]. [Mood — briefly, at the end].
```
Separate fields: `BPM: [number consistent with the description]`, `key: [X major/minor]`, `length: [s]`, `language: [pl/en…]`.

Lyrics — song:
```
[Intro - (one instrument from the description)]

[Verse 1]
[line of 6–10 syllables]
[line of 6–10 syllables]

[Chorus - (one word of character)]
[line]
[line]

[Outro - fade out]
```
Lyrics — instrumental piece (version with a progression):
```
[Intro - (instrument/texture)]

[Main Theme - (instrument)]

[Breakdown - (what remains)]

[Outro - fade out]
```

## What works
- **Specifics instead of adjectives**: "sad piano ballad with female breathy vocal" > "a sad song" [4] (official). Combine several dimensions (style + emotion + instruments + timbre) [4].
- **Description = "overall portrait", lyrics = "screenplay"** — they should tell the same story: instruments in the description ↔ solo tags; emotion in the description ↔ energy tags [4] (official). Example of a conflict: description "violin solo", in the lyrics `[Guitar Solo - electric]` → worse result [4].
- **Turn contradictory styles into development over time**: "Start with soft strings, middle becomes noisy dynamic rock, end turns to …" instead of mixing them at once [4] (official).
- **Repeating a word strengthens** an element in a mixed style [4] (official).
- **Amount of detail = amount of control**: less description → more surprises, more description → less freedom [4] (official).
- **Syllables**: 6–10 per line; corresponding verse lines ±1–2 syllables — the model fits syllables to beats [4][5] (official).
- **One metaphor per song**, no piling up of adjectives ("neon skies, electric hearts") — against "AI-sounding" lyrics [4] (official). Applies to lyrics written from scratch; the participant's poem stays verbatim.
- **Structure tags even without words** give an energy map [5] (official) — but for instrumentals see the pitfalls below.
- **Write for the rhythm**: short phrases, repetitions, words with clear stress are more stable than long sentences; change the description first, then one lyrics section at a time [15] (community).
- **Generate several seeds** and choose; when tuning one parameter keep the seed fixed [4][5] (official).
- Official ComfyUI XL sft template: description as prose with production details ("warm and analog-sounding, with subtle tape saturation and a slight room ambience"), tags with an instrument description `[Intro – Rhodes piano and brushed drums]` [9] (official).

## Biases and pitfalls
- **Default BPM 100 / E minor** — if they don't fit the description, the model gets contradictory signals [1][4]. Always set them.
- **4/4 time hard-wired** — don't promise a waltz or 6/8; "waltz" in the description at 4/4 is a conflict (inferred from [2][4]).
- **Instrumentals leak vocalisation:** bare `[Verse]`/`[Chorus]` tags without words can produce humming/vocalising [14] (community). Safer: `[Instrumental]` (official [4]) or tags naming an instrument (`[Main Theme - piano]`), and in the description a clear "instrumental, no vocals" (at the start or end of the description) [14] (community).
- Community: **words suggesting a song** ("pop", "ballad", "song") in an instrumental pull towards vocals; with an orchestra add "no choir" [14] (community). The same advice: an empty lyrics field is sometimes more reliable than tags — in the Studio the field defaults to `[Instrumental]`; whether an empty one goes through — untested.
- Singing language in an instrumental: the Studio has no "instrumental/unknown" option; the language goes only to the lyrics text encoder [8] — with `[Instrumental]` leave the default (effect unconfirmed).
- **Too many modifiers in a tag** → sung as lyrics [4] (official).
- **Rare keys, extreme BPM, long pieces** (>4 min) — less stable; 30–60 s and 2–4 min are the most stable [4] (official). The Studio stops at 240 s anyway.
- **Gacha**: changing one word gives a completely different piece — hard to iterate in small steps [13] (community), [11] (official).
- **Artist names** are allowed by the authors ("reminiscent of …") [4], but the Studio's medium template says to describe what is taken from them — stick to the template.
- Weak in some genres (e.g. Chinese rap) [11] (official); ambient/experimental — see above [13].

## Beyond photorealism (in music: beyond convention — texture, tape, lo-fi, abstraction)
- Working production vocabulary from the official tables: **lo-fi, live recording, bedroom pop, studio-polished, high-fidelity**; timbre: **warm, crisp, muddy, airy, punchy, lush, raw** — "they affect the mix and timbre" [4] (official).
- **Tape/analog**: "subtle tape saturation", "analog-sounding", "slight room ambience" — from the official template [9] (official).
- **Era of the sound** as shorthand: "80s synth-pop", "vintage soul", "90s grunge" [4] (official) — for an archival feel name the era and the medium.
- **Abstraction / ambient / drones**: poorly documented and unreliable in practice [13] (community). If the participant wants abstraction, consider MiniMax Music 3 or short tests with several seeds; describe concrete sound sources (e.g. "bowed cymbal, sine drones, field recording of wind"), not "ambient" in general (unconfirmed).
- Unusual ("long-tail") instruments are better understood by a larger LM — the Studio uses the largest, 4B [4] (official), [2] (our configuration).

## Motion / time / sound
- **Length** is set by the "length" field (the LM gets exactly that many seconds) [8]. The model "may deviate slightly" [4].
- **Amount of lyrics for the length:** official examples of 124–240 s typically have an intro, 2–3 verses, choruses, a bridge, an outro [7] (official). For 30–60 s give one verse and a chorus, or just the text of a short poem (ratio unconfirmed — listen to check it isn't rushing).
- **Progression over time** — write it twice, consistently: in the description in words ("builds slowly, ends with a fade-out") and with tags in the lyrics (`[Build]`, `[Breakdown]`, `[Outro - fade out]`) [4] (official).
- **A poem spoken over music:** the `[spoken word]` tag ("rap/recitation") [4] (official); in the description "spoken-word delivery over …". Effectiveness for recitation in Polish (or the participant's language) — untested.
- **A poem sung in Polish (or the participant's language):** enter the text verbatim, set the language (e.g. `pl`), in the description "vocal … in Polish" (or the relevant language) [7] (official). With the participant's consent you can break long lines of the poem into shorter ones at natural pauses (6–10 syllables) [4] — don't change the words.

## Check before sending
- [ ] Description in English, no BPM/key/time signature in the text.
- [ ] BPM and key fields set and **consistent** with the description (e.g. a slow piece ≠ the default 100 BPM).
- [ ] Nothing requires a time signature other than 4/4.
- [ ] Instrumental: "instrumental, no vocals" in the description (+"no choir" with an orchestra); in the lyrics `[Instrumental]` or tags with an instrument — not bare `[Verse]`/`[Chorus]`.
- [ ] Song: each tag on its own line, max one modifier, a blank line between sections; singing language set in the field and named in the description.
- [ ] Instruments/energy in the tags don't contradict the description.
- [ ] Amount of lyrics matches the length.
- [ ] No artist names; no weights or negative.
- [ ] Suggest 2–3 seeds instead of rewriting the prompt after the first result.

## Sources
[1] Studio — `modele/muzyka/ace-step-1-5-xl.yaml` — modele/muzyka/ace-step-1-5-xl.yaml — our configuration
[2] Studio — workflow `workflows/muzyka/ace_step_1_5_xl.api.json` — workflows/muzyka/ace_step_1_5_xl.api.json — our configuration
[3] Tests on the Spark (Polish diction sft 0.97 / turbo 0.60; 30 s in ~20 s) — own notes (unpublished) — our configuration
[4] ACE-Step 1.5 Ultimate Guide (Tutorial) — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md — official
[5] ACE-Step 1.5 — A Musician's Guide — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md — official
[6] ACE-Step 1.5 README (50+ languages, 10 s – 10 min) — https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md — official
[7] Official text2music examples (200 files; incl. example_27, example_40, example_41 in Polish) — https://github.com/ace-step/ACE-Step-1.5/tree/main/examples/text2music — official
[8] ComfyUI — ACE 1.5 encoder code (LM prompt templates, metadata in `<think>`, language) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/ace15.py — official (implementation)
[9] Comfy-Org — ACE-Step 1.5 XL sft workflow template — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_ace_step1_5_xl_sft.json — official
[10] ComfyUI Docs — ACE-Step v1.5 (and a separate v1 page) — https://docs.comfy.org/tutorials/audio/ace-step/ace-step-v1-5 — official
[11] ACE-Step 1.5 — project page, Limitations section — https://ace-step.github.io/ace-step-v1.5.github.io/ — official
[12] GitHub Issue #1114 "Technical Feedback on ACE-Step 1.5 XL" — https://github.com/ace-step/ACE-Step-1.5/issues/1114 — community
[13] "Release and test: Ace-Step 1.5" (a practitioner's test, ambient/Eno) — https://jurn.link/dazposer/index.php/2026/02/04/release-and-test-ace-step-1-5/ — community
[14] Z.Tools — "Instrumental prompts for ACE-Step: keeping the vocals out" — https://z.tools/blog/ace-step-instrumental-prompts — community
[15] Hacker News — "Ace-Step 1.5 prompt tips" — https://news.ycombinator.com/item?id=46948483 — community
[16] GitHub Discussion #1071 "What were you able to do with XL models…" (anecdotal user reports) — https://github.com/ace-step/ACE-Step-1.5/discussions/1071 — community
