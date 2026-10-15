<!-- Model card for the promptmaker. modele: ideogram-4 -->
# Ideogram 4 (open weights, 9.3B) — text → image, prompt in JSON

## What it is and what it's good for (including: what it does NOT do well)
- A text→image model from Ideogram, trained from scratch, 9.3B parameters, single-stream DiT; the text encoder is Qwen3-VL-8B-Instruct, the VAE comes from FLUX.2 [10][9][2] (official / our configuration).
- Trained **exclusively on JSON-structured captions** that exhaustively describe every element of the image. Plain prose "will not work and will likely trigger a safety warning" [4][14] (official).
- Strengths: lettering in the image (OCR score for English 0.97) [14], **palette control via hex** [4], **element placement via bbox** [4], posters, covers, typography, layout [15][27] (official / community). According to the community, people don't look "plastic", and placement control is very precise [20] (community).
- Weaknesses:
  - The safety filter built into the weights gives false positives: instead of the image you get a grey image with the text "Image blocked by safety filter". It cannot be disabled in ComfyUI [4][15][21] (official / community).
  - No transparency or alpha channel. It draws a checkerboard that only fakes it [23] (community).
  - Layout (mIoU 0.69) and spatial reasoning (0.76) are its weakest scores in its own benchmarks [14] (official).
  - Long text breaks down. Diacritics (e.g. Polish ones) are sometimes dropped or doubled [26] (community, not verified on our setup).
  - Results have little variety [29] (community).
  - It does not edit images and takes no image input (in our Studio it is text→image only) [2] (our configuration).
- Weights license: Ideogram 4 Non-Commercial (code: Apache-2.0) [10] (official). Note: our YAML says "Ideogram Open Model" [1] — a discrepancy in the configuration, not in the card.

## What the participant sets in the Studio (fields, inputs, parameters from our YAML — and how they affect the prompt)
- **prompt**: goes **verbatim** into `CLIPTextEncode` (encoder `qwen3vl_8b_int8_convrot`, type `ideogram4`) [1][2] (our configuration).
  - **Magic prompt does not work here.** The "magic prompt" subgraph in the workflow only assembles the system-instruction text for preview and does not run any LLM [2]. So the promptmaker itself plays the role of the magic prompt and must deliver **complete, valid JSON**.
  - The "template" button inserts a skeleton in the non-photographic variant (`art_style`) [1].
- **aspect ratio**: 16:9 (default), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16, at 1.0 MP. Sides are rounded to multiples of 16 [1][2] (our configuration).
  - Bbox is measured on a 0–1000 scale **on each axis** relative to the frame. When the aspect ratio changes, the boxes stretch along with it [5][3].
  - The model natively supports 256–2048 px and aspect ratios up to 6:1 [7]. The authors report the highest quality at 2048×2048 [10]. Our 1 MP may weaken small text (unconfirmed).
- **profile**: fast = Turbo (12 steps), default = Default (20), quality = Quality (48) [1][2].
  - According to the documentation, CFG 7 runs for most of the steps, followed by a few "polishing" steps at CFG 3 [7] (official).
  - In our setup `CFGOverride` sets cfg 3 from 70% to 100% of the run [2] (our configuration).
  - For small lettering use the "quality" profile [12] (official).
- **seed**: also strongly affects whether a false filter block kicks in [21] (community).
- **There is no negative prompt.** The negative branch is `ConditioningZeroOut` (zeroed text) plus a separate unconditional model in `DualModelGuider` [2][8] (our configuration / official). Exclusions from the hosted Ideogram.ai do not work here [12].

## Prompt format
- **Valid JSON**: double quotes for keys and strings, no comments, no ``` fences. Inside prose, write quotations with apostrophes (`'LETTERING'`) [5] (official).
- **Prose in English, lettering in the original language.** Descriptive fields (`high_level_description`, `style_description`, `background`, `desc`) are always in English. Only the `text` field is in the language of the lettering, e.g. the participant's language, with diacritics typed directly, not as `\u0105` [5][6][4] (official).
- **Keys and their order are strictly defined** (CaptionVerifier warns about unknown keys, missing keys and wrong order) [4][6] (official):
  - top level: `high_level_description`, `style_description`, `compositional_deconstruction`. Any other key is unknown, including `aspect_ratio` (don't add it; only magic prompt v1 returns it, and that contradicts the schema [22][5]);
  - `style_description` for photography: `aesthetics`, `lighting`, `photo`, `medium`, `color_palette`;
  - `style_description` for non-photography: `aesthetics`, `lighting`, `medium`, `art_style`, `color_palette`. **Exactly one of `photo` / `art_style`, never both**;
  - `compositional_deconstruction`: `background`, then `elements`;
  - `obj` element: `type`, `bbox`, `desc`, `color_palette`;
  - `text` element: `type`, `bbox`, `text`, `desc`, `color_palette`.
- **Required fields:** `compositional_deconstruction` with `background` and `elements` [4]. `high_level_description` is "strongly recommended" [4]. In the hosted Ideogram, JSON without it is treated as plain text [11], so **always include it**.
- **Always fill in `style_description`**: "the model has no default style" [12]. Without it, it drifts toward photography (see Biases).
- **`medium`**: the official examples are `photograph`, `illustration`, `3d_render`, `painting`, `graphic_design` (open list, "etc.") [4]. The ComfyUI example also uses e.g. "Mixed-media digital collage" [2].
- **bbox**: `[y_min, x_min, y_max, x_max]`, integers 0–1000, origin in the top-left corner, **y first** [4][18].
- **Colors**: only `#RRGGBB` in UPPERCASE. Up to 16 in `style_description`, up to 5 per element. `color_palette` is always the last key in its block [4][6] (official).
- **Length**:
  - the encoder accepts up to 2048 tokens [9];
  - `high_level_description` has max. 50 words, 1 sentence (2 at most) [5][12];
  - an element's `desc` has 30–60 words [5];
  - the hosted guide recommends ≤5 elements for best quality [12], although the official full example has 17 elements [4]. For us: 2–6 elements.
- **Weights**: syntax like `(word:1.3)` does not exist. Express emphasis through bbox, palette and element order (unconfirmed that weights do harm, but they are not in the schema [4]).

## Prompt skeleton
Non-photographic variant (default for the workshops):
```json
{
  "high_level_description": "[medium/technique] of [main subject + action], [frame layout in 3–6 words], [mood as a physical fact].",
  "style_description": {
    "aesthetics": "[2–5 concrete visual traits: texture, contrast, density, emptiness]",
    "lighting": "[light source + direction + hardness; for graphics e.g. flat/even]",
    "medium": "[illustration | painting | graphic_design | 3d_render | another medium in one phrase]",
    "art_style": "[technique and material: tool, support, trace of the hand, print/grain, palette limits]",
    "color_palette": ["[#BACKGROUND]", "[#SHADOW]", "[#LIGHT]", "[#ACCENT]"]
  },
  "compositional_deconstruction": {
    "background": "[the scene's shell: ground/wall/sky/atmosphere; for graphics: the surface of the sheet]",
    "elements": [
      {"type": "obj", "bbox": [y1, x1, y2, x2], "desc": "[subject identity] — [main traits] — [one distinguishing feature]", "color_palette": ["[#..]"]},
      {"type": "text", "bbox": [y1, x1, y2, x2], "text": "[LITERAL LETTERING\nSECOND LINE]", "desc": "[size, position, one typeface category, one weight, color, technique]", "color_palette": ["[#..]"]}
    ]
  }
}
```
Photographic variant: in `style_description`, instead of `art_style` put `"photo": "[camera/lens/film stock/grain]"` **before** `medium`, and set `medium` to `"photograph"` [4].

## What works
- **A bbox for every main element.**
  - Adding a bbox removed the filter block in a reported case [19] (community).
  - Without bboxes the model flattens the scene into a side view [25] (community).
  - Omit the bbox only for masses that can't be counted (a crowd, a field of flowers, stars) [5] (official).
- **Convert the bbox shape to the aspect ratio.** `[0,0,500,500]` is a square only in a 1:1 frame. For a round or square object you need `(x2-x1)/(y2-y1) ≈ W/H`. Shape errors produce duplicates and wrong scale [5] (official). At 16:9, frame no tighter than waist-up, or use a wide shot [28] (community).
- **One subject = one element.** Describe parts of a body or object in its `desc`, not as separate elements [5].
- **The ground always goes in `background`.** Floor, earth, water, puddles and reflections must not be an `obj` element. Otherwise the model "buries" the figure in a strip of floor [5][12] (official).
- **Don't describe anything twice.** Each thing appears either in `background` or as an element [5].
- **Element order close to reading order.** If an element refers to another one ("below the lettering…"), the other one must come earlier [18] (community/provider). Large objects attached to the wall (background) go in `background` and also as the first element [5].
- **Concrete facts instead of mood.** Words like "moody", "vibrant", "luminous" or "stunning" carry little weight or do harm. Light source and direction, color as hex and material work better [12][5] (official).
- **One value instead of a choice.** No "or", "such as", "various", "implied", "maybe". In typography: one typeface category, one weight and one style [5] (official).
- **Palette**:
  - add the background color (dark background = dark hex in the palette) and a light/shadow pair [4];
  - hex sets the direction, while a color described in words is only an interpretation [18];
  - the palette steers the image strongly, but doesn't fix the color of every pixel [11];
  - for a print effect, 3–4 spot colors are enough [13] (official).
- **Text**:
  - each separate block is a separate `text` element, and the literal wording goes in `text`, not in `desc` [4][18];
  - a name written in an object's `desc` is only "guessed" [18];
  - at most 5–7 words in a single piece of lettering [12];
  - break a long slogan with `\n` at word boundaries [5];
  - write small numbers out in words [12] (official, hosted 4.0).
- **Filter block (grey image with a message):**
  - change the seed [21];
  - add or fix bboxes [19][20];
  - add details to the JSON [12].
  - Don't shorten the prompt into prose (official / community).
- **Iteration**: change only the field you need and leave the rest of the JSON as is. Even so, the whole image may shift [18].

## Biases and pitfalls
- **By default it drifts toward photography.** The magic prompt v1 instruction says to choose `photograph` and an "iPhone aesthetic" when nothing else is specified [5]. The hosted guide says the model has no default style [12]. If you want something else, **always** set `medium` and `art_style` explicitly.
- **The verbs "Paint/Draw/Illustrate" do not mean a medium**, just "show". The medium is decided by the noun (watercolor, ink drawing…) [5].
- **It "populates" empty scenes on its own.** That's how the captions were trained — they described everything [10][5]. When emptiness is the point, say so directly ("minimal, single subject, empty negative space"), because those are the words v1 treats as switching off population [5].
- **The word "warm"** in a photographic grading description produces an amber "AI look". Better to name the light source (candle, sodium streetlight) [5] (official, magic prompt rule).
- **Invented effects**: don't add "glitch", "digital artifacts" or "dissolved" unless they are the goal [5].
- **The safety filter** in local ComfyUI blocked 53–93% of prose prompts depending on the seed, even for a lake at dawn [21]. False positives also happen with JSON [20]. In our setup, a short prose prompt produced a grey image with a garbled message [3] (community / our configuration).
- **The official documentation example without a bbox** (a sailboat) reportedly always gets blocked [19] (community).
- **16:9 as a rotated portrait**: a frame looking like a rotated portrait has been reported. Setting bboxes consistently with the aspect ratio helps [24] (community, weak source).
- **Foreground and background don't blend** [29]. One report also described stubborn anime style in fantasy scenes despite asking for photography [20] (community, single reports).
- **Diacritics in lettering** (e.g. Polish characters) may disappear or get doubled [26] (community). Large lettering is more reliable than small (English: approx. 97% vs approx. 90%) [12]. We have not tested non-English lettering on our setup.
- **Transparent background doesn't work** (VAE without alpha) [23]. For cut-outs there is a separate Studio tool, "background removal" [32] (our configuration).
- **The full official example contains an agency watermark** as a `text` element [4]. So the model knows captions with watermarks and may add them for "archival/press" descriptions (unconfirmed).
- **Prompts from the hosted Ideogram.ai** (style codes, negative prompt, production magic prompt) **do not carry over 1:1**. The magic prompt in the repository "is not the one from production" [4].

## Beyond photorealism
- Mechanism: `art_style` instead of `photo`, `medium` ≠ `photograph` [4]. The documentation and ComfyUI show: soft contemporary illustration, ink with watercolor, flat vector [14], graphic poster [11], mixed-media collage [2].
- **Describe technique and material, not names.** The hosted guide recommends naming the medium and an artist or movement [12]. In our workshops, however, we avoid imitating styles "as a shortcut" [31], so replace the name with a description of the trace:
  - tool: technical pen, charcoal, dry brush;
  - support: handmade paper, cardboard, canvas;
  - application: glazing, impasto, paper cut-out;
  - palette limits.
- **Drawing, illustration**: `medium: "illustration"`. In `art_style` describe the tool, line and fill. v1 counts many hand techniques as illustration: ink, watercolor, oil, vector, pixel art [5].
- **Painterliness**: `medium: "painting"` [4]. Put texture (impasto, glazing, brush marks) in `art_style`/`aesthetics`.
- **Print, grain, risograph, halftone**:
  - describe the worn print texture (risograph halftone, paper tooth, registration shifts), 3–4 spot colors, no 3D and no gradients [13] (official, hosted);
  - according to v1, medium effects (grain, paper texture, halftone, risograph) **do not belong in `background`**, but in the overall description and the style [5];
  - the official business card example, however, has "subtle paper texture" in `background` [4];
  - our rule: the physical surface of the sheet may go in `background`, while technique and grain go in `art_style`/`aesthetics`/HLD.
- **Tape, film, archive**:
  - in the photo variant the `photo` field takes the film stock and grain, e.g. "vintage grainy 35mm film… halftone scan… light leaks" in the ComfyUI example [2], as well as a camera description like "Hasselblad medium format, slightly desaturated" [12];
  - v1 forbids motion blur and "cinematic" grading in ordinary photos unless intended [5].
- **Collage**: the example in our workflow uses `medium: "Mixed-media digital collage"`, photographic cut-outs with a white border, torn paper and stamps. Each cut-out is a separate `obj` with a bbox [2] (our configuration / ComfyUI). Mixing traditions requires a clear boundary between them [13].
- **Abstraction**: no sources (unknown how well the model handles it). Proposal (unconfirmed): `obj` elements as named shapes and patches with a bbox and their own palette, `medium: "painting"` or `"graphic_design"`. Avoid the words "implied/suggested", because v1 demands concrete description [5].
- **Anime/comics** works in JSON (`medium: "anime illustration"`) [29][28], but it's not a workshop goal.

## Motion / time / sound
- Not applicable: a single image. The image can serve as the first or last frame for video models in the Studio (H3, LTX, WAN) [33] (our configuration). In that case set the aspect ratio to match the video, usually 16:9, and leave room in the frame for motion (unconfirmed as a method; the participant's decision).

## Check before sending
- [ ] The JSON parses, has no ``` fences or comments and has only 3 top-level keys (no `aspect_ratio`).
- [ ] `high_level_description` has ≤50 words, is in English and starts with the subject.
- [ ] `style_description` is filled in: exactly one of `photo`/`art_style`, keys in schema order, and `medium` is explicit.
- [ ] Prose is in English. Lettering in `text` is literal, with diacritics typed directly, ≤5–7 words, broken with `\n`.
- [ ] Hexes are UPPERCASE `#RRGGBB`: ≤16 in the style, ≤5 per element, including the background color and a light/shadow pair, and `color_palette` is the last key.
- [ ] Main elements have a bbox `[y1,x1,y2,x2]` in the 0–1000 range, shapes are converted to the frame's aspect ratio, and the ground is in `background`.
- [ ] One subject is one element, nothing is described twice, no "or/such as/various/implied" and no empty mood adjectives.
- [ ] No expectations of a negative prompt or transparency.
- [ ] The "quality" profile for small lettering. On a grey image with "blocked", change the seed and bboxes.

## Sources
[1] Model configuration in the Studio — modele/obraz/ideogram-4.yaml — our configuration
[2] Studio ComfyUI workflow — workflows/obraz/ideogram4_tekst-na-obraz.api.json (nodes 98:24, 98:155, 98:10, 98:147, 98:157, subgraph 134, collage example) — our configuration
[3] Studio guide + test on the Spark 2026-10-04 — poradniki/ideogram-4.md — our configuration
[4] Ideogram 4 — Prompting Guide — https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md — official
[5] Magic prompt system prompt v1 — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/magic_prompt_system_prompts/v1.txt — official (identical to the one in our workflow)
[6] CaptionVerifier — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/caption_verifier.py — official
[7] Inference (sampler presets) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/inference.md — official
[8] Pipeline (asymmetric CFG, unconditional branch) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/pipeline.md — official
[9] Model architecture (max 2048 text tokens) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/model_architecture.md — official
[10] Repository README — https://github.com/ideogram-oss/ideogram4 — official
[11] Ideogram Docs — JSON Prompting (Ideogram 4.0) — https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0 — official (hosted product)
[12] How to JSON prompt for Ideogram 4.0 (18.06.2026) — https://ideogram.ai/blog/ideogram-4-json-prompting/ — official (hosted product)
[13] The Ideogram 4.0 prompt guide — https://ideogram.ai/blog/claude-mcp/ — official (hosted product)
[14] Ideogram 4.0 Technical Details — https://ideogram.ai/blog/ideogram-4.0/ — official
[15] ComfyUI — Ideogram 4.0 Day-0 Support — https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui — official (ComfyUI)
[16] ComfyUI Docs — Ideogram v4 — https://docs.comfy.org/tutorials/image/ideogram/ideogram-v4 — official (ComfyUI)
[17] ComfyUI Docs — BuildJsonPromptIdeogram — https://docs.comfy.org/built-in-nodes/BuildJsonPromptIdeogram — official (ComfyUI)
[18] Runware — Ideogram 4.0 structured prompts — https://runware.ai/docs/models/ideogram-4-0/guides/structured-prompts — community (API provider)
[19] GitHub issue #13 "Prompting documentation bug" (bbox removes the block) — https://github.com/ideogram-oss/ideogram4/issues/13 — community
[20] GitHub issues #5 and #12 (false positives, bboxes, quality of people, drift into anime) — https://github.com/ideogram-oss/ideogram4/issues/5 , https://github.com/ideogram-oss/ideogram4/issues/12 — community
[21] GitHub issue #14 (measuring blocks in ComfyUI vs seed) — https://github.com/ideogram-oss/ideogram4/issues/14 — community
[22] GitHub issue #33 (contradiction: `aspect_ratio` in v1 vs the schema) — https://github.com/ideogram-oss/ideogram4/issues/33 — community
[23] GitHub issue #35 (no transparency) — https://github.com/ideogram-oss/ideogram4/issues/35 — community
[24] GitHub issue #21 (rotated 16:9 frame) — https://github.com/ideogram-oss/ideogram4/issues/21 — community
[25] r/StableDiffusion "Ideogram 4 compared with Krea 2 in natural language prompting" (snapshot) — https://reddit.sentinel-team.org/posts/1ursrrv/snapshots/2026-07-09T23%3A35%3A57.68774Z — community
[26] invideo — Best AI model for text in images (08.2026) — https://invideo.io/blog/best-ai-model-text-in-images/ — community
[27] GoEnhance — Ideogram 4.0 review — https://www.goenhance.ai/blog/ideogram-4-review — community
[28] EvoLinkAI — awesome-ideogram-4.0-prompts — https://github.com/EvoLinkAI/awesome-ideogram-4.0-prompts — community
[29] ipentec — Ideogram 4.0 の画像生成結果 — https://www.ipentec.com/document/ai-image/image-generation-ideogram-4-model — community
[30] Hugging Face — ideogram-ai/ideogram-4-nf4 — https://huggingface.co/ideogram-ai/ideogram-4-nf4 — official
[31] Conversation rules in the Studio — prompty/proces.md — our configuration
[32] Studio description for participants (background removal in the Image area) — own notes (unpublished) — our configuration
[33] Studio README (video models with first/last frame) — README.md — our configuration
