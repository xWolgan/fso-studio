# Qwen-Image-Edit 2511 — how to prompt

## How the model listens
An image editing model driven by instructions, geared towards **preserving consistency** (character identity, style, layout) and editing text within the image. The first image is treated as the **main** one (the canvas) — that's the one that changes; the second is a reference (in the Studio: up to two images). The result is about 1 MP in the aspect ratio of image 1 (the Studio scales it before editing), not the size of the original. Write the instruction **in English**, in plain prose, as a command (verb first), not as a description of the finished image.

## Instruction structure
`[operation: Replace / Change / Remove / Add…] + [target and its place in the frame] + [into what / from which image, specifically] + [what should stay unchanged]`
- Refer to images as **"image 1", "image 2"** — in the order they were uploaded (not `<image1>` — that's the Qwen-Image 2.1 Edit syntax).
- Always add what stays — briefly, all at once and in affirmative form: "Keep the face, pose, background and lighting unchanged." Don't describe in detail the look of what should stay (the model will start redrawing it).
- Point to a person's identity from the reference by the image ("the woman from image 2"), don't describe the face in words.
- Template: "Place the person from image 2 into the scene in image 1, matching the lighting and perspective. Keep the rest of image 1 unchanged."
- Text in the image: in quotation marks, verbatim, in its own language ("Replace the text "OPEN" with "ZAMKNIĘTE""); non-English characters (e.g. Polish diacritics) — unconfirmed.
- One operation per instruction; do a complex edit as a chain (result → new input).

## What it's sensitive to / pitfalls
- A vague instruction ("make it nicer") = unexpected changes across the whole image. The more specific, the less the rest changes.
- References with a similar framing and perspective blend better.
- The image can shift or zoom in slightly relative to the input — for local edits add "keep the framing and camera angle unchanged".
- Skin can come out "plastic" — for portraits ask for natural skin texture.
- There are no weights `(word:1.3)` and no negatives — brackets reach the model as text.
- Fast mode (Lightning, 4 steps, CFG 1, about 30 s) — for trying things out, loses texture; quality mode (40 steps, CFG 4, about 7 min) — clearly more accurate in detail.

## Examples (structure)
- "Change the season in image 1 to late autumn: bare trees, wet leaves on the ground. Keep the buildings, the people and the camera angle unchanged."
- "Replace the sofa fabric in image 1 with the material from image 2. Keep the shape of the sofa, the room and the lighting unchanged."

## Parameters that really change the result
- **Mode** fast / quality. **Seed** — with a fixed seed you can see the effect of the instruction alone.

## Sources (accessed 2026-10-05)
- Qwen/Qwen-Image-Edit-2511 — model card: https://huggingface.co/Qwen/Qwen-Image-Edit-2511
- QwenLM/Qwen-Image — README and the edit instruction rewriter: https://github.com/QwenLM/Qwen-Image
- Scenario — Advanced Editing with Qwen Models: https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models
- Replicate — qwen-image-edit-2511: https://replicate.com/qwen/qwen-image-edit-2511
- RunComfy — Qwen Image Edit 2511 in ComfyUI: https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing
