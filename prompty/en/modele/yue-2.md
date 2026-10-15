<!-- Model card for the promptmaker. modele: yue-2, yue-2-cover -->
# YuE 2 (YuE2-3B, m-a-p / HKUST, 09.2026) — text to music and cover from a recording

## What it is and what it's good for
- **A song model** (lyrics-to-song), 3B, AR–NAR architecture with flow matching. It first writes a **score in ABC notation** (melody + chords), then turns it into music tokens and 48 kHz stereo audio [4][5] (official).
- Planning modes: **full** (melody + chords; default for new pieces), **melody** (melody only, freer accompaniment; recommended for covers), **off** (no score) [4][5] (official). Studio: "YuE 2" = full with ABC planning; "YuE 2 · cover" = melody with the score transcribed from the recording [1][2] (our configuration).
- **Cover** = recording → SheetSage2 → melody in ABC → YuE2 with **a new style and new lyrics**. The recording is **not** audio conditioning: it does not carry over timbre, voice or mix, only the melody [6][9] (official).
- Strengths: song form, arrangements "often convincing", close to human production (EN, FR, PT-BR, ID) [13] (community); the authors: competitive with Suno v5/v6 on WildSongBench (authors' own measurement) [4] (official).
- **What it does NOT do well:**
  - **instrumental pieces "out of the box"**: the official instrumental recipe moves the notes of the Vocal part into the Ins part **before** rendering — Studio does **not** do this [7] (official), [2] (our configuration) → risk of voice/vocalizing (see pitfalls);
  - vocals: in almost every language "recognizably synthetic" [13] (community); pronunciation (PER) worse than Suno v6, vowels need checking by ear [14] (community);
  - **Polish (and most other languages) — no official support**: officially documented are EN and ZH (ComfyUI also lists Japanese) [9] (official); practitioners: demos in EN/ZH/JA/ES, "other languages may work" [14]; MindStudio lists Polish among tested languages without rating its quality [13] (community);
  - no "audio reference" input, no BPM, no negative, no phoneme alignment [5] (official).

## What the participant sets in Studio
**YuE 2 (text to music)** [1][2] (our configuration):
| Field | Values | Where it goes / effect |
|---|---|---|
| **style** | text | `style` → both the score planner (ABC) and the generator; in the model prompt this is the `[Tags]` section [2][10] |
| **lyrics / structure** | text; default `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` | `lyrics` → the `[Lyrics]` section [2][10] |
| **max length (s)** | 10–300, default 60 | upper limit; the piece may end earlier [9] |
| **seed** | number | shared by the score and the audio [2] |

**YuE 2 · cover from a recording** [1][3] (our configuration):
| Field | Values | Where it goes / effect |
|---|---|---|
| **recording (melody)** | audio file, required | SheetSage2 in `melody` mode → ABC (melody only) [3][11] |
| **style** | text | the target sound (not the original's!) [6] |
| **lyrics / structure** | text; default as above | lyrics to be sung to the transcribed melody [6] |
| **max length (s)** | 10–360, default 120 | upper limit [9] |
| **seed** | number | |

- Fixed: score — temperature 0.7, top_p 0.9, top_k 30, max 8192 ABC tokens; music — temperature 1, top_p 0.95, top_k 100, repetition 1.2; CFG 1.0 (= no guidance); render 32 steps [2][3] (our configuration) — the default values of the ComfyUI nodes [11] (official).
- **The participant does not see or edit the score (ABC) in Studio** — although the model allows it [4] (official), [1] (our configuration).
- **No negative**; at CFG 1.0 the negative branch is not computed [10] (ComfyUI code).

## Prompt format
- **Style: one line, comma-separated descriptors, in English.** Order from the official ComfyUI guide: **Language + Genre + Vocal character + Tempo + Instruments + Musical features** [9] (official). Official examples:
  - "English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM" [5] (official);
  - "Instrumental, expressive chamber string ensemble, lyrical violin melody, warm viola and cello accompaniment, G major, 96 BPM, a repeated opening phrase followed by a short gentle ending, natural concert hall acoustics, no vocals, no singing, no choir, no spoken words." [7] (official).
- **Tempo, key (and meter) go in the style** — there are no separate fields; the score records tempo and meter, and the style should describe them consistently [5] (official).
- **Keep the style short**: a long prompt automatically **reduces the length budget** (context of 24,576 tokens = prompt + score + music at 25 tokens/s) [9][10] (official). Official styles are ~15–35 words.
- **Lyrics: only what is to be sung**, + section tags in square brackets, each on its own line, **a blank line between sections** [5][9] (official). Musical instructions go in the style only [9].
- **Tags — what is documented for YuE2:**
  - guides: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` [9] (official);
  - in the official instrumental code: planning with `[Intro]`, `[Verse]`, `[Chorus]`, `[Outro]`, and the final tags come from the section names in the score (`% verse`, `% chorus`, `% bridge`, `% interlude` → `[Verse]`, `[Chorus]`, `[Bridge]`, `[Interlude]`) [7][8] (official);
  - `[Instrumental]` and `[Solo]` (Studio defaults) **do not appear in the YuE2 documentation** — they work technically (Studio API test) [12] (our configuration), but what they mean to the model is unconfirmed.
- **Parenthetical stage directions in the lyrics** (e.g. "(instrumental theme)") — no: the lyrics hold only words to be sung [9], and for an instrumental the lyrics must officially be **empty or tags only** [7] (official). Text in parentheses may get sung (inference).
- **Mind the versions:** YuE (v1, 2025; separate 7B + 1B models, different pipeline) is a different model — do not use v1 guides [15] (official). Everything here applies to YuE2-3B.

## Prompt skeleton
Song — style:
```
[Language: English / Polish / …], [genre], [voice: gender, timbre, delivery], [N BPM], [key if it matters], [2–4 instruments], [melody/phrasing feature], [space/recording]
```
Song — lyrics:
```
[Verse]
[line]
[line]

[Chorus]
[line]
[line]

[Bridge]
[line]

[Outro]
[line]
```
Instrumental — style (official pattern for the opening and closing):
```
Instrumental, [genre/texture], [lead instrument + role], [accompaniment], [key], [N BPM], [course: how it starts and ends], [space/recording], no vocals, no singing, no choir, no spoken words.
```
Instrumental — lyrics: tags only (e.g. the Studio defaults or `[Intro]` / `[Verse]` / `[Interlude]` / `[Outro]`), no words at all.

## What works
- **Style and lyrics kept separate** — style = sound, lyrics = text + sections [5][9] (official).
- **Language at the start of the style** ("English, …") — all official song examples look like this [5][9] (official). For other languages: "Polish, …" etc. by analogy (unconfirmed).
- **Exclusions as a list at the end of the style** ("no guitar", "no vocals") — the official jazz style example contains "no guitar", the instrumental recipe four "no …" items [7][8] (official).
- **A short style paragraph beats a pile of tags** [14] (community).
- **A fixed seed** when comparing style changes; the same seed on different hardware/version may give a different result [4][8] (official).
- **Cover**: simplest is to keep the original lyrics and change only the style; for a stronger reinterpretation, change both [6] (official).
- **Changing the language of the lyrics in a cover**: adapt for singing (syllables, stresses, long vowels on long notes, breaths), do not translate word for word [8] (official).

## Biases and pitfalls
- **An instrumental sometimes gets sung.** The model is song-oriented by nature; the official instrumental works by moving the melody from the Vocal part to Ins, and even so the authors write that it "does not guarantee the absence of voice" [7] (official). Studio lacks this step [2] → **always start the style with "Instrumental," and end it with "no vocals, no singing, no choir, no spoken words."** [7], lyrics with no words; listen back; if there is voice, change the seed. Whether YuE instrumentals in Studio stay voice-free — still to be checked by ear [12] (our configuration).
- **Length budget**: a style/lyrics that are too long shorten the piece; a "max length" that is too low cuts it off mid-phrase [9] (official). Length is set mainly by the score and the lyrics — short lyrics = short piece [9] (official).
- **Pronunciation** — check every version; vowels and phrasing "require a human ear" [14] (community). Undocumented language (e.g. Polish) → a short test before a long piece.
- **Deviations from the score**: exact realization of notes and durations is not guaranteed [7][8] (official).
- **Weak in Hindi/Urdu** [13] (community) — a sign that languages outside the main training data come out worse (inference).

## Cover from a recording — rules
- **The style describes the target sound, not the original** [6] (official).
- **New lyrics close to the phrasing and syllable count of the original** — better fit to the melody [6][9] (official). Sections and lyric order match the order in the recording [6][16] (official).
- **Recording**: transcription errors carry over into the cover [16] (official) — pick a passage with a clear, single melodic line (inference). SheetSage2 in melody mode takes the vocal melody or the leading instrumental melody [8] (official).
- **Max length ≥ length of the melody from the recording** — the score covers the whole recording; too low a limit will cut the piece off (inference from [9]). Default 120 s; the official ComfyUI template uses 360 [11] (official).
- **Instrumental cover**: officially it also requires the Vocal → Ins transfer [17] (official) — Studio doesn't have it, so a melody that was sung in the original will most likely come back as voice/vocalizing (inference). If the participant wants an instrumental from a melody — warn them and listen back together.
- A cover does not keep the performer's voice or the waveform of the recording; it is a new realization of the same melody [5][17] (official).

## Beyond photorealism (in music: beyond convention — texture, tape, lo-fi, abstraction)
- The YuE2 documentation **does not describe** lo-fi, tape or abstract styles. The only official vocabulary for space: "natural concert hall acoustics", "spacious modern harmony" [7][8] (official).
- Texture/medium descriptions ("tape-saturated", "lo-fi home recording", "vinyl crackle") — unconfirmed; if needed, put them briefly at the end of the style and compare with a version without them (same seed).
- For abstraction, drones and melody-less textures MiniMax Music 3 is a better fit (rich official ambient patterns) — YuE2 always plans **melody and chords** [4][5] (official).
- Its strength for "form research": the same melody in different styles (cover), or the same song with different harmony — that's what the model is built for [4] (official); in Studio only via cover and style changes.

## Movement / time / sound
- **Form** = section tags + score; tempo and meter in the style (e.g. "88 BPM") [5][9] (official).
- **Length**: "max length" is a ceiling; YuE2 ends the piece on its own when the plan is finished [9] (official). For 30–60 s: one verse + chorus or a short poem.
- **A sung poem**: the text verbatim under `[Verse]`/`[Chorus]`; long lines can be broken at pauses (with the participant's consent). Recitation / spoken word — not in the YuE2 documentation (unknown).
- Output: FLAC 48 kHz stereo [1] (our configuration).

## Check before sending
- [ ] Style: one line in English, starts with the language (song) or "Instrumental," (instrumental); tempo in BPM in the style.
- [ ] Instrumental: the style ends with "no vocals, no singing, no choir, no spoken words."; the lyrics contain **no** words or parentheses — tags only.
- [ ] Song: the lyrics contain only the text to be sung + `[Verse]`/`[Chorus]`/`[Bridge]`/`[Outro]` tags on their own lines, blank lines between sections.
- [ ] Style short (about 15–35 words), no contradictions.
- [ ] Cover: style = target sound; lyrics with a similar syllable count and section order; max length ≥ length of the recording.
- [ ] Singing in an undocumented language (e.g. the participant's language, if not English/Chinese) → warn that it's undocumented; suggest a short test.
- [ ] Remind them to listen back (voice in an instrumental, pronunciation) and to try 2–3 seeds.

## Sources
[1] Studio — `modele/muzyka/yue-2.yaml` and `yue-2-cover.yaml` — modele/muzyka/yue-2.yaml, modele/muzyka/yue-2-cover.yaml — our configuration
[2] Studio — workflow `workflows/muzyka/yue2_tekst-na-muzyke.api.json` — workflows/muzyka/yue2_tekst-na-muzyke.api.json — our configuration
[3] Studio — workflow `workflows/muzyka/yue2_cover-z-nagrania.api.json` — workflows/muzyka/yue2_cover-z-nagrania.api.json — our configuration
[4] YuE2 — README (full/melody/off modes, cover, score editing) — https://github.com/multimodal-art-projection/YuE/blob/main/README.md and the card https://huggingface.co/m-a-p/YuE2-3B — official
[5] YuE2 — Generation guide + example `examples/song.json` + the "generation-and-covers" reference (request fields, no BPM/negative, CFG) — https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/generation-and-covers.md — official
[6] Comfy-Org — "audio_yue2_music_cover" template (notes: style, lyrics, syllables, how the cover works) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json — official
[7] YuE2 — instrumental skill (SKILL.md, README, `assets/example-style.txt`, `scripts/instrumental.py`) — https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental — official
[8] YuE2 — "yue2-music" skill (SKILL.md, references/abc-editing.md: section names in the score, lyric adaptation) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/SKILL.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/abc-editing.md — official
[9] ComfyUI Docs — "YuE2 Music Generation Guide" + "audio_yue2_text2music" template (order of style elements, length budget, languages) — https://docs.comfy.org/tutorials/audio/yue2/yue2 , https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_text2music.json — official
[10] ComfyUI — YuE2 encoder code (`[Tags]`/`[Lyrics]`, context 24,576, 25 tokens/s, CFG) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/yue2.py — official (implementation)
[11] ComfyUI Docs — YuE2GenerateABC, YuE2GenerateMusic, SheetSage2AudioToABC nodes — https://docs.comfy.org/built-in-nodes/YuE2GenerateABC.md , https://docs.comfy.org/built-in-nodes/YuE2GenerateMusic.md , https://docs.comfy.org/built-in-nodes/SheetSage2AudioToABC.md — official
[12] FSO — PROGRESS.md (5.10: API test; "whether YuE stays voice-free in instrumentals" — to be checked by ear) and docs/audio.md — own notes (unpublished) — our configuration
[13] MindStudio — "YuE2: How to Run This Open-Source Music Generation Model Locally" — https://www.mindstudio.ai/blog/yue2-open-music-generation-model — community
[14] YuE2 AI (unofficial service; notes on languages and pronunciation) — https://yue2ai.org/ — community
[15] YuE (v1) — project page — https://map-yue.github.io/ — official (previous version)
[16] YuE2 — "Cover a recording" — https://github.com/multimodal-art-projection/YuE/blob/main/docs/covers.md — official
[17] YuE2 — instrumental skill, cover (`references/cover.md`) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/instrumental/references/cover.md — official
