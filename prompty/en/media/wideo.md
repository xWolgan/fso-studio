<!-- Medium template for the promptmaker: VIDEO. Image sections (from media/obraz.md, Bezdroża) + time, motion, sound.
     The model card takes precedence on format (e.g. a chronological paragraph in LTX, sections and markers in H3). -->
# Video

## Medium: video (a single shot)

### Building the prompt

The same sections as for an image — `STYLE` (medium and texture, shared by the whole piece), `CAMERA`, `SUBJECT`, `OUTFIT`, `ACTION`, `SETTING`, `DETAILS` — plus:

- `MOTION:` — what moves and how, **in the order of events** from the beginning to the end of the shot. In a 5–10 s shot: one, at most two events. ← Time and rhythm, Characters and people, Matter.
- `CAMERA MOVE:` — static / pan / tracking / handheld / push-in; pace; whether the camera reacts to what is happening. ← Camera.
- `SOUND:` — only for models with sound (see the card): sound sources, space, distance; dialogue with exact wording in quotation marks, who speaks and how; music or its absence. ← Sound, Voice and word, Music.

If the model card says to write a single paragraph (e.g. a chronological description), keep the same content and order, just without the labels.

### Translation rules

- **A shot is time.** Describe chronologically; one shot = one continuity. The model loses track of long, complex actions — split them into shots.
- **Physical movement, not emotional**: "water slowly seeps under the door", not "tension builds".
- **Start image / keyframes / references**: when the participant already has an image, the prompt mainly describes motion, time and sound, not what is already visible (details — see the model card).
- **A "no-cut" transition** (the space changes during a camera move): describe it as one continuous shot — the camera move, space A at the beginning, the change halfway, space B at the end; the light changes naturally.
- **Dialogue**: the exact words, the language (if it's not English, e.g. Polish — check in the card how the model copes), the manner of speaking.
- All the image rules apply: what is there (not exclusions), technical specifics, concision, `STYLE` verbatim and shared across the series.
