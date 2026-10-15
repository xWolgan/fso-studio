<!-- Fiche modèle pour le promptmaker. modele: yue-2, yue-2-cover -->
# YuE 2 (YuE2-3B, m-a-p / HKUST, 09.2026) — texte vers musique et cover à partir d'un enregistrement

## Ce que c'est et à quoi ça sert
- **Modèle de chansons** (lyrics-to-song), 3B, architecture AR–NAR avec flow matching. Il écrit d'abord une **partition en notation ABC** (mélodie + accords), puis en tire les tokens musicaux et un son 48 kHz stéréo [4][5] (officiel).
- Modes de planification : **full** (mélodie + accords ; par défaut pour les nouveaux morceaux), **melody** (mélodie seule, accompagnement plus libre ; recommandé pour les covers), **off** (sans partition) [4][5] (officiel). Studio : « YuE 2 » = full avec planification ABC ; « YuE 2 · cover » = melody avec la partition lue dans l'enregistrement [1][2] (notre configuration).
- **Cover** (reprise) = enregistrement → SheetSage2 → mélodie en ABC → YuE2 avec un **nouveau style et de nouvelles paroles**. L'enregistrement **n'est pas** un conditionnement audio : il ne transmet ni le timbre, ni la voix, ni le mix, seulement la mélodie [6][9] (officiel).
- Points forts : forme chanson, arrangements « souvent convaincants », proches d'une production humaine (EN, FR, PT-BR, ID) [13] (communauté) ; selon les auteurs : compétitif avec Suno v5/v6 sur WildSongBench (mesure des auteurs) [4] (officiel).
- **Ce qu'il ne fait PAS bien :**
  - **les morceaux instrumentaux « tels quels »** : la recette officielle pour l'instrumental transfère les notes de la partie Vocal vers la partie Ins **avant** le rendu — le Studio **ne le fait pas** [7] (officiel), [2] (notre configuration) → risque de voix/vocalises (voir pièges) ;
  - la voix : dans presque toutes les langues « reconnaissablement synthétique » [13] (communauté) ; prononciation (PER) moins bonne que Suno v6, les voyelles sont à vérifier à l'oreille [14] (communauté) ;
  - **les langues hors EN/ZH (dont le polonais) — pas de support officiel** : officiellement documentés EN et ZH (ComfyUI cite aussi le japonais) [9] (officiel) ; praticiens : démos EN/ZH/JA/ES, « d'autres langues peuvent marcher » [14] ; MindStudio cite le polonais parmi les langues testées, sans évaluer la qualité [13] (communauté) ;
  - pas d'entrée « référence audio », ni BPM, ni négatif, ni alignement des phonèmes [5] (officiel).

## Ce que le participant règle dans le Studio
**YuE 2 (texte vers musique)** [1][2] (notre configuration) :
| Champ | Valeurs | Où ça va / effet |
|---|---|---|
| **style** | texte | `style` → à la fois le planificateur de partition (ABC) et le générateur ; dans le prompt du modèle, c'est la section `[Tags]` [2][10] |
| **paroles / structure** | texte ; par défaut `[Intro]`, `[Instrumental]`, `[Instrumental]`, `[Solo]`, `[Outro]` | `lyrics` → section `[Lyrics]` [2][10] |
| **durée max. (s)** | 10–300, par défaut 60 | limite haute ; le morceau peut finir plus tôt [9] |
| **seed** | nombre | commun à la partition et au son [2] |

**YuE 2 · cover à partir d'un enregistrement** [1][3] (notre configuration) :
| Champ | Valeurs | Où ça va / effet |
|---|---|---|
| **enregistrement (mélodie)** | fichier audio, obligatoire | SheetSage2 en mode `melody` → ABC (mélodie seule) [3][11] |
| **style** | texte | le son visé (pas celui de l'original !) [6] |
| **paroles / structure** | texte ; par défaut comme ci-dessus | texte à chanter sur la mélodie lue [6] |
| **durée max. (s)** | 10–360, par défaut 120 | limite haute [9] |
| **seed** | nombre | |

- Fixes : partition — temperature 0,7, top_p 0,9, top_k 30, max. 8192 tokens ABC ; musique — temperature 1, top_p 0,95, top_k 100, repetition 1,2 ; CFG 1,0 (= sans guidance) ; rendu 32 pas [2][3] (notre configuration) — valeurs par défaut des nœuds ComfyUI [11] (officiel).
- **Le participant ne voit pas et n'édite pas la partition (ABC) dans le Studio** — bien que le modèle le permette [4] (officiel), [1] (notre configuration).
- **Pas de négatif** ; avec CFG 1,0, la branche négative n'est pas calculée [10] (code ComfyUI).

## Format du prompt
- **Style : une ligne, descripteurs séparés par des virgules, en anglais.** Ordre selon le guide officiel ComfyUI : **Langue + Genre + Caractère de la voix + Tempo + Instruments + Caractéristiques musicales** [9] (officiel). Exemples officiels :
  - « English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM » [5] (officiel) ;
  - « Instrumental, expressive chamber string ensemble, lyrical violin melody, warm viola and cello accompaniment, G major, 96 BPM, a repeated opening phrase followed by a short gentle ending, natural concert hall acoustics, no vocals, no singing, no choir, no spoken words. » [7] (officiel).
- **Tempo, tonalité (et mesure) dans le style** — il n'y a pas de champs séparés ; la partition note le tempo et la mesure, le style doit les décrire de façon cohérente [5] (officiel).
- **Style court** : un long prompt **réduit automatiquement le budget de durée** (contexte de 24 576 tokens = prompt + partition + musique à 25 tokens/s) [9][10] (officiel). Les styles officiels font ~15–35 mots.
- **Paroles : uniquement ce qui doit être chanté**, + balises de section entre crochets, chacune sur sa propre ligne, **ligne vide entre les sections** [5][9] (officiel). Les indications musicales — exclusivement dans le style [9].
- **Balises — ce qui est documenté pour YuE2 :**
  - guides : `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` [9] (officiel) ;
  - dans le code instrumental officiel : planification avec `[Intro]`, `[Verse]`, `[Chorus]`, `[Outro]`, et les balises finales viennent des noms de sections de la partition (`% verse`, `% chorus`, `% bridge`, `% interlude` → `[Verse]`, `[Chorus]`, `[Bridge]`, `[Interlude]`) [7][8] (officiel) ;
  - `[Instrumental]` et `[Solo]` (par défaut dans le Studio) **n'apparaissent pas dans la documentation de YuE2** — elles fonctionnent techniquement (test de l'API du Studio) [12] (notre configuration), mais leur sens pour le modèle n'est pas confirmé.
- **Parenthèses avec didascalies dans les paroles** (p. ex. « (instrumental theme) ») — non : dans les paroles, seulement les mots à chanter [9], et pour un instrumental, officiellement, les paroles doivent être **vides ou ne contenir que des balises** [7] (officiel). Le texte entre parenthèses risque d'être chanté (déduction).
- **Attention aux versions :** YuE (v1, 2025 ; modèles séparés 7B + 1B, autre pipeline) est un autre modèle — n'utilise pas les guides pour la v1 [15] (officiel). Tout ce qui est ici concerne YuE2-3B.

## Squelette du prompt
Chanson — style :
```
[Langue : English / French / Polish…], [genre], [voix : sexe, timbre, manière], [N BPM], [tonalité si importante], [2–4 instruments], [caractère de la mélodie / du phrasé], [espace / enregistrement]
```
Chanson — paroles :
```
[Verse]
[vers]
[vers]

[Chorus]
[vers]
[vers]

[Bridge]
[vers]

[Outro]
[vers]
```
Instrumental — style (formule officielle d'ouverture et de clôture) :
```
Instrumental, [genre/texture], [instrument principal + rôle], [accompagnement], [tonalité], [N BPM], [déroulé : comment ça commence et finit], [espace/enregistrement], no vocals, no singing, no choir, no spoken words.
```
Instrumental — paroles : uniquement des balises (p. ex. celles par défaut du Studio ou `[Intro]` / `[Verse]` / `[Interlude]` / `[Outro]`), sans aucun mot.

## Ce qui marche
- **Style et paroles séparés** — style = le son, paroles = texte + sections [5][9] (officiel).
- **La langue au début du style** (« English, … ») — c'est la forme de tous les exemples officiels de chansons [5][9] (officiel). Pour une autre langue (p. ex. « French, … », « Polish, … ») : par analogie (non confirmé).
- **Exclusions en liste à la fin du style** (« no guitar », « no vocals ») — l'exemple officiel de style jazz contient « no guitar », la recette instrumentale quatre « no … » [7][8] (officiel).
- **Un court paragraphe de style vaut mieux qu'un tas de tags** [14] (communauté).
- **Seed fixe** pour comparer des changements de style ; le même seed sur un autre matériel / une autre version peut donner un autre résultat [4][8] (officiel).
- **Cover** : le plus simple est de garder le texte original et de ne changer que le style ; pour une réinterprétation plus forte — change les deux [6] (officiel).
- **Changer la langue du texte dans un cover** : adapte au chant (syllabes, accents, voyelles longues sur les notes longues, respirations), ne traduis pas mot à mot [8] (officiel).

## Biais et pièges
- **L'instrumental est parfois chanté.** Le modèle est par nature fait pour les chansons ; l'instrumental officiel fonctionne grâce au transfert de la mélodie de la partie Vocal vers Ins, et les auteurs écrivent malgré tout que cela « ne garantit pas l'absence de voix » [7] (officiel). Le Studio n'a pas cette étape [2] → **commence toujours le style par « Instrumental, » et termine par « no vocals, no singing, no choir, no spoken words. »** [7], paroles sans mots ; écoute ; s'il y a de la voix, change de seed. Que l'instrumental YuE du Studio ne chante pas — encore à vérifier à l'écoute [12] (notre configuration).
- **Budget de durée** : un style/texte trop long raccourcit le morceau ; une « durée max. » trop basse coupe au milieu d'une phrase [9] (officiel). La durée est surtout déterminée par la partition et le texte — texte court = morceau court [9] (officiel).
- **Prononciation** — vérifie chaque version ; les voyelles et le phrasé « demandent une oreille humaine » [14] (communauté). Langue non documentée (tout sauf EN/ZH) → un court essai avant un long morceau.
- **Écarts par rapport à la partition** : la réalisation exacte des notes et des durées n'est pas garantie [7][8] (officiel).
- **Faible en hindi/ourdou** [13] (communauté) — signe que les langues hors des données principales s'en sortent moins bien (déduction).

## Cover à partir d'un enregistrement — règles
- **Le style décrit le son visé, pas l'original** [6] (officiel).
- **Nouveau texte proche du phrasé et du nombre de syllabes de l'original** — meilleure adéquation à la mélodie [6][9] (officiel). Sections et ordre du texte conformes à l'ordre de l'enregistrement [6][16] (officiel).
- **Enregistrement** : les erreurs de transcription passent dans le cover [16] (officiel) — choisis un extrait avec une seule ligne mélodique bien nette (déduction). SheetSage2 en mode melody prend la mélodie vocale ou la mélodie instrumentale principale [8] (officiel).
- **Durée max. ≥ durée de la mélodie de l'enregistrement** — la partition couvre tout l'enregistrement ; une limite trop basse coupera le morceau (déduction à partir de [9]). Par défaut 120 s ; le template officiel ComfyUI met 360 [11] (officiel).
- **Cover instrumental** : officiellement, il exige lui aussi le transfert Vocal → Ins [17] (officiel) — le Studio ne l'a pas, donc une mélodie chantée dans l'original reviendra très probablement en voix/vocalise (déduction). Si le participant veut un instrumental à partir d'une mélodie — préviens-le et écoutez ensemble.
- Le cover ne conserve ni la voix de l'interprète ni la forme d'onde de l'enregistrement ; c'est une nouvelle réalisation de la même mélodie [5][17] (officiel).

## Au-delà du photoréalisme (en musique : au-delà de la convention — texture, bande, lo-fi, abstraction)
- La documentation de YuE2 **ne décrit pas** les styles lo-fi, la bande ni l'abstraction. Seul vocabulaire officiel de l'espace : « natural concert hall acoustics », « spacious modern harmony » [7][8] (officiel).
- Descriptions de textures/supports (« tape-saturated », « lo-fi home recording », « vinyl crackle ») — non confirmées ; si nécessaire, brièvement à la fin du style, et compare avec une version sans (même seed).
- Pour l'abstraction, les drones et les textures sans mélodie, MiniMax Music 3 convient mieux (riches exemples officiels d'ambient) — YuE2 planifie toujours **mélodie et accords** [4][5] (officiel).
- Point fort pour la « recherche de forme » : la même mélodie dans différents styles (cover), ou la même chanson avec une autre harmonie — le modèle est construit pour ça [4] (officiel) ; dans le Studio, seulement via le cover et le changement de style.

## Mouvement / temps / son
- **Forme** = balises de section + partition ; tempo et mesure dans le style (p. ex. « 88 BPM ») [5][9] (officiel).
- **Durée** : la « durée max. » est un plafond ; YuE2 termine le morceau de lui-même quand il a fini son plan [9] (officiel). Pour 30–60 s : un couplet + un refrain ou un court poème.
- **Poème chanté** : le texte tel quel sous `[Verse]`/`[Chorus]` ; éventuellement couper les longs vers aux pauses (avec l'accord du participant). Récitation / spoken word — absent de la documentation de YuE2 (inconnu).
- Sortie FLAC 48 kHz stéréo [1] (notre configuration).

## Vérifie avant d'envoyer
- [ ] Style : une ligne en anglais, commence par la langue (chanson) ou par « Instrumental, » (instrumental) ; tempo en BPM dans le style.
- [ ] Instrumental : le style se termine par « no vocals, no singing, no choir, no spoken words. » ; dans les paroles, **aucun** mot ni parenthèse — uniquement des balises.
- [ ] Chanson : dans les paroles, uniquement le texte à chanter + les balises `[Verse]`/`[Chorus]`/`[Bridge]`/`[Outro]` sur des lignes séparées, lignes vides entre les sections.
- [ ] Style court (env. 15–35 mots), sans contradictions.
- [ ] Cover : style = son visé ; texte avec un nombre de syllabes et un ordre des sections proches ; durée max. ≥ durée de l'enregistrement.
- [ ] Chant dans une langue autre que l'anglais ou le chinois (p. ex. la langue du participant) → préviens que ce n'est pas documenté ; propose un court essai.
- [ ] Rappelle d'écouter (voix dans l'instrumental, prononciation) et de tester 2–3 seeds.

## Sources
[1] Studio — `modele/muzyka/yue-2.yaml` et `yue-2-cover.yaml` — modele/muzyka/yue-2.yaml, modele/muzyka/yue-2-cover.yaml — notre configuration
[2] Studio — workflow `workflows/muzyka/yue2_tekst-na-muzyke.api.json` — workflows/muzyka/yue2_tekst-na-muzyke.api.json — notre configuration
[3] Studio — workflow `workflows/muzyka/yue2_cover-z-nagrania.api.json` — workflows/muzyka/yue2_cover-z-nagrania.api.json — notre configuration
[4] YuE2 — README (modes full/melody/off, cover, édition de la partition) — https://github.com/multimodal-art-projection/YuE/blob/main/README.md et fiche https://huggingface.co/m-a-p/YuE2-3B — officiel
[5] YuE2 — Generation guide + exemple `examples/song.json` + référence « generation-and-covers » (champs de la requête, pas de BPM/négatif, CFG) — https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/generation-and-covers.md — officiel
[6] Comfy-Org — template « audio_yue2_music_cover » (notes : style, texte, syllabes, fonctionnement du cover) — https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json — officiel
[7] YuE2 — skill instrumental (SKILL.md, README, `assets/example-style.txt`, `scripts/instrumental.py`) — https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental — officiel
[8] YuE2 — skill « yue2-music » (SKILL.md, references/abc-editing.md : noms des sections dans la partition, adaptation du texte) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/SKILL.md , https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/references/abc-editing.md — officiel
[9] ComfyUI Docs — « YuE2 Music Generation Guide » + template « audio_yue2_text2music » (ordre des éléments du style, budget de durée, langues) — https://docs.comfy.org/tutorials/audio/yue2/yue2 , https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_text2music.json — officiel
[10] ComfyUI — code de l'encodeur YuE2 (`[Tags]`/`[Lyrics]`, contexte 24 576, 25 tokens/s, CFG) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/yue2.py — officiel (implémentation)
[11] ComfyUI Docs — nœuds YuE2GenerateABC, YuE2GenerateMusic, SheetSage2AudioToABC — https://docs.comfy.org/built-in-nodes/YuE2GenerateABC.md , https://docs.comfy.org/built-in-nodes/YuE2GenerateMusic.md , https://docs.comfy.org/built-in-nodes/SheetSage2AudioToABC.md — officiel
[12] FSO — PROGRESS.md (5.10 : test de l'API ; « est-ce que YuE en instrumental ne chante pas » — à vérifier à l'écoute) et docs/audio.md — notes internes (non publiées) — notre configuration
[13] MindStudio — « YuE2: How to Run This Open-Source Music Generation Model Locally » — https://www.mindstudio.ai/blog/yue2-open-music-generation-model — communauté
[14] YuE2 AI (service non officiel ; remarques sur les langues et la prononciation) — https://yue2ai.org/ — communauté
[15] YuE (v1) — page du projet — https://map-yue.github.io/ — officiel (version précédente)
[16] YuE2 — « Cover a recording » — https://github.com/multimodal-art-projection/YuE/blob/main/docs/covers.md — officiel
[17] YuE2 — skill instrumental, cover (`references/cover.md`) — https://github.com/multimodal-art-projection/YuE/blob/main/skills/yue2-music/instrumental/references/cover.md — officiel
