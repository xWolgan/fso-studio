# FastH3 V2 — comment prompter

## Comment le modèle écoute
FastH3 V2 est une version distillée (DMD2) de MiniMax H3 par l'équipe FastVideo : image et son en **exactement 8 étapes**. **Tu écris le prompt exactement comme pour H3** — même structure en trois champs, balises `<d>`, ID des personnages qui parlent, description en anglais. Détails : guide `minimax-h3`.

## Structure du prompt
Comme pour H3 : d'abord toute la scène (lieu, personnage, ce qui se passe), puis les plans avec le temps, le mouvement de caméra et le son dans un seul bloc ; à part, l'ambiance sonore et la musique hors scène.

## Points sensibles / pièges
- **Le nombre d'étapes est fixe (8)** — le modèle est entraîné sur exactement 8 étapes ; le changer dégrade la qualité.
- La durée est « aimantée » vers une grille de 17 images (17k+5) à 24 i/s ; petit côté natif 768 px, dimensions arrondies à un multiple de 32.
- **Sur le Spark, FastH3 V2 est env. 20–30 % plus lent que le H3 classique en mode rapide** (très probablement faute de noyaux rapides pour l'attention creuse sur le GB10) — ça vaut la peine de comparer les deux avec le même prompt et le même seed.
- Comme pour H3 : pas de prompt négatif ; ne nomme pas ce qui ne doit pas apparaître.

## Exemple
Le même que dans le guide H3 — le format est identique.

## Paramètres qui changent vraiment le résultat
- **Durée** et **format**. Étapes — ne pas modifier.

## Sources (consultées le 2026-10-05)
- ComfyUI — FastVideo FastH3 : https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo
- Hugging Face — FastVideo-FastH3-8-Step-V2 : https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2
- Kombitz — FastH3 V2 dans ComfyUI : https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/
- Mesures : notre propre test sur le Spark.
