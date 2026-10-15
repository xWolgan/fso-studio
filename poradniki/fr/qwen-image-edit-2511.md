# Qwen-Image-Edit 2511 — comment prompter

## Comment le modèle écoute
Modèle de retouche d'image par consigne, orienté vers la **préservation de la cohérence** (identité des personnages, style, composition) et la retouche du texte dans l'image. La première image est traitée comme **image principale** (la toile) — c'est elle qui change ; la deuxième sert de référence (dans le Studio : jusqu'à deux images). Le résultat fait env. 1 MP aux proportions de l'image 1 (le Studio la redimensionne avant la retouche), pas la taille de l'original. Écris la consigne **en anglais**, en prose simple, comme un ordre (verbe en tête), pas comme la description de l'image finale.

## Structure de la consigne
`[opération : Replace / Change / Remove / Add…] + [cible et emplacement dans le cadre] + [par quoi / depuis quelle image, concrètement] + [ce qui doit rester inchangé]`
- Désigne les images par **« image 1 », « image 2 »** — dans l'ordre d'import (pas `<image1>` — c'est la syntaxe de Qwen-Image 2.1 Edit).
- Ajoute toujours ce qui reste — brièvement, en bloc et à la forme affirmative : « Keep the face, pose, background and lighting unchanged. » Ne décris pas en détail l'apparence de ce qui doit rester (le modèle se mettrait à le redessiner).
- Désigne l'identité d'une personne de la référence par l'image (« the woman from image 2 »), ne décris pas le visage avec des mots.
- Modèle : « Place the person from image 2 into the scene in image 1, matching the lighting and perspective. Keep the rest of image 1 unchanged. »
- Texte dans l'image : entre guillemets, mot pour mot, dans ta langue (« Replace the text "OPEN" with "FERMÉ" ») ; caractères accentués — non confirmés.
- Une seule opération par consigne ; fais une retouche complexe en chaîne (résultat → nouvelle entrée).

## Points sensibles / pièges
- Une consigne vague (« rends-le plus joli ») = des changements inattendus dans toute l'image. Plus c'est concret, moins le reste change.
- Les références au cadrage et à la perspective similaires se combinent mieux.
- L'image peut légèrement se décaler ou zoomer par rapport à l'entrée — pour les retouches locales, ajoute « keep the framing and camera angle unchanged ».
- La peau est parfois « plastique » — pour les portraits, demande une texture de peau naturelle.
- Il n'y a ni pondérations `(mot:1.3)` ni négatifs — les parenthèses arriveront au modèle comme du texte.
- Mode rapide (Lightning, 4 étapes, CFG 1, env. 30 s) — pour les essais, perd la texture ; mode qualité (40 étapes, CFG 4, env. 7 min) — nettement plus précis dans le détail.

## Exemples (structure)
- « Change the season in image 1 to late autumn: bare trees, wet leaves on the ground. Keep the buildings, the people and the camera angle unchanged. »
- « Replace the sofa fabric in image 1 with the material from image 2. Keep the shape of the sofa, the room and the lighting unchanged. »

## Paramètres qui changent vraiment le résultat
- **Mode** rapide / qualité. **Seed** — avec un seed fixe, on voit l'effet de la seule consigne.

## Sources (consultées le 2026-10-05)
- Qwen/Qwen-Image-Edit-2511 — fiche modèle : https://huggingface.co/Qwen/Qwen-Image-Edit-2511
- QwenLM/Qwen-Image — README et réécriture des consignes de retouche : https://github.com/QwenLM/Qwen-Image
- Scenario — Advanced Editing with Qwen Models : https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models
- Replicate — qwen-image-edit-2511 : https://replicate.com/qwen/qwen-image-edit-2511
- RunComfy — Qwen Image Edit 2511 in ComfyUI : https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing
