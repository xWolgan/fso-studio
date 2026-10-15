<!-- Fiche modèle pour le promptmaker. modele: woosh, woosh-wideo -->
# Woosh (Sony AI, poids publics 03.2026) — effet à partir d'une description et son pour une vidéo

## Ce que c'est et à quoi ça sert
- Modèle de fondation d'**effets sonores** de Sony AI : **texte → effet** (Woosh-Flow / DFlow distillé) et **vidéo → son synchronisé** avec description optionnelle (VFlow / DVFlow distillé) [5][6] (officiel).
- Sortie : **mono, 48 kHz** (l'autoencodeur ne fonctionne qu'en mono) [5] (officiel), WAV 24 bits ; avec une vidéo, aussi un MP4 avec le son remplacé [2][3] (notre configuration).
- Version publique entraînée sur **Freesound (descriptions originales), AudioCaps (légendes humaines), WavCaps (légendes faiblement étiquetées)** ; vidéo→son sur VGGSound (légendes de Qwen3-Omni ou étiquettes de classe originales) [5] (officiel). La meilleure version « privée » (bibliothèques Pro Sound Effects / BOOM) **n'est pas disponible** — le Studio a la version publique [3][8] (notre configuration / officiel).
- Points forts : événements courts et uniques (véhicules, moteurs, applaudissements, impacts), son collé au mouvement dans l'image. Dans le test des auteurs vidéo→son (FoleyBench), meilleure qualité/adéquation que MMAudio, mais **moins bonne synchronisation** (DeSync 0,575 contre 0,400) [5] (officiel).
- **Ce qu'il ne fait PAS bien :**
  - **la stéréo, le mouvement dans le panoramique** — mono uniquement [5] ;
  - **les ambiances longues** — entraînement sur des fragments de **5 s** (texte→effet) [5] ; le Studio permet 1–10 s, >5 s = expérimental [1] (notre configuration). Paysages sonores longs → Stable Audio 3 ;
  - **les boucles** — les « boucles parfaites » ne sont encore que dans les projets de Sony [8] (officiel) ;
  - **le timing précis, le morphing** — également en projet [8] (officiel) ;
  - **la musique et la parole** — c'est un modèle de SFX ; musique et parole : autres modèles du Studio [3] (notre configuration) ;
  - les modèles distillés (mode « rapide ») font moins bien que les complets sur la plupart des métriques [5] (officiel).
  - Sur les effets de la BBC (mesure de Stability), Woosh-Flow est moins bon que SA3 small-SFX [11] (officiel, source concurrente).

## Ce que le participant règle dans le Studio
**woosh (effet à partir d'une description)** [1][2] (notre configuration)
| Champ | Valeurs | Effet |
|---|---|---|
| **prompt** | texte (obligatoire) | description de l'événement |
| **durée (s)** | 1–10, pas de 0,5, 5 par défaut | entraînement env. 5 s ; plus long = expérimental |
| **mode** | rapide (DFlow, 4 étapes) / qualité (Flow, solveur ODE) | rapide ~0,4 s, qualité ~12 s [3] |
| **force de la description (CFG)** | 1–10, 4,5 par défaut (avancé) | plus haut = plus fidèle à la description |
| **seed** | nombre | variantes |

**woosh-wideo (son pour une vidéo)** [1][2] (notre configuration)
| Champ | Valeurs | Effet |
|---|---|---|
| **clip vidéo** | obligatoire | le modèle voit **8 s à partir du « début de fenêtre »** ; le résultat est coupé à la durée du clip |
| **description (optionnelle)** | texte, peut être vide | suggère *ce qui* doit sonner ; le *quand* découle de l'image |
| **début de fenêtre (s)** | 0–60, pas de 0,5 | clip > 8 s → fenêtres suivantes en générations séparées |
| **mode** | rapide (DVFlow) / qualité (VFlow) | ~3 s / ~8 s [3] |
| **force de la description (CFG)** | 1–10, 3 par défaut (avancé) | poids de la description par rapport à l'image |
| **seed** | nombre | variantes |

- **Pas de champ négatif** — l'API Woosh dans le Studio n'en accepte pas [1][2] (notre configuration). N'ajoute pas « no music », etc. au prompt (l'encodeur CLAP comprend mal les négations — non confirmé pour Woosh, par prudence).
- **Volume** : parfois très faible (des pas sur du gravier à env. −60 dB RMS) ; le Studio ne normalise pas, il empêche seulement la saturation [2][3] (notre configuration).
- Licence des poids **CC-BY-NC** (non commerciale) [6] (officiel).

## Format du prompt
- **Langue : anglais — indispensable.** L'encodeur de texte est **RoBERTa-Large de Woosh-CLAP** [5] (officiel), un modèle de langue anglais ; légendes d'entraînement en anglais.
- **Limite stricte : 77 tokens** (`max_sentence_tokens: 77`, l'excédent est coupé) [4] (officiel, configuration des poids) → en pratique **jusqu'à env. 40–50 mots** ; l'essentiel au début. Recommandé : **8–25 mots**.
- **Style : une phrase qui décrit l'événement sonore comme une légende AudioCaps/Freesound** : [source] + [action] (+ contexte). Exemples officiels : « Emergency vehicle driving with siren on », « An engine humming and brakes squealing », « Starting a motorcycle », « A crowd applauds » [7] (officiel). AudioCaps, ce sont des légendes humaines de clips AudioSet [12] (officiel, jeu de données).
- **Le texte n'est pas prétraité** (`text_preprocessing: no_op`) [4] — la ponctuation et la casse arrivent telles quelles au modèle ; écris une phrase normale.
- **Pas** de tags, de préfixes (`TrackType`, c'est Stable Audio — ici ça ne marche pas), de poids, de JSON, de `Length:` — la durée se règle dans le champ [1][2] (notre configuration) ; rien de tel n'apparaît dans la documentation de Woosh [5][6][7].
- **Vidéo + texte** : les légendes V2A de l'entraînement sont des phrases naturelles de Qwen3-Omni qui décrivent la scène et le son, ou de courtes étiquettes de classe VGGSound [5] (officiel). Exemples officiels de descriptions pour vidéo : « A propeller plane flies over a snowy landscape, its engine roaring. », « A large audience in a formal hall gives a standing ovation with applause. » [7] — **description de la source visible + le son qu'elle produit**.

## Squelette de prompt
Effet à partir d'une description (woosh) :
```
[sujet/source avec sa matière] [verbe d'action, avec intensité/rythme], [deuxième événement : "followed by…" / "while…"], [espace : in a large empty hall / outdoors / indoors], [distance : close / in the distance]
```
Son pour une vidéo (woosh-wideo) :
```
[source visible] [action visible dans le cadre], [quel son elle produit : matière, caractère], [fond acoustique : vent / réverbération de la pièce — optionnel]
```
ou en version minimale (étiquette à la VGGSound) : `[source] [action]` — p. ex. la structure « dog barking ».

## Ce qui marche
- **Du concret : source + action** plutôt que des adjectifs — tous les exemples des auteurs sont ainsi [7] (officiel) ; guide du Studio : 8–15 mots [13] (notre configuration).
- **Action + texture + acoustique** en une seule expression, p. ex. la structure « fast metallic whoosh in a concrete stairwell » [10] (communauté).
- **Deux événements** reliés par « and » / « followed by » (exemple officiel « An engine humming and brakes squealing » [7]) ; plus de 2–3 brouille le résultat (non confirmé).
- **Durées courtes** : 1–5 s ; les sons plus longs se font en plusieurs générations qu'on raccorde (déduit de [5]).
- **Mode rapide pour chercher, qualité pour la version finale** — les modèles distillés sont moins bons [5] (officiel) ; la pratique « scout DVFlow → finalize VFlow » [10] (communauté).
- **CFG** : modéré pour les textures naturelles, plus haut pour les sons stylisés / strictement fidèles à la description [10] (communauté). La distillation a été entraînée pour un CFG de 1 à 9 ; les auteurs ont évalué DFlow à CFG 7 [5] (officiel). Valeurs par défaut 4,5 (texte) et 3 (vidéo) dans le Studio — garde-les, sauf si le résultat ignore la description (alors 5–7).
- **Seed** : plusieurs variantes — les bons résultats tiennent du hasard [3] (notre configuration).

## Biais et pièges
- **Coupure après 77 tokens** — une description longue et poétique perd sa fin sans avertissement [4] (officiel).
- **La poésie et l'ambiance ne marchent pas** — « les descriptions longues et poétiques aident moins qu'une source et une action concrètes » [13] (notre configuration) ; l'encodeur CLAP a été entraîné sur des descriptions d'événements acoustiques [5].
- **Prompt dans une autre langue que l'anglais** (p. ex. la langue du participant) — RoBERTa-Large est un modèle anglais [5] ; le résultat sera aléatoire (non confirmé par un test, mais découle de l'architecture).
- **Résultat très faible** — ce n'est pas une erreur de prompt [3] (notre configuration).
- **Vidéo : la synchronisation porte sur ce qu'on voit** ; les sons hors champ (ambiance, événements lointains), le modèle peut les omettre — mieux vaut les générer à part (woosh ou Stable Audio 3) et les mixer (déduction, non confirmé).
- **Vidéo : texte contraire à l'image** — le modèle est conditionné par l'image *et* la description [7] ; une description totalement incohérente (p. ex. des oiseaux sur un plan avec un moteur) donnera un résultat incertain ; un contrepoint voulu se fait mieux par une génération texte→effet séparée (non confirmé).
- **Vidéo sans description** : ça marche (Studio : description vide = son à partir de l'image seule) [3], mais les modèles VFlow/DVFlow utilisés sont conditionnés par l'image **et** la légende ; les auteurs ont des variantes « OV » vidéo seule, que le Studio n'utilise pas [7] (officiel). Conclusion : avec une image ambiguë (dessin, abstraction, vidéo générée), **mieux vaut donner une description**.
- **Fenêtre de 8 s** : un clip plus long = plusieurs générations avec des « débuts de fenêtre » différents ; raccord et fondu enchaîné au montage [1][3] (notre configuration) ; la communauté découpe les clips de la même façon [14] (communauté).

## Au-delà du photoréalisme
- Woosh est un modèle de **foley/SFX réaliste** issu des données Freesound/AudioCaps/WavCaps [5] ; le vocabulaire de traitement (bande, saturation, filtre, glitch) **n'est pas documenté** pour Woosh — on peut essayer des tags typiques de Freesound (« lo-fi », « distorted », « reversed », « glitch »), efficacité non confirmée.
- Sons traités / stylisés (bande, granulaire, « 8-bit », tape stop) — **plutôt Stable Audio 3** (il les a dans ses exemples officiels) ; utilise Woosh pour la matière brute que le participant traitera au montage.
- **Vidéo non réaliste** (dessin, animation, collage) : le modèle voit le mouvement, mais peut mal identifier la source → une description textuelle qui nomme la source et la matière du son (pas le style de l'image — « drawing », « animation » ne disent rien du son) (déduction, non confirmé).
- Pas de stéréo → l'espace et le mouvement dans le panoramique s'ajoutent au montage [5].

## Mouvement / temps / son
- **Texte→effet** : durée réglée par le champ (1–10 s, idéalement ≤5 s) [1][5]. Décris le déroulé avec des verbes simples : « starts… », « …then stops », « passes by », « approaches » (style des légendes AudioCaps ; efficacité non confirmée). Sans stéréo — « left to right » ne marchera pas [5].
- **Vidéo→son** : le temps et le rythme des événements viennent du mouvement dans l'image (features Synchformer, 24 i/s) [2] (notre configuration) ; **dans la description, ne donne pas de temps** (« at 2 seconds ») — ce pilotage n'existe pas (non confirmé, absent de la documentation). Description = *quoi* et *comment* ; image = *quand*.
- Description pour vidéo : nomme la source **visible** et sa matière (« boots on wet snow », pas « steps »), éventuellement le fond acoustique du lieu.

## Vérifie avant d'envoyer
- [ ] Anglais ; une seule phrase ; 8–25 mots (strictement < 77 tokens)
- [ ] Source + action au début ; matière/texture ; espace et distance (optionnel)
- [ ] Pas d'ambiance, de métaphores, de tags, de poids, de `TrackType`, de `Length:`
- [ ] Pas de négations (« no music ») — Woosh n'a pas de négatif
- [ ] Texte→effet : durée ≤5 s (plus long seulement en connaissance de cause) ; ambiance longue/stéréo → propose Stable Audio 3
- [ ] Vidéo : description conforme à ce qu'on voit ; clip > 8 s → fenêtres suivantes (« début de fenêtre ») ; sans indiquer de temps
- [ ] Rappel : résultat mono, souvent faible — niveau à régler au montage ; plusieurs seeds ; licence non commerciale

## Sources
[1] Studio — `modele/sfx/woosh.yaml` et `woosh-wideo.yaml` — notre configuration
[2] Service Woosh sur le Spark — notes internes (non publiées) — notre configuration
[3] notes internes (non publiées) (section SFX) — notre configuration
[4] Configuration des poids Woosh — `~/sfx/Woosh/checkpoints/TextConditionerA/config.yaml` et `Woosh-CLAP/config.yaml` sur le Spark (roberta-large, max_sentence_tokens: 77, text_preprocessing: no_op) ; fichiers de la release https://github.com/SonyResearch/Woosh/releases — officiel
[5] Woosh: A Sound Effects Foundation Model — rapport technique (arXiv 2604.01929) — https://arxiv.org/html/2604.01929 — officiel
[6] GitHub — SonyResearch/Woosh (README, licences) — https://github.com/SonyResearch/Woosh — officiel
[7] Woosh — page du projet avec exemples — https://sonyresearch.github.io/Woosh/ — officiel
[8] Sony AI — Introducing Woosh — https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model — officiel
[9] GamesBeat — entretien avec l'équipe Woosh — https://gamesbeat.com/sony-ai-releases-woosh-foundation-model-for-sound-effect-generation-exclusive-interview/ — officiel (propos des auteurs)
[10] RunComfy — Woosh Sound Effect Generation in ComfyUI — https://www.runcomfy.com/comfyui-workflows/woosh-sound-effect-generation-in-comfyui-text2audio-videosync — communauté
[11] Stable Audio 3 — article technique, comparaison avec Woosh-Flow — https://arxiv.org/html/2605.17991v1 — officiel (Stability)
[12] AudioCaps: Generating Captions for Audios in The Wild (NAACL 2019) — https://aclanthology.org/N19-1011/ — officiel (jeu de données)
[13] Studio — guide `poradniki/woosh.md` — notre configuration
[14] Civitai — workflow Woosh vidéo→son (découpage en segments de 8 s) — https://civitai.com/models/2627712 — communauté
