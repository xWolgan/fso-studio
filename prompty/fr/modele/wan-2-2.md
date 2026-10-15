<!-- Fiche modèle pour le promptmaker. modele: wan-2-2, wan-2-2-tekst, wan-2-2-obraz, wan-2-2-klatki -->
# WAN 2.2 (Alibaba Wan-AI, 14B MoE) — vidéo sans son

## Ce que c'est et à quoi ça sert
- Modèle vidéo ouvert (Apache 2.0) dans trois modes du Studio : **texte → vidéo** (T2V-A14B), **image → vidéo** (I2V-A14B), **première + dernière image** (le même I2V-A14B, nœud `WanFirstLastFrameToVideo`) [1][2][3].
- Deux « experts » : high-noise construit la composition et le mouvement au début du débruitage, low-noise affine le détail [3] (officiel). C'est pourquoi le mouvement et le cadre dépendent de ce que le prompt dit clairement et en premier.
- Wan 2.2 a été entraîné sur des données esthétiques étiquetées par **lumière, composition, contraste, tonalité colorimétrique** — il réagit au vocabulaire du chef opérateur [3] (officiel).
- Points forts : mouvement fluide d'une seule action, mouvements de caméra lisibles, vocabulaire de la lumière et du cadre, stylisations « matérielles » (feutre, pâte à modeler, marionnettes, stop-motion, pixel, dessin au trait) — les exemples de stylisation du guide d'Alibaba sont justement faits avec Wan 2.2 [7] (officiel).
- **Ce qu'il NE fait PAS bien :**
  - le son — pas du tout (le son n'arrive qu'avec Wan 2.5+, fermés) [1][7] ;
  - plusieurs événements dans un même clip, montage à l'intérieur du clip, longues chorégraphies — un plan = une action continue [7] (officiel), [19] (communauté) ;
  - texte lisible dans le cadre (il sort approximatif) [7] (officiel) ;
  - mouvement très rapide et brusque — artefacts, surtout en mode rapide [8] (officiel), [17] (communauté) ;
  - durées au-delà de ~5 s (81 images) — voir « Mouvement / temps » [5][21] ;
  - rotations complètes de caméra à 360° en 5 s — souvent ignorées ; garder l'orbite dans un arc < 45° [7] (officiel), [15] (communauté).

## Ce que le participant règle dans le Studio
Une seule entrée « WAN 2.2 » ; la variante se choisit d'elle-même selon les images fournies [1] (notre configuration) :
- **aucune image** → texte → vidéo (`wan-2-2-tekst`) ;
- **première image** → image → vidéo (`wan-2-2-obraz`) ;
- **première + dernière image** → transition entre elles (`wan-2-2-klatki`).

Champs :
- **prompt** — UN SEUL champ, envoyé directement à l'encodeur umT5-XXL (`CLIPTextEncode`), sans extension du prompt par un LLM (le dépôt officiel recommande la « prompt extension » — nous ne l'avons pas, donc c'est toi qui écris le prompt dans un style étendu) [2][3] (notre configuration / officiel).
- **Pas de champ de negative prompt.** Le négatif est inscrit en dur dans le workflow — le négatif par défaut de Wan, dans la traduction anglaise officielle du README de Wan2.1 (« Bright tones, overexposed, static, … walking backwards » ; en T2V s'y ajoutent « nudity, NSFW ») [2][6]. Tout ce qui NE doit PAS apparaître, écris-le dans le prompt comme une contrainte positive (voir plus bas).
- **format (proportions)** — 16:9 (par défaut), 4:3, 1:1, 3:4, 9:16 ; env. 0,4 MP (p. ex. 16:9 ≈ 848×480 = 480p, dimensions ×16) [1]. 480p est la résolution à laquelle le modèle est officiellement pris en charge [3]. Cadre vertical : en mode rapide, le mouvement est parfois encore plus faible (signalement isolé) [9] (communauté).
- **durée** — 1–8 s, 5 s par défaut ; 16 images/s ; T2V/I2V par pas de 0,5 s (images 16n+1), « première + dernière image » par pas de 0,25 s (4n+1) [1]. Nativement 81 images = 5 s [5] (officiel).
- **mode** :
  - **rapide** (par défaut) — LoRA lightx2v 4 pas, CFG 1, env. 30 s → **le négatif ne fonctionne pas** (avec CFG 1, ComfyUI saute la branche négative) [2][11][12] ;
  - **qualité** — 20 pas, CFG 3,5 (première + dernière image : CFG 4, shift 8), env. 3,5 min → le négatif fonctionne [1][2].
- **seed** — un seed fixe pour comparer des versions du prompt (change une seule chose à la fois) [12][19] (communauté).

Effet sur le prompt : en image → vidéo et en première + dernière image, **l'apparence et le style viennent de l'image**, le prompt décrit le mouvement. En T2V, le prompt porte tout.

## Format du prompt
- **Langue : anglais.** Le modèle est bilingue zh/en (umT5) ; les exemples officiels et l'extenseur I2V officiel écrivent toujours en anglais [3][4] (officiel). Les autres langues (y compris celle du participant) ne sont pas des langues d'entraînement (on ne sait pas comment il réagit — ne prends pas le risque). Le chinois n'est recommandé que pour le modèle **Wan 2.1 FLF2V** (« entraîné surtout sur des paires chinoises ») [6] — c'est un AUTRE modèle que notre mode première + dernière image (chez nous Wan 2.2 I2V), donc sans objet ; de toute façon, le participant doit pouvoir lire le prompt.
- **Prose, phrases complètes, présent.** Pas de listes de tags façon SD, pas de JSON, pas de balises de section.
- **Longueur :**
  - T2V : env. 60–120 mots (extenseur officiel : « 60–200 », exemples ~60–90 mots) [4] (officiel) ; praticiens : 80–120 mots [15][16] (communauté) ; un autre : 25–80 [17] — retiens **~60–110**.
  - Image → vidéo / première + dernière image : **≤ 100 mots**, seulement le mouvement [4] (officiel). Souvent 1–3 phrases suffisent.
  - Limite de l'encodeur dans le code d'origine : 512 tokens [5] ; ComfyUI ne tronque pas [13] — des prompts plus longs n'aident pas pour autant.
- **Formule officielle (Alibaba)** [7] :
  - de base : Sujet + Scène + Mouvement ;
  - avancée : Sujet (description) + Scène (description) + Mouvement (description : amplitude, tempo, effet) + Contrôle esthétique (source de lumière, type de lumière, valeur de plan, angle, objectif, mouvement de caméra) + Stylisation ;
  - image → vidéo : **Mouvement + Mouvement de caméra** (l'image définit le sujet, la scène et le style).
- **Ordre selon l'extenseur T2V officiel** [4] (officiel) :
  1. s'il y a un style non cinématographique — **le style tout au début** ;
  2. puis jusqu'à **4** tags esthétiques courts séparés par des virgules (moment de la journée, source de lumière, douceur, angle de la lumière, tonalité, valeur de plan, angle de caméra, composition), terminés par un point ;
  3. puis 2–4 phrases : sujet avec son apparence → action pas à pas → arrière-plan et son mouvement.
  Attention : pour les styles 2D/illustration, l'extenseur officiel **n'ajoute pas** de termes cinématographiques (lumière, objectif) [4].
- Le modèle accorde plus de poids au **début du prompt** ; les détails de la fin sont parfois ignorés (communauté, non testé de façon contrôlée) [17]. L'essentiel — en tête.
- **Pas de « littérature ».** L'extenseur officiel interdit les descriptions d'ambiance et d'atmosphère (« plein de tension », « climat mélancolique ») [4]. Traduis l'ambiance d'un poème en lumière, couleur, tempo, cadre, matière.
- **Negative prompt :** il n'existe pas dans le champ du participant. Écris les exclusions positivement : « only one person in the frame », « the camera stays fixed », « she remains seated » [12] (communauté).
- **Poids `(mot:1.3)` — NE les utilise PAS.** ComfyUI analyse les parenthèses aussi pour umT5 (parenthèse = poids 1,1, la parenthèse disparaît du texte) [13] (code), mais rien ne confirme que cela améliore quoi que ce soit dans Wan. Conséquence : **n'utilise pas du tout de parenthèses** (elles se transforment en poids). Les incises — avec une virgule.
- Les guillemets pour du texte dans le cadre — seulement quand le texte est indispensable ; il sortira de toute façon approximatif [7].

## Squelette du prompt
Texte → vidéo :
```
[style / médium / technique — seulement si non photographique]. [moment de la journée], [source et type de lumière], [tonalité], [valeur de plan], [angle ou composition]. [sujet : qui/quoi, combien, 2–3 traits d'apparence, matériau]. [action : un seul mouvement décomposé pas à pas, avec tempo : slowly/quickly/gradually]. [mouvement de caméra : un seul, avec direction et tempo — ou « The camera stays fixed. »]. [arrière-plan : 1–2 éléments et leur mouvement : vent, eau, fumée, lumière]. [texture de l'image : grain / papier / peinture — le cas échéant]. [contrainte positive : ce qui ne doit pas apparaître, p. ex. un seul personnage].
```
Image → vidéo :
```
[mouvement de caméra avec tempo, ou « Static camera. »]. [sujet visible sur l'image, nommé brièvement] [action pas à pas avec tempo et état final : « until … »]. [mouvement du second plan]. [ce qui reste immobile].
```
Première + dernière image :
```
[mouvement de caméra menant du cadre A au cadre B]. [ce qui se passe entre les deux : une seule transformation / une seule transition, dans l'ordre]. [tempo : gradually / smoothly / suddenly]. [élément commun aux deux images, qui doit rester stable].
```

## Ce qui marche
- **Vocabulaire esthétique de l'extenseur officiel** (à copier tel quel) [4] :
  - moment : Day time, Night time, Dawn time, Sunrise time ;
  - source : Daylight, Artificial lighting, Moonlight, Practical lighting, Firelight, Fluorescent lighting, Overcast lighting, Sunny lighting ;
  - douceur : Soft lighting, Hard lighting ; angle de la lumière : Top lighting, Side lighting, Underlighting, Edge lighting ;
  - tonalité : Warm colors, Cool colors, Mixed colors ;
  - valeur de plan : Extreme close-up shot, Close-up shot, Medium close-up shot, Medium shot, Medium wide shot, Wide shot, Extreme wide shot ;
  - angle : Over-the-shoulder shot, Low angle shot, High angle shot, Dutch angle shot, Aerial shot, Overhead shot (à omettre si tu décris un mouvement de caméra) ;
  - composition : Center composition, Balanced composition, Left-heavy / Right-heavy composition, Symmetrical composition, Short-side composition.
- En plus, d'après le guide d'Alibaba [7] : High contrast / Low contrast, Low saturation / High saturation, Golden hour sunlight, Rim light, Backlight, Long-focus lens, Wide-angle lens, Ultra-wide-angle fisheye, Tilt-shift lens, Establishing shot, Clean single shot.
- **Mouvement de caméra** — mots du guide [7] : camera pushes in / pulls out, camera moves left/right, camera moves forward, camera tilts up, camera pans, tracking shot, orbiting camera movement (arc < 45°), drone shot, **fixed camera**. Sens selon Alibaba : travelling avant = proximité/tension, travelling arrière = échelle/solitude, travelling d'accompagnement = accompagner, orbite = poids du personnage, caméra fixe = concentration [7].
- **Nomme toujours la caméra** — y compris « static camera / fixed camera ». Sans cela, le modèle ajoute sa propre dérive ou un léger travelling avant (deux guides indépendants, non testé de façon contrôlée) [17][19].
- **Un mouvement de caméra + une action.** Combiner dolly + tilt a échoué lors d'un test ; le modèle favorise le premier mouvement et éteint les suivants [15] (communauté). Le mouvement le plus important — en premier.
- **Le mouvement décrit comme un processus** : amplitude + tempo + effet (« slowly lifts her hand, the sleeve slides down ») [4][7] (officiel). Adverbes de tempo : slowly, quickly, gradually, suddenly [7].
- **Le mouvement de l'arrière-plan** (vent dans l'herbe, nuages qui passent, fumée) — l'extenseur officiel l'ajoute quand la scène est statique [4].
- **L'état final** du mouvement (« until the door is fully open ») limite la dérive en fin de clip [19] (communauté).
- **Image → vidéo : ne décris pas ce qu'on voit.** L'extenseur I2V officiel supprime les descriptions statiques et ne garde que le mouvement ; l'erreur la plus fréquente est un prompt écrit comme pour un générateur d'images [4] (officiel), [19] (communauté).
- **Première + dernière image :** le prompt doit convenir aux deux images [14] (officiel ComfyUI) ; décris la transition, pas les cadres eux-mêmes.
- Profondeur : oppose le mouvement du premier plan à un arrière-plan immobile (ou l'inverse) [16][18] (communauté).
- Ciel : l'extenseur officiel remplace tout ciel par « clear blue sky », « pour éviter la surexposition » [4] — indice qu'un ciel clair se brûle facilement ; pour les extérieurs lumineux, envisage low contrast / overcast.

## Biais et pièges
- **Mode rapide (lightx2v) = tempo ralenti.** L'équipe lightx2v le reconnaît : mouvement plus lent que dans le modèle de base [9] ; les workflows ComfyUI par défaut avec cette LoRA « transforment les scènes en slow motion » [10] ; la LoRA change aussi le style [9] (communauté), avec un très grand mouvement elle produit des artefacts et peut inverser le sens de marche des véhicules [8] (officiel). Contournement par le prompt : verbes et tempo explicites (« quickly », « briskly »), moins d'éléments en mouvement. Quand le tempo est crucial → mode qualité.
- **Le négatif (mode qualité uniquement) travaille contre la stylisation.** Le négatif par défaut (chez nous en anglais, traduction officielle du README de Wan 2.1) contient entre autres « style, works, paintings, images » et « static, still picture » [5][6]. Conclusion (non confirmée par un test) : en mode qualité, le pictural/« l'œuvre » est légèrement repoussé, et l'immobilité totale pénalisée. Pour les styles non photographiques, **nomme la technique plus fortement** et compare les deux modes sur le même seed.
- **Attraction vers le réalisme** — les auteurs d'une LoRA anime parlent du « fort biais de Wan 2.2 vers des générations réalistes » et de l'insertion d'une esthétique 3D [20] (communauté). Le style doit être placé au début et répété dans la description de la texture.
- **Esthétique « propre » par défaut** — sans indications de texture, l'image sort lisse et uniformément éclairée ; le grain, le flou de mouvement et la lumière de la scène doivent être nommés [17] (communauté, non testé).
- **N'ajoute pas de sujets** — l'extenseur officiel interdit d'ajouter des personnages absents (p. ex. des gens dans un paysage) [4]. Un paysage sans personne s'écrit « no people, empty … ».
- **Jour par défaut** — l'extenseur officiel choisit « Day time » quand le prompt ne dit rien d'autre [4] ; ne laisse pas la nuit ou l'aube à la devinette.
- **Nombre de personnages** — indique le nombre ; plusieurs personnages et leurs interactions sont un risque [18] (communauté). Le négatif contient « many people in the background, three legs, walking backwards » [6] — ce sont des faiblesses connues.
- **Plans contradictoires** (close-up + wide shot en un) gâchent le résultat [17] ; les mouvements contradictoires aussi [18].
- **Transformations extrêmes** (jour → nuit en 5 s, plusieurs métamorphoses) — mal [18] (communauté). En première + dernière image : une seule transformation.
- **Les parenthèses** disparaissent et changent les poids [13] — voir « Format ».
- Personnes réelles nommées — à éviter [7] (officiel).
- Divergences entre guides : certains parlent de « 24 fps » — cela concerne le modèle **TI2V-5B** [3] ; notre 14B tourne à 16 images/s [5]. Les formules de son, de plans multiples (« Shot 1 [0–3 s] »), « Image 1 » — c'est **Wan 2.5–3.0**, pas 2.2 [7]. Ne les transpose pas.

## Au-delà du photoréalisme
- Stylisations officiellement citées (exemples faits avec Wan 2.2) [7] : **felt style, 3D cartoon style, pixel style / 8-bit, puppet animation, claymation style, black and white animation, stop-motion animation, line art illustration**, surreal style ; effets : **tilt-shift photography, time-lapse photography**, bokeh ; dans les exemples : **VHS glitch aesthetic, CRT scanline effect** [7].
- Exemple officiel de style 2D tiré de l'extenseur : nom de la technique au début + description du trait et de l'ombrage à la fin (« smooth linework », « cel-shaded »), **sans** termes de lumière cinématographique [4]. Applique ce modèle au dessin, à la gouache, à la linogravure, au papier découpé : technique → contenu → description de la trace de l'outil (trait, tache, texture du papier).
- Aquarelle, encre, huile, collage, papier découpé — **non cités** dans les documents officiels ; efficacité inconnue (non confirmé). Décris en termes matériels : papier, pigment, bord, couches.
- Bande / archives : les praticiens utilisent « 16mm grain », « 35mm film grain », « high contrast black and white », « bleach-bypass », « kodak portra » [16] (communauté, sans tests comparatifs). Pour l'effet d'archive, ajoute l'époque et le support (p. ex. « 1960s 16mm footage, scratches ») — effet non confirmé.
- Abstraction : le modèle veut un sujet et une action ; décris l'abstraction comme de la matière en mouvement (fumée, encre dans l'eau, lumière à travers le verre) avec une caméra (non confirmé — déduit de la formule Sujet+Scène+Mouvement [7]).
- **La voie la plus sûre vers le non-photoréalisme : image → vidéo ou première + dernière image** avec une image dans la technique visée (faite avec un autre modèle / à la main). Le style vient de l'image, le prompt ne donne que le mouvement [4][19]. Nomme quand même une fois la technique dans le prompt (p. ex. « the charcoal drawing comes alive… »), pour que le modèle ne la « réalise » pas [20] (communauté).
- Mouvement dans les stylisations : « stop-motion » suggère un mouvement saccadé, « hand-drawn animation » — un rythme image par image ; à 16 images/s et en mode rapide, l'effet est parfois fluide et lent (non confirmé).

## Mouvement / temps / son
- **Pas de son.** N'écris ni dialogues, ni musique, ni descriptions sonores — le modèle ne les générera pas, et les mots prennent de la place [1]. La bouche d'un personnage qui parle peut bouger (« speaks ») sans voix [4].
- **Durée :** 5 s (81 images à 16 images/s) est le maximum natif [1][5]. Le Studio autorise jusqu'à 8 s, mais au-delà d'~81 images l'action a tendance à revenir à l'état initial (signalements d'utilisateurs) [21] (communauté). Plan plus long = plusieurs clips (dernière image → première du suivant, ou mode première + dernière image) [21].
- En 5 s tiennent **un mouvement de caméra + une action du sujet** [19] (communauté) ; un clip plus court = encore moins.
- **Tempo :** les mots de tempo fonctionnent (slowly/quickly, slow-motion, time-lapse) [7][16] ; en mode rapide, l'ensemble ralentit de toute façon [9][10].
- Ordre des phrases = ordre des événements : d'abord le cadre d'ouverture, puis le mouvement de caméra, puis la « révélation » [15][16] (communauté).

## Vérifie avant d'envoyer
- [ ] En anglais, en prose, sans parenthèses, sans poids, sans tags de section.
- [ ] T2V ~60–110 mots ; image / première + dernière image ≤ 100 mots et **seulement le mouvement** (tu ne décris pas ce qu'on voit).
- [ ] Style non photographique — tout au début, et texture/trait répétés.
- [ ] L'essentiel au début ; 4 tags esthétiques max. ; pas de valeurs de plan contradictoires.
- [ ] Exactement **un** mouvement de caméra (ou « static/fixed camera ») et **une** action avec tempo et état final.
- [ ] Nombre de personnages indiqué ; aucun sujet ajouté.
- [ ] Zéro mot d'ambiance/d'atmosphère — traduit en lumière, couleur, mouvement, matière.
- [ ] Exclusions sous forme de phrases positives (il n'y a pas de champ négatif).
- [ ] Pas de son, de dialogues, de texte à lire, de noms de personnes réelles.
- [ ] Durée ≤ 5 s ; si le tempo du mouvement compte — suggère le mode « qualité » ; en cas de stylisation — comparaison des modes sur le même seed.

## Sources
[1] Studio FSO — `modele/wideo/wan-2-2.yaml`, `wan-2-2-tekst.yaml`, `wan-2-2-obraz.yaml`, `wan-2-2-klatki.yaml`  — notre configuration
[2] Studio FSO — `workflows/wideo/wan_2_2_tekst-na-wideo.api.json`, `wan_2_2_obraz-na-wideo.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka_jakosc.api.json`  — notre configuration
[3] Wan2.2 README — https://github.com/Wan-Video/Wan2.2 — officiel
[4] Wan2.2 `wan/utils/system_prompt.py` (prompts système de l'extenseur T2V/I2V) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/system_prompt.py — officiel
[5] Wan2.2 `wan/configs/shared_config.py` (sample_neg_prompt, 16 fps, 81 images, text_len 512) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/shared_config.py — officiel
[6] Wan2.1 README (traduction anglaise du négatif par défaut ; FLF2V et le chinois) — https://github.com/Wan-Video/Wan2.1 — officiel
[7] Alibaba Cloud Model Studio — Text-to-video / image-to-video prompt guide — https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — officiel
[8] lightx2v — Wan2.2-Lightning (fiche modèle) — https://huggingface.co/lightx2v/Wan2.2-Lightning — officiel (auteurs de la LoRA)
[9] lightx2v — discussion #26 sur le mouvement lent — https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/26 — communauté + auteurs
[10] rzgar — Wan2.2 I2V LightX2V Slow-Mo Fix — https://huggingface.co/rzgar/Wan2.2_I2V_LightX2V_Slow-Mo_Fix — communauté
[11] Civitai — article sur la Lightning LoRA, CFG 1 et NAG — https://civitai.com/articles/18711 — communauté
[12] Hugging Face Forum — How to get the most out of prompts for WAN models — https://discuss.huggingface.co/t/how-to-get-the-most-out-of-prompts-for-wan-models/170354 — communauté
[13] ComfyUI — `comfy/sd1_clip.py` (analyse des parenthèses/poids) et `comfy/text_encoders/wan.py` (tokenizer umT5) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/sd1_clip.py , https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/wan.py — officiel (code ComfyUI)
[14] ComfyUI Docs — Wan2.2 tutorial — https://docs.comfy.org/tutorials/video/wan/wan2_2 — officiel (ComfyUI)
[15] aistudynow — How to Write Better WAN 2.2 Prompts, Tested in ComfyUI — https://aistudynow.com/how-to-write-better-wan-2-2-prompts-tested-in-comfyui/ — communauté
[16] ViewComfy — Wan 2.2 prompt guide with examples — https://www.viewcomfy.com/blog/wan2.2_prompt_guide_with_examples — communauté
[17] wan27.org — Wan 2.2 Prompt Guide — https://wan27.org/blog/wan-2-2-prompt-guide — communauté (site commercial, affirmations non testées)
[18] VEED — Wan 2.2 Prompting Guide — https://www.veed.io/learn/wan-2-2-prompting-guide — communauté
[19] Unifically — Wan 2.2 Image-to-Video Prompt Guide — https://unifically.com/blogs/wan-2.2-image-to-video-prompt-guide — communauté
[20] CivArchive — Anime style Wan 2.2 I2V (LoRA, remarques sur le biais réaliste) — https://civarchive.com/models/2222779/anime-style-wan-22-i2v — communauté
[21] Hugging Face — Phr00t WAN2.2-14B-Rapid-AllInOne, discussion #198 (81 images, retour de l'action en arrière) — https://huggingface.co/Phr00t/WAN2.2-14B-Rapid-AllInOne/discussions/198 — communauté
