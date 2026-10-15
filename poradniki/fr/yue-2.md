# YuE 2 — comment prompter

## Comment le modèle écoute
YuE 2 (3B) est par nature un **modèle de chansons** : à partir d'une description de style et de paroles, il produit un morceau entier avec voix et accompagnement, construit en intro–couplet–refrain–pont–outro. Deux champs : **style** et **paroles**. Il a aussi un mode **cover** : il extrait la mélodie d'un enregistrement (sous forme de notation), puis génère un morceau avec un nouveau style et de nouvelles paroles.

## Structure
- **Style :** en anglais, sur une seule ligne, séparé par des virgules, court (env. 15–35 mots). Ordre : langue, genre, caractère de la voix, tempo, instruments, caractéristiques musicales. Exemple tiré de la documentation : « English, warm piano pop, expressive female voice, acoustic piano, rounded bass and light drums, lyrical memorable melody, unhurried phrasing, 88 BPM ». Écris le tempo (BPM) et la tonalité dans le style — il n'y a pas de champs séparés pour eux.
- **Paroles :** uniquement les mots à chanter, avec les balises de sections `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` — chaque balise sur sa propre ligne, une ligne vide entre les sections. Les indications musicales vont uniquement dans le style.
- **Pas de didascalies entre parenthèses dans les paroles** (p. ex. « (instrumental theme) », « (guitar solo) ») — le texte entre parenthèses risque d'être chanté.
- **En instrumental** (selon la recette officielle de YuE2) : le style commence par « Instrumental, » et se termine par « no vocals, no singing, no choir, no spoken words. » ; dans le champ des paroles, **uniquement les balises de sections, sans aucun mot ni parenthèse** (p. ex. les valeurs par défaut du Studio). La recette officielle transfère en plus la mélodie de la partie vocale vers un instrument — le Studio ne le fait pas, et même officiellement l'absence de voix n'est pas garantie. **Écoute le résultat** — s'il y a de la voix, change le seed.

## Points sensibles / pièges
- Ne mets dans les paroles ni tags de style, ni BPM, ni accords, ni emoji, ni mise en forme.
- **Budget de tokens :** un prompt long raccourcit le morceau ; quand le budget est épuisé, l'enregistrement peut s'arrêter au milieu d'une phrase.
- Le cover fonctionne le mieux quand les nouvelles paroles ont un phrasé et un nombre de syllabes proches de l'original, et que les sections suivent le même ordre que dans l'enregistrement. Le style décrit le son visé, pas l'original ; l'enregistrement ne transfère que la mélodie (ni la voix ni le timbre).
- Les autres langues, dont le français et le polonais, ne sont pas officiellement prises en charge (documentées : anglais, chinois) — fais un court essai avant un long morceau.

## Exemple (structure)
Instrumental :
- Style : « Instrumental, slow cinematic folk, nylon guitar leading the melody, cello and soft hand percussion accompaniment, D minor, 70 BPM, a quiet opening that grows and fades out, intimate room sound, no vocals, no singing, no choir, no spoken words. »
- Paroles (uniquement les balises, sans mots) :
```
[Intro]

[Verse]

[Chorus]

[Outro]
```

## Paramètres qui changent vraiment le résultat
- **Durée max.** — une limite haute, le morceau peut se terminer plus tôt (60 s par défaut, 120 s en cover ; règle-la au moins à la durée de l'enregistrement). Trop basse, elle coupe le morceau au milieu d'une phrase.
- **Seed** — commun à la partition et au son ; garde-le fixe quand tu compares des styles.
- Le mode de planification est réglé par le Studio : « YuE 2 » = full (mélodie et accords), « YuE 2 · cover » = melody (mélodie tirée de l'enregistrement, accompagnement plus libre).

## Sources (consultées le 2026-10-05)
- ComfyUI — YuE2 Music Generation Guide : https://docs.comfy.org/tutorials/audio/yue2/yue2
- YuE — generation docs : https://github.com/multimodal-art-projection/YuE/blob/main/docs/generation.md
- YuE2 — skill instrumental (recette officielle) : https://github.com/multimodal-art-projection/YuE/tree/main/skills/yue2-music/instrumental
- ComfyUI — template de cover YuE2 : https://github.com/Comfy-Org/workflow_templates/blob/main/templates/audio_yue2_music_cover.json
