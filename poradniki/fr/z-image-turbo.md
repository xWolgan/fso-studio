# Z-Image Turbo — comment prompter

## Comment le modèle écoute
Modèle distillé rapide (8 étapes, CFG 1). Il réagit le mieux à des **descriptions longues et concrètes**, écrites comme une consigne au chef opérateur, et non comme une liste d'adjectifs. **Le prompt négatif ne fonctionne pas** (à CFG 1, il est ignoré) — tout ce qui doit être dans le cadre, ou ne pas y être, se décrit de façon positive.

## Structure du prompt et ordre des blocs
`[médium et style] → [plan, angle et composition] → [objet/personnage : apparence] → [vêtements, matériaux, couleurs] → [environnement/arrière-plan] → [lumière et palette] → [texture ; pour une photo : un seul appareil/objectif et une seule pellicule] → [texte dans le cadre] → [contraintes décrites positivement]`

Écris **en anglais**, en phrases complètes, de façon factuelle — pas en liste de tags. Les auteurs recommandent des prompts longs et détaillés ; la communauté indique env. 80–250 mots comme bonne fourchette. Dans le Studio, le prompt n'est pas tronqué (la limite de 512 tokens ne concerne que le code officiel diffusers, pas ComfyUI) et personne ne l'enrichit en chemin.

Donne le médium au début — le modèle tire vers le photoréalisme ; pour un dessin ou une peinture, n'utilise pas de mots liés à l'appareil photo ou à la pellicule, sinon la photo revient. Traduis l'ambiance en lumière, palette, cadrage et matière — sans métaphores ni jugements (« beautiful », « masterpiece », « 8K »).

## Points sensibles / pièges
- Les généralités (« beau », « épique ») donnent un résultat générique ; le détail fonctionne.
- Au lieu de « sans personne » — décris ce qu'il y a dans le cadre (« une rue vide, seulement des pavés mouillés et des réverbères »).
- Très rapide (quelques secondes) — bon pour chercher une direction ; compare la qualité finale avec Qwen-Image 2.1.
- **Faible diversité :** changer le seed donne souvent presque la même image. Une variante = un cadre décrit autrement (plan, angle, moment de la journée, disposition), pas seulement un autre seed.
- Texte dans l'image : court, mot pour mot entre guillemets `"…"`, avec emplacement et police. Fiable seulement en anglais et en chinois ; caractères accentués — non confirmés (pour le texte, mieux vaut Ideogram 4 ou Qwen-Image 2.1).
- Il n'y a pas de pondérations `(mot:1.3)` — parenthèses et nombres arrivent au modèle comme du texte.
- Sans description de texture (pores, tissage du tissu, grain), les personnes sortent « plastiques » et banque d'images.

## Exemples (structure)
- « Photograph, close-up portrait at eye level, centred composition, shallow depth of field. A middle-aged man with grey stubble, tired half-closed eyes and visible skin pores, in a dark wool coat. Behind him a blurred tram stop at dusk. Cold blue ambient light with a warm sodium streetlamp from the left. Shot on a 50mm lens, Kodak Portra 400, fine film grain. »
- « Documentary photograph, wide shot from a high angle. An empty concrete courtyard after rain, only wet concrete and puddles reflecting an overcast sky. A single red bicycle leaning against the wall in the right third. Flat diffuse light, muted grey palette with one red accent. »

## Paramètres qui changent vraiment le résultat
- **Étapes** (avancé, 4–16, 8 par défaut) — le modèle est entraîné sur 8 étapes ; moins = esquisse, plus ne veut pas toujours dire mieux.
- **Seed** — levier faible (faible diversité) ; un seed fixe est utile pour voir l'effet de chaque changement dans le prompt.

## Sources (consultées le 2026-10-05)
- Tongyi-MAI/Z-Image-Turbo — fiche modèle : https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- Tongyi-MAI/Z-Image-Turbo — « PROMPTING GUIDE » (réponses des auteurs) : https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8
- Z-Image-Turbo Prompting Guide (communauté) : https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32
- deAPI — Z-Image Turbo prompting : https://deapi.ai/blog/z-image-turbo-prompting-guide-formula-tips-and-5-example-prompts
- fal — Z-Image Turbo prompt guide : https://fal.ai/learn/devs/z-image-turbo-prompt-guide
