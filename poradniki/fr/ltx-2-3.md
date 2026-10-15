# LTX 2.3 — comment prompter

## Comment le modèle écoute
LTX 2.3 (Lightricks, 22B) génère de la vidéo avec du son ; il peut aussi prendre une **image** et un **son** en entrée (mouvement synchronisé avec l'enregistrement). Il lit le prompt comme un modèle de langage : **l'ordre des mots fixe la priorité**. Ce qui marche le mieux, c'est **un seul paragraphe fluide au présent**, écrit comme une description de plan destinée au chef opérateur — de la prose, pas une liste de mots-clés. La version distillée tourne à CFG 1 (le négatif ne fonctionne pas).

## Structure du prompt et ordre
Donne le style / médium (si ce n'est pas du photoréalisme) dans la première phrase, puis :
1. L'action principale en une phrase.
2. Les détails du mouvement et des gestes — dans l'ordre chronologique.
3. L'apparence des personnages / objets (avec précision).
4. L'arrière-plan et l'environnement.
5. L'angle et le mouvement de caméra.
6. La lumière et la couleur.
7. Les changements et événements soudains.
8. Le son : acoustique du lieu, timbre de voix, ambiance ; le dialogue entre guillemets.

Longueur : proportionnelle à la durée du clip — en pratique env. 80–220 mots (les sources officielles divergent : le guide 2.3 dit que les prompts longs et détaillés l'emportent, l'article sur le respect du prompt conseille de tenir en env. 200 mots ; le guide 2.5 indique 4–8 phrases pour un plan simple). Un prompt court sur un clip long = le modèle « survole » l'action. **Une action principale toutes les 2–3 secondes** de clip. Pas d'étiquettes du type « Sound: » — intègre le son dans la prose.

## Points sensibles / pièges
- Trop d'événements dans un clip court → le modèle en choisit une partie ou les mélange.
- La « musique/son sans voix » est parfois de moindre qualité (les auteurs le signalent dans la fiche modèle).
- Dimensions divisibles par 32, nombre d'images de la forme 8n+1 (le Studio ajuste de lui-même).

## Exemple (structure)
« A woman in a grey raincoat stops at the edge of a pier and looks down at the water. She slowly crouches, touches the wet wooden planks with her palm and then stands up again. She is in her forties, short dark hair, no make-up. Behind her, a grey sea and a lighthouse in the fog. The camera starts in a wide shot and slowly pushes in to a medium shot. Overcast, soft light, desaturated blue-grey palette. Wind gusts and waves hit the pylons, a distant foghorn sounds, and she quietly says in Polish, "Już tu nie wrócę." »

## Paramètres qui changent vraiment le résultat
- **Durée** (images 8n+1), **format**, **seed**. Dans les workflows du Studio, texte → vidéo, image → vidéo et image + enregistrement se font en deux passes (demi-résolution + upscaler ×2) ; première et dernière image — une seule passe en pleine résolution.

## Sources (consultées le 2026-10-05)
- LTX — LTX-2.3 Prompt Guide : https://ltx.io/blog/ltx-2-3-prompt-guide
- LTX — How to improve LTX-2.3 prompt adherence : https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence
- Hugging Face — Lightricks/LTX-2.3 (fiche modèle) : https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md
- deAPI — LTX-2.3 guide : https://deapi.ai/blog/ltx-2-3-video-generation-guide
