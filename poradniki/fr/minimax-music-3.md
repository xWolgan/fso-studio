# MiniMax Music 3 — comment prompter

## Comment le modèle écoute
Modèle musical ouvert de MiniMax (août 2026) : à partir des **paroles** et d'une **description du son**, il produit un morceau cohérent jusqu'à 5 minutes (32 kHz, stéréo). La description peut être de la prose ordinaire ou une **description structurée** en trois sections. Les balises de sections et les descriptions sont des indications, pas des garanties — le tempo, la tonalité et la construction ne seront pas toujours respectés à la lettre.

## Structure
**Description structurée (trois sections) :**
1. **Global metadata** — genre, sous-genre, BPM, tonalité, gamme, trajectoire émotionnelle, situation d'écoute, profil de production.
2. **Vocal details** — sexe, timbre, manière de chanter, harmonies, chœurs, effets (pour un morceau instrumental — omets la section ou écris explicitement qu'il n'y a pas de voix).
3. **Arrangement** — instruments principaux et secondaires, leur évolution d'une section à l'autre, groove, basse, batterie, textures, espace.

Modèle tiré de la fiche modèle : « Genre: acoustic pop. BPM: 96. Key: C major. Warm and intimate… » / « Vocals: soft female lead… » / « Arrangement: fingerpicked guitar and soft piano; brushed drums… ».

**Paroles :** balises `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` — **chacune sur sa propre ligne**, sans mots sur la même ligne. Morceau instrumental : sections `[Instrumental]` / `[Solo]`.

## Points sensibles / pièges
- Des paroles sur la même ligne qu'une balise — mal interprétées.
- Morceau long = génération longue (sur le Spark, env. 93 s pour 30 s de musique en mode rapide).

## Exemple (structure, instrumental)
- Description : « Genre: ambient electronica. BPM: 80. Key: D minor. Slowly brightening, from tension to calm. Vocals: none, purely instrumental. Arrangement: analog synth drones, sparse plucked bass, distant processed field recordings, slowly opening filter, wide stereo reverb. »
- Paroles :
```
[Intro]
[Instrumental]
[Solo]
[Outro]
```

## Paramètres qui changent vraiment le résultat
- **Mode** : rapide (encodeur INT8) / qualité maximale (bf16, env. 146 s pour 30 s). **Durée**, **seed**.

## Sources (consultées le 2026-10-05)
- Hugging Face — MiniMaxAI/MiniMax-Music3 : https://huggingface.co/MiniMaxAI/MiniMax-Music3
- MiniMax — Music 3.0 (blog) : https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model
- ComfyUI — MiniMax Music 3 : https://blog.comfy.org/p/minimax-music-3-state-of-the-art
- Prompting MiniMax Music 3 (Space) : https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide
