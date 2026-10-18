# Studio — improvising with AI in text, image, video and sound

*Polski: [README.md](README.md)*

A browser-based Studio for working with generative models in six areas — **Text, Image, Video, Music, SFX, Speech** —
with a job queue, gallery, notes, and a conversation partner (LLM) that helps you search for form, keeps the piece's
“bible” and writes prompts for specific models. Built for the workshop “AI Form Research Group” (Kraków, 2026).

This is the **single-user version for your own computer**. Models run **in the cloud, on your own API keys** — no GPU
needed. The repository contains no keys and no access to anyone else's machines.

Interface: Polish, English, French (switch in the header).

## Providers

You enter keys in the Studio (**Settings**), fetch the provider's model list and tick the models that should appear in
the areas. You can change the selection at any time.

| Provider | What it gives you in the Studio | Key |
|---|---|---|
| **OpenRouter** | text (hundreds of models), image, video, speech | https://openrouter.ai/keys |
| **fal.ai** | image, video, music, sound effects, speech (over a thousand models; forms are built automatically) | https://fal.ai/dashboard/keys |
| **HiggsField** | video: Kling 3.0, Kling 3.0 Omni, WAN 3.0 | https://cloud.higgsfield.ai/api-keys |
| **Kie.ai** | image, video, speech (Kling, Wan, Veo, Seedream, Hailuo, ElevenLabs…) | https://kie.ai/api-key |
| **Claude** (Anthropic) | text | https://console.anthropic.com/settings/keys |
| **ChatGPT** (OpenAI) | text, image, speech | https://platform.openai.com/api-keys |
| **Gemini** (Google) | text, image | https://aistudio.google.com/apikey |
| **Local** (Ollama, LM Studio, llama.cpp) | text on your own computer — free, nothing leaves your machine; a server address instead of a key | https://ollama.com/download |

One key is enough to start — e.g. **OpenRouter** gives you text, image, video and speech. Models marked “support coming
soon” in Settings are visible but not yet available (e.g. Lyria music, Gemini video and speech).

## One-command install

**Windows** — open PowerShell (Start menu → type “PowerShell”) and paste:
```powershell
irm https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.ps1 | iex
```
**macOS / Linux** — open Terminal and paste:
```bash
curl -fsSL https://raw.githubusercontent.com/xWolgan/fso-studio/main/install.sh | bash
```
The installer downloads the Studio into a `Studio` folder in your home directory, installs Python on Windows if needed,
puts a **Studio** shortcut on the desktop (macOS: `Studio.command`), starts the Studio and opens the browser on
Settings. Next time just double-click the shortcut. Running the installer again = update (keys, settings and your files
stay). On macOS you need Python 3.11+ (https://www.python.org/downloads/).

## Quick start (manual)

You need **Python 3.11+** and a browser.

```bash
git clone https://github.com/xWolgan/fso-studio.git
cd fso-studio
./start.sh            # Linux / macOS
```
Windows: double-click **`start.cmd`** (or `.\start.ps1` in PowerShell).

The first run installs dependencies and creates `config.yaml` and `sekrety.env` (“secrets.env”). Then:

1. Open **http://127.0.0.1:8100/ustawienia** (Settings).
2. Enter a provider key → **Save** (the Studio checks right away whether it works).
3. **Fetch model list**, expand it and tick models — they appear in the matching areas.
4. Optionally set a monthly **spending limit**.

There is no login — the Studio opens straight away.

## Spending

Every cloud generation costs whatever the provider charges and is **billed to your account with that provider**.
The bar at the top shows this month's spending; click it for today / month / total and the most expensive models.
Amounts come from the providers (OpenRouter reports the cost of each request) or from the model's price list in the
Studio; jobs for which the provider reports no price are listed separately — check them in its dashboard. When spending
reaches the limit set in Settings, the Studio pauses paid generations (conversations keep working).

## Security — please read

- **The Studio has no passwords.** By default it listens only on `127.0.0.1` — this computer only. Don't expose it to a
  network (`HOST=0.0.0.0`) or the internet: anyone who got in could generate at your expense and read your files.
- **Settings** (keys, limit) work only from this computer, even if the Studio is shared on a network. Keys are never
  sent back to the browser.
- Keys live in `sekrety.env`; your files, conversations and model selection in `zasoby/`. Both stay out of git.
- Conversation and prompt content goes to the provider whose model you choose. In conversations via OpenRouter the Studio uses only
  providers that don't collect request data (for image, video and speech the model provider's terms apply).

## Optional: local models

Free, on your own computer. Everything is set up in **Settings** — no file editing.

- **Text:** install [LM Studio](https://lmstudio.ai) (start the server: Developer → Start Server) or
  [Ollama](https://ollama.com/download). In Settings → **Local**, enter the address (LM Studio: `http://127.0.0.1:1234/v1`,
  Ollama: `http://127.0.0.1:11434/v1`), fetch the list and tick models.
- **Image, video, music, speech:** install [ComfyUI](https://www.comfy.org/download) (NVIDIA GPU; video realistically
  24–48 GB VRAM) and download the model files listed in **[MODELE.md](MODELE.md)** (some models are non-commercial).
  In Settings → **ComfyUI on this computer**, enter the address (`http://127.0.0.1:8188`) — the Studio checks which
  models you have installed (✓ ready / ✗ what's missing) and enables only those.

Advanced: several ComfyUI machines or custom models — `config.yaml` → `maszyny` and YAML files in `modele/<area>/`
+ a ComfyUI workflow in API format in `workflows/` (see the existing files).

## Notes

- The conversation partner (prompts in `prompty/`) is set up pedagogically: it asks questions rather than handing out
  solutions. You can change that in the Studio (Text → system prompt preview and your own copies) or in the files.
- The Kie.ai catalog is collected from its documentation (Kie.ai has no catalog API). When new models appear:
  `python narzedzia/kie_katalog.py`.
- Optional: `pdftotext` / `pdftoppm` (Poppler) — reading PDFs attached in the chat.

License: MIT (code and texts). AI models and provider services — their own licenses and terms.
