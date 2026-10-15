# LTX 2.5 — how to prompt

## How the model listens
LTX 2.5 (Lightricks, August 2026) — the successor to LTX 2.3, with sound and **native multi-shot**: in a single generation it can make several connected shots while keeping the character, scene, light, style and voice. The writing rules are the same as for 2.3: **one chronological paragraph**, present tense, prose.

## Prompt structure (six elements from the Lightricks guide)
1. **Shot** — framing and cinematography terms.
2. **Scene** — light, colour, texture.
3. **Action** — as a natural sequence from beginning to end.
4. **Characters** — age, hair, clothing, emotions shown physically (through gesture, facial expression).
5. **Camera movement.**
6. **Sound** — dialogue in quotation marks, ambience, effects.

Length: officially about 4–8 sentences for a simple shot, more for complex scenes — as long as every sentence adds a concrete detail of image or sound. No labels like "Sound:"/"Audio:" — weave sound into the prose next to the action that causes it. Always name the camera movement (no movement = "the camera remains static"), otherwise the model is happy to push in on its own.

**Multiple shots (2–4, text → video only):** the whole scene as one paragraph; name each cut in words ("A hard cut transitions to…", "The view cuts to a close-up of…"), in the new shot describe again who is in it, and say whether the sound carries across the cut.

## What it's sensitive to / pitfalls
- Cuts have to be named — otherwise the model makes one long shot.
- A character not described again after a cut may "jump" in appearance.
- Image → video: start with a sentence that matches the image (framing, subject, place), then the movement — in a single shot. The identity of a character from the image sometimes gets changed.
- Prompt expansion (the "model expands the prompt" switch) adds a "cinematic" sheen and camera movement, and sometimes drifts from the content — when you're working on a stylisation, leave it off.

## Example (structure)
"Medium shot of a man in a worn leather jacket sitting alone in an empty bus at night, his face lit by passing streetlights. He looks at a folded letter in his hands and slowly unfolds it. A hard cut transitions to a close-up of the letter: handwritten lines, a coffee stain in the corner. The view cuts back to the man, the same leather jacket, as he folds the letter again and looks out of the window. The engine drone and the rattle of the windows continue across both cuts as he exhales softly."

## Parameters that really change the result
- **Length**, **aspect ratio**, **seed**.
- **Model expands the prompt** (advanced, off by default) — rewrites the prompt with the Gemma 4 E2B model; adds about 1–2 min.

## Sources (accessed 2026-10-05)
- LTX — LTX-2.5 Prompt Guide: https://ltx.io/blog/ltx-2-5-prompt-guide
- LTX Docs — Prompting Guide: https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide
- deAPI — LTX-2.5 Prompt Guide (multi-shot, sound): https://deapi.ai/blog/ltx-2-5-prompting-guide-multi-shot-scenes-native-audio-and-prompts-that-actually-cut
- Runware — LTX-2.5 prompting: https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/prompting
- Hugging Face — Lightricks/LTX-2.5: https://huggingface.co/Lightricks/LTX-2.5
