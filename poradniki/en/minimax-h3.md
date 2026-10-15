# MiniMax H3 — how to prompt

## How the model listens
H3 generates **image and stereo sound together** (dialogue, effects, ambience, music). The prompt is a **script with a timeline**, not a description of a picture: successive shots, camera movement, who speaks and what you hear. Write the prompt **in English** (dialogue and on-screen text can be in their own language — verbatim). It runs at CFG 1: **there is no negative prompt**, and naming an unwanted thing adds it to the description.

## Prompt structure (official three-field layout)
```
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:04.000, the camera cuts to ...

overall_soundscape: ...

non_diegetic_music: ...
```
Fields separated by a blank line, in this order.
- **integrated_multimodal_description** — shots `[Shot 1]`, `[Shot 2]`… with image, action, camera movement and diegetic sound (dialogue, effects, music within the scene) in one block. First the whole scene (place, character, what's happening), then the shots.
- **overall_soundscape** — 1–4 sentences: ambience, sounds of the action, non-verbal sounds. `N/A` only for complete silence.
- **non_diegetic_music** — 1–3 sentences about music heard only by the viewer; `N/A` if there is none.
- **Dialogue:** in `<d>` tags, with a speaker ID and a language tag in square brackets: `(S1) says: <d>[English] Exact words.</d>` (not `<d>English: …</d>`); inside `<d>` only the language tag and the words, end the line with a full stop/?/!. Each voice has a fixed ID `(S1)`, `(S2)`, repeated in every shot where it speaks; describe the voice (age, gender, timbre, pace) on its first appearance, outside `<d>`. A character who doesn't speak gets no ID.
- **On-screen text:** in quotation marks, verbatim, in the original language.
- **Off-screen voice:** "says in an off-screen voiceover" + a note that the lips stay closed.
- **Camera:** type of movement + amplitude + speed, in natural language within the shot sentence (e.g. "the camera pushes in with small amplitude at slow speed"); vocabulary: static, zoom in/out, push in / pull out, pan, truck, tilt, pedestal, arc, tracking, shake slightly/strongly, POV, roll.
- **Shots:** `[Shot 1]` without a time; the following ones with a cut time `At MM:SS.mmm` (ascending, less than the clip length). Every cut = new information (place, state, point of view).
- **Image → video — you write the alignment line yourself.** The Studio/ComfyUI node adds nothing to the prompt (the node only labels images as `<Picture n>`). When you provide frames, the **first line of the prompt** is literally (then a blank line, then the three fields):
  - first frame only (I2VA):
    `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
  - first and last (FL2VA) — `S.SS` = clip length with two decimal places, `N` = number of the last shot:
    `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  - last frame only (L2VA):
    `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
  - no frames (text → video): no such line.
- **Inspirations (Ref2VA):** when you provide inspiration images/videos/sounds, the model uses a different format — six sections `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` with `<Picture n>`, `<Video n>`, `<Audio n>` tags; the first/last frame are then ignored. The Studio's prompt assistant knows the details.

## What it's sensitive to / pitfalls
- "No on-screen text" adds the word "text" to the description → instead write "the sign above the door is blank".
- Shot length: one clear action per shot. Clip officially 4–15 s (10 s by default in the Studio); the model was trained on about 5–15 s — **set at least 5 s**.
- Polish is not among the stably supported dialogue languages (the same may apply to your language) — keep lines short and simple (`<d>[Polish] …</d>`); in the description don't mix your language with English (the model may read the description aloud).
- Native resolution: shorter side 768 px; in the Studio 480p (default) or 720p.

## Example (structure)
```
integrated_multimodal_description: [Shot 1] Cinematic live-action. A narrow kitchen at night, one lamp on. Medium shot, static camera. An old woman with a low, slightly hoarse voice slowly peels an apple at the table; the knife scrapes softly. (S1) says: <d>[Polish] Jeszcze chwilę.</d> She closes her lips and keeps peeling silently. [Shot 2] At 00:04.000, the camera cuts to a close-up of her hands and pushes in with small amplitude at slow speed; the peel falls in one long ribbon onto the oilcloth.

overall_soundscape: A refrigerator hum, a distant tram outside, the soft scrape of the knife.

non_diegetic_music: N/A
```

## Parameters that really change the result
- **Mode**: fast (turbo LoRA, 8 steps; with inspirations and keyframes 4 steps; about 40–44 s per 2 s of clip on the Spark; somewhat weaker sound and motion) / full quality (20 steps; about 84 s).
- **Length** and **aspect ratio** (natively 768 px on the shorter side).

## Sources (accessed 2026-10-05)
- MiniMax — Video Prompt Writing Guide (alignment lines, `<d>[Language] …</d>` format): https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- ComfyUI — H3 node code (the node doesn't add the alignment line): https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py
- ComfyUI — MiniMax H3 Prompt Guide (official format): https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- RunDiffusion — H3 Prompt Guide: https://www.rundiffusion.com/minimax-h3-prompt-guide
- DEV — H3 camera motion, timing, audio: https://dev.to/jaysean_brambila_1f12d6cc/minimax-h3-prompt-engineering-camera-motion-timing-and-native-audio-1a8g
- Timing measurements: our own test on the Spark.
