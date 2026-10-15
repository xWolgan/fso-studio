# Ideogram 4 — how to prompt

## How the model listens
Ideogram 4 (open weights) was trained **exclusively on captions in a JSON structure** — with position boxes (bbox), colour palettes and the literal text to be rendered. A plain, short prose prompt "doesn't work": the authors say outright that it usually triggers a safety warning. In our test on the Spark, a short prompt produced a grey image with the words "Image blocked by safety filter" drawn on it (with typos); the same idea written in JSON gave a clean, precise poster.

## Prompt structure (key order matters)
```json
{
  "high_level_description": "1–2 sentences about the whole image",
  "style_description": {
    "aesthetics": "...",
    "lighting": "...",
    "photo": "... (ONLY for photography; then medium: photograph)",
    "medium": "...",
    "color_palette": ["#1B1B2F", "#E4DED3"]
  },
  "compositional_deconstruction": {
    "background": "...",
    "elements": [
      {"type": "obj",  "bbox": [y_min, x_min, y_max, x_max], "desc": "...", "color_palette": ["#..."]},
      {"type": "text", "bbox": [y_min, x_min, y_max, x_max], "text": "LITERAL TEXT", "desc": "typeface, size, layout", "color_palette": ["#..."]}
    ]
  }
}
```
- Only `compositional_deconstruction` is required (with `background` and `elements`); `high_level_description` is strongly recommended.
- `style_description`: `aesthetics`, `lighting`, `medium` are required; exactly **one of** `photo` (photography) **or** `art_style` (everything else). Order: photography — `aesthetics, lighting, photo, medium, color_palette`; non-photography — `aesthetics, lighting, medium, art_style, color_palette`.
- Elements: `obj` → `type, bbox, desc, color_palette`; `text` → `type, bbox, text, desc, color_palette`. The text to be rendered goes in the **`text`** field, the description of its look in `desc`.
- **bbox**: `[y_min, x_min, y_max, x_max]`, numbers 0–1000, origin in the top-left corner. E.g. `[80, 100, 300, 900]` = a band at the top of the image, almost full width.
- **Colours**: uppercase `#RRGGBB` only; up to 16 in the style, up to 5 per element.

## What it's sensitive to / pitfalls
- Prose instead of JSON → hallucinations and false "blocked by filter" results.
- Wrong key order, lowercase hex, missing `text` on a text element — the model was trained on a consistent format.
- Type accented and non-Latin characters (e.g. Polish `ą`) as they are, not as escape codes.
- The "template" button in the Studio inserts a skeleton — adjust it: for graphics replace `photo` with `art_style` (after `medium`), for text add the `text` field.

## Example (structure, not an idea)
```json
{"high_level_description":"A typographic poster on warm grey paper with a single line of text.",
 "style_description":{"aesthetics":"Swiss minimalism, generous negative space","lighting":"Soft even light","medium":"Letterpress print","art_style":"Minimal editorial typography","color_palette":["#D8D3CA","#2B2A27"]},
 "compositional_deconstruction":{"background":"Uncoated warm grey paper with fine fibres",
  "elements":[{"type":"text","bbox":[440,120,520,880],"text":"FORM RESEARCH GROUP","desc":"Thin serif capitals, wide letter spacing, centred","color_palette":["#2B2A27"]}]}}
```

## Parameters that really change the result
- **Profile** (Turbo 12 steps / Default 20 / Quality 48) — they differ in the number of steps and the noise schedule.
- **Aspect ratio** — bbox refers to the whole frame; when you change the aspect ratio, the boxes "stretch" with it.

## Sources (accessed 2026-10-05)
- Ideogram — prompting (open model repository): https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md
- Ideogram — JSON Prompting (4.0): https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0
- ComfyUI — Ideogram 4.0 Day-0: https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui
- Our own test on the Spark (2026-10-04).
