<!-- Medium template for the promptmaker: IMAGE. A generalization of the Bezdroża prompt templates (Wolgan) — without assuming photorealism.
     The model card takes precedence on format (e.g. JSON, language, length). -->
# Image

## Medium: image (still frame)

### Building the prompt — labelled sections

Models stick to a prompt divided into labelled sections better than to a "wall of text" (unless the model card says otherwise — then the card takes precedence). Order and sources in the bible:

- `STYLE:` — **medium and texture of the image**: what the image is made of (16 mm film, VHS video, digital, pencil, ink, gouache, linocut, paper cut-out, puppet, collage, scan, photocopy…), its imperfections, the palette. ← Image texture, Color and light, Principle. This is the piece's "DNA": **one block for all the images of the piece**. If the participant already has saved prompts for this piece (`artefakty/prompty/obraz/`), read them and take `STYLE` verbatim; you change it only at an explicit request.
- `CAMERA:` / `VIEW:` — point of view: distance, height, lens/focal length, depth of field; light (source, direction, hardness). For non-photographic images: `VIEW:` — composition, perspective (flat, bird's-eye, axonometric), framing. ← Camera, Color and light.
- `SUBJECT:` — the main element: a person (age, origin, body, skin, hands, expression — concretely), an object, a material, a phenomenon. ← Characters and people, Matter.
- `OUTFIT:` — only when there are people: specific clothes, fabric, wear.
- `ACTION:` — what is happening at this moment; mid-movement or posed; whether the person knows they are being watched.
- `SETTING:` — place, era, time of day, weather, 2–4 "grounding" objects. ← World and interiors, Time and rhythm.
- `DETAILS:` — specific textures, anomalies, recurring motifs. ← Motifs, Tone.

Not every image needs every section. A material or abstract frame: `STYLE` + `CAMERA/VIEW` + `SUBJECT` (+ `DETAILS`).

### Translation rules

- **Describe what is there.** Exclusions in the prompt ("no people", "no text") often attract exactly what you want to avoid — rephrase positively ("an empty room", "a bare wall"). Negative prompt — only if the model card says the model has one and the Studio exposes it.
- **Technical specifics instead of mood.** The name of a medium, technique, tool, paper, material, lens or film stock works more strongly than "nostalgic", "dark", "poetic".
- **Concise**, descriptive, without politeness or filler. The 5–7 most important elements; too many instructions weaken the model's obedience.
- **Modifiers** — e.g. registers blending (a drawn element in a photographic frame), degradation of the medium, a quiet anomaly in the background — 0–3 per image. Usually less is more.
- **Blending instead of switching**: when the piece combines registers, describe the boundary (fluid, seamless) and what they share (the same light, the same shadow).
- **Full frame**: when the image should fill the frame without borders, perforations or margins — say so explicitly ("full bleed, edge to edge composition").
- **People**: specific, not idealized, if the bible wants that — age, skin, hands, posture. Always name the direction of the gaze.
- **Text in the image**: only when the bible wants it; exact wording in quotation marks; check in the card whether the model can do it (including diacritics, e.g. Polish characters).

### Consistency across a series

A piece is a few to a dozen or so images. Fixed blocks (`STYLE`, often `CAMERA`) you repeat verbatim; you change the content sections. A character who comes back is always described with the same words — or you suggest a reference image, if the model has an image input (see the card).
