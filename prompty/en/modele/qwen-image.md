<!-- Model card for the promptmaker. modele: qwen-image-2-1 -->
# Qwen-Image 2.1 (Alibaba Qwen) — text → image

## What it is and what it's good for (including: what it does NOT do well)
- Open weights since 20.09.2026, Qwen Research licence (non-commercial); 7B generator (32-layer single-stream DiT), Qwen3-VL 8B text encoder [1][2] (official), [14] (our configuration).
- Natively generates at 2K (e.g. 2752×1536 for 16:9); one model handles both generation and editing [1] (official). Editing has its own card (`qwen-image-edycja.md`).
- Strengths: **long, dense descriptions** (the 2.0 family claims instructions of up to ~1K tokens) [9] (official, version 2.0), **text in the image** with layout and typography (posters, slides, infographics, charts) [1][9][11] (official / community), images with transparency (RGBA) [1] (official).
- What it does NOT do well / risks:
  - hands and feet — a dedicated complaint thread on HF [16] (community, thread title only);
  - "noisy, muddy, overprocessed" results with prompts overloaded with quality and style terms [17] (community, no reply from the authors);
  - text in languages other than zh/en — multilingual support is claimed in general terms, **Polish diacritics (ą, ę, ł, ż…) and other non-English characters are unconfirmed** by any test [9][11][18];
  - the size at which the Studio runs it is ~1 MP, i.e. about a quarter of the native 2K area [14] (our configuration); small text and fine detail may suffer from this (unconfirmed).

## What the participant sets in the Studio (fields, inputs, parameters from our YAML — and how they affect the prompt)
Source: `modele/obraz/qwen-image-2-1.yaml` + `workflows/obraz/qwenimage21_tekst-na-obraz.api.json` [14] (our configuration).
- **prompt** — a single field. It goes to `TextEncodeQwenImage21` (Qwen3-VL 8B). The encoder wraps the text in a chat template with the system message "Comprehend and analyze the provided prompt." and then cuts that system part off [3] (ComfyUI code).
- **No negative prompt field.** In the workflow `negative_prompt` = empty and **CFG = 1** — at CFG 1 ComfyUI skips the negative branch entirely [2][5] (official). Whatever should be absent, you write affirmatively.
- **aspect ratio** — 16:9 (default), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16; **1.0 MP** (ResolutionSelector node, multiple of 8). **Do not put the aspect ratio in the prompt** — the official expander forbids writing aspect ratio, resolution and pixel counts into the description [14] (our configuration / official PE system prompt).
- **seed** — the same seed goes to the generator and to the expander. Fixed seed = comparing prompt versions.
- **steps** (advanced) — 10–50, default 25; euler/simple sampler. Official examples: 40 steps [1]; ComfyUI: hands "settle" at about 30 steps, 40 steps reduces "shimmering" in dense details [2] (official).
- **"the model expands the prompt itself"** (advanced, default OFF) — switches to a prompt rewritten by Qwen3.5 9B PE-T2I (Qwen's official expander) with our system prompt (a single English paragraph, no JSON), **with thinking mode** (`thinking: true`, `max_length` 8192, so that the reasoning doesn't truncate the answer) [14] — as in the official example on the PE card (`enable_thinking=True`) [6]; ComfyUI's default templates after the 30.09.2026 correction have thinking turned off [8], but practitioners report that without it the PE produces weaker prompts [7] (community). Cost: generation takes longer (estimated +1–2 min for reasoning; not measured). Conclusion: **when the promptmaker writes the prompt, leave the switch off** — the PE will rewrite everything its own way (decide the framing, invent the rest of the scene). Turning it on only makes sense as "show me the model's interpretation" for a 3-word idea.

## Prompt format (language, length, structure, tags, negative, weights)
The best template = what the official PE-T2I expander feeds the model. Its rules are in our workflow (node 459:475) [14] (our configuration, text based on the official PE [6]):
- **Language: English.** The PE always writes the description in English, regardless of the language of the request; exception: **text visible in the image stays in its own language and script** [6][14] (official). Qwen is strongest with Chinese text [10] (official, Qwen-Image 1.0), but the participant must be able to read the prompt, so the prose is always in English.
- **Form: one continuous paragraph of prose**, present tense, third person, declarative sentences. A description of the finished image "as an observer sees it", not an instruction ("create…", "make sure…", "you") [14].
- **Length:** the PE aims at **about 20 sentences, 400–500 words** (~25 words per sentence) — the same for a short and a long request; a dense frame longer, a quiet single motif shorter [14]. The older Qwen-Image 1.0 expander aimed at < 200 words [12] — that's a different version, don't apply it.
- **Order (per the PE)** [14]:
  1. **opening sentence (~20 words)**: orientation + **style** + **medium noun** (photograph / illustration / poster / page / scene / portrait / graphic…) + subject + background and palette. The medium must never disappear.
  2. **background and surface** right after the opening (not at the end);
  3. **a pass through the frame**: top band → left side, centre, right → bottom band. Or, when one motif fills the frame: background and how it falls off → pose and place in the frame → head/face → body, each item of clothing and surface → what it holds/touches → edges;
  4. **8–14 position phrases** (upper-left, along the lower edge, behind the left shoulder…), reaching the corners and edges; about 1/3 of sentences start with a position phrase;
  5. **every piece of text in the frame** in reading order (see below);
  6. **a separate sentence about lighting**: source, direction, quality, shadows and highlights ("The lighting is…");
  7. **one closing sentence** about the whole: balance, palette, style, mood ("The overall composition…"). Only one.
- **Text in the image** [14][6] (official):
  - verbatim, **in straight double quotes**, in the original script, character by character with punctuation;
  - for each piece of text: where it sits, weight, colour, upper/lower case, relative size ("a bold black headline across the top reads "…"");
  - describe a line break in words ("a second line reads…"), no newline character inside the quotes;
  - text that shouldn't be legible (a distant sign, fine print) → call it "blurred / indistinct / too small to read", don't invent letters;
  - **don't add text the participant doesn't want** — about 1/3 of images have no text at all.
- **No "quality boosters"**: "masterpiece", "8K", "highly detailed", "award-winning" — the PE forbids them [14]. (The example on the HF card has "8k", but that's a demo prompt [1].)
- **Colours with qualifiers** (deep navy, muted olive, warm terracotta), **material instead of a bare noun** (coarse linen, weathered wood, paper fibre, visible brush strokes), **enumerate, don't summarise** ("several items" = error), small numbers in words, age as a life stage/decade, objects by class, not by brand [14].
- **Negative prompt:** none (CFG 1) [2][14]. Phrase constraints affirmatively: "the street is empty except for…", "the background is a flat, untextured off-white".
- **Weights `(word:1.3)` — NO.** The Qwen3-VL tokenizer in ComfyUI has `disable_weights=True`: brackets and numbers go to the model as plain text [4] (ComfyUI code). Also avoid brackets as decoration.
- **No JSON, headings, lists, markdown** — the PE returns a clean paragraph; JSON with `wh_ratio` is only the expander's output format, not the generator's input [6][14].
- **Transparency (RGBA):** official pattern: start with "This is an RGBA image with transparency.", describe the motif, end with "The image has alpha channel and the background is transparent." [1] (official). Whether the Studio saves the alpha channel in the PNG — unconfirmed.

## Prompt skeleton
```
The image is a [orientation: wide / vertical / square] [style: hand-drawn / watercolour / flat-vector / archival / cinematic…] [medium: photograph / illustration / collage / poster / page…] of [subject], [background and palette: 2–3 qualified colours].
[Background and surface: what it's made of, texture, how far and how sharp].
[Top band: what occupies the top edge]. [On the left side of the frame, … ]. [In the centre, … subject: pose, gaze direction, appearance, each item of clothing with colour and material]. [On the right side, … ]. [Across the lower third / along the bottom edge, … ].
[Text, in reading order: where, typeface/weight, colour, size, reads "EXACT TEXT"].
[Texture of the medium: grain / paper fibre / brush strokes / halftone / smudges — concretely, where visible].
The lighting is [source], [direction], [quality: hard/soft/flat], [shadows and highlights].
The overall composition [balance/symmetry], [palette], [style], [mood].
```

## What works
- **A spatially described frame** — position phrases at the edges and in the corners, not just in the centre; this is the core of the official PE [14].
- **A single style word in the opening sentence** (may be repeated in the closing one) instead of scattered adjectives [14].
- **Material and texture** give concreteness: "matte", "brushed metal", "frosted glass", "grain", "scuffs", "paper fibre", "visible brush strokes" [14].
- **Physical consistency**: shadows from the light, reflections consistent with the scene, consistent object scale — the PE explicitly requires this; describe impossible things the way the image shows them, keep the rest of the scene consistent [14].
- **Specifics instead of generalities**: sentences with a subject, pose, light source, film/lens reference work better than a general description [19] (community, vendor review).
- **For a poem:** translate mood into light, colour, matter and arrangement — the PE asks you to describe what is visible and leaves mood to a single closing sentence [14].
- **Fixed seed, change one thing at a time** [2] (official).

## Biases and pitfalls
- **Drift towards a "professional" finish**: the 2.x family boasts "more photorealistic details, texture and lighting" [9][18] (official). No medium specified = most often a polished photograph/render (untested, inferred from [9]). Always name the medium.
- **Style overload** ("hyper-realistic, photorealistic detail, high contrast, dramatic volumetric lighting…" all at once) → reports of "noisy, muddy, overprocessed" [17] (community). One style word, one lighting sentence.
- **Invented text**: the model readily adds signs and labels — when the image should have no text, don't mention signs, screens, covers; describe surfaces as smooth/blank [14].
- **Polish (and other non-English) diacritics**: unconfirmed. Short text, exactly in quotes; check the result letter by letter, try several seeds if it fails. When the text is crucial, consider Ideogram 4 in the Studio ("text in images") [15] (our configuration).
- **CFG**: not exposed to the participant. For reference: CFG ~2 holds a dense prompt and small text better, but oversharpens edges; CFG 5 breaks things, 0.5 breaks the image [2] (official). A reply on HF: in generation you can raise CFG and use a negative, in editing don't raise it [13] (community).
- **Numbers and sets of objects**: enumerate each element separately; "several", "various" = the model improvises [14].
- **Faces of specific people / brands**: the PE describes objects by class; a name or brand only when the participant has decided on it [14].

## Beyond photorealism
- **Medium in the first sentence, as a noun**: "illustration", "ink drawing", "watercolour painting", "collage", "poster", "page", "sheet" — the official PE style list includes watercolour, hand-drawn, flat-vector, isometric, retro, minimalist, 3D-rendered [14].
- **Collage / graphics**: the sample prompt in our workflow (official ComfyUI template) shows a working vocabulary: "mixed-media graphic collage", "flat vibrant planes", "overlapping circles", "dense micro-halftone dot matrices", "vector topographic contour lines" [14]. Describe the collage layers like elements of the frame — each with a position.
- **Drawing / painting**: describe the tool and its trace: "graphite hatching", "visible brush strokes", "pigment pooling at the edges", "paper fibre showing through" (material vocabulary from the PE [14]; the specific painterly phrases — untested).
- **Tape / archive / grain**: describe texture as what is visible in the image (grain, scratches, discolouration, blurred edges), plus one lighting sentence. Film vocabulary (film stock, lens) works as a concrete anchor [19] (community). Don't mix with "crisp, razor-sharp".
- **Abstraction**: frame divided into regions → describe the regions (top band, left, centre, right, bottom) with shape, colour, edge and texture; lighting "flat even ambient light" [14].
- **Animation / flat graphics**: "flat-vector", "cel-shaded", "flat colour fills with thin outlines"; flat lighting. Don't add a lens or depth of field.
- A clash of registers (e.g. photo + cartoon without justification) — make it deliberate and describe it spatially ("a hand-drawn figure pasted onto a black-and-white photograph"), otherwise the model averages them.

## Motion / time / sound
Not applicable (static image). If the image is to be the **first frame of a video** in the Studio — set the aspect ratio to match the video (usually 16:9), leave room in the frame for movement, avoid small text (video will blur it).

## Check before sending
- [ ] Prose in English; text in the frame in its own language, in straight `"…"`, verbatim with all diacritics.
- [ ] First sentence: orientation + style + **medium** + subject + background/palette.
- [ ] Frame traversed spatially, position phrases reach the corners and edges.
- [ ] A separate lighting sentence; one closing sentence.
- [ ] None of: "masterpiece/8K/highly detailed", weights `( :1.3)`, JSON, aspect ratio/resolution in the text, "create/make sure" instructions.
- [ ] Exclusions phrased affirmatively (there is no negative).
- [ ] No text the participant didn't want.
- [ ] Switch "the model expands the prompt itself" — recommend OFF when the prompt is already complete.
- [ ] ~250–500 words; fewer for a single quiet motif.

## Sources
[1] Qwen/Qwen-Image-2.1 — model card — https://huggingface.co/Qwen/Qwen-Image-2.1 — official
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — official (ComfyUI)
[3] ComfyUI — comfy/text_encoders/qwen_image21.py (encoder chat template) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — official (code)
[4] ComfyUI — comfy/text_encoders/qwen3vl.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — official (code)
[5] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21: negative, resolution) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — official (code)
[6] Qwen/Qwen-Image-2.1-PE-T2I — expander card — https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I — official
[7] ComfyUI Wiki — Qwen-Image 2.1 Prompt Enhancer Models Run in ComfyUI — https://comfyui-wiki.com/en/news/2026-09-22-qwen-image-2-1-prompt-enhancer — community
[8] Comfy-Org/docs PR #1843 — correct the Qwen Image 2.1 prompt enhancer defaults — https://github.com/Comfy-Org/docs/pull/1843 — official (ComfyUI)
[9] Qwen-Image-2.0 Technical Report (arXiv 2605.10730) — https://arxiv.org/abs/2605.10730 — official (version 2.0)
[10] QwenLM/Qwen-Image — README (earlier versions, PE recommendations) — https://github.com/QwenLM/Qwen-Image — official
[11] Qwen-Image: Crafting with Native Text Rendering (1.0 blog) — https://qwenlm.github.io/blog/qwen-image/ — official (version 1.0)
[12] QwenLM/Qwen-Image — src/examples/tools/prompt_utils.py (1.0 expander, < 200 words) — https://github.com/QwenLM/Qwen-Image/blob/main/src/examples/tools/prompt_utils.py — official (version 1.0)
[13] HF discussion #14 — CFG and negative in the default code — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/14 — community
[14] Our configuration: modele/obraz/qwen-image-2-1.yaml; workflows/obraz/qwenimage21_tekst-na-obraz.api.json (nodes 459:452, 459:458, 459:471, 459:474, 459:475 = PE system prompt) — our configuration
[15] Our configuration: own notes (unpublished) (Ideogram 4 for text) — our configuration
[16] HF discussion #29 — 手脚的问题就解决不了了? (hands and feet) — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/29 — community
[17] HF discussion #56 — Qwen 2.1 image quality issue — noisy and muddy results — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/56 — community
[18] eesel — Qwen Image 2.1 review — https://www.eesel.ai/blog/qwen-image-2-1-review — community
[19] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — community (vendor)
