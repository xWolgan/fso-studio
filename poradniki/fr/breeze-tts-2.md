# Breeze TTS 2 — comment prompter

## Comment le modèle écoute
Modèle de voix de BreezeBlue — **anglais et chinois uniquement** (il ne gère ni le polonais ni le français ; pour les autres langues : OmniVoice). Son point fort, c'est le pilotage de la voix par la description : la **conception de voix** en prose (sans enregistrement) et la **direction d'acteur** — le clonage de voix à partir d'un enregistrement, avec une consigne sur la manière de jouer (ton, émotion, tempo, façon de dire).

## Structure
- **Conception de voix :** une description en prose dans la langue du texte, p. ex. « A warm, thoughtful young woman with a clear voice and a calm, reflective delivery. »
- **Direction d'acteur (avec enregistrement) :** une consigne de jeu, p. ex. « Speak slowly with a restrained, serious tone. » Tu peux y demander un accent, un rire, des soupirs, de la fatigue, de la nervosité.
- **Événements dans le texte (anglais) :** entre parenthèses — `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)` ; en chinois entre crochets — `[笑]`, `[叹气]`.

## Points sensibles / pièges
- La langue de la description doit correspondre à celle du texte.
- Enregistrement pour le clone : voix propre, peu de fond sonore, avec une **transcription exacte** dans le champ « transcription de l'échantillon ».
- **Clone pur :** échantillon + transcription, champ « voix et diction » **vide** (par défaut), CFG 1. Toute consigne saisie transforme le clone en direction d'acteur.
- Dans le Studio, le service traite **une seule requête à la fois** — s'il y a une file d'attente, il faut patienter un peu.

## Exemple (structure)
- Description de la voix : « An elderly man with a low, gravelly voice, speaking slowly, as if remembering something painful. »
- Texte : « I kept the key for years. (sigh) I never found the door. »

## Paramètres qui changent vraiment le résultat
- **Force de l'instruction (CFG)** — avancé, 0,5–4. Pour la description de voix et la direction d'acteur, les auteurs recommandent 4. Sans instruction, laisse 1 (toute autre valeur provoque une erreur).

## Licence
Poids réservés à la recherche et à un usage non commercial.

## Sources (consultées le 2026-10-05)
- Hugging Face — BreezeBlue/Breeze-TTS-2 : https://huggingface.co/BreezeBlue/Breeze-TTS-2
- BreezeBlue — Introducing Breeze TTS 2 : https://breezeblue.ai/breeze-tts-2
