<!-- Model card for the promptmaker. modele: stable-audio-3 -->
# Stable Audio 3 small-SFX (Stability AI, 05.2026)

## What it is and what it's good for
- A small (approx. 0.5–0.6 billion parameters) diffusion model for **text → effect / ambience / foley / one-shot**, **44.1 kHz stereo**, length 1 s – 2 min [6][7] (official), [3] (our configuration).
- Final training stages of small-SFX: **a curated subset of Freesound** (field recordings, foley, sound design); small-music got AudioSparx separately, because SFX data hurt musical coherence [6] (official). Takeaway: the model best understands descriptions in the style of **Freesound titles, tags and descriptions** [4][6] (official).
- Strengths: single events (impacts, footsteps, doors, glass), textures and ambiences, processed sound design (tape stop, distortion, filters), movement across the stereo field [4][9] (official).
- In Stability's test on BBC effects (5 s), small-SFX beat Woosh-Flow (FAD 0.395 vs 0.580; CLAP 0.351 vs 0.277) — the vendor's own measurement [6] (official).
- **What it does NOT do well:**
  - **music** — the modes table: small-sfx = "Samples/SFX" only, not Music or Stems [4] (official) → for music: other Studio models [3] (our configuration);
  - **intelligible speech and singing** — the SA3 family does not produce intelligible vocals [4][5] (official);
  - **mixing many sources at once** — a practitioner finds that the old Stable Audio Open 1.0 follows a "mix these" instruction better [13] (community);
  - **precise event timing** (e.g. "a hit exactly at second 3") — temporal control is outside the model's scope [6] (official);
  - overall quality: mixed opinions — "reasonable results, lightning fast", but worse than SA Open 1.0 [13]; another user: "about 10% better than 1.0"; isolated complaints about noise [14] (community).

## What the participant sets in Studio
| Field | Values | Effect on the prompt |
|---|---|---|
| **prompt** | text | the only description; goes to the T5Gemma encoder [1][2] (our configuration) |
| **length (s)** | 1–120, default 10 | this is **real length control**: ComfyUI derives the `seconds_total` condition from it (an integer — fractions are truncated) [1][12] (our configuration / ComfyUI code). Match it to the event (see below) |
| **seed** | number | results depend heavily on the seed — generate variants [3] (our configuration) |

- One mode: the **distilled** small-SFX model, 8 steps, **CFG 1**, lcm sampler [1][2] (our configuration). **No "quality" mode and no negative field** — according to the HF card the base checkpoint is "pretrained, intended for fine-tuning; use Small SFX for generation" [8] (official), so Studio doesn't expose it. At CFG 1 the negative branch wouldn't be computed anyway [12][17].
- The official example for the distilled model uses the pingpong sampler; Studio uses lcm (like the official ComfyUI template) [2][7] — this doesn't affect the prompt.
- Output: stereo FLAC; **loudness is not normalized** [1][3] (our configuration).
- Studio **does not expand the prompt** with an LLM (deliberately, unlike the medium template) [3] (our configuration) — the promptmaker's prompt goes to the model 1:1.

## Prompt format
- **Language: English.** Model card: language English; the training data is English Freesound/AudioSparx metadata [6][7] (official). Words in other languages at most as proper names — translate everything.
- **The `TrackType: SFX,` prefix** at the start — officially recommended for effects and samples; in the technical paper the authors write that such prefixes "significantly improve quality" (there in the context of models trained with AudioSparx data) [4][5][6] (official). No separate test for small-SFX — use it, but it's not a magic spell.
- **Structure (Stability's order):** 1) **source** (the exact object / material / instrument / synthesizer) → 2) **action** (how the sound is produced, how long it lasts, how it decays — attack, sustain, tail) → 3) **production and character** (microphone and its distance, room, processing) [4][5] (official).
- **Text length:** the official SFX template (Comfy-Org/Stability) calls for **1–2 dense sentences**, technical, specific language, no redundancy [9] (official). Encoder limit: **256 tokens**, beyond that it's truncated [6] (official) — in practice never get anywhere near it.
- **Style:** in training, metadata fields were joined **with commas**, randomly shuffled, and lowercased half of the time; some Freesound descriptions are captions rewritten by an LLM [6] (official). So both a natural sentence and a string of comma-separated phrases work; case and tag order are not critical.
- **`Length: N seconds`** at the end — a convention of the official template and ComfyUI examples [9][10] (official). In Studio the length is set by the "length" field anyway; if you add it, it **must match the field**. Effect of the text itself on small-SFX — unconfirmed.
- **Weights `(word:1.3)`, JSON, section tags** — not in the documentation; don't use them.
- **There is no negative** — don't describe what should be absent; if needed, name positively what should be there ("dry, isolated").
- **BPM** — this is musical vocabulary (AudioSparx, Music/Instrument mode) [4][9]; small-SFX doesn't do music. For rhythmic effects (e.g. a clock ticking) describe the tempo in words ("steady, once per second") — effectiveness unconfirmed.

## Prompt skeleton
```
TrackType: SFX, [source: specific object + material], [action: how the sound is produced, tempo/intensity], [course over time: attack, sustain, tail / build-up, fade-out], [space: indoor/outdoor, dry/reverberant, type of room], [perspective: close-up / distant / approaching / passing left to right], [recording and processing: microphone, tape, filter, distortion, reversal]. Length: [N] seconds
```
Soundscape (ambience):
```
TrackType: SFX, [place/environment] ambience, [constant layer: background/noise], [2–3 background events, rare/frequent], [distance of the layers], [time of day/weather as sound, not mood], [recording character: field recording, stereo]. Length: [N] seconds
```

## What works
- **Precision about material and physics**: "wooden desk drawer", "thin glass", "hard boot on dry leaves", "14-inch hi-hats played tightly closed" — the official examples always name the material, force and tail length [4][5][9] (official).
- **Describing evolution over time** in the SFX template: attack, sustain, movement, transitions — e.g. "starts with a suck-back of ambient noise, followed by a supersonic crack… that disappears into the distance" [9] (official).
- **Space vocabulary** from the template: indoor/outdoor, cave / open field / underwater, dry / reverberant, close-up / distant, echoing / muffled [9] (official).
- **Movement and stereo** (the model is stereo): "passing", "approaching", "doppler effect", "sound moving from left to right stereo field", "footsteps approaching then fading away" [9][10] (official).
- **Sequences**: the official example "Rapid sequence of three impacts: metal hit, glass break, wood crack, spaced evenly" [9] (official) — short, countable sequences can be described; don't expect exact placement in time.
- **Microphone and recording** as part of the description: "close-mic", "recorded with a small-diaphragm condenser mic", "ribbon mic", "recorded in a dead room with no room reflections" [4][9] (official; some examples from the One-shot template).
- **Length matched to the event** (official template): impacts, clicks 1–3 s; medium actions (footsteps, sliding, transitions) 3–6 s; ambiences 6–15 s (ambience examples up to 45–120 s) [9] (official). Stability: results are better when the length fits the described sound [4] (official).
- **Variants via seed**, not by rewriting the prompt — generation takes 1–2 s [3] (our configuration).
- **Layers separately**: instead of "rain + footsteps + siren" in one prompt, generate each layer separately and mix them in editing (inference from [13]; the official example "Layered soundscape: rain, thunder, footsteps, and distant sirens" [9] shows it's possible, but mix quality tends to be weaker).

## Biases and pitfalls
- **Length too long for a short event** → silence, padding or repetitions [18] (our configuration); training appended silence after recordings to decouple length from content [6] (official).
- **Mood words instead of sound** ("melancholic", "loneliness") — the model was trained on sound-library metadata; translate the mood into an acoustic phenomenon (distance, reverb, sparseness of events, filter) [4][6] (inference from official sources).
- **Drift toward music/tone** with words like "cinematic", "epic", "drone" — the template uses them deliberately for sound design [9]; if you want a raw recording, don't add them (unconfirmed as a bias; caution).
- **Loudness**: Studio doesn't normalize [3] (our configuration) — warn the participant that levels will be evened out in editing.
- **Little variation between seeds** with the same prompt (observation for SA3 music) [15] (community) — if variants are too similar, change one element of the description (perspective, material).
- **No looping**: there is no loop parameter and no loop documentation for SA3 (none found). Loops are made in editing (crossfade) — see below.

## Beyond photorealism
Processing and "tape" vocabulary appears in the official examples, so the model knows it [4][9] (official):
- **tape / vinyl / archive**: "tape stop", "tape-saturated", "vinyl crackle", "dusty", "lo-fi", "1950s" (examples from the SFX/One-shot/Instrument templates) [9];
- **processing**: "processed with resonant band-pass filter", "slightly distorted", "bit-crushing", "pitch-shifted", "reversed", "granular texture", "glitchy digital distortion", "long dark wooden room reverb" [9];
- **medium stylization**: "8-bit style", "retro arcade", "soft futuristic interface sounds" are in the examples [9]; "cartoon", "hand-drawn" — unconfirmed;
- **abstraction / texture**: describe the physical phenomenon, not the meaning — "metal scraping slowly in a dark tunnel", "heavy timber under immense structural tension, swaying slowly" [9];
- **unusual perspectives**: "underwater", "interior perspective", "muffled" [9]; special microphones ("contact microphone", "hydrophone") are typical Freesound tags — effectiveness unconfirmed.
- How to do "drawing/animation" in sound: simplified and exaggerated physics (short, dry, no background: "dry, isolated, no background") — inference, unconfirmed.

## Movement / time / sound
- Source movement: approaching / receding / passing / doppler / left-to-right stereo [9][10] (official).
- Course: attack (sharp transient / slow attack), decay (fast decay / long shimmering decay / reverb tail), build-up (slow build) [4][9] (official).
- **Loop (ambience)**: generate longer than needed (e.g. 30–60 s), with no standout events at the start and end ("steady, continuous, no sudden events" — unconfirmed), close the loop with a long crossfade in editing; Studio has no loop mode [1] (our configuration).
- Field length = result length; max 120 s [1][7].

## Check before sending
- [ ] Prompt in English, starts with `TrackType: SFX,`
- [ ] Named source **and material**, action, course over time, space, perspective
- [ ] 1–2 sentences, no moods or metaphors from the poem (translated into acoustic phenomena)
- [ ] The "length" field fits the event (impact 1–3 s, action 3–6 s, ambience 6–15 s+); if `Length: N seconds` was added — it matches the field
- [ ] One event / one layer per prompt (layers → separate generations)
- [ ] No music, speech, BPM, weights, JSON
- [ ] Reminder: several seeds; loudness to be evened out in editing

## Sources
[1] Studio — `modele/sfx/stable-audio-3.yaml` — our configuration
[2] Studio — `workflows/sfx/stable_audio_3_tekst-na-efekt.api.json` — our configuration
[3] own notes (unpublished) (SFX section) — our configuration
[4] Stability AI — Stable Audio 3 prompting guide (GitHub) — https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md — official
[5] Stability AI — Stable Audio 3.0 Prompt Guide — https://stability.ai/guides/stable-audio-3-prompt-guide — official
[6] Stable Audio 3 — technical paper (arXiv 2605.17991) — https://arxiv.org/html/2605.17991v1 — official
[7] Hugging Face — stabilityai/stable-audio-3-small-sfx — https://huggingface.co/stabilityai/stable-audio-3-small-sfx — official
[8] Hugging Face — stabilityai/stable-audio-3-small-sfx-base — https://huggingface.co/stabilityai/stable-audio-3-small-sfx-base — official
[9] Comfy-Org — "audio_stable_audio_3_medium" template (reprompt categories: SFX, One-shot, Instrument; read from the comfyui-workflow-templates package on the Spark) — https://github.com/Comfy-Org/workflow_templates — official (template written for SA3 Medium; the effect examples carry over to small-SFX)
[10] Comfy blog — Stable Audio 3.0 Day-0 Support — https://blog.comfy.org/p/stable-audio-3-day-0-support — official
[11] ComfyUI docs — Stable Audio 3 — https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3 — official
[12] ComfyUI — `comfy/samplers.py` (skipping the negative branch at CFG 1) and `comfy/model_base.py` (StableAudio3: `seconds_total` from latent length) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py — official (code)
[13] jurn.link — How to install Stable Audio 3.0 small-SFX… — https://jurn.link/dazposer/index.php/2026/05/22/how-to-install-stable-audio-3-0-small-sfx-safetensors-and-run-it-in-comfyui/ — community
[14] r/StableDiffusion (snapshot) — Stable Audio 3.0 Day-0 Support in ComfyUI — https://reddit.sentinel-team.org/posts/1tj7afx/snapshots/2026-05-21T18%3A20%3A48.87163Z — community
[15] Dubspot — Stable Audio 3 review — https://blog.dubspot.com/stable-audio-3-review — community
[16] fal.ai — Stable Audio 3 Small SFX Base (API parameters) — https://fal.ai/models/fal-ai/stable-audio-3/small/sfx/base/text-to-audio/llms.txt — community/service
[17] ComfyUI notes — Conditioning Zero Out (CFG 1 and the negative) — https://comfyui.nomadoor.net/en/notes/conditioning-zero-out/ — community
[18] Studio — guide `poradniki/stable-audio-3-sfx.md` — our configuration
