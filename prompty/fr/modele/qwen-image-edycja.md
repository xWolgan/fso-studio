<!-- Fiche modèle pour le promptmaker. modele: qwen-image-2-1-edycja, qwen-image-edit-2511 -->
# Édition d'image par instruction : Qwen-Image 2.1 Edit et Qwen-Image-Edit 2511

> Deux modèles DIFFÉRENTS, avec une syntaxe différente pour désigner les images. Vérifie d'abord lequel le participant a choisi.
> **2.1 Edit → `<image1>`, `<image2>`**. **Edit 2511 → « image 1 », « image 2 »** (jamais `<image1>`).

## Ce que c'est et à quoi ça sert (y compris : ce qu'il NE fait PAS bien)
- **Qwen-Image 2.1 Edit** (`qwen-image-2-1-edycja`) — le même modèle 7B que la génération 2.1, avec l'encodeur Qwen3-VL 8B ; jusqu'à 10 images de référence officiellement, **2** dans le Studio [1][2] (officiel), [20] (notre configuration). Licence non commerciale. Préservation de l'identité des personnes et des produits, édition locale en recouvrant une zone d'une couleur [1][2].
- **Qwen-Image-Edit 2511** (`qwen-image-edit-2511`) — la lignée Edit plus ancienne (20B, encodeur Qwen2.5-VL 7B), Apache 2.0 ; jusqu'à 2 images dans le Studio [5][21]. Nouveautés par rapport à 2509 : moins de « dérive » de l'image, meilleure cohérence des personnages (y compris des photos de groupe à partir de deux personnes photographiées séparément), effets intégrés de LoRA populaires (contrôle de la lumière, nouveaux points de vue), remplacement de matériaux dans les projets de design industriel, lignes de construction [5][6] (officiel).
- La lignée Edit (2509) est la meilleure avec **1 à 3 images** ; elle accepte aussi en entrée des cartes de profondeur, de contours, de points clés (poses) [7] (officiel, version 2509 — non confirmé pour 2511).
- Ce qu'ils NE font PAS bien :
  - 2.1 : la cohérence avec plusieurs références faiblit à partir d'environ 3 images ; de profil, la coiffure peut « glisser » [10] (communauté, critique précoce) ; plaintes sur la lumière, les références et la stabilité du visage [11] (communauté, titre du fil seulement). Tendance à redessiner une plus grande partie du cadre que demandé [12] (communauté).
  - 2511 : décalage/zoom de l'image par rapport à l'entrée (« pixel drift »), « peau plastique » [16][17] (communauté) ; le mode rapide perd la texture (comparaison d'une fourrure à 40 vs 4 pas) [14] (communauté).
  - Les deux : caractères accentués hors anglais/chinois dans les inscriptions (é, ç, ą, ł…) — non confirmé.

## Ce que le participant règle dans le Studio (champs, entrées, paramètres de notre YAML — et leur effet sur le prompt)
Source : YAML + workflows [20][21] (notre configuration).

**Qwen-Image 2.1 Edit**
- **image 1** (obligatoire) = **la toile** : c'est elle qui est éditée ; le résultat a **sa taille** (workflow `resolution: 0` → taille native arrondie à un multiple de 32) [2][3][20]. Grande photo = lent (3000×4000 ≈ 12 MP) [2] (officiel).
- **image 2** (facultative) = source d'un matériau, d'un costume, d'un personnage, d'un style.
- **instruction** — un seul champ → `TextEncodeQwenImage21`. L'encodeur **insère lui-même devant chaque image le marqueur `<image1>`, `<image2>`** [4] (code ComfyUI) — c'est pourquoi, dans l'instruction, tu y fais référence exactement ainsi : `<image1>`, `<image2>` [2] (officiel).
- Pas de négatif (vide, CFG 1) [2][20]. **pas** 10–50, 25 par défaut ; les petites modifications locales fonctionnent dès un faible nombre de pas, la reconstruction de tout le cadre demande les 25 pas complets [2] (officiel).
- **« le modèle développe lui-même l'instruction »** (DÉSACTIVÉ par défaut) — le PE-I2I officiel (Qwen3.5 9B, il regarde les images) avec le prompt système officiel dans notre workflow, avec mode de réflexion (depuis le 12.10 ; officiellement le PE est entraîné pour ce mode — environ 1 à 2 min de plus) [20]. Quand le promptmaker écrit une instruction précise — laisse DÉSACTIVÉ.

**Qwen-Image-Edit 2511**
- **image 1** = la toile ; avant l'édition, elle est redimensionnée par le nœud `FluxKontextImageScale` à environ 1 MP (la plus proche des résolutions Kontext) — le résultat a cette taille, pas celle d'origine [21][13].
- **image 2** = référence (matériau, personnage, scène).
- **instruction** → `TextEncodeQwenImageEditPlus`. L'encodeur ajoute avant le texte « Picture 1: [image] Picture 2: [image] » et le système « Describe the key features of the input image…, then explain how the user's text instruction should alter or modify the image » [8] (code ComfyUI).
- **mode** : **rapide** (par défaut) = LoRA Lightning 4 pas, CFG 1, environ 30 s ; **qualité** = 40 pas, CFG 4, environ 7 min [21]. Négatif vide, non modifiable. Le workflow a déjà `index_timestep_zero` (méthode de référence contre la dérive et l'effet « plastique ») [21][17].
- Dépôt officiel : « sans réécriture de l'instruction, l'édition peut être instable » [9] (officiel) — chez nous, c'est le promptmaker qui réécrit.

## Format du prompt (langue, longueur, structure, marqueurs, négatif, poids)
- **Langue : anglais** (prose simple). PE-I2I officiel : description en chinois uniquement pour une instruction en chinois, en anglais pour toutes les autres langues [20] (officiel). 2511 : exemples officiels en anglais et en chinois [5][9]. Pas dans la langue du participant (sauf anglais/chinois).
- **Texte dans l'image** — entre guillemets doubles, mot pour mot, dans sa langue, en respectant les majuscules ; ne le traduis pas [9][20] (officiel). Langue de l'inscription : (1) si le participant a donné les mots ou la langue — ceux-là ; (2) si l'image contient déjà du texte — la langue dominante dans l'image ; (3) sinon — la langue de l'instruction du participant. Une seule langue, pas de paires « FR/EN » [20].
- **Forme : une instruction, pas la description de l'image finale.** Commence par l'opération (Replace / Change / Remove / Add / Turn / Place / Relight / Restore…) [20] (officiel). Une description « façon générateur » amène le modèle à ignorer l'entrée [15] (communauté, Edit Plus).
- **Un seul paragraphe, sans listes, JSON, titres ; sans format ni résolution** [20].
- **Longueur :** concis — l'extenseur officiel d'Edit (2511) demande de raccourcir et de limiter le descriptif [9] (officiel). 2.1 : autant qu'il faut pour qu'il ne reste rien à deviner ; un simple remplacement = 1 à 3 phrases ; « une nouvelle scène avec ce motif » (séance photo, affiche, composition à partir de deux images) = construis la scène, la lumière et la disposition plus largement [20] (officiel).
- **Structure (4 parties)** : opération → cible (quoi, où : « the man on the right ») → spécification du changement (concret : couleur, matériau, style) → **clause de préservation** (« keep … unchanged ») [15][13][20].
- **Clause de préservation courte et en bloc** : nomme ce qui reste **par son type et sa place**, ne décris pas son apparence (« keep the face, pose, background and lighting unchanged »). Plus tu décris précisément quelque chose qui devait rester, plus le modèle le redessine [20] (officiel).
- **À l'affirmative** : « keep the background identical to the input » plutôt que « do not change the background » [20] (officiel).
- **Négatif** : pas de champ (2.1 : CFG 1 ; 2511 : vide, non modifiable) [20][21]. N'utilise pas de poids `( :1.3)` — les deux chemins ont `disable_weights=True`, les parenthèses passent comme du texte [18] (code ComfyUI).

**Références aux images**
- **2.1 :** avec ≥ 2 images, **obligatoirement `<image1>`, `<image2>`** — pas « image 1 », « first image », « l'image 1 » [20][2] (officiel). Avec une seule image, le marqueur n'est pas requis (le PE officiel ne l'utilise qu'à partir de 2 images) — écris « the image » ; l'encodeur marque de toute façon une image unique comme `<image1>` [4], donc `<image1>` n'est pas une erreur non plus. Précise le rôle de chaque image : laquelle est la toile (la composition et le reste sont conservés), ce que tu prends de laquelle [20].
- **2511 :** « image 1 », « image 2 » (l'instruction par défaut de notre workflow) [21] ; l'encodeur les nomme en interne « Picture 1/2 » [8], l'exemple officiel SGLang utilise « Figure 1/2 » [9] — les trois sont du simple texte, choisis-en un et tiens-t'y (efficacité comparée non confirmée). L'ordre des images compte [5][13].
- Identité tirée d'une référence : **désigne l'image, ne décris pas le visage avec des mots** — une description verbale pousse à régénérer et nuit à la ressemblance [20] (officiel).

## Squelette du prompt
Modification sur une seule image (2.1 et 2511) :
```
[Opération] [cible + position dans le cadre] [en quoi : concret — couleur/matériau/forme/style, à un degré fort et net]. [Si quelque chose disparaît ou se déplace : ce qui apparaît à l'endroit dégagé]. Keep [ce qui reste : type + place, en bloc] unchanged.
```
Deux images — Qwen-Image 2.1 :
```
Using <image1> as the canvas, [opération] [cible dans <image1>] with [élément] from <image2>, [comment l'intégrer : échelle, lumière, perspective]. Keep [visage/pose/fond/lumière] of <image1> unchanged.
```
Deux images — Edit 2511 :
```
[Opération] the [cible] in image 1 [with / to] the [élément] from image 2, [intégration : lumière, échelle, perspective]. Keep [ce qui reste] in image 1 unchanged.
```
Changement de médium/style :
```
Turn the image into [médium] with [2–4 traits visibles : trait, remplissage, texture du support, palette]. Keep the composition, [personnages/objets] and their positions unchanged.
```

## Ce qui marche
- **Pleine force de l'édition + gel du reste** : principe officiel du PE-I2I — change l'attribut exactement nommé **fortement et sans ambiguïté**, tout le reste fidèle à l'entrée. Deux erreurs symétriques : la « fuite » (modification de quelque chose qui n'a pas été nommé) et la « sous-édition » (le résultat ressemble à l'entrée) [20] (officiel).
- **« change nothing else in the frame »** à la fin — parce que 2.1 redessine plus que demandé [12] (communauté).
- **Remplacement** : « Replace Y with X » [9] (officiel). **Une opération par instruction**, les choses complexes en chaîne (résultat → nouvelle entrée) [15] (communauté).
- **Suppression** : décris l'objet et sa place (« the second person from the left »), et remplis l'endroit dégagé de façon cohérente avec l'environnement, la lumière et l'ombre [15][20].
- **Édition locale (2.1)** : le participant recouvre une zone de l'image 1 d'une couleur (par ex. rouge) avant de l'importer ; dans l'instruction, nomme la couleur : « …in the red-marked area » ; si cette couleur peut apparaître dans le résultat, ajoute la couleur cible [2] (officiel).
- **Texte** : cite l'ancienne et la nouvelle inscription ; verrouille la typographie (police, couleur, place), sinon elle dérive vers la police par défaut [15] (communauté, Edit Plus) ; officiellement : position/couleur/mise en page seulement si le participant le demande [9].
- **Photos de personnes** : l'identité (âge, genre, coiffure, expression, vêtements) est conservée, les changements d'expression « subtils et naturels » [9] (officiel). Peau : « natural pores, fine detail, texture that matches the lighting of the scene » [17] (communauté).
- **Vieille photo** : modèle officiel « Restore and colorize the photo. » [9] (officiel).
- **Lumière (2511)** : le contrôle de la lumière et le nouveau point de vue sont intégrés [5][6] ; la communauté commence ces instructions par « Relight … » + description de la lumière [16] (communauté, non confirmé).
- **Des références au cadrage, à la perspective et à la lumière similaires** se combinent mieux [13] (communauté).
- **Mode rapide 2511 pour les essais, qualité pour la version finale** — Lightning modifie la texture [13][14] (communauté).

## Biais et pièges
- **Syntaxe de référence confondue** (`<image1>` dans 2511 ou « image 1 » dans 2.1) — l'erreur la plus fréquente avec cette paire de modèles [2][4][8].
- **Fuite** : une accentuation de netteté qui change les couleurs ; un style qui change le visage ; un changement de costume qui perd un accessoire ; un « nettoyage » du cadre « serviable » [20] (officiel). Ne demande rien que le participant n'a pas demandé.
- **Le médium de l'entrée fait partie de son « identité »** : une photo reste une photo, un dessin un dessin, sauf si l'instruction vise explicitement le médium [20] (officiel). Tu veux changer de médium — nomme-le directement et fortement.
- **Dérive / zoom (2511)** : l'image peut se décaler de quelques pixels ou se rapprocher [16] ; d'où la clause « keep the framing and camera angle unchanged » pour les éditions locales (communauté).
- **Peau « plastique » (2511)** — signalée sur Reddit [17] (communauté) ; chez nous `index_timestep_zero` est déjà activé [21] ; dans l'instruction, demande la texture de la peau.
- **Taille du résultat** : 2.1 = taille de l'image 1 ; 2511 = ~1 MP selon l'image 1. Changer le format par l'instruction ne marchera pas — nomme explicitement l'extension de la toile « outpainting » (2.1) [20] ou recadre l'image avant [15].
- **Plusieurs personnages à partir de deux photos** : 2511 s'en sort mieux que 2509 [5] ; 2.1 faiblit à partir de ≥ 3 références [10].

## Au-delà du photoréalisme
- **Changement de style** : décris le style par ses **traits visuels clés**, pas seulement par son nom [9] (officiel) ; avec plusieurs changements à la fois — la description du style à la fin de l'instruction [9]. Exemple de syntaxe : « Make this look like a watercolor painting. » [19] (communauté) — développe avec des traits : flaques de pigment, réserves de papier blanc, bords doux.
- **Style tiré de l'image 2** : pour une stylisation à partir d'une référence, décris le style de la référence et conserve le contenu de la toile [9] (officiel). 2.1 : « Render <image1> in the visual style of <image2>: [traits]. Keep the content and composition of <image1> unchanged. »
- **Force** : le changement de médium doit être **sans ambiguïté** — sinon le résultat ressemble à l'entrée (« sous-édition ») [20]. Nomme la trace de l'outil : trait, hachures, aplat de couleur, trame, grain, rayures.
- **Archive / pellicule** : décris les effets visibles (grain, décoloration, rayures, bords adoucis) et ce qui reste intact. La direction inverse a un modèle officiel (« Restore and colorize the photo. ») [9].
- **Collage** : 2 images → « Place [élément] from <image2> / image 2 onto [endroit] in <image1> / image 1 as a [cut-out paper / torn photo] collage element, [bord, ombre] » — la syntaxe de placement elle-même est officielle [13][19], l'effet collage n'est pas confirmé par un test.
- LoRA de style : le Studio n'en expose pas ici [20][21].

## Mouvement / temps / son
Sans objet. Quand l'édition doit fournir une image pour une vidéo (par ex. première/dernière image) — veille à garder le même cadrage et le même angle de caméra (« keep the framing, camera angle and all positions unchanged »), pour que les deux images concordent.

## À vérifier avant l'envoi
- [ ] Quel modèle ? **2.1 → `<image1>`/`<image2>`** (une seule image : marqueur superflu, « the image ») ; **2511 → « image 1 »/« image 2 »**.
- [ ] Commence par l'opération (un verbe), pas par la description de l'image finale.
- [ ] Changement nommé concrètement et fortement ; rôle de chaque image clair (toile vs source).
- [ ] Clause de préservation : courte, en bloc, à l'affirmative (« keep … unchanged »), sans décrire l'apparence de ce qui reste.
- [ ] Inscriptions entre `"…"`, mot pour mot, dans une seule langue, selon la règle de langue.
- [ ] Une seule opération ; le complexe — en chaîne, en plusieurs étapes.
- [ ] Absents : poids, JSON, format, négatifs du type « no … ».
- [ ] Identité tirée d'une référence — désignée par l'image, pas décrite avec des mots.
- [ ] 2511 : rapide pour les essais, qualité pour la version finale. 2.1 : grandes images d'entrée = lent.

## Sources
[1] Qwen/Qwen-Image-2.1 — fiche modèle — https://huggingface.co/Qwen/Qwen-Image-2.1 — officiel
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — officiel (ComfyUI)
[3] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21 : resolution 0 = taille native ×32) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — officiel (code)
[4] ComfyUI — comfy/text_encoders/qwen_image21.py (marqueurs `<imageN>` insérés devant les images) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — officiel (code)
[5] Qwen/Qwen-Image-Edit-2511 — fiche modèle — https://huggingface.co/Qwen/Qwen-Image-Edit-2511 — officiel
[6] Blog Qwen — Qwen-Image-Edit-2511: Improve Consistency — https://qwen.ai/blog?id=qwen-image-edit-2511 — officiel (contenu d'après les extraits du moteur de recherche ; page rendue en JS)
[7] Qwen/Qwen-Image-Edit-2509 — fiche modèle — https://huggingface.co/Qwen/Qwen-Image-Edit-2509 — officiel (version 2509)
[8] ComfyUI — comfy_extras/nodes_qwen.py + comfy/text_encoders/qwen_image.py (TextEncodeQwenImageEditPlus : « Picture N: », modèle système) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image.py — officiel (code)
[9] QwenLM/Qwen-Image — README + src/examples/tools/prompt_utils.py (polish_edit_prompt) — https://github.com/QwenLM/Qwen-Image — officiel
[10] OrcaRouter — Qwen-Image 2.1 shipped quietly: inside the PE-I2I rewriter — https://www.orcarouter.ai/blog/qwen-image-2-1-open-weights-research-license — communauté
[11] Discussion HF #11 — 光影，参考能力，脸不变能力仍不及预期 — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/11 — communauté (titre seulement)
[12] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — communauté (vendeur)
[13] RunComfy — Qwen Image Edit 2511 in ComfyUI — https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing — communauté
[14] Résultats de recherche : comparaison 40 pas vs Lightning 4 pas (fourrure) — https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning — officiel (LoRA) / communauté (comparaison)
[15] deAPI — Qwen Image Edit Plus prompting guide — https://deapi.ai/blog/qwen-image-edit-plus-prompting-guide-how-to-write-edit-instructions-that-actually-work — communauté (version Edit Plus)
[16] MyAIForce — Fixing Pixel Drift / Qwen Image Edit 2511 Relighting — https://myaiforce.com/qwen-image-edit-2511-relighting/ — communauté (page indisponible lors de la vérification ; contenu d'après le moteur de recherche)
[17] AIStudyNow — Qwen Image Edit 2511 ComfyUI Workflow (index_timestep_zero, peau) — https://aistudynow.com/qwen-image-edit-2511-comfyui-workflow/ — communauté
[18] ComfyUI — comfy/text_encoders/qwen3vl.py, qwen_image.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — officiel (code)
[19] Scenario — Advanced Editing with Qwen Models — https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models — communauté
[20] Notre configuration : modele/obraz/qwen-image-2-1-edycja.yaml ; workflows/obraz/qwenimage21_edycja-obrazu.api.json (nœud 459:479 = prompt système officiel PE-I2I « Edit Prompt Enhancer — General (v2) », 459:474 resolution 0) — notre configuration / officiel
[21] Notre configuration : modele/obraz/qwen-image-edit-2511.yaml ; workflows/obraz/qwenedit2511_edycja-obrazu.api.json (FluxKontextImageScale, index_timestep_zero, Lightning, CFG 1/4, 4/40 pas) — notre configuration
