<!-- Fiche modèle pour le promptmaker. modele: qwen-image-2-1 -->
# Qwen-Image 2.1 (Alibaba Qwen) — texte → image

## Ce que c'est et à quoi ça sert (y compris : ce qu'il NE fait PAS bien)
- Poids ouverts depuis le 20.09.2026, licence Qwen Research (non commerciale) ; générateur 7B (32 couches DiT single-stream), encodeur de texte Qwen3-VL 8B [1][2] (officiel), [14] (notre configuration).
- Génère nativement en 2K (par ex. 2752×1536 pour 16:9) ; un seul modèle fait la génération et l'édition [1] (officiel). L'édition a sa propre fiche (`qwen-image-edycja.md`).
- Points forts : **descriptions longues et denses** (la famille 2.0 annonce des instructions jusqu'à ~1K tokens) [9] (officiel, version 2.0), **texte dans l'image** avec mise en page et typographie (affiches, diapositives, infographies, graphiques) [1][9][11] (officiel / communauté), images avec transparence (RGBA) [1] (officiel).
- Ce qu'il NE fait PAS bien / risques :
  - mains et pieds — un fil de plaintes dédié sur HF [16] (communauté, titre du fil seulement) ;
  - « bruit, bouillie, surtraitement » avec des prompts surchargés de termes de qualité et de style [17] (communauté, sans réponse des auteurs) ;
  - texte dans des langues autres que zh/en — multilinguisme annoncé en termes généraux, **caractères accentués (é, ç, ą, ł…) non confirmés** par aucun test [9][11][18] ;
  - la taille à laquelle le Studio le lance est ~1 MP, soit environ un quart de la surface native 2K [14] (notre configuration) ; le petit texte et le détail fin peuvent en pâtir (non confirmé).

## Ce que le participant règle dans le Studio (champs, entrées, paramètres de notre YAML — et leur effet sur le prompt)
Source : `modele/obraz/qwen-image-2-1.yaml` + `workflows/obraz/qwenimage21_tekst-na-obraz.api.json` [14] (notre configuration).
- **prompt** — un seul champ. Il va dans `TextEncodeQwenImage21` (Qwen3-VL 8B). L'encodeur enveloppe le texte dans un modèle de chat avec le système « Comprehend and analyze the provided prompt. », puis retire cette partie système [3] (code ComfyUI).
- **Pas de champ de prompt négatif.** Dans le workflow, `negative_prompt` = vide, et **CFG = 1** — à CFG 1, ComfyUI saute complètement la branche négative [2][5] (officiel). Ce qui ne doit pas apparaître, tu l'écris à l'affirmative.
- **format (proportions)** — 16:9 (par défaut), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16 ; **1,0 MP** (nœud ResolutionSelector, multiple de 8). **N'écris pas le format dans le prompt** — l'extenseur officiel interdit d'inscrire format, résolution et nombre de pixels dans la description [14] (notre configuration / prompt système officiel du PE).
- **seed** — le même seed va au générateur et à l'extenseur. Seed fixe = comparaison de versions du prompt.
- **pas** (avancé) — 10–50, 25 par défaut ; sampler euler/simple. Exemples officiels : 40 pas [1] ; ComfyUI : les mains « se mettent en place » vers 30 pas, 40 pas réduisent le « fourmillement » dans les détails denses [2] (officiel).
- **« le modèle développe lui-même le prompt »** (avancé, DÉSACTIVÉ par défaut) — bascule sur un prompt réécrit par Qwen3.5 9B PE-T2I (l'extenseur officiel de Qwen) avec notre prompt système (un seul paragraphe en anglais, sans JSON), **avec mode de réflexion** (`thinking: true`, `max_length` 8192, pour que le raisonnement ne coupe pas la réponse) [14] — comme dans l'exemple officiel de la fiche du PE (`enable_thinking=True`) [6] ; les modèles par défaut de ComfyUI, après la correction du 30.09.2026, ont la réflexion désactivée [8], mais des praticiens écrivent que sans elle le PE donne des prompts plus faibles [7] (communauté). Coût : la génération dure plus longtemps (estimation +1 à 2 min de raisonnement ; non mesuré). Conclusion : **quand c'est le promptmaker qui écrit le prompt, laisse l'interrupteur désactivé** — le PE réécrira tout à sa façon (il fixera le cadrage, inventera le reste de la scène). L'activer n'a de sens que comme « montre-moi l'interprétation du modèle » pour une idée en 3 mots.

## Format du prompt (langue, longueur, structure, marqueurs, négatif, poids)
Le meilleur modèle = ce que l'extenseur officiel PE-T2I transmet au modèle. Ses règles sont dans notre workflow (nœud 459:475) [14] (notre configuration, texte fondé sur le PE officiel [6]) :
- **Langue : anglais.** Le PE écrit toujours la description en anglais, quelle que soit la langue de la demande ; exception : **le texte visible dans l'image reste dans sa langue et son alphabet** [6][14] (officiel). Qwen est le plus fort pour le texte chinois [10] (officiel, Qwen-Image 1.0), mais le participant doit pouvoir lire le prompt, donc la prose est toujours en anglais.
- **Forme : un seul paragraphe de prose continu**, au présent, à la troisième personne, en phrases déclaratives. Description de l'image finale « telle que la voit un observateur », pas une consigne (« create… », « make sure… », « you ») [14].
- **Longueur :** le PE vise **environ 20 phrases, 400–500 mots** (~25 mots par phrase) — autant pour une demande courte que longue ; un cadre dense plus long, un motif unique et calme plus court [14]. L'ancien extenseur de Qwen-Image 1.0 visait < 200 mots [12] — c'est une autre version, ne l'applique pas.
- **Ordre (selon le PE)** [14] :
  1. **phrase d'ouverture (~20 mots)** : orientation + **style** + **nom du médium** (photograph / illustration / poster / page / scene / portrait / graphic…) + sujet + fond et palette. Le médium ne doit jamais disparaître.
  2. **fond et surface** juste après l'ouverture (pas à la fin) ;
  3. **parcours du cadre** : bande supérieure → côté gauche, centre, droite → bande inférieure. Ou, quand un seul motif remplit le cadre : le fond et sa façon de s'estomper → la pose et la place dans le cadre → tête/visage → corps, chaque pièce du costume et chaque surface → ce qu'il tient/touche → les bords ;
  4. **8 à 14 indications de position** (upper-left, along the lower edge, behind the left shoulder…), qui atteignent les coins et les bords ; environ 1/3 des phrases commencent par une indication de position ;
  5. **chaque texte dans le cadre** dans l'ordre de lecture (voir plus bas) ;
  6. **une phrase à part sur la lumière** : source, direction, qualité, ombres et reflets (« The lighting is… ») ;
  7. **une phrase de clôture** sur l'ensemble : équilibre, palette, style, ambiance (« The overall composition… »). Une seule.
- **Texte dans l'image** [14][6] (officiel) :
  - mot pour mot, **entre guillemets doubles droits**, dans l'alphabet d'origine, caractère par caractère avec la ponctuation ;
  - pour chaque inscription : où elle se trouve, graisse, couleur, majuscules/minuscules, taille relative (« a bold black headline across the top reads "…" ») ;
  - décris un retour à la ligne avec des mots (« a second line reads… »), sans caractère de nouvelle ligne entre les guillemets ;
  - un texte qui ne doit pas être lisible (enseigne lointaine, petits caractères) → nomme-le « blurred / indistinct / too small to read », n'invente pas de lettres ;
  - **n'ajoute pas d'inscriptions dont le participant ne veut pas** — environ 1/3 des images n'ont aucun texte.
- **Pas d'« amplificateurs de qualité »** : « masterpiece », « 8K », « highly detailed », « award-winning » — le PE les interdit [14]. (L'exemple de la fiche HF contient « 8k », mais c'est un prompt de démonstration [1].)
- **Couleurs qualifiées** (deep navy, muted olive, warm terracotta), **le matériau plutôt que le nom seul** (coarse linen, weathered wood, paper fibre, visible brush strokes), **énumère, ne résume pas** (« several items » = erreur), petits nombres en toutes lettres, l'âge comme étape de vie/décennie, les objets par catégorie, pas par marque [14].
- **Prompt négatif :** aucun (CFG 1) [2][14]. Les contraintes à l'affirmative : « the street is empty except for… », « the background is a flat, untextured off-white ».
- **Poids `(mot:1.3)` — NON.** Le tokenizer Qwen3-VL dans ComfyUI a `disable_weights=True` : parenthèses et nombres arrivent au modèle comme du texte ordinaire [4] (code ComfyUI). Évite aussi les parenthèses comme ornement.
- **Pas de JSON, de titres, de listes, de markdown** — le PE rend un paragraphe brut ; le JSON avec `wh_ratio` n'est que le format de sortie de l'extenseur, pas l'entrée du générateur [6][14].
- **Transparence (RGBA) :** modèle officiel : commence par « This is an RGBA image with transparency. », décris le motif, termine par « The image has alpha channel and the background is transparent. » [1] (officiel). Le Studio enregistre-t-il le canal alpha dans le PNG — non confirmé.

## Squelette du prompt
```
The image is a [orientation : wide / vertical / square] [style : hand-drawn / watercolour / flat-vector / archival / cinematic…] [médium : photograph / illustration / collage / poster / page…] of [sujet], [fond et palette : 2–3 couleurs qualifiées].
[Fond et surface : de quoi il est fait, texture, à quelle distance et avec quelle netteté].
[Bande supérieure : ce qui occupe le bord supérieur]. [On the left side of the frame, … ]. [In the centre, … sujet : pose, direction du regard, apparence, chaque élément du costume avec couleur et matériau]. [On the right side, … ]. [Across the lower third / along the bottom edge, … ].
[Inscriptions, dans l'ordre de lecture : où, police/graisse, couleur, taille, reads "TEXTE EXACT"].
[Texture du médium : grain / fibre du papier / coups de pinceau / trame / salissures — concrètement, où c'est visible].
The lighting is [source], [direction], [qualité : hard/soft/flat], [ombres et reflets].
The overall composition [équilibre/symétrie], [palette], [style], [ambiance].
```

## Ce qui marche
- **Un cadre décrit spatialement** — des indications de position sur les bords et dans les coins, pas seulement au centre ; c'est le cœur du PE officiel [14].
- **Un seul mot de style dans la phrase d'ouverture** (qu'on peut répéter dans la clôture) plutôt que des adjectifs éparpillés [14].
- **Matériau et texture** donnent du concret : « matte », « brushed metal », « frosted glass », « grain », « scuffs », « paper fibre », « visible brush strokes » [14].
- **Cohérence physique** : ombres issues de la lumière, reflets conformes à la scène, échelle des objets cohérente — le PE l'exige explicitement ; les choses impossibles, décris-les telles que l'image les montre, et garde le reste de la scène cohérent [14].
- **Du concret plutôt que des généralités** : des phrases avec sujet, pose, source de lumière, référence de pellicule/d'objectif marchent mieux qu'une description générale [19] (communauté, critique d'un vendeur).
- **Pour un poème :** traduis l'ambiance en lumière, couleur, matière et disposition — le PE demande de décrire ce qui se voit et réserve l'ambiance à une seule phrase de clôture [14].
- **Seed fixe, change une chose à la fois** [2] (officiel).

## Biais et pièges
- **Dérive vers une finition « professionnelle »** : la famille 2.x se vante de « détails, textures et lumière plus photoréalistes » [9][18] (officiel). Pas de médium indiqué = le plus souvent une photographie/un rendu poli (non confirmé par un test, déduit de [9]). Nomme toujours le médium.
- **Surcharge de style** (« hyper-realistic, photorealistic detail, high contrast, dramatic volumetric lighting… » à la fois) → signalements « noisy, muddy, overprocessed » [17] (communauté). Un mot de style, une phrase de lumière.
- **Inscriptions inventées** : le modèle place volontiers enseignes et étiquettes — quand l'image doit être sans texte, ne mentionne ni enseignes, ni écrans, ni couvertures ; décris les surfaces comme lisses/vides [14].
- **Caractères accentués (é, ç, ą, ł…)** : non confirmés. Inscriptions courtes, exactes entre guillemets ; vérifie le résultat lettre par lettre, en cas d'erreur plusieurs seeds. Quand l'inscription est essentielle, envisage dans le Studio Ideogram 4 (« inscriptions dans l'image ») [15] (notre configuration).
- **CFG** : non exposé au participant. Pour info : CFG ~2 tient mieux un prompt dense et le petit texte, mais suraccentue les contours ; CFG 5 abîme, 0,5 casse l'image [2] (officiel). Réponse sur HF : en génération on peut monter le CFG et utiliser un négatif, en édition ne pas le monter [13] (communauté).
- **Nombres et ensembles d'objets** : énumère chaque élément séparément ; « quelques », « divers » = le modèle improvise [14].
- **Visages de personnes réelles / marques** : le PE décrit les objets par catégorie ; un nom de personne ou de marque seulement si le participant l'a décidé [14].

## Au-delà du photoréalisme
- **Le médium dans la première phrase, par un nom** : « illustration », « ink drawing », « watercolour painting », « collage », « poster », « page », « sheet » — la liste officielle des styles du PE comprend watercolour, hand-drawn, flat-vector, isometric, retro, minimalist, 3D-rendered [14].
- **Collage / graphisme** : l'exemple de prompt de notre workflow (modèle officiel ComfyUI) montre un vocabulaire qui fonctionne : « mixed-media graphic collage », « flat vibrant planes », « overlapping circles », « dense micro-halftone dot matrices », « vector topographic contour lines » [14]. Décris les couches du collage comme des éléments du cadre — chacune avec sa position.
- **Dessin / peinture** : décris l'outil et sa trace : « graphite hatching », « visible brush strokes », « pigment pooling at the edges », « paper fibre showing through » (vocabulaire de matériaux du PE [14] ; formules picturales précises — non confirmées par un test).
- **Pellicule / archive / grain** : décris la texture comme ce qui se voit dans l'image (grain, rayures, décolorations, bords flous), plus une phrase sur la lumière. Le vocabulaire cinéma (film stock, lens) fonctionne comme du concret [19] (communauté). Ne mélange pas avec « crisp, razor-sharp ».
- **Abstraction** : cadre divisé en régions → décris les régions (bande supérieure, gauche, centre, droite, bas) avec forme, couleur, contour et texture ; lumière « flat even ambient light » [14].
- **Animation / graphisme plat** : « flat-vector », « cel-shaded », « flat colour fills with thin outlines » ; lumière plate. N'ajoute ni objectif ni profondeur de champ.
- Conflit de registres (par ex. photo + dessin animé sans justification) — de façon consciente et décrite spatialement (« a hand-drawn figure pasted onto a black-and-white photograph »), sinon le modèle fait une moyenne.

## Mouvement / temps / son
Sans objet (image fixe). Si l'image doit être la **première image d'une vidéo** dans le Studio — règle le format comme celui de la vidéo (en général 16:9), laisse de la place pour le mouvement dans le cadre, évite le petit texte (la vidéo le rendra flou).

## À vérifier avant l'envoi
- [ ] Prose en anglais ; le texte dans le cadre dans sa langue, entre `"…"` droits, mot pour mot avec ses caractères accentués.
- [ ] Première phrase : orientation + style + **médium** + sujet + fond/palette.
- [ ] Cadre parcouru spatialement, les indications de position atteignent les coins et les bords.
- [ ] Une phrase à part sur la lumière ; une phrase de clôture.
- [ ] Absents : « masterpiece/8K/highly detailed », poids `( :1.3)`, JSON, format/résolution dans le texte, consignes « create/make sure ».
- [ ] Exclusions formulées à l'affirmative (il n'y a pas de négatif).
- [ ] Aucune inscription dont le participant ne voulait pas.
- [ ] Interrupteur « le modèle développe lui-même le prompt » — recommande DÉSACTIVÉ quand le prompt est déjà complet.
- [ ] ~250–500 mots ; moins pour un seul motif calme.

## Sources
[1] Qwen/Qwen-Image-2.1 — fiche modèle — https://huggingface.co/Qwen/Qwen-Image-2.1 — officiel
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — officiel (ComfyUI)
[3] ComfyUI — comfy/text_encoders/qwen_image21.py (modèle de chat de l'encodeur) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — officiel (code)
[4] ComfyUI — comfy/text_encoders/qwen3vl.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — officiel (code)
[5] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21 : négatif, resolution) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — officiel (code)
[6] Qwen/Qwen-Image-2.1-PE-T2I — fiche de l'extenseur — https://huggingface.co/Qwen/Qwen-Image-2.1-PE-T2I — officiel
[7] ComfyUI Wiki — Qwen-Image 2.1 Prompt Enhancer Models Run in ComfyUI — https://comfyui-wiki.com/en/news/2026-09-22-qwen-image-2-1-prompt-enhancer — communauté
[8] Comfy-Org/docs PR #1843 — correct the Qwen Image 2.1 prompt enhancer defaults — https://github.com/Comfy-Org/docs/pull/1843 — officiel (ComfyUI)
[9] Qwen-Image-2.0 Technical Report (arXiv 2605.10730) — https://arxiv.org/abs/2605.10730 — officiel (version 2.0)
[10] QwenLM/Qwen-Image — README (versions antérieures, recommandations PE) — https://github.com/QwenLM/Qwen-Image — officiel
[11] Qwen-Image: Crafting with Native Text Rendering (blog 1.0) — https://qwenlm.github.io/blog/qwen-image/ — officiel (version 1.0)
[12] QwenLM/Qwen-Image — src/examples/tools/prompt_utils.py (extenseur 1.0, < 200 mots) — https://github.com/QwenLM/Qwen-Image/blob/main/src/examples/tools/prompt_utils.py — officiel (version 1.0)
[13] Discussion HF #14 — CFG et négatif dans le code par défaut — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/14 — communauté
[14] Notre configuration : modele/obraz/qwen-image-2-1.yaml ; workflows/obraz/qwenimage21_tekst-na-obraz.api.json (nœuds 459:452, 459:458, 459:471, 459:474, 459:475 = prompt système du PE) — notre configuration
[15] Notre configuration : notes internes (non publiées) (Ideogram 4 pour les inscriptions) — notre configuration
[16] Discussion HF #29 — 手脚的问题就解决不了了? (mains et pieds) — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/29 — communauté
[17] Discussion HF #56 — Qwen 2.1 image quality issue — noisy and muddy results — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/56 — communauté
[18] eesel — Qwen Image 2.1 review — https://www.eesel.ai/blog/qwen-image-2-1-review — communauté
[19] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — communauté (vendeur)
