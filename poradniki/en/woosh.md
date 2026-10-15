# Woosh (Sony AI) — how to prompt

## How the model listens
A model built specifically for **sound effects**: text → effect and **video → synchronised sound** (foley for a clip), the latter with optional text that hints at what should be heard. The authors don't publish a separate prompting guide — what follows is based on the examples from their demo page.

## Structure of the description
**A short description of the sound event and its source**, about 8–15 words: what makes the sound + what happens to it. Examples from the authors' demo:
- "Emergency vehicle driving with siren on"
- "An engine humming and brakes squealing"
- "Starting a motorcycle"
- "A crowd applauds"
- (video + text) "A propeller plane flies over a snowy landscape, its engine roaring"

## Video → sound
- The clip is analysed in a window of **up to 8 s**; the result is trimmed to the clip's length.
- Without text the model guesses the sound from the image; a short text helps when the image is ambiguous.

## What it's sensitive to / pitfalls
- **Mono output, 48 kHz.**
- **The volume can be very low** — the Studio doesn't normalise anything; raise the level in your edit.
- Long, poetic descriptions help less than a concrete source and action.

## Parameters that really change the result
- **Mode**: fast (text → 5 s of effect in about 0.4 s; video → about 3 s) / quality (about 8–12 s).

## Licence
CC-BY-NC weights — non-commercial only.

## Sources (accessed 2026-10-05)
- Sony AI — Woosh (project page, examples): https://sonyresearch.github.io/Woosh/
- GitHub — SonyResearch/Woosh: https://github.com/SonyResearch/Woosh
- Sony AI — Introducing Woosh: https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model
- Timings and format: our own test on the Spark.
