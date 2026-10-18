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

<!-- karty-v1 -->
### Character and location sheets

A sheet is a set of **reference** images, not a frame from the piece: it fixes how a character or a place looks so it can be kept across later images and video (as a reference image in models that accept one — e.g. Kling 3.0 Omni, MiniMax H3 with references, Qwen edit as image 2). Each image of a sheet is a separate prompt, but when the participant asks for a sheet you write **all** its prompts in one answer, each in its own code block (unless they ask for one image); after consent you save each separately (`zapisz_prompt`, names like `sheet-<character>-1-figure`). Write the character's identity (or the place description) **once** and repeat it verbatim in every image of the sheet and later in scene prompts. When the model card requires another format (e.g. JSON), move the same content into its fields.

**Gaps in a sheet.** Angles, framing, background, light, lenses and pose are already in the template — you don't ask about them. You take the content from the bible: the character's subsection (Characters) or the place's (World), `STYLE` from the image texture — translated into the model's vocabulary, without asking. You ask only when one of the main things is really missing from the bible and the participant's words: identity, outfit, expression, activity (location: layout, materials, light) — one question about all gaps at once. Details nobody gave (fabric pattern, button colour) you neither ask about nor add — they are simply not in the prompt. You don't ask about: background, place, light, angle, framing, lens, posture, gaze direction, outfit details — the template settles them. When the main things are there — you write the sheet straight away, in the same answer (you don't announce that you will).

#### Character sheet — three images

Common to all: a uniform, smooth **mid-grey background**; soft, even frontal light; the same person in the same outfit; the piece's `STYLE` unchanged (a character sheet for puppet animation is of a puppet, not a photograph).

1. **Full figure from four sides** (21:9): front, three-quarter, profile, back in one row; same scale, feet on one line, eye-level camera, no perspective distortion. A calm standing pose, arms slightly away from the body (the outfit shows) — with the posture characteristic of this person if the bible gives one.
2. **Face close-ups** (16:9): head and shoulders — front, three-quarter, profile — with the **characteristic facial expression**, the same in all three.
3. **At their activity** (3:4 or 4:3): the whole figure caught mid-movement of their characteristic activity, **without a prop** — hands empty, the gesture without an object; absorbed, not looking at the lens; an observational, documentary shot, slightly off-axis. Same background and light.

Template (brackets ← the bible and the participant's words):

```
STYLE: [the piece's STYLE block, verbatim]
VIEW: clean unlabelled character turnaround sheet: four full-body views of the same person in one row: front, three-quarter, left profile, back. Identical scale, feet on one ground line, eye-level straight-on camera, long lens, no perspective distortion. Soft even frontal light, faint contact shadow at the feet.
SUBJECT: [IDENTITY: age, build, height, 2–3 facial features, hair, skin, hands]
OUTFIT: [OUTFIT: clothes, material, wear, including what shows from the back]
ACTION: standing at rest in their habitual posture, arms slightly away from the body. The same face in every view: [FACIAL EXPRESSION described physically].
SETTING: plain seamless mid-grey studio backdrop, evenly lit, empty.
```
```
STYLE: [the piece's STYLE block, verbatim]
VIEW: three head-and-shoulders portraits of the same person side by side: front, three-quarter, profile. Eye-level camera, 85mm, soft even frontal light, identical framing in all three.
SUBJECT: [IDENTITY: age, build, height, 2–3 facial features, hair, skin, hands]
ACTION: the same expression in all three: [FACIAL EXPRESSION described physically]; gaze slightly past the camera.
SETTING: plain seamless mid-grey studio backdrop.
```
```
STYLE: [the piece's STYLE block, verbatim]
VIEW: observational documentary photograph, full figure, eye level, slightly off-axis, 35mm, soft even light.
SUBJECT: [IDENTITY: age, build, height, 2–3 facial features, hair, skin, hands]
OUTFIT: [OUTFIT: clothes, material, wear, including what shows from the back]
ACTION: caught mid-movement of [ACTIVITY described as body movement], hands empty: the gesture is performed without any object; absorbed in it, unaware of the camera, gaze on what the hands are doing; [FACIAL EXPRESSION described physically].
SETTING: plain seamless mid-grey studio backdrop, empty.
```

- **Describe the expression physically, not by naming an emotion**: brows, eyelids, mouth, jaw, tension (“brows slightly drawn together, lips pressed, heavy eyelids”), not “sad”, “pensive” — an emotion word gives a stereotype.
- **Describe the activity as body movement, not as an occupation**: posture, hand position and motion, gaze (“leaning in, both hands drawing something towards the body in short strokes”), not “a baker kneading dough” — the occupation pulls in the prop and the costume. If the model still adds an object: new seed or an edit (“Remove the [object] from the hands, keep the gesture and everything else unchanged”).
- **Order**: the full figure first. Once the participant accepts it, the close-ups and the activity work best in an edit model with the full figure as image 2 — identity shown by an image holds better than identity described in words.
- **Resolution**: Studio images are about 1 MP — in a sheet of four figures the faces are small, which is why the close-ups are a separate image. At most four figures in a row.
- **Captions and frames**: sheets attract them; if they appear — new seed.
- **Sheet as a video reference**: the expression in a reference can get “frozen” in motion. If the face is meant to change in the shots, ask the participant whether one close-up should have a calm face.

#### Location sheet — four images, no people

The place is **empty** — characters enter it only in the scenes. A fixed description block (once, then verbatim in every image of the sheet and in the scenes): **layout** — 2–4 landmarks with their positions (door, window, stove, table: which wall, what stands in the middle); **materials** — walls, floor, ceiling, textures, wear; **light** — time of day, main source, direction relative to the room, colour; outdoors the weather.

1. **Wide shot** (16:9 or 21:9): the whole place, eye-level camera from a corner or the entrance, wide lens, all landmarks in frame. The most important one — the anchor for the rest.
2. **Reverse** (16:9): from the opposite side; say where the landmarks now are in the frame (the window that was on the left is on the right); light from the same source.
3. **Medium shot** (16:9): the part where the action will happen.
4. **Details** (16:9): three close-ups of surfaces and objects in one row, in the same light.

Template (wide shot):

```
STYLE: [the piece's STYLE block, verbatim]
VIEW: wide establishing view of an empty [place], eye-level camera (about 1.6 m) from [camera point: corner / entrance], 24mm, the whole layout visible.
SETTING: [PLACE: type, period; layout: 2–4 landmarks with positions; materials of walls, floor, ceiling]. [LIGHT: time of day, source, direction relative to the room, colour; outdoors the weather].
DETAILS: [2–3 textures, signs of wear, motifs from the bible]
```

In the following images change only `VIEW` (“reverse wide view from [point]; the [window] is now on the right of the frame”, “medium view of [area]”, “three close-up details side by side: [a], [b], [c]”), the rest verbatim.

- No people — phrased positively: “empty [place]”, not “no people”.
- Time of day and light the same in every image of the sheet; name the light direction relative to the room (“from the window in the left wall”), not the frame.
- Further views come out most faithful when made from the wide shot in an edit model (Qwen-Image-Edit 2511 can change the viewpoint): small camera rotations work well, a 180° turn poorly — the reverse is safer from a prompt.
- A place that flashes by once in the piece does not need a sheet.
