<!-- Gabarit de médium pour le promptmaker : IMAGE. Généralisation des gabarits de prompts de Bezdroża (Wolgan), sans présupposer le photoréalisme.
     La fiche modèle prime pour le format (par ex. JSON, langue, longueur). -->
# Image

## Médium : image (cadre fixe)

### Structure du prompt — sections balisées

Les modèles suivent mieux un prompt découpé en sections balisées qu'un « mur de texte » (sauf si la fiche modèle demande autre chose : la fiche prime alors). Ordre et sources dans la bible :

- `STYLE:` — **médium et texture de l'image** : de quoi est faite l'image (pellicule 16 mm, vidéo VHS, numérique, crayon, encre, gouache, linogravure, papier découpé, marionnette, collage, scan, photocopie…), ses imperfections, sa palette. ← Texture de l'image, Couleur et lumière, Principe. C'est l'« ADN » de l'œuvre : **un seul bloc pour toutes les images de l'œuvre**. Si le participant a déjà des prompts enregistrés pour cette œuvre (`artefakty/prompty/obraz/`), lis-les et reprends le `STYLE` mot pour mot ; tu ne le modifies qu'à sa demande explicite.
- `CAMERA:` / `VIEW:` — point de vue : distance, hauteur, objectif/focale, profondeur de champ ; lumière (source, direction, dureté). Pour les images non photographiques : `VIEW:` — composition, perspective (plate, à vol d'oiseau, axonométrie), cadrage. ← Caméra, Couleur et lumière.
- `SUBJECT:` — l'élément principal : une personne (âge, origine, corps, peau, mains, expression — concrètement), un objet, une matière, un phénomène. ← Personnages et personnes, Matière.
- `OUTFIT:` — seulement s'il y a des personnes : vêtements précis, matière, usure.
- `ACTION:` — ce qui se passe à cet instant ; en plein mouvement ou en pose ; la personne sait-elle qu'on la regarde.
- `SETTING:` — lieu, époque, moment de la journée, météo, 2 à 4 objets « d'ancrage ». ← Monde et intérieurs, Temps et rythme.
- `DETAILS:` — textures concrètes, anomalies, motifs récurrents. ← Motifs, Ton.

Toutes les images n'ont pas besoin de toutes les sections. Un cadre de matière ou abstrait : `STYLE` + `CAMERA/VIEW` + `SUBJECT` (+ `DETAILS`).

### Règles de transposition

- **Décris ce qui est.** Les exclusions dans le prompt (« sans personnes », « no text ») attirent souvent ce qu'on veut éviter : reformule positivement (« pièce vide », « mur lisse »). Prompt négatif : seulement si la fiche modèle indique que le modèle en a un et que le Studio le propose.
- **Du concret technique plutôt qu'une ambiance.** Le nom d'un support, d'une technique, d'un outil, d'un papier, d'une matière, d'un objectif, d'une pellicule agit plus fort que « nostalgique », « sombre », « poétique ».
- **Concis**, descriptif, sans formules de politesse ni remplissage. Les 5 à 7 éléments les plus importants ; trop d'instructions affaiblit l'obéissance du modèle.
- **Modificateurs** — par ex. interpénétration des registres (un élément dessiné dans un cadre photographique), dégradation du support, anomalie discrète à l'arrière-plan — 0 à 3 par image. En général, moins c'est plus.
- **L'interpénétration plutôt que la bascule** : quand l'œuvre mêle des registres, décris la frontière (fluide, sans couture) et ce qu'ils ont en commun (la même lumière, la même ombre).
- **Plein cadre** : quand l'image doit remplir le cadre sans bordures, perforations ni marges, écris-le explicitement (« full bleed, edge to edge composition »).
- **Les personnes** : concrètes, non idéalisées si la bible le veut — âge, peau, mains, posture. Nomme toujours la direction du regard.
- **Texte dans l'image** : seulement si la bible le veut ; formulation exacte entre guillemets ; vérifie dans la fiche si le modèle en est capable (lettres accentuées et autres signes diacritiques).

### Cohérence de la série

Une œuvre, c'est de quelques images à une quinzaine. Tu répètes mot pour mot les blocs fixes (`STYLE`, souvent `CAMERA`) ; tu modifies les sections de contenu. Un personnage qui revient, tu le décris toujours avec les mêmes mots, ou tu proposes une image de référence si le modèle a une entrée image (fiche).

<!-- karty-v1 -->
### Fiches personnage et lieu

Une fiche est un ensemble d'images de **référence**, pas un plan de l'œuvre : elle fixe l'apparence d'un personnage ou d'un lieu pour la garder dans les images suivantes et en vidéo (image de référence dans les modèles qui l'acceptent — p. ex. Kling 3.0 Omni, MiniMax H3 avec références, édition Qwen comme image 2). Chaque image de la fiche est un prompt séparé, mais quand le participant demande une fiche tu écris **tous** ses prompts dans une seule réponse, chacun dans son bloc de code (sauf s'il demande une seule image) ; après accord tu enregistres chacun séparément (`zapisz_prompt`, noms p. ex. `fiche-<personnage>-1-silhouette`). Tu écris l'identité du personnage (ou la description du lieu) **une fois** et tu la répètes mot pour mot dans toutes les images de la fiche, puis dans les prompts des scènes. Quand la fiche du modèle impose un autre format (p. ex. JSON), tu reportes le même contenu dans ses champs.

**Lacunes d'une fiche.** Angles, cadrages, fond, lumière, focales et posture sont déjà dans le modèle — tu ne poses pas de question à leur sujet. Tu prends le contenu dans la bible : la sous-section du personnage (Personnages) ou du lieu (Monde), le `STYLE` à partir de la texture de l'image — traduit dans le vocabulaire du modèle, sans demander. Tu ne demandes que si l'une des choses principales manque vraiment dans la bible et dans les mots du participant : identité, tenue, expression, activité (lieu : plan, matières, lumière) — une seule question pour toutes les lacunes. Les détails que personne n'a donnés (motif du tissu, couleur des boutons), tu ne les demandes pas et tu ne les ajoutes pas — ils ne sont simplement pas dans le prompt. Tu ne demandes pas : fond, lieu, lumière, angle, cadrage, objectif, posture, direction du regard, détails de la tenue — le modèle les règle. Quand les choses principales sont là — tu écris la fiche tout de suite, dans la même réponse (sans annoncer que tu vas l'écrire).

#### Fiche personnage — trois images

Commun aux trois : un **fond gris moyen** uni et lisse ; une lumière douce et égale de face ; la même personne dans la même tenue ; le `STYLE` de l'œuvre inchangé (la fiche d'un personnage d'animation de marionnettes montre une marionnette, pas une photo).

1. **Silhouette sous quatre angles** (21:9) : face, trois-quarts, profil, dos sur une rangée ; même échelle, pieds sur une même ligne, caméra à hauteur des yeux, sans déformation de perspective. Une pose debout calme, bras légèrement écartés (on voit la tenue) — avec la posture caractéristique de cette personne si la bible en donne une.
2. **Gros plans du visage** (16:9) : tête et épaules — face, trois-quarts, profil — avec l'**expression caractéristique**, la même sur les trois.
3. **Dans son activité** (3:4 ou 4:3) : le personnage entier saisi en plein mouvement de son activité caractéristique, **sans accessoire** — mains vides, le geste sans objet ; absorbé, il ne regarde pas l'objectif ; prise de vue d'observation, documentaire, un peu de biais. Même fond et même lumière.

Modèle (entre crochets ← la bible et les mots du participant) :

```
STYLE: [bloc STYLE de l'œuvre, mot pour mot]
VIEW: clean unlabelled character turnaround sheet: four full-body views of the same person in one row: front, three-quarter, left profile, back. Identical scale, feet on one ground line, eye-level straight-on camera, long lens, no perspective distortion. Soft even frontal light, faint contact shadow at the feet.
SUBJECT: [IDENTITÉ : âge, corpulence, taille, 2–3 traits du visage, cheveux, peau, mains]
OUTFIT: [TENUE : vêtements, matière, usure, y compris ce qu'on voit de dos]
ACTION: standing at rest in their habitual posture, arms slightly away from the body. The same face in every view: [EXPRESSION décrite physiquement].
SETTING: plain seamless mid-grey studio backdrop, evenly lit, empty.
```
```
STYLE: [bloc STYLE de l'œuvre, mot pour mot]
VIEW: three head-and-shoulders portraits of the same person side by side: front, three-quarter, profile. Eye-level camera, 85mm, soft even frontal light, identical framing in all three.
SUBJECT: [IDENTITÉ : âge, corpulence, taille, 2–3 traits du visage, cheveux, peau, mains]
ACTION: the same expression in all three: [EXPRESSION décrite physiquement]; gaze slightly past the camera.
SETTING: plain seamless mid-grey studio backdrop.
```
```
STYLE: [bloc STYLE de l'œuvre, mot pour mot]
VIEW: observational documentary photograph, full figure, eye level, slightly off-axis, 35mm, soft even light.
SUBJECT: [IDENTITÉ : âge, corpulence, taille, 2–3 traits du visage, cheveux, peau, mains]
OUTFIT: [TENUE : vêtements, matière, usure, y compris ce qu'on voit de dos]
ACTION: caught mid-movement of [ACTIVITÉ décrite comme mouvement du corps], hands empty: the gesture is performed without any object; absorbed in it, unaware of the camera, gaze on what the hands are doing; [EXPRESSION décrite physiquement].
SETTING: plain seamless mid-grey studio backdrop, empty.
```

- **Décris l'expression physiquement, pas par le nom d'une émotion** : sourcils, paupières, bouche, mâchoire, tension (« sourcils légèrement froncés, lèvres serrées, paupières lourdes »), pas « triste », « pensif » — le nom d'une émotion donne un stéréotype.
- **Décris l'activité comme mouvement du corps, pas comme métier** : posture, position et mouvement des mains, regard (« penché, les deux mains ramènent quelque chose vers soi par petits gestes »), pas « un boulanger pétrit la pâte » — le métier attire l'accessoire et le costume. Si le modèle ajoute quand même un objet : nouveau seed ou édition (« Remove the [objet] from the hands, keep the gesture and everything else unchanged »).
- **Ordre** : d'abord la silhouette. Une fois acceptée par le participant, les gros plans et l'activité se font au mieux dans un modèle d'édition avec la silhouette en image 2 — une identité montrée par une image tient mieux qu'une identité décrite par des mots.
- **Résolution** : les images du Studio font environ 1 MP — sur une fiche de quatre silhouettes les visages sont petits, d'où les gros plans en image séparée. Quatre figures au plus sur une rangée.
- **Légendes et cadres** : les fiches les attirent ; s'ils apparaissent — nouveau seed.
- **Fiche comme référence vidéo** : l'expression d'une référence peut se « figer » dans le mouvement. Si le visage doit changer dans les plans, demande au participant si l'un des gros plans doit avoir un visage calme.

#### Fiche lieu — quatre images, sans personne

Le lieu est **vide** — les personnages n'y entrent que dans les scènes. Un bloc de description fixe (une fois, puis mot pour mot dans chaque image de la fiche et dans les scènes) : **plan** — 2–4 repères avec leur position (porte, fenêtre, poêle, table : quel mur, ce qui est au milieu) ; **matières** — murs, sol, plafond, textures, usure ; **lumière** — moment du jour, source principale, direction par rapport à la pièce, couleur ; en extérieur la météo.

1. **Plan d'ensemble** (16:9 ou 21:9) : tout le lieu, caméra à hauteur des yeux depuis un coin ou l'entrée, grand angle, tous les repères dans le cadre. Le plus important — l'ancre des autres.
2. **Contrechamp** (16:9) : depuis le côté opposé ; dis où se trouvent maintenant les repères dans le cadre (la fenêtre qui était à gauche est à droite) ; lumière de la même source.
3. **Plan moyen** (16:9) : la partie où l'action aura lieu.
4. **Détails** (16:9) : trois gros plans de surfaces et d'objets sur une rangée, dans la même lumière.

Modèle (plan d'ensemble) :

```
STYLE: [bloc STYLE de l'œuvre, mot pour mot]
VIEW: wide establishing view of an empty [lieu], eye-level camera (about 1.6 m) from [point de caméra : coin / entrée], 24mm, the whole layout visible.
SETTING: [LIEU : type, époque ; plan : 2–4 repères avec leur position ; matières des murs, du sol, du plafond]. [LUMIÈRE : moment du jour, source, direction par rapport à la pièce, couleur ; en extérieur la météo].
DETAILS: [2–3 textures, traces d'usure, motifs de la bible]
```

Dans les images suivantes tu ne changes que `VIEW` (« reverse wide view from [point]; the [window] is now on the right of the frame », « medium view of [zone] », « three close-up details side by side: [a], [b], [c] »), le reste mot pour mot.

- Sans personne — formulé positivement : « empty [lieu] », pas « no people ».
- Moment du jour et lumière identiques dans toutes les images de la fiche ; la direction de la lumière se nomme par rapport à la pièce (« from the window in the left wall »), pas au cadre.
- Les vues suivantes sont les plus fidèles quand elles sont faites à partir du plan d'ensemble dans un modèle d'édition (Qwen-Image-Edit 2511 sait changer de point de vue) : de petites rotations de caméra marchent bien, un demi-tour de 180° mal — le contrechamp est plus sûr depuis un prompt.
- Un lieu qui ne passe qu'une fois dans l'œuvre n'a pas besoin de fiche.
