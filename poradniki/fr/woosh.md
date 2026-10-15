# Woosh (Sony AI) — comment prompter

## Comment le modèle écoute
Modèle conçu spécialement pour les **effets sonores** : texte → effet et **vidéo → son synchronisé** (bruitage d'un clip), ce dernier avec un texte facultatif qui suggère ce qui doit sonner. Les auteurs ne publient pas de guide de prompting à part — ce qui suit s'appuie sur les exemples de leur page de démonstration.

## Structure de la description
**Une courte description de l'événement sonore et de sa source**, env. 8–15 mots : ce qui sonne + ce qui lui arrive. Exemples tirés de la démo des auteurs :
- « Emergency vehicle driving with siren on »
- « An engine humming and brakes squealing »
- « Starting a motorcycle »
- « A crowd applauds »
- (vidéo + texte) « A propeller plane flies over a snowy landscape, its engine roaring »

## Vidéo → son
- Le clip est analysé dans une fenêtre **de 8 s maximum** ; le résultat est coupé à la durée du clip.
- Sans texte, le modèle devine le son à partir de l'image ; un texte court aide quand l'image est ambiguë.

## Points sensibles / pièges
- **Sortie mono, 48 kHz.**
- **Le volume est souvent très faible** — le Studio ne normalise rien ; remonte le niveau au montage.
- Les descriptions longues et poétiques aident moins qu'une source et une action concrètes.

## Paramètres qui changent vraiment le résultat
- **Mode** : rapide (texte → 5 s d'effet en env. 0,4 s ; vidéo → env. 3 s) / qualité (env. 8–12 s).

## Licence
Poids CC-BY-NC — usage non commercial uniquement.

## Sources (consultées le 2026-10-05)
- Sony AI — Woosh (page du projet, exemples) : https://sonyresearch.github.io/Woosh/
- GitHub — SonyResearch/Woosh : https://github.com/SonyResearch/Woosh
- Sony AI — Introducing Woosh : https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model
- Temps et format : notre propre test sur le Spark.
