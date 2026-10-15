# Qwen-Image 2.1 — how to prompt

## How the model listens
A large image model with very good understanding of long descriptions and **text rendering** (dense small text, layouts of posters, slides, infographics). It runs at CFG 1 — a negative prompt doesn't work. It has a built-in "prompt expander", **off by default**: a small LLM first thinks it over and then rewrites your prompt into a longer one before the image is made — this takes longer, about 1–2 min (in the Studio: the "model expands the prompt" switch).

## Prompt structure
- **Text → image:** prose: what is in the image → composition → light and colour → style/medium. Text in the image: give the **exact words** (in quotation marks) and describe where and how they should be laid out (typeface, size, order).
- **Editing (reference images):** refer to images by number: `<image1>`, `<image2>`…; say plainly what stays unchanged and what changes. Template from the documentation: "Keep the character and pose in `<image1>` unchanged, put this light blue denim shirt from `<image2>` on the character, preserve the original facial features, hair, body shape and pose".
- **Changing a region:** paint over the area with a colour on the input image and refer to the colour in the instruction: "change the jacket in the red area".

## What it's sensitive to / pitfalls
- The prompt expander changes your words — when working on a specific frame, leave it off; turn it on if you want to see the model's interpretation.
- Give text verbatim; a paraphrase = different text.

## Examples (structure)
- "A slide-style infographic on off-white background. Title at the top in bold sans-serif: "Water in Motion". Below, three columns with small line icons and one-line captions. Muted blue and grey palette."
- Editing: "Keep the room in `<image1>` unchanged. Replace the view outside the window with the winter landscape from `<image2>`, matching the evening light of the room."

## Parameters that really change the result
- **Steps**: 25 by default (CFG 1).
- **Prompt expansion**: yes/no (see above).

## Sources (accessed 2026-10-05)
- ComfyUI — Qwen-Image 2.1: https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1
- Qwen-Image 2.1 Prompt Enhancer (description of the T2I / editing modes): https://github.com/benjiyaya/ComfyUI-Qwen-Image-2.1-Prompt-Enhancer/
