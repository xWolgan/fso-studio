<!-- Model card for the promptmaker. modele: ltx-2-3, ltx-2-5 -->
# LTX-2.3 and LTX-2.5 (Lightricks): video with sound

## What it is and what it's good for (including what it does NOT do well)

- A single model (22B, DiT) generates **picture and sound together**, in one pass. The sound (ambience, effects, speech, singing, music) comes from the prompt, so the prompt also describes what is heard [12][13][14] (official).
- **LTX-2.3** (March 2026). Text encoder Gemma 3 12B [2][12][5]. One continuous scene per generation. Has an **image + recording → video** variant: the image moves to the supplied audio, e.g. speaks or sings [1].
- **LTX-2.5** (August 2026). Its own fine-tuned Gemma 4 12B encoder, which holds complex prompts (several characters, camera movement, light) better [11][13][18] (official). New: **native multi-shot**: 2–4 shots joined by cuts in a single generation [3][6] (official). In Studio this model has no audio input [1].
- What works best: cinematic frames with one main subject, clear camera language, consistent light, well-described sound, atmosphere (fog, rain, reflections), small gestures and facial expressions [3][4] (official). According to the 2.3 Prompt Guide, stylization also works well: "painterly, noir, analog film, pixelated animation" [4] (official).
- **What works poorly:**
  - text and logos (spelling is unreliable, in 2.5 as well) [3][4];
  - chaotic physics (dance is fine) [4];
  - crowded frames with many characters or actions, mixed lighting logic [3][4] (official);
  - assigning lines to characters when several people speak [14] (official);
  - pronunciation in languages poorly represented in the data [14] (official);
  - drift in scenes longer than about 20 s [14] (official);
  - object permanence: things appear and disappear [34] (community).
- **Sound limitation (2.3):** when there is no speech in the audio, sound quality tends to be lower [12] (official).

## What the participant sets in Studio (fields, inputs, parameters from our YAML — and how they affect the prompt)

One entry per model. Studio picks the variant itself, based on the inputs provided [1] (our configuration):

| Inputs | LTX-2.3 | LTX-2.5 |
|---|---|---|
| none | text → video | text → video |
| `klatka_start` | image → video | image → video |
| `klatka_start` + `klatka_koniec` | first and last frame | first and last frame |
| `klatka_start` + `dzwiek` | image + recording → video | — (not available) |

Parameters [1][2] (our configuration):

- **prompt.** A single field. **There is no negative field.** The workflows have a hard-coded negative ("pc game, … cartoon, childish, ugly"), but all samplers run at **CFG = 1** (distilled model), so the negative has no effect. The official recommendations say the same: "distilled… CFG=1" [11][12]. A negative only starts to work at CFG > 1 [27] (community). So everything the model should avoid has to be handled in the prompt itself, as a description of what should be there.
- **aspect ratio:** 16:9 (default), 21:9, 4:3, 1:1, 3:4, 9:16; about 0.9 MP, dimensions divisible by 32.
  - In LTX-2.3 (image, image + recording) and in both "frames" variants, images are **center-cropped** to the selected aspect ratio. So the aspect ratio should match the image, otherwise part of the frame is lost.
  - LTX-2.5 image → video does not crop the image before the model. What happens with mismatched aspect ratios is unknown; best to keep them matching.
- **length:** 1–20 s (default 10). **fps:** 24 or 25.
  - A long shot needs a longer, richer description: "A short prompt for a long video often results in the model rushing through the described action" [4] (official).
  - Rule of thumb: **one main action per 2–3 s** [5] (official, blog).
  - A long clip with a short prompt also risks "end cards" and logos in the last frames. The bug was fixed in upscaler v1.1, which we use [28] (community + Lightricks reply).
  - In the recording variant, the length trims the recording [1].
- **expansion** ("the model expands the prompt itself"; advanced setting, off by default; not available in the LTX-2.3 "frames" variant). A built-in LLM rewrites the prompt **into an English paragraph in the style of the training captions** [7][8][9][10]:
  - 2.3: Gemma 3 12B (the same model as the encoder);
  - 2.5: Gemma 4 E2B (about 1–2 min longer) [13].
- **seed.** With the same seed, change one thing at a time [5].
- **Two stages** (half resolution, then a ×2 upscaler) are used only by the text → video, image → video and image + recording variants [2].
  - The "frames" variants do a single pass directly at full resolution, without the upscaler [2] (our configuration; consistent with [13]). This does not affect the prompt.
- **The start image** goes through `LTXVPreprocess` (light compression, meant to make the frame look more like a video frame) [2] (our configuration).

## Prompt format

- **Language: English.**
  - The training captions and both enhancers are in English. The 2.5 enhancer has an explicit instruction: "If the user wrote in another language, produce the English caption" [8][9] (official, code).
  - The encoder is multilingual [14], but nobody has studied the quality of descriptions written in other languages, e.g. Polish (**not established**). We write the description in English.
- **Spoken lines** go in quotation marks, **in the language in which they are to be spoken** (Polish lines in Polish). Name the language and accent [3][4][8] (official).
  - Speech quality in the participant's language (e.g. Polish): **not established**; no tests found.
  - Accent and pronunciation in other languages can be unreliable [29] (community).
  - The model does not translate lines [3] (official, refers to Dub-It).
- **Structure:** **one flowing paragraph, present tense**, chronologically from the start to the end of the shot [3][4][6] (official).
  - No lists, bullets, headings or labels like "Audio:"/"Visual:": the 2.5 enhancer is explicitly forbidden to use them [8] (official, code).
  - Exception: for dialogue, multiple beats or precise timing, the official guide allows a **screenplay style**: scene heading, "Reporter: "…"" [3][4] (official).
  - Our cards do not use the tags or section labels from `media/wideo.md`: we write the same content as prose, in the same order.
- **Six elements (both models)** [3][4][6] (official):
  1. Shot: shot size, category, film terminology.
  2. Scene: light, palette, textures, atmosphere.
  3. Action as a sequence, every sentence with a verb of motion ("walks, turns, exhales, reaches").
  4. Characters: age, hair, clothing, distinguishing features; emotion only through physical signs.
  5. Camera: how and **when** it moves, described relative to the subject, plus how the subject looks **after** the move.
  6. Sound: ambience, effects, music, speech, singing.
- **Order:**
  - LTX-2.3: the blog on prompt adherence advises starting with **the main action in one sentence**, then motion details, appearance, surroundings, and finally camera and light [5] (official, blog).
  - The style direction is best given **at the very beginning** [7][15] (official). The 2.3 enhancer starts with "Style: <style>, …" [7][10]; this is the only "marker" visible in the code.
  - LTX-2.5: the training captions start with the action or a visual detail. Three things are woven into the prose: **shot size** (one of: extreme wide / wide / medium / medium close-up / close-up / extreme close-up), **camera movement** (always; no movement = "the camera remains static") and **point of view** (front-facing / side view / over-the-shoulder / top-down / low-angle / high-angle) [8] (official, enhancer code).
- **Length:**
  - 2.5: officially "4–8 descriptive sentences" for a simple shot, more for complex scenes, "provided every sentence adds concrete visual or audio detail" [3][6]. The 2.5 enhancer aims at **150–220 words** [8].
  - 2.3: sources differ. The Prompt Guide says "long, detailed prompts win" [4], while the blog on prompt adherence says to stay within 200 words [5] (both official).
  - In practice: **about 80–220 words**, proportional to the clip length.
- **No weights, no JSON, no "(word:1.2)".** The Gemma 3 and Gemma 4 tokenizers in ComfyUI have `disable_weights=True` — brackets and numbers reach the model as plain text (ComfyUI code: `comfy/text_encoders/lt.py`, `gemma4.py`). No numbers or degrees either ("pans at 2 degrees per second"): that is an example of the "over-constrained" mistake [4] (official).
- **Negations in the text:** an official example uses them in the sound description ("a low male vocal drone…, no instruments, no music") [3] (official). The blog on 2D animation advises "no gradients, no shadows" for flat graphics [15] (official, blog). Use sparingly: first describe what is there.

## Prompt skeleton

Text → video, single shot (both models):
```
[style/medium/texture — first phrase]. [shot size] of [subject: age, appearance, clothing — only what is visible], [point of view], in [place: materials, textures]. [light: source, direction, color; one logic] and [palette]. [action 1, present tense], as [camera movement relative to the subject, pace]. Then [action 2 / change], [how the subject looks after the camera move]. [background sound — specific sources], [effect tied to the action]; [who] says in [language, timbre, pace, volume], "[line]". [music or its absence; reverb/space].
```

Image → video:
```
[2.5: one anchoring sentence consistent with the image: shot size, subject, place]. [what starts to move and how — chronologically: initially…, a moment later…], [camera movement or "the camera remains static"]. [what changes in the light/matter]. [sound: sources synchronized with the movement; speech in quotation marks].
```

First and last frame:
```
[how we get from the state in the first frame to the state in the last: successive phases of the change], [camera movement connecting both frames], [light/time]. [sound during the transition].
```

Image + recording (2.3 only):
```
[style], [shot size, point of view]. [subject] [how they perform the sound from the recording: mouth, breath, gesture, facial expression — in the rhythm of the recording], [small movements of the body/background], [camera].
```

Multi-shot (2.5 only, text → video):
```
[shot 1: shot size, framing, subject with an identifier, action, sound]. A hard cut transitions to [shot 2: new shot size, angle, who is in frame — same identifier], [action]; [sound: what continues / what changes across the cut]. [optional shot 3, same pattern].
```

## What works

- **Camera movement from well-known vocabulary:** "follows, tracks, pans across, circles around, tilts upward, pushes in / pulls back, overhead view, handheld movement, over-the-shoulder, wide establishing shot, static frame" [3][4]. Plus "slow dolly in", "handheld tracking" [4] (official).
- **Emotion through the body:** instead of "sad" write "his eyebrows angle downward and his lips are pressed together" [8]. Instead of "tense confrontation" write "two men stand three feet apart, both leaning forward with clenched fists" [5] (official).
- **Literal, not metaphorical:** describe what the camera physically sees [5] (official, blog). A metaphor from a poem has to be translated into matter, movement, light and sound.
- **Time connectives:** "Initially…, A moment later…, Simultaneously…" [3][8] and "as / then / while" [7][35] (official + community).
- **Dialogue split into phrases with stage directions** (2.3): "…says in a slow voice, "…" He pauses and looks to the side, then continues, "…"". Pauses written into the text ("a beat of silence", "she pauses") are actually performed by the model [3][4] (official).
- **Sound tied to a source in the frame:**
  - First the background of the space, then effects tied to the action that causes them [30]; specifics instead of generalities ("soft footsteps on tile", not "ambient sound") [7] (official).
  - The signal that works is a moving object with a sound attached to it; mood adjectives don't work [33] (community).
- **Sound described as it happens, alongside the action, not tacked on at the end** [10] (official, 2.3 I2V system prompt).
- **Sound quality:** in 2.3, describing the acoustics, voice timbre and ambience has more influence than before [4] (official). An addition like "The audio is crisp with faint room tone" helps [4]. Fill silence with room tone ("quiet room tone") [30] (community).
- **Professional vocabulary with a clear hierarchy:** start with the main domain (e.g. animation), add a second one as a material qualifier, a third only as light or grading. Mixing them on equal terms makes the model "average" them [16] (official, blog).
- **Static shot:** write "A static shot of …" as the **first phrase** [19] (community; effectiveness in 2.5 uncertain, see pitfalls).

## Biases and pitfalls

- **Photorealism by default.** "AI video generation defaults to photorealism" [15] (official). A longer clip in 2D style drifts towards realism [15].
- **The enhancer ("expansion") shifts aesthetics and content:**
  - 2.3 enhancer: when no style is given, "Default to cinematic-realistic" [7]. Plus "Restrained language": plain colors, no intensifiers [7].
  - The 2.5 enhancer has "cinematic, film-grade color…, beautiful natural lighting, crisp fine detail" built in and encourages camera movement ("Camera movement is expected and good") [8][9] (official, code). This clashes with the promptmaker's rule "we don't add prettiness".
  - Community: with the 2.5 enhancer on, results are sometimes completely unrelated to the prompt [17]. Unwanted demographic traits of characters creep in; Gemma 3 stuck to the prompt better [18] (community).
  - Conclusion: **"expansion" off by default**. Officially, the enhancer helps least when the prompt already has the right structure [3].
  - Our workflows have two gaps [2] (our configuration). In LTX-2.3 image + recording, the enhancer **does not receive the image**, so it writes as if for text → video and may invent an appearance that contradicts the image. In LTX-2.5 "frames" it sees **only the first frame** and is forbidden to use cuts.
- **Camera push-in.** In 2.5 (and 2.3) clips often "zoom" into the face on their own. Asking for a static camera helps little: according to one user, about 2 in 50 attempts without zoom. Another says 2.5 handles it better than 2.3. Close shots dominate [19] (community). Camera LoRAs are not available in Studio.
- **Without a description of camera movement, the model makes its own drift** or random angle changes [5] (official, blog). Always specify the camera, also as "static".
- **Unrequested speech.** 2.3 sometimes "reads the prompt out loud" or babbles when no speech was requested [24] (community). When there should be no voices, describe exactly what is heard: sources, "no one speaks" (**unconfirmed** whether it helps).
- **Music adds itself.** Without guidance, the model may add its own soundtrack [30][33]. The host recommends "no music" [30], but in 2.3 users could not switch it off via the prompt [26] (community). If music is to be added later: write "no music" and be prepared to cut the track in editing.
- **Voice volume and distance** ("whisper", "from a distance") are poorly controllable in 2.3 according to users [25] (community). The official word list, however, includes "Whisper · Mutter · Shout · Scream" [3]. The result is not reliable.
- **Text in frame.** 2.3 can add subtitles on its own, often with errors [27]. Quotation marks mean speech, not on-screen text [30] (community). Officially: keep text in frame short and large, spelling is not guaranteed, add important text and logos in editing [3] (official). For us: better not to request text in frame.
- **Contradictions** ("a still, peaceful lake with dramatic waves crashing"; "running quickly… in slow motion") confuse the model [4][5] (official). Describe slow motion by its effect: "suspended in slow motion, each step drawn out" [5].
- **Overloading:** five actions in one clip end up compressed or with the middle ones skipped [5] (official, blog). Short form: one, at most two events.
- **I2V in 2.5: the identity of the character from the image is sometimes altered.** Users report that 2.3 held the face better [20] (community).
- **I2V in 2.3:** a description that does not match the image "may cause scene cuts" [10] (official, system prompt).
- **A prompt carried over from another model** (tags, shot lists from Kling/Seedance/H3) works worse. Rewrite it as an LTX paragraph [3] (official).

## Beyond photorealism

- **Main rule (official, 2D blog [15]):**
  - style declaration as the **first phrase** of the prompt, repeated in the body;
  - when realism creeps back: "not photorealistic, no realistic textures, 2D only";
  - the strongest anchor is a **start image in the target style** (made in the Image area or drawn), because the prompt then only describes motion;
  - **short clips (2–4 s)** protect against drifting into realism.
- **Vocabulary from the official guide** [3][4]:
  - Animation: stop-motion, 2D / 3D animation, claymation, hand-drawn;
  - Stylized: comic book, 8-bit pixel, surreal, minimalist, painterly, illustrated;
  - Cinematic: film noir, experimental film, arthouse, documentary;
  - Film Characteristics: **film grain, lens flares, pixelated edges, jittery stop-motion**.
- **Drawing / 2D animation** [15][16] (official, blogs):
  - "hand-drawn linework", "ink-and-paint style", "cel-shaded flat color", "limited animation with held frames";
  - flat: "flat vector illustration style, solid color fills with clean outlines, no gradients, no shadows";
  - watercolor / picture book: "watercolor illustration style, soft painted textures, muted pastel palette, gentle hand-drawn lines";
  - words about pace help the style: "gentle, calming motion"; "exaggerated" frees it from realistic proportions;
  - **don't mix 2D and 3D vocabulary** in one shot [16].
- **Film stock, grain, archive (restoration)** [16] (official, 2.3 blog):
  - "coarse silver-halide grain, black-and-white 16mm", "fine grain, Kodachrome-tight";
  - "telecine flicker, gate weave, edge halation";
  - film stock names ("Ektachrome", "Portra", "Fuji Reala"); watch out for anachronisms.
  - VHS and analog video: no official source (**unconfirmed**).
- **Painterliness, noir, analog cinema:** listed as strengths of 2.3 [4] (official).
- **Collage, abstraction, pure texture without a subject:** no sources (**not established**).
  - The model is tuned for "cinematic, single-subject scenes" [3]. In practice the most reliable route is a start image (collage, abstraction) plus a prompt describing only the movement of matter and camera. This is an inference from [15], not a test.
- **The enhancer hurts stylization** (default "cinematic-realistic" / "film-grade") [7][8]. With stylization, "expansion" off.
- **Animation patterns** described in frame numbers ("anticipation frame at frame one… snap to release pose at frame six") come from the blog [16]. This clashes with the warning against numbers [4]; treat them as **unconfirmed**.

## Motion / time / sound

- **Motion:** one continuous action with a clear beginning and end; one main action per 2–3 s [5]. Write pauses and "beats" into the text [3].
- **Camera:** name the movement, pace and moment ("as she turns, the camera slowly pushes in"). Describe the frame after the move [3][4].
- **I2V (2.3 / 2.5 difference):**
  - 2.3: describe **motion and change**, don't repeat what is already visible in the image; "describe the transition from stillness to motion" [4][10] (official).
  - 2.5: the enhancer starts with a sentence consistent with the image (shot size, subject, place, light), then runs the action chronologically, **in a single shot, without cuts** [9] (official, code). Multi-shot with a start frame only when a cut away from the image is intended [3].
  - Both: in the new prompt, don't change the appearance of the subject from the image.
  - Technically, I2V inserts the image as the first latent frame and freezes it; otherwise the flow is the same as T2V [23] (official, Lightricks reply).
- **First and last frame:**
  - describe the **transition**: what happens between the frames, with camera movement and sound [13] (official);
  - both frames with the same aspect ratio [13]; ideally the last frame is an edit of the first and the changes happen one after another, not all at once [33] (community);
  - the strength of both frames in our workflows is 0.7, so they hold the frame "softly" [2] (our configuration).
- **Multi-shot (2.5 only)** [3][6][32]:
  - 2–4 shots [3] (official); at 10 s rather at most 3 [32] (API host, **unconfirmed** officially);
  - every cut named in prose ("A hard cut transitions to…", "The view cuts to a close-up of…", "A match cut connects…", "The image dissolves into…");
  - after the cut, re-establish: shot size, angle, who is in frame, light;
  - **the same identifier** for a character or object (clothing, color);
  - at every cut, say what happens to the sound: continues, fades or changes;
  - each shot has a job (wide → detail → reaction).
  - Without a named cut, the model makes one shot with camera movement [32] (community).
  - Lip-sync and intimate scenes: better as a single shot [3].
- **Generated sound (text/image → video):**
  - layers: voice in front, effects at the actions, background underneath [30];
  - in every line: who speaks, language, accent, timbre, pace; one person per line [30] (community); the line shorter than the clip;
  - for singing: "sings"; name the genre, mood and instruments of the music, or its absence [3][8];
  - word stress in capital letters doesn't work; describe where the pause is and which word is stronger [29] (community).
- **Image + recording (LTX-2.3 only):**
  - Our workflow **freezes the audio** (noise mask 0) [2][22], so the model doesn't change it, it only animates the image.
  - In the prompt, **don't describe a different soundtrack**. Describe the visual interpretation of the recording: who performs, how (mouth, breath, gesture), camera, background [4] (official).
  - According to the API host for 2.5 Pro: "describes the look and the performance, not the words" [31]. Face sharp, well lit, frontal, with the mouth visible; framing as in the final result, because the model does not reframe [31] (community/host).
  - Singing: a clear lead vocal; vocals with heavy reverb are sometimes taken for backing vocals and the character doesn't sing them; a lot depends on the seed [22] (community, test on 2.5).
  - External audio and singing work better in 2.3 than in 2.5 [21] (community). Studio only has this variant in 2.3, so that fits.
  - **Speech in the participant's language (e.g. Polish) more reliably:** record or generate the voice in the Speech area (e.g. OmniVoice), then use this variant. This is an inference from [29] and [14], not a test.

## Check before sending

- [ ] English paragraph, present tense, no lists, headings or labels ("Audio:") — unless it is a deliberate screenplay style.
- [ ] Style / medium / texture in the **first phrase**, verbatim from the bible; no "cinematic, beautiful, 8k" unless the bible says so.
- [ ] Shot size, point of view and camera movement named (or "the camera remains static" / "A static shot of…" at the start).
- [ ] Action chronological; about 1 action per 2–3 s of the set length; pauses written in.
- [ ] Emotions as physical signs; metaphors translated into matter, light, motion, sound.
- [ ] Sound described specifically (sources in frame, space); music or its absence stated explicitly; speech in quotation marks, with language and manner of speaking, one person per line.
- [ ] No requested text in frame; no contradictions (calm vs waves, fast vs slow motion).
- [ ] I2V: 2.3 only motion and change; 2.5 an anchoring sentence consistent with the image, then motion; aspect ratio in Studio = aspect ratio of the image.
- [ ] Frames: transition between the states described; both frames with the same aspect ratio.
- [ ] Image + recording (2.3): description of the performance and its visual interpretation, no new soundtrack.
- [ ] Multi-shot (2.5): 2–4 cuts named in prose, frame re-established, same identifiers, sound continuity.
- [ ] Leave "expansion" off (especially with stylization); if the participant turns it on, they should check the preview of the rewritten prompt.
- [ ] No negative in Studio (CFG 1): what we don't want, we don't name; we describe what should be there.

## Sources

[1] FSO Studio — model configuration: `modele/wideo/ltx-2-3*.yaml`, `ltx-2-5*.yaml` — our configuration
[2] FSO Studio — ComfyUI workflows: `workflows/wideo/ltx_23_*.api.json`, `ltx_25_*.api.json` (CFG 1, fixed negative, Gemma 3 12B fp8 / Gemma 4 12B + E2B, 2.3 upscaler v1.1, audio mask 0, image cropping) — our configuration
[3] LTX Docs — Prompting Guide (LTX-2.5; multi-shot, enhancer, examples, vocabulary) — https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide — official
[4] LTX Blog — LTX-2.3 Prompt Guide (10.03.2026) — https://ltx.io/blog/ltx-2-3-prompt-guide — official
[5] LTX Blog — How To Improve LTX-2.3 Prompt Adherence (13.05.2026) — https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence — official (blog)
[6] LTX Blog — LTX-2.5 Prompt Guide (10.08.2026) — https://ltx.io/blog/ltx-2-5-prompt-guide — official
[7] Lightricks/LTX-2 — gemma3_t2v_system_prompt.txt (LTX-2.x / Gemma 3 enhancer) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma3_t2v_system_prompt.txt — official (code)
[8] Lightricks/LTX-2 — gemma4_t2v_system_prompt.txt (LTX-2.5 enhancer) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_t2v_system_prompt.txt — official (code)
[9] Lightricks/LTX-2 — gemma4_i2v_system_prompt.txt (LTX-2.5 enhancer, I2V) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_i2v_system_prompt.txt — official (code)
[10] ComfyUI — comfy_extras/nodes_textgen.py (TextGenerateLTX2Prompt node; Gemma 3 I2V system prompt; T2V/I2V selection depending on the image) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_textgen.py — official (ComfyUI code)
[11] Hugging Face — Lightricks/LTX-2.5 (model card) — https://huggingface.co/Lightricks/LTX-2.5 — official
[12] Hugging Face — Lightricks/LTX-2.3 README — https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md — official
[13] ComfyUI Docs — LTX-2.5 tutorial — https://docs.comfy.org/tutorials/video/ltx/ltx-2-5 — official (ComfyUI)
[14] LTX-2: Efficient Joint Audio-Visual Foundation Model (arXiv 2601.03233; training captions, limitations) — https://arxiv.org/html/2601.03233v1 — official (paper)
[15] LTX Blog — How To Generate 2D Animation With AI Video Models (26.04.2026) — https://ltx.io/blog/how-to-generate-2d-animation-with-ai-video-models — official (blog)
[16] LTX Blog — Domain-Specific Prompting for LTX-2.3: VFX, Animation & More (04.08.2026) — https://ltx.io/blog/domain-specific-prompting — official (blog)
[17] HF LTX-2.5 discussion #36 — Prompt Enhancement Produces Unrelated Generations — https://huggingface.co/Lightricks/LTX-2.5/discussions/36 — community
[18] HF LTX-2.5 discussion #9 — LTX Gemma API Text Encode (LTX reply: own Gemma 4; notes on the enhancer) — https://huggingface.co/Lightricks/LTX-2.5/discussions/9 — community + official reply
[19] HF LTX-2.5 discussion #54 — Zooming in — https://huggingface.co/Lightricks/LTX-2.5/discussions/54 — community
[20] HF LTX-2.5 discussion #30 — The character consistency in i2v — https://huggingface.co/Lightricks/LTX-2.5/discussions/30 — community
[21] HF LTX-2.5 discussion #57 — Don't Use LTX 2.5 For Music Videos! Stick To LTX 2.3 — https://huggingface.co/Lightricks/LTX-2.5/discussions/57 — community
[22] HF LTX-2.5 discussion #44 — custom audio lipsync (frozen audio latent; dependence on material and seed) — https://huggingface.co/Lightricks/LTX-2.5/discussions/44 — community
[23] HF LTX-2.5 discussion #48 — Are I2V & T2V workflows actually different? (LTX reply) — https://huggingface.co/Lightricks/LTX-2.5/discussions/48 — official reply
[24] HF LTX-2.3 discussion #45 — Model reading the prompt out loud — https://huggingface.co/Lightricks/LTX-2.3/discussions/45 — community
[25] HF LTX-2.3 discussion #52 — Why is it impossible to control the volume of speaking characters? — https://huggingface.co/Lightricks/LTX-2.3/discussions/52 — community
[26] HF LTX-2.3 discussion #25 — How to kill the music — https://huggingface.co/Lightricks/LTX-2.3/discussions/25 — community
[27] HF LTX-2.3 discussion #5 — Subtitles and Removal (negative requires CFG > 1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/5 — community
[28] HF LTX-2.3 discussion #13 — spatial-upscaler-x2-1.0 causes unwanted text/overlay (fixed in v1.1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/13 — community + official reply
[29] HF Forum — LTX 2.3 problem with dialogs (word stress, pronunciation) — https://discuss.huggingface.co/t/ltx-2-3-problem-with-dialogs/176649 — community
[30] Runware — LTX-2.5 Pro: Native audio — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/native-audio — community (API host)
[31] Runware — LTX-2.5 Pro: Audio-driven characters — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/audio-driven — community (API host)
[32] Runware — LTX-2.5 Pro: Multi-shot — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/multi-shot — community (API host)
[33] fal — How To Use LTX-2.5: Prompts & Workflows — https://fal.ai/learn/tools/how-to-use-ltx-2-5 — community (API host)
[34] HF LTX-2.5 discussion #38 — object permanence/consistency — https://huggingface.co/Lightricks/LTX-2.5/discussions/38 — community
[35] RunDiffusion — LTX-2 Prompt Guide (time connectives, present tense) — https://www.rundiffusion.com/ltx-2-prompt-guide — community
