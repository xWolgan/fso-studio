# Z-Image Turbo — how to prompt

## How the model listens
A fast distilled model (8 steps, CFG 1). It responds best to **long, specific descriptions** written like instructions for a camera operator, not a list of adjectives. **A negative prompt doesn't work** (at CFG 1 it's ignored) — everything that should or shouldn't be in the frame is described in positive terms.

## Prompt structure and order of blocks
`[medium and style] → [framing, angle and composition] → [object/character: appearance] → [clothing, materials, colours] → [surroundings/background] → [light and palette] → [texture; for a photo: one camera/lens and one film stock] → [text in the frame] → [constraints described positively]`

Write **in English**, in full sentences, matter-of-factly — not as a list of tags. The authors recommend long, detailed prompts; the community points to about 80–250 words as a good range. In the Studio the prompt isn't truncated (the 512-token limit applies only to the official diffusers code, not ComfyUI) and nobody expands it along the way.

State the medium at the beginning — the model pulls towards photorealism; for drawing or painting don't use words about cameras and film, or the photo will come back. Translate mood into light, palette, framing and material — no metaphors or judgements ("beautiful", "masterpiece", "8K").

## What it's sensitive to / pitfalls
- Generalities ("beautiful", "epic") give a generic result; detail works.
- Instead of "no people" — describe what is in the frame ("an empty street, only wet cobblestones and streetlamps").
- Very fast (a few seconds) — good for finding a direction; compare final quality with Qwen-Image 2.1.
- **Low diversity:** changing the seed often gives almost the same image. A variant = a differently described frame (framing, angle, time of day, arrangement), not just a different seed.
- Text in the image: short, verbatim in quotation marks `"…"`, with its position and typeface. Reliable only in English and Chinese; other scripts and accented characters (e.g. Polish) — unconfirmed (text is better done in Ideogram 4 or Qwen-Image 2.1).
- There are no weights `(word:1.3)` — brackets and numbers reach the model as text.
- Without a description of texture (pores, fabric weave, grain) people come out "plastic" and stock-like.

## Examples (structure)
- "Photograph, close-up portrait at eye level, centred composition, shallow depth of field. A middle-aged man with grey stubble, tired half-closed eyes and visible skin pores, in a dark wool coat. Behind him a blurred tram stop at dusk. Cold blue ambient light with a warm sodium streetlamp from the left. Shot on a 50mm lens, Kodak Portra 400, fine film grain."
- "Documentary photograph, wide shot from a high angle. An empty concrete courtyard after rain, only wet concrete and puddles reflecting an overcast sky. A single red bicycle leaning against the wall in the right third. Flat diffuse light, muted grey palette with one red accent."

## Parameters that really change the result
- **Steps** (advanced, 4–16, default 8) — the model is trained on 8 steps; fewer = a sketch, more doesn't always mean better.
- **Seed** — a weak lever (low diversity); a fixed seed is useful for seeing the effect of each change in the prompt.

## Sources (accessed 2026-10-05)
- Tongyi-MAI/Z-Image-Turbo — model card: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- Tongyi-MAI/Z-Image-Turbo — "PROMPTING GUIDE" (authors' answers): https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8
- Z-Image-Turbo Prompting Guide (community): https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32
- deAPI — Z-Image Turbo prompting: https://deapi.ai/blog/z-image-turbo-prompting-guide-formula-tips-and-5-example-prompts
- fal — Z-Image Turbo prompt guide: https://fal.ai/learn/devs/z-image-turbo-prompt-guide
