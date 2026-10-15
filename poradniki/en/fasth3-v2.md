# FastH3 V2 — how to prompt

## How the model listens
FastH3 V2 is a distilled (DMD2) version of MiniMax H3 by the FastVideo team: image and sound in **exactly 8 steps**. **You write the prompt the same way as for H3** — the same three-field structure, `<d>` tags, speaker IDs, description in English. Details: the `minimax-h3` guide.

## Prompt structure
As in H3: first the whole scene (place, character, what's happening), then the shots with timing, camera movement and sound in one block; ambience and off-screen music separately.

## What it's sensitive to / pitfalls
- **The number of steps is fixed (8)** — the model is trained for exactly 8 steps; changing it degrades quality.
- Length "snaps" to a 17-frame grid (17k+5) at 24 fps; native shorter side 768 px, dimensions rounded to multiples of 32.
- **On the Spark, FastH3 V2 is about 20–30% slower than regular H3 in fast mode** (most likely due to missing fast kernels for sparse attention on GB10) — it's worth comparing both on the same prompt and seed.
- As in H3: no negative prompt; don't name what shouldn't be there.

## Example
The same as in the H3 guide — the format is identical.

## Parameters that really change the result
- **Length** and **aspect ratio**. Steps — don't change.

## Sources (accessed 2026-10-05)
- ComfyUI — FastVideo FastH3: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo
- Hugging Face — FastVideo-FastH3-8-Step-V2: https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2
- Kombitz — FastH3 V2 in ComfyUI: https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/
- Measurements: our own test on the Spark.
