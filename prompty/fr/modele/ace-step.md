<!-- Fiche modèle pour le promptmaker. modele: ace-step-1-5-xl -->
# ACE-Step 1.5 XL sft (ACE Studio × StepFun, 2026)

## Ce que c'est et à quoi ça sert
- Modèle musical à deux « cerveaux » : un **LM planificateur** (dans le Studio Qwen 4B, `qwen_4b_ace15`) transforme la description + les paroles en codes sémantiques (mélodie, arrangement, une partie du timbre), et un **DiT** (ici la variante **XL sft**, 4B, 50 pas, CFG 7) en fait du son [4] (officiel), [2] (notre configuration).
- La variante **sft** selon les auteurs : plus lente que turbo, « meilleure dans le détail et la compréhension de la description », un tout petit peu moins propre [4] (officiel). Studio : 30 s de morceau en environ 20 s — le plus rapide des trois modèles musicaux [3] (notre configuration).
- Sait faire : des chansons à la diction nette, des morceaux instrumentaux, 50+ langues de chant (dont le **polonais** — 3 chansons en polonais figurent dans les exemples officiels ; le français est dans la liste des langues du Studio) [6][7] (officiel). Notre test : diction polonaise **0,97** sur sft (turbo seulement 0,60) [3] (notre configuration).
- **Ce qu'il NE fait PAS bien :**
  - des résultats « comme une machine à sous » — très dépendants du seed et de la durée ; « synthèse vocale grossière sans nuance » ; fidélité au style plus faible dans certains genres [11] (officiel) ;
  - rythme raide, « quadrillé », dynamique plate, peu de contraste couplet/refrain, mélodies prévisibles (test du XL) [12] (communauté) ;
  - **l'ambient à la Eno**, l'électronique des débuts « à la Kraftwerk » — un praticien : « échec », dérive vers de la musique de bibliothèque générique, « kitsch » [13] (communauté) ;
  - exclure des instruments (« sans guitare ») marche mal ; environ la moitié des morceaux peu variés, une partie des générations n'est que du bruit — témoignage d'un seul utilisateur [16] (communauté) ;
  - **mesure fixée à 4/4** dans le Studio (voir plus bas) — valse 3/4, 6/8 indisponibles [2] (notre configuration).

## Ce que le participant règle dans le Studio
| Champ | Valeurs | Où ça va / effet sur le prompt |
|---|---|---|
| **style (tags)** | texte | `tags` = **caption** ; va au LM et à l'encodeur de texte 0,6B **tel quel** [1][8] (notre configuration / code ComfyUI) |
| **paroles** | texte, `[Instrumental]` par défaut | `lyrics` — texte + marqueurs de sections ; « un scénario dans le temps » [1][4] |
| **durée (s)** | 10–240, pas de 5, 60 par défaut | à la fois la longueur du latent et la `duration` pour le LM (le LM génère 5 codes/s) [1][8] |
| **tempo (BPM)** (avancé) | 40–200, **100** par défaut | `bpm` — **toujours envoyé** [1][2] |
| **tonalité** (avancé) | texte, **« E minor »** par défaut | `keyscale` — **toujours envoyé** [1][2] |
| **langue du chant** (avancé) | en, pl, de, fr, es, it, ja, zh ; **en** par défaut | `language` — ne va qu'à l'encodeur du texte de la chanson [1][8] |
| **seed** | nombre | commun au LM et au DiT [2] |

- Constantes du workflow : mesure `4` (= 4/4), LM : cfg 2.0, temperature 0.85, top_p 0.9 ; DiT : 50 pas, CFG 7, euler/simple, shift 3 — comme le modèle officiel ComfyUI [2][9] (notre configuration / officiel).
- **Il n'y a pas de prompt négatif** (la branche négative du DiT est un conditionnement mis à zéro) [2] (notre configuration).
- Dans ComfyUI, le LM **ne réécrit pas la description** (seul le Gradio officiel le fait) : BPM, tonalité, mesure et durée entrent comme métadonnées toutes prêtes dans le bloc `<think>`, la description et les paroles passent 1:1 [8] (code ComfyUI). Ce que tu écris, c'est ce que le modèle reçoit.
- **Conséquence :** BPM 100 et E minor partiront toujours, même si le participant n'y touche pas. Le promptmaker **indique toujours** un BPM et une tonalité cohérents avec la description — une contradiction (« slow ballad » + 160 BPM) déroute le modèle [4] (officiel).

## Format du prompt
- **Description (caption) en anglais.** Les 200 exemples officiels ont tous une description en anglais — y compris les chansons en polonais/chinois/coréen ; la langue du chant se nomme en toutes lettres dans la description, par ex. « A clear female vocal delivers a melancholic melody in Polish » [7] (officiel).
- **Forme :** le modèle accepte des mots-clés, des tags séparés par des virgules ou de la prose — « le format n'a pas d'influence notable » [4] (officiel). Les exemples officiels sont **un paragraphe de prose de 22 à 112 mots (médiane ~31)** décrivant le déroulement [7] (officiel). L'étiquette « tags » du Studio n'impose pas de tags — la prose convient.
- **Dimensions de la description** (tableau officiel) : genre, émotion/atmosphère, instruments, texture du timbre (warm, crisp, muddy, airy, punchy, raw), époque, style de production (lo-fi, live recording, bedroom), voix, rythme, indications de construction (building intro, fade-out ending) [4] (officiel).
- **N'écris PAS le BPM, la tonalité, la mesure dans la description** — il y a des champs séparés pour ça [4] (officiel).
- **Tonalité — format des exemples :** `C major`, `E minor`, `F# minor`, `Bb major` (lettre + major/minor) [7] (officiel). Les plus stables : C, G, D, Am, Em ; les rares sont parfois ignorées [4] (officiel).
- **BPM :** 60–180 marche bien ; les extrêmes sont instables. À titre indicatif : lent 60–80, moyen 90–120, rapide 130–180 [4] (officiel). Le modèle traite le BPM comme une ancre (on obtiendra par ex. 118 au lieu de 120) [4].
- **Paroles (lyrics)** — syntaxe [4][5][7] (officiel) :
  - marqueur de section entre crochets, **seul sur sa ligne** : `[Intro]`, `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Bridge]`, `[Outro]` ; dynamiques : `[Build]`, `[Drop]`, `[Breakdown]` ; instrumentaux : `[Instrumental]`, `[Guitar Solo]`, `[Piano Interlude]`, `[Instrumental Break]` ; spéciaux : `[Fade Out]`, `[Silence]` ;
  - **une seule précision après un tiret** : `[Chorus - anthemic]`, `[Bridge - whispered]`, `[Intro - piano]`. Officiellement, une seule est recommandée ; empiler les précisions (exemple du guide : cinq à la fois) = risque que le modèle **chante le contenu du marqueur** [4] ;
  - marqueurs de voix (ligne à part) : `[whispered]`, `[falsetto]`, `[raspy vocal]`, `[spoken word]`, `[harmonies]`, `[ad-lib]` [4] ;
  - **une ligne vide entre les sections** [4][5] ;
  - `(texte entre parenthèses)` = chœur/écho ; **MAJUSCULES** = plus fort, cri [4][5] ;
  - allonger les voyelles (« Feeeling ») — instable, à éviter plutôt [4].
- Poids `(mot:1.2)`, JSON ou négatif — absents de la documentation ; ne les utilise pas.
- **Attention aux versions :** c'est **ACE-Step 1.5** (2026). Les guides pour ACE-Step v1 (3.5B, 2025) ont un autre pipeline — ne mélange pas [10] (officiel).

## Squelette du prompt
Description (champ « style »), en anglais, 1 paragraphe de ~30 à 80 mots :
```
[genre/tradition ou son absence] with [instrument/source principale] and [2–3 instruments au second plan]. [Voix : aucune → "Instrumental, no vocals." / présente → genre, timbre, manière, "in French"]. [Déroulement : comment ça commence → ce qui monte/disparaît → comment ça finit]. [Texture et prise de son : par ex. warm / raw / lo-fi / close-miked / room ambience / tape saturation]. [Ambiance — brièvement, à la fin].
```
Champs séparés : `BPM: [nombre cohérent avec la description]`, `tonalité: [X major/minor]`, `durée: [s]`, `langue: [fr/pl/en…]`.

Paroles — chanson :
```
[Intro - (un instrument de la description)]

[Verse 1]
[ligne de 6 à 10 syllabes]
[ligne de 6 à 10 syllabes]

[Chorus - (un mot de caractère)]
[ligne]
[ligne]

[Outro - fade out]
```
Paroles — morceau instrumental (version avec déroulement) :
```
[Intro - (instrument/texture)]

[Main Theme - (instrument)]

[Breakdown - (ce qui reste)]

[Outro - fade out]
```

## Ce qui marche
- **Du concret plutôt que des adjectifs** : « sad piano ballad with female breathy vocal » > « a sad song » [4] (officiel). Combine plusieurs dimensions (style + émotion + instruments + timbre) [4].
- **Description = « portrait d'ensemble », paroles = « découpage »** — elles doivent raconter la même chose : instruments de la description ↔ marqueurs de solos ; émotion de la description ↔ marqueurs d'énergie [4] (officiel). Exemple de conflit : description « violin solo », dans les paroles `[Guitar Solo - electric]` → résultat moins bon [4].
- **Transforme des styles contradictoires en évolution dans le temps** : « Start with soft strings, middle becomes noisy dynamic rock, end turns to … » plutôt que de tout mélanger à la fois [4] (officiel).
- **Répéter un mot renforce** un élément dans un style mixte [4] (officiel).
- **Quantité de détail = quantité de contrôle** : moins de description → plus de surprises, plus de description → moins de liberté [4] (officiel).
- **Syllabes** : 6 à 10 par ligne ; les lignes correspondantes des couplets à ±1–2 syllabes près — le modèle cale les syllabes sur les temps [4][5] (officiel).
- **Une seule métaphore par chanson**, sans empilement d'adjectifs (« neon skies, electric hearts ») — contre les paroles « à la IA » [4] (officiel). Vaut pour des paroles écrites de zéro ; le poème du participant reste mot pour mot.
- **Des marqueurs de construction, même sans paroles,** donnent une carte de l'énergie [5] (officiel) — mais pour un instrumental, voir les pièges plus bas.
- **Écris pour le rythme** : phrases courtes, répétitions, mots à l'accent net sont plus stables que de longues phrases ; change d'abord la description, puis une section des paroles à la fois [15] (communauté).
- **Génère plusieurs seeds** et choisis ; quand tu ajustes un paramètre, garde le seed fixe [4][5] (officiel).
- Modèle officiel ComfyUI XL sft : description en prose avec détails de production (« warm and analog-sounding, with subtle tape saturation and a slight room ambience »), marqueurs avec description de l'instrument `[Intro – Rhodes piano and brushed drums]` [9] (officiel).

## Biais et pièges
- **BPM 100 / E minor par défaut** — s'ils ne correspondent pas à la description, le modèle reçoit des signaux contradictoires [1][4]. Règle-les toujours.
- **Mesure 4/4 figée** — ne promets ni valse ni 6/8 ; « waltz » dans la description avec du 4/4, c'est un conflit (déduit de [2][4]).
- **L'instrumental laisse fuir des vocalises :** des marqueurs nus `[Verse]`/`[Chorus]` sans paroles peuvent donner du fredonnement/des vocalises [14] (communauté). Plus sûr : `[Instrumental]` (officiel [4]) ou des marqueurs avec le nom d'un instrument (`[Main Theme - piano]`), et dans la description clairement « instrumental, no vocals » (au début ou à la fin de la description) [14] (communauté).
- Communauté : **des mots qui suggèrent une chanson** (« pop », « ballad », « song ») dans un instrumental tirent vers la voix ; pour un orchestre, ajoute « no choir » [14] (communauté). Même conseil : un champ de paroles vide est parfois plus sûr que des marqueurs — dans le Studio, le champ contient `[Instrumental]` par défaut ; un champ vide passe-t-il — non vérifié.
- Langue du chant dans un instrumental : le Studio n'a pas d'option « instrumental/unknown » ; la langue ne va qu'à l'encodeur du texte [8] — avec `[Instrumental]`, laisse la valeur par défaut (effet non confirmé).
- **Trop de précisions dans un marqueur** → chantées comme du texte [4] (officiel).
- **Tonalités rares, BPM extrêmes, morceaux longs** (>4 min) — moins stables ; 30–60 s et 2–4 min sont les plus stables [4] (officiel). Le Studio s'arrête de toute façon à 240 s.
- **Gacha** : changer un seul mot donne un morceau complètement différent — difficile d'itérer par petites touches [13] (communauté), [11] (officiel).
- **Noms d'artistes** : les auteurs les admettent (« reminiscent of … ») [4], mais le gabarit de médium du Studio demande de décrire ce qu'on leur emprunte — tiens-t'en au gabarit.
- Faible dans certains genres (par ex. le rap chinois) [11] (officiel) ; ambient/expérimental — voir plus haut [13].

## Au-delà du photoréalisme (en musique : au-delà des conventions — texture, bande, lo-fi, abstraction)
- Vocabulaire de production qui fonctionne, tiré des tableaux officiels : **lo-fi, live recording, bedroom pop, studio-polished, high-fidelity** ; timbre : **warm, crisp, muddy, airy, punchy, lush, raw** — « influent sur le mix et le timbre » [4] (officiel).
- **Bande/analogique** : « subtle tape saturation », « analog-sounding », « slight room ambience » — tirés du modèle officiel [9] (officiel).
- **L'époque du son** comme raccourci : « 80s synth-pop », « vintage soul », « 90s grunge » [4] (officiel) — pour un effet d'archive, nomme l'époque et le support.
- **Abstraction / ambient / drones** : peu documentés et peu fiables en pratique [13] (communauté). Si le participant veut de l'abstraction, envisage MiniMax Music 3 ou de courts essais avec plusieurs seeds ; décris des sources sonores concrètes (par ex. « bowed cymbal, sine drones, field recording of wind »), pas « ambient » en général (non confirmé).
- Les instruments inhabituels (« long-tail ») sont mieux compris par un LM plus grand — le Studio a le plus grand, 4B [4] (officiel), [2] (notre configuration).

## Mouvement / temps / son
- **La durée** se règle dans le champ « durée » (le LM reçoit exactement ce nombre de secondes) [8]. Le modèle « peut s'en écarter un peu » [4].
- **Quantité de paroles par rapport à la durée :** les exemples officiels de 124 à 240 s ont typiquement intro, 2 ou 3 couplets, refrains, pont, outro [7] (officiel). Pour 30–60 s, mets un couplet et un refrain, ou seulement le texte d'un poème court (proportion non confirmée — écoute si ça ne galope pas).
- **Le déroulement dans le temps** s'écrit deux fois, de façon cohérente : dans la description, en mots (« builds slowly, ends with a fade-out »), et par des marqueurs dans les paroles (`[Build]`, `[Breakdown]`, `[Outro - fade out]`) [4] (officiel).
- **Poème dit sur de la musique :** marqueur `[spoken word]` (« rap/récitation ») [4] (officiel) ; dans la description « spoken-word delivery over … ». Efficacité pour une récitation dans une autre langue que l'anglais — non vérifiée.
- **Poème chanté dans la langue du participant :** écris le texte mot pour mot, règle la langue (par ex. `fr`, `pl`), dans la description « vocal … in French » (ou la langue concernée) [7] (officiel). Avec l'accord du participant, tu peux couper les longs vers du poème en lignes plus courtes aux pauses naturelles (6 à 10 syllabes) [4] — ne change pas les mots.

## À vérifier avant l'envoi
- [ ] Description en anglais, sans BPM/tonalité/mesure dans le contenu.
- [ ] Champs BPM et tonalité réglés et **cohérents** avec la description (par ex. un morceau lent ≠ les 100 BPM par défaut).
- [ ] Rien n'exige une mesure autre que 4/4.
- [ ] Instrumental : dans la description « instrumental, no vocals » (+ « no choir » pour un orchestre) ; dans les paroles `[Instrumental]` ou des marqueurs avec instrument — pas de `[Verse]`/`[Chorus]` nus.
- [ ] Chanson : chaque marqueur sur sa propre ligne, une précision au maximum, une ligne vide entre les sections ; langue du chant réglée dans le champ et nommée dans la description.
- [ ] Les instruments/l'énergie des marqueurs ne contredisent pas la description.
- [ ] La quantité de paroles correspond à la durée.
- [ ] Pas de noms d'artistes ; pas de poids ni de négatif.
- [ ] Propose 2 ou 3 seeds plutôt que de réécrire le prompt après le premier résultat.

## Sources
[1] Studio — `modele/muzyka/ace-step-1-5-xl.yaml` — modele/muzyka/ace-step-1-5-xl.yaml — notre configuration
[2] Studio — workflow `workflows/muzyka/ace_step_1_5_xl.api.json` — workflows/muzyka/ace_step_1_5_xl.api.json — notre configuration
[3] Tests sur le Spark (diction PL sft 0,97 / turbo 0,60 ; 30 s en ~20 s) — notes internes (non publiées) — notre configuration
[4] ACE-Step 1.5 Ultimate Guide (Tutorial) — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md — officiel
[5] ACE-Step 1.5 — A Musician's Guide — https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md — officiel
[6] ACE-Step 1.5 README (50+ langues, 10 s – 10 min) — https://github.com/ace-step/ACE-Step-1.5/blob/main/README.md — officiel
[7] Exemples officiels text2music (200 fichiers ; dont example_27, example_40, example_41 en polonais) — https://github.com/ace-step/ACE-Step-1.5/tree/main/examples/text2music — officiel
[8] ComfyUI — code de l'encodeur ACE 1.5 (modèles de prompt du LM, métadonnées dans `<think>`, langue) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/ace15.py — officiel (implémentation)
[9] Comfy-Org — modèle de workflow ACE-Step 1.5 XL sft — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_ace_step1_5_xl_sft.json — officiel
[10] ComfyUI Docs — ACE-Step v1.5 (et une page séparée v1) — https://docs.comfy.org/tutorials/audio/ace-step/ace-step-v1-5 — officiel
[11] ACE-Step 1.5 — page du projet, section Limitations — https://ace-step.github.io/ace-step-v1.5.github.io/ — officiel
[12] GitHub Issue #1114 « Technical Feedback on ACE-Step 1.5 XL » — https://github.com/ace-step/ACE-Step-1.5/issues/1114 — communauté
[13] « Release and test: Ace-Step 1.5 » (test d'un praticien, ambient/Eno) — https://jurn.link/dazposer/index.php/2026/02/04/release-and-test-ace-step-1-5/ — communauté
[14] Z.Tools — « Instrumental prompts for ACE-Step: keeping the vocals out » — https://z.tools/blog/ace-step-instrumental-prompts — communauté
[15] Hacker News — « Ace-Step 1.5 prompt tips » — https://news.ycombinator.com/item?id=46948483 — communauté
[16] GitHub Discussion #1071 « What were you able to do with XL models… » (témoignages anecdotiques d'utilisateurs) — https://github.com/ace-step/ACE-Step-1.5/discussions/1071 — communauté
