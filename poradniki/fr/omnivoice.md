# OmniVoice — comment prompter

## Comment le modèle écoute
Modèle de voix (k2-fsa) pour plus de 600 langues — **il parle bien polonais** (dans notre test, concordance des mots 0,93). Trois façons de travailler : synthèse simple, **conception de voix** à partir d'une liste de traits (sans enregistrement) et **clonage de voix** à partir d'un court enregistrement. Il lit le texte tel qu'il est écrit — la ponctuation façonne la phrase.

## Conception de voix (traits de la liste)
Traits séparés par des virgules, **un seul trait par catégorie** :
- sexe : male / female
- âge : child, teenager, young adult, middle-aged, elderly
- hauteur : very low pitch, low pitch, moderate pitch, high pitch, very high pitch
- style : whisper
- accent anglais : American, British, Australian, Canadian, Indian… (seulement avec un texte en anglais)

Exemple : `female, middle-aged, low pitch` ou `male, elderly, whisper`. Les descriptions en prose (« une voix chaude, fatiguée »), le modèle **ne les comprend pas** dans ce mode.

Dans le Studio, le texte d'échantillon (champ « texte d'échantillon ») doit être dans la langue choisie dans le champ « langue » : le modèle le lit d'abord avec la nouvelle voix, puis clone cet enregistrement et s'en sert pour dire ton texte. L'accent ne fonctionne donc qu'avec un texte en anglais. Chaque lancement conçoit la voix à neuf — pour garder la même voix sur plusieurs répliques, télécharge l'échantillon de référence (le résultat marqué « wzorzec ») et utilise-le pour le clonage.

## Clonage de voix
- Enregistrement de **3–10 s**, voix propre, idéalement avec un instant de silence à la fin. Plus long, ça ralentit et peut dégrader le clone.
- **Transcription de l'échantillon** — exactement ce qu'on entend dans l'enregistrement (sans elle, le Studio ne génère rien).
- Enregistrement dans **la même langue** que celle que doit parler le clone — sinon un accent apparaît.
- La réverbération, la bande magnétique, le son de téléphone de l'échantillon ne sont pas transférés — le modèle « nettoie » le son.

## Texte : prononciation, pauses, sons non verbaux
- Ponctuation = phrasé et pauses (point, virgule, tiret, points de suspension) — une pause due à la ponctuation est probable, pas certaine. Termine toujours le texte par un point, un point d'interrogation ou un point d'exclamation (sinon le modèle coupe plus volontiers la fin).
- **Sons non verbaux entre chevrons :** `<laughter>`, `<sigh>` (ainsi que p. ex. `<question-en>`, `<surprise-ah>`, `<dissatisfaction-hnn>` — en polonais, les plus fiables sont `<laughter>` et `<sigh>`). **N'écris pas `[laughter]`** — dans le Studio, les crochets ont un autre sens.
- **Pause d'une durée précise :** `[pause:1.5s]`, `[pause:500ms]` — plus fiable qu'un point.
- **Changer la langue d'un passage :** `[en:]` avant un passage en anglais.
- **Tout autre `[…]` disparaît** (le Studio le traite comme un nom de personnage) — n'écris pas de didascalies du type `[soupire]`. La notation phonétique de la documentation du modèle (`[B EY1 S]`) ne fonctionne pas dans le Studio.
- **Écris les nombres, dates et abréviations en toutes lettres** (la normalisation du texte est désactivée).

## Points sensibles / pièges
- Les traits hors liste sont ignorés ; le chuchotement et la hauteur basse ne fonctionnent pas avec « child ».
- On ne peut pas imposer une émotion par une description — seuls l'échantillon (clone), le texte et la ponctuation la portent.
- Sans échantillon ni traits (synthèse simple), le modèle choisit **une voix différente** à chaque seed.
- Un retour à la ligne n'est pas une pause — sépare les vers par la ponctuation ou par `[pause:…]`.
- Un texte très long gagne à être découpé en paragraphes (générations séparées) — plus facile à corriger, moins de risque que la voix change en cours de route.

## Paramètres qui changent vraiment le résultat
- **débit de parole** 0,5–2,0 (>1 plus rapide, <1 plus lent ; un peu plus lent aide quand le modèle coupe les fins). Le Studio ne propose pas de durée fixe en secondes.
- **seed** — les résultats varient beaucoup ; essaie-en 2–3 et garde le bon.

## Licence
CC-BY-NC — usage non commercial uniquement.

## Sources (consultées le 2026-10-05)
- k2-fsa/OmniVoice (README) : https://github.com/k2-fsa/OmniVoice
- OmniVoice — voice design : https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md
- TTS Audio Suite — OmniVoice Tags Guide (syntaxe des balises dans le Studio) : https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md
- Test du polonais : notre propre test sur le Spark.
