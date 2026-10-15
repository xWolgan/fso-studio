<!-- Fiche modèle pour le promptmaker. modele: minimax-h3, minimax-h3-fl2va, minimax-h3-referencje, minimax-h3-klatki, fasth3-v2 -->
# MiniMax H3 (+ FastH3 V2) — vidéo avec son stéréo

## Ce que c'est et à quoi ça sert
- Modèle ouvert « omni » : image + **son stéréo 32 kHz** (dialogue, chant, effets, musique) en une seule passe, 24 i/s, 4–15 s [3][5] (officiel).
- Deux checkpoints : **FL2VA** (0, 1 ou 2 images : texte → vidéo, première / dernière / les deux images) et **Ref2VA** (références : ≤ 9 images, ≤ 3 vidéos de 2–15 s chacune (au total ≤ 15 s), ≤ 3 sons de 2–15 s chacun (au total ≤ 15 s), en tout ≤ 12 fichiers) [3] (officiel).
- Encodeur de texte : **Qwen3-VL-32B** (couche 50). Il voit aussi les images et (à 2 i/s) les images des vidéos de référence ; **il NE voit PAS les sons de référence** — ils vont uniquement au générateur [3][12] (officiel / code).
- H3 a été entraîné sur des descriptions très détaillées dans un format fixe (« Context-IR »). Dans le cloud, MiniMax réécrit le prompt à la place de l'utilisateur ; **dans les poids ouverts, cela n'existe pas — c'est toi qui fais cette réécriture** et tu écris directement au format IR [3] (officiel), [18] (communauté).
- Points forts : le multiplan avec des coupes à des moments donnés, le mouvement de caméra, le son synchronisé avec l'action, la combinaison de plusieurs références dans une seule scène, la transition fluide première→dernière image [1][3] (officiel), [26][31] (communauté).
- **Ce qu'il ne fait PAS bien :**
  - les visages en plan large (déformés ; plans moyens et rapprochés OK) [26] (communauté) ;
  - le silence et les pauses — dans les moments « vides », il peut marmonner / baragouiner [17][23] (communauté) ;
  - un fond sonore fort sous le dialogue (l'ambiance baisse quand quelqu'un parle ; surtout en Ref2VA) [24] (communauté) ;
  - une voix hors champ fiable (la bouche du personnage bouge souvent quand même) [27] (communauté) ;
  - séparer les accents de deux locuteurs (l'accent « déteint » sur l'autre personnage) [30] (communauté) ;
  - le clignement des yeux (les personnages ne clignent presque pas) [22] (communauté) ;
  - une animation 2D fluide (elle sort « en deux », à 12 i/s) [16] (communauté) ;
  - un texte fiable dans le cadre (fragile ; mieux vaut l'ajouter au montage) [31] (communauté).

## Ce que le participant règle dans le Studio
Une seule entrée « MiniMax H3 » — la variante se choisit d'elle-même selon les fichiers fournis [L1] (notre configuration) :
- **rien** → texte → vidéo (T2VA, checkpoint FL2VA) ;
- **première image** → I2VA ; **dernière** → L2VA ; **les deux** → FL2VA ;
- **n'importe quelle inspiration** (jusqu'à 9 images, 3 vidéos, 3 sons) → **Ref2VA** ; dans ce cas, **la première/dernière image sont ignorées** [L1].
Entrées séparées « MiniMax H3 · images clés » et « FastH3 V2 » — voir plus bas.

Champs communs [L1][L2] :
- **prompt** — un seul champ, envoyé **sans aucun traitement** au nœud ComfyUI (le Studio n'ajoute rien). **La ligne d'alignement avec l'image n'est pas dans le workflow — tu dois l'écrire toi-même** (voir Format) [11][L2] (code / notre configuration).
- **Pas de prompt négatif.** Les poids sont « CFG-distilled », le workflow utilise `BasicGuider` (sans branche négative) [3][6][L2] (officiel).
- **format (proportions)** 16:9 (par défaut), 21:9, 4:3, 1:1, 3:4, 9:16 [L1].
- **résolution** 480p (0,4 MP, 16:9 = 864×480, par défaut) / 720p (0,9 MP, 1280×736) [L1][13]. Nativement, côté court de 768 px [3]. En 480p, le modèle tient généralement mieux la structure du prompt (plans, caméra, disposition) qu'en 768p [20] (communauté), mais les visages dans les plans plus larges sont moins bons [26] (communauté). 720p FL2VA/I2VA : rarement, un « assombrissement du cadre comme un diaphragme » qui dépend de la seed [28] (communauté) — change de seed.
- **durée** 1–15 s (10 par défaut), pas de 0,5 s ; le nombre d'images est calé sur la grille 17n+5 à 24 i/s (5 s → 124 images) [L1][L2]. Officiellement 4–15 s [3] ; plage d'entraînement env. 124–362 images (≈5–15 s), plus court « non testé » [11] (code). **Règle-la sur ≥ 5 s.**
- **mode** : rapide = LoRA turbo (FL2VA 8 étapes, Ref2VA et images clés 4 étapes) / qualité = 20 étapes [L1][L2]. Turbo : « son et mouvement un peu moins bons » [7] (officiel).
- **seed** — pour comparer des versions de prompt, garde la seed fixe et change une seule chose [31] (communauté).

Ref2VA (inspirations) — détails tirés du code [11][L1][L2] :
- Marqueurs dans l'ordre des fichiers, numérotation séparée par type : `<Picture 1..9>`, `<Video 1..3>`, `<Audio 1..3>`. Le Studio affiche le marqueur à côté de chaque fichier.
- **Le son d'un fichier vidéo n'est pas utilisé** (le Studio ne transmet que l'image de la vidéo) → `<Audio n>`, ce sont uniquement les fichiers audio. N'écris pas « le son de `<Video 1>` ».
- Une vidéo de référence plus longue que le clip est coupée à la durée du clip ; les images de référence sont réduites à la résolution de génération (le petit texte / les petits détails des références se perdent en 480p).

Images clés (`minimax-h3-klatki`) [L1][L2][8][13] :
- Checkpoint Ref2VA + 1–3 images épinglées aux secondes `czas1..3` (elles doivent tenir dans la durée). Référence optionnelle = `<Picture 1>`.
- **L'encodeur de texte ne voit pas les images clés** — elles n'ont pas de marqueur. N'écris pas `<Picture 2>` pour une image clé ; décris avec des mots ce qui doit être visible à cette seconde-là, et places-y une coupe ou un temps fort de l'action [8] (officiel).

## Format du prompt
- **Langue : anglais** pour toute la description ; **dans la langue d'origine, mot pour mot, seulement les répliques/textes chantés (dans `<d>`) et les textes visibles dans le cadre** [1][2] (officiel) ; un employé de MiniMax : « à part le contenu à générer et les dialogues, tout en anglais » [15]. Une description en chinois ou dans une autre langue (p. ex. la langue du participant) est parfois lue à voix haute comme une réplique [15] (communauté).
- **Longueur : long et détaillé.** Les exemples officiels font 150–1000 mots ; en Ref2VA, `detailed_description` fait généralement **350–500 mots** [2][3] (officiel). Les prompts courts sans références sont une cause typique de mauvais résultat [18][31] (communauté). Dans ComfyUI, il n'y a pratiquement pas de limite de caractères [12] (code). Heuristique (non confirmé) : 1 plan ~120–200 mots, 2–4 plans ~250–450.
- **Pas de poids** `(word:1.3)` — le tokenizer de H3 a les poids désactivés, les parenthèses deviendront du texte [12] (code). **Pas de JSON, pas de listes de tags.** Des phrases complètes, au présent.
- **Ne nomme pas ce qui ne doit pas être là** (à CFG 1, le mot « text » dans « no text » ajoute du texte). Écris en positif : « the sign above the door is blank » [6] (officiel). Attention : les templates officiels de Comfy contiennent eux-mêmes « no subtitles… » [13] — tiens-toi malgré tout au principe positif.

**Modes FL2VA (sans inspiration)** — 1re ligne = instruction, puis une ligne vide, puis 3 champs séparés par des lignes vides, dans cet ordre [1] (officiel) :
- T2VA (sans images) : pas de ligne d'instruction.
- I2VA (première image seulement), mot pour mot :
  `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.` (de même dans les prompts de la communauté [14])
- FL2VA (les deux), mot pour mot (sans chevrons — c'est ainsi dans l'original) ; `S.SS` = durée du clip avec 2 décimales, `N` = numéro du dernier plan :
  `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA (dernière image seulement — dans le nœud, c'est alors `<Picture 1>` [11]) :
  `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
- Champs : `integrated_multimodal_description:` (image, action, plans, locuteurs, dialogue, chant, son diégétique le long de l'axe du temps) · `overall_soundscape:` (1–4 phrases : ambiance, bruits de l'action, respirations, rires ; sans dialogues ; `N/A` seulement en cas de silence total) · `non_diegetic_music:` (1–3 phrases : instruments, tempo, rythme, dynamique — sans mots d'ambiance ; `N/A` s'il n'y en a pas) [1].

**Ref2VA (inspirations)** — six sections dans cet ordre, tout en anglais [2] (officiel) :
`subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`.
- `<Subject N>` = contenu extrait de la référence (personne, lieu, accessoire, style, mouvement) ; `<Picture N>` à part seulement quand l'image est une image précise / un ancrage de cadre ou un storyboard ; `<Video N>` seulement pour une relation à la vidéo entière (montage, continuation, structure de caméra/montage) ; `<Audio N>` = signal copié ou référence [2].
- `summary` : un paragraphe d'une phrase avec un préfixe de type entre crochets : `[reference generation]`, `[keyframe completion]`, `[video editing]`, `[video continuation]`, `[audio reuse]`, `[audio reference]`, reliés par ` + ` [2].
- `retention_analysis` : une ligne par étiquette ; image/vidéo : `fully_preserved` / `partially_preserved` / `attribute_transfer` / `weak_reference` ; son : `fully_copy` / `partially_copy` / `reference` / `weak_reference`. Pas de `(Sx)` dans cette section [2].
- `detailed_description` : 1–2 phrases de style AVANT `[Shot 1]`, puis les plans ; place les étiquettes à leur première apparition et là où elles agissent (« the shot begins from <Picture 1> ») [2].
- Le format n'a pas besoin d'être copié mot pour mot — ce qui compte, c'est la cohérence des étiquettes et des relations claires [25] (communauté, réponse sur HF). Comfy : « Ref2VA est très sensible à la formulation ; des marqueurs précis et une attribution explicite de quelle référence pilote quoi » [13] (officiel).

**Marqueurs communs** [1][2] (officiel) :
- Plans : `[Shot 1]` sans temps ; ensuite `[Shot 2] At 00:03.500, the camera cuts to …` — temps croissants et < durée du clip. Coupes : « the camera cuts to / the shot cuts to / transitions to / changes to / switches to » ; fondu enchaîné / fondu au noir seulement si voulu.
- Locuteurs : ID fixe `(S1)`, `(S2)` dans tous les plans ; ensemble `(S1,S2)` ; un personnage qui ne parle pas — sans ID. À la première apparition, décris la voix (âge, sexe, timbre, rythme, accent) EN DEHORS de `<d>`.
- Dialogue/chant : `<d>[Language] mots exacts.</d>` — à l'intérieur, seulement le tag de langue et les mots. Termine la réplique par un point/?/! avant `</d>` [2] ; l'absence de point favorise le marmonnement après la réplique [17] (communauté).
- Voix hors champ : exactement `says in an off-screen voiceover:` + après `</d>` « while his/her lips remain completely closed » [1].
- Réplique à travers une coupe : `<scenetrans>` aux deux endroits + « continues seamlessly across the cut » [1]. Marqueur de coupure : le guide écrit `<cutoff>`, alors que le tokenizer a `<|cutoff|>` [1][12] — pas clair ; **ne l'utilise pas**.
- Texte dans le cadre : entre guillemets anglais, mot pour mot, dans la langue d'origine : `a hand-painted sign reading "…"` [1].

## Squelette de prompt
T2VA / I2VA / FL2VA / L2VA (n'insère la ligne d'instruction que s'il y a des images) :
```
[ligne d'instruction — mot pour mot selon le mode]

integrated_multimodal_description: [Shot 1] [style/medium], [valeur de plan et composition d'ouverture], [sujet : apparence, vêtements, position dans le cadre], [lieu, lumière, texture, accessoires clés]. [mouvement de caméra : type + amplitude + vitesse, sous forme de phrase]. [action : début → développement → résultat], [son diégétique lié à l'action]. [description de la voix] (S1) says: <d>[Language] [réplique].</d> [ce qu'il fait après la réplique, bouche fermée]. [Shot 2] At 00:0[s].[ms], the camera cuts to [nouvelle information : lieu/état/point de vue/moment], [mouvement de caméra], [action], [son].

overall_soundscape: [ambiance continue], [bruits de l'action dans l'ordre], [sons non verbaux].

non_diegetic_music: [instruments], [tempo], [rythme], [évolution de la dynamique] | N/A
```
Ref2VA (inspirations) :
```
subject_definitions:
<Subject 1> is [qui/quoi] in <Picture 1>, [traits à conserver].
<Subject 2> is [lieu/style/mouvement] from <Picture 2> / <Video 1>, [traits].
<Audio 1> is the voice-timbre reference for <Subject 1> (S1). | <Audio 1> is [ambiance/musique/réplique] [rôle].

summary:
[type de tâche + type de tâche] [1 paragraphe : ce qui se passe, quelles étiquettes servent à quoi].

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): [marqueur] - [ce qui est conservé].
<Audio 1>: [marqueur] - [ce qui est copié / à quoi sert la référence].

detailed_description:
The target video is in [style/medium, palette, lumière, texture].
[Shot 1] [comme en T2VA, avec les étiquettes à leur première apparition] … <Subject 1> (S1) says: <d>[Language] [réplique].</d> …
[Shot 2] At 00:0[s].[ms], the shot cuts to …

overall_soundscape:
[…]

non_diegetic_music:
[…] | N/A
```
Images clés : squelette Ref2VA ; s'il y a une référence — `<Subject 1> is [qui] in <Picture 1>` ; summary `[keyframe completion]` (+ `reference generation`, s'il y a une référence) ; dans `detailed_description`, les coupes ou moments clés exactement aux secondes `czas1..3` (« At 00:05.000 … the composition shows [description de l'image clé en mots] »). Sans référence : omets `subject_definitions` et `retention_analysis`, ou garde-les avec une description en mots (non confirmé — pas d'exemple dans les sources).

## Ce qui marche
- **D'abord toute la scène, ensuite les plans** ; style et composition d'ouverture au début de `[Shot 1]` [1][6] (officiel).
- **Chaque coupe = une information nouvelle** (lieu, état, point de vue, moment) ; si seul le cadre change — un mouvement de caméra plutôt qu'une coupe [1] (officiel).
- **La caméra comme action, pas comme objectif** : « keep him in frame » ne marche pas ; « the camera pulls out with large amplitude, matching his walking speed » marche [31] (communauté). Un seul mouvement de caméra dominant et une seule action principale par plan — surtout en haute résolution [20][31] (communauté).
- **I2VA : ancrage → début de l'action → développement → résultat** ; conserve l'identité, les vêtements, les couleurs, la disposition de l'image [1]. **FL2VA : un seul plan continu**, décris le chemin entre les états, pas deux images statiques ; la dernière image est atteinte vers la fin [1] (officiel). Un élément qui doit bouger malgré des images semblables (feuilles, eau) : nomme-le comme le seul élément animé et décris son trajet et son retour [21] (communauté).
- **La dernière image du clip précédent comme première** = continuation du plan [L1].
- **Décris le son à chaque instant** — y compris le « silence » comme une ambiance discrète (ronronnement d'un frigo, vent) ; le mot « silently » pour les actions sans parole ; après une réplique, « closes her lips » [17][23] (communauté). Parole non voulue dans un plan calme → remplis explicitement les deux champs de son et régénère [6] (officiel).
- `non_diegetic_music: N/A` coupe efficacement la musique (elle fuit parfois quand même, ~20 %) [31] (communauté).
- **L'accent par le tag de langue** : `<d>[French] English words</d>` a donné un accent français là où la description « with a French accent » ne marchait pas [19] (communauté).
- **Clignements, petits gestes** — écris-les explicitement avec un temps (« she blinks slowly at 00:02 ») [22] (communauté).
- **Références** : donne un rôle à chacune (identité / style / mouvement / caméra / voix) — « les attributions explicites marchent beaucoup mieux » [7] (officiel). Quand les références portent l'apparence, concentre la description sur la nouvelle action [31] (communauté).
- **Voix de référence** : un enregistrement court (~4 s) et explicitement « `<Audio 1>` is the voice-timbre reference for `<Subject 1>` (S1) » — un enregistrement plus long favorisait le baragouin au début [17] (communauté, source unique).
- **Une réplique attribuée à la mauvaise personne** → génère-la avec un outil de voix et fournis-la comme `<Audio n>` de ce locuteur ; avec plusieurs locuteurs, rattache les répliques à des événements visibles, pas à un timecode [6] (officiel).

## Biais et pièges
- **Pas de ligne d'instruction avec des images** — le Studio ne l'ajoute pas (l'ancien guide du Studio affirme le contraire — à tort) [11][L2].
- **Mauvais format de dialogue** : correct `<d>[Polish] …</d>` (ou `[French]`, etc.), pas `<d>Polish: …</d>` [1][2] (officiel).
- **Baragouin / « interjection » dans les ~0,5 premières s**, surtout en Ref2VA ; dépend de la seed ; remplacer `<d>` par des guillemets a aidé certaines personnes, pas d'autres [17] (communauté). Génère plusieurs seeds.
- **Une réplique trop longue pour trop peu de temps**, ou **trop de temps libre** après une réplique courte → précipitation, répétitions, remplissage [31][35] (communauté). Pas de norme officielle en mots/s — ajuste la durée du clip à la réplique, laisse de l'air.
- **Narrateur nommé comme un personnage dans le cadre** (« the man ») → le modèle fait bouger la bouche de ce personnage. Mieux : « Female narrator voice, saying: … » ou une description de voix à part, sans référence à une personne visible [27] (communauté). Toujours peu fiable.
- **Fuite d'accent/de voix** entre deux locuteurs [30] (communauté) → différencie fortement les voix (sexe, âge, timbre), et fournis les voix critiques comme `<Audio n>`.
- **Ambiance couverte par le dialogue** [24] (communauté) → ajoute le fond important au montage, ou fais un plan sans dialogue.
- **Biais « pub TV »/brillant** avec des prompts courts et généraux (avis isolé) [18] (communauté) → nomme toujours le medium et la texture au début.
- **Visages en plan large** [26] ; **rougeurs/joues rouges qui s'accentuent en Ref2VA** [29] (communauté) → plans moyens/rapprochés pour les visages.
- **Un personnage ne parle pas, mais a un ID** → de la parole apparaîtra ; ID seulement pour ceux qui émettent une voix [1].
- **Langues mélangées** (noms propres dans la langue du participant dans la description, description de l'action dans une autre langue que l'anglais) → baragouin ou lecture de la description à voix haute [15][35] (communauté). Les mots dans une autre langue que l'anglais seulement dans `<d>` et entre les guillemets d'un texte à l'écran.

## Au-delà du photoréalisme
- **Le mot de style tout au début de `[Shot 1]`** (Ref2VA : la phrase de style avant `[Shot 1]`). Liste officielle : `Cinematic`, `live-action`, `2D-animated`, `3D CG`, `claymation`, `watercolor`, `vintage film` [1][2] (officiel).
- **Le levier le plus puissant : l'image.** En I2VA/FL2VA, le style est « dérivé de l'image de référence » [1] (officiel) → fais une image dans la technique visée (dessin, collage, aquarelle) avec un autre modèle du Studio et fournis-la comme première image ou comme `<Picture n>` avec un rôle de style (`weak_reference` / `attribute_transfer`) [2].
- **Dessin/animation à la main** — vocabulaire du skill officiel de MiniMax : crayon, chalk, colored pencil, pastel, rough brush ; lines slightly jittering, uneven smudging, frayed edges, a redrawn-every-frame feel ; « flat hand-drawn animation » dans un espace live-action [4] (officiel). Aquarelle/BD (exemple d'API) : « keep the watercolour texture, visible ink outlines, off-register paper grain » [34] (communauté). L'animation 2D sortira de toute façon généralement à 12 i/s (« en deux ») [16] — pour un caractère fait main, c'est un atout.
- **Papier / stop-motion** [4] (officiel) : visible paper fibers, folds, seams, cut edges, visible thickness ; frame-by-frame, hand-manipulated motion: small stepped movements, tiny pauses, slight rebounds, pieces sliding and settling ; physical shadows ; layered paper diorama. Au lieu de « no smooth CG », écris en positif sur le mouvement saccadé.
- **Collage** [4] (officiel) : flat bold color fields, black-and-white halftone photographic cut-outs, colored cardstock accents, torn edges, soft paper shadows ; pieces pop in, slide into place, press flat, pause, lock. Son : paper rustle, scissors, tape peel, page flip [4].
- **Pellicule / film / archive** : `vintage film` (officiel [1]) ; d'après des exemples d'API (sans confirmation en local) : « 35 mm film look with fine grain, soft highlight halation », « 1990s film grain, scanlines, chromatic aberration, light leaks », « VHS tracking artifacts » [13][33] (communauté/fournisseur).
- **BD/encre** : « bold comic-book ink style, heavy linework, limited palette » — template Comfy Ref2VA [13] (officiel Comfy).
- **Mélange** : live-action + éléments dessinés marche avec une description du type « hand-drawn luminous animation in a live-action space », avec un contact net entre le dessin et une vraie main/un vrai objet [4][33].
- **Abstraction, pure texture, peinture de matière** — pas de sources ; on ne sait pas comment le modèle réagit (non confirmé). Plus sûr de passer par une image/une référence dans cette technique.
- `embedding:minimaxh3_…` (styles de la communauté) — fichiers non confirmés dans notre installation ; **ne les utilise pas** [6].

## Mouvement / temps / son
- **Caméra = type + amplitude + vitesse**, comme une phrase naturelle dans le plan, pas des étiquettes à la fin [1] (officiel). Types : Zoom In/Out (focale), Push In/Pull Out (travelling), Pan Left/Right, Truck Left/Right, Tilt Up/Down, Pedestal Up/Down, Arc Shot, Tracking Shot, Static Shot, Shake Slightly/Strongly, POV, Roll Clockwise/Counterclockwise. Amplitude : `with small amplitude` / `with large amplitude` ; vitesse : `at slow speed` / `at fast speed` ; omets les valeurs moyennes [1]. « Dolly in/out » n'est pas dans le vocabulaire [1] — utilise push in / pull out.
- **Temps** : coupes `At MM:SS.mmm` ; le premier plan sans temps ; tous les temps < durée du clip [1]. Des timecodes trop serrés sont une erreur fréquente [31] (communauté) ; le seuil « pas plus dense que toutes les ~2–3 s » — non confirmé. FL2VA — de préférence 1 plan [1].
- **Durée** : ≥ 5 s (plage d'entraînement ~5–15 s) [3][11]. Dialogue : un seul locuteur et une seule réplique par clip quand la qualité de la parole compte [35] (communauté) ; « 1–2 répliques courtes pour 5–8 s » — heuristique, non confirmé.
- **Son — où écrire quoi** [1] (officiel) : dialogue, chant, musique entendue dans la scène (radio, quelqu'un qui joue) et effets liés à une action précise → dans le plan, au moment de l'événement ; fond et bruits de tout le clip → `overall_soundscape` ; musique uniquement pour le spectateur → `non_diegetic_music` (instruments, tempo, rythme, dynamique ; pas de « triste/joyeuse »).
- **Dialogue dans la langue du participant** : 11 langues sont prises en charge de façon stable (ar, zh, en, fr, de, it, ja, ko, pt, ru, es) ; « les autres langues à des degrés divers » [3] (officiel) — le français en fait partie, le polonais par exemple non. Notation : `<d>[French] …</d>`, `<d>[Polish] …</d>`, etc. (par analogie avec `[English]`/`[Chinese]` [1][2] ; les tags des langues hors exemples officiels, p. ex. `[Polish]`, ne sont pas confirmés par un test). Pour une langue hors de la liste : court, simple, sans sigles ni noms propres rares [35]. Plan B : enregistrer/générer la réplique avec un outil de voix du Studio et la fournir comme `<Audio n>` (Ref2VA) avec `fully_copy`/`partially_copy`, en écrivant exactement ces mots dans `<d>` [2][6] (officiel) — ou poser la voix au montage.
- **Textes à l'écran dans la langue du participant** : entre guillemets, mot pour mot [1] ; le rendu du texte est fragile, les caractères accentués/diacritiques ne sont pas confirmés → textes plutôt au montage [31].
- **Chant** : les paroles d'une chanson aussi dans `<d>[Language] …</d>` [6] (officiel).

## FastH3 V2 (`fasth3-v2`) — différences
- Distillation DMD2 par FastVideo ; même encodeur, même VAE et **même format de prompt** (T2VA/I2VA/FL2VA/L2VA) [9][10] (officiel).
- Champs uniquement : première/dernière image, format, résolution, durée, seed ; **pas de mode et pas d'inspirations** — Ref2VA n'a pas été distillé [9][L1].
- Carte HF : seul T2VA a été distillé, « FL2VA n'a pas été distillé » [10] ; Comfy montre l'I2V avec images comme fonctionnel [9] → avec des images, attends-toi à une fidélité moindre (non confirmé chez nous).
- Moins bon sur les mouvements difficiles, les petits détails et une partie du son [9][10][32]. Prompts : mouvement plus simple, un seul événement principal, moins de coupes. Sur le Spark, généralement plus lent que H3 en mode rapide [L3] — pour comparer.

## Vérifie avant d'envoyer
1. Mode selon les fichiers : rien / première / dernière / les deux / inspirations / images clés → la bonne ligne d'instruction ou le format à 6 sections.
2. Ligne d'instruction mot pour mot, puis une ligne vide ; `S.SS` = durée du clip, `N` = numéro du dernier plan.
3. Tout en anglais ; dans une autre langue seulement dans `<d>[Language] …</d>` et entre les guillemets d'un texte à l'écran.
4. Style/medium au début de `[Shot 1]` (Ref2VA : avant `[Shot 1]`).
5. `[Shot 1]` sans temps ; les suivants `At MM:SS.mmm` croissants et < durée ; coupe = information nouvelle.
6. Chaque locuteur a un `(Sx)` fixe et une description de voix ; les répliques finissent par un point ; après la réplique, bouche fermée / « silently ».
7. Les deux champs de son remplis (`N/A` en connaissance de cause) ; pas de dialogues dans `overall_soundscape`.
8. Zéro négation du type « no … », zéro poids et JSON.
9. Marqueurs de référence conformes à la numérotation des fichiers dans le Studio ; chacun a un rôle ; pas de `<Picture n>` pour les images clés ; pas de « son de `<Video n>` ».
10. Durée ≥ 5 s et adaptée à la quantité de dialogue ; pas de visages en plan large.

## Sources
[1] MiniMax — Video Prompt Writing Guide (T2VA/I2VA/FL2VA/L2VA) — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md — officiel
[2] MiniMax — Full-Reference Mode (Ref2VA) Guide — https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md — officiel
[3] MiniMax H3 — carte du modèle (README) — https://huggingface.co/MiniMaxAI/MiniMax-H3 — officiel
[4] MiniMax H3 — skills (h3-prompt-writing, handdrawn-live-video-generator, papercraft-stop-motion-explainer, paper-collage-explainer-generator) — https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills — officiel
[5] MiniMax — blog « MiniMax H3 » — https://www.minimax.io/blog/minimax-h3 — officiel
[6] ComfyUI — MiniMax H3 Prompt Guide — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide — officiel (Comfy)
[7] ComfyUI — MiniMax H3 native workflows — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native — officiel (Comfy)
[8] ComfyUI — MiniMax H3 multiframe — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-multiframe — officiel (Comfy)
[9] ComfyUI — FastVideo FastH3 — https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo — officiel (Comfy)
[10] FastVideo — FastH3-8-Step-V2 (carte HF) — https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2 — officiel
[11] ComfyUI — code des nœuds H3 (nodes_minimax_h3.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py — officiel (code)
[12] ComfyUI — code de l'encodeur H3 (text_encoders/minimax.py) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py — officiel (code)
[13] Comfy-Org — templates de workflow H3 (t2v, r2v, multiframe_reference) — https://github.com/Comfy-Org/workflow_templates/tree/main/templates — officiel (Comfy)
[14] HF #47 « The actual correct system prompt for IT2V » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/47 — communauté
[15] HF #32 prompts en chinois (réponse d'un membre de l'org. MiniMaxAI + utilisateurs) — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/32 — officiel/communauté
[16] HF #74 « Anime style videos have half the FPS » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/74 — communauté
[17] HF #76 « Weird gibberish / clipped voice at the very start » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/76 — communauté
[18] HF #83 « Very bad prompt adherence » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/83 — communauté
[19] HF #84 « Getting different Accents » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/84 — communauté
[20] HF #65 « Prompt adherence varies depending on the resolution » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/65 — communauté
[21] HF #81 « Question about prompting on static elements » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/81 — communauté
[22] HF #96 clignement des yeux — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/96 — communauté
[23] HF #106 baragouin des personnages — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/106 — communauté
[24] HF #82 « Ref2VA environmental audio feels too quiet » — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/82 — communauté
[25] HF #71 questions sur le guide Ref2VA — https://huggingface.co/MiniMaxAI/MiniMax-H3/discussions/71 — communauté
[26] Comfy-Org HF #30 « Why MiniMax H3 Ruins Faces on Wide Shots? » — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/30 — communauté
[27] Comfy-Org HF #44 « problem with off-screen voiceover » — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/44 — communauté
[28] Comfy-Org HF #67 « FL2VA / I2VA: mid-clip blackout » — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/67 — communauté
[29] Comfy-Org HF #55 « Ref2VA: red/blush patches » — https://huggingface.co/Comfy-Org/MiniMax-H3/discussions/55 — communauté
[30] ComfyUI issue #15454 « voice/accent conditioning can leak between subjects » — https://github.com/Comfy-Org/ComfyUI/issues/15454 — communauté
[31] Aireiter — « MiniMax H3 Prompt Review: What Works, What Breaks » — https://aireiter.com/blog/minimax-h3-prompt-review — communauté
[32] Kombitz — « FastH3 V2: 8-Step MiniMax H3 in ComfyUI » — https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/ — communauté
[33] fal.ai — « MiniMax H3 Prompting Guide + 44 Video Examples » (API) — https://fal.ai/learn/devs/minimax-h3-prompting-guide — communauté/fournisseur
[34] Atlas Cloud — « I Studied 45 Official Prompts » (API) — https://www.atlascloud.ai/blog/tips/minimax-h3-prompt-guide — communauté
[35] Seedance.tv — « MiniMax H3 Gibberish Fix » — https://www.seedance.tv/blog/minimax-h3-gibberish-fix — communauté
[L1] Studio : gui/modele/wideo/minimax-h3*.yaml, fasth3-v2.yaml — notre configuration
[L2] Studio : gui/workflows/wideo/h3_wideo, h3_referencje_lista, h3_klatki-kluczowe, fasth3_wideo (.api.json) — notre configuration
[L3] notes internes (non publiées) (mesures sur le Spark) — notre configuration
