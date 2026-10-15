<!-- Model card for the promptmaker. modele: minimax-h3, minimax-h3-fl2va, minimax-h3-referencje, minimax-h3-klatki, fasth3-v2 -->
# MiniMax H3 (+ FastH3 V2) — video with stereo sound

## What it is and what it's good for
- An open "omni" model: picture + **32 kHz stereo sound** (dialogue, singing, effects, music) in a single pass, 24 fps, 4–15 s [3][5] (official).
- Two checkpoints: **FL2VA** (0, 1 or 2 images: text → video, first / last / both frames) and **Ref2VA** (references: ≤ 9 images, ≤ 3 videos of 2–15 s each (≤ 15 s total), ≤ 3 audio files of 2–15 s each (≤ 15 s total), ≤ 12 files altogether) [3] (official).
- Text encoder: **Qwen3-VL-32B** (layer 50). It also sees images and (at 2 fps) frames of the reference videos; **it does NOT see the reference audio** — that goes only to the generator [3][12] (official / code).
- H3 was trained on very detailed descriptions in a fixed format ("Context-IR"). In the cloud, MiniMax rewrites the prompt for the user; **the open weights don't have this — you are the rewriter** and write directly in the IR format [3] (official), [18] (community).
- Strengths: multi-shot with cuts at set times, camera movement, sound synchronized with the action, combining many references into one scene, smooth first→last frame transition [1][3] (official), [26][31] (community).
- **What it does NOT do well:**
  - faces in wide shots (distorted; medium and close shots are fine) [26] (community);
  - silence and pauses — in "empty" moments it may mumble / babble [17][23] (community);
  - loud background under dialogue (the ambience drops when someone speaks; especially Ref2VA) [24] (community);
  - reliable off-screen voice (the character's lips often move anyway) [27] (community);
  - keeping the accents of two speakers apart (the accent "leaks" onto the other character) [30] (community);
  - blinking (characters hardly blink) [22] (community);
  - smooth 2D animation (it comes out "on twos", 12 fps) [16] (community);
  - reliable text in frame (fragile; better added in editing) [31] (community).

## What the participant sets in Studio
A single entry "MiniMax H3" — the variant is chosen automatically based on the files provided [L1] (our configuration):
- **nothing** → text → video (T2VA, FL2VA checkpoint);
- **first frame** → I2VA; **last** → L2VA; **both** → FL2VA;
- **any inspiration** (up to 9 images, up to 3 videos, up to 3 audio files) → **Ref2VA**; in that case **the first/last frame are ignored** [L1].
Separate entries "MiniMax H3 · keyframes" and "FastH3 V2" — see below.

Common fields [L1][L2]:
- **prompt** — a single field, passed **without any processing** to the ComfyUI node (Studio adds nothing). **The image alignment line is not in the workflow — you have to write it yourself** (see Format) [11][L2] (code / our configuration).
- **No negative prompt.** The weights are "CFG-distilled", the workflow uses `BasicGuider` (no negative branch) [3][6][L2] (official).
- **aspect ratio** 16:9 (default), 21:9, 4:3, 1:1, 3:4, 9:16 [L1].
- **resolution** 480p (0.4 MP, 16:9 = 864×480, default) / 720p (0.9 MP, 1280×736) [L1][13]. Natively the short side is 768 px [3]. At 480p the model usually holds the prompt structure (shots, camera, layout) better than at 768p [20] (community), but faces in more distant shots are weaker [26] (community). 720p FL2VA/I2VA: rarely a seed-dependent "frame blackout like a shutter" [28] (community) — change the seed.
- **length** 1–15 s (default 10), step 0.5 s; frames are snapped to a 17n+5 grid at 24 fps (5 s → 124 frames) [L1][L2]. Officially 4–15 s [3]; training range about 124–362 frames (≈5–15 s), shorter ones "untested" [11] (code). **Set ≥ 5 s.**
- **mode**: fast = turbo LoRA (FL2VA 8 steps, Ref2VA and keyframes 4 steps) / quality = 20 steps [L1][L2]. Turbo: "slightly weaker sound and motion" [7] (official).
- **seed** — when comparing prompt versions, keep the seed fixed and change one thing [31] (community).

Ref2VA (inspirations) — details from the code [11][L1][L2]:
- Markers in file order, numbered separately per type: `<Picture 1..9>`, `<Video 1..3>`, `<Audio 1..3>`. Studio shows the marker next to each file.
- **The audio from a video file is not used** (Studio passes only the video picture) → `<Audio n>` means audio files only. Don't write "sound from `<Video 1>`".
- A reference video longer than the clip is trimmed to the clip length; reference images are downscaled to the generation resolution (fine text/detail from the reference is lost at 480p).

Keyframes (`minimax-h3-klatki`) [L1][L2][8][13]:
- Ref2VA checkpoint + 1–3 images pinned to the seconds `czas1..3` (must fit within the length). Optional reference = `<Picture 1>`.
- **The text encoder does not see the keyframes** — they have no markers. Don't write `<Picture 2>` for a keyframe; describe in words what should be visible at that second, and place a cut or an action point there [8] (official).

## Prompt format
- **Language: English** for the whole description; **verbatim in the original language only the spoken lines/sung lyrics (in `<d>`) and text visible in the frame** [1][2] (official); a MiniMax employee: "apart from the content to be generated and the dialogue, everything in English" [15]. A description in Chinese/Polish is sometimes read out loud as a line [15] (community).
- **Length: long and detailed.** Official examples 150–1000 words; Ref2VA `detailed_description` usually **350–500 words** [2][3] (official). Short prompts without references are a typical cause of bad results [18][31] (community). There is practically no character limit in ComfyUI [12] (code). Heuristic (unconfirmed): 1 shot ~120–200 words, 2–4 shots ~250–450.
- **No weights** `(word:1.3)` — the H3 tokenizer has weights disabled, brackets become text [12] (code). **No JSON, no tag lists.** Full sentences, present tense.
- **Don't name what should not be there** (at CFG 1 the word "text" in "no text" adds text). Write positively: "the sign above the door is blank" [6] (official). Note: the official Comfy templates themselves contain "no subtitles…" [13] — stick to the positive rule anyway.

**FL2VA modes (no inspirations)** — line 1 = instruction, then an empty line, then 3 fields separated by empty lines, in this order [1] (official):
- T2VA (no images): no instruction line.
- I2VA (first frame only), verbatim:
  `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.` (the same in community prompts [14])
- FL2VA (both), verbatim (without angle brackets — as in the original); `S.SS` = clip length with 2 decimal places, `N` = number of the last shot:
  `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA (last frame only — the node then has `<Picture 1>` [11]):
  `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
- Fields: `integrated_multimodal_description:` (picture, action, shots, speakers, dialogue, singing, diegetic sound along the timeline) · `overall_soundscape:` (1–4 sentences: ambience, action sounds, breathing, laughter; no dialogue; `N/A` only for total silence) · `non_diegetic_music:` (1–3 sentences: instruments, tempo, rhythm, dynamics — no mood words; `N/A` when there is none) [1].

**Ref2VA (inspirations)** — six sections in this order, all in English [2] (official):
`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`.
- `<Subject N>` = content extracted from a reference (person, place, prop, style, motion); `<Picture N>` separately only when the image is a specific frame/framing anchor or a storyboard; `<Video N>` only for relations to the whole video (editing, continuation, camera/editing structure); `<Audio N>` = a copied signal or a reference [2].
- `summary`: a single-sentence paragraph with a type prefix in brackets: `[reference generation]`, `[keyframe completion]`, `[video editing]`, `[video continuation]`, `[audio reuse]`, `[audio reference]`, joined with ` + ` [2].
- `retention_analysis`: one line per label; image/video: `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference`; audio: `fully_copy` / `partially_copy` / `reference` / `weak_reference`. No `(Sx)` in this section [2].
- `detailed_description`: 1–2 style sentences BEFORE `[Shot 1]`, then the shots; insert labels at the first appearance and where they act ("the shot begins from <Picture 1>") [2].
- The format doesn't have to be copied word for word — what matters is consistent labels and clear relations [25] (community, reply on HF). Comfy: "Ref2VA is very sensitive to wording; precise markers and explicit assignment of which reference controls what" [13] (official).

**Common markers** [1][2] (official):
- Shots: `[Shot 1]` without a time; then `[Shot 2] At 00:03.500, the camera cuts to …` — times increasing and < clip length. Cuts: "the camera cuts to / the shot cuts to / transitions to / changes to / switches to"; dissolve/fade only when wanted.
- Speakers: fixed ID `(S1)`, `(S2)` across all shots; together `(S1,S2)`; a character who doesn't speak — no ID. At the first appearance, describe the voice (age, gender, timbre, pace, accent) OUTSIDE `<d>`.
- Dialogue/singing: `<d>[Language] exact words.</d>` — inside only the language tag and the words. End the line with a period/?/! before `</d>` [2]; a missing period encourages mumbling after the line [17] (community).
- Off-screen voice: exactly `says in an off-screen voiceover:` + after `</d>` "while his/her lips remain completely closed" [1].
- A line across a cut: `<scenetrans>` in both places + "continues seamlessly across the cut" [1]. Cutoff marker: the guide writes `<cutoff>`, while the tokenizer has `<|cutoff|>` [1][12] — unclear; **don't use it**.
- Text in frame: in English double quotes, verbatim, in the original language: `a hand-painted sign reading "…"` [1].

## Prompt skeleton
T2VA / I2VA / FL2VA / L2VA (insert the instruction line only when there are frames):
```
[instruction line — verbatim according to the mode]

integrated_multimodal_description: [Shot 1] [style/medium], [opening shot size and composition], [subject: appearance, clothing, position in frame], [place, light, texture, key props]. [camera movement: type + amplitude + speed as a sentence]. [action: start → development → result], [diegetic sound with the action]. [voice description] (S1) says: <d>[Language] [line].</d> [what they do after the line, lips closed]. [Shot 2] At 00:0[s].[ms], the camera cuts to [new information: place/state/point of view/time], [camera movement], [action], [sound].

overall_soundscape: [continuous ambience], [action sounds in order], [non-verbal sounds].

non_diegetic_music: [instruments], [tempo], [rhythm], [change in dynamics] | N/A
```
Ref2VA (inspirations):
```
subject_definitions:
<Subject 1> is [who/what] in <Picture 1>, [features to preserve].
<Subject 2> is [place/style/motion] from <Picture 2> / <Video 1>, [features].
<Audio 1> is the voice-timbre reference for <Subject 1> (S1). | <Audio 1> is [ambience/music/line] [role].

summary:
[task type + task type] [1 paragraph: what happens, which labels are responsible for what].

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): [marker] - [what is preserved].
<Audio 1>: [marker] - [what is copied / what it is a reference for].

detailed_description:
The target video is in [style/medium, palette, light, texture].
[Shot 1] [as in T2VA, with labels at first appearance] … <Subject 1> (S1) says: <d>[Language] [line].</d> …
[Shot 2] At 00:0[s].[ms], the shot cuts to …

overall_soundscape:
[…]

non_diegetic_music:
[…] | N/A
```
Keyframes: the Ref2VA skeleton; if there is a reference — `<Subject 1> is [who] in <Picture 1>`; summary `[keyframe completion]` (+ `reference generation` if there is a reference); in `detailed_description`, cuts or key moments exactly at the seconds `czas1..3` ("At 00:05.000 … the composition shows [frame described in words]"). Without a reference: omit `subject_definitions` and `retention_analysis`, or keep them with a verbal description (unconfirmed — no example in the sources).

## What works
- **The whole scene first, then the shots**; style and opening composition at the start of `[Shot 1]` [1][6] (official).
- **Every cut = new information** (place, state, point of view, time); if only the framing changes — camera movement instead of a cut [1] (official).
- **Camera as an action, not a goal**: "keep him in frame" doesn't work; "the camera pulls out with large amplitude, matching his walking speed" works [31] (community). One dominant camera move and one main action per shot — especially at higher resolution [20][31] (community).
- **I2VA: anchor → start of the action → development → result**; keep the identity, clothing, colors and layout from the image [1]. **FL2VA: one continuous shot**, describe the path between the states, not two static images; the last frame reached near the end [1] (official). An element that should move despite similar frames (leaves, water): name it as the only animated element and describe its path and return [21] (community).
- **The last frame of the previous clip as the first frame** = continuation of the shot [L1].
- **Describe the sound at every moment** — including "silence" as a quiet ambience (fridge hum, wind); the word "silently" for actions without speech; after a line "closes her lips" [17][23] (community). Unwanted speech in a quiet shot → fill in both sound fields explicitly and generate again [6] (official).
- `non_diegetic_music: N/A` effectively switches off the music (it sometimes leaks through anyway, ~20%) [31] (community).
- **Accent via the language tag**: `<d>[French] English words</d>` produced a French accent where the description "with a French accent" didn't work [19] (community).
- **Blinking, small gestures** — write them explicitly with a time ("she blinks slowly at 00:02") [22] (community).
- **References**: give each one a role (identity / style / motion / camera / voice) — "explicit assignments work much better" [7] (official). When the references carry the appearance, focus the description on the new action [31] (community).
- **Reference voice**: a short recording (~4 s) and explicitly "`<Audio 1>` is the voice-timbre reference for `<Subject 1>` (S1)" — longer ones encouraged babbling at the start [17] (community, single source).
- **A line that goes to the wrong person** → generate it with a voice tool and supply it as that speaker's `<Audio n>`; with many speakers, tie lines to visible events, not to timecodes [6] (official).

## Biases and pitfalls
- **Missing instruction line with frames** — Studio does not add it (the old Studio guide claims otherwise — wrongly) [11][L2].
- **Wrong dialogue format**: correct is `<d>[Polish] …</d>`, not `<d>Polish: …</d>` [1][2] (official).
- **Babble / a "glitch" in the first ~0.5 s**, especially Ref2VA; seed-dependent; replacing `<d>` with quotation marks helped some people, not others [17] (community). Generate several seeds.
- **Too long a line in too short a time**, or **too much free time** after a short line → rushing, repetitions, fillers [31][35] (community). No official words-per-second norm — fit the clip length to the line, leave room to breathe.
- **A narrator named like a character in the frame** ("the man") → the model moves that character's lips. Better "Female narrator voice, saying: …" or a separate voice description with no reference to a visible person [27] (community). Still unreliable.
- **Accent/voice leaking** between two speakers [30] (community) → differentiate the voices strongly (gender, age, timbre), and supply critical voices as `<Audio n>`.
- **Ambience drowned by dialogue** [24] (community) → add important background in editing, or use a shot without dialogue.
- **"TV commercial"/glossy bias** with short, generic prompts (a single opinion) [18] (community) → always name the medium and texture at the start.
- **Faces in wide shots** [26]; **blush/red cheeks building up in Ref2VA** [29] (community) → medium/close shots for faces.
- **A character doesn't speak but has an ID** → speech will appear; IDs only for those who make vocal sounds [1].
- **Mixed languages** (names or action descriptions in the participant's language, e.g. Polish, inside the description) → babble or the description read out loud [15][35] (community). Words in the participant's language only in `<d>` and in the quoted on-screen text.

## Beyond photorealism
- **Style word at the very start of `[Shot 1]`** (Ref2VA: style sentence before `[Shot 1]`). Official list: `Cinematic`, `live-action`, `2D-animated`, `3D CG`, `claymation`, `watercolor`, `vintage film` [1][2] (official).
- **The strongest lever: the image.** In I2VA/FL2VA the style is "derived from the reference image" [1] (official) → make a frame in the target technique (drawing, collage, watercolor) with another Studio model and supply it as the first frame, or as `<Picture n>` with a style role (`weak_reference` / `attribute_transfer`) [2].
- **Drawing/hand-drawn animation** — vocabulary from the official MiniMax skill: crayon, chalk, colored pencil, pastel, rough brush; lines slightly jittering, uneven smudging, frayed edges, a redrawn-every-frame feel; "flat hand-drawn animation" in a live-action space [4] (official). Watercolor/comics (API example): "keep the watercolour texture, visible ink outlines, off-register paper grain" [34] (community). 2D animation will usually come out at 12 fps anyway ("on twos") [16] — for a hand-drawn character that's an advantage.
- **Paper / stop-motion** [4] (official): visible paper fibers, folds, seams, cut edges, visible thickness; frame-by-frame, hand-manipulated motion: small stepped movements, tiny pauses, slight rebounds, pieces sliding and settling; physical shadows; layered paper diorama. Instead of "no smooth CG", write positively about stepped motion.
- **Collage** [4] (official): flat bold color fields, black-and-white halftone photographic cut-outs, colored cardstock accents, torn edges, soft paper shadows; pieces pop in, slide into place, press flat, pause, lock. Sound: paper rustle, scissors, tape peel, page flip [4].
- **Film stock / film / archive**: `vintage film` (official [1]); from API examples (not confirmed locally): "35 mm film look with fine grain, soft highlight halation", "1990s film grain, scanlines, chromatic aberration, light leaks", "VHS tracking artifacts" [13][33] (community/vendor).
- **Comics/ink**: "bold comic-book ink style, heavy linework, limited palette" — Comfy Ref2VA template [13] (official Comfy).
- **Mixing**: live-action + drawn elements works when described as "hand-drawn luminous animation in a live-action space", with clear contact between the drawing and a real hand/object [4][33].
- **Abstraction, pure texture, matter painting** — no sources; unknown how the model responds (unconfirmed). Safer via a frame/reference in that technique.
- `embedding:minimaxh3_…` (community styles) — the files are not confirmed in our installation; **don't use** [6].

## Motion / time / sound
- **Camera = type + amplitude + speed**, as a natural sentence within the shot, not labels at the end [1] (official). Types: Zoom In/Out (focal length), Push In/Pull Out (dolly), Pan Left/Right, Truck Left/Right, Tilt Up/Down, Pedestal Up/Down, Arc Shot, Tracking Shot, Static Shot, Shake Slightly/Strongly, POV, Roll Clockwise/Counterclockwise. Amplitude: `with small amplitude` / `with large amplitude`; speed: `at slow speed` / `at fast speed`; omit medium values [1]. "Dolly in/out" is not in the vocabulary [1] — use push in / pull out.
- **Time**: cuts `At MM:SS.mmm`; the first shot without a time; all times < clip length [1]. Tightly packed timecodes are a common mistake [31] (community); a threshold of "no more often than every ~2–3 s" — unconfirmed. FL2VA — preferably 1 shot [1].
- **Length**: ≥ 5 s (training range ~5–15 s) [3][11]. Dialogue: one speaker and one line per clip when speech quality matters [35] (community); "1–2 short lines per 5–8 s" — heuristic, unconfirmed.
- **Sound — what goes where** [1] (official): dialogue, singing, music heard in the scene (radio, someone playing) and effects tied to a specific action → in the shot, at the moment of the event; background and sounds of the whole clip → `overall_soundscape`; music for the viewer only → `non_diegetic_music` (instruments, tempo, rhythm, dynamics; no "sad/happy").
- **Dialogue in the participant's language**: if it is not among the 11 stably supported languages (ar, zh, en, fr, de, it, ja, ko, pt, ru, es) — Polish, for example, is not — "other languages to varying degrees" [3] (official). Notation: `<d>[Polish] …</d>` (by analogy with `[English]`/`[Chinese]` [1][2]; the `[Polish]` tag is not confirmed by a test). Keep it short and simple, no acronyms or rare proper names [35]. Plan B: record/generate the line with Studio's voice tool and supply it as `<Audio n>` (Ref2VA) with `fully_copy`/`partially_copy`, writing exactly those words in `<d>` [2][6] (official) — or lay the voice in during editing.
- **On-screen text in the participant's language**: in quotation marks, verbatim [1]; text rendering is fragile, diacritics (e.g. Polish characters) unconfirmed → text rather in editing [31].
- **Singing**: song lyrics also go in `<d>[Language] …</d>` [6] (official).

## FastH3 V2 (`fasth3-v2`) — differences
- A DMD2 distillation by FastVideo; same encoder, VAE and **the same prompt format** (T2VA/I2VA/FL2VA/L2VA) [9][10] (official).
- Only these fields: first/last frame, aspect ratio, resolution, length, seed; **no mode and no inspirations** — Ref2VA was not distilled [9][L1].
- HF card: only T2VA was distilled, "FL2VA was not distilled" [10]; Comfy shows I2V with frames as working [9] → with frames, expect weaker fidelity (not confirmed on our side).
- Weaker with difficult motion, fine detail and some of the sound [9][10][32]. Prompts: simpler motion, one main event, fewer cuts. On the Spark it is usually slower than H3 in fast mode [L3] — for comparisons.

## Check before sending
1. Mode according to the files: none / first / last / both / inspirations / keyframes → the right instruction line or the 6-section format.
2. Instruction line verbatim, then an empty line; `S.SS` = clip length, `N` = number of the last shot.
3. Everything in English; the participant's language only in `<d>[Language] …</d>` and in quoted on-screen text.
4. Style/medium at the start of `[Shot 1]` (Ref2VA: before `[Shot 1]`).
5. `[Shot 1]` without a time; subsequent `At MM:SS.mmm` increasing and < length; cut = new information.
6. Every speaker has a fixed `(Sx)` and a voice description; lines end with a period; after a line lips closed / "silently".
7. Both sound fields filled in (`N/A` deliberately); no dialogue in `overall_soundscape`.
8. Zero negations like "no …", zero weights and JSON.
9. Reference markers consistent with the file numbering in Studio; each has a role; no `<Picture n>` for keyframes; no "sound from `<Video n>`".
10. Length ≥ 5 s and matching the amount of dialogue; faces not in wide shots.

## Sources
[1] MiniMax — Video Prompt Writing Guide (T2VA/I2VA/FL2VA/L2VA) — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md — official
[2] MiniMax — Full-Reference Mode (Ref2VA) Guide — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md — official
[3] MiniMax H3 — model card (README) — https://huggingface.co/MiniMaxAI/MiniMax-H3 — official
[4] MiniMax H3 — skills (h3-prompt-writing, handdrawn-live-video-generator, papercraft-stop-motion-explainer, paper-collage-explainer-generator) — https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills — official
[5] MiniMax — blog "MiniMax H3" — https://www.minimax.io/blog/minimax-h3 — official
[6] ComfyUI — MiniMax H3 Prompt Guide — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide — official (Comfy)
[7] ComfyUI — MiniMax H3 native workflows — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native — official (Comfy)
[8] ComfyUI — MiniMax H3 multiframe — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe — official (Comfy)
[9] ComfyUI — FastVideo FastH3 — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo — official (Comfy)
[10] FastVideo — FastH3-8-Step-V2 (HF card) — https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2 — official
[11] ComfyUI — H3 node code (nodes_minimax_h3.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py — official (code)
[12] ComfyUI — H3 encoder code (text_encoders/minimax.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py — official (code)
[13] Comfy-Org — H3 workflow templates (t2v, r2v, multiframe_reference) — https://github.com/Comfy-Org/workflow_templates/tree/main/templates — official (Comfy)
[14] HF #47 "The actual correct system prompt for IT2V" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/47 — community
[15] HF #32 prompts in Chinese (reply from a MiniMaxAI org member + users) — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/32 — official/community
[16] HF #74 "Anime style videos have half the FPS" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/74 — community
[17] HF #76 "Weird gibberish / clipped voice at the very start" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/76 — community
[18] HF #83 "Very bad prompt adherence" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/83 — community
[19] HF #84 "Getting different Accents" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/84 — community
[20] HF #65 "Prompt adherence varies depending on the resolution" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/65 — community
[21] HF #81 "Question about prompting on static elements" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/81 — community
[22] HF #96 blinking — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/96 — community
[23] HF #106 character babbling — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/106 — community
[24] HF #82 "Ref2VA environmental audio feels too quiet" — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/82 — community
[25] HF #71 questions about the Ref2VA guide — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/71 — community
[26] Comfy-Org HF #30 "Why MiniMax H3 Ruins Faces on Wide Shots?" — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30 — community
[27] Comfy-Org HF #44 "problem with off-screen voiceover" — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/44 — community
[28] Comfy-Org HF #67 "FL2VA / I2VA: mid-clip blackout" — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/67 — community
[29] Comfy-Org HF #55 "Ref2VA: red/blush patches" — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/55 — community
[30] ComfyUI issue #15454 "voice/accent conditioning can leak between subjects" — https://github.com/Comfy-Org/ComfyUI/issues/15454 — community
[31] Aireiter — "MiniMax H3 Prompt Review: What Works, What Breaks" — https://aireiter.com/blog/minimax-h3-prompt-review — community
[32] Kombitz — "FastH3 V2: 8-Step MiniMax H3 in ComfyUI" — https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/ — community
[33] fal.ai — "MiniMax H3 Prompting Guide + 44 Video Examples" (API) — https://fal.ai/learn/devs/minimax-h3-prompting-guide — community/vendor
[34] Atlas Cloud — "I Studied 45 Official Prompts" (API) — https://www.atlascloud.ai/blog/tips/minimax-h3-prompt-guide — community
[35] Seedance.tv — "MiniMax H3 Gibberish Fix" — https://www.seedance.tv/blog/minimax-h3-gibberish-fix — community
[L1] Studio: gui/modele/wideo/minimax-h3*.yaml, fasth3-v2.yaml — our configuration
[L2] Studio: gui/workflows/wideo/h3_wideo, h3_referencje_lista, h3_klatki-kluczowe, fasth3_wideo (.api.json) — our configuration
[L3] own notes (unpublished) (measurements on the Spark) — our configuration
