<!-- Model card for the promptmaker. modele: wan-2-2, wan-2-2-tekst, wan-2-2-obraz, wan-2-2-klatki -->
# WAN 2.2 (Alibaba Wan-AI, 14B MoE) — video without sound

## What it is and what it's good for
- An open video model (Apache 2.0) in three Studio modes: **text → video** (T2V-A14B), **image → video** (I2V-A14B), **first + last frame** (the same I2V-A14B, node `WanFirstLastFrameToVideo`) [1][2][3].
- Two "experts": high-noise lays out composition and motion early in denoising, low-noise refines detail [3] (official). That's why motion and framing are decided by what the prompt says clearly and up front.
- Wan 2.2 was trained on aesthetic data labelled for **lighting, composition, contrast, color tone** — it responds to cinematographer vocabulary [3] (official).
- Strengths: smooth motion of a single action, readable camera moves, vocabulary of light and framing, "material" stylizations (felt, clay, puppets, stop-motion, pixel, line drawing) — the stylization examples in Alibaba's guide were made with Wan 2.2 itself [7] (official).
- **What it does NOT do well:**
  - sound — none at all (sound only arrives in Wan 2.5+, closed) [1][7];
  - multiple events in one clip, editing within a clip, long choreography — one shot = one continuous action [7] (official), [19] (community);
  - legible text in the frame (comes out approximate) [7] (official);
  - very fast, violent motion — artifacts, especially in fast mode [8] (official), [17] (community);
  - lengths over ~5 s (81 frames) — see "Motion / time" [5][21];
  - full 360° camera rotations within 5 s — often ignored; keep an orbit within an arc of < 45° [7] (official), [15] (community).

## What the participant sets in the Studio
A single entry, "WAN 2.2"; the variant is chosen automatically based on the frames provided [1] (our configuration):
- **no frames** → text → video (`wan-2-2-tekst`);
- **first frame** → image → video (`wan-2-2-obraz`);
- **first + last frame** → transition between them (`wan-2-2-klatki`).

Fields:
- **prompt** — ONE field, goes straight into the umT5-XXL encoder (`CLIPTextEncode`), with no LLM prompt extension (the official repo recommends "prompt extension" — we don't have it, so you write the prompt in the extended style yourself) [2][3] (our configuration / official).
- **No negative prompt field.** The negative is hard-coded in the workflow — Wan's default negative in the official English translation from the Wan2.1 README ("Bright tones, overexposed, static, … walking backwards"; in T2V with "nudity, NSFW" added) [2][6]. Write everything that should NOT appear as a positive constraint in the prompt (see below).
- **aspect ratio** — 16:9 (default), 4:3, 1:1, 3:4, 9:16; approx. 0.4 MP (e.g. 16:9 ≈ 848×480 = 480p, dimensions ×16) [1]. 480p is the resolution the model is officially supported at [3]. Vertical frame: in fast mode motion can be even weaker (single report) [9] (community).
- **length** — 1–8 s, default 5 s; 16 fps; T2V/I2V step 0.5 s (frames 16n+1), "frames" mode step 0.25 s (4n+1) [1]. Natively 81 frames = 5 s [5] (official).
- **mode**:
  - **fast** (default) — lightx2v LoRA, 4 steps, CFG 1, approx. 30 s → **the negative has no effect** (at CFG 1 ComfyUI skips the negative branch) [2][11][12];
  - **quality** — 20 steps, CFG 3.5 (frames: CFG 4, shift 8), approx. 3.5 min → the negative works [1][2].
- **seed** — a fixed seed for comparing prompt versions (change one thing at a time) [12][19] (community).

Effect on the prompt: in image → video and frames mode **the image provides look and style**, the prompt describes motion. In T2V the prompt carries everything.

## Prompt format
- **Language: English.** The model is bilingual zh/en (umT5); the official examples and the official I2V extender always write in English [3][4] (official). Other languages (including the participant's) are not training languages (unconfirmed how they behave — don't risk it). Chinese is sometimes recommended only for the **Wan 2.1 FLF2V** model ("trained mainly on Chinese pairs") [6] — that is a DIFFERENT model from our frames mode (we use Wan 2.2 I2V), so it doesn't apply; the participant has to be able to read the prompt anyway.
- **Prose, full sentences, present tense.** No SD-style tag lists, no JSON, no section markers.
- **Length:**
  - T2V: approx. 60–120 words (official extender: "60–200", examples ~60–90 words) [4] (official); practitioners: 80–120 words [15][16] (community); another: 25–80 [17] — go with **~60–110**.
  - Image → video / frames: **≤ 100 words**, motion only [4] (official). Often 1–3 sentences are enough.
  - Encoder limit in the original code: 512 tokens [5]; ComfyUI doesn't truncate [13] — longer prompts don't help anyway.
- **Official formula (Alibaba)** [7]:
  - basic: Subject + Scene + Motion;
  - advanced: Subject (description) + Scene (description) + Motion (description: amplitude, pace, effect) + Aesthetic control (light source, type of light, shot size, angle, lens, camera movement) + Stylization;
  - image → video: **Motion + Camera movement** (the image defines subject, scene and style).
- **Order according to the official T2V extender** [4] (official):
  1. if there is a non-film style — **style at the very beginning**;
  2. then up to **4** short aesthetic tags separated by commas (time of day, light source, softness, light angle, color tone, shot size, camera angle, composition), ending with a period;
  3. then 2–4 sentences: subject with appearance → action step by step → background and its motion.
  Note: for 2D/illustration styles the official extender **does not add** film terms (light, lens) [4].
- The model weighs **the beginning of the prompt** more heavily; details at the end are sometimes dropped (community, not tested under controlled conditions) [17]. Put the most important things first.
- **No "literature".** The official extender forbids descriptions of mood and atmosphere ("full of tension", "melancholic vibe") [4]. Translate the mood of a poem into light, color, pace, framing, matter.
- **Negative prompt:** does not exist in the participant's fields. Write exclusions positively: "only one person in the frame", "the camera stays fixed", "she remains seated" [12] (community).
- **Weights `(word:1.3)` — do NOT use.** ComfyUI parses parentheses for umT5 too (parenthesis = weight 1.1, the parenthesis disappears from the text) [13] (code), but whether it improves anything in Wan is unconfirmed. Consequence: **don't use round parentheses at all** (they turn into weights). Use commas for asides.
- Quotation marks for text in the frame — only when text is necessary; it will come out approximate anyway [7].

## Prompt skeleton
Text → video:
```
[style / medium / technique — only if non-photographic]. [time of day], [light source and type], [color tone], [shot size], [angle or composition]. [subject: who/what, how many, 2–3 appearance traits, material]. [action: one motion broken down step by step, with pace: slowly/quickly/gradually]. [camera movement: one, with direction and pace — or "The camera stays fixed."]. [background: 1–2 elements and their motion: wind, water, smoke, light]. [image texture: grain / paper / paint — if relevant]. [positive constraint: what must not appear, e.g. only one figure].
```
Image → video:
```
[camera movement with pace, or "Static camera."]. [subject visible in the image, named briefly] [action step by step with pace and end state: "until …"]. [background motion]. [what stays still].
```
First + last frame:
```
[camera movement leading from frame A to frame B]. [what happens in between: one transformation / one transition, in order]. [pace: gradually / smoothly / suddenly]. [element common to both frames that should stay constant].
```

## What works
- **Aesthetic vocabulary from the official extender** (copy verbatim) [4]:
  - time of day: Day time, Night time, Dawn time, Sunrise time;
  - source: Daylight, Artificial lighting, Moonlight, Practical lighting, Firelight, Fluorescent lighting, Overcast lighting, Sunny lighting;
  - softness: Soft lighting, Hard lighting; light angle: Top lighting, Side lighting, Underlighting, Edge lighting;
  - color tone: Warm colors, Cool colors, Mixed colors;
  - shot size: Extreme close-up shot, Close-up shot, Medium close-up shot, Medium shot, Medium wide shot, Wide shot, Extreme wide shot;
  - angle: Over-the-shoulder shot, Low angle shot, High angle shot, Dutch angle shot, Aerial shot, Overhead shot (skip if you describe a camera movement);
  - composition: Center composition, Balanced composition, Left-heavy / Right-heavy composition, Symmetrical composition, Short-side composition.
- Additionally from Alibaba's guide [7]: High contrast / Low contrast, Low saturation / High saturation, Golden hour sunlight, Rim light, Backlight, Long-focus lens, Wide-angle lens, Ultra-wide-angle fisheye, Tilt-shift lens, Establishing shot, Clean single shot.
- **Camera movement** — words from the guide [7]: camera pushes in / pulls out, camera moves left/right, camera moves forward, camera tilts up, camera pans, tracking shot, orbiting camera movement (arc < 45°), drone shot, **fixed camera**. Meanings according to Alibaba: push-in = closeness/tension, pull-out = scale/loneliness, tracking = accompanying, orbit = weight of the character, static = focus [7].
- **Always name the camera** — including "static camera / fixed camera". Without it the model adds its own drift or a slight push-in (two independent guides, not tested under controlled conditions) [17][19].
- **One camera movement + one action.** Combining dolly + tilt failed in a test; the model favours the first movement and fades out the following ones [15] (community). Put the more important movement first.
- **Motion written as a process**: amplitude + pace + effect ("slowly lifts her hand, the sleeve slides down") [4][7] (official). Pace adverbs: slowly, quickly, gradually, suddenly [7].
- **Background motion** (wind in the grass, drifting clouds, smoke) — the official extender adds it when the scene is static [4].
- **An end state** for the motion ("until the door is fully open") limits drift toward the end of the clip [19] (community).
- **Image → video: don't describe what's visible.** The official I2V extender removes static descriptions and keeps only motion; the most common mistake is a prompt written as for an image generator [4] (official), [19] (community).
- **Frames:** the prompt must fit both frames [14] (official ComfyUI); describe the transition, not the frames themselves.
- Depth: contrast foreground motion with a still background (or vice versa) [16][18] (community).
- Sky: the official extender turns any sky into "clear blue sky", "to avoid overexposure" [4] — a hint that a bright sky blows out easily; for bright outdoor scenes consider low contrast / overcast.

## Biases and pitfalls
- **Fast mode (lightx2v) = slowed-down pace.** The lightx2v team admits: motion is slower than in the base model [9]; default ComfyUI workflows with this LoRA "turn scenes into slow motion" [10]; the LoRA also changes the style [9] (community), with very large motion it produces artifacts and can reverse the direction vehicles drive in [8] (official). Prompt workaround: strong verbs and pace ("quickly", "briskly"), fewer moving elements. When pace is key → quality mode.
- **The negative (quality mode only) works against stylization.** The default negative (in English here, the official translation from the Wan 2.1 README) contains, among others, "style, works, paintings, images" and "static, still picture" [5][6]. Conclusion (not confirmed by testing): in quality mode painterliness / "artwork" is slightly pushed away, and total stillness is penalised. For non-photographic styles **name the technique more strongly** and compare both modes on the same seed.
- **Pull toward realism** — authors of an anime LoRA write about "Wan 2.2's strong bias toward realistic generations" and the insertion of a 3D aesthetic [20] (community). The style must come first and be repeated in the texture description.
- **Default "clean" aesthetic** — without texture cues the image comes out smooth and evenly lit; grain, motion blur and scene lighting have to be named [17] (community, not tested).
- **Don't add subjects** — the official extender forbids adding characters that aren't there (e.g. people in a landscape) [4]. Write a landscape without people as "no people, empty …".
- **Daytime by default** — the official extender picks "Day time" when the prompt doesn't say otherwise [4]; don't leave night/dawn to guesswork.
- **Number of characters** — state the number; many characters and their interactions are a risk [18] (community). The negative contains "many people in the background, three legs, walking backwards" [6] — these are known weaknesses.
- **Contradictory shots** (close-up + wide shot in one) spoil the result [17]; so do contradictory movements [18].
- **Extreme transformations** (day → night in 5 s, several metamorphoses) — weak [18] (community). In frames mode: one transformation.
- **Round parentheses** disappear and change weights [13] — see "Format".
- Real people by name — avoid [7] (official).
- Discrepancies between guides: some mention "24 fps" — that applies to the **TI2V-5B** model [3]; our 14B runs at 16 fps [5]. Formulas for sound, multiple shots ("Shot 1 [0–3 s]"), "Image 1" — those are **Wan 2.5–3.0**, not 2.2 [7]. Don't carry them over.

## Beyond photorealism
- Officially listed stylizations (examples made with Wan 2.2) [7]: **felt style, 3D cartoon style, pixel style / 8-bit, puppet animation, claymation style, black and white animation, stop-motion animation, line art illustration**, surreal style; effects: **tilt-shift photography, time-lapse photography**, bokeh; in examples: **VHS glitch aesthetic, CRT scanline effect** [7].
- Official 2D style example from the extender: technique name at the beginning + description of line and shading at the end ("smooth linework", "cel-shaded"), **without** film lighting terms [4]. Apply this pattern to drawing, gouache, linocut, paper cut-out: technique → content → description of the tool's trace (line, patch, paper texture).
- Watercolor, ink, oil, collage, paper cut-out — **not listed** in official materials; effectiveness unknown (unconfirmed). Describe materially: paper, pigment, edge, layers.
- Tape / archive: practitioners use "16mm grain", "35mm film grain", "high contrast black and white", "bleach-bypass", "kodak portra" [16] (community, no comparative tests). For an archival feel add the era and the medium (e.g. "1960s 16mm footage, scratches") — effect unconfirmed.
- Abstraction: the model wants a subject and an action; describe abstraction as matter in motion (smoke, ink in water, light through glass) with a camera (unconfirmed — inferred from the Subject+Scene+Motion formula [7]).
- **The most reliable route to non-photorealism: image → video or frames** with an image in the target technique (made with another model / by hand). The image provides the style, the prompt only the motion [4][19]. Still, name the technique once in the prompt (e.g. "the charcoal drawing comes alive…") so the model doesn't "realify" it [20] (community).
- Motion in stylizations: "stop-motion" suggests jerky motion, "hand-drawn animation" — frame-by-frame stepping; at 16 fps and in fast mode the effect often comes out smooth and slow (unconfirmed).

## Motion / time / sound
- **No sound.** Don't write dialogue, music or sound descriptions — the model won't generate them, and the words take up space [1]. A speaking character's mouth can move ("speaks") without a voice [4].
- **Length:** 5 s (81 frames at 16 fps) is the native maximum [1][5]. The Studio allows up to 8 s, but beyond ~81 frames the action tends to revert to the initial state (user reports) [21] (community). A longer shot = several clips (last frame → first frame of the next, or frames mode) [21].
- 5 s fits **one camera movement + one subject action** [19] (community); a shorter clip = even less.
- **Pace:** pace words work (slowly/quickly, slow-motion, time-lapse) [7][16]; in fast mode everything slows down anyway [9][10].
- Sentence order = order of events: opening frame first, then the camera movement, then the "reveal" [15][16] (community).

## Check before sending
- [ ] In English, prose, no round parentheses, no weights, no section tags.
- [ ] T2V ~60–110 words; image/frames ≤ 100 words and **motion only** (you don't describe what's visible).
- [ ] Non-photographic style — at the very beginning, with texture/line repeated.
- [ ] Most important things first; max. 4 aesthetic tags; no contradictory shot sizes.
- [ ] Exactly **one** camera movement (or "static/fixed camera") and **one** action with pace and end state.
- [ ] Number of characters stated; no added subjects.
- [ ] Zero mood/atmosphere words — translated into light, color, motion, matter.
- [ ] Exclusions as positive sentences (there is no negative field).
- [ ] No sound, dialogue, text meant to be read, or names of real people.
- [ ] Length ≤ 5 s; when the pace of motion matters — suggest "quality" mode; for stylization — a comparison of modes on the same seed.

## Sources
[1] FSO Studio — `modele/wideo/wan-2-2.yaml`, `wan-2-2-tekst.yaml`, `wan-2-2-obraz.yaml`, `wan-2-2-klatki.yaml`  — our configuration
[2] FSO Studio — `workflows/wideo/wan_2_2_tekst-na-wideo.api.json`, `wan_2_2_obraz-na-wideo.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka_jakosc.api.json`  — our configuration
[3] Wan2.2 README — https://github.com/Wan-Video/Wan2.2 — official
[4] Wan2.2 `wan/utils/system_prompt.py` (T2V/I2V extender system prompts) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/system_prompt.py — official
[5] Wan2.2 `wan/configs/shared_config.py` (sample_neg_prompt, 16 fps, 81 frames, text_len 512) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/shared_config.py — official
[6] Wan2.1 README (English translation of the default negative; FLF2V and Chinese) — https://github.com/Wan-Video/Wan2.1 — official
[7] Alibaba Cloud Model Studio — Text-to-video / image-to-video prompt guide — https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — official
[8] lightx2v — Wan2.2-Lightning (model card) — https://huggingface.co/lightx2v/Wan2.2-Lightning — official (LoRA authors)
[9] lightx2v — discussion #26 on slow motion — https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/26 — community + authors
[10] rzgar — Wan2.2 I2V LightX2V Slow-Mo Fix — https://huggingface.co/rzgar/Wan2.2_I2V_LightX2V_Slow-Mo_Fix — community
[11] Civitai — article on Lightning LoRA, CFG 1 and NAG — https://civitai.com/articles/18711 — community
[12] Hugging Face Forum — How to get the most out of prompts for WAN models — https://discuss.huggingface.co/t/how-to-get-the-most-out-of-prompts-for-wan-models/170354 — community
[13] ComfyUI — `comfy/sd1_clip.py` (parenthesis/weight parsing) and `comfy/text_encoders/wan.py` (umT5 tokenizer) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/sd1_clip.py , https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/wan.py — official (ComfyUI code)
[14] ComfyUI Docs — Wan2.2 tutorial — https://docs.comfy.org/tutorials/video/wan/wan2_2 — official (ComfyUI)
[15] aistudynow — How to Write Better WAN 2.2 Prompts, Tested in ComfyUI — https://aistudynow.com/how-to-write-better-wan-2-2-prompts-tested-in-comfyui/ — community
[16] ViewComfy — Wan 2.2 prompt guide with examples — https://www.viewcomfy.com/blog/wan2.2_prompt_guide_with_examples — community
[17] wan27.org — Wan 2.2 Prompt Guide — https://wan27.org/blog/wan-2-2-prompt-guide — community (commercial site, claims not tested)
[18] VEED — Wan 2.2 Prompting Guide — https://www.veed.io/learn/wan-2-2-prompting-guide — community
[19] Unifically — Wan 2.2 Image-to-Video Prompt Guide — https://unifically.com/blogs/wan-2.2-image-to-video-prompt-guide — community
[20] CivArchive — Anime style Wan 2.2 I2V (LoRA, notes on realism bias) — https://civarchive.com/models/2222779/anime-style-wan-22-i2v — community
[21] Hugging Face — Phr00t WAN2.2-14B-Rapid-AllInOne, discussion #198 (81 frames, action reverting) — https://huggingface.co/Phr00t/WAN2.2-14B-Rapid-AllInOne/discussions/198 — community
