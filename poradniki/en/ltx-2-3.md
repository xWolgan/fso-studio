# LTX 2.3 — how to prompt

## How the model listens
LTX 2.3 (Lightricks, 22B) generates video with sound; it can also take an **image** and **audio** as input (motion synchronised with the recording). It reads the prompt like a language model: **word order sets priority**. What works best is **one flowing paragraph in the present tense**, written like a shot description for a camera operator — prose, not a list of keywords. The distilled version runs at CFG 1 (negative prompts don't work).

## Prompt structure and order
Give the style / medium (if not photorealism) in the first phrase, then:
1. The main action in one sentence.
2. Details of movement and gestures — in chronological order.
3. Appearance of characters / objects (precisely).
4. Background and surroundings.
5. Camera angle and movement.
6. Light and colour.
7. Changes and sudden events.
8. Sound: the acoustics of the place, voice timbre, ambience; dialogue in quotation marks.

Length: in proportion to the length of the clip — in practice about 80–220 words (official sources differ: the 2.3 guide says long, detailed prompts win, the blog post on prompt adherence advises staying within about 200 words; the 2.5 guide gives 4–8 sentences for a simple shot). A short prompt with a long clip = the model "rushes" through the action. **One main action per 2–3 seconds** of clip. No labels like "Sound:" — weave sound into the prose.

## What it's sensitive to / pitfalls
- Too many events in a short clip → the model picks some of them or mixes them up.
- "Music/sound without speech" can be of lower quality (the authors note this in the model card).
- Dimensions divisible by 32, frame count of the form 8n+1 (the Studio picks these for you).

## Example (structure)
"A woman in a grey raincoat stops at the edge of a pier and looks down at the water. She slowly crouches, touches the wet wooden planks with her palm and then stands up again. She is in her forties, short dark hair, no make-up. Behind her, a grey sea and a lighthouse in the fog. The camera starts in a wide shot and slowly pushes in to a medium shot. Overcast, soft light, desaturated blue-grey palette. Wind gusts and waves hit the pylons, a distant foghorn sounds, and she quietly says in Polish, "Już tu nie wrócę.""

## Parameters that really change the result
- **Length** (frames 8n+1), **aspect ratio**, **seed**. In the Studio workflow, text → video, image → video and image + recording run in two stages (half resolution + ×2 upscaler); first and last frame — a single pass at full resolution.

## Sources (accessed 2026-10-05)
- LTX — LTX-2.3 Prompt Guide: https://ltx.io/blog/ltx-2-3-prompt-guide
- LTX — How to improve LTX-2.3 prompt adherence: https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence
- Hugging Face — Lightricks/LTX-2.3 (model card): https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md
- deAPI — LTX-2.3 guide: https://deapi.ai/blog/ltx-2-3-video-generation-guide
