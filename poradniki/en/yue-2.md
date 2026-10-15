# YuE 2 — how to prompt

## How the model listens
YuE 2 (3B) is by nature a **song model**: from a style description and lyrics it makes a whole piece with vocals and accompaniment, with an intro–verse–chorus–bridge–outro structure. Two fields: **style** and **lyrics**. It also has a **cover** mode: it reads the melody from a recording (as a score) and then generates a piece with a new style and lyrics.

## Structure
- **Style:** in English, on one line, comma-separated, short (about 15–35 words). Order: language, genre, vocal character, tempo, instruments, musical features. Example from the documentation: "English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM". Put tempo (BPM) and key in the style — there are no separate fields for them.
- **Lyrics:** only the words to be sung, with section tags `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` — each tag on its own line, a blank line between sections. Musical instructions go in the style only.
- **No bracketed stage directions in the lyrics** (e.g. "(instrumental theme)", "(guitar solo)") — text in brackets may get sung.
- **Instrumental** (according to the official YuE2 recipe): the style starts with "Instrumental," and ends with "no vocals, no singing, no choir, no spoken words."; in the lyrics field **only section tags, with no words or brackets at all** (e.g. the Studio default). The official recipe additionally moves the melody from the vocal part to an instrument — the Studio doesn't do that, and even officially the absence of vocals isn't guaranteed. **Listen to the result** — if there's a voice, change the seed.

## What it's sensitive to / pitfalls
- Don't put style tags, BPM, chords, emoji or formatting into the lyrics.
- **Token budget:** a long prompt shortens the piece; when the budget runs out, the recording can cut off mid-phrase.
- Cover works best when the new lyrics have similar phrasing and syllable count to the original, and the sections go in the same order as in the recording. The style describes the target sound, not the original; the recording carries over only the melody (not the voice or the sound).
- Polish is not officially supported (documented: English, Chinese) — if you're writing in another language, do a short test before a long piece.

## Example (structure)
Instrumental:
- Style: "Instrumental, slow cinematic folk, nylon guitar leading the melody, cello and soft hand percussion accompaniment, D minor, 70 BPM, a quiet opening that grows and fades out, intimate room sound, no vocals, no singing, no choir, no spoken words."
- Lyrics (tags only, no words):
```
[Intro]

[Verse]

[Chorus]

[Outro]
```

## Parameters that really change the result
- **Max length** — an upper limit, the piece may end earlier (60 s by default, 120 s in cover; set it no lower than the length of the recording). Too low cuts the piece off mid-phrase.
- **Seed** — shared by the score and the sound; keep it fixed when comparing styles.
- The planning mode is set by the Studio: "YuE 2" = full (melody and chords), "YuE 2 · cover" = melody (melody from the recording, freer accompaniment).

## Sources (accessed 2026-10-05)
- ComfyUI — YuE2 Music Generation Guide: https://docs.comfy.org/tutorials/audio/yue2/yue2
- YuE — generation docs: https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md
- YuE2 — instrumental skill (official recipe): https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental
- ComfyUI — YuE2 cover template: https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json
