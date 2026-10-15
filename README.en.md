# Studio — improvising with AI in text, image, video and sound

*Polski: [README.md](README.md)*

A browser-based Studio built for the workshop “AI Form Research Group” (Kraków, 2026). One place to work with generative
models in six areas — **Text, Image, Video, Music, SFX, Speech** — with a job queue, gallery, notes, and a conversation
partner (LLM) that helps you search for form, keeps the piece's “bible”, and writes prompts for specific models.

This repository contains **no keys, no models and no access to our machines**. You connect your own:
- **your own computer with an NVIDIA GPU and ComfyUI** — local generation, free;
- **your own API keys** — OpenRouter (conversation) and HiggsField (video: Kling, WAN, MiniMax H3);
- or both. The Studio only shows the models your installation can actually run.

Interface: Polish, English, French (switch in the header).

## What's inside

| Area | Local (ComfyUI) | Via API |
|---|---|---|
| Text | — (optionally a local LLM as fallback) | OpenRouter (default: Qwen 3.8 Flash) |
| Image | Z-Image Turbo, Qwen-Image 2.1 (+ Edit), Qwen-Image-Edit 2511, Ideogram 4 | — |
| Video | MiniMax H3 (+ keyframes, references), FastH3 V2, LTX-2.3, LTX-2.5, WAN 2.2 | Kling 3.0, Kling 3.0 Omni, WAN 3.0 (HiggsField); MiniMax H3 as a fallback for the local one |
| Music | ACE-Step 1.5 XL, MiniMax Music 3, YuE 2 (+ cover from a recording) | — |
| SFX | Stable Audio 3 small-SFX (Woosh — separate service, not in this repo) | — |
| Speech | OmniVoice: text-to-speech, voice design and cloning (Breeze TTS — separate service) | — |

Full list with files to download and licenses: **[MODELE.md](MODELE.md)**. Model licenses are their own — some are non-commercial.

## Requirements

- **Python 3.11+**
- a browser
- for local generation: **ComfyUI ≥ 0.39** (https://github.com/comfyanonymous/ComfyUI) on a machine with an NVIDIA GPU
  (video: realistically 24–48 GB VRAM; image and audio less); for Speech (OmniVoice) — the **TTS-Audio-Suite** nodes
- optional: `pdftotext` / `pdftoppm` (Poppler) — reading PDFs attached in the chat

## Quick start

```bash
git clone https://github.com/xWolgan/fso-studio.git
cd fso-studio
./start.sh            # Linux / macOS
```
Windows: double-click **`start.cmd`** (or `.\start.ps1` in PowerShell).

The first run creates `config.yaml` and `sekrety.env` (“secrets.env”) from the examples and installs dependencies. Then:

1. **Keys** — put them in `sekrety.env` (never committed):
   - `OPENROUTER_API_KEY` — https://openrouter.ai/keys (conversation, mirror, promptmaker, “description → JSON”),
   - `HF_KEY` — https://console.higgsfield.ai, format `key_id:secret` (video via API; paid).
2. **Machines** — in `config.yaml` → `maszyny:` (“machines”) add your ComfyUI (address and the areas it serves). Without a GPU keep `maszyny: []`.
3. **Model files** — download the ones you want into `ComfyUI/models/...` (list: `MODELE.md`). Hide models you don't have with `modele_wylaczone:`.
4. Restart and open **http://127.0.0.1:8100**. The login is any name (no password) — it separates people's files and budgets.

Area names in the config are Polish: `tekst` (text), `obraz` (image), `wideo` (video), `muzyka` (music), `sfx`, `mowa` (speech).

### API-only mode (no GPU)
`OPENROUTER_API_KEY` (Text) and/or `HF_KEY` (Video via API) plus `maszyny: []` is enough. Areas without models are shown as “not set up”.

### With your own ComfyUI
```yaml
maszyny:
  - id: my-pc
    nazwa: My computer
    comfyui: http://127.0.0.1:8188
    role: [obraz, muzyka, sfx, mowa]     # add "wideo" if your GPU can handle it
modele_wylaczone: [ideogram-4]           # models whose weights you didn't download
```
Several machines = several entries; the Studio distributes jobs between them.

## Security — please read

- **The Studio has no passwords.** The login is just a name. By default it listens only on `127.0.0.1` (this computer).
  Share it only on a trusted network (`HOST=0.0.0.0 ./start.sh`) or through a VPN such as Tailscale — **never directly on the internet**,
  or anyone could generate at your expense and read other people's files.
- Keep keys only in `sekrety.env`. Users' conversations and files live in `zasoby/` (also outside git).
- Text conversations are sent to the LLM provider (OpenRouter and onwards); API jobs — to HiggsField.

## Budget (API only)
API generations use a budget counted in “seconds” (`budzet` in `config.yaml`): 1000 s per person by default,
1 s = 0.042 USD. Local generation is unlimited. When a local job would take longer than `prog_zadania_s`, the Studio offers a paid model.
Prices in `modele/wideo/*.yaml` (`cena`) are from October 2026 (with a promotional discount) — check current HiggsField pricing.

## Your own models
A model = a YAML file in `modele/<area>/` + a ComfyUI workflow in API format in `workflows/` (in ComfyUI: *Workflow → Export (API)*).
See the example in [README.md](README.md#własne-modele) and the existing files in `modele/`. A selector `"@<node id>.<input>"`
targets one node in the workflow; `"<Class>.<input>"` targets all nodes of that class.

## Notes
- Times in descriptions and guides were measured on an **NVIDIA DGX Spark** (“Spark” in the texts) and an RTX PRO 5000 48 GB.
- The conversation partner (prompts in `prompty/`) is set up pedagogically: it asks questions rather than handing out solutions.
  You can change that in the Studio (Text → system prompt preview and your own copies) or in the files.
- Big-screen board: **/tablica** (machines, queue, recent results — without prompt contents).

License: MIT (code and texts). AI models — their own licenses.
