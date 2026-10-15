# ACE-Step 1.5 XL — how to prompt

## How the model listens
A music model with two text fields: **description (caption / tags)** — genre, mood, instruments, sound, production — and **lyrics** with section tags. Tempo (BPM), key, time signature and length have **separate settings** — don't put them in the description. The Studio runs the **sft** variant (50 steps, with CFG): slower than turbo, but richer in detail and clearly better with vocals.

## Structure of the description (order recommended by the authors)
`genre/style → emotion/atmosphere → instruments → sound texture → vocal character (if any) → era/production`

Specifics win: "sad piano ballad with female breathy vocal" works better than "a sad song".

## Lyrics and instrumental music
- Section tags: `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`; with a short qualifier: `[Chorus - anthemic]`, `[Bridge - whispered]`.
- **Instrumental:** empty lyrics or `[Instrumental]`; describe how the piece develops with tags, e.g.:
```
[Intro - ambient]
[Main Theme - piano]
[Climax - powerful]
[Outro - fade out]
```
- Solo parts: `[Guitar Solo]`, `[Piano Interlude]`, `[drum break]`.

## What it's sensitive to / pitfalls
- **A contradiction between description and lyrics** (e.g. "violin solo" in the description, `[Guitar Solo]` in the lyrics) spoils the result.
- Don't stack qualifiers in a tag (`[Chorus - anthemic - stacked harmonies - high energy]` — too much); a complex description belongs in the description field.
- BPM and key in the description instead of the settings — works worse.
- Shorter pieces (30–60 s) are the most predictable; 4/4 time is the most stable.

## Examples (structure)
- Description: "minimal ambient, melancholic and spacious, felt piano and soft string pads, warm tape saturation, slow evolving textures, lo-fi home recording." Lyrics: `[Instrumental]`
- Description: "dark post-rock, tense then cathartic, tremolo electric guitars, deep bass, live drums with heavy room reverb, 2000s production." Lyrics: `[Intro - quiet guitar]` `[Build - drums enter]` `[Climax - full band]` `[Outro - feedback fade]`

## Parameters that really change the result
- **BPM** (30–300), **key**, **time signature**, **length** (separate fields). **Seed.**

## Sources (accessed 2026-10-05)
- ACE-Step 1.5 — Ultimate Guide (official): https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md
- ACE-Step 1.5 — A Musician's Guide: https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md
