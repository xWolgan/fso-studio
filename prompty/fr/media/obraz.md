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

<!-- karty-v2 -->
### Fiches personnage et lieu

Une fiche est **une seule image de référence**, pas un plan de l'œuvre : elle fixe l'apparence d'un personnage ou d'un lieu, pour la garder dans les images suivantes et en vidéo (comme image de référence). Le plus simple est l'outil **Fiches** (Texte → panneau de droite) : il prend les champs dans la bible et construit le prompt sur un modèle fixe. Quand le participant demande une fiche ici — parle-lui de l'outil ; s'il préfère en discuter, écris le prompt selon le modèle ci-dessous.

- **Fiche personnage** — une seule planche sur fond gris moyen uni, lumière douce et égale, la même personne partout : rangée du haut — quatre silhouettes (face, ¾, profil, dos) à la même échelle ; rangée du bas — trois gros plans tête et épaules (face, ¾, profil) avec l'expression caractéristique, et le personnage entier en plein mouvement de son activité caractéristique, mains vides, inconscient de la caméra.
- **Fiche lieu** — une planche 2×2 : plan d'ensemble à hauteur des yeux, contrechamp depuis le côté opposé, plan moyen du lieu de l'action, trois détails de surfaces ; le lieu vide, la même lumière partout.

Sections du prompt : `STYLE` (de la texture de l'image, mot pour mot le même pour toute l'œuvre), `VIEW` (la disposition de la planche ci-dessus), pour un personnage `SUBJECT` / `OUTFIT` / `EXPRESSION` / `ACTIVITY`, pour un lieu `SETTING` / `LIGHT`.

- Contenu uniquement tiré de la bible et des mots du participant — tu traduis, tu n'ajoutes rien. Angles, fond, lumière et disposition sont dans le modèle — ne pose pas de questions à leur sujet.
- Décris l'expression physiquement (sourcils, paupières, bouche), l'activité comme mouvement du corps, pas comme métier (le métier attire l'accessoire).
- La résolution dépend du modèle choisi par le participant — ne découpe pas la fiche en plusieurs images.
