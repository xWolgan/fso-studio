<!-- Model card for the promptmaker. modele: woosh, woosh-wideo -->
# Woosh (Sony AI, public weights 03.2026) — effect from a description and sound for video

## What it is and what it's good for
- Sony AI's foundation model for **sound effects**: **text → effect** (Woosh-Flow / distilled DFlow) and **video → synchronized sound** with an optional description (VFlow / distilled DVFlow) [5][6] (official).
- Output: **mono, 48 kHz** (the autoencoder works only in mono) [5] (official), 24-bit WAV; for video also an MP4 with the sound replaced [2][3] (our configuration).
- The public version was trained on **Freesound (original descriptions), AudioCaps (human captions), WavCaps (weakly labeled captions)**; video→sound on VGGSound (captions from Qwen3-Omni or the original class labels) [5] (official). The better "private" version (Pro Sound Effects / BOOM libraries) **is not available** — Studio has the public one [3][8] (our configuration / official).
- Strengths: short, single events (vehicles, engines, applause, impacts), sound glued to the motion in the picture. In the authors' video→sound test (FoleyBench), better quality/adherence than MMAudio, but **worse synchronization** (DeSync 0.575 vs 0.400) [5] (official).
- **What it does NOT do well:**
  - **stereo, movement across the panorama** — mono only [5];
  - **long ambiences** — trained on **5 s** fragments (text→effect) [5]; Studio allows 1–10 s, >5 s = experiment [1] (our configuration). Long soundscapes → Stable Audio 3;
  - **loops** — "perfect loops" are only in Sony's plans [8] (official);
  - **precise timing, morphing** — also only planned [8] (official);
  - **music and speech** — it's an SFX model; music and speech: other Studio models [3] (our configuration);
  - the distilled models (fast mode) score worse than the full ones on most metrics [5] (official).
  - On BBC effects (Stability's measurement), Woosh-Flow is weaker than SA3 small-SFX [11] (official, competitor's source).

## What the participant sets in Studio
**woosh (effect from a description)** [1][2] (our configuration)
| Field | Values | Effect |
|---|---|---|
| **prompt** | text (required) | description of the event |
| **length (s)** | 1–10, step 0.5, default 5 | trained on about 5 s; longer = experiment |
| **mode** | fast (DFlow, 4 steps) / quality (Flow, ODE solver) | fast ~0.4 s, quality ~12 s [3] |
| **prompt strength (CFG)** | 1–10, default 4.5 (advanced) | higher = closer to the description |
| **seed** | number | variants |

**woosh-wideo (sound for video)** [1][2] (our configuration)
| Field | Values | Effect |
|---|---|---|
| **video clip** | required | the model sees **8 s from the "window start"**; the result is trimmed to the clip length |
| **description (optional)** | text, may be empty | suggests *what* should sound; *when* comes from the picture |
| **window start (s)** | 0–60, step 0.5 | clip > 8 s → further windows as separate generations |
| **mode** | fast (DVFlow) / quality (VFlow) | ~3 s / ~8 s [3] |
| **prompt strength (CFG)** | 1–10, default 3 (advanced) | influence of the description relative to the picture |
| **seed** | number | variants |

- **No negative field** — the Woosh API in Studio doesn't accept one [1][2] (our configuration). Don't add "no music" etc. to the prompt (the CLAP encoder understands negations poorly — unconfirmed for Woosh, caution).
- **Volume**: can be very quiet (footsteps on gravel about −60 dB RMS); Studio does not normalize, it only prevents clipping [2][3] (our configuration).
- Weights license **CC-BY-NC** (non-commercial) [6] (official).

## Prompt format
- **Language: English — required.** The text encoder is **RoBERTa-Large from Woosh-CLAP** [5] (official), an English language model; training captions are in English.
- **Hard limit: 77 tokens** (`max_sentence_tokens: 77`, excess is cut off) [4] (official, weights configuration) → in practice **up to about 40–50 words**; the most important things first. Recommended: **8–25 words**.
- **Style: one sentence describing a sound event like an AudioCaps/Freesound caption**: [source] + [action] (+ context). Official examples: "Emergency vehicle driving with siren on", "An engine humming and brakes squealing", "Starting a motorcycle", "A crowd applauds" [7] (official). AudioCaps are human captions of AudioSet clips [12] (official, dataset).
- **The text is not preprocessed** (`text_preprocessing: no_op`) [4] — punctuation and capitalization reach the model as is; write a normal sentence.
- **No** tags, prefixes (`TrackType` is Stable Audio — it doesn't work here), weights, JSON, `Length:` — the length is set by the field [1][2] (our configuration); nothing like this appears in the Woosh documentation [5][6][7].
- **Video + text**: the V2A captions in training are natural sentences from Qwen3-Omni describing the scene and the sound, or short VGGSound class labels [5] (official). Official examples of descriptions for video: "A propeller plane flies over a snowy landscape, its engine roaring.", "A large audience in a formal hall gives a standing ovation with applause." [7] — **a description of the visible source + its sound**.

## Prompt skeleton
Effect from a description (woosh):
```
[subject/source with material] [action verb, with intensity/pace], [second event: "followed by…" / "while…"], [space: in a large empty hall / outdoors / indoors], [distance: close / in the distance]
```
Sound for video (woosh-wideo):
```
[visible source] [action visible in the frame], [what sound it makes: material, character], [acoustic background: wind / room reverb — optional]
```
or minimally (a label like VGGSound): `[source] [action]` — e.g. the structure "dog barking".

## What works
- **Specifics: source + action** instead of adjectives — all the authors' examples look like this [7] (official); Studio guide: 8–15 words [13] (our configuration).
- **Action + texture + acoustics** in one phrase, e.g. the structure "fast metallic whoosh in a concrete stairwell" [10] (community).
- **Two events** joined with "and" / "followed by" (official example "An engine humming and brakes squealing" [7]); more than 2–3 blurs the result (unconfirmed).
- **Short lengths**: 1–5 s; make longer sounds as several generations and join them (inference from [5]).
- **Fast mode for searching, quality for the final** — the distilled models are weaker [5] (official); the practice "scout DVFlow → finalize VFlow" [10] (community).
- **CFG**: moderate for natural textures, higher for stylized ones / strictly following the description [10] (community). The distillation was trained for CFG in the 1–9 range; the authors evaluated DFlow at CFG 7 [5] (official). The Studio defaults 4.5 (text) and 3 (video) — leave them, unless the result ignores the description (then 5–7).
- **Seed**: several variants — good results are random [3] (our configuration).

## Biases and pitfalls
- **Cut-off after 77 tokens** — a long, poetic description loses its ending without warning [4] (official).
- **Poetry and mood don't work** — "long, poetic descriptions help less than a concrete source and action" [13] (our configuration); the CLAP encoder was trained on descriptions of acoustic events [5].
- **A prompt in a language other than English (e.g. Polish)** — RoBERTa-Large is an English model [5]; the result will be random (not confirmed by a test, but follows from the architecture).
- **Very quiet result** — not a prompt error [3] (our configuration).
- **Video: synchronization applies to what is visible**; sounds outside the frame (ambience, distant events) may be skipped by the model — better to generate them separately (woosh or Stable Audio 3) and mix them (inference, unconfirmed).
- **Video: text contradicting the picture** — the model is conditioned on the picture *and* the description [7]; an extremely mismatched description (e.g. birds for a frame with an engine) gives an uncertain result; a deliberate counterpoint is better done via a separate text→effect generation (unconfirmed).
- **Video without a description**: works (Studio: empty description = sound from the picture only) [3], but the VFlow/DVFlow models used are conditioned on the picture **and** a caption; the authors have separate video-only "OV" variants, which Studio does not use [7] (official). Conclusion: with an ambiguous picture (drawing, abstraction, generated video), **it's worth giving a description**.
- **8 s window**: a longer clip = several generations with different "window start" values; joining and crossfades in editing [1][3] (our configuration); the community splits clips the same way [14] (community).

## Beyond photorealism
- Woosh is a **realistic foley/SFX** model built on Freesound/AudioCaps/WavCaps data [5]; processing vocabulary (tape, distortion, filter, glitch) **is not documented** for Woosh — you can try tags typical of Freesound ("lo-fi", "distorted", "reversed", "glitch"), effectiveness unconfirmed.
- Processed / stylized sounds (tape, granular, "8-bit", tape stop) — **better Stable Audio 3** (it has them in its official examples); use Woosh for raw material that the participant will process in editing.
- **Non-realistic video** (drawing, animation, collage): the model sees the motion but may misrecognize the source → a text description naming the source and the material of the sound (not the style of the picture — "drawing", "animation" say nothing about sound) (inference, unconfirmed).
- No stereo → space and panoramic movement are added in editing [5].

## Motion / time / sound
- **Text→effect**: length from the field (1–10 s, preferably ≤5 s) [1][5]. Describe the course of the sound with simple verbs: "starts…", "…then stops", "passes by", "approaches" (AudioCaps caption style; effectiveness unconfirmed). No stereo — "left to right" won't work [5].
- **Video→sound**: it takes the timing and rhythm of events from the motion in the picture (Synchformer features, 24 fps) [2] (our configuration); **don't give times in the description** ("at 2 seconds") — there is no such control (unconfirmed, not in the documentation). Description = *what* and *what kind*; picture = *when*.
- Description for video: name the **visible** source and its material ("boots on wet snow", not "steps"), optionally the acoustic background of the place.

## Check before sending
- [ ] English; one sentence; 8–25 words (strictly < 77 tokens)
- [ ] Source + action at the start; material/texture; space and distance (optional)
- [ ] No mood, metaphors, tags, weights, `TrackType`, `Length:`
- [ ] No negations ("no music") — Woosh has no negative
- [ ] Text→effect: length ≤5 s (longer only deliberately); long/stereo ambience → suggest Stable Audio 3
- [ ] Video: description consistent with what is visible; clip > 8 s → further windows ("window start"); no times given
- [ ] Reminder: mono output, often quiet — set the level in editing; several seeds; non-commercial license

## Sources
[1] Studio — `modele/sfx/woosh.yaml` and `woosh-wideo.yaml` — our configuration
[2] Woosh service on the Spark — own notes (unpublished) — our configuration
[3] own notes (unpublished) (SFX section) — our configuration
[4] Woosh weights configuration — `~/sfx/Woosh/checkpoints/TextConditionerA/config.yaml` and `Woosh-CLAP/config.yaml` on the Spark (roberta-large, max_sentence_tokens: 77, text_preprocessing: no_op); files from the release https://github.com/SonyResearch/Woosh/releases — official
[5] Woosh: A Sound Effects Foundation Model — technical report (arXiv 2604.01929) — https://arxiv.org/html/2604.01929 — official
[6] GitHub — SonyResearch/Woosh (README, licenses) — https://github.com/SonyResearch/Woosh — official
[7] Woosh — project page with examples — https://sonyresearch.github.io/Woosh/ — official
[8] Sony AI — Introducing Woosh — https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model — official
[9] GamesBeat — interview with the Woosh team — https://gamesbeat.com/sony-ai-releases-woosh-foundation-model-for-sound-effect-generation-exclusive-interview/ — official (authors' statements)
[10] RunComfy — Woosh Sound Effect Generation in ComfyUI — https://www.runcomfy.com/comfyui-workflows/woosh-sound-effect-generation-in-comfyui-text2audio-videosync — community
[11] Stable Audio 3 — technical paper, comparison with Woosh-Flow — https://arxiv.org/html/2605.17991v1 — official (Stability)
[12] AudioCaps: Generating Captions for Audios in The Wild (NAACL 2019) — https://aclanthology.org/N19-1011/ — official (dataset)
[13] Studio — guide `poradniki/woosh.md` — our configuration
[14] Civitai — Woosh video→sound workflow (split into 8 s segments) — https://civitai.com/models/2627712 — community
