# MiniMax Music 3 — how to prompt

## How the model listens
MiniMax's open music model (August 2026): from **lyrics** and a **description of the sound** it makes a coherent piece up to 5 minutes long (32 kHz, stereo). The description can be plain prose or a **structured description** in three sections. Section tags and descriptions are hints, not guarantees — tempo, key and structure won't always be followed exactly.

## Structure
**Structured description (three sections):**
1. **Global metadata** — genre, subgenre, BPM, key, scale, emotional arc, listening situation, production profile.
2. **Vocal details** — gender, timbre, singing style, harmonies, backing vocals, effects (for an instrumental piece — skip it or state plainly that there are no vocals).
3. **Arrangement** — lead and supporting instruments, how they change across sections, groove, bass, drums, textures, space.

Template from the model card: "Genre: acoustic pop. BPM: 96. Key: C major. Warm and intimate…" / "Vocals: soft female lead…" / "Arrangement: fingerpicked guitar and soft piano; brushed drums…".

**Lyrics:** tags `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` — **each on its own line**, with no words on the same line. Instrumental piece: `[Instrumental]` / `[Solo]` sections.

## What it's sensitive to / pitfalls
- Lyrics on the same line as a tag — parsed badly.
- A long piece = a long generation (on the Spark about 93 s per 30 s of music in fast mode).

## Example (structure, instrumental)
- Description: "Genre: ambient electronica. BPM: 80. Key: D minor. Slowly brightening, from tension to calm. Vocals: none, purely instrumental. Arrangement: analog synth drones, sparse plucked bass, distant processed field recordings, slowly opening filter, wide stereo reverb."
- Lyrics:
```
[Intro]
[Instrumental]
[Solo]
[Outro]
```

## Parameters that really change the result
- **Mode**: fast (INT8 encoder) / full quality (bf16, about 146 s per 30 s). **Length**, **seed**.

## Sources (accessed 2026-10-05)
- Hugging Face — MiniMaxAI/MiniMax-Music3: https://huggingface.co/MiniMaxAI/MiniMax-Music3
- MiniMax — Music 3.0 (blog): https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model
- ComfyUI — MiniMax Music 3: https://blog.comfy.org/p/minimax-music-3-state-of-the-art
- Prompting MiniMax Music 3 (Space): https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide
