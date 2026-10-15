# Stable Audio 3 small-SFX — comment prompter

## Comment le modèle écoute
Petit modèle (459M) spécialisé dans les **effets sonores**, signé Stability AI. Il travaille en **stéréo**, effets jusqu'à env. 2 minutes, très rapidement (10 s d'effet en 1–2 s sur le Spark). Il aime les descriptions factuelles, comme une fiche de sonothèque : source, action, caractère de l'enregistrement.

## Structure de la description (ordre selon Stability AI)
1. **Source** — quel objet, instrument ou synthétiseur sonne, précisément.
2. **Action** — comment le son naît, combien de temps il dure, comment il s'éteint (queue courte/longue).
3. **Production / caractère** — placement du micro, acoustique de la pièce, traitement.

Les auteurs recommandent aussi la balise **`TrackType: SFX`**, qui donne généralement des effets plus pertinents.

## Points sensibles / pièges
- **Règle une durée courte** — la plupart des effets sont courts ; une durée longue pour un événement court donne du silence ou des répétitions.
- Décris le matériau, la force de l'impact et la longueur de la queue — c'est ce qui change le plus le résultat.

## Exemples (tirés du guide de Stability AI)
- « A blunt, powerful 'thud' made by slamming a wooden desk drawer shut. It has a pronounced low-mid body, making it feel heavy, and is given a touch of analog distortion for aggressive character. »
- « A classic, natural recording of 14-inch hi-hats played tightly closed. Zero ring and a very fast decay. »
- « A massive sub-bass note that mimics a vinyl record or tape machine being turned off. »

## Paramètres qui changent vraiment le résultat
- **Durée** (1–120 s ; c'est un vrai contrôle de la durée — adapte-la à l'événement : impact 1–3 s, action 3–6 s, ambiance 6–15 s et plus) et **seed** (la génération prend 1–2 s — fais des variantes avec le seed).
- Le Studio utilise le modèle distillé small-SFX (8 étapes, CFG 1), donc **il n'y a pas de champ négatif** — ce qui ne doit pas être là, ne le décris tout simplement pas. Le volume n'est pas normalisé.

## Sources (consultées le 2026-10-05)
- Stability AI — Stable Audio 3 prompting (GitHub) : https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md
- Stability AI — Stable Audio 3.0 Prompt Guide : https://stability.ai/guides/stable-audio-3-prompt-guide
- ComfyUI — Stable Audio 3 : https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3
