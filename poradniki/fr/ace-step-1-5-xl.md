# ACE-Step 1.5 XL — comment prompter

## Comment le modèle écoute
Un modèle musical avec deux champs de texte : **la description (caption / tags)** — genre, ambiance, instruments, timbre, production — et **les paroles (lyrics)** avec des balises de sections. Le tempo (BPM), la tonalité, la mesure et la durée ont des **réglages séparés** — ne les écris pas dans la description. Dans le Studio tourne la variante **sft** (50 étapes, avec CFG) : plus lente que turbo, mais plus riche en détails et nettement meilleure pour le chant.

## Structure de la description (ordre recommandé par les auteurs)
`genre/style → émotion/atmosphère → instruments → texture sonore → caractère de la voix (s'il y en a une) → époque/production`

Le concret l'emporte : « sad piano ballad with female breathy vocal » fonctionne mieux que « a sad song ».

## Paroles et musique instrumentale
- Balises de sections : `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` ; avec une courte précision : `[Chorus - anthemic]`, `[Bridge - whispered]`.
- **En instrumental :** paroles vides ou `[Instrumental]` ; décris le développement du morceau avec des balises, p. ex. :
```
[Intro - ambient]
[Main Theme - piano]
[Climax - powerful]
[Outro - fade out]
```
- Parties solistes : `[Guitar Solo]`, `[Piano Interlude]`, `[drum break]`.

## Points sensibles / pièges
- **Une contradiction entre la description et les paroles** (p. ex. « violin solo » dans la description, `[Guitar Solo]` dans les paroles) gâche le résultat.
- N'empile pas les précisions dans une balise (`[Chorus - anthemic - stacked harmonies - high energy]` — c'est trop) ; une description complexe va dans le champ de description.
- BPM et tonalité dans la description au lieu des réglages — ça marche moins bien.
- Les morceaux courts (30–60 s) sont les plus prévisibles ; la mesure 4/4 est la plus stable.

## Exemples (structure)
- Description : « minimal ambient, melancholic and spacious, felt piano and soft string pads, warm tape saturation, slow evolving textures, lo-fi home recording. » Paroles : `[Instrumental]`
- Description : « dark post-rock, tense then cathartic, tremolo electric guitars, deep bass, live drums with heavy room reverb, 2000s production. » Paroles : `[Intro - quiet guitar]` `[Build - drums enter]` `[Climax - full band]` `[Outro - feedback fade]`

## Paramètres qui changent vraiment le résultat
- **BPM** (30–300), **tonalité**, **mesure**, **durée** (champs séparés). **Seed.**

## Sources (consultées le 2026-10-05)
- ACE-Step 1.5 — Ultimate Guide (officiel) : https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/Tutorial.md
- ACE-Step 1.5 — A Musician's Guide : https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/ace_step_musicians_guide.md
