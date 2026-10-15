<!-- Model card for the promptmaker. modele: z-image-turbo -->
# Z-Image Turbo (Tongyi-MAI / Alibaba) — fast text → image

## What it is and what it's good for (including: what it does NOT do well)
- A 6B model (single-stream DiT, S3-DiT), a version **distilled to 8 steps**, without CFG; Apache 2.0 [1][4] (official). Text encoder: Qwen3 4B [5] (our configuration).
- In the Studio: **a few seconds per image — for finding a direction and sketching** [5] (our configuration). For final quality, dense text and difficult composition, compare with Qwen-Image 2.1.
- Strengths: photorealism and aesthetics (the distilled model often beats its 100-step teacher in quality ratings) [4] (official), **bilingual text in the image: Chinese and English** [1][4] (official).
- What it does NOT do well:
  - **low diversity** — official table: Turbo "diversity: low"; in OneIG diversity 0.139 vs 0.194 in the base model [1][4] (official). Changing the seed often gives a very similar image [10] (community);
  - **style**: Turbo "excels in photorealistic image generation", while the card attributes the "wide range of artistic styles" to the base Z-Image model [1] (official); its OneIG-Style score is slightly lower than the base model's [4];
  - world knowledge, understanding intent, complex reasoning — limited (officially stated for the 6B without the extender) [4];
  - **the negative does not work at all** [2] (official);
  - text in languages other than zh/en — Polish diacritics (and other non-English characters) **unconfirmed**.

## What the participant sets in the Studio (fields, inputs, parameters from our YAML — and how they affect the prompt)
Source: `modele/obraz/z-image-turbo.yaml` + `workflows/obraz/zimage-turbo_tekst-na-obraz.api.json` [5] (our configuration).
- **prompt** — one field → `CLIPTextEncode` with the Qwen3 4B encoder. ComfyUI wraps it in the chat template `<|im_start|>user … <|im_end|><|im_start|>assistant`, **with no system prompt and no extender** [6] (ComfyUI code). Nobody will fix the prompt along the way — you write it in "extended" form from the start.
- **No negative**: the negative branch is `ConditioningZeroOut`, CFG 1 [5]. Officially: the model doesn't use negative prompts [2].
- **No truncation**: the official diffusers code truncates the text to 512 tokens (they recommend raising it to 1024) [2], but the ComfyUI tokenizer has no such limit [6] (code). A long prompt arrives in full.
- **aspect ratio** — 16:9 (default), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16; approx. **1 MP**, dimensions ×16 [5]. Native demo size: 1024×1024 [1].
- **seed** — with low diversity it's a weak lever; changes come from **the content of the prompt** [1][10].
- **steps** (advanced) — 4–16, default 8 (sampler res_multistep, shift 3) [5]. Officially 9 in diffusers = 8 DiT passes [1]; practitioners: 8–12, more only when noise remains [9] (community). Fewer steps = a sketch.

## Prompt format (language, length, structure, tags, negative, weights)
- **Language: English** (or Chinese). Trained on bilingual zh/en descriptions [4] (official); no evidence that Chinese gives a better image [7] (community). The participant needs to read the prompt → English. Not the participant's language (unless it is English).
- **A long, detailed description.** Officially: "works best with long and detailed prompts" [2]. Practitioners: 80–250 words as the sweet spot, "hundreds of words are OK" [9] (community). The claim of "attention drift after 75–100 tokens" [8] contradicts the official recommendation — ignore it.
- **Register: matter-of-fact, objective description**, not poetry. The long training descriptions were written in a "plain and objective linguistic style" [4] (official), and fine-tuning (SFT) was done on prompts passed through the official PE extender [4] — so the model understands prompts in that extender's style best.
- **Rules of the official extender (pe.py)** [3] (official, original in Chinese):
  1. lock the non-negotiable elements: subject, number, action, state, names, colors, texts;
  2. if the request calls for an idea ("design…", "show how…") — first come up with a concrete, visible solution and describe it;
  3. add professional details: **composition, light and lighting atmosphere, material/texture, color scheme, spatial layers**;
  4. **text to render — verbatim, in English double quotes `"…"`**; for a poster/menu/UI describe all the text, the typeface and the layout; for a sign/screen: content, position, size, material;
  5. **no metaphors or emotional rhetoric**, no meta tags ("8K", "masterpiece") and no drawing instructions.
- **Prose, full sentences, not a tag list**; SD-era boosters ("masterpiece, best quality, trending on artstation") do nothing [3][11] (official / community).
- **Negative**: everything positively — "sharp focus" instead of "no blur", "empty street, only wet cobblestones" instead of "no people" [2][12] (official / community).
- **Weights `(word:1.3)` — NO.** The Z-Image tokenizer in ComfyUI has `disable_weights=True` — parentheses and numbers reach the model as text [6] (code).
- **Don't mix contradictory styles** (photorealism + cartoon + oil painting) [11][12] (community).

## Prompt skeleton
```
[medium and style: photograph / ink drawing / watercolour painting / collage… + 1 technique qualifier]. [shot size and angle: wide shot / close-up, eye level / high angle], [composition: where the subject stands in the frame].
[subject: who/what, how many, age as a life stage, 2–3 appearance traits], [clothing/surface: color + material], [action or state].
[surroundings: 2–3 concrete elements with their position; foreground / background].
[light: source, direction, quality, time of day], [palette: 2–3 colors with qualifiers].
[image texture: grain / brushstrokes / paper fibre / halftone — if relevant]; [for photo: ONE camera or lens + ONE film stock].
[text in the frame: where, what typeface, reads "EXACT TEXT" — or nothing].
[constraints stated positively: only one figure in the frame / plain untextured background].
```

## What works
- **Cinematographer's language**: shot size, angle, placement, light — the model responds strongly to these [9][12] (community).
- **Concrete facts instead of evaluative adjectives**: "beautiful", "nice", "epic" add nothing [11][12] (community); the official PE says to translate intent into visible facts [3].
- **Photographic vocabulary instead of "realistic"**: a specific camera/lens and film stock (e.g. "Kodak Portra 400", "Ilford HP5"), skin texture ("visible pores, slight asymmetry") — attributed to a photographer from r/StableDiffusion [11] (community). Max. **one** camera phrase and **one** film/light phrase — more dilutes the effect [11].
- **Role + 2–3 traits** instead of one "loaded" word ("CEO", "witch" pull in stereotypes of gender, body, makeup) [9] (community). Instead of "businessman" → "office worker" + traits.
- **A simple, uncluttered background** when the subject matters [9].
- **Text in the frame**: short, in quotes, with position and typeface; early in the prompt; one language per piece of lettering; add "no other text in the image" in positive form ("the rest of the wall is blank") [3][9][11].
- **Variations**: change the content of the prompt (framing, angle, time of day, placement), not just the seed — the distilled model returns to the same composition [1][10]. A shorter prompt = more freedom of layout, a long one = anchors the composition [10] (community, in the context of a diversity LoRA).
- **A fixed seed while refining**, changing one thing at a time [9].

## Biases and pitfalls
- **Default "stock beauty photography"**: smooth, symmetrical faces, gloss — when camera, film stock and imperfections are missing [11] (community). Training with rewards for, among other things, "AI-content detection perception" (realism, "doesn't look like AI") and aesthetics [4] (official) — the model pulls toward polished realism.
- **Low diversity**: successive seeds ≈ the same frame, the same face [1][4][10]. If the participant wants a series — describe each variant differently.
- **People**: specify age, build, origin, clothing; don't leave it to the model (loaded words → stereotype) [9]. Whether the model has a default facial ethnicity — **unconfirmed** (the examples in the HF card feature Chinese characters [1]).
- **"Plastic"** = usually missing texture words (pores, fabric weave, grain, brushstrokes) [11] (community).
- **Overloading** with a list of details and contradictory instructions → chaos [12] (community).
- **Non-English characters in lettering** (e.g. Polish diacritics): unconfirmed (officially zh/en only) [1][4]. Keep it short, check the result; key lettering → Ideogram 4 or Qwen-Image 2.1 in the Studio [13] (our configuration).
- **Steps**: with too many steps, distilled models are sometimes burnt out/full of artifacts (unconfirmed for our 4–16); stay at 8.

## Beyond photorealism
- Turbo is a model geared toward photorealism [1] — style has to be **enforced consistently**: medium as the first words, the tool's trace in the description, **zero camera vocabulary** (lens, aperture, "shot on…", film stock) for drawing/painting — otherwise it reverts to a photo [11][12] (community, inferred from the ban on mixing styles).
- Phrases from practitioners' presets (not tested under controlled conditions) [11] (community):
  - watercolor: "watercolor painting, loose brushwork, pigment pooling";
  - comics: "western comic book style, strong inked outlines, bold graphic look";
  - analog: "analog film photograph, grainy texture, warm tonal shifts, slight vignette";
  - anime: "anime artwork, studio anime key visual"; manga with screentone; pixel art; stained glass; art deco.
- **Pixel art** the base model can do (a LoRA only adds detail) [14] (community).
- The abundance of style LoRAs (anime, "artist style") on Civitai for Turbo [15] (community) suggests that pure illustrative styles without a LoRA are weaker; the Studio doesn't expose LoRAs here [5].
- **Tape / grain / archive**: one film stock + a description of visible traces (grain, discoloration, scratches, vignette); this is the register where Turbo is most reliable [11].
- **Abstraction / collage**: describe shapes, edges, color planes, paper texture and their positions matter-of-factly; no metaphors (PE forbids them [3]). Effect — not confirmed by testing; if it doesn't work, switch to Qwen-Image 2.1.
- **The mood of a poem**: translate it into light, palette, framing and matter — a literal metaphor will be ignored or drawn literally [3].

## Motion / time / sound
Not applicable. A sketch for a video's first frame: aspect ratio matching the video (16:9), simple layout, room for motion; once the direction is chosen, make the final in Qwen-Image 2.1.

## Check before sending
- [ ] English, full sentences, matter-of-fact — no metaphors or judgments ("beautiful", "epic").
- [ ] Medium/style at the beginning; for non-photo, zero words about camera and film stock.
- [ ] Shot size, angle, placement, light (source + direction), palette, texture.
- [ ] People: age, build, clothing, traits stated explicitly; no loaded labels.
- [ ] Lettering short, in `"…"`, with position and typeface — or none.
- [ ] None of: negatives ("no…"), weights `( :1.3)`, "masterpiece/8K", tag lists.
- [ ] ~80–250 words.
- [ ] Variant = a different description, not just a different seed.

## Sources
[1] Tongyi-MAI/Z-Image-Turbo — model card — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo — official
[2] Tongyi-MAI/Z-Image-Turbo — discussion #8 "PROMPTING GUIDE" (pinned, answers from the authors) — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8 — official
[3] Tongyi-MAI Space — pe.py (prompt extender template) — https://huggingface.co/spaces/Tongyi-MAI/Z-Image-Turbo/blob/main/pe.py — official
[4] Z-Image: An Efficient Image Generation Foundation Model with Single-Stream Diffusion Transformer (arXiv 2511.22699) — https://arxiv.org/abs/2511.22699 — official
[5] Our configuration: modele/obraz/z-image-turbo.yaml; workflows/obraz/zimage-turbo_tekst-na-obraz.api.json (Qwen3 4B, CFG 1, res_multistep, shift 3, ConditioningZeroOut) — our configuration
[6] ComfyUI — comfy/text_encoders/z_image.py (chat template, `disable_weights=True`, no length limit) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/z_image.py — official (code)
[7] Search results: Chinese vs English prompt (no controlled comparison) — https://aioz.network/blog/z-image-turbo-a-bilingual-image-generation-model-for-text-rich-visuals-2 — community
[8] Fliki — claim of drift after 75–100 tokens (see [11]) — https://fliki.ai/blog/z-image-turbo-prompting-guide — community
[9] illuminatianon — Z-Image-Turbo Prompting Guide (gist + comments) — https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32 — community
[10] Floyo — Z-Image Turbo Text to Image With Diversity LoRA — https://www.floyo.ai/workflows/z-image-turbo-text-to-image-with-div-efye86mk80ax — community
[11] Fliki — Z-Image Turbo Prompting Guide: 25 Style Presets, Realism Secrets — https://fliki.ai/blog/z-image-turbo-prompting-guide — community (vendor, quotes r/StableDiffusion)
[12] fal — Z-Image Turbo prompt guide — https://fal.ai/learn/devs/z-image-turbo-prompt-guide — community (vendor)
[13] Our configuration: own notes (unpublished) (Ideogram 4 for lettering), modele/obraz/ — our configuration
[14] elusarca — pixel art style LoRA for Z-Image Turbo — https://huggingface.co/reverentelusarca/elusarca-pixel-art-style-lora-zimage-turbo — community
[15] Civitai — Anime Style Lora For Z-Image-Turbo — https://civitai.com/models/2186181/anime-style-lora-for-z-image-turbo — community
