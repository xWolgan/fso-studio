<!-- Fiche modèle pour le promptmaker. modele: z-image-turbo -->
# Z-Image Turbo (Tongyi-MAI / Alibaba) — texte → image rapide

## Ce que c'est et à quoi ça sert (y compris : ce qu'il NE fait PAS bien)
- Modèle 6B (single-stream DiT, S3-DiT), version **distillée sur 8 pas**, sans CFG ; Apache 2.0 [1][4] (officiel). Encodeur de texte : Qwen3 4B [5] (notre configuration).
- Dans le Studio : **quelques secondes par image — pour chercher une direction et faire des esquisses** [5] (notre configuration). Pour la qualité finale, du texte dense et une composition difficile, compare avec Qwen-Image 2.1.
- Points forts : photoréalisme et esthétique (le distillat dépasse souvent l'enseignant à 100 pas dans l'évaluation de la qualité) [4] (officiel), **texte bilingue dans l'image : chinois et anglais** [1][4] (officiel).
- Ce qu'il NE fait PAS bien :
  - **faible diversité** — tableau officiel : Turbo « diversity: low » ; dans OneIG, diversité 0,139 vs 0,194 pour le modèle de base [1][4] (officiel). Changer le seed donne souvent une image très semblable [10] (communauté) ;
  - **le style** : Turbo « excels in photorealistic image generation », alors que la fiche attribue la « wide range of artistic styles » au modèle de base Z-Image [1] (officiel) ; le score OneIG-Style est un peu plus bas que celui de la base [4] ;
  - connaissance du monde, compréhension de l'intention, raisonnement complexe — limités (c'est ce qu'ils disent officiellement du 6B sans extenseur) [4] ;
  - **le négatif ne fonctionne pas du tout** [2] (officiel) ;
  - le texte dans d'autres langues que zh/en — caractères accentués (polonais, français, etc.) **non confirmés**.

## Ce que le participant règle dans le Studio (champs, entrées, paramètres de notre YAML — et leur effet sur le prompt)
Source : `modele/obraz/z-image-turbo.yaml` + `workflows/obraz/zimage-turbo_tekst-na-obraz.api.json` [5] (notre configuration).
- **prompt** — un seul champ → `CLIPTextEncode` avec l'encodeur Qwen3 4B. ComfyUI l'enveloppe dans un gabarit de chat `<|im_start|>user … <|im_end|><|im_start|>assistant`, **sans prompt système et sans extenseur** [6] (code ComfyUI). Personne ne corrigera le prompt en route — tu l'écris directement sous forme « étendue ».
- **Pas de négatif** : la branche négative est un `ConditioningZeroOut`, CFG 1 [5]. Officiellement : le modèle n'utilise pas de prompts négatifs [2].
- **Pas de troncature** : le code officiel de diffusers tronque le texte à 512 tokens (ils recommandent de monter à 1024) [2], mais le tokenizer de ComfyUI n'a pas cette limite [6] (code). Un long prompt arrivera en entier.
- **format (proportions)** — 16:9 (par défaut), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16 ; env. **1 MP**, dimensions ×16 [5]. Taille native de la démo : 1024×1024 [1].
- **seed** — avec une faible diversité, c'est un levier faible ; les changements passent par **le contenu du prompt** [1][10].
- **pas** (avancé) — 4–16, 8 par défaut (sampler res_multistep, shift 3) [5]. Officiellement 9 dans diffusers = 8 passes DiT [1] ; praticiens : 8–12, davantage seulement s'il reste du bruit [9] (communauté). Moins de pas = esquisse.

## Format du prompt (langue, longueur, structure, balises, négatif, poids)
- **Langue : anglais** (ou chinois). Entraînement sur des descriptions bilingues zh/en [4] (officiel) ; aucune preuve que le chinois donne une meilleure image [7] (communauté). Le participant doit pouvoir lire le prompt → anglais. La langue du participant (si ce n'est pas l'anglais) — non.
- **Une description longue et détaillée.** Officiellement : « works best with long and detailed prompts » [2]. Praticiens : 80–250 mots comme juste milieu, « des centaines de mots, ça va » [9] (communauté). La thèse d'une « dérive de l'attention après 75–100 tokens » [8] contredit la recommandation officielle — ignore-la.
- **Registre : description factuelle, objective**, pas de poésie. Les longues descriptions d'entraînement ont été écrites dans un « plain and objective linguistic style » [4] (officiel), et le fine-tuning (SFT) a été fait sur des prompts passés par l'extenseur officiel PE [4] — le modèle comprend donc le mieux les prompts dans le style de cet extenseur.
- **Règles de l'extenseur officiel (pe.py)** [3] (officiel, original en chinois) :
  1. verrouille les éléments intangibles : sujet, nombre, action, état, noms, couleurs, textes ;
  2. si la demande exige une idée (« conçois… », « montre comment… ») — invente d'abord une solution concrète et visible, puis décris-la ;
  3. ajoute des détails professionnels : **composition, lumière et atmosphère lumineuse, matériau/texture, schéma de couleurs, plans de l'espace** ;
  4. **texte à rendre — littéralement, entre guillemets doubles anglais `"…"`** ; pour une affiche/un menu/une UI, décris tout le texte, la police et la mise en page ; pour une enseigne/un écran : contenu, position, taille, matériau ;
  5. **interdiction des métaphores et de la rhétorique émotionnelle**, interdiction des méta-tags (« 8K », « masterpiece ») et des ordres de dessin.
- **Prose, phrases complètes, pas de liste de tags** ; les boosters de l'ère SD (« masterpiece, best quality, trending on artstation ») n'apportent rien [3][11] (officiel / communauté).
- **Négatif** : tout en positif — « sharp focus » au lieu de « no blur », « empty street, only wet cobblestones » au lieu de « no people » [2][12] (officiel / communauté).
- **Poids `(mot:1.3)` — NON.** Le tokenizer de Z-Image dans ComfyUI a `disable_weights=True` — les parenthèses et les nombres arrivent au modèle comme du texte [6] (code).
- **Ne mélange pas des styles contradictoires** (photoréalisme + dessin animé + peinture à l'huile) [11][12] (communauté).

## Squelette du prompt
```
[médium et style : photograph / ink drawing / watercolour painting / collage… + 1 précision de technique]. [valeur de plan et angle : wide shot / close-up, eye level / high angle], [composition : où se trouve le sujet dans le cadre].
[sujet : qui/quoi, combien, âge comme étape de la vie, 2–3 traits d'apparence], [vêtements/surface : couleur + matériau], [action ou état].
[environnement : 2–3 éléments concrets avec leur position ; premier plan / arrière-plan].
[lumière : source, direction, qualité, moment de la journée], [palette : 2–3 couleurs avec une précision].
[texture de l'image : grain / coups de pinceau / fibre du papier / trame — le cas échéant] ; [pour la photo : UN appareil ou objectif + UNE pellicule].
[texte dans le cadre : où, quelle police, reads "TEXTE EXACT" — ou rien].
[contraintes en positif : only one figure in the frame / plain untextured background].
```

## Ce qui marche
- **Le langage du chef opérateur** : valeur de plan, angle, disposition, lumière — le modèle y réagit fortement [9][12] (communauté).
- **Du concret plutôt que des adjectifs de jugement** : « beautiful », « nice », « epic » n'apportent rien [11][12] (communauté) ; le PE officiel demande de traduire l'intention en faits visibles [3].
- **Un vocabulaire photographique plutôt que « realistic »** : un appareil/objectif précis et une pellicule (p. ex. « Kodak Portra 400 », « Ilford HP5 »), la texture de la peau (« visible pores, slight asymmetry ») — attribué à un photographe de r/StableDiffusion [11] (communauté). Au maximum **une** formule d'appareil et **une** de pellicule/lumière — davantage dilue l'effet [11].
- **Un rôle + 2–3 traits** plutôt qu'un seul mot « connoté » (« CEO », « witch » tirent vers un stéréotype de genre, de corps, de maquillage) [9] (communauté). Au lieu de « businessman » → « office worker » + traits.
- **Un arrière-plan simple, non encombré**, quand c'est le sujet qui compte [9].
- **Texte dans le cadre** : court, entre guillemets, avec emplacement et police ; tôt dans le prompt ; une seule langue par inscription ; ajoute « no other text in the image » sous forme positive (« the rest of the wall is blank ») [3][9][11].
- **Variations** : change le contenu du prompt (cadre, angle, moment, disposition), pas seulement le seed — le distillat revient à la même composition [1][10]. Prompt plus court = plus de liberté de composition, prompt long = ancre la composition [10] (communauté, dans le contexte d'une LoRA de diversité).
- **Seed fixe lors des retouches**, une seule chose changée à la fois [9].

## Biais et pièges
- **Par défaut, « photo de stock beauté »** : visages lisses, symétriques, brillance — quand il n'y a ni appareil, ni pellicule, ni imperfections [11] (communauté). Entraînement avec récompense notamment pour l'« AI-content detection perception » (réalisme, « ne ressemble pas à de l'IA ») et l'esthétique [4] (officiel) — le modèle tire vers un réalisme poli.
- **Faible diversité** : seeds successifs ≈ même cadre, même visage [1][4][10]. Si le participant veut une série — décris chaque variante différemment.
- **Personnes** : précise l'âge, la corpulence, l'origine, les vêtements ; ne laisse pas cela au modèle (mots connotés → stéréotype) [9]. Le modèle a-t-il une ethnicité de visage par défaut — **non confirmé** (les exemples de la fiche HF montrent des personnages chinois [1]).
- **« Plastique »** = généralement absence de mots sur la texture (pores, tissage du tissu, grain, coups de pinceau) [11] (communauté).
- **Surcharge** par une liste de détails et des consignes contradictoires → chaos [12] (communauté).
- **Caractères accentués dans les textes** (polonais, français, etc.) : non confirmé (officiellement uniquement zh/en) [1][4]. Fais court, vérifie le résultat ; textes essentiels → Ideogram 4 ou Qwen-Image 2.1 dans le Studio [13] (notre configuration).
- **Pas** : avec trop de pas, les distillats sont parfois brûlés/pleins d'artefacts (non confirmé pour nos 4–16) ; reste à 8.

## Au-delà du photoréalisme
- Turbo est un modèle orienté photoréalisme [1] — le style doit être **imposé avec constance** : le médium dans les premiers mots, la trace de l'outil dans la description, **zéro vocabulaire d'appareil** (objectif, ouverture, « shot on… », pellicule) pour le dessin/la peinture — sinon la photo revient [11][12] (communauté, déduit de l'interdiction de mélanger les styles).
- Formules tirées des presets de praticiens (non confirmées de façon contrôlée) [11] (communauté) :
  - aquarelle : « watercolor painting, loose brushwork, pigment pooling » ;
  - bande dessinée : « western comic book style, strong inked outlines, bold graphic look » ;
  - argentique : « analog film photograph, grainy texture, warm tonal shifts, slight vignette » ;
  - anime : « anime artwork, studio anime key visual » ; manga avec trame ; pixel art ; vitrail ; art déco.
- **Le pixel art**, le modèle sait le faire de base (la LoRA ne fait qu'ajouter du détail) [14] (communauté).
- La multitude de LoRA de style (anime, « artist style ») sur Civitai pour Turbo [15] (communauté) suggère que les styles purement illustratifs sans LoRA sont plus faibles ; le Studio n'expose pas de LoRA ici [5].
- **Bande / grain / archives** : une pellicule + description des traces visibles (grain, décolorations, rayures, vignettage) ; c'est le registre où Turbo est le plus sûr [11].
- **Abstraction / collage** : décris de façon factuelle les formes, les bords, les aplats de couleur, la texture du papier et leur position ; sans métaphores (le PE les interdit [3]). Effet — non confirmé par un test ; si ça ne marche pas, passe à Qwen-Image 2.1.
- **L'ambiance d'un poème** — traduis-la en lumière, palette, cadre et matière — une métaphore directe sera ignorée ou dessinée littéralement [3].

## Mouvement / temps / son
Sans objet. Esquisse pour la première image d'une vidéo : format comme la vidéo (16:9), composition simple, place pour le mouvement ; une fois la direction choisie, fais la version finale dans Qwen-Image 2.1.

## Vérifie avant d'envoyer
- [ ] Anglais, phrases complètes, factuel — sans métaphores ni jugements (« beautiful », « epic »).
- [ ] Médium/style au début ; hors photo, zéro mot sur l'appareil et la pellicule.
- [ ] Valeur de plan, angle, disposition, lumière (source + direction), palette, texture.
- [ ] Personnes : âge, corpulence, vêtements, traits explicites ; sans étiquettes connotées.
- [ ] Textes courts, entre `"…"`, avec emplacement et police — ou aucun.
- [ ] Absents : négatifs (« no… »), poids `( :1.3)`, « masterpiece/8K », listes de tags.
- [ ] ~80–250 mots.
- [ ] Variante = autre description, pas seulement un autre seed.

## Sources
[1] Tongyi-MAI/Z-Image-Turbo — fiche modèle — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo — officiel
[2] Tongyi-MAI/Z-Image-Turbo — discussion #8 « PROMPTING GUIDE » (épinglée, réponses des auteurs) — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8 — officiel
[3] Tongyi-MAI Space — pe.py (gabarit de l'extenseur de prompt) — https://huggingface.co/spaces/Tongyi-MAI/Z-Image-Turbo/blob/main/pe.py — officiel
[4] Z-Image: An Efficient Image Generation Foundation Model with Single-Stream Diffusion Transformer (arXiv 2511.22699) — https://arxiv.org/abs/2511.22699 — officiel
[5] Notre configuration : modele/obraz/z-image-turbo.yaml ; workflows/obraz/zimage-turbo_tekst-na-obraz.api.json (Qwen3 4B, CFG 1, res_multistep, shift 3, ConditioningZeroOut) — notre configuration
[6] ComfyUI — comfy/text_encoders/z_image.py (gabarit de chat, `disable_weights=True`, pas de limite de longueur) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/z_image.py — officiel (code)
[7] Résultats de recherche : Chinese vs English prompt (pas de comparaison contrôlée) — https://aioz.network/blog/z-image-turbo-a-bilingual-image-generation-model-for-text-rich-visuals-2 — communauté
[8] Fliki — thèse de la dérive après 75–100 tokens (voir [11]) — https://fliki.ai/blog/z-image-turbo-prompting-guide — communauté
[9] illuminatianon — Z-Image-Turbo Prompting Guide (gist + commentaires) — https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32 — communauté
[10] Floyo — Z-Image Turbo Text to Image With Diversity LoRA — https://www.floyo.ai/workflows/z-image-turbo-text-to-image-with-div-efye86mk80ax — communauté
[11] Fliki — Z-Image Turbo Prompting Guide: 25 Style Presets, Realism Secrets — https://fliki.ai/blog/z-image-turbo-prompting-guide — communauté (vendeur, cite r/StableDiffusion)
[12] fal — Z-Image Turbo prompt guide — https://fal.ai/learn/devs/z-image-turbo-prompt-guide — communauté (vendeur)
[13] Notre configuration : notes internes (non publiées) (Ideogram 4 pour les textes), modele/obraz/ — notre configuration
[14] elusarca — pixel art style LoRA for Z-Image Turbo — https://huggingface.co/reverentelusarca/elusarca-pixel-art-style-lora-zimage-turbo — communauté
[15] Civitai — Anime Style Lora For Z-Image-Turbo — https://civitai.com/models/2186181/anime-style-lora-for-z-image-turbo — communauté
