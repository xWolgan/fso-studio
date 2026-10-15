# WAN 2.2 — comment prompter

## Comment le modèle écoute
WAN 2.2 (14B ; deux modèles : « high noise » construit la composition et le mouvement, « low noise » affine les détails) génère de la vidéo **sans son**. Il aime les **prompts détaillés et descriptifs** (les exemples des auteurs dépassent souvent 100 mots) ; il comprend l'anglais et le chinois. Point fort : un nombre énorme de LoRA de la communauté.

## Structure du prompt et ordre
`[objet/personnage] + [action] + [environnement] + [mouvement de caméra] + [lumière] + [style] + [mouvement dans l'environnement et rythme]`

Associe mouvement de caméra et mouvement du personnage dans une même phrase, p. ex. « The dancer spins in place while the camera smoothly orbits clockwise around her ». Vocabulaire caméra : slow tracking shot, orbit, dolly-in / dolly-out, pan left/right, tilt up/down, crane, handheld follow, static camera, drone pullback.

**Image → vidéo :** décris le mouvement et le changement, pas ce qui est déjà visible sur l'image.

## Points sensibles / pièges
- **Le prompt négatif ne fonctionne qu'en mode qualité maximale** (CFG 3,5–4). En mode rapide (LoRA lightx2v, 4 étapes, CFG 1), il est ignoré.
- Ajoute les négatifs en réaction : d'abord une génération sans eux, puis ajoute l'artefact précis qui est apparu (p. ex. « morphing, warping, flickering, face deformation »).
- Nativement **16 i/s**, nombre d'images de la forme 4n+1 (p. ex. 81 images ≈ 5 s) ; 480p ou 720p. Les clips de plus de 5 s environ sortent de ce sur quoi le modèle a été entraîné.

## Exemple (structure)
« An old fisherman mends a net on a wooden jetty, his fingers moving quickly through the knots. Gulls circle above, the water glitters. The camera slowly dollies in from a medium shot to a close-up of his hands. Late afternoon golden light, long shadows. Naturalistic documentary style, gentle wind moving the net. »

## Paramètres qui changent vraiment le résultat
- **Mode** : rapide (lightx2v, 4 étapes ; env. 28 s pour 2 s de clip sur le Spark) / qualité maximale (20 étapes ; env. 210 s).
- **LoRA** — quand elles seront disponibles dans le Studio, chacune aura une force recommandée.

## Sources (consultées le 2026-10-05)
- Wan-Video / Wan2.2 (dépôt officiel) : https://github.com/Wan-Video/Wan2.2
- VEED — Wan 2.2 Prompting Guide : https://www.veed.io/learn/wan-2-2-prompting-guide
- Dreamina — Wan 2.2 Prompt Guide : https://dreamina.capcut.com/ai-video/wan-2-2-prompt
- Mesures : notre propre test sur le Spark.
