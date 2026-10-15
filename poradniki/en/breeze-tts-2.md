# Breeze TTS 2 — how to prompt

## How the model listens
A speech model by BreezeBlue — **English and Chinese only** (for other languages, including Polish: OmniVoice). Its strength is controlling the voice through description: **voice design** in prose (no recording) and **direction** — cloning a voice from a recording with an instruction on how to perform (tone, emotion, pace, delivery).

## Structure
- **Voice design:** a prose description in the language of the text, e.g. "A warm, thoughtful young woman with a clear voice and a calm, reflective delivery."
- **Direction (with a recording):** an acting instruction, e.g. "Speak slowly with a restrained, serious tone." You can ask for an accent, laughter, sighs, tiredness, nervousness.
- **Events in the text (English):** in round brackets — `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)`; in Chinese, in square brackets — `[笑]`, `[叹气]`.

## What it's sensitive to / pitfalls
- The language of the description should match the language of the text.
- Recording for a clone: clean speech, little background, with an **exact transcript** in the "sample transcript" field.
- **Pure clone:** sample + transcript, the "voice and delivery" field **empty** (the default), CFG 1. Any instruction you type turns the clone into direction.
- In the Studio the service handles **one request at a time** — if there's a queue, you'll need to wait a moment.

## Example (structure)
- Voice description: "An elderly man with a low, gravelly voice, speaking slowly, as if remembering something painful."
- Text: "I kept the key for years. (sigh) I never found the door."

## Parameters that really change the result
- **Instruction strength (CFG)** — advanced, 0.5–4. For voice description and direction the authors recommend 4. Without an instruction leave it at 1 (any other value ends in an error).

## Licence
Weights for research and non-commercial use only.

## Sources (accessed 2026-10-05)
- Hugging Face — BreezeBlue/Breeze-TTS-2: https://huggingface.co/BreezeBlue/Breeze-TTS-2
- BreezeBlue — Introducing Breeze TTS 2: https://breezeblue.ai/breeze-tts-2
