<!-- Fiche modèle pour le promptmaker. modele: breeze-tts-2 -->
# Breeze TTS 2 (BreezeBlue, poids ouverts 08.2026) — voix EN / ZH, voix à partir d'une description

## Ce que c'est et à quoi ça sert
- Modèle TTS d'environ 3B, **anglais et chinois uniquement** dans un seul modèle ; sortie 24 kHz mono [4][6] (officiel). **Ne parle ni polonais ni français** — pour les autres langues, OmniVoice [1] (notre configuration).
- Point fort : **contrôle de la voix par une description libre en langage naturel** [4][6] (officiel). Trois modes, choisis selon les champs remplis [4][5] (officiel / code) :
  - **Voice Design** — l'instruction seule, sans échantillon : une nouvelle voix à partir de la description d'un personnage ;
  - **Voice Clone** — échantillon + transcription exacte, **sans instruction** : timbre, rythme, émotion et style tirés de l'échantillon ;
  - **Voice Direction** — échantillon + transcription + instruction : la voix vient de l'échantillon, et l'instruction dirige le ton, l'émotion, le tempo, le débit.
- Événements vocaux dans le texte (EN) : `(laugh)`, `(cough)`, `(clears throat)`, `(sigh)` [4][6] (officiel).
- Dans notre test : concordance des mots 1,00 (Whisper) pour les modes simple, conçu et dirigé ; une phrase de 5 à 9 s de parole se calcule en 7 à 15 s [3] (notre configuration). Le service accepte **une seule requête à la fois** — file d'attente [3].
- **Ce qu'il NE fait PAS bien :**
  - **le polonais, le français** ni d'autres langues (la version hébergée « multilingual » avec 51 langues est **un autre modèle**, pas celui du Studio) [13] (officiel) ;
  - **les noms propres non anglais / mots inhabituels** dans un texte anglais — un testeur : marques, sigles, noms chimiques mal prononcés ; pas de dictionnaire phonétique, une graphie phonétique aide (« Kree-Pal ») [17] (communauté) ;
  - **l'acoustique de l'environnement** (pièce, téléphone, bande magnétique) — les descriptions d'environnement ne font pas partie des catégories de contrôle documentées [7][16] (officiel ; aucune confirmation que ça marche) ;
  - **une voix identique entre des textes différents par le seul seed** — le seed ne reproduit le résultat que pour une entrée identique [9] (officiel) ;
  - rarement : fin qui s'éteint, mot déformé avec un seed donné (signalement sur un GPU sans BF16 ; le fabricant met en cause le matériel) [8] (communauté/officiel).
- Licence : poids et résultats uniquement pour la recherche/un usage non commercial [4] (officiel).

## Ce que le participant règle dans le Studio
Le Studio appelle le service Breeze (`/v1/audio/speech`), en mode de base (eager) [1][3] (notre configuration). Un champ texte vide **n'est pas envoyé** — le service applique alors son comportement par défaut [2] (notre configuration / code du Studio) ; pour l'instruction, cela signifie « pas d'instruction » (dans l'API officielle, `instruction` vaut `None` par défaut) [5] (code).

| Champ | Valeurs | Effet sur le prompt |
|---|---|---|
| **texte à dire** | texte EN/ZH | contenu + événements vocaux |
| **voix et manière de parler** (instruction) | texte ; **vide par défaut** | **sans échantillon** = description de la voix (Design) ; **avec échantillon** = direction (Direction). **Vide + échantillon = clone pur** [4][5]. Vide sans échantillon = mode simple (`tts_plain`, le modèle choisit la voix) [5] |
| **échantillon de voix** (facultatif) | fichier | avec la transcription ou pas du tout — sinon erreur [5] |
| **transcription de l'échantillon** | texte | mot pour mot, y compris les répétitions de l'enregistrement [4] (officiel) |
| **force de l'instruction (CFG)** (avancé) | 0,5–4, 1,0 par défaut | à quel point le modèle s'en tient à l'instruction ; voir plus bas |
| **seed** | vide = aléatoire | variantes ; même seed + champs identiques = répétition [9] |

- **L'instruction par défaut est vide :** échantillon + transcription sans instruction = **clone pur** (CFG 1,0) — c'est ce que recommande le fabricant [8] (officiel). Tout texte saisi dans l'instruction transforme le clone en direction.
- **CFG :** le README recommande **4** pour Design et Direction (« renforce l'adhésion à l'instruction ») [4] (officiel) — le Studio permet jusqu'à 4. Documentation du service hébergé : pour concevoir une voix, commence entre 2 et 4, passages expressifs 1–3, narration continue 1–2 [10][11] (officiel, version hébergée). À CFG 1,0, le modèle ne calcule pas la branche sans instruction, donc la description agit plus faiblement [5] (code). **CFG ≠ 1 sans instruction = erreur du service** (le modèle sans instruction n'a pas de branche négative) [5] (code) — pour un clone pur, laisse 1,0.

## Format du prompt
- **Langue : anglais** (texte en anglais → instruction en anglais). « Fais correspondre la langue de l'instruction à celle du texte » ; les instructions ne sont pas traduites [4][10] (officiel). En chinois — instruction en chinois.
- Le prompt pour le participant a 2 ou 3 parties : **instruction** (champ « voix et manière de parler »), **texte**, éventuellement **échantillon + transcription**.
- **Instruction en mode Design (description de la voix) :** concise, « télégraphique » ou en phrases complètes. Les descriptions du benchmark du fabricant font **110 à 250 caractères** : genre et âge, accent, rôle/persona, débit (tempo, hauteur, texture), émotion/style [15] (officiel). Le service hébergé accepte jusqu'à 500 caractères de description ; « plus de détails ne garantit pas une meilleure voix » [11] (officiel). Composantes (au choix) [11] :
  1. rôle et situation (qui parle, où),
  2. voix de base — âge, genre, hauteur, accent, en mots simples,
  3. **une ou deux** caractéristiques audibles de texture (gravelly, breathy, velvety, light rasp),
  4. tempo et articulation habituels,
  5. centre de gravité émotionnel — pas l'émotion de chaque phrase.
  Exemples de style tirés des documents du fabricant : « A warm, thoughtful young woman with a clear voice and a calm, reflective delivery. » [4] ; « Mature nomadic storyteller. Weathered, resonant speaking voice with rhythmic pacing » [7] (officiel).
- **Instruction en mode Direction (avec échantillon) :** **2 ou 3 décisions** parmi ces dimensions : situation, intention (rassure, avertit, dissimule), émotion avec son intensité (« restrained panic »), rythme et accents (tempo, pauses, respiration), état physique décrit par le son [10] (officiel, hébergé). Exemple du README : « Speak slowly with a restrained, serious tone. » [4]. N'y change pas l'identité (âge, genre, accent) — c'est le rôle de l'échantillon/de la conception [10].
- **Matrice du médium « Voix » → Breeze :** situation d'enregistrement, qui, texture, caractère, rapport à ce qui est dit, manière de parler — tout peut s'exprimer en anglais [21]. L'expérience de l'auteur (descriptions d'environ 1000 caractères) vient d'ElevenLabs [20] ; pour Breeze, vise environ 150 à 500 caractères (benchmark/limite hébergée) — une description plus longue n'est pas confirmée.
- **Événements dans le texte :** anglais — parenthèses rondes, à l'endroit du son : `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)` [4] (officiel) ; chinois — crochets `[笑]`, `[叹气]`, `[咳嗽]`, `[清嗓子]` [4]. Ne mélange pas les syntaxes dans une même requête [12]. La liste plus longue de la documentation hébergée (`(gasps)`, `(whispers)`, `(sobs)`, `(pause)`…, là sous la forme `(sighs)`, `(laughs)`) concerne le modèle multilingual — **non confirmée dans notre modèle** ; risque que le marqueur soit lu à voix haute [12][16].
- **Crochets dans un texte anglais** — ne les utilise pas (le modèle ajoute un préfixe interne de locuteur `[S0]` ; effet de tes propres `[...]` inconnu) [5] (code ; non confirmé). Le format « [Voice: …] » vu dans une critique n'est pas documenté par le fabricant [17] (communauté, douteux).
- **Poids, négatif, JSON** — n'existent pas. Nombres et abréviations : la documentation ne dit rien — écris-les en toutes lettres (non confirmé, par prudence).
- **Longueur du texte :** limite de génération d'environ **120 s de parole**, moins en pratique (budget de contexte, surtout avec un long échantillon) — garde une marge [9] (officiel). Découpe les passages plus longs aux limites de paragraphes/phrases ; le fabricant conseille de garder ensemble les fragments cohérents, sans hacher en phrases isolées [9].

## Squelette du prompt
Conception de voix (sans échantillon) :
```
instruction (EN) : [rôle/situation]. [genre], [âge], [accent ou « neutral accent »]. [1–2 traits de texture], [hauteur/registre]. [tempo et articulation habituels] ; [centre émotionnel].
texte (EN) : [phrase], [pause par virgule/points de suspension]… {(sigh)} [phrase].
CFG : 4 (recommandation du README ; plus léger : 2–3)
```
Direction (avec échantillon) :
```
échantillon : [parole propre d'une seule personne, sans musique] + transcription : [mot pour mot]
instruction (EN) : [intention/situation] + [émotion avec intensité] + [rythme/respiration/état physique]{; at the word '[mot]', [changement]}.
texte (EN) : [...]
CFG : 4 (recommandation du README ; plus délicat : 1,5–3)
```
Clone pur : échantillon + transcription, **instruction vide**, CFG 1,0.

## Ce qui marche
- **La description d'un rôle plutôt qu'une liste d'adjectifs** — le benchmark du fabricant évalue le « Role Fit » : à quel point la voix incarne de façon convaincante tout le rôle décrit [15] (officiel).
- **Changement au cours d'une réplique :** indique le mot déclencheur : « At the word 'Wait', suddenly shift to terrified, breathless alarm » [7] (officiel). Évaluation du fabricant : ce qui compte, c'est l'état initial, l'endroit du changement et l'état final [16].
- **L'état physique par des symptômes audibles :** « heavily out of breath and gasping », tremblement, fatigue, bégaiement — le benchmark exige des marqueurs concrets, pas une émotion générale [7][16] (officiel).
- **Une nuance d'émotion précise** (« restrained », « conflicted », « resentful ») — évaluée séparément de l'émotion générale [16] (officiel).
- **Un accent anglais avec son degré** (« a gentle Southern lilt », « Japanese-accented English ») [7][16] (officiel).
- **Une série de répliques avec une même voix :** conçois la voix → enregistre le résultat → utilise-le comme échantillon (avec transcription exacte) dans toutes les suivantes ; mêmes paramètres ; assemble avec 0,2 à 0,3 s de silence et égalise le volume [9][14] (officiel). Le fabricant normalise les échantillons à −18 LUFS et utilise un extrait de 30 s maximum se terminant sur une phrase complète [9][14] (officiel, version hébergée).
- **Échantillon :** propre, une seule personne, sans fond sonore ni boucles, 3 s minimum ; testeur : 6 s ont donné un timbre stable [4][14][17]. Durée optimale pour le modèle local — non établie.
- **Plusieurs seeds** — pour des défauts rares, un seul essai ne suffit pas [8] (communauté).

## Biais et pièges
- **Texte dans une autre langue que EN/ZH** (polonais, français…) → le modèle ne le gère pas ; n'essaie pas « du français avec une instruction en anglais » [1][4].
- **N'importe quelle instruction avec un clone** (même « Speak clearly and naturally. ») transforme le clone en direction et peut modifier le débit de l'échantillon [1][8].
- **Contradiction entre échantillon et instruction** (par ex. échantillon féminin, « deep male voice ») : c'est déjà une Direction en conflit — le fabricant a attribué de tels mauvais résultats à une entrée incohérente [8] (officiel).
- **Transcription inexacte** (par ex. l'échantillon répète une phrase, mais pas la transcription) : abîme le résultat [8] (officiel).
- **Clone interlangue** (échantillon dans une autre langue que le texte EN/ZH) — « collapse » du résultat signalé [8] (communauté) ; garde un échantillon en anglais pour un texte en anglais.
- **Chaîne Breeze → OmniVoice (voix à partir d'une description, puis une autre langue) :** OmniVoice transfère l'accent de l'échantillon sur l'autre langue, donc un échantillon anglais donnera du polonais (ou du français) avec un accent anglais [18] (officiel OmniVoice) ; le test de cette chaîne dans le Studio n'a pas encore été fait [19] (notre configuration).
- **Sifflantes et bande passante :** le testeur a entendu des « s/t » durs et un manque d'« air » (24 kHz), un volume d'environ −18 LUFS — à corriger au montage [17] (communauté).

## Au-delà du photoréalisme
- **Les voix non humaines et stylisées peuvent se décrire** — le benchmark du fabricant contient notamment « Non-human, mechanical-spectral. Low engine thrum, metallic distorted whisper. », « Booming resonant, massive mechanical scale. », des créatures, des personnages d'animation et de bande dessinée [7][15] (officiel). C'est la voie principale vers une parole « non photoréaliste » avec ce modèle.
- **Conventions de diction :** narrateur archaïque, conteur au rythme marqué, récitation, rythme hypnotique (« hypnotic and persuasive rhythm »), théâtralité [7] (officiel).
- **Chuchotement, cri, essoufflement, pleurs** — en instruction Direction (catégories : acoustic attributes, physiological state) [16] (officiel).
- **Texture du support (bande, radio, téléphone, réverbération)** — non documentée ; ne la promets pas. Si la bible le demande : le prompt décrit la voix, et la texture va dans l'espace SFX/au montage [7][16].
- Chant : non documenté pour le modèle ouvert (`(singing)` seulement dans la liste hébergée) [12] — non confirmé.

## Mouvement / temps / son
- Durée = longueur du texte × tempo indiqué dans l'instruction (« slowly », « brisk pace ») ; le Studio n'a pas de champ de durée ni de tempo [1][4].
- Pauses : ponctuation et instruction (« emotional pauses », « measured pauses ») [10][11] (officiel) ; marqueur `(pause)` non confirmé dans ce modèle [12]. Silences précis — au montage.
- Max. environ 120 s par génération, moins en réalité [9]. Résultat : WAV 24 kHz mono [2][4].
- Dialogue : une réplique (une voix) par requête, assemblage au montage [13] (officiel, hébergé).

## À vérifier avant l'envoi
- [ ] Texte en anglais (ou en chinois), instruction dans la même langue ; pas de mots dans d'autres langues, ou bien une graphie phonétique.
- [ ] Mode clair : Design (instruction = description de la voix) / Direction (échantillon + direction) / clone pur (instruction vide, CFG 1,0).
- [ ] Description : rôle + voix de base + 1 ou 2 traits de texture + tempo + centre émotionnel, environ 150 à 500 caractères, sans contradiction.
- [ ] Direction : 2 ou 3 décisions, sans changer l'identité ; changement en cours de réplique via « at the word '…' ».
- [ ] Événements uniquement `(laugh)`, `(sigh)`, `(cough)`, `(clears throat)` ; aucun `[...]` dans un texte anglais.
- [ ] Échantillon avec transcription exacte (les deux champs ou aucun) ; CFG 4 pour description/direction (recommandation du README), 1,0 avec une instruction vide.
- [ ] Texte en dessous d'environ 1 à 1,5 min de parole ; plusieurs seeds.

## Sources
[1] Studio : `modele/mowa/breeze-tts-2.yaml` — notre configuration
[2] Studio : `studio/backends/http.py` (les champs vides ne sont pas envoyés), `studio/workflow.py` (seed, valeurs des champs) — notre configuration
[3] Tests et API Breeze — notes internes (non publiées) — notre configuration
[4] breezeblue-ai/breeze-tts README (commit 58ec70c, version sur le Spark) — https://github.com/breezeblue-ai/breeze-tts — officiel
[5] breeze-tts, code des modèles de prompt et de l'API — https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/templates.py , https://github.com/breezeblue-ai/breeze-tts/blob/58ec70c/breeze_infer/api.py — officiel (code)
[6] Hugging Face — BreezeBlue/Breeze-TTS-2 — https://huggingface.co/BreezeBlue/Breeze-TTS-2 — officiel
[7] BreezeBlue — Introducing Breeze TTS 2 (exemples Design/Direction) — https://breezeblue.ai/breeze-tts-2 — officiel
[8] Issue #14 — défauts selon les seeds ; réponse du fabricant : clone pur sans instruction et CFG 1, conflit échantillon/instruction — https://github.com/breezeblue-ai/breeze-tts/issues/14 — communauté / officiel (réponse du fabricant)
[9] Issue #25 — textes longs (~120 s), cohérence de la voix, assemblage des fragments — https://github.com/breezeblue-ai/breeze-tts/issues/25 — officiel (réponse du fabricant)
[10] BreezeBlue Docs — Voice instruction prompting — https://docs.breezeblue.ai/guides/voice-instruction-prompting — officiel (service hébergé)
[11] BreezeBlue Docs — Voice Design prompting — https://docs.breezeblue.ai/guides/voice-design-prompting — officiel (service hébergé)
[12] BreezeBlue Docs — Audio tags — https://docs.breezeblue.ai/guides/audio-tags — officiel (service hébergé, modèle multilingual)
[13] BreezeBlue Docs — Text to Speech (modèles breeze-tts-2 vs multilingual, dialogues) — https://docs.breezeblue.ai/guides/text-to-speech — officiel (service hébergé)
[14] BreezeBlue Docs — Voice clone (échantillon : min. 3 s, extrait jusqu'à 30 s, −18 LUFS) — https://docs.breezeblue.ai/guides/voice-clone — officiel (service hébergé)
[15] TTS Voice Design Benchmark (ensemble de 1000 descriptions) — https://huggingface.co/datasets/BreezeBlue/TTS-Voice-Design-Benchmark , https://github.com/breezeblue-ai/tts-voice-design-benchmark — officiel
[16] TTS Voice Direction Benchmark (catégories : émotion, accent, état physique, variation, événements) — https://github.com/breezeblue-ai/TTS-Voice-Direction-Benchmark — officiel
[17] CrePal — Breeze TTS 2 Review for AI Video Voiceovers — https://crepal.ai/blog/?p=9183 — communauté (critique isolée)
[18] k2-fsa/OmniVoice README (accent lors d'un clone interlangue) — https://github.com/k2-fsa/OmniVoice — officiel
[19] Plan : test de la chaîne Breeze → clone OmniVoice — notes internes (non publiées) — notre configuration
[20] Channelers, voix « Ludzie » (ElevenLabs v3) — notes internes (non publiées), `ludzie_matryca.md` — expérience de l'auteur (autre modèle)
[21] Gabarit du médium « Voix » — `prompty/media/mowa.md` — notre configuration
