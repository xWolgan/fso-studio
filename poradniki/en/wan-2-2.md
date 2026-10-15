# WAN 2.2 — how to prompt

## How the model listens
WAN 2.2 (14B; two models: "high noise" builds the composition and motion, "low noise" refines the detail) generates video **without sound**. It likes **detailed, descriptive prompts** (the authors' examples often run over 100 words); it understands English and Chinese. Its strength: a huge number of community LoRAs.

## Prompt structure and order
`[object/character] + [action] + [surroundings] + [camera movement] + [light] + [style] + [movement in the surroundings and pace]`

Combine camera movement and character movement in one sentence, e.g. "The dancer spins in place while the camera smoothly orbits clockwise around her". Camera vocabulary: slow tracking shot, orbit, dolly-in / dolly-out, pan left/right, tilt up/down, crane, handheld follow, static camera, drone pullback.

**Image → video:** describe the movement and the change, not what is already visible in the image.

## What it's sensitive to / pitfalls
- **The negative prompt only works in full quality mode** (CFG 3.5–4). In fast mode (lightx2v LoRA, 4 steps, CFG 1) it's ignored.
- Add negatives reactively: first generate without them, then add the specific artefact that appeared (e.g. "morphing, warping, flickering, face deformation").
- Natively **16 fps**, frame count of the form 4n+1 (e.g. 81 frames ≈ 5 s); 480p or 720p. Clips longer than about 5 s go beyond what the model was trained on.

## Example (structure)
"An old fisherman mends a net on a wooden jetty, his fingers moving quickly through the knots. Gulls circle above, the water glitters. The camera slowly dollies in from a medium shot to a close-up of his hands. Late afternoon golden light, long shadows. Naturalistic documentary style, gentle wind moving the net."

## Parameters that really change the result
- **Mode**: fast (lightx2v, 4 steps; about 28 s per 2 s of clip on the Spark) / full quality (20 steps; about 210 s).
- **LoRA** — once they're available in the Studio, each one has a recommended strength.

## Sources (accessed 2026-10-05)
- Wan-Video / Wan2.2 (official repository): https://github.com/Wan-Video/Wan2.2
- VEED — Wan 2.2 Prompting Guide: https://www.veed.io/learn/wan-2-2-prompting-guide
- Dreamina — Wan 2.2 Prompt Guide: https://dreamina.capcut.com/ai-video/wan-2-2-prompt
- Measurements: our own test on the Spark.
