<!-- Fiche modèle pour le promptmaker. modele: stable-audio-3 -->
# Stable Audio 3 small-SFX (Stability AI, 05.2026)

## Ce que c'est et à quoi ça sert
- Petit modèle de diffusion (env. 0,5–0,6 milliard de paramètres) **texte → effet / ambiance / foley / one-shot**, **stéréo 44,1 kHz**, durée de 1 s à 2 min [6][7] (officiel), [3] (notre configuration).
- Dernières étapes de l'entraînement de small-SFX : **un sous-ensemble sélectionné de Freesound** (enregistrements de terrain, foley, sound design) ; small-music a reçu AudioSparx à part, parce que les données SFX nuisaient à la cohérence de la musique [6] (officiel). Conclusion : le modèle comprend le mieux les descriptions dans le style des **titres, tags et descriptions de Freesound** [4][6] (officiel).
- Points forts : événements isolés (impacts, pas, portes, verre), textures et ambiances, sound design traité (tape stop, distorsions, filtres), mouvement dans le panoramique stéréo [4][9] (officiel).
- Dans le test de Stability sur les effets BBC (5 s), small-SFX a devancé Woosh-Flow (FAD 0,395 contre 0,580 ; CLAP 0,351 contre 0,277) — mesure du fabricant [6] (officiel).
- **Ce qu'il ne fait PAS bien :**
  - **la musique** — tableau des modes : small-sfx = uniquement « Samples/SFX », ni Music ni Stems [4] (officiel) → pour la musique : les autres modèles du Studio [3] (notre configuration) ;
  - **la parole et le chant intelligibles** — la famille SA3 ne produit pas de voix intelligibles [4][5] (officiel) ;
  - **le mélange de plusieurs sources à la fois** — un praticien estime que l'ancien Stable Audio Open 1.0 exécute mieux la consigne « mélange » des sons [13] (communauté) ;
  - **le placement précis des événements dans le temps** (p. ex. « un impact exactement à la 3ᵉ seconde ») — le contrôle temporel est hors de portée du modèle [6] (officiel) ;
  - qualité en général : avis partagés — « des résultats raisonnables, en un éclair », mais moins bien que SA Open 1.0 [13] ; un autre utilisateur : « environ 10 % mieux que la 1.0 » ; quelques plaintes isolées sur du bruit [14] (communauté).

## Ce que le participant règle dans le Studio
| Champ | Valeurs | Effet sur le prompt |
|---|---|---|
| **prompt** | texte | unique description ; va dans l'encodeur T5Gemma [1][2] (notre configuration) |
| **durée (s)** | 1–120, par défaut 10 | c'est le **vrai contrôle de la durée** : ComfyUI en calcule la condition `seconds_total` (nombre entier — les décimales sont tronquées) [1][12] (notre configuration / code ComfyUI). Adapte-la à l'événement (voir plus bas) |
| **seed** | nombre | les résultats dépendent fortement de la graine — génère des variantes [3] (notre configuration) |

- Un seul mode : modèle **distillé** small-SFX, 8 pas, **CFG 1**, sampler lcm [1][2] (notre configuration). **Pas de mode « qualité » ni de champ négatif** — selon la fiche HF, le checkpoint base est « pré-entraîné, destiné au fine-tuning ; pour générer, utilise Small SFX » [8] (officiel), donc le Studio ne le propose pas. Avec CFG 1, la branche négative ne serait de toute façon pas calculée [12][17].
- L'exemple officiel pour le modèle distillé utilise le sampler pingpong ; le Studio utilise lcm (comme le template officiel ComfyUI) [2][7] — sans effet sur le prompt.
- Sortie : FLAC stéréo ; **le volume n'est pas normalisé** [1][3] (notre configuration).
- Le Studio **n'enrichit pas le prompt** par un LLM (délibérément, contrairement au template medium) [3] (notre configuration) — le prompt du promptmaker arrive au modèle tel quel.

## Format du prompt
- **Langue : anglais.** Fiche du modèle : langue English ; les données d'entraînement sont les métadonnées anglaises de Freesound/AudioSparx [6][7] (officiel). Des mots dans la langue du participant, tout au plus comme nom propre — traduis tout.
- **Préfixe `TrackType: SFX,`** au début — officiellement recommandé pour les effets et les samples ; dans l'article technique, les auteurs écrivent que de tels préfixes « améliorent nettement la qualité » (là, dans le contexte des modèles entraînés avec les données AudioSparx) [4][5][6] (officiel). Pas de test séparé pour small-SFX — utilise-le, mais ce n'est pas une formule magique.
- **Structure (ordre de Stability) :** 1) **source** (objet / matériau / instrument / synthétiseur précis) → 2) **action** (comment le son naît, combien il dure, comment il s'éteint — attaque, résonance, queue) → 3) **production et caractère** (micro et sa distance, pièce, traitement) [4][5] (officiel).
- **Longueur du texte :** le template SFX officiel (Comfy-Org/Stability) demande **1–2 phrases denses**, un langage technique et concret, sans redondance [9] (officiel). Limite de l'encodeur : **256 tokens**, au-delà c'est tronqué [6] (officiel) — en pratique, n'approche jamais de cette limite.
- **Style :** à l'entraînement, les champs de métadonnées étaient joints **par des virgules**, mélangés au hasard et, une fois sur deux, passés en minuscules ; une partie des descriptions Freesound sont des légendes réécrites par un LLM [6] (officiel). Donc une phrase naturelle fonctionne aussi bien qu'une suite de syntagmes séparés par des virgules ; la casse et l'ordre des tags ne sont pas critiques.
- **`Length: N seconds`** à la fin — convention du template officiel et des exemples ComfyUI [9][10] (officiel). Dans le Studio, la durée est de toute façon réglée par le champ « durée » ; si tu l'ajoutes, elle **doit correspondre au champ**. L'effet du texte seul sur small-SFX n'est pas confirmé.
- **Poids `(mot:1.3)`, JSON, balises de section** — absents de la documentation ; ne les utilise pas.
- **Il n'y a pas de négatif** — ne décris pas ce qui ne doit pas être là ; si besoin, nomme positivement ce qui doit y être (« dry, isolated »).
- **BPM** — c'est du vocabulaire musical (AudioSparx, mode Music/Instrument) [4][9] ; small-SFX ne fait pas de musique. Pour les effets rythmiques (p. ex. le tic-tac d'une horloge), décris le tempo par des mots (« steady, once per second ») — efficacité non confirmée.

## Squelette du prompt
```
TrackType: SFX, [source : objet précis + matériau], [action : comment le son naît, tempo/intensité], [déroulé dans le temps : attaque, résonance, queue / montée, extinction], [espace : intérieur/extérieur, sec/réverbéré, type de pièce], [perspective : close-up / distant / approaching / passing left to right], [enregistrement et traitement : micro, bande, filtre, distorsion, inversion]. Length: [N] seconds
```
Paysage sonore (ambiance) :
```
TrackType: SFX, [lieu/environnement] ambience, [couche continue : fond/bruit], [2–3 événements de fond, rares/fréquents], [distance des couches], [moment de la journée / météo comme son, pas comme humeur], [caractère de l'enregistrement : field recording, stereo]. Length: [N] seconds
```

## Ce qui marche
- **Précision du matériau et de la physique** : « wooden desk drawer », « thin glass », « hard boot on dry leaves », « 14-inch hi-hats played tightly closed » — les exemples officiels nomment toujours le matériau, la force et la longueur de la queue [4][5][9] (officiel).
- **Description de l'évolution dans le temps** dans le template SFX : attaque, résonance, mouvement, transitions — p. ex. « starts with a suck-back of ambient noise, followed by a supersonic crack… that disappears into the distance » [9] (officiel).
- **Vocabulaire de l'espace** du template : indoor/outdoor, cave / open field / underwater, dry / reverberant, close-up / distant, echoing / muffled [9] (officiel).
- **Mouvement et stéréo** (le modèle est stéréo) : « passing », « approaching », « doppler effect », « sound moving from left to right stereo field », « footsteps approaching then fading away » [9][10] (officiel).
- **Séquences** : exemple officiel « Rapid sequence of three impacts: metal hit, glass break, wood crack, spaced evenly » [9] (officiel) — on peut décrire des séquences courtes et dénombrables ; n'attends pas un placement exact dans le temps.
- **Micro et enregistrement** comme partie de la description : « close-mic », « recorded with a small-diaphragm condenser mic », « ribbon mic », « recorded in a dead room with no room reflections » [4][9] (officiel ; une partie des exemples vient du template One-shot).
- **Durée adaptée à l'événement** (template officiel) : impacts, clics 1–3 s ; actions moyennes (pas, glissements, transitions) 3–6 s ; ambiances 6–15 s (exemples d'ambiances jusqu'à 45–120 s) [9] (officiel). Stability : les résultats sont meilleurs quand la durée correspond au son décrit [4] (officiel).
- **Variantes par le seed**, pas en réécrivant le prompt — une génération prend 1–2 s [3] (notre configuration).
- **Couches séparées** : au lieu de « pluie + pas + sirène » dans un seul prompt, génère chaque couche séparément et mélange-les au montage (déduction à partir de [13] ; l'exemple officiel « Layered soundscape: rain, thunder, footsteps, and distant sirens » [9] montre que c'est possible, mais la qualité du mélange est parfois moindre).

## Biais et pièges
- **Durée trop longue pour un événement court** → silence, remplissage ou répétitions [18] (notre configuration) ; l'entraînement ajoutait du silence après l'enregistrement pour dissocier la durée du contenu [6] (officiel).
- **Des mots d'humeur au lieu du son** (« mélancolique », « solitude ») — le modèle a appris sur les métadonnées de sonothèques ; traduis l'humeur en phénomène acoustique (distance, réverbération, rareté des événements, filtre) [4][6] (déduction à partir des sources officielles).
- **Dérive vers la musique / le ton** avec des mots comme « cinematic », « epic », « drone » — le template les utilise délibérément pour le sound design [9] ; si tu veux un enregistrement brut, ne les ajoute pas (non confirmé comme biais, par prudence).
- **Volume** : le Studio ne normalise pas [3] (notre configuration) — préviens le participant que les niveaux s'égaliseront au montage.
- **Peu de différence entre les seeds** pour un même prompt (observation pour la musique SA3) [15] (communauté) — si les variantes sont trop semblables, change un élément de la description (perspective, matériau).
- **Pas de boucle** : il n'y a ni paramètre de boucle ni documentation des boucles pour SA3 (rien trouvé). La boucle se fait au montage (crossfade) — voir plus bas.

## Au-delà du photoréalisme
Le vocabulaire du traitement et de la « bande » figure dans les exemples officiels, donc le modèle le connaît [4][9] (officiel) :
- **bande / vinyle / archive** : « tape stop », « tape-saturated », « vinyl crackle », « dusty », « lo-fi », « 1950s » (exemples des templates SFX/One-shot/Instrument) [9] ;
- **traitement** : « processed with resonant band-pass filter », « slightly distorted », « bit-crushing », « pitch-shifted », « reversed », « granular texture », « glitchy digital distortion », « long dark wooden room reverb » [9] ;
- **stylisation du médium** : « 8-bit style », « retro arcade », « soft futuristic interface sounds » figurent dans les exemples [9] ; « cartoon », « hand-drawn » — non confirmés ;
- **abstraction / texture** : décris le phénomène physique, pas le sens — « metal scraping slowly in a dark tunnel », « heavy timber under immense structural tension, swaying slowly » [9] ;
- **perspectives inhabituelles** : « underwater », « interior perspective », « muffled » [9] ; les micros spéciaux (« contact microphone », « hydrophone ») sont des tags Freesound courants — efficacité non confirmée.
- Comment faire du « dessin / de l'animation » en son : simplifier et exagérer la physique (court, sec, sans fond : « dry, isolated, no background ») — déduction, non confirmé.

## Mouvement / temps / son
- Mouvement de la source : approaching / receding / passing / doppler / left-to-right stereo [9][10] (officiel).
- Déroulé : attaque (sharp transient / slow attack), résonance (fast decay / long shimmering decay / reverb tail), montée (slow build) [4][9] (officiel).
- **Boucle (ambiance)** : génère plus long que nécessaire (p. ex. 30–60 s), sans événements marquants au début et à la fin (« steady, continuous, no sudden events » — non confirmé), ferme la boucle par un long crossfade au montage ; le Studio n'a pas de mode boucle [1] (notre configuration).
- Durée du champ = durée du résultat ; max. 120 s [1][7].

## Vérifie avant d'envoyer
- [ ] Prompt en anglais, commence par `TrackType: SFX,`
- [ ] Source nommée **et matériau**, action, déroulé dans le temps, espace, perspective
- [ ] 1–2 phrases, sans humeurs ni métaphores du poème (traduites en phénomènes acoustiques)
- [ ] Le champ « durée » correspond à l'événement (impact 1–3 s, action 3–6 s, ambiance 6–15 s+) ; si `Length: N seconds` est ajouté — conforme au champ
- [ ] Un événement / une couche par prompt (couches → générations séparées)
- [ ] Sans musique, parole, BPM, poids, JSON
- [ ] Rappel : plusieurs seeds ; volume à égaliser au montage

## Sources
[1] Studio — `modele/sfx/stable-audio-3.yaml` — notre configuration
[2] Studio — `workflows/sfx/stable_audio_3_tekst-na-efekt.api.json` — notre configuration
[3] notes internes (non publiées) (section SFX) — notre configuration
[4] Stability AI — Stable Audio 3 prompting guide (GitHub) — https://github.com/Stability-AI/stable-audio-3/blob/main/docs/guides/prompting.md — officiel
[5] Stability AI — Stable Audio 3.0 Prompt Guide — https://stability.ai/guides/stable-audio-3-prompt-guide — officiel
[6] Stable Audio 3 — article technique (arXiv 2605.17991) — https://arxiv.org/html/2605.17991v1 — officiel
[7] Hugging Face — stabilityai/stable-audio-3-small-sfx — https://huggingface.co/stabilityai/stable-audio-3-small-sfx — officiel
[8] Hugging Face — stabilityai/stable-audio-3-small-sfx-base — https://huggingface.co/stabilityai/stable-audio-3-small-sfx-base — officiel
[9] Comfy-Org — template « audio_stable_audio_3_medium » (catégories de reprompt : SFX, One-shot, Instrument ; lu dans le paquet comfyui-workflow-templates sur le Spark) — https://github.com/Comfy-Org/workflow_templates — officiel (template écrit pour SA3 Medium ; les exemples d'effets se transposent à small-SFX)
[10] Blog Comfy — Stable Audio 3.0 Day-0 Support — https://blog.comfy.org/p/stable-audio-3-day-0-support — officiel
[11] ComfyUI docs — Stable Audio 3 — https://docs.comfy.org/tutorials/audio/stable-audio/stable-audio-3 — officiel
[12] ComfyUI — `comfy/samplers.py` (branche négative ignorée avec CFG 1) et `comfy/model_base.py` (StableAudio3 : `seconds_total` à partir de la longueur du latent) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/samplers.py — officiel (code)
[13] jurn.link — How to install Stable Audio 3.0 small-SFX… — https://jurn.link/dazposer/index.php/2026/05/22/how-to-install-stable-audio-3-0-small-sfx-safetensors-and-run-it-in-comfyui/ — communauté
[14] r/StableDiffusion (snapshot) — Stable Audio 3.0 Day-0 Support in ComfyUI — https://reddit.sentinel-team.org/posts/1tj7afx/snapshots/2026-05-21T18%3A20%3A48.87163Z — communauté
[15] Dubspot — Stable Audio 3 review — https://blog.dubspot.com/stable-audio-3-review — communauté
[16] fal.ai — Stable Audio 3 Small SFX Base (paramètres de l'API) — https://fal.ai/models/fal-ai/stable-audio-3/small/sfx/base/text-to-audio/llms.txt — communauté/service
[17] ComfyUI notes — Conditioning Zero Out (CFG 1 et le négatif) — https://comfyui.nomadoor.net/en/notes/conditioning-zero-out/ — communauté
[18] Studio — guide `poradniki/stable-audio-3-sfx.md` — notre configuration
