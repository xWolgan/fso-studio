<!-- Gabarit de médium pour le promptmaker : VIDÉO. Les sections de l'image (de media/obraz.md, Bezdroża) + temps, mouvement, son.
     La fiche modèle prime pour le format (par ex. paragraphe chronologique pour LTX, sections et balises pour H3). -->
# Vidéo

## Médium : vidéo (un seul plan)

### Structure du prompt

Les mêmes sections que pour l'image — `STYLE` (médium et texture, commun à toute l'œuvre), `CAMERA`, `SUBJECT`, `OUTFIT`, `ACTION`, `SETTING`, `DETAILS` — plus :

- `MOTION:` — ce qui bouge et comment, **dans l'ordre des événements**, du début à la fin du plan. Dans un plan de 5 à 10 s : un événement, deux au maximum. ← Temps et rythme, Personnages et personnes, Matière.
- `CAMERA MOVE:` — fixe / panoramique / travelling / caméra à l'épaule / zoom avant ; tempo ; la caméra réagit-elle à ce qui se passe. ← Caméra.
- `SOUND:` — seulement pour les modèles avec son (fiche) : sources sonores, espace, distance ; dialogue avec sa formulation exacte entre guillemets, qui parle et comment ; musique ou absence de musique. ← Son, Voix et parole, Musique.

Si la fiche modèle demande d'écrire en un seul paragraphe (par ex. une description chronologique), garde le même contenu et le même ordre, simplement sans les étiquettes.

### Règles de transposition

- **Un plan, c'est du temps.** Décris chronologiquement ; un plan = une continuité. Le modèle perd le fil des actions longues et complexes : découpe-les en plusieurs plans.
- **Du mouvement physique, pas émotionnel** : « l'eau s'infiltre lentement sous la porte », pas « la tension monte ».
- **Image de départ / images clés / références** : quand le participant a déjà une image, le prompt décrit surtout le mouvement, le temps et le son, et non ce qu'on voit déjà (détails : fiche modèle).
- **Transition « sans coupe »** (l'espace change pendant le mouvement de caméra) : décris-la comme un seul plan continu — mouvement de caméra, espace A au début, changement au milieu, espace B à la fin ; la lumière change naturellement.
- **Dialogue** : les mots exacts, la langue (si ce n'est pas l'anglais, vérifie dans la fiche comment le modèle s'en sort), la manière de parler.
- Toutes les règles de l'image s'appliquent : ce qui est (pas d'exclusions), le concret technique, la concision, un `STYLE` commun mot pour mot à toute la série.
