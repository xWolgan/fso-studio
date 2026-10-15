<!-- Fiche modèle pour le promptmaker. modele: ideogram-4 -->
# Ideogram 4 (poids ouverts, 9,3B) — texte → image, prompt en JSON

## Ce que c'est et à quoi ça sert (y compris : ce qu'il NE fait PAS bien)
- Modèle texte→image d'Ideogram, entraîné de zéro, 9,3B de paramètres, DiT à flux unique ; l'encodeur de texte est Qwen3-VL-8B-Instruct, le VAE vient de FLUX.2 [10][9][2] (officiel / notre configuration).
- Entraîné **exclusivement sur des légendes structurées en JSON**, qui décrivent de façon exhaustive chaque élément de l'image. La prose ordinaire « ne fonctionnera pas et déclenchera probablement un avertissement de sécurité » [4][14] (officiel).
- Points forts : texte dans l'image (score OCR pour l'anglais 0,97) [14], **contrôle de la palette par hex** [4], **placement des éléments par bbox** [4], affiche, couverture, typographie, mise en page [15][27] (officiel / communauté). Selon la communauté, les personnes n'ont pas l'air « en plastique » et le contrôle de la position est très précis [20] (communauté).
- Points faibles :
  - Le filtre de sécurité intégré aux poids donne des faux positifs : au lieu de l'image apparaît une image grise avec le texte « Image blocked by safety filter ». Dans ComfyUI, impossible de le désactiver [4][15][21] (officiel / communauté).
  - Pas de transparence ni de canal alpha. Il dessine un damier qui ne fait que l'imiter [23] (communauté).
  - En mise en page (mIoU 0,69) et en raisonnement spatial (0,76), il obtient ses plus faibles scores parmi ses propres benchmarks [14] (officiel).
  - Les textes longs se dégradent. Les diacritiques polonais sont parfois perdus ou doublés [26] (communauté, non vérifié chez nous ; on peut s'attendre au même risque pour les accents d'autres langues, non confirmé).
  - Les résultats sont peu variés [29] (communauté).
  - Il n'édite pas d'images et n'accepte pas d'image en entrée (dans notre Studio, c'est uniquement texte→image) [2] (notre configuration).
- Licence des poids : Ideogram 4 Non-Commercial (code : Apache-2.0) [10] (officiel). Attention : notre YAML indique « Ideogram Open Model » [1] — divergence dans la configuration, pas dans la fiche.

## Ce que le participant règle dans le Studio (champs, entrées, paramètres de notre YAML — et leur effet sur le prompt)
- **prompt** : envoyé **tel quel** à `CLIPTextEncode` (encodeur `qwen3vl_8b_int8_convrot`, type `ideogram4`) [1][2] (notre configuration).
  - **Chez nous, le magic prompt ne fonctionne pas.** Le sous-graphe « magic prompt » du workflow se contente d'assembler le texte de l'instruction système pour l'aperçu et ne lance aucun LLM [2]. C'est donc le promptmaker qui joue le rôle du magic prompt et qui doit rendre un **JSON complet et valide**.
  - Le bouton « modèle » insère un squelette dans la variante non photographique (`art_style`) [1].
- **format (proportions)** : 16:9 (par défaut), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16, à 1,0 MP. Les côtés sont arrondis à un multiple de 16 [1][2] (notre configuration).
  - La bbox se calcule sur une échelle 0–1000 **sur chaque axe** par rapport au cadre. Quand on change de format, les cadres s'étirent avec lui [5][3].
  - Le modèle gère nativement 256–2048 px et des proportions jusqu'à 6:1 [7]. Les auteurs annoncent la meilleure qualité en 2048×2048 [10]. Notre 1 MP peut affaiblir le petit texte (non confirmé).
- **profil** : rapide = Turbo (12 pas), par défaut = Default (20), qualité = Quality (48) [1][2].
  - Selon la documentation, la plupart des pas tournent en CFG 7, avec à la fin quelques pas de « polissage » en CFG 3 [7] (officiel).
  - Chez nous, `CFGOverride` règle cfg 3 de 70 % à 100 % du parcours [2] (notre configuration).
  - Pour du petit texte, utilise le profil « qualité » [12] (officiel).
- **seed** : a aussi une forte influence sur le déclenchement d'un faux blocage du filtre [21] (communauté).
- **Pas de negative prompt.** La branche négative est un `ConditioningZeroOut` (texte mis à zéro) plus un modèle inconditionnel séparé dans `DualModelGuider` [2][8] (notre configuration / officiel). Les exclusions de la version hébergée Ideogram.ai ne fonctionnent pas ici [12].

## Format du prompt
- **JSON valide** : guillemets doubles pour les clés et les chaînes, pas de commentaires, pas de balises ```. À l'intérieur de la prose, écris les citations entre apostrophes (`'TEXTE'`) [5] (officiel).
- **Prose en anglais, textes dans leur langue d'origine.** Les champs descriptifs (`high_level_description`, `style_description`, `background`, `desc`) sont toujours en anglais. Seul le champ `text` est dans la langue de l'inscription, p. ex. celle du participant, avec les caractères accentués écrits directement, et non sous forme `\u0105` [5][6][4] (officiel).
- **Les clés et leur ordre sont strictement définis** (CaptionVerifier avertit des clés inconnues, des manques et d'un mauvais ordre) [4][6] (officiel) :
  - niveau principal : `high_level_description`, `style_description`, `compositional_deconstruction`. Toute autre clé est inconnue, y compris `aspect_ratio` (ne l'ajoute pas ; seul le magic prompt v1 le renvoie, ce qui contredit le schéma [22][5]) ;
  - `style_description` pour la photographie : `aesthetics`, `lighting`, `photo`, `medium`, `color_palette` ;
  - `style_description` hors photographie : `aesthetics`, `lighting`, `medium`, `art_style`, `color_palette`. **Exactement un parmi `photo` / `art_style`, jamais les deux** ;
  - `compositional_deconstruction` : `background`, puis `elements` ;
  - élément `obj` : `type`, `bbox`, `desc`, `color_palette` ;
  - élément `text` : `type`, `bbox`, `text`, `desc`, `color_palette`.
- **Champs obligatoires :** `compositional_deconstruction` avec `background` et `elements` [4]. `high_level_description` est « fortement recommandé » [4]. Dans Ideogram hébergé, sans lui le JSON est traité comme du texte [11], donc **mets-le toujours**.
- **Remplis toujours `style_description`** : « le modèle n'a pas de style par défaut » [12]. Sans lui, il dérive vers la photographie (voir Biais).
- **`medium`** : les exemples officiels sont `photograph`, `illustration`, `3d_render`, `painting`, `graphic_design` (liste ouverte, « etc. ») [4]. Dans l'exemple ComfyUI apparaît aussi p. ex. « Mixed-media digital collage » [2].
- **bbox** : `[y_min, x_min, y_max, x_max]`, entiers 0–1000, origine dans le coin supérieur gauche, **y d'abord** [4][18].
- **Couleurs** : uniquement `#RRGGBB` en MAJUSCULES. Jusqu'à 16 dans `style_description`, jusqu'à 5 par élément. `color_palette` est toujours la dernière clé de son bloc [4][6] (officiel).
- **Longueur** :
  - l'encodeur accepte jusqu'à 2048 tokens [9] ;
  - `high_level_description` : 50 mots max., 1 phrase (2 au plus) [5][12] ;
  - le `desc` d'un élément : 30–60 mots [5] ;
  - le guide hébergé recommande ≤5 éléments pour la meilleure qualité [12], bien que l'exemple complet officiel ait 17 éléments [4]. Pour nous : 2–6 éléments.
- **Poids** : une syntaxe du type `(mot:1.3)` n'existe pas. L'accent s'exprime par la bbox, la palette et l'ordre des éléments (non confirmé que les poids nuisent, mais ils ne figurent pas dans le schéma [4]).

## Squelette du prompt
Variante non photographique (par défaut pour les ateliers) :
```json
{
  "high_level_description": "[médium/technique] of [sujet principal + action], [composition du cadre en 3–6 mots], [ambiance en tant que fait physique].",
  "style_description": {
    "aesthetics": "[2–5 traits visuels concrets : texture, contraste, densité, vide]",
    "lighting": "[source de lumière + direction + dureté ; pour le graphisme p. ex. plate/uniforme]",
    "medium": "[illustration | painting | graphic_design | 3d_render | autre médium en une expression]",
    "art_style": "[technique et matériau : outil, support, trace de la main, impression/grain, limites de palette]",
    "color_palette": ["[#FOND]", "[#OMBRE]", "[#LUMIÈRE]", "[#ACCENT]"]
  },
  "compositional_deconstruction": {
    "background": "[enveloppe de la scène : sol/mur/ciel/atmosphère ; pour le graphisme : surface de la feuille]",
    "elements": [
      {"type": "obj", "bbox": [y1, x1, y2, x2], "desc": "[identité du sujet] — [traits principaux] — [un signe distinctif]", "color_palette": ["[#..]"]},
      {"type": "text", "bbox": [y1, x1, y2, x2], "text": "[TEXTE LITTÉRAL\nDEUXIÈME LIGNE]", "desc": "[taille, position, une catégorie de police, une graisse, couleur, technique]", "color_palette": ["[#..]"]}
    ]
  }
}
```
Variante photographique : dans `style_description`, à la place d'`art_style`, mets `"photo": "[appareil/objectif/pellicule/grain]"` **avant** `medium`, et règle `medium` sur `"photograph"` [4].

## Ce qui marche
- **Une bbox pour chaque élément principal.**
  - L'ajout d'une bbox a levé le blocage du filtre dans un cas signalé [19] (communauté).
  - Sans bbox, le modèle aplatit la scène en vue de profil [25] (communauté).
  - N'omets la bbox que pour des masses impossibles à compter (foule, champ de fleurs, étoiles) [5] (officiel).
- **Recalcule la forme de la bbox selon le format.** `[0,0,500,500]` n'est un carré que dans un cadre 1:1. Pour un objet rond ou carré, il faut `(x2-x1)/(y2-y1) ≈ W/H`. Les erreurs de forme produisent des doublons et une mauvaise échelle [5] (officiel). En 16:9, rapproche-toi au plus jusqu'au plan taille ou reste en plan d'ensemble [28] (communauté).
- **Un sujet = un élément.** Décris les parties d'un corps ou d'un objet dans son `desc`, pas comme éléments séparés [5].
- **Le sol toujours dans `background`.** Plancher, terre, eau, flaques et reflets ne peuvent pas être un élément `obj`. Sinon le modèle « enterre » le personnage dans une bande de sol [5][12] (officiel).
- **Ne décris rien deux fois.** Chaque chose figure soit dans `background`, soit comme élément [5].
- **Ordre des éléments proche de l'ordre de lecture.** Si un élément fait référence à un autre (« sous le texte… »), ce dernier doit venir avant [18] (communauté/fournisseur). Les grands objets liés au mur (fond) se mettent dans `background` et en plus comme premier élément [5].
- **Du concret plutôt que de l'ambiance.** Les mots « moody », « vibrant », « luminous » ou « stunning » pèsent peu ou nuisent. Ce qui marche mieux : la source et la direction de la lumière, la couleur en hex et le matériau [12][5] (officiel).
- **Une valeur plutôt qu'un choix.** Pas de « or », « such as », « various », « implied », « maybe ». En typographie, une catégorie de police, une graisse et un style [5] (officiel).
- **Palette** :
  - ajoute la couleur du fond (fond sombre = hex sombre dans la palette) et une paire lumière/ombre [4] ;
  - le hex fixe la direction, alors qu'une couleur décrite en mots n'est qu'une interprétation [18] ;
  - la palette pilote fortement l'image, mais ne fixe pas la couleur de chaque pixel [11] ;
  - pour un effet d'impression, 3–4 couleurs d'accompagnement (tons directs) suffisent [13] (officiel).
- **Texte** :
  - chaque bloc distinct est un élément `text` à part, et la formulation littérale va dans `text`, pas dans `desc` [4][18] ;
  - un nom écrit dans le `desc` d'un objet est seulement « deviné » [18] ;
  - dans une même inscription, 5–7 mots au maximum [12] ;
  - coupe un slogan long avec `\n` aux limites des mots [5] ;
  - écris les petits nombres en toutes lettres [12] (officiel, 4.0 hébergé).
- **Blocage du filtre (image grise avec texte) :**
  - change le seed [21] ;
  - ajoute ou corrige les bbox [19][20] ;
  - ajoute des détails dans le JSON [12].
  - Ne réduis pas le prompt à de la prose (officiel / communauté).
- **Itération** : ne change que le champ nécessaire et laisse le reste du JSON. Malgré cela, toute l'image peut bouger [18].

## Biais et pièges
- **Par défaut, il dérive vers la photographie.** L'instruction du magic prompt v1 dit de choisir, sans indication, `photograph` et une « esthétique iPhone » [5]. Le guide hébergé dit que le modèle n'a pas de style par défaut [12]. Si tu veux autre chose, règle **toujours** explicitement `medium` et `art_style`.
- **Les verbes « Paint/Draw/Illustrate » ne désignent pas le médium**, seulement « montre ». C'est le nom qui décide du médium (watercolor, ink drawing…) [5].
- **Il « peuple » de lui-même les scènes vides.** C'est ainsi qu'ont été entraînées des légendes qui décrivaient tout [10][5]. Quand tu veux du vide, écris-le explicitement (« minimal, single subject, empty negative space »), car ce sont les mots que v1 traite comme désactivant le peuplement [5].
- **Le mot « warm »** dans la description de l'étalonnage d'une photo donne un « look IA » ambré. Nomme plutôt la source de lumière (bougie, lampadaire au sodium) [5] (officiel, règle du magic prompt).
- **Effets inventés** : n'ajoute pas « glitch », « digital artifacts » ni « dissolved » s'ils ne sont pas le but [5].
- **Le filtre de sécurité** dans ComfyUI en local a bloqué 53–93 % des prompts en prose selon le seed, même pour un lac à l'aube [21]. Les faux positifs arrivent aussi avec du JSON [20]. Chez nous, une prose courte a donné une image grise avec un message mal écrit [3] (communauté / notre configuration).
- **L'exemple de la documentation officielle sans bbox** (voilier) est toujours bloqué selon un signalement [19] (communauté).
- **16:9 comme portrait pivoté** : on a signalé un cadre qui ressemblait à un portrait tourné. Ce qui aide : des bbox cohérentes avec le format [24] (communauté, source faible).
- **Le premier plan et le fond ne se fondent pas** [29]. On a aussi signalé une fois un entêtement sur le style anime dans des scènes de fantasy malgré une demande de photographie [20] (communauté, témoignages isolés).
- **Les caractères diacritiques dans les textes** (signalé pour le polonais) peuvent disparaître ou se doubler [26] (communauté). Un grand texte est plus fiable qu'un petit (anglais : env. 97 % vs env. 90 %) [12]. Nous n'avons pas testé d'autres langues que l'anglais chez nous.
- **Le fond transparent ne fonctionne pas** (VAE sans alpha) [23]. Pour le détourage, il y a un outil séparé du Studio, « suppression de l'arrière-plan » [32] (notre configuration).
- **L'exemple complet officiel contient le filigrane d'une agence** comme élément `text` [4]. Le modèle connaît donc des légendes avec filigranes et peut en ajouter dans des descriptions « d'archives/de presse » (non confirmé).
- **Les prompts d'Ideogram.ai hébergé** (style codes, negative prompt, magic prompt de production) **ne se transposent pas 1:1**. Le magic prompt du dépôt « n'est pas celui de la production » [4].

## Au-delà du photoréalisme
- Mécanisme : `art_style` au lieu de `photo`, `medium` ≠ `photograph` [4]. La documentation et ComfyUI montrent : une illustration douce et contemporaine, encre et aquarelle, flat vector [14], affiche graphique [11], collage mixed-media [2].
- **Décris la technique et le matériau, pas des noms.** Le guide hébergé recommande de nommer le médium et l'artiste ou le courant [12]. Dans nos ateliers, nous évitons cependant d'imiter des styles « par raccourci » [31], donc remplace le nom par une description de la trace :
  - outil : rotring, fusain, pinceau sec ;
  - support : papier fait main, carton, toile ;
  - mode d'application : glacis, empâtement, papier découpé ;
  - limitation de la palette.
- **Dessin, illustration** : `medium: "illustration"`. Dans `art_style`, décris l'outil, le trait et le remplissage. Beaucoup de techniques manuelles sont classées par v1 comme illustration : encre, aquarelle, huile, vecteur, pixel art [5].
- **Picturalité** : `medium: "painting"` [4]. Mets la texture (empâtement, glacis, trace de pinceau) dans `art_style`/`aesthetics`.
- **Impression, grain, risographie, similigravure** :
  - décris une texture d'impression usée (trame de risographie, grain du papier, défauts de repérage), 3–4 tons directs, sans 3D et sans dégradés [13] (officiel, hébergé) ;
  - selon v1, les effets de médium (grain, texture du papier, trame, risographie) **ne vont pas dans `background`**, mais dans la description générale et le style [5] ;
  - l'exemple officiel de carte de visite a pourtant « subtle paper texture » dans `background` [4] ;
  - règle pour nous : la surface physique de la feuille peut aller dans `background`, la technique et le grain vont dans `art_style`/`aesthetics`/HLD.
- **Bande, pellicule, archives** :
  - dans la variante photo, le champ `photo` accepte le support et le grain, p. ex. « vintage grainy 35mm film… halftone scan… light leaks » dans l'exemple ComfyUI [2], ainsi qu'une description d'appareil du type « Hasselblad medium format, slightly desaturated » [12] ;
  - v1 interdit le flou de mouvement et l'étalonnage « cinéma » dans les photos ordinaires, sauf si c'est voulu [5].
- **Collage** : l'exemple de notre workflow utilise `medium: "Mixed-media digital collage"`, des découpes photographiques avec un liseré blanc, du papier déchiré et des tampons. Chaque découpe est un `obj` séparé avec sa bbox [2] (notre configuration / ComfyUI). Mélanger des traditions exige une frontière nette entre elles [13].
- **Abstraction** : pas de sources (on ne sait pas comment le modèle s'en sort). Proposition (non confirmée) : des éléments `obj` comme formes et taches nommées, avec bbox et palette propre, `medium: "painting"` ou `"graphic_design"`. Évite les mots « implied/suggested », car v1 demande de décrire concrètement [5].
- **Anime/BD** fonctionne en JSON (`medium: "anime illustration"`) [29][28], mais ce n'est pas l'objectif des ateliers.

## Mouvement / temps / son
- Sans objet : image unique. L'image peut servir de première ou dernière image pour les modèles vidéo du Studio (H3, LTX, WAN) [33] (notre configuration). Dans ce cas, règle un format compatible avec la vidéo, généralement 16:9, et laisse de la place pour le mouvement dans le cadre (non confirmé comme méthode ; c'est la décision du participant).

## Vérifie avant d'envoyer
- [ ] Le JSON se parse, il n'y a ni balises ``` ni commentaires, et seulement 3 clés principales (sans `aspect_ratio`).
- [ ] `high_level_description` fait ≤50 mots, en anglais, et commence par le sujet.
- [ ] `style_description` est rempli : exactement un parmi `photo`/`art_style`, ordre des clés conforme au schéma, et `medium` explicite.
- [ ] La prose est en anglais. Les textes dans `text` sont littéraux, avec les caractères accentués écrits directement, ≤5–7 mots, coupés par `\n`.
- [ ] Les hex sont en MAJUSCULES `#RRGGBB` : ≤16 dans le style, ≤5 par élément, avec la couleur du fond et une paire lumière/ombre, et `color_palette` est la dernière clé.
- [ ] Les éléments principaux ont une bbox `[y1,x1,y2,x2]` dans la plage 0–1000, les formes sont recalculées selon le format du cadre, et le sol est dans `background`.
- [ ] Un sujet = un élément, rien n'est décrit deux fois, pas de mots « or/such as/various/implied » ni d'adjectifs d'ambiance creux.
- [ ] Aucune attente envers un negative prompt ou la transparence.
- [ ] Pour du petit texte, profil « qualité ». En cas d'image grise avec « blocked », change le seed et les bbox.

## Sources
[1] Configuration du modèle dans le Studio — modele/obraz/ideogram-4.yaml — notre configuration
[2] Workflow ComfyUI du Studio — workflows/obraz/ideogram4_tekst-na-obraz.api.json (nœuds 98:24, 98:155, 98:10, 98:147, 98:157, sous-graphe 134, exemple de collage) — notre configuration
[3] Guide du Studio + test sur le Spark 2026-10-04 — poradniki/ideogram-4.md — notre configuration
[4] Ideogram 4 — Prompting Guide — https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md — officiel
[5] Magic prompt system prompt v1 — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/magic_prompt_system_prompts/v1.txt — officiel (identique à celui de notre workflow)
[6] CaptionVerifier — https://github.com/ideogram-oss/ideogram4/blob/main/src/ideogram4/caption_verifier.py — officiel
[7] Inference (presets du sampler) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/inference.md — officiel
[8] Pipeline (CFG asymétrique, branche inconditionnelle) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/pipeline.md — officiel
[9] Model architecture (max. 2048 tokens de texte) — https://github.com/ideogram-oss/ideogram4/blob/main/docs/model_architecture.md — officiel
[10] README du dépôt — https://github.com/ideogram-oss/ideogram4 — officiel
[11] Ideogram Docs — JSON Prompting (Ideogram 4.0) — https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0 — officiel (produit hébergé)
[12] How to JSON prompt for Ideogram 4.0 (18.06.2026) — https://ideogram.ai/blog/ideogram-4-json-prompting/ — officiel (produit hébergé)
[13] The Ideogram 4.0 prompt guide — https://ideogram.ai/blog/claude-mcp/ — officiel (produit hébergé)
[14] Ideogram 4.0 Technical Details — https://ideogram.ai/blog/ideogram-4.0/ — officiel
[15] ComfyUI — Ideogram 4.0 Day-0 Support — https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui — officiel (ComfyUI)
[16] ComfyUI Docs — Ideogram v4 — https://docs.comfy.org/tutorials/image/ideogram/ideogram-v4 — officiel (ComfyUI)
[17] ComfyUI Docs — BuildJsonPromptIdeogram — https://docs.comfy.org/built-in-nodes/BuildJsonPromptIdeogram — officiel (ComfyUI)
[18] Runware — Ideogram 4.0 structured prompts — https://runware.ai/docs/models/ideogram-4-0/guides/structured-prompts — communauté (fournisseur d'API)
[19] GitHub issue #13 « Prompting documentation bug » (la bbox lève le blocage) — https://github.com/ideogram-oss/ideogram4/issues/13 — communauté
[20] GitHub issues #5 et #12 (faux positifs, bbox, qualité des personnes, dérive vers l'anime) — https://github.com/ideogram-oss/ideogram4/issues/5 , https://github.com/ideogram-oss/ideogram4/issues/12 — communauté
[21] GitHub issue #14 (mesure des blocages dans ComfyUI vs seed) — https://github.com/ideogram-oss/ideogram4/issues/14 — communauté
[22] GitHub issue #33 (contradiction : `aspect_ratio` dans v1 vs schéma) — https://github.com/ideogram-oss/ideogram4/issues/33 — communauté
[23] GitHub issue #35 (absence de transparence) — https://github.com/ideogram-oss/ideogram4/issues/35 — communauté
[24] GitHub issue #21 (cadre 16:9 pivoté) — https://github.com/ideogram-oss/ideogram4/issues/21 — communauté
[25] r/StableDiffusion « Ideogram 4 compared with Krea 2 in natural language prompting » (snapshot) — https://reddit.sentinel-team.org/posts/1ursrrv/snapshots/2026-07-09T23%3A35%3A57.68774Z — communauté
[26] invideo — Best AI model for text in images (08.2026) — https://invideo.io/blog/best-ai-model-text-in-images/ — communauté
[27] GoEnhance — Ideogram 4.0 review — https://www.goenhance.ai/blog/ideogram-4-review — communauté
[28] EvoLinkAI — awesome-ideogram-4.0-prompts — https://github.com/EvoLinkAI/awesome-ideogram-4.0-prompts — communauté
[29] ipentec — Ideogram 4.0 の画像生成結果 — https://www.ipentec.com/document/ai-image/image-generation-ideogram-4-model — communauté
[30] Hugging Face — ideogram-ai/ideogram-4-nf4 — https://huggingface.co/ideogram-ai/ideogram-4-nf4 — officiel
[31] Règles de conversation dans le Studio — prompty/proces.md — notre configuration
[32] Présentation du Studio pour les participants (suppression de l'arrière-plan dans l'espace Image) — notes internes (non publiées) — notre configuration
[33] README du Studio (modèles vidéo avec première/dernière image) — README.md — notre configuration
