<!-- Model card for the promptmaker. modele: minimax-music-3 -->
# MiniMax Music 3 (MiniMax, open weights 08.2026)

## What it is and what it's good for
- A hierarchical autoregressive model: a **Global LLM 8B** (initialized from Qwen3-8B) plans the long-range structure of the piece, a **Local LLM 0.6B** fills in acoustic detail, then flow matching + Flow-VAE. Conditioned on **song lyrics** and a **detailed description of the music**; pieces **up to 5 min**, coherent form (intro, verse, chorus, bridge, instrumental break, outro) [4] (official).
- The description is read **over time** — the model follows how the piece develops, not just the global style [4][6] (official). "The more specific, the closer" [6] (official).
- In Studio: the main model for **instrumental pieces** (a workshop priority); 30 s ≈ 93 s of compute (fast mode) [3] (our configuration).
- **What it does NOT do well:**
  - tempo, key, instrumentation and structure are **not guaranteed** — "guidance, not hard commands" [4] (official);
  - the instrumental layer can be **flat**, even when the description names specific instruments; dense, high parts and vocal layers "blur together"; it conveys genre energy poorly (e.g. stadium rock) [12] (community);
  - rock/metal and older acoustic sounds — mixed opinions, a "muddy" mix in dense arrangements; praised mainly for pop and electronic music [13] (community);
  - **Polish (and most other languages) — no data**: official demos only in English, Mandarin, Cantonese, French [7] (official); a practitioner: other languages are "less predictable" [11] (community).

## What the participant sets in Studio
| Field | Values | Where it goes / effect on the prompt |
|---|---|---|
| **description** | text | `caption` — the entire music description [1][2] (our configuration) |
| **lyrics / structure** | text; default `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` (each on its own line, blank lines between) | `lyrics` — section tags + any lyrics [1] |
| **max length (s)** | 10–300, step 10, default 60 | `max_duration` — **upper limit**; the model may end earlier [1][8] |
| **mode** | fast (INT8 encoder, ~1.5 min / 30 s) / quality (bf16, ~2.5 min / 30 s) | only quality/time, the prompt stays the same [1][3] |
| **seed** | number | a different version of the same prompt [1][6] |

- **No BPM / key fields** — you write tempo and key **into the description** [1] (our configuration), [4] (official).
- Fixed: CFG 1.7 (the model constant in ComfyUI is 1.5), top_k 50; diffusion 30 steps, euler; tiled decoding enabled [2] (our configuration), [9] (ComfyUI code).
- **There is no negative prompt** (zeroed conditioning) [2] (our configuration). Write exclusions in the description as facts ("no drums", "no vocals").
- Studio output: MP3 V0 [2]; the model is natively 32 kHz stereo [4] (official).

## Prompt format
- **Description in English.** The official "music-caption-rewriter" writes the description in English "unless the user explicitly wants another language" [5] (official); the entire library of 1000 reference descriptions is in English [5] (official).
- **Structure: three headings in this order** — `Global Metadata`, `Vocal Details`, `Arrangement` [4][5] (official). Studio hint: the description starts with "Global Metadata:" [1] (our configuration). The official ComfyUI template writes the heading with a colon and the content in the same paragraph, paragraphs separated by a blank line [10] (official); the MiniMax library — heading on its own line plus subfields [5] (official). Both variants are correct.
- **Subfields from the official library** (closest to the training data) [5][6] (official / community):
  - Global Metadata → `Basic Attributes:` (exactly in the form "bpm is 76. key is Bb, and scale is major. Genre / Subgenre."), `Global Emotional Progression:`, `Application Scenarios & Imagery:`, `Sonics & Production Profile:`;
  - Vocal Details → `Vocal Gender & Timbre:`, `Vocal Style:`, `Harmony/Backing Vocals:`, `Vocal FX:`;
  - Arrangement → `Instrument Lifecycle Description (Primary/Secondary Layering):` with "Primary: …" and "Secondary: …", `Groove & Foundation Progression:`, `Embellishments, Textures & Spatial FX:`.
- **Description length: about 250–450 words** (the rewriter's default) [5] (official). Limit for the whole prompt: 5000 tokens [4][9] (official).
- **Markdown does nothing**: ComfyUI strips `#` headings, `-`/`*` bullets, bold, and collapses blank lines [9] (ComfyUI code). Write in plain sentences.
- **Lyrics / structure** — the official tag list: `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` [4][8] (official).
  - **Each tag on its own line**; text on the same line as a tag may get lost [6] (community).
  - Case doesn't matter — ComfyUI lowercases the tags anyway [9] (ComfyUI code).
  - **Only tags are structural commands**; lyrics carry only content and emotion. "Drums come in" written into the lyrics won't change the drums — that belongs in Arrangement [8][10] (official), [11] (community).
  - Repeat sections with plain tags (`[Verse]` … `[Verse]`) as in the official template [10]; numbering like `[Verse 1]` is community advice [11], effectiveness unconfirmed.
- Weights, JSON, negatives — not in the documentation; don't use them. The description field supports ComfyUI "dynamic prompts" [8] — avoid curly braces `{a|b}` (unconfirmed whether they work through the Studio API).

## Prompt skeleton
Description (in English, plain sentences, ~250–450 words):
```
Global Metadata
Basic Attributes: bpm is [number]. key is [note], and scale is [major/minor]. [Genre] / [Subgenre or texture].
Global Emotional Progression: [how it opens] → [where it builds / peaks] → [how it resolves, or doesn't].
Application Scenarios & Imagery: [the scene/image the music belongs to — from the bible, without quoting the poem].
Sonics & Production Profile: [stereo width, frequency range (dark/bright), dynamics (compressed/natural), space, medium/recording].

Vocal Details
[INSTRUMENTAL: The piece is fully instrumental, no vocals. The lead melodic role is carried by [instrument/texture].]
[SONG: Vocal Gender & Timbre: Singer A ([Male/Female]) … Vocal Style: … Harmony/Backing Vocals: … Vocal FX: …]

Arrangement
Instrument Lifecycle Description (Primary/Secondary Layering):
Primary: [backbone instrument, when it's present, how it changes].
Secondary: [what enters/leaves and when].
Groove & Foundation Progression: [pulse or its absence — e.g. no percussive groove, free time; how it thickens].
Embellishments, Textures & Spatial FX: [textures, noise, reverbs, transitions].
[Intro: … / Instrumental sections: … / Solo: … / Outro: … — one sentence for each tag used in the "lyrics" field]
```
Lyrics / structure — instrumental:
```
[Intro]

[Instrumental]

[Solo]

[Instrumental]

[Outro]
```
Lyrics — song: `[Verse]` + lines of lyrics, `[Chorus]` + lines, … — a tag always alone on its line, a blank line between sections [8][10].

## What works
- **The description as a timeline, not an equipment list**: for each section, write what enters, leaves, changes, builds [5][6] (official / community).
- **An energy arc told like a story** (tension, release, breathing room, climax) gives better form than a static description [6] (community).
- **Every tag from the "lyrics" field gets its own sentence in Arrangement** — a mismatch between tags and arrangement is the most common reason a piece doesn't hold its structure [11] (community); the official ComfyUI template describes "Intro: …, Verses: …, Instrumental sections: …, Bridge: …, Outro: …" [10] (official).
- **Application Scenarios & Imagery** — the scene the music belongs to anchors the mood better than adjectives [6] (community). Carry the image over from the piece bible here (without the poem's text — lyrics do not go into the description [5]).
- **Don't invent precision**: exact BPM/key only when really needed; otherwise a range or a word ("unhurried", "driving") [5][6] (official / community).
- **Keep exclusions and requirements consistent across the whole description** (instrumental, vocal gender, a banned instrument) — don't contradict them in later sections [5] (official).
- **Fusing two styles**: name both and write how they share the arrangement [6] (community). Words like emotional, epic, dark, cinematic are **modifiers, not genres** [5] (official).
- **Seed** for variants; a fixed seed when comparing a change to the description [8] (official).

## Biases and pitfalls
- **The reference library is songs**: among the 1000 official descriptions there isn't a single instrumental; Mandopop/C-pop, R&B, folk, pop-rock and ballads dominate [5] (official; index analysis). The model pulls toward **song form and the ballad** — an instrumental has to be stated explicitly.
- **Unspecified vocals** = the most common cause of drift: always fill in Vocal Details — for an instrumental, write that there are none and name the lead instrument [5] (official), [6] (community). Our practice: "No vocals. Fully instrumental." [3] (our configuration).
- **Too short a structure = too short a piece**: max length is a ceiling; the model ends when "the lyrics run out". A five-minute piece needs a full set of sections [6][11] (community). How many seconds the default 5 sections fill — unknown (check by ear); for longer pieces add `[Instrumental]`/`[Solo]`/`[Bridge]` and describe them in Arrangement.
- **Named instruments ≠ audible in the mix** [12] (community): don't cram in 8 instruments; 2–4 with clear Primary/Secondary roles.
- **Dense high layers blur together** [12] — with many layers, separate them in time (by section), not all at once.
- **Long pieces = long waits** (proportionally, ~93 s per 30 s in fast mode) [3] (our configuration) — work at 30–60 s for sketches.

## Beyond photorealism (in music: beyond convention — texture, tape, lo-fi, abstraction)
- **Lo-fi / tape / vinyl** — the official ComfyUI template: "muddy warm texture, heavy vinyl crackle, tape hiss and wow-flutter pitch wobble, low-passed dusty mix, soft-clipped drums, everything slightly detuned" [10] (official). Write this in `Sonics & Production Profile` and in Embellishments.
- **Music without a pulse** — official patterns: "There is no percussive groove or rhythmic foundation; the tempo is driven entirely by the rubato phrasing…", "relies entirely on free-time atmospheric progression" [5] (official).
- **Dark ambient / drones / textures** — official patterns: "low-frequency synthesizer drone… present continuously", "granular textures and wind-like noise sweeps", "continuous layer of ambient noise resembling underwater static or hydrophone recordings", "reverse reverb swells as transitional markers" [5] (official).
- **Space and frequency range** as a tool of form: "high frequencies significantly rolled off", "cavernous, aquatic spatial feel", "heavily compressed and saturated, wall-of-sound" [5] (official).
- **Archival feel**: name the medium and its flaws (vinyl, tape, wow & flutter, narrow bandwidth) instead of "old" [10] (official — vocabulary from the template); effectiveness of "1930s radio" and the like is unconfirmed.
- Specific gear is rare in the library (pop dominates) — describe experimental instrumentation by sound and function, not by name alone (unconfirmed).

## Movement / time / sound
- **Time = tags + Arrangement**: tags define the sections, Arrangement says what happens in them [4][8] (official).
- **A section can change the local arrangement** (e.g. `[Solo]`) without changing the genre of the whole [5][6] (official / community).
- **Length**: set "max length" with headroom and choose the number of sections to match; the model ends the piece itself with an end token [6] (community), [8] (official).
- **A poem spoken over music**: the library has spoken-word patterns ("Cinematic Ambient / Spoken Word"): in Vocal Details "a deliberate, theatrical spoken-word delivery rather than singing… slow and measured, with distinct pauses" [5] (official). The poem's text → the "lyrics" field under `[Verse]` tags. Recitation in languages other than the demo ones (e.g. Polish) — untested.
- **A song in the participant's language** (if not one of the demo languages): no official support in the documentation [7]; if the participant wants it — a short 30 s test, listen for pronunciation (unconfirmed). Name the singing language in Vocal Details (e.g. "sung in Polish") — unconfirmed.

## Check before sending
- [ ] Description in English, three parts in the order Global Metadata → Vocal Details → Arrangement, plain sentences (no Markdown).
- [ ] Tempo and key in the description ("bpm is …. key is …, and scale is ….") — or deliberately in words, without false precision.
- [ ] Vocal Details filled in: instrumental → "fully instrumental, no vocals" + lead instrument.
- [ ] Each tag on its own line, only from the official list of 9; no musical instructions in the lyrics.
- [ ] Every tag used has a sentence in Arrangement; Arrangement reads like a timeline.
- [ ] Number of sections matches "max length".
- [ ] Requirements/exclusions don't contradict each other across parts of the description.
- [ ] No artist names (medium template), no `{|}`, no poem text in the description.

## Sources
[1] Studio — `modele/muzyka/minimax-music-3.yaml` — modele/muzyka/minimax-music-3.yaml — our configuration
[2] Studio — workflow `workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json` — workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json — our configuration
[3] Audio tests and recommendations (93 s / 30 s INT8; "No vocals. Fully instrumental.") — own notes (unpublished) — our configuration
[4] MiniMax-Music3 — README (architecture, tags, Structured Caption, limitations) — https://github.com/MiniMax-AI/MiniMax-Music3 (also https://huggingface.co/MiniMaxAI/MiniMax-Music3) — official
[5] MiniMax — "music-caption-rewriter" skill (SKILL.md, references/genre-router.md, indexes and 1000 templates, incl. dark-ambient-slowcore_0001, contemporary-classical-ambient-ballad_0001, cinematic-ambient-spoken-word_0001) — https://github.com/MiniMax-AI/MiniMax-Music3/tree/main/skills/music-caption-rewriter — official
[6] "Prompting MiniMax Music 3" — Hugging Face Space (multimodalart) — https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide — community (based on the official skill)
[7] MiniMax Music 3 — demo page (demo languages and genres) — https://minimax-ai.github.io/music3-demo/ — official
[8] ComfyUI Docs — MiniMax Music 3 (tutorial) and the MiniMaxMusic3TextEncode node — https://docs.comfy.org/tutorials/audio/minimax/minimax-music-3 and https://docs.comfy.org/built-in-nodes/MiniMaxMusic3TextEncode.md — official
[9] ComfyUI — code: prompt construction (`comfy/ldm/minimax_music/prompt.py`) and constants (`ar.py`: CFG 1.5, top_k 50, 5000 tokens, 9000 frames) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/ldm/minimax_music/prompt.py — official (implementation)
[10] Comfy-Org — official workflow template "audio_minimax_music_3" (sample lo-fi description and notes) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_minimax_music_3.json — official
[11] EarnGenix — "MiniMax Music 3 in ComfyUI: Generate a Full 5-Minute Song" — https://www.earngenix.com/workflows/minimax-music-3-comfyui — community
[12] MindStudio — "MiniMax Music 3: The Open-Weight AI Music Model, Explained" — https://www.mindstudio.ai/blog/minimax-music-3-open-weight — community
[13] AIReiter — "MiniMax Music 3.0 Review: API, Pricing & Local Setup" — https://aireiter.com/blog/minimax-music-3-0-review-api-pricing-local-setup — community
