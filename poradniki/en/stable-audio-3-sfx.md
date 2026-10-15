# Stable Audio 3 small-SFX — how to prompt

## How the model listens
A small (459M), specialised **sound effects** model by Stability AI. It works in **stereo**, effects up to about 2 minutes, very fast (10 s of effect in 1–2 s on the Spark). It likes matter-of-fact descriptions, like an entry in a sound library: source, action, character of the recording.

## Structure of the description (order according to Stability AI)
1. **Source** — exactly which object, instrument or synthesiser is making the sound.
2. **Action** — how the sound is produced, how long it lasts, how it decays (short/long tail).
3. **Production / character** — microphone placement, room acoustics, processing.

The authors also recommend the **`TrackType: SFX`** tag, which usually gives more sensible effects.

## What it's sensitive to / pitfalls
- **Set a short length** — most effects are short; a long duration for a short event gives silence or repetitions.
- Describe the material, the force of the impact and the length of the tail — these change the result the most.

## Examples (from the Stability AI guide)
- "A blunt, powerful 'thud' made by slamming a wooden desk drawer shut. It has a pronounced low-mid body, making it feel heavy, and is given a touch of analog distortion for aggressive character."
- "A classic, natural recording of 14-inch hi-hats played tightly closed. Zero ring and a very fast decay."
- "A massive sub-bass note that mimics a vinyl record or tape machine being turned off."

## Parameters that really change the result
- **Length** (1–120 s; this is real length control — match it to the event: an impact 1–3 s, an action 3–6 s, ambience 6–15 s and more) and **seed** (a generation takes 1–2 s — make variants with the seed).
- The Studio uses the distilled small-SFX model (8 steps, CFG 1), so **there is no negative field** — whatever shouldn't be there, simply don't describe it. Loudness is not normalised.

## Sources (accessed 2026-10-05)
- Stability AI — Stable Audio 3 prompting (GitHub): https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md
- Stability AI — Stable Audio 3.0 Prompt Guide: https://stability.ai/guides/stable-audio-3-prompt-guide
- ComfyUI — Stable Audio 3: https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3
