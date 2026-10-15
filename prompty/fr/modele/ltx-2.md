<!-- Fiche modèle pour le promptmaker. modele: ltx-2-3, ltx-2-5 -->
# LTX-2.3 et LTX-2.5 (Lightricks) : vidéo avec son

## Ce que c'est et à quoi ça sert (y compris : ce qu'il ne fait PAS bien)

- Un seul modèle (22B, DiT) génère **l'image et le son en même temps**, en une seule passe. Le son (ambiance, effets, parole, chant, musique) découle du prompt, donc le prompt décrit aussi ce qu'on entend [12][13][14] (officiel).
- **LTX-2.3** (mars 2026). Encodeur de texte Gemma 3 12B [2][12][5]. Une seule scène continue par génération. Il existe une variante **image + enregistrement → vidéo** : l'image s'anime au rythme du son fourni, p. ex. elle parle ou chante [1].
- **LTX-2.5** (août 2026). Son propre encodeur Gemma 4 12B affiné, qui tient mieux les prompts complexes (plusieurs personnages, mouvement de caméra, lumière) [11][13][18] (officiel). Nouveauté : le **multiplan natif**, 2 à 4 plans reliés par des coupes dans une seule génération [3][6] (officiel). Dans le Studio, il n'y a pas ici d'entrée son [1].
- Ce qui marche le mieux : des cadres cinématographiques avec un seul sujet principal, un langage de caméra clair, une lumière cohérente, un son bien décrit, l'atmosphère (brume, pluie, reflets), les petits gestes et les expressions du visage [3][4] (officiel). D'après le 2.3 Prompt Guide, la stylisation fonctionne bien aussi : « painterly, noir, analog film, pixelated animation » [4] (officiel).
- **Ce qui marche mal :**
  - les textes et logos (l'orthographe n'est pas fiable, y compris en 2.5) [3][4] ;
  - la physique chaotique (la danse, ça va) [4] ;
  - les cadres surchargés avec beaucoup de personnages ou d'actions, une logique d'éclairage mélangée [3][4] (officiel) ;
  - l'attribution des répliques aux personnages quand plusieurs parlent [14] (officiel) ;
  - la prononciation dans les langues peu représentées dans les données [14] (officiel) ;
  - la dérive dans les scènes de plus de 20 s environ [14] (officiel) ;
  - la permanence des objets : des choses apparaissent et disparaissent [34] (communauté).
- **Limite du son (2.3) :** quand le son ne contient pas de parole, sa qualité est parfois plus faible [12] (officiel).

## Ce que le participant règle dans le Studio (champs, entrées, paramètres de notre YAML — et leur effet sur le prompt)

Une seule entrée par modèle. Le Studio choisit la variante tout seul, d'après les entrées fournies [1] (notre configuration) :

| Entrées | LTX-2.3 | LTX-2.5 |
|---|---|---|
| rien | texte → vidéo | texte → vidéo |
| `klatka_start` | image → vidéo | image → vidéo |
| `klatka_start` + `klatka_koniec` | première et dernière image | première et dernière image |
| `klatka_start` + `dzwiek` | image + enregistrement → vidéo | — (absent) |

Paramètres [1][2] (notre configuration) :

- **prompt.** Un seul champ. **Il n'y a pas de champ négatif.** Les workflows ont un négatif écrit en dur (« pc game, … cartoon, childish, ugly »), mais tous les samplers tournent à **CFG = 1** (modèle distillé), donc le négatif n'agit pas. C'est aussi ce que disent les recommandations officielles : « distilled… CFG=1 » [11][12]. Le négatif ne commence à agir qu'à CFG > 1 [27] (communauté). Tout ce que le modèle doit éviter doit donc être écrit dans le prompt lui-même, sous forme de description de ce qui doit être là.
- **format (proportions) :** 16:9 (par défaut), 21:9, 4:3, 1:1, 3:4, 9:16 ; env. 0,9 MP, dimensions divisibles par 32.
  - En LTX-2.3 (image, image + enregistrement) et dans les deux variantes « images » (première/dernière), les images sont **recadrées au centre** au format choisi. Le format doit donc correspondre à l'image, sinon une partie du cadre disparaît.
  - LTX-2.5 image → vidéo ne recadre pas l'image avant le modèle. On ne sait pas ce qui se passe quand les proportions ne correspondent pas ; le mieux est qu'elles concordent.
- **durée :** 1–20 s (10 par défaut). **fps :** 24 ou 25.
  - Un plan long demande une description plus longue et plus riche : « A short prompt for a long video often results in the model rushing through the described action » [4] (officiel).
  - Règle empirique : **une action principale toutes les 2–3 s** [5] (officiel, blog).
  - Un clip long avec un prompt court, c'est aussi le risque de « cartons de fin » et de logos dans les dernières images. Le bug a été corrigé par l'upscaler v1.1, que nous utilisons [28] (communauté + réponse de Lightricks).
  - Dans la variante avec enregistrement, la durée coupe l'enregistrement [1].
- **enrichissement** (« le modèle enrichit lui-même le prompt » ; réglage avancé, désactivé par défaut ; absent de la variante LTX-2.3 « images »). Un LLM intégré réécrit le prompt **en un paragraphe anglais dans le style des légendes d'entraînement** [7][8][9][10] :
  - 2.3 : Gemma 3 12B (le même modèle que l'encodeur) ;
  - 2.5 : Gemma 4 E2B (env. 1–2 min de plus) [13].
- **seed.** À seed égale, change une seule chose à la fois [5].
- **Deux étapes** (demi-résolution, puis upscaler ×2) : seulement pour les variantes texte → vidéo, image → vidéo et image + enregistrement [2].
  - Les variantes « images » font une seule passe directement en pleine résolution, sans upscaler [2] (notre configuration ; conforme à [13]). Cela n'a pas d'effet sur le prompt.
- **L'image de départ** passe par `LTXVPreprocess` (légère compression, censée rapprocher le cadre d'une image vidéo) [2] (notre configuration).

## Format du prompt

- **Langue : anglais.**
  - Les légendes d'entraînement et les deux enhancers écrivent en anglais. L'enhancer 2.5 a une consigne explicite : « If the user wrote in another language, produce the English caption » [8][9] (officiel, code).
  - L'encodeur est multilingue [14], mais personne n'a étudié la qualité d'une description dans une autre langue (**non établi**). On écrit la description en anglais.
- **Les répliques parlées** s'écrivent entre guillemets, **dans la langue où elles doivent être prononcées** (une réplique dans la langue du participant s'écrit dans cette langue). Nomme la langue et l'accent [3][4][8] (officiel).
  - Qualité de la parole dans d'autres langues que l'anglais (p. ex. le polonais) : **non établi** ; aucun test trouvé.
  - L'accent et la prononciation dans d'autres langues sont parfois incertains [29] (communauté).
  - Le modèle ne traduit pas les répliques [3] (officiel, concerne Dub-It).
- **Structure :** **un seul paragraphe fluide, au présent**, dans l'ordre chronologique du début à la fin du plan [3][4][6] (officiel).
  - Pas de listes, de puces, de titres ni d'étiquettes du type « Audio: »/« Visual: » : l'enhancer 2.5 les a interdites [8] (officiel, code).
  - Exception : pour les dialogues, les multiples beats ou un timing précis, le guide officiel admet un **style scénario** : en-tête de scène, « Reporter: "…" » [3][4] (officiel).
  - Nos fiches n'utilisent pas les tags ni les étiquettes de section de `media/wideo.md` : on écrit le même contenu en prose, dans le même ordre.
- **Six éléments (les deux modèles)** [3][4][6] (officiel) :
  1. Le plan : valeur de plan, catégorie, terminologie cinéma.
  2. La scène : lumière, palette, textures, atmosphère.
  3. L'action comme séquence, chaque phrase avec un verbe de mouvement (« walks, turns, exhales, reaches »).
  4. Les personnages : âge, cheveux, tenue, signes particuliers ; l'émotion uniquement par des signes physiques.
  5. La caméra : comment et **quand** elle bouge, décrite par rapport au sujet, plus l'aspect du sujet **après** le mouvement.
  6. Le son : ambiance, effets, musique, parole, chant.
- **Ordre :**
  - LTX-2.3 : l'article de blog sur l'adhérence au prompt conseille de commencer par **l'action principale en une phrase**, puis les détails du mouvement, l'apparence, l'environnement, et à la fin la caméra et la lumière [5] (officiel, blog).
  - La direction de style se donne de préférence **tout au début** [7][15] (officiel). L'enhancer 2.3 commence par « Style: <style>, … » [7][10] ; c'est le seul « marqueur » visible dans le code.
  - LTX-2.5 : les légendes d'entraînement commencent par l'action ou par un détail visuel. Trois choses sont tissées dans la prose : la **valeur de plan** (l'une de : extreme wide / wide / medium / medium close-up / close-up / extreme close-up), le **mouvement de caméra** (toujours ; pas de mouvement = « the camera remains static ») et le **point de vue** (front-facing / side view / over-the-shoulder / top-down / low-angle / high-angle) [8] (officiel, code de l'enhancer).
- **Longueur :**
  - 2.5 : officiellement « 4–8 descriptive sentences » pour un plan simple, davantage pour les scènes complexes, « provided every sentence adds concrete visual or audio detail » [3][6]. L'enhancer 2.5 vise **150–220 mots** [8].
  - 2.3 : les sources divergent. Le Prompt Guide dit que « les prompts longs et détaillés l'emportent » [4], et l'article sur l'adhérence au prompt demande de rester sous 200 mots [5] (tous deux officiels).
  - En pratique : **env. 80–220 mots**, proportionnellement à la durée du clip.
- **Pas de poids, pas de JSON, pas de « (word:1.2) ».** Les tokenizers Gemma 3 et Gemma 4 dans ComfyUI ont `disable_weights=True` — parenthèses et nombres arrivent au modèle comme du texte ordinaire (code ComfyUI : `comfy/text_encoders/lt.py`, `gemma4.py`). Pas non plus de chiffres ni de degrés (« pans at 2 degrees per second ») : c'est un exemple d'erreur « over-constrained » [4] (officiel).
- **Négations dans le texte :** l'exemple officiel les utilise dans la description du son (« a low male vocal drone…, no instruments, no music ») [3] (officiel). L'article de blog sur l'animation 2D conseille « no gradients, no shadows » pour un graphisme en aplat [15] (officiel, blog). À utiliser avec parcimonie : d'abord décrire ce qui est là.

## Squelette de prompt

Texte → vidéo, un seul plan (les deux modèles) :
```
[style/medium/texture — première phrase]. [valeur de plan] of [sujet : âge, apparence, tenue — seulement ce qu'on voit], [point de vue], in [lieu : matériaux, textures]. [lumière : source, direction, couleur ; une seule logique] and [palette]. [action 1, au présent], as [mouvement de caméra par rapport au sujet, rythme]. Then [action 2 / changement], [aspect du sujet après le mouvement de caméra]. [son de fond — sources concrètes], [effet rattaché à l'action] ; [qui] says in [langue, timbre, rythme, volume], "[réplique]". [musique ou son absence ; réverbération/espace].
```

Image → vidéo :
```
[2.5 : une phrase d'ancrage conforme à l'image : valeur de plan, sujet, lieu]. [ce qui se met à bouger et comment — chronologiquement : d'abord…, un instant plus tard…], [mouvement de caméra ou « the camera remains static »]. [ce qui change dans la lumière/la matière]. [son : sources synchronisées avec le mouvement ; parole entre guillemets].
```

Première et dernière image :
```
[comment on passe de l'état de la première image à celui de la dernière : phases successives du changement], [mouvement de caméra reliant les deux cadres], [lumière/moment]. [son pendant la transition].
```

Image + enregistrement (2.3 uniquement) :
```
[style], [valeur de plan, point de vue]. [sujet] [comment il exécute le son de l'enregistrement : bouche, souffle, geste, expression — au rythme de l'enregistrement], [petits mouvements du corps/du fond], [caméra].
```

Multiplan (2.5 uniquement, texte → vidéo) :
```
[plan 1 : valeur de plan, cadre, sujet avec identifiant, action, son]. A hard cut transitions to [plan 2 : nouvelle valeur de plan, angle, qui est dans le cadre — même identifiant], [action] ; [son : ce qui continue / ce qui change à la coupe]. [év. plan 3 sur le même modèle].
```

## Ce qui marche

- **Mouvement de caméra avec un vocabulaire connu :** « follows, tracks, pans across, circles around, tilts upward, pushes in / pulls back, overhead view, handheld movement, over-the-shoulder, wide establishing shot, static frame » [3][4]. Plus « slow dolly in », « handheld tracking » [4] (officiel).
- **L'émotion par le corps :** au lieu de « sad », écris « his eyebrows angle downward and his lips are pressed together » [8]. Au lieu de « tense confrontation », écris « two men stand three feet apart, both leaning forward with clenched fists » [5] (officiel).
- **Au sens littéral, pas métaphorique :** décris ce que la caméra voit physiquement [5] (officiel, blog). Une métaphore tirée d'un poème doit être traduite en matière, mouvement, lumière et son.
- **Connecteurs temporels :** « Initially…, A moment later…, Simultaneously… » [3][8] ainsi que « as / then / while » [7][35] (officiel + communauté).
- **Dialogue découpé en phrases avec didascalies** (2.3) : « …says in a slow voice, "…" He pauses and looks to the side, then continues, "…" ». Les pauses écrites dans le texte (« a beat of silence », « she pauses ») sont réellement exécutées par le modèle [3][4] (officiel).
- **Son rattaché à une source dans le cadre :**
  - D'abord le fond sonore de l'espace, puis les effets rattachés à l'action qui les produit [30] ; du concret plutôt que du générique (« soft footsteps on tile », pas « ambient sound ») [7] (officiel).
  - Le signal qui marche, c'est un objet en mouvement avec son son attaché ; les adjectifs d'ambiance ne marchent pas [33] (communauté).
- **Son décrit au fil de l'action, pas ajouté à la fin** [10] (officiel, prompt système I2V 2.3).
- **Qualité du son :** en 2.3, la description de l'acoustique, du timbre de voix et de l'ambiance a plus d'influence qu'avant [4] (officiel). Un ajout du type « The audio is crisp with faint room tone » aide [4]. On remplit le silence par un ton de pièce (« quiet room tone ») [30] (communauté).
- **Vocabulaire du métier avec une hiérarchie claire :** commence par le domaine principal (p. ex. l'animation), ajoute le deuxième comme qualificatif de matière, le troisième seulement comme lumière ou étalonnage. Les mélanger à égalité pousse le modèle à « faire la moyenne » [16] (officiel, blog).
- **Plan fixe :** écris « A static shot of … » comme **première phrase** [19] (communauté ; efficacité en 2.5 incertaine, voir les pièges).

## Biais et pièges

- **Photoréalisme par défaut.** « AI video generation defaults to photorealism » [15] (officiel). Un clip plus long en style 2D dérive vers le réalisme [15].
- **L'enhancer (« enrichissement ») déplace l'esthétique et le contenu :**
  - Enhancer 2.3 : en l'absence de style, « Default to cinematic-realistic » [7]. Avec en plus « Restrained language » : des couleurs ordinaires, sans intensificateurs [7].
  - L'enhancer 2.5 contient en dur « cinematic, film-grade color…, beautiful natural lighting, crisp fine detail » et encourage le mouvement de caméra (« Camera movement is expected and good ») [8][9] (officiel, code). Cela contredit le principe du promptmaker « on n'ajoute pas de joliesse ».
  - Communauté : avec l'enhancer 2.5 activé, on obtient parfois des résultats sans aucun rapport avec le prompt [17]. S'y ajoutent des caractéristiques démographiques non voulues chez les personnages ; Gemma 3 respectait mieux le prompt [18] (communauté).
  - Conclusion : **« enrichissement » désactivé par défaut**. Officiellement, l'enhancer aide le moins quand le prompt a déjà la bonne structure [3].
  - Nos workflows ont deux failles [2] (notre configuration). En LTX-2.3 image + enregistrement, l'enhancer **ne reçoit pas l'image**, donc il écrit comme pour du texte → vidéo et peut inventer une apparence contraire à l'image. En LTX-2.5 « images », il ne voit **que la première image** et a l'interdiction de faire des coupes.
- **Le zoom de caméra.** En 2.5 (et 2.3), les clips « foncent » souvent tout seuls vers le visage. Demander une caméra fixe aide peu : selon un utilisateur, environ 2 essais sur 50 sans zoom. Un autre écrit que 2.5 s'en sort mieux que 2.3. Les plans rapprochés dominent [19] (communauté). Il n'y a pas de LoRA de caméra dans le Studio.
- **Sans description du mouvement de caméra, le modèle fait sa propre dérive** ou des changements d'angle aléatoires [5] (officiel, blog). Précise toujours la caméra, y compris « static ».
- **Parole non demandée.** Le 2.3 « lit parfois le prompt à voix haute » ou baragouine quand on n'a pas demandé de parole [24] (communauté). Quand il doit n'y avoir aucune voix, décris précisément ce qu'on entend : les sources, « no one speaks » (**non confirmé** que ça aide).
- **La musique s'ajoute toute seule.** Sans indication, le modèle peut ajouter sa propre piste [30][33]. L'hébergeur recommande « no music » [30], mais en 2.3 les utilisateurs n'ont pas réussi à la couper par le prompt [26] (communauté). Si la musique doit être ajoutée après : écris « no music » et prévois de devoir couper la piste au montage.
- **Le volume et la distance de la voix** (« whisper », « from a distance ») se pilotent mal en 2.3 selon les utilisateurs [25] (communauté). La liste officielle de mots donne pourtant « Whisper · Mutter · Shout · Scream » [3]. Le résultat n'est pas garanti.
- **Texte dans le cadre.** Le 2.3 peut ajouter des sous-titres de lui-même, souvent avec des fautes [27]. Les guillemets signifient de la parole, pas un texte écrit [30] (communauté). Officiellement : texte dans le cadre court et gros, orthographe non garantie, les textes et logos importants s'ajoutent au montage [3] (officiel). Pour nous : mieux vaut ne pas demander de texte dans le cadre.
- **Les contradictions** (« a still, peaceful lake with dramatic waves crashing » ; « running quickly… in slow motion ») perdent le modèle [4][5] (officiel). Décris le ralenti par son effet : « suspended in slow motion, each step drawn out » [5].
- **Surcharge :** cinq actions dans un seul clip finissent compressées, ou celles du milieu sont omises [5] (officiel, blog). Forme courte : un événement, deux au plus.
- **I2V en 2.5 : l'identité du personnage de l'image est parfois modifiée.** Les utilisateurs rapportent que le 2.3 tenait mieux le visage [20] (communauté).
- **I2V en 2.3 :** une description contraire à l'image « may cause scene cuts » [10] (officiel, prompt système).
- **Un prompt repris d'un autre modèle** (tags, listes de plans de Kling/Seedance/H3) marche moins bien. Réécris-le en paragraphe LTX [3] (officiel).

## Au-delà du photoréalisme

- **Principe de base (officiel, blog sur la 2D [15]) :**
  - la déclaration de style comme **première phrase** du prompt, répétée dans le texte ;
  - en cas de retour du réalisme : « not photorealistic, no realistic textures, 2D only » ;
  - l'ancre la plus forte est **une image de départ dans le style visé** (faite dans l'espace Image ou dessinée), car le prompt ne décrit alors plus que le mouvement ;
  - **des clips courts (2–4 s)** protègent de la dérive vers le réalisme.
- **Vocabulaire du guide officiel** [3][4] :
  - Animation : stop-motion, 2D / 3D animation, claymation, hand-drawn ;
  - Stylized : comic book, 8-bit pixel, surreal, minimalist, painterly, illustrated ;
  - Cinematic : film noir, experimental film, arthouse, documentary ;
  - Film Characteristics : **film grain, lens flares, pixelated edges, jittery stop-motion**.
- **Dessin / animation 2D** [15][16] (officiel, blogs) :
  - « hand-drawn linework », « ink-and-paint style », « cel-shaded flat color », « limited animation with held frames » ;
  - en aplat : « flat vector illustration style, solid color fills with clean outlines, no gradients, no shadows » ;
  - aquarelle / livre illustré : « watercolor illustration style, soft painted textures, muted pastel palette, gentle hand-drawn lines » ;
  - les mots sur le rythme aident le style : « gentle, calming motion » ; « exaggerated » libère des proportions réalistes ;
  - **ne mélange pas le vocabulaire 2D et 3D** dans un même plan [16].
- **Pellicule, grain, archive (restauration)** [16] (officiel, blog 2.3) :
  - « coarse silver-halide grain, black-and-white 16mm », « fine grain, Kodachrome-tight » ;
  - « telecine flicker, gate weave, edge halation » ;
  - noms de pellicules (« Ektachrome », « Portra », « Fuji Reala ») ; attention aux anachronismes.
  - VHS et vidéo analogique : pas de source officielle (**non confirmé**).
- **Rendu pictural, noir, cinéma argentique :** cités comme points forts du 2.3 [4] (officiel).
- **Collage, abstraction, pure texture sans sujet :** pas de sources (**non établi**).
  - Le modèle est réglé pour des « cinematic, single-subject scenes » [3]. En pratique, la voie la plus sûre est une image de départ (collage, abstraction) plus un prompt qui décrit uniquement le mouvement de la matière et de la caméra. C'est une déduction de [15], pas un test.
- **L'enhancer nuit à la stylisation** (« cinematic-realistic » / « film-grade » par défaut) [7][8]. En cas de stylisation, « enrichissement » désactivé.
- **Les schémas d'animation** décrits en numéros d'images (« anticipation frame at frame one… snap to release pose at frame six ») viennent du blog [16]. Cela contredit l'avertissement contre les chiffres [4] ; considère-les comme **non confirmés**.

## Mouvement / temps / son

- **Mouvement :** une seule action continue avec un début et une fin clairs ; une action principale toutes les 2–3 s [5]. Écris les pauses et les « beats » dans le texte [3].
- **Caméra :** nomme le mouvement, le rythme et le moment (« as she turns, the camera slowly pushes in »). Décris le cadre après le mouvement [3][4].
- **I2V (différence 2.3 / 2.5) :**
  - 2.3 : décris **le mouvement et le changement**, ne répète pas ce qu'on voit déjà sur l'image ; « describe the transition from stillness to motion » [4][10] (officiel).
  - 2.5 : l'enhancer commence par une phrase conforme à l'image (valeur de plan, sujet, lieu, lumière), puis déroule l'action chronologiquement, **en un seul plan, sans coupes** [9] (officiel, code). Le multiplan avec image de départ seulement si la coupe à partir de l'image est voulue [3].
  - Les deux : dans le nouveau prompt, ne change pas l'apparence du sujet de l'image.
  - Techniquement, l'I2V insère l'image comme première image latente et la fige ; pour le reste, le flux est le même qu'en T2V [23] (officiel, réponse de Lightricks).
- **Première et dernière image :**
  - décris **la transition** : ce qui se passe entre les images, avec le mouvement de caméra et le son [13] (officiel) ;
  - les deux images au même format [13] ; idéalement, la dernière est une retouche de la première et les changements se font l'un après l'autre, pas tous en même temps [33] (communauté) ;
  - la force des deux images dans nos workflows est de 0,7, donc elles tiennent le cadre « en souplesse » [2] (notre configuration).
- **Multiplan (2.5 uniquement)** [3][6][32] :
  - 2–4 plans [3] (officiel) ; pour 10 s, plutôt 3 au maximum [32] (hébergeur d'API, **non confirmé** officiellement) ;
  - chaque coupe nommée en prose (« A hard cut transitions to… », « The view cuts to a close-up of… », « A match cut connects… », « The image dissolves into… ») ;
  - après la coupe, on redéfinit : valeur de plan, angle, qui est dans le cadre, lumière ;
  - **le même identifiant** pour le personnage ou l'objet (tenue, couleur) ;
  - à chaque coupe, écris ce que devient le son : il continue, s'éteint ou change ;
  - chaque plan a une fonction (plan large → détail → réaction).
  - Sans coupe nommée, le modèle fera un seul plan avec un mouvement de caméra [32] (communauté).
  - Lip-sync et scène intime : mieux vaut un seul plan [3].
- **Son généré (texte/image → vidéo) :**
  - couches : la voix devant, les effets sur les actions, le fond en dessous [30] ;
  - pour chaque réplique : qui parle, la langue, l'accent, le timbre, le rythme ; une personne par réplique [30] (communauté) ; réplique plus courte que la durée du clip ;
  - pour le chant : « sings » ; nomme le genre, l'ambiance et les instruments de la musique, ou son absence [3][8] ;
  - l'accent tonique en majuscules ne marche pas ; décris où est la pause et quel mot est plus appuyé [29] (communauté).
- **Image + enregistrement (LTX-2.3 uniquement) :**
  - Notre workflow **fige le son** (masque de bruit 0) [2][22], donc le modèle ne le modifie pas, il anime seulement l'image.
  - Dans le prompt, **ne décris pas une autre piste**. Décris l'interprétation visuelle de l'enregistrement : qui l'exécute, comment (bouche, souffle, geste), la caméra, le fond [4] (officiel).
  - Selon l'hébergeur d'API pour le 2.5 Pro : « describes the look and the performance, not the words » [31]. Visage net, bien éclairé, de face, bouche visible ; un cadre identique au cadre final, car le modèle ne recadre pas [31] (communauté/hébergeur).
  - Chant : une voix lead bien nette ; les voix avec beaucoup de réverbération sont parfois prises pour des chœurs et le personnage ne les chante pas ; beaucoup dépend de la seed [22] (communauté, test sur 2.5).
  - L'audio externe et le chant marchent mieux en 2.3 qu'en 2.5 [21] (communauté). Dans le Studio, seul le 2.3 a cette variante, donc ça tombe bien.
  - **Parole dans la langue du participant, de façon plus sûre :** enregistrer la voix dans l'espace Voix (p. ex. OmniVoice), puis utiliser cette variante. C'est une déduction de [29] et [14], pas un test.

## Vérifie avant d'envoyer

- [ ] Paragraphe en anglais, au présent, sans listes, titres ni étiquettes (« Audio: ») — sauf style scénario voulu.
- [ ] Style / medium / texture dans la **première phrase**, littéralement d'après la bible ; pas de « cinematic, beautiful, 8k » si la bible ne le dit pas.
- [ ] Valeur de plan, point de vue et mouvement de caméra nommés (ou « the camera remains static » / « A static shot of… » au début).
- [ ] Action chronologique ; env. 1 action toutes les 2–3 s de la durée réglée ; pauses écrites.
- [ ] Émotions sous forme de signes physiques ; métaphores traduites en matière, lumière, mouvement, son.
- [ ] Son décrit concrètement (sources dans le cadre, espace) ; musique ou absence de musique dite explicitement ; parole entre guillemets, avec la langue et la manière de parler, une personne par réplique.
- [ ] Pas de texte demandé dans le cadre ; pas de contradictions (calme contre vagues, vite contre ralenti).
- [ ] I2V : 2.3 seulement le mouvement et le changement ; 2.5 une phrase d'ancrage conforme à l'image, puis le mouvement ; format dans le Studio = format de l'image.
- [ ] Images (première/dernière) : la transition entre les états décrite ; les deux images au même format.
- [ ] Image + enregistrement (2.3) : description de l'interprétation et de la lecture visuelle, sans nouvelle piste son.
- [ ] Multiplan (2.5) : 2–4 coupes nommées en prose, cadre redéfini, mêmes identifiants, continuité du son.
- [ ] Laisse « enrichissement » désactivé (surtout en cas de stylisation) ; si le participant l'active, qu'il vérifie l'aperçu du prompt réécrit.
- [ ] Pas de négatif dans le Studio (CFG 1) : ce qu'on ne veut pas, on ne le nomme pas ; on décrit ce qui doit être là.

## Sources

[1] Studio FSO — configuration des modèles : `modele/wideo/ltx-2-3*.yaml`, `ltx-2-5*.yaml` — notre configuration
[2] Studio FSO — workflows ComfyUI : `workflows/wideo/ltx_23_*.api.json`, `ltx_25_*.api.json` (CFG 1, négatif fixe, Gemma 3 12B fp8 / Gemma 4 12B + E2B, upscaler 2.3 v1.1, masque audio 0, recadrage des images) — notre configuration
[3] LTX Docs — Prompting Guide (LTX-2.5 ; multi-shot, enhancer, exemples, vocabulaire) — https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide — officiel
[4] LTX Blog — LTX-2.3 Prompt Guide (10.03.2026) — https://ltx.io/blog/ltx-2-3-prompt-guide — officiel
[5] LTX Blog — How To Improve LTX-2.3 Prompt Adherence (13.05.2026) — https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence — officiel (blog)
[6] LTX Blog — LTX-2.5 Prompt Guide (10.08.2026) — https://ltx.io/blog/ltx-2-5-prompt-guide — officiel
[7] Lightricks/LTX-2 — gemma3_t2v_system_prompt.txt (enhancer LTX-2.x / Gemma 3) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma3_t2v_system_prompt.txt — officiel (code)
[8] Lightricks/LTX-2 — gemma4_t2v_system_prompt.txt (enhancer LTX-2.5) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_t2v_system_prompt.txt — officiel (code)
[9] Lightricks/LTX-2 — gemma4_i2v_system_prompt.txt (enhancer LTX-2.5, I2V) — https://github.com/Lightricks/LTX-2/blob/main/packages/ltx-core/src/ltx_core/text_encoders/gemma/encoders/prompts/gemma4_i2v_system_prompt.txt — officiel (code)
[10] ComfyUI — comfy_extras/nodes_textgen.py (nœud TextGenerateLTX2Prompt ; prompt système I2V Gemma 3 ; choix T2V/I2V selon la présence d'une image) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_textgen.py — officiel (code ComfyUI)
[11] Hugging Face — Lightricks/LTX-2.5 (carte du modèle) — https://huggingface.co/Lightricks/LTX-2.5 — officiel
[12] Hugging Face — Lightricks/LTX-2.3 README — https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md — officiel
[13] ComfyUI Docs — LTX-2.5 tutorial — https://docs.comfy.org/tutorials/video/ltx/ltx-2-5 — officiel (ComfyUI)
[14] LTX-2: Efficient Joint Audio-Visual Foundation Model (arXiv 2601.03233 ; légendes d'entraînement, limites) — https://arxiv.org/html/2601.03233v1 — officiel (article)
[15] LTX Blog — How To Generate 2D Animation With AI Video Models (26.04.2026) — https://ltx.io/blog/how-to-generate-2d-animation-with-ai-video-models — officiel (blog)
[16] LTX Blog — Domain-Specific Prompting for LTX-2.3: VFX, Animation & More (04.08.2026) — https://ltx.io/blog/domain-specific-prompting — officiel (blog)
[17] HF LTX-2.5 discussion #36 — Prompt Enhancement Produces Unrelated Generations — https://huggingface.co/Lightricks/LTX-2.5/discussions/36 — communauté
[18] HF LTX-2.5 discussion #9 — LTX Gemma API Text Encode (réponse de LTX : Gemma 4 maison ; remarques sur l'enhancer) — https://huggingface.co/Lightricks/LTX-2.5/discussions/9 — communauté + réponse officielle
[19] HF LTX-2.5 discussion #54 — Zooming in — https://huggingface.co/Lightricks/LTX-2.5/discussions/54 — communauté
[20] HF LTX-2.5 discussion #30 — The character consistency in i2v — https://huggingface.co/Lightricks/LTX-2.5/discussions/30 — communauté
[21] HF LTX-2.5 discussion #57 — Don't Use LTX 2.5 For Music Videos! Stick To LTX 2.3 — https://huggingface.co/Lightricks/LTX-2.5/discussions/57 — communauté
[22] HF LTX-2.5 discussion #44 — custom audio lipsync (latent audio figé ; dépendance au matériau et à la seed) — https://huggingface.co/Lightricks/LTX-2.5/discussions/44 — communauté
[23] HF LTX-2.5 discussion #48 — Are I2V & T2V workflows actually different? (réponse de LTX) — https://huggingface.co/Lightricks/LTX-2.5/discussions/48 — réponse officielle
[24] HF LTX-2.3 discussion #45 — Model reading the prompt out loud — https://huggingface.co/Lightricks/LTX-2.3/discussions/45 — communauté
[25] HF LTX-2.3 discussion #52 — Why is it impossible to control the volume of speaking characters? — https://huggingface.co/Lightricks/LTX-2.3/discussions/52 — communauté
[26] HF LTX-2.3 discussion #25 — How to kill the music — https://huggingface.co/Lightricks/LTX-2.3/discussions/25 — communauté
[27] HF LTX-2.3 discussion #5 — Subtitles and Removal (le négatif exige CFG > 1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/5 — communauté
[28] HF LTX-2.3 discussion #13 — spatial-upscaler-x2-1.0 causes unwanted text/overlay (corrigé en v1.1) — https://huggingface.co/Lightricks/LTX-2.3/discussions/13 — communauté + réponse officielle
[29] HF Forum — LTX 2.3 problem with dialogs (accent tonique, prononciation) — https://discuss.huggingface.co/t/ltx-2-3-problem-with-dialogs/176649 — communauté
[30] Runware — LTX-2.5 Pro: Native audio — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/native-audio — communauté (hébergeur d'API)
[31] Runware — LTX-2.5 Pro: Audio-driven characters — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/audio-driven — communauté (hébergeur d'API)
[32] Runware — LTX-2.5 Pro: Multi-shot — https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/multi-shot — communauté (hébergeur d'API)
[33] fal — How To Use LTX-2.5: Prompts & Workflows — https://fal.ai/learn/tools/how-to-use-ltx-2-5 — communauté (hébergeur d'API)
[34] HF LTX-2.5 discussion #38 — object permanence/consistency — https://huggingface.co/Lightricks/LTX-2.5/discussions/38 — communauté
[35] RunDiffusion — LTX-2 Prompt Guide (connecteurs temporels, présent) — https://www.rundiffusion.com/ltx-2-prompt-guide — communauté
