<!-- Fiche modèle pour le promptmaker. modele: minimax-music-3 -->
# MiniMax Music 3 (MiniMax, poids ouverts 08.2026)

## Ce que c'est et à quoi ça sert
- Modèle autorégressif hiérarchique : un **Global LLM 8B** (initialisé à partir de Qwen3-8B) planifie la structure longue du morceau, un **Local LLM 0,6B** ajoute le détail acoustique, puis flow matching + Flow-VAE. Conditionné par le **texte de la chanson** et une **description détaillée de la musique** ; morceaux **jusqu'à 5 min**, forme cohérente (intro, couplet, refrain, bridge, pause instrumentale, outro) [4] (officiel).
- La description est lue **dans le temps** — le modèle suit le développement du morceau, pas seulement le style global [4][6] (officiel). « Plus c'est concret, plus c'est proche » [6] (officiel).
- Dans le Studio : modèle principal pour les **morceaux instrumentaux** (priorité des ateliers) ; 30 s ≈ 93 s de calcul (mode rapide) [3] (notre configuration).
- **Ce qu'il ne fait PAS bien :**
  - tempo, tonalité, instrumentation et construction **ne sont pas garantis** — « des indications, pas des ordres stricts » [4] (officiel) ;
  - la couche instrumentale est parfois **plate**, même quand la description cite des instruments précis ; les parties denses et aiguës et les couches de voix « se fondent » ; il rend mal l'énergie d'un genre (p. ex. le rock de stade) [12] (communauté) ;
  - rock/metal et sons acoustiques plus anciens — avis partagés, mix « boueux » dans les arrangements denses ; loué surtout en pop et en électronique [13] (communauté) ;
  - **langues hors démos (dont le polonais) — pas de données** : les démos officielles sont uniquement en anglais, mandarin, cantonais et français [7] (officiel) ; un praticien : les autres langues sont « moins prévisibles » [11] (communauté).

## Ce que le participant règle dans le Studio
| Champ | Valeurs | Où ça va / effet sur le prompt |
|---|---|---|
| **description** | texte | `caption` — toute la description de la musique [1][2] (notre configuration) |
| **paroles / structure** | texte ; par défaut `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` (chacune sur sa ligne, lignes vides entre elles) | `lyrics` — balises de section + paroles éventuelles [1] |
| **durée max. (s)** | 10–300, pas de 10, par défaut 60 | `max_duration` — **limite haute** ; le modèle peut finir plus tôt [1][8] |
| **mode** | rapide (encodeur INT8, ~1,5 min / 30 s) / qualité (bf16, ~2,5 min / 30 s) | seulement qualité/temps, le prompt ne change pas [1][3] |
| **seed** | nombre | une autre version du même prompt [1][6] |

- **Pas de champs BPM / tonalité** — tu écris le tempo et la tonalité **dans la description** [1] (notre configuration), [4] (officiel).
- Fixes : CFG 1,7 (la constante du modèle dans ComfyUI est 1,5), top_k 50 ; diffusion 30 pas, euler ; décodage par tuiles activé [2] (notre configuration), [9] (code ComfyUI).
- **Il n'y a pas de negative prompt** (conditionnement mis à zéro) [2] (notre configuration). Écris les exclusions dans la description comme un fait (« no drums », « no vocals »).
- Sortie du Studio : MP3 V0 [2] ; le modèle produit nativement du 32 kHz stéréo [4] (officiel).

## Format du prompt
- **Description en anglais.** Le « music-caption-rewriter » officiel écrit la description en anglais, « sauf si l'utilisateur veut explicitement une autre langue » [5] (officiel) ; toute la bibliothèque de 1000 descriptions de référence est en anglais [5] (officiel).
- **Structure : trois en-têtes dans cet ordre** — `Global Metadata`, `Vocal Details`, `Arrangement` [4][5] (officiel). Indication du Studio : la description commence par « Global Metadata: » [1] (notre configuration). Le template officiel ComfyUI écrit l'en-tête avec deux-points et le contenu dans le même paragraphe, paragraphes séparés par une ligne vide [10] (officiel) ; la bibliothèque MiniMax — en-tête sur sa propre ligne et sous-champs [5] (officiel). Les deux variantes sont correctes.
- **Sous-champs de la bibliothèque officielle** (les plus proches des données d'entraînement) [5][6] (officiel / communauté) :
  - Global Metadata → `Basic Attributes:` (exactement sous la forme « bpm is 76. key is Bb, and scale is major. Genre / Sous-genre. »), `Global Emotional Progression:`, `Application Scenarios & Imagery:`, `Sonics & Production Profile:` ;
  - Vocal Details → `Vocal Gender & Timbre:`, `Vocal Style:`, `Harmony/Backing Vocals:`, `Vocal FX:` ;
  - Arrangement → `Instrument Lifecycle Description (Primary/Secondary Layering):` avec « Primary: … » et « Secondary: … », `Groove & Foundation Progression:`, `Embellishments, Textures & Spatial FX:`.
- **Longueur de la description : env. 250–450 mots** (valeur par défaut du rewriter) [5] (officiel). Limite de tout le prompt : 5000 tokens [4][9] (officiel).
- **Le Markdown ne sert à rien** : ComfyUI supprime les en-têtes `#`, les puces `-`/`*`, le gras, et fusionne les lignes vides [9] (code ComfyUI). Écris en phrases ordinaires.
- **Paroles / structure** — liste officielle des balises : `[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]` [4][8] (officiel).
  - **Chaque balise sur sa propre ligne** ; un texte sur la même ligne que la balise peut disparaître [6] (communauté).
  - La casse n'a pas d'importance — ComfyUI convertit de toute façon les balises en minuscules [9] (code ComfyUI).
  - **Seules les balises sont des instructions de construction** ; les paroles ne portent que le contenu et l'émotion. « La batterie entre » écrit dans les paroles ne changera rien à la batterie — ça va dans Arrangement [8][10] (officiel), [11] (communauté).
  - Répète les sections avec des balises simples (`[Verse]` … `[Verse]`), comme dans le template officiel [10] ; la numérotation `[Verse 1]` est un conseil de la communauté [11], efficacité non confirmée.
- Poids, JSON, négatif — absents de la documentation ; ne les utilise pas. Le champ de description prend en charge les « dynamic prompts » de ComfyUI [8] — évite les accolades `{a|b}` (non confirmé qu'elles fonctionnent via l'API du Studio).

## Squelette du prompt
Description (en anglais, phrases ordinaires, ~250–450 mots) :
```
Global Metadata
Basic Attributes: bpm is [nombre]. key is [note], and scale is [major/minor]. [Genre] / [Sous-genre ou texture].
Global Emotional Progression: [comment ça s'ouvre] → [où ça monte / point culminant] → [comment ça se résout, ou pas].
Application Scenarios & Imagery: [scène/image à laquelle appartient la musique — tirée de la bible, sans citer le poème].
Sonics & Production Profile: [largeur stéréo, spectre (sombre/brillant), dynamique (compressée/naturelle), espace, support/enregistrement].

Vocal Details
[INSTRUMENTAL : The piece is fully instrumental, no vocals. The lead melodic role is carried by [instrument/texture].]
[CHANSON : Vocal Gender & Timbre: Singer A ([Male/Female]) … Vocal Style: … Harmony/Backing Vocals: … Vocal FX: …]

Arrangement
Instrument Lifecycle Description (Primary/Secondary Layering):
Primary: [instrument-colonne vertébrale, quand il est présent, comment il évolue].
Secondary: [ce qui entre/sort et quand].
Groove & Foundation Progression: [pulsation ou son absence — p. ex. no percussive groove, free time ; comment ça s'épaissit].
Embellishments, Textures & Spatial FX: [textures, bruits, réverbérations, transitions].
[Intro: … / Instrumental sections: … / Solo: … / Outro: … — une phrase pour chaque balise utilisée dans le champ « paroles »]
```
Paroles / structure — instrumental :
```
[Intro]

[Instrumental]

[Solo]

[Instrumental]

[Outro]
```
Paroles — chanson : `[Verse]` + lignes de texte, `[Chorus]` + lignes, … — la balise toujours seule sur sa ligne, ligne vide entre les sections [8][10].

## Ce qui marche
- **La description comme une ligne du temps, pas une liste de matériel** : pour chaque section, écris ce qui entre, sort, change, monte [5][6] (officiel / communauté).
- **Un arc d'énergie raconté comme une histoire** (tension, détente, respiration, apogée) donne une meilleure forme qu'une description statique [6] (communauté).
- **Chaque balise du champ « paroles » a sa phrase dans Arrangement** — le décalage entre balises et arrangement est la cause la plus fréquente d'un morceau qui ne tient pas sa construction [11] (communauté) ; le template officiel ComfyUI décrit « Intro: …, Verses: …, Instrumental sections: …, Bridge: …, Outro: … » [10] (officiel).
- **Application Scenarios & Imagery** — la scène à laquelle appartient la musique ancre l'humeur mieux que des adjectifs [6] (communauté). C'est ici que tu reportes l'image de la bible de l'œuvre (sans le contenu du poème — les paroles ne vont pas dans la description [5]).
- **N'invente pas de précision** : BPM/tonalité exacts seulement quand c'est vraiment nécessaire ; sinon une fourchette ou un mot (« unhurried », « driving ») [5][6] (officiel / communauté).
- **Maintiens exclusions et exigences dans toute la description** (instrumental, sexe de la voix, instrument interdit) — ne les contredis pas dans les sections suivantes [5] (officiel).
- **Fusion de deux styles** : nomme-les tous les deux et écris comment ils se partagent l'arrangement [6] (communauté). Les mots emotional, epic, dark, cinematic sont des **modificateurs, pas des genres** [5] (officiel).
- **Seed** pour les variantes ; seed fixe quand tu compares un changement de description [8] (officiel).

## Biais et pièges
- **La bibliothèque de référence, ce sont des chansons** : sur les 1000 descriptions officielles, pas un seul instrumental ; dominent Mandopop/C-pop, R&B, folk, pop-rock, ballades [5] (officiel ; analyse des index). Le modèle tire vers **la forme chanson et la ballade** — l'instrumental doit être dit explicitement.
- **Voix non spécifiée** = cause la plus fréquente de dérive : remplis toujours Vocal Details — pour un instrumental, écris qu'il n'y a pas de voix et nomme l'instrument principal [5] (officiel), [6] (communauté). Notre pratique : « No vocals. Fully instrumental. » [3] (notre configuration).
- **Structure trop courte = morceau trop court** : la durée max. est un plafond ; le modèle termine quand « le texte est fini ». Un morceau de cinq minutes demande un nombre complet de sections [6][11] (communauté). Combien de secondes remplissent les 5 sections par défaut — inconnu (à vérifier à l'écoute) ; pour des morceaux plus longs, ajoute `[Instrumental]`/`[Solo]`/`[Bridge]` et décris-les dans Arrangement.
- **Instruments nommés ≠ audibles dans le mix** [12] (communauté) : n'entasse pas 8 instruments ; 2–4 avec des rôles Primary/Secondary clairs.
- **Les couches aiguës denses se fondent** [12] — avec beaucoup de couches, sépare-les dans le temps (par sections), pas tout à la fois.
- **Longs morceaux = longue attente** (proportionnellement, ~93 s pour 30 s en mode rapide) [3] (notre configuration) — pour les esquisses, travaille sur 30–60 s.

## Au-delà du photoréalisme (en musique : au-delà de la convention — texture, bande, lo-fi, abstraction)
- **Lo-fi / bande / vinyle** — template officiel ComfyUI : « muddy warm texture, heavy vinyl crackle, tape hiss and wow-flutter pitch wobble, low-passed dusty mix, soft-clipped drums, everything slightly detuned » [10] (officiel). Écris-le dans `Sonics & Production Profile` et dans Embellishments.
- **Musique sans pulsation** — exemples officiels : « There is no percussive groove or rhythmic foundation; the tempo is driven entirely by the rubato phrasing… », « relies entirely on free-time atmospheric progression » [5] (officiel).
- **Dark ambient / drones / textures** — exemples officiels : « low-frequency synthesizer drone… present continuously », « granular textures and wind-like noise sweeps », « continuous layer of ambient noise resembling underwater static or hydrophone recordings », « reverse reverb swells as transitional markers » [5] (officiel).
- **L'espace et le spectre** comme outils de forme : « high frequencies significantly rolled off », « cavernous, aquatic spatial feel », « heavily compressed and saturated, wall-of-sound » [5] (officiel).
- **Effet d'archive** : nomme le support et ses défauts (vinyle, bande, wow & flutter, bande passante étroite) plutôt que « old » [10] (officiel — vocabulaire du template) ; l'efficacité de « radio des années 1930 », etc., n'est pas confirmée.
- Les appareils précis sont rares dans la bibliothèque (prédominance de la pop) — décris une instrumentation expérimentale par son son et sa fonction, pas seulement par son nom (non confirmé).

## Mouvement / temps / son
- **Temps = balises + Arrangement** : les balises définissent les sections, Arrangement dit ce qui s'y passe [4][8] (officiel).
- **Une section peut changer l'arrangement local** (p. ex. `[Solo]`) sans changer le genre de l'ensemble [5][6] (officiel / communauté).
- **Durée** : règle la « durée max. » avec de la marge et ajuste le nombre de sections ; le modèle termine lui-même le morceau par un token de fin [6] (communauté), [8] (officiel).
- **Poème dit sur de la musique** : la bibliothèque contient des exemples de spoken word (« Cinematic Ambient / Spoken Word ») : dans Vocal Details, « a deliberate, theatrical spoken-word delivery rather than singing… slow and measured, with distinct pauses » [5] (officiel). Le texte du poème → champ « paroles », sous des balises `[Verse]`. Récitation dans une langue autre que l'anglais (p. ex. la langue du participant) — non testée.
- **Chanson dans la langue du participant** : les démos officielles ne couvrent que l'anglais, le mandarin, le cantonais et le français [7] ; pour les autres langues, pas de support documenté. Si le participant le veut — un court essai de 30 s, écoute de la prononciation (non confirmé). Nomme la langue du chant dans Vocal Details (p. ex. « sung in French », « sung in Polish ») — non confirmé.

## Vérifie avant d'envoyer
- [ ] Description en anglais, trois parties dans l'ordre Global Metadata → Vocal Details → Arrangement, phrases ordinaires (sans markdown).
- [ ] Tempo et tonalité dans la description (« bpm is …. key is …, and scale is …. ») — ou délibérément par un mot, sans fausse précision.
- [ ] Vocal Details rempli : instrumental → « fully instrumental, no vocals » + instrument principal.
- [ ] Chaque balise sur sa propre ligne, uniquement tirée de la liste officielle de 9 ; pas d'indications musicales dans les paroles.
- [ ] Chaque balise utilisée a sa phrase dans Arrangement ; Arrangement se lit comme une ligne du temps.
- [ ] Le nombre de sections correspond à la « durée max. ».
- [ ] Exigences/exclusions non contradictoires d'une partie à l'autre de la description.
- [ ] Pas de noms d'artistes (template medium), pas de `{|}`, pas le contenu du poème dans la description.

## Sources
[1] Studio — `modele/muzyka/minimax-music-3.yaml` — modele/muzyka/minimax-music-3.yaml — notre configuration
[2] Studio — workflow `workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json` — workflows/muzyka/minimax_music3_tekst-na-muzyke.api.json — notre configuration
[3] Tests et recommandations audio (93 s / 30 s INT8 ; « No vocals. Fully instrumental. ») — notes internes (non publiées) — notre configuration
[4] MiniMax-Music3 — README (architecture, balises, Structured Caption, limites) — https://github.com/MiniMax-AI/MiniMax-Music3 (aussi https://huggingface.co/MiniMaxAI/MiniMax-Music3) — officiel
[5] MiniMax — skill « music-caption-rewriter » (SKILL.md, references/genre-router.md, index et 1000 templates, entre autres dark-ambient-slowcore_0001, contemporary-classical-ambient-ballad_0001, cinematic-ambient-spoken-word_0001) — https://github.com/MiniMax-AI/MiniMax-Music3/tree/main/skills/music-caption-rewriter — officiel
[6] « Prompting MiniMax Music 3 » — Space Hugging Face (multimodalart) — https://huggingface.co/spaces/multimodalart/minimax-music3-prompting-guide — communauté (basé sur le skill officiel)
[7] MiniMax Music 3 — page de démo (langues et genres des démos) — https://minimax-ai.github.io/music3-demo/ — officiel
[8] ComfyUI Docs — MiniMax Music 3 (tutoriel) et nœud MiniMaxMusic3TextEncode — https://docs.comfy.org/tutorials/audio/minimax/minimax-music-3 et https://docs.comfy.org/built-in-nodes/MiniMaxMusic3TextEncode.md — officiel
[9] ComfyUI — code : construction du prompt (`comfy/ldm/minimax_music/prompt.py`) et constantes (`ar.py` : CFG 1.5, top_k 50, 5000 tokens, 9000 trames) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/ldm/minimax_music/prompt.py — officiel (implémentation)
[10] Comfy-Org — template de workflow officiel « audio_minimax_music_3 » (exemple de description lo-fi et notes) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_minimax_music_3.json — officiel
[11] EarnGenix — « MiniMax Music 3 in ComfyUI: Generate a Full 5-Minute Song » — https://www.earngenix.com/workflows/minimax-music-3-comfyui — communauté
[12] MindStudio — « MiniMax Music 3: The Open-Weight AI Music Model, Explained » — https://www.mindstudio.ai/blog/minimax-music-3-open-weight — communauté
[13] AIReiter — « MiniMax Music 3.0 Review: API, Pricing & Local Setup » — https://aireiter.com/blog/minimax-music-3-0-review-api-pricing-local-setup — communauté
