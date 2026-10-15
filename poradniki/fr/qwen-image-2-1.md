# Qwen-Image 2.1 — comment prompter

## Comment le modèle écoute
Grand modèle d'image qui comprend très bien les longues descriptions et excelle dans le **rendu de texte** (texte dense et petit, mises en page d'affiches, de diapositives, d'infographies). Il tourne à CFG 1 — le prompt négatif ne fonctionne pas. Il intègre un « enrichisseur de prompt », **désactivé par défaut** : un petit LLM réfléchit d'abord, puis réécrit ton prompt en plus long avant que l'image ne soit créée — cela prend plus de temps, env. 1–2 min (dans le Studio : l'interrupteur « le modèle enrichit lui-même le prompt »).

## Structure du prompt
- **Texte → image :** en prose : ce qu'il y a dans l'image → composition → lumière et couleur → style/médium. Texte dans l'image : donne les **mots exacts** (entre guillemets) et décris où et comment ils doivent être disposés (police, taille, ordre).
- **Retouche (images de référence) :** désigne les images par leur numéro : `<image1>`, `<image2>`… ; dis explicitement ce qui reste inchangé et ce qui change. Modèle tiré de la documentation : « Keep the character and pose in `<image1>` unchanged, put this light blue denim shirt from `<image2>` on the character, preserve the original facial features, hair, body shape and pose ».
- **Modifier une zone :** peins la zone d'une couleur sur l'image d'entrée et fais référence à cette couleur dans la consigne : « change the jacket in the red area ».

## Points sensibles / pièges
- L'enrichisseur de prompt modifie tes mots — quand tu travailles sur un cadre précis, laisse-le désactivé ; active-le si tu veux voir l'interprétation du modèle.
- Donne le texte mot pour mot ; une paraphrase = un autre texte.

## Exemples (structure)
- « A slide-style infographic on off-white background. Title at the top in bold sans-serif: "Ruch wody". Below, three columns with small line icons and one-line captions. Muted blue and grey palette. »
- Retouche : « Keep the room in `<image1>` unchanged. Replace the view outside the window with the winter landscape from `<image2>`, matching the evening light of the room. »

## Paramètres qui changent vraiment le résultat
- **Étapes** : 25 par défaut (CFG 1).
- **Enrichissement du prompt** : oui/non (voir plus haut).

## Sources (consultées le 2026-10-05)
- ComfyUI — Qwen-Image 2.1 : https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1
- Qwen-Image 2.1 Prompt Enhancer (description des modes T2I / retouche) : https://github.com/benjiyaya/ComfyUI-Qwen-Image-2.1-Prompt-Enhancer/
