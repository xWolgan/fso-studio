# MiniMax H3 — comment prompter

## Comment le modèle écoute
H3 génère **l'image et un son stéréo ensemble** (dialogues, effets, ambiance, musique). Le prompt est un **scénario avec une ligne de temps**, pas la description d'une image : plans successifs, mouvement de caméra, qui parle et ce qu'on entend. Écris le prompt **en anglais** (les dialogues et le texte à l'écran peuvent être dans leur propre langue — mot pour mot). Il tourne à CFG 1 : **il n'y a pas de prompt négatif**, et nommer une chose indésirable l'ajoute à la description.

## Structure du prompt (disposition officielle en trois champs)
```
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:04.000, the camera cuts to ...

overall_soundscape: ...

non_diegetic_music: ...
```
Champs séparés par une ligne vide, dans cet ordre.
- **integrated_multimodal_description** — les plans `[Shot 1]`, `[Shot 2]`… avec l'image, l'action, le mouvement de caméra et le son diégétique (dialogues, effets, musique dans la scène) dans un seul bloc. D'abord toute la scène (lieu, personnage, ce qui se passe), puis les plans.
- **overall_soundscape** — 1–4 phrases : ambiance, bruits de l'action, sons non verbaux. `N/A` seulement en cas de silence total.
- **non_diegetic_music** — 1–3 phrases sur la musique que seul le spectateur entend ; `N/A` s'il n'y en a pas.
- **Dialogue :** dans des balises `<d>`, avec l'ID de la personne qui parle et une étiquette de langue entre crochets : `(S1) says: <d>[English] Exact words.</d>` (pas `<d>English: …</d>`) ; à l'intérieur de `<d>`, seulement l'étiquette de langue et les mots, termine la réplique par un point/?/!. Chaque voix a un ID fixe `(S1)`, `(S2)`, répété dans chaque plan où elle parle ; décris la voix (âge, sexe, timbre, débit) à sa première apparition, en dehors de `<d>`. Un personnage qui ne parle pas ne reçoit pas d'ID.
- **Texte à l'écran :** entre guillemets, mot pour mot, dans la langue d'origine.
- **Voix off :** « says in an off-screen voiceover » + l'indication que la bouche reste fermée.
- **Caméra :** type de mouvement + amplitude + vitesse, en langage naturel dans la phrase du plan (p. ex. « the camera pushes in with small amplitude at slow speed ») ; vocabulaire : static, zoom in/out, push in / pull out, pan, truck, tilt, pedestal, arc, tracking, shake slightly/strongly, POV, roll.
- **Plans :** `[Shot 1]` sans temps ; les suivants avec le moment de la coupe `At MM:SS.mmm` (croissant, inférieur à la durée du clip). Chaque coupe = une information nouvelle (lieu, état, point de vue).
- **Image → vidéo — c'est toi qui écris la ligne d'alignement.** Le Studio / le nœud ComfyUI n'ajoute rien au prompt (le nœud se contente de marquer les images comme `<Picture n>`). Quand tu fournis des images, **la première ligne du prompt** est, mot pour mot (puis une ligne vide, puis les trois champs) :
  - première image seulement (I2VA) :
    `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
  - première et dernière (FL2VA) — `S.SS` = durée du clip avec deux décimales, `N` = numéro du dernier plan :
    `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  - dernière image seulement (L2VA) :
    `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
  - sans images (texte → vidéo) : pas de ligne d'alignement.
- **Inspirations (Ref2VA) :** quand tu fournis des images/vidéos/sons d'inspiration, le modèle utilise un autre format — six sections `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` avec les balises `<Picture n>`, `<Video n>`, `<Audio n>` ; la première/dernière image sont alors ignorées. L'assistant de prompts du Studio connaît les détails.

## Points sensibles / pièges
- « No on-screen text » ajoute le mot « texte » à la description → écris plutôt « the sign above the door is blank ».
- Durée des plans : une action nette par plan. Clip officiellement de 4 à 15 s (10 s par défaut dans le Studio) ; le modèle a été entraîné sur env. 5–15 s — **règle au moins 5 s**.
- Toutes les langues ne sont pas aussi stables dans les dialogues (le polonais, par exemple, ne fait pas partie des langues bien prises en charge) — garde les répliques courtes et simples (`<d>[Polish] …</d>`) ; dans la description, ne mélange pas ta langue avec l'anglais (le modèle risque de lire la description à voix haute).
- Résolution native : petit côté 768 px ; dans le Studio 480p (par défaut) ou 720p.

## Exemple (structure)
```
integrated_multimodal_description: [Shot 1] Cinematic live-action. A narrow kitchen at night, one lamp on. Medium shot, static camera. An old woman with a low, slightly hoarse voice slowly peels an apple at the table; the knife scrapes softly. (S1) says: <d>[Polish] Jeszcze chwilę.</d> She closes her lips and keeps peeling silently. [Shot 2] At 00:04.000, the camera cuts to a close-up of her hands and pushes in with small amplitude at slow speed; the peel falls in one long ribbon onto the oilcloth.

overall_soundscape: A refrigerator hum, a distant tram outside, the soft scrape of the knife.

non_diegetic_music: N/A
```

## Paramètres qui changent vraiment le résultat
- **Mode** : rapide (LoRA turbo, 8 étapes ; avec inspirations et images clés 4 étapes ; env. 40–44 s pour 2 s de clip sur le Spark ; son et mouvement un peu plus faibles) / qualité maximale (20 étapes ; env. 84 s).
- **Durée** et **format** (nativement 768 px pour le petit côté).

## Sources (consultées le 2026-10-05)
- MiniMax — Video Prompt Writing Guide (lignes d'alignement, format `<d>[Language] …</d>`) : https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- ComfyUI — code des nœuds H3 (le nœud n'ajoute pas de ligne d'alignement) : https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py
- ComfyUI — MiniMax H3 Prompt Guide (format officiel) : https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- RunDiffusion — H3 Prompt Guide : https://www.rundiffusion.com/minimax-h3-prompt-guide
- DEV — H3 camera motion, timing, audio : https://dev.to/jaysean_brambila_1f12d6cc/minimax-h3-prompt-engineering-camera-motion-timing-and-native-audio-1a8g
- Mesures de temps : notre propre test sur le Spark.
