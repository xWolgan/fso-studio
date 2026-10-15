<!-- Fiche modèle pour le promptmaker. modele: omnivoice, omnivoice-projekt, omnivoice-klon -->
# OmniVoice (k2-fsa / Xiaomi) — voix, trois entrées dans le Studio

## Ce que c'est et à quoi ça sert
- Modèle TTS de 0,6B, « modèle de langage par diffusion » non autorégressif, plus de 600 langues (646), sortie 24 kHz mono [7][11][13] (officiel). Polonais : env. 912 h de données d'entraînement [11] (officiel) ; dans notre test, **le meilleur polonais parmi les modèles locaux** (concordance des mots 0,93 selon Whisper), une phrase en env. 1 s [3] (notre configuration). Les autres langues n'ont pas été testées chez nous.
- Trois entrées dans le Studio = trois modes du modèle [1][2] (notre configuration) :
  - **OmniVoice** (`omnivoice`) — texte seul, **sans description de voix** : mode « auto », le modèle choisit lui-même la voix, **différente à chaque seed** [7][22] (officiel).
  - **conception de voix** (`omnivoice-projekt`) — voix à partir d'une **liste fermée de caractéristiques** (genre, âge, hauteur, chuchotement, accent anglais) [8] (officiel), [1] (notre configuration).
  - **clonage de voix** (`omnivoice-klon`) — voix à partir d'un échantillon + sa transcription exacte [7] (officiel). C'est le mode **le plus stable** — le modèle a été entraîné principalement pour le clonage [9][16][35] (officiel).
- **Ce qu'il NE fait PAS bien :**
  - **les émotions et la direction par description** — il n'y a pas de champ pour « triste, tendu » ; selon les auteurs : pas de données avec ce type d'annotations [30] (officiel). L'émotion ne passe que par l'échantillon (clonage), le texte et la ponctuation.
  - **une description libre de la voix en prose** (« chaleureuse, fatiguée, enrouée ») — il ne connaît que la liste de caractéristiques [8] (officiel). Pour une description riche : Breeze (EN/ZH uniquement) [1] (notre configuration).
  - **des énoncés très courts (1–2 s) sans échantillon** — instables [9][16] (officiel).
  - **l'acoustique/la texture d'enregistrement** — par défaut, le modèle « débruite » et génère un son plus propre que l'échantillon ; la réverbération, la bande, le téléphone de l'échantillon ne se transmettent pas [25] (officiel).
  - **des pauses fiables** — le point et la virgule donnent « généralement » une pause, mais pas toujours [15] (officiel).
  - il lui arrive de : couper le dernier son/mot [18][19], répéter ou sauter un fragment [26], changer de voix au milieu d'un énoncé plus long [27], avoir un tempo irrégulier dans ~10 % des générations [28] (officiel/communauté) — d'où : plusieurs seeds et des morceaux plus courts.
- Licence des poids : CC-BY-NC — usage non commercial uniquement [12] (officiel).

## Ce que le participant règle dans le Studio
Le Studio lance OmniVoice via le plugin ComfyUI **TTS Audio Suite 5.9.2** ; 32 pas, guidance 2,0, t_shift 0,1, `denoise` activé, normalisation du texte **désactivée** — le participant ne change pas cela [2][5] (notre configuration / code du plugin).

| Entrée | Champ | Valeurs | Effet sur le prompt |
|---|---|---|---|
| toutes | **texte à prononcer** | texte | seul endroit pour le contenu ; syntaxe — plus bas |
| toutes | **langue** | Polish (par défaut), English, German, French, Spanish, Italian, Ukrainian, Czech, Russian, Chinese, Japanese | doit être la langue du texte ; avec la langue indiquée, le modèle fonctionne « un peu mieux » [7] (officiel) |
| omnivoice, klon | **vitesse de parole** | 0,5–2,0, 1,0 par défaut | >1 plus vite, <1 plus lentement [10] (officiel). Plus lentement (p. ex. 0,9), c'est aussi un contournement des fins coupées [19] (officiel) |
| toutes | **seed** | vide = aléatoire | en mode auto, seed = **autre voix** ; note le seed qui convient [2][22] |
| projekt | **caractéristiques de la voix** | au plus une par groupe (genre, âge, hauteur, chuchotement, accent angl.) | c'est toute la « description de la voix » ; ne peut pas être vide (le plugin renvoie une erreur) [1][5] |
| projekt | **texte de l'échantillon** (avancé) | par défaut « To jest próbka nowego głosu. Mówię spokojnie i wyraźnie. » (en polonais : « Ceci est un échantillon d'une nouvelle voix. Je parle calmement et distinctement. ») | 10 caractères min. [5]. Le modèle le lit d'abord avec la nouvelle voix (fichier « modèle de voix »), **puis clone ce modèle de voix** et dit le texte avec [1][5]. Si la langue n'est pas le polonais, ce texte par défaut doit être remplacé par un texte dans la langue choisie |
| klon | **échantillon de voix** | fichier audio, obligatoire | 3–10 s de parole propre [7] (officiel) |
| klon | **transcription de l'échantillon** | texte, obligatoire | exactement ce qu'on entend dans l'échantillon ; sans elle, le plugin refuse, Studio : silence [1][5] |

- **Le mode conception en pratique** [5] (code du plugin) : les caractéristiques n'agissent que sur le modèle de voix ; ton texte est déjà produit par clonage de ce modèle. Donc : (a) **langue du texte de l'échantillon = langue choisie dans le champ « langue »** (la même langue va aux deux étapes) ; (b) **l'accent ne fonctionne que si le texte de l'échantillon et le texte sont en anglais** [8] (officiel) — avec un texte dans une autre langue, le groupe « accent » ne fait rien ; (c) le texte de l'échantillon doit donner 3–10 s de parole (1–2 phrases, env. 50–150 caractères) et se terminer par un point — c'est le modèle pour le clonage [7][17].
- **La même voix sur plusieurs répliques :** la conception crée la voix de zéro à chaque fois (il y a une marge de liberté à l'intérieur des caractéristiques) [21] (officiel). Méthode sûre : télécharge le « modèle de voix », importe-le comme échantillon dans le **clonage** avec transcription = texte de l'échantillon [21] (officiel).

## Format du prompt
- **Langue : langue du texte = champ « langue ».** Les caractéristiques de la voix sont en anglais, mais c'est le participant qui les choisit avec des boutons — le promptmaker indique seulement **quels boutons** cliquer [1] (notre configuration).
- **Description de la voix (conception uniquement) :** uniquement des valeurs de la liste, séparées par des virgules, une par groupe : `female, elderly, low pitch` [8] (officiel). Groupe vide = le modèle choisit lui-même. Tout ce qui est hors liste est ignoré [8]. Transposition depuis la matrice du médium « Voix » : des rubriques « Qui » et « Texture », il ne reste que le genre, l'âge, la hauteur, le chuchotement ; le reste (timbre, voix rauque, caractère, situation) — **il faut dire clairement au participant que ce modèle ne l'acceptera pas** — on peut l'obtenir par un échantillon (clonage) ou en choisissant Breeze (en anglais) [34][8].
- **Texte à prononcer — syntaxe dans NOTRE Studio** (plugin TTS Audio Suite) [4][5][6] :
  - **Sons non verbaux entre chevrons :** `<laughter>`, `<sigh>` (ainsi que `<confirmation-en>`, `<question-en>`, `<question-ah>`, `<question-oh>`, `<question-ei>`, `<question-yi>`, `<surprise-ah>`, `<surprise-oh>`, `<surprise-wa>`, `<surprise-yo>`, `<dissatisfaction-hnn>`). Le plugin les convertit en `[laughter]` natifs, etc. **N'écris pas `[laughter]` entre crochets** — dans le Studio, `[...]` est la syntaxe du plugin [4] (officiel pour le plugin). (Attention : l'ancien guide `poradniki/omnivoice.md` indique `[laughter]` — c'est une erreur pour le Studio.)
  - **Pause de durée exacte :** `[pause:1.5s]`, `[pause:500ms]`, `[pause:2]` (= secondes) ; alias `wait`, `stop` [5][6]. Le plugin coupe le texte à cet endroit et insère du silence — **la pause est garantie**, contrairement à la ponctuation [5][15]. Attention : les morceaux entre les pauses sont générés séparément (l'intonation « repart de zéro ») [5].
  - **Changement de langue d'un fragment :** `[en:]` avant le fragment, p. ex. un texte dans la langue du participant avec une citation en anglais ; alias du type `[English:]` [6] (officiel pour le plugin). Non testé dans le Studio (non confirmé). Sans balise, le modèle essaie lui-même de gérer le texte mixte [32] (officiel), mais la prononciation des insertions étrangères est parfois moins bonne.
  - **Tout le reste entre `[...]` disparaît** — le plugin le traite comme un nom de personnage (p. ex. `[soupire]`, `[un temps]`, `[B EY1 S]`) et ne le lit pas [5] (code du plugin). N'écris pas de didascalies dans le texte. La correction native de prononciation du README (`[B EY1 S]`, pinyin) **ne fonctionne pas dans le Studio** [5][7].
- **Ponctuation = prosodie :** point, virgule, points de suspension, tiret, point d'interrogation façonnent la phrase [1] (notre configuration) ; les pauses issues de la ponctuation sont probables, pas garanties [15] (officiel). Termine toujours le texte par un point/point d'interrogation/point d'exclamation — l'absence de ponctuation finale favorise la coupure de la fin [18] (officiel/communauté).
- **Nombres, dates, abréviations — en toutes lettres.** La normalisation du texte est désactivée dans le Studio [5] ; selon les auteurs, les chiffres peuvent être mal lus, « normalise-les en mots » [7][20] (officiel). Dans la langue du texte, avec les bonnes formes grammaticales (p. ex. « en mille neuf cent quatre-vingt-un »). Développe les abréviations (« M. », « p. ex. », « etc. ») (déduit de l'absence de normalisation — non confirmé par un test).
- **Poids, JSON, négatif, tags d'émotion** (`[happy]` etc.) — n'existent pas [7][30] (officiel).
- **Longueur :** pas de limite stricte ; au-delà d'env. 30 s de parole, le modèle découpe lui-même le texte en morceaux d'env. 15 s [10] (officiel). En pratique : **une strophe / un paragraphe par génération** — plus facile à corriger, moins de risque de changement de voix et d'erreurs [27][28] (déduit des signalements).

## Squelette du prompt
Conception (les caractéristiques sont cliquées par le participant) :
```
caractéristiques : [genre], [âge], [hauteur]{, whisper}{, [accent — texte anglais uniquement]}
texte de l'échantillon : [1–2 phrases dans la langue du texte, 3–10 s de parole, dans le ton de l'œuvre, avec un point à la fin]
texte : [vers/phrase, ponctuation = phrasé]{ <sigh>}{ [pause:Ns]} [suite du texte, nombres en toutes lettres].
```
Clonage :
```
échantillon : [3–10 s de parole propre de cette personne, dans la langue du texte, silence à la fin]
transcription : [mot pour mot ce qu'on entend dans l'échantillon, avec ponctuation]
texte : [comme ci-dessus]
```
OmniVoice seul : uniquement `texte` + langue + vitesse.

## Ce qui marche
- **Le clonage plutôt que la description**, quand la bible décrit un timbre/une émotion précise : un enregistrement d'une personne (ou du participant) dans cet état, 3–10 s [7][9]. Émotions : des échantillons séparés « triste », « en colère », etc., et une génération par morceaux, chacun avec un échantillon différent — contournement accepté par les auteurs [30] (officiel/communauté).
- **Un échantillon avec du silence à la fin** : coupé de façon à ce que la parole se termine avant la fin du fichier — c'est ainsi que l'auteur a corrigé les artefacts des énoncés courts [17] (officiel).
- **Conception → modèle de voix → clonage** pour une série de répliques avec une même voix [21] (officiel).
- **`[pause:…]` plutôt que compter sur le point** là où la pause fait partie de la forme (césure, enjambement, silence entre les vers) [5][15].
- **`<laughter>` est le plus fiable** ; les autres balises ont été entraînées surtout sur des données chinoises — dans les langues avec espaces, elles étaient parfois sautées ou lues à voix haute (en partie corrigé dans le code) [14] (officiel/communauté). Pour les langues européennes : `<laughter>`, `<sigh>`, et traite le reste comme une expérience.
- **Point d'interrogation/d'exclamation en polonais :** un utilisateur, en polonais : « gotowi do ofiary ? » (espace avant `?`/`!`) donnait une fin correcte, sans espace — une « suspension » [18] (communauté, test unique). Non testé pour d'autres langues (en français, l'espace avant `?`/`!` est de toute façon la norme typographique).
- **Plusieurs seeds** du même texte, puis choisir — l'aléa est grand (tempo, pauses, accent de mot) [28][19] (officiel).
- **Une graphie familière dans le texte** (p. ex. en polonais « ide », « sie », « troche ») donnait une prononciation rurale/familière dans le travail de l'auteur sur les voix « Ludzie » — mais dans ElevenLabs, pas dans OmniVoice [33] (expérience de l'auteur ; non confirmé pour OmniVoice).

## Biais et pièges
- **Mode auto = voix aléatoire** à chaque seed ; impossible de la décrire [22]. Si la bible dit à qui appartient la voix — oriente vers la conception ou le clonage.
- **L'accent de l'échantillon passe dans le texte** dans une autre langue (échantillon polonais → texte anglais avec accent polonais, et inversement) ; difficile à supprimer [7][31] (officiel). Piège de la chaîne « voix de Breeze en anglais → clonage OmniVoice dans une autre langue » : le texte recevra un accent anglais [7] (officiel) — sauf si c'est voulu.
- **Conflit de caractéristiques :** le chuchotement et la hauteur basse ne fonctionnent pas avec « child » (pas de données de ce type) [24] ; « whisper » ne fonctionne pas en mode clonage [23] (officiel). Certaines combinaisons sont ignorées — simplifie la liste [8].
- **Mauvaise transcription de l'échantillon** → des mots de l'échantillon ou des coupures peuvent apparaître dans le résultat [29] (communauté) ; le plugin ajoute seulement la ponctuation finale et supprime les longs silences de l'échantillon [10].
- **Coupure du dernier son** — due aux données d'entraînement ; ce qui atténue : un point à la fin, un tempo plus lent, un échantillon plus calme avec du silence [18][19] (officiel).
- **Le retour à la ligne n'est pas une pause :** les sauts de ligne deviennent des espaces ; l'absence de ponctuation entre les phrases favorisait les répétitions et la « fusion » des phrases [26] (officiel/communauté). Termine chaque vers qui doit se détacher par un signe ou par `[pause:…]`.
- **La voix dérive dans un texte long** (changement de locuteur au milieu) — défaut des données, impossible à corriger par un réglage [27] (officiel). Morceaux plus courts, clonage.
- **L'accent de mot** ne se contrôle pas (les signes d'accent U+0301 fonctionnent « un peu » et abîment le reste — tests en russe) [37] (communauté). Rarement nécessaire dans les langues à accent fixe (polonais, français) ; si un mot sonne mal — autre seed ou reformulation.

## Au-delà du photoréalisme
La parole « non naturaliste » dans OmniVoice relève surtout du **choix de la voix, du rythme et du montage**, pas de la description :
- **Le chuchotement** (`whisper`) comme registre entier de la voix (conception) [8] ; hauteurs extrêmes `very low pitch` / `very high pitch`, âge `child` / `elderly` [8] (officiel).
- **Un accent étranger comme moyen expressif :** le clonage d'un échantillon dans une autre langue lisant le texte transmet l'accent de l'échantillon [7][31] (officiel) — p. ex. une « voix venue d'ailleurs ».
- **Rythme mécanique / litanie :** des `[pause:…]` de longueurs égales, vitesse 0,5 ou 2,0 [5][10] ; chaque morceau entre les pauses est généré séparément, donc l'intonation « se réinitialise » — ce peut être un effet (non confirmé artistiquement).
- **Chœur, superposition, le même texte avec plusieurs voix :** plusieurs seeds en mode auto = plusieurs voix différentes [22] — les couches s'assemblent au montage.
- **Texture (bande, radio, téléphone, réverbération, lo-fi) — pas dans ce modèle.** Le modèle nettoie le son (denoise) et ne transmet pas l'acoustique de l'échantillon [25] (officiel). Fais-le dans l'espace SFX/au montage ; ne l'écris ni dans le texte ni dans les caractéristiques.
- Il n'existe pas de contrôle de l'émotion par les mots — ne promets pas un rendu « sombre » ou « lyrique » depuis le prompt [30].

## Mouvement / temps / son
- **La durée du résultat découle du texte et de la vitesse** (estimée à partir du nombre de caractères ; la ponctuation ajoute du temps) [10][36] (officiel). Un champ « durée » existe dans le modèle, mais **le Studio ne l'expose pas** (toujours auto) [2].
- La vitesse change la durée sans changer la hauteur ; en clonage, l'estimation se base sur le tempo de l'échantillon — échantillon lent = parole plus lente [36][19] (officiel).
- Le modèle coupe les respirations et le silence au début/à la fin (le post-traitement supprime les longs silences, ajoute un court fondu de 0,1 s) [10] (officiel). Un silence plus long au milieu ne s'obtient qu'avec `[pause:…]`.
- Résultat : WAV 24 kHz mono, volume non normalisé [7][2].

## Vérifie avant d'envoyer
- [ ] La bonne entrée : voix précise d'après une description → conception ; personne/émotion précise → clonage ; « n'importe quelle voix » → OmniVoice.
- [ ] Langue du texte = champ « langue » (en conception, le texte de l'échantillon aussi dans cette langue).
- [ ] Caractéristiques uniquement de la liste, une par groupe, non vides ; accent seulement avec l'anglais ; pas de « child + whisper ».
- [ ] Sons non verbaux sous la forme `<laughter>`, `<sigh>` ; aucun autre `[…]` que `[pause:…]` et `[en:]`.
- [ ] Nombres, dates, abréviations en toutes lettres ; le texte se termine par un signe de ponctuation ; vers séparés par de la ponctuation ou `[pause:…]`.
- [ ] Clonage : échantillon de 3–10 s, même langue, transcription mot pour mot.
- [ ] Une strophe/un paragraphe par génération ; recommande au participant 2–3 seeds.
- [ ] Pas de didascalies, d'émotions ni de description acoustique dans le texte — dis où les obtenir (échantillon, SFX, montage).

## Sources
[1] Studio : configuration des entrées voix — `modele/mowa/omnivoice.yaml`, `omnivoice-projekt.yaml`, `omnivoice-klon.yaml` — notre configuration
[2] Studio : workflows ComfyUI — `workflows/mowa/omnivoice_*.api.json` ; gestion du seed/des champs — `studio/workflow.py` — notre configuration
[3] Tests de voix — notes internes (non publiées) — notre configuration
[4] TTS Audio Suite 5.9.2, OmniVoice Native Tags Guide — https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md — officiel (plugin)
[5] TTS Audio Suite 5.9.2, code : `nodes/omnivoice/omnivoice_processor.py`, `utils/text/omnivoice_special_tags.py`, `utils/text/pause_processor.py`, `engines/adapters/omnivoice_adapter.py`, `utils/voice/designers.py` — https://github.com/diodiogod/TTS-Audio-Suite/tree/85da51e0 — officiel (code du plugin, version sur le Spark)
[6] TTS Audio Suite README (pauses, changement de langue) — https://github.com/diodiogod/TTS-Audio-Suite — officiel (plugin)
[7] k2-fsa/OmniVoice README — https://github.com/k2-fsa/OmniVoice — officiel
[8] OmniVoice — Voice Design attributes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md — officiel
[9] OmniVoice — Tips & Notes — https://github.com/k2-fsa/OmniVoice/blob/master/docs/tips.md — officiel
[10] OmniVoice — Generation Parameters — https://github.com/k2-fsa/OmniVoice/blob/master/docs/generation-parameters.md — officiel
[11] OmniVoice — Supported Languages (Polish : 911,68 h) — https://github.com/k2-fsa/OmniVoice/blob/master/docs/languages.md — officiel
[12] Hugging Face — k2-fsa/OmniVoice (licence CC-BY-NC) — https://huggingface.co/k2-fsa/OmniVoice — officiel
[13] Zhu et al., « OmniVoice: Towards Omnilingual Zero-Shot TTS with Diffusion Language Models », arXiv 2604.00688 — https://arxiv.org/abs/2604.00688 — officiel
[14] Issue #28 — balises non verbales et espaces — https://github.com/k2-fsa/OmniVoice/issues/28 — officiel (réponse de l'auteur) / communauté
[15] Issues #63 et #203 — pauses issues de la ponctuation non garanties — https://github.com/k2-fsa/OmniVoice/issues/63 , https://github.com/k2-fsa/OmniVoice/issues/203 — officiel (réponse de l'auteur)
[16] Issue #118 — énoncés courts sans échantillon — https://github.com/k2-fsa/OmniVoice/issues/118 — officiel (réponse de l'auteur)
[17] Issue #265 — silence à la fin de l'échantillon — https://github.com/k2-fsa/OmniVoice/issues/265 — officiel (réponse de l'auteur)
[18] Issues #245 et #204 — coupure de la fin ; test polonais avec espace avant « ? » — https://github.com/k2-fsa/OmniVoice/issues/245 , https://github.com/k2-fsa/OmniVoice/issues/204 — officiel / communauté
[19] Issue #116 — dernier son ; contournement par un tempo plus lent — https://github.com/k2-fsa/OmniVoice/issues/116 — officiel (réponse de l'auteur)
[20] Issues #51 et #174 — nombres — https://github.com/k2-fsa/OmniVoice/issues/51 , https://github.com/k2-fsa/OmniVoice/issues/174 — officiel (réponse de l'auteur)
[21] Issue #44 — voix constante : enregistrer la conception et cloner — https://github.com/k2-fsa/OmniVoice/issues/44 — officiel (réponse de l'auteur)
[22] Issue #255 — le mode auto tire la voix au hasard — https://github.com/k2-fsa/OmniVoice/issues/255 — officiel (réponse de l'auteur)
[23] Issue #119 — « whisper » sans effet en clonage — https://github.com/k2-fsa/OmniVoice/issues/119 — officiel (réponse de l'auteur)
[24] Issue #124 — chuchotement et hauteur basse vs « child » — https://github.com/k2-fsa/OmniVoice/issues/124 — officiel (réponse de l'auteur)
[25] Issue #95 — denoise, l'acoustique de l'échantillon ne se transmet pas — https://github.com/k2-fsa/OmniVoice/issues/95 — officiel (réponse de l'auteur)
[26] Issue #134 — absence de points et espaces → répétitions — https://github.com/k2-fsa/OmniVoice/issues/134 — communauté (confirmé avec l'auteur)
[27] Issues #206 et #176 — changement de voix en cours de route — https://github.com/k2-fsa/OmniVoice/issues/206 , https://github.com/k2-fsa/OmniVoice/issues/176 — officiel (réponse de l'auteur)
[28] Issue #248 — tempo irrégulier (estimation de la durée) — https://github.com/k2-fsa/OmniVoice/issues/248 — communauté
[29] Issue #21 — transcription erronée de l'échantillon — https://github.com/k2-fsa/OmniVoice/issues/21 — communauté
[30] Issues #78, #177, #178 — pas de contrôle de l'émotion ; contournement par des échantillons — https://github.com/k2-fsa/OmniVoice/issues/78 , https://github.com/k2-fsa/OmniVoice/issues/178 — officiel (réponse de l'auteur) / communauté
[31] Issue #47 — accent de l'échantillon — https://github.com/k2-fsa/OmniVoice/issues/47 — officiel (réponse de l'auteur)
[32] Issue #84 — textes multilingues — https://github.com/k2-fsa/OmniVoice/issues/84 — officiel (réponse de l'auteur)
[33] Channelers, voix « Ludzie » (ElevenLabs v3) — notes internes (non publiées), `LUDZIE_uwagi_i_poprawki.md`, `LUDZIE_PL\05_babcia\05_babcia_prompt_i_tekst.md` — expérience de l'auteur (autre modèle)
[34] Gabarit du médium « Voix » — `prompty/media/mowa.md` — notre configuration
[35] Issue #144 — conception moins stable que le clonage — https://github.com/k2-fsa/OmniVoice/issues/144 — officiel (réponse de l'auteur)
[36] OmniVoice — estimation de la durée (`omnivoice/utils/duration.py`) — https://github.com/k2-fsa/OmniVoice/blob/master/omnivoice/utils/duration.py — officiel (code)
[37] Issues #129, #37, #65 — accent de mot (russe) — https://github.com/k2-fsa/OmniVoice/issues/129 — communauté
