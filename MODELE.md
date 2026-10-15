# Modele — co jest potrzebne do każdego

Plik wygenerowany z `modele/*.yaml` i `workflows/`. Ścieżki katalogów są względem `ComfyUI/models/`.
Studio pokazuje tylko modele, które Twoja instalacja umie uruchomić (zob. README). Nie musisz mieć wszystkich.

Licencje modeli są ich własne (pole „licencja” w YAML) — część jest **niekomercyjna**.


## Tekst

### Qwen 3.8 Flash (`qwen-czat`)

Licencja: Apache 2.0  
Model językowy przez API zgodne z OpenAI (`llm_api`, np. OpenRouter) albo lokalnie (`llm_url`, np. llama-swap / Ollama).


## Obraz

### Ideogram 4 (`ideogram-4`)

Licencja: Ideogram 4 Non-Commercial  

- `diffusion_models/ideogram4_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/diffusion_models/ideogram4_fp8_scaled.safetensors
- `diffusion_models/ideogram4_unconditional_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Ideogram-4/resolve/main/diffusion_models/ideogram4_unconditional_fp8_scaled.safetensors
- `text_encoders/qwen3vl_8b_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors
- `vae/flux2-vae.safetensors` — https://huggingface.co/VAST-AI/TripoSplat/resolve/main/vae/flux2-vae.safetensors

### Qwen-Image 2.1 Edit (`qwen-image-2-1-edycja`)

Licencja: Qwen Research (niekomercyjna)  

- `diffusion_models/qwen_image_2.1_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_int8_convrot.safetensors
- `text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_i2i.int8_convrot.safetensors
- `text_encoders/qwen3vl_8b_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors
- `vae/qwen_image_2.1_vae_bf16.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/vae/qwen_image_2.1_vae_bf16.safetensors

### Qwen-Image 2.1 (`qwen-image-2-1`)

Licencja: Qwen Research (niekomercyjna)  

- `diffusion_models/qwen_image_2.1_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/diffusion_models/qwen_image_2.1_int8_convrot.safetensors
- `text_encoders/qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3.5_9b_qwen_image_2.1_pe_t2i.int8_convrot.safetensors
- `text_encoders/qwen3vl_8b_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/text_encoders/qwen3vl_8b_int8_convrot.safetensors
- `vae/qwen_image_2.1_vae_bf16.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-2.1/resolve/main/vae/qwen_image_2.1_vae_bf16.safetensors

### Qwen-Image-Edit 2511 (`qwen-image-edit-2511`)

Licencja: Apache 2.0  

- `diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors` — https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_fp8mixed.safetensors
- `loras/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors` — https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning/resolve/main/Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors
- `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/HunyuanVideo_1.5_repackaged/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors
- `vae/qwen_image_vae.safetensors` — https://huggingface.co/FireRedTeam/FireRed-Image-Edit-1.0-ComfyUI/resolve/main/qwen_image_vae.safetensors

### Z-Image Turbo (`z-image-turbo`)

Licencja: Apache 2.0  

- `diffusion_models/z_image_turbo_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_int8_convrot.safetensors
- `text_encoders/qwen_3_4b_fp8_mixed.safetensors` — https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b_fp8_mixed.safetensors
- `vae/ae.safetensors` — https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors


## Wideo

### FastH3 V2 (`fasth3-v2`)

Licencja: MiniMax (otwarte wagi)  

- `diffusion_models/fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors` — https://huggingface.co/FastVideo/FastVideo-FastH3-Comfy/resolve/main/diffusion_models/fastvideo_fasth3_8step_v2_pruned_int8_convrot.safetensors
- `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- `vae/minimax_h3_audio_vae_fp32.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors
- `vae/minimax_h3_video_vae_fp16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors

### Kling 3.0 Omni · referencja wideo · API (`kling-3-omni-wideo`)

Licencja: Kling (usługa komercyjna, przez HiggsField)  
Przez API (higgsfield) — wystarczy klucz w `sekrety.env` (`HF_KEY`). Płatne, liczone w budżecie.

### Kling 3.0 Omni · API (`kling-3-omni`)

Licencja: Kling (usługa komercyjna, przez HiggsField)  
Przez API (higgsfield) — wystarczy klucz w `sekrety.env` (`HF_KEY`). Płatne, liczone w budżecie.

### Kling 3.0 · API (`kling-3`)

Licencja: Kling (usługa komercyjna, przez HiggsField)  
Przez API (higgsfield) — wystarczy klucz w `sekrety.env` (`HF_KEY`). Płatne, liczone w budżecie.

### LTX 2.3 (`ltx-2-3`)

Licencja: LTX-2 Community  

- `checkpoints/ltx-2.3-22b-distilled-fp8.safetensors` — https://huggingface.co/Lightricks/LTX-2.3-fp8/resolve/main/ltx-2.3-22b-distilled-fp8.safetensors
- `latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.1.safetensors` — https://huggingface.co/Lightricks/LTX-2.3/resolve/main/ltx-2.3-spatial-upscaler-x2-1.1.safetensors
- `text_encoders/gemma_3_12B_it_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/ltx-2/resolve/main/split_files/text_encoders/gemma_3_12B_it_fp8_scaled.safetensors

### LTX 2.5 (`ltx-2-5`)

Licencja: LTX-2 Community  

- `diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors` — https://huggingface.co/Lightricks/LTX-2.5/resolve/main/diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors
- `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` — https://huggingface.co/Lightricks/LTX-2.5/resolve/main/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
- `text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` — https://huggingface.co/Lightricks/LTX-2.5/resolve/main/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors
- `text_encoders/gemma4_e2b_it_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/gemma-4/resolve/main/text_encoders/gemma4_e2b_it_int8_convrot.safetensors
- `vae/ltx-2.5-audio-vae-bf16.safetensors` — https://huggingface.co/Lightricks/LTX-2.5/resolve/main/vae/ltx-2.5-audio-vae-bf16.safetensors
- `vae/ltx-2.5-video-vae-bf16.safetensors` — https://huggingface.co/Lightricks/LTX-2.5/resolve/main/vae/ltx-2.5-video-vae-bf16.safetensors

### MiniMax H3 · klatki kluczowe (`minimax-h3-klatki`)

Licencja: MiniMax (otwarte wagi)  

- `diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors
- `loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
- `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- `vae/minimax_h3_audio_vae_fp32.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors
- `vae/minimax_h3_video_vae_fp16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors

### MiniMax H3 (`minimax-h3`)

Licencja: MiniMax H3 Community License (zgoda na UE — wniosek w toku)  

- `diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
- `diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors
- `loras/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors` — https://huggingface.co/lightx2v/Minimax-h3-Turbo/resolve/main/minimax_h3_fl2v_turbo_8step_v1.0_comfyui_bf16.safetensors
- `loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/loras/minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors
- `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- `vae/minimax_h3_audio_vae_fp32.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_audio_vae_fp32.safetensors
- `vae/minimax_h3_video_vae_fp16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-H3/resolve/main/vae/minimax_h3_video_vae_fp16.safetensors

### WAN 2.2 (`wan-2-2`)

Licencja: Apache 2.0  

- `diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors
- `diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors
- `diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors
- `diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors
- `loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors
- `loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors
- `loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors
- `loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/loras/wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors
- `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors?download=true
- `vae/wan_2.1_vae.safetensors` — https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors

### WAN 3.0 · API (`wan-3`)

Licencja: Alibaba Wan (usługa komercyjna, przez HiggsField)  
Przez API (higgsfield) — wystarczy klucz w `sekrety.env` (`HF_KEY`). Płatne, liczone w budżecie.


## Muzyka

### ACE-Step 1.5 XL (`ace-step-1-5-xl`)

Licencja: MIT  

- `diffusion_models/acestep_v1.5_xl_sft_bf16.safetensors` — https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/diffusion_models/acestep_v1.5_xl_sft_bf16.safetensors
- `text_encoders/qwen_0.6b_ace15.safetensors` — https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_0.6b_ace15.safetensors
- `text_encoders/qwen_4b_ace15.safetensors` — https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_4b_ace15.safetensors
- `vae/ace_1.5_vae.safetensors` — https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/vae/ace_1.5_vae.safetensors

### MiniMax Music 3 (`minimax-music-3`)

Licencja: MiniMax Community (komercyjnie do 20 mln $ przychodu)  

- `diffusion_models/minimax_music3_dit_fp16.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/diffusion_models/minimax_music3_dit_fp16.safetensors
- `text_encoders/minimax_music3_text_encoder_pruned_int8_convrot.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/text_encoders/minimax_music3_text_encoder_pruned_int8_convrot.safetensors
- `vae/minimax_music3_dav.safetensors` — https://huggingface.co/Comfy-Org/MiniMax-Music-3/resolve/main/vae/minimax_music3_dav.safetensors

### YuE 2 · cover z nagrania (`yue-2-cover`)

Licencja: CC-BY-NC (niekomercyjna)  

- `audio_encoders/sheetsage2_bf16.safetensors` — https://huggingface.co/Comfy-Org/YuE2/resolve/main/audio_encoders/sheetsage2_bf16.safetensors
- `checkpoints/yue2_3b_bf16.safetensors` — https://huggingface.co/Comfy-Org/YuE2/resolve/main/checkpoints/yue2_3b_bf16.safetensors

### YuE 2 (`yue-2`)

Licencja: CC-BY-NC (niekomercyjna)  

- `checkpoints/yue2_3b_bf16.safetensors` — https://huggingface.co/Comfy-Org/YuE2/resolve/main/checkpoints/yue2_3b_bf16.safetensors


## SFX

### Stable Audio 3 small-SFX (`stable-audio-3`)

Licencja: Stability AI Community (komercyjnie do 1 mln $ przychodu)  

- `checkpoints/stable_audio_3_small_sfx.safetensors` — https://huggingface.co/Comfy-Org/stable-audio-3
- `text_encoders/t5gemma_b_b_ul2.safetensors` — https://huggingface.co/Comfy-Org/stable-audio-3/resolve/main/text_encoders/t5gemma_b_b_ul2.safetensors

### Woosh — dźwięk do wideo (`woosh-wideo`)

Licencja: Sony AI — niekomercyjna (badania)  
Osobna usługa HTTP `woosh` (nie ma jej w tym repo) — w `config.yaml` → `maszyny[].uslugi`. Dla zaawansowanych.

### Woosh — efekt z opisu (`woosh`)

Licencja: Sony AI — niekomercyjna (badania)  
Osobna usługa HTTP `woosh` (nie ma jej w tym repo) — w `config.yaml` → `maszyny[].uslugi`. Dla zaawansowanych.


## Mowa

### Breeze TTS 2 (EN / ZH) (`breeze-tts-2`)

Licencja: niekomercyjna (wagi i wyniki); kod Apache 2.0  
Osobna usługa HTTP `breeze` (nie ma jej w tym repo) — w `config.yaml` → `maszyny[].uslugi`. Dla zaawansowanych.

### OmniVoice · klonowanie głosu (`omnivoice-klon`)

Licencja: CC-BY-NC (niekomercyjna)  
Wymaga węzłów **TTS-Audio-Suite**: https://github.com/diodiogod/TTS-Audio-Suite — wagi OmniVoice pobiera sam przy pierwszym użyciu (do `ComfyUI/models/TTS/`).  


### OmniVoice · projektowanie głosu (`omnivoice-projekt`)

Licencja: CC-BY-NC (niekomercyjna)  
Wymaga węzłów **TTS-Audio-Suite**: https://github.com/diodiogod/TTS-Audio-Suite — wagi OmniVoice pobiera sam przy pierwszym użyciu (do `ComfyUI/models/TTS/`).  


### OmniVoice (`omnivoice`)

Licencja: CC-BY-NC (niekomercyjna)  
Wymaga węzłów **TTS-Audio-Suite**: https://github.com/diodiogod/TTS-Audio-Suite — wagi OmniVoice pobiera sam przy pierwszym użyciu (do `ComfyUI/models/TTS/`).  


