<!-- Model card for the promptmaker. modele: qwen-image-2-1-edycja, qwen-image-edit-2511 -->
# Image editing by instruction: Qwen-Image 2.1 Edit and Qwen-Image-Edit 2511

> Two DIFFERENT models with different syntax for referring to images. First check which one the participant has chosen.
> **2.1 Edit → `<image1>`, `<image2>`**. **Edit 2511 → "image 1", "image 2"** (never `<image1>`).

## What it is and what it's good for (including: what it does NOT do well)
- **Qwen-Image 2.1 Edit** (`qwen-image-2-1-edycja`) — the same 7B model as 2.1 generation, with a Qwen3-VL 8B encoder; officially up to 10 reference images, in the Studio **2** [1][2] (official), [20] (our configuration). Non-commercial licence. Preserves the identity of people and products; local editing by painting over part of the image with a colour [1][2].
- **Qwen-Image-Edit 2511** (`qwen-image-edit-2511`) — the older Edit line (20B, Qwen2.5-VL 7B encoder), Apache 2.0; in the Studio up to 2 images [5][21]. New compared with 2509: less image "drift", better character consistency (including group photos built from two separate people), built-in effects of popular LoRAs (lighting control, new viewpoints), material swaps in industrial design, construction lines [5][6] (official).
- The Edit line (2509) works best with **1–3 images**; it also accepts depth maps, edge maps and keypoint (pose) maps as input [7] (official, version 2509 — unconfirmed for 2511).
- What they do NOT do well:
  - 2.1: consistency across multiple references weakens from about 3 images; in profile views the hairstyle can "shift" [10] (community, early review); complaints about lighting, references and face stability [11] (community, thread title only). It tends to redraw a larger part of the frame than asked [12] (community).
  - 2511: image shift/zoom relative to the input ("pixel drift"), "plastic skin" [16][17] (community); fast mode loses texture (fur comparison, 40 vs 4 steps) [14] (community).
  - Both: Polish (and other non-English) diacritics in rendered text — unconfirmed.

## What the participant sets in the Studio (fields, inputs, parameters from our YAML — and how they affect the prompt)
Source: YAML + workflows [20][21] (our configuration).

**Qwen-Image 2.1 Edit**
- **image 1** (required) = **the canvas**: this is the image being edited; the result has **its size** (workflow `resolution: 0` → native size rounded to a multiple of 32) [2][3][20]. Large photo = slow (3000×4000 ≈ 12 MP) [2] (official).
- **image 2** (optional) = source of a material, outfit, character, style.
- **instruction** — a single field → `TextEncodeQwenImage21`. The encoder **itself inserts a `<image1>`, `<image2>` tag before each image** [4] (ComfyUI code) — which is why in the instruction you refer to them exactly like that: `<image1>`, `<image2>` [2] (official).
- No negative (empty, CFG 1) [2][20]. **steps** 10–50, default 25; small local changes already work at low step counts, rebuilding the whole frame needs the full 25 [2] (official).
- **"the model expands the instruction itself"** (default OFF) — the official PE-I2I (Qwen3.5 9B, looks at the images) with the official system prompt in our workflow, with thinking mode (since 12.10; officially the PE is trained for it — about 1–2 min longer) [20]. When the promptmaker writes a precise instruction — leave it OFF.

**Qwen-Image-Edit 2511**
- **image 1** = canvas; before editing it is scaled by the `FluxKontextImageScale` node to about 1 MP (the nearest Kontext resolution) — the result has that size, not the original [21][13].
- **image 2** = reference (material, character, scene).
- **instruction** → `TextEncodeQwenImageEditPlus`. The encoder prepends "Picture 1: [image] Picture 2: [image]" to the text, plus the system text "Describe the key features of the input image…, then explain how the user's text instruction should alter or modify the image" [8] (ComfyUI code).
- **mode**: **fast** (default) = Lightning LoRA, 4 steps, CFG 1, about 30 s; **quality** = 40 steps, CFG 4, about 7 min [21]. Negative empty, not editable. The workflow already has `index_timestep_zero` (a reference method against drift/"plastic") [21][17].
- Official repo: "without rewriting the instruction, editing can be unstable" [9] (official) — in our setup the promptmaker is the rewriter.

## Prompt format (language, length, structure, tags, negative, weights)
- **Language: English** (plain prose). Official PE-I2I: description in Chinese only for an instruction in Chinese, in English for all other languages [20] (official). 2511: official examples in English and Chinese [5][9]. Not Polish, not the participant's language.
- **Text in the image** — in double quotes, verbatim, in its own language, preserving capitalisation; do not translate [9][20] (official). Language of the text: (1) if the participant gave the words/language — use those; (2) if the image already contains text — the dominant language in the image; (3) otherwise — the language of the participant's request. One language only, no "PL/EN" pairs [20].
- **Form: an instruction, not a description of the finished image.** Start with the operation (Replace / Change / Remove / Add / Turn / Place / Relight / Restore…) [20] (official). A "generator-style" description makes the model ignore the input [15] (community, Edit Plus).
- **One paragraph, no lists, JSON or headings; no aspect ratio or resolution** [20].
- **Length:** concise — the official Edit expander (2511) is told to shorten and limit descriptiveness [9] (official). 2.1: as much as needed so that nothing is left to guess; a simple swap = 1–3 sentences; "a new scene with this motif" (photo shoot, poster, composition from two images) = build the scene, lighting and layout more fully [20] (official).
- **Structure (4 parts)**: operation → target (what, where: "the man on the right") → specification of the change (concrete: colour, material, style) → **preservation clause** ("keep … unchanged") [15][13][20].
- **Keep the preservation clause short and wholesale**: name what stays **by type and location**, do not describe its appearance ("keep the face, pose, background and lighting unchanged"). The more precisely you describe something that was meant to stay, the more the model will redraw it [20] (official).
- **Affirmatively**: "keep the background identical to the input" instead of "do not change the background" [20] (official).
- **Negative**: no field (2.1: CFG 1; 2511: empty, not editable) [20][21]. Do not use weights `( :1.3)` — both paths have `disable_weights=True`, brackets go through as text [18] (ComfyUI code).

**Referring to images**
- **2.1:** with ≥ 2 images **`<image1>`, `<image2>` are mandatory** — not "image 1", "first image", "obraz 1" [20][2] (official). With one image the tag is not required (the official PE only uses it from 2 images) — write "the image"; the encoder tags a single image as `<image1>` anyway [4], so `<image1>` is not an error either. State the role of each image: which one is the canvas (composition and everything else stays), what you take from which [20].
- **2511:** "image 1", "image 2" (the default instruction in our workflow) [21]; the encoder internally calls them "Picture 1/2" [8], the official SGLang example uses "Figure 1/2" [9] — all three are plain text; pick one and stick to it (comparative effectiveness unconfirmed). Image order matters [5][13].
- Identity from a reference: **point to the image, don't describe the face in words** — a verbal description makes the model regenerate and spoils the likeness [20] (official).

## Prompt skeleton
Change on a single image (2.1 and 2511):
```
[Operation] [target + position in the frame] [into what: concrete — colour/material/shape/style, to a strong, clear degree]. [If something disappears or moves: what appears in the revealed area]. Keep [what stays: type + location, wholesale] unchanged.
```
Two images — Qwen-Image 2.1:
```
Using <image1> as the canvas, [operation] [target in <image1>] with [element] from <image2>, [how it should fit: scale, lighting, perspective]. Keep [face/pose/background/lighting] of <image1> unchanged.
```
Two images — Edit 2511:
```
[Operation] the [target] in image 1 [with / to] the [element] from image 2, [fit: lighting, scale, perspective]. Keep [what stays] in image 1 unchanged.
```
Change of medium/style:
```
Turn the image into [medium] with [2–4 visible features: line, fill, ground texture, palette]. Keep the composition, [characters/objects] and their positions unchanged.
```

## What works
- **Full editing strength + freeze everything else**: the official PE-I2I principle — change exactly the named attribute **strongly and unambiguously**, keep everything else faithful to the input. Two symmetrical errors: "leakage" (changing something that wasn't named) and "under-editing" (the result looks like the input) [20] (official).
- **"change nothing else in the frame"** at the end — because 2.1 redraws more than asked [12] (community).
- **Swap**: "Replace Y with X" [9] (official). **One operation per instruction**, complex things as a chain (result → new input) [15] (community).
- **Removal**: describe the object and its location ("the second person from the left"), and fill the revealed area consistently with its surroundings, with lighting and shadow [15][20].
- **Local editing (2.1)**: the participant paints over part of image 1 with a colour (e.g. red) before uploading; in the instruction name the colour: "…in the red-marked area"; if that colour might appear in the result, add the target colour [2] (official).
- **Text**: quote the old and the new text; lock the typography (typeface, colour, position), otherwise it drifts to a default font [15] (community, Edit Plus); officially: position/colour/layout only if the participant asks for it [9].
- **Photos of people**: identity (age, gender, hairstyle, facial expression, outfit) stays, expression changes "subtle and natural" [9] (official). Skin: "natural pores, fine detail, texture that matches the lighting of the scene" [17] (community).
- **Old photo**: official template "Restore and colorize the photo." [9] (official).
- **Lighting (2511)**: lighting control and new viewpoints are built in [5][6]; the community starts such instructions with "Relight …" + a description of the light [16] (community, unconfirmed).
- **References with similar framing, perspective and lighting** combine better [13] (community).
- **2511 fast mode for tests, quality for the final** — Lightning changes texture [13][14] (community).

## Biases and pitfalls
- **Mixed-up reference syntax** (`<image1>` in 2511 or "image 1" in 2.1) — the most common error with this pair of models [2][4][8].
- **Leakage**: sharpening that changes colours; a style that changes the face; an outfit change that loses an accessory; "helpful" tidying of the frame [20] (official). Don't ask for anything the participant didn't ask for.
- **The input's medium is its "identity"**: a photo stays a photo, a drawing stays a drawing, unless the instruction explicitly targets the medium [20] (official). If you want a change of medium — name it directly and strongly.
- **Drift / zoom (2511)**: the image can shift by a few pixels or zoom in [16]; hence the clause "keep the framing and camera angle unchanged" for local edits (community).
- **"Plastic" skin (2511)** — reported on Reddit [17] (community); `index_timestep_zero` is already enabled in our setup [21]; ask for skin texture in the instruction.
- **Result size**: 2.1 = size of image 1; 2511 = ~1 MP based on image 1. Changing the aspect ratio by instruction won't work — name canvas extension explicitly as "outpainting" (2.1) [20] or crop the image beforehand [15].
- **Multiple characters from two photos**: 2511 is better at this than 2509 [5]; 2.1 weakens with ≥ 3 references [10].

## Beyond photorealism
- **Style change**: describe the style by its **key visual features**, not by its name alone [9] (official); with several changes at once — put the style description at the end of the instruction [9]. Syntax example: "Make this look like a watercolor painting." [19] (community) — expand with features: pigment blooms, white paper showing through, soft edges.
- **Style from image 2**: when stylising from a reference, describe the reference's style and keep the canvas content [9] (official). 2.1: "Render <image1> in the visual style of <image2>: [features]. Keep the content and composition of <image1> unchanged."
- **Strength**: a change of medium must be **unambiguous** — otherwise the result looks like the input ("under-editing") [20]. Name the trace of the tool: line, hatching, flat colour fill, halftone, grain, scratches.
- **Archival look / tape**: describe the visible effects (grain, discolouration, scratches, softened edges) and what stays untouched. The opposite direction has an official template ("Restore and colorize the photo.") [9].
- **Collage**: 2 images → "Place [element] from <image2> / image 2 onto [location] in <image1> / image 1 as a [cut-out paper / torn photo] collage element, [edge, shadow]" — the placement syntax itself is official [13][19], the collage effect is untested.
- Style LoRAs: the Studio doesn't expose them here [20][21].

## Motion / time / sound
Not applicable. When the edit is meant to produce a frame for video (e.g. first/last frame) — keep the framing and camera angle fixed ("keep the framing, camera angle and all positions unchanged") so that both frames match.

## Check before sending
- [ ] Which model? **2.1 → `<image1>`/`<image2>`** (one image: tag unnecessary, "the image"); **2511 → "image 1"/"image 2"**.
- [ ] Starts with the operation (a verb), not with a description of the finished image.
- [ ] Change named concretely and strongly; the role of each image is clear (canvas vs source).
- [ ] Preservation clause: short, wholesale, affirmative ("keep … unchanged"), without describing the appearance of what stays.
- [ ] Text in `"…"`, verbatim, one language, following the language rule.
- [ ] One operation; complex ones — chained in several steps.
- [ ] None of: weights, JSON, aspect ratio, "no …"-style negatives.
- [ ] Identity from a reference — pointed to via the image, not described in words.
- [ ] 2511: fast for tests, quality for the final. 2.1: large input images = slow.

## Sources
[1] Qwen/Qwen-Image-2.1 — model card — https://huggingface.co/Qwen/Qwen-Image-2.1 — official
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — official (ComfyUI)
[3] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21: resolution 0 = native size ×32) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — official (code)
[4] ComfyUI — comfy/text_encoders/qwen_image21.py (`<imageN>` tags inserted before images) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — official (code)
[5] Qwen/Qwen-Image-Edit-2511 — model card — https://huggingface.co/Qwen/Qwen-Image-Edit-2511 — official
[6] Qwen blog — Qwen-Image-Edit-2511: Improve Consistency — https://qwen.ai/blog?id=qwen-image-edit-2511 — official (content from search-engine snippets; JS-rendered page)
[7] Qwen/Qwen-Image-Edit-2509 — model card — https://huggingface.co/Qwen/Qwen-Image-Edit-2509 — official (version 2509)
[8] ComfyUI — comfy_extras/nodes_qwen.py + comfy/text_encoders/qwen_image.py (TextEncodeQwenImageEditPlus: "Picture N:", system template) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image.py — official (code)
[9] QwenLM/Qwen-Image — README + src/examples/tools/prompt_utils.py (polish_edit_prompt) — https://github.com/QwenLM/Qwen-Image — official
[10] OrcaRouter — Qwen-Image 2.1 shipped quietly: inside the PE-I2I rewriter — https://www.orcarouter.ai/blog/qwen-image-2-1-open-weights-research-license — community
[11] HF discussion #11 — 光影，参考能力，脸不变能力仍不及预期 — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/11 — community (title only)
[12] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — community (vendor)
[13] RunComfy — Qwen Image Edit 2511 in ComfyUI — https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing — community
[14] Search results: comparison of 40 steps vs Lightning 4 steps (fur) — https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning — official (LoRA) / community (comparison)
[15] deAPI — Qwen Image Edit Plus prompting guide — https://deapi.ai/blog/qwen-image-edit-plus-prompting-guide-how-to-write-edit-instructions-that-actually-work — community (Edit Plus version)
[16] MyAIForce — Fixing Pixel Drift / Qwen Image Edit 2511 Relighting — https://myaiforce.com/qwen-image-edit-2511-relighting/ — community (page unavailable at verification; content from search engine)
[17] AIStudyNow — Qwen Image Edit 2511 ComfyUI Workflow (index_timestep_zero, skin) — https://aistudynow.com/qwen-image-edit-2511-comfyui-workflow/ — community
[18] ComfyUI — comfy/text_encoders/qwen3vl.py, qwen_image.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — official (code)
[19] Scenario — Advanced Editing with Qwen Models — https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models — community
[20] Our configuration: modele/obraz/qwen-image-2-1-edycja.yaml; workflows/obraz/qwenimage21_edycja-obrazu.api.json (node 459:479 = official PE-I2I system prompt "Edit Prompt Enhancer — General (v2)", 459:474 resolution 0) — our configuration / official
[21] Our configuration: modele/obraz/qwen-image-edit-2511.yaml; workflows/obraz/qwenedit2511_edycja-obrazu.api.json (FluxKontextImageScale, index_timestep_zero, Lightning, CFG 1/4, 4/40 steps) — our configuration
