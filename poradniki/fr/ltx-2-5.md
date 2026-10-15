# LTX 2.5 — comment prompter

## Comment le modèle écoute
LTX 2.5 (Lightricks, août 2026) — successeur de LTX 2.3, avec son et **multi-plans natif** : en une seule génération, il sait enchaîner plusieurs plans reliés en conservant le personnage, la scène, la lumière, le style et la voix. Les règles d'écriture sont celles de la 2.3 : **un seul paragraphe chronologique**, au présent, en prose.

## Structure du prompt (six éléments du guide de Lightricks)
1. **Plan** — valeur de plan et termes de prise de vue.
2. **Scène** — lumière, couleur, texture.
3. **Action** — comme une séquence naturelle, du début à la fin.
4. **Personnages** — âge, cheveux, vêtements, émotions montrées physiquement (par un geste, une expression).
5. **Mouvement de caméra.**
6. **Son** — dialogue entre guillemets, ambiance, effets.

Longueur : officiellement env. 4–8 phrases pour un plan simple, davantage pour des scènes complexes — à condition que chaque phrase ajoute un détail concret d'image ou de son. Pas d'étiquettes du type « Sound: »/« Audio: » — intègre le son dans la prose, à côté de l'action qui le provoque. Nomme toujours le mouvement de caméra (pas de mouvement = « the camera remains static »), sinon le modèle a tendance à faire un travelling avant de lui-même.

**Plusieurs plans (2–4, texte → vidéo uniquement) :** toute la scène en un seul paragraphe ; nomme chaque coupe avec des mots (« A hard cut transitions to… », « The view cuts to a close-up of… »), dans le nouveau plan décris à nouveau qui s'y trouve, et précise si le son continue à travers la coupe.

## Points sensibles / pièges
- Les coupes doivent être nommées — sinon le modèle fait un seul long plan.
- Un personnage qui n'est pas redécrit après la coupe peut « sauter » d'apparence.
- Image → vidéo : commence par une phrase cohérente avec l'image (plan, sujet, lieu), puis le mouvement — en un seul plan. L'identité du personnage de l'image est parfois modifiée.
- L'« enrichissement » (le modèle enrichit lui-même le prompt) ajoute un vernis « cinéma » et des mouvements de caméra, et s'éloigne parfois du contenu — pour un travail stylisé, laisse-le désactivé.

## Exemple (structure)
« Medium shot of a man in a worn leather jacket sitting alone in an empty bus at night, his face lit by passing streetlights. He looks at a folded letter in his hands and slowly unfolds it. A hard cut transitions to a close-up of the letter: handwritten lines, a coffee stain in the corner. The view cuts back to the man, the same leather jacket, as he folds the letter again and looks out of the window. The engine drone and the rattle of the windows continue across both cuts as he exhales softly. »

## Paramètres qui changent vraiment le résultat
- **Durée**, **format**, **seed**.
- **Enrichissement** (avancé, désactivé par défaut) — réécrit le prompt avec le modèle Gemma 4 E2B ; ajoute env. 1–2 min.

## Sources (consultées le 2026-10-05)
- LTX — LTX-2.5 Prompt Guide : https://ltx.io/blog/ltx-2-5-prompt-guide
- LTX Docs — Prompting Guide : https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide
- deAPI — LTX-2.5 Prompt Guide (multi-plans, son) : https://deapi.ai/blog/ltx-2-5-prompting-guide-multi-shot-scenes-native-audio-and-prompts-that-actually-cut
- Runware — LTX-2.5 prompting : https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/prompting
- Hugging Face — Lightricks/LTX-2.5 : https://huggingface.co/Lightricks/LTX-2.5
