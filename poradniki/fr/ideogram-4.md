# Ideogram 4 — comment prompter

## Comment le modèle écoute
Ideogram 4 (poids ouverts) a été entraîné **exclusivement sur des descriptions structurées en JSON** — avec des cadres de position (bbox), des palettes de couleurs et le texte exact à dessiner. Un prompt ordinaire, court, en prose « ne marche pas » : les auteurs écrivent explicitement qu'il déclenche généralement un avertissement de sécurité. Dans notre test sur le Spark, un prompt court a donné une image grise avec l'inscription dessinée (et pleine de fautes) « Image blocked by safety filter » ; la même idée écrite en JSON — une affiche nette et précise.

## Structure du prompt (l'ordre des clés compte)
```json
{
  "high_level_description": "1–2 phrases sur l'image entière",
  "style_description": {
    "aesthetics": "...",
    "lighting": "...",
    "photo": "... (UNIQUEMENT pour la photographie ; alors medium: photograph)",
    "medium": "...",
    "color_palette": ["#1B1B2F", "#E4DED3"]
  },
  "compositional_deconstruction": {
    "background": "...",
    "elements": [
      {"type": "obj",  "bbox": [y_min, x_min, y_max, x_max], "desc": "...", "color_palette": ["#..."]},
      {"type": "text", "bbox": [y_min, x_min, y_max, x_max], "text": "TEXTE EXACT", "desc": "police, taille, disposition", "color_palette": ["#..."]}
    ]
  }
}
```
- Seul `compositional_deconstruction` est obligatoire (avec `background` et `elements`) ; `high_level_description` est fortement recommandé.
- `style_description` : `aesthetics`, `lighting`, `medium` obligatoires ; exactement **un seul parmi** `photo` (photographie) **ou** `art_style` (tout le reste). Ordre : photographie — `aesthetics, lighting, photo, medium, color_palette` ; hors photographie — `aesthetics, lighting, medium, art_style, color_palette`.
- Éléments : `obj` → `type, bbox, desc, color_palette` ; `text` → `type, bbox, text, desc, color_palette`. Le texte à dessiner va dans le champ **`text`**, la description de son apparence dans `desc`.
- **bbox** : `[y_min, x_min, y_max, x_max]`, nombres de 0 à 1000, origine dans le coin supérieur gauche. P. ex. `[80, 100, 300, 900]` = une bande en haut de l'image, presque sur toute la largeur.
- **Couleurs** : uniquement en majuscules `#RRGGBB` ; jusqu'à 16 dans le style, jusqu'à 5 par élément.

## Points sensibles / pièges
- De la prose au lieu du JSON → hallucinations et faux « bloqué par le filtre ».
- Mauvais ordre des clés, minuscules dans l'hexadécimal, absence de `text` dans un élément texte — le modèle a appris sur un format cohérent.
- Les caractères accentués (é, ç, ą…) s'écrivent normalement (sans notation d'échappement du type `é`).
- Le bouton « gabarit » du Studio insère un squelette — adapte-le : pour un visuel non photographique, remplace `photo` par `art_style` (après `medium`) ; pour du texte, ajoute le champ `text`.

## Exemple (structure, pas idée)
```json
{"high_level_description":"A typographic poster on warm grey paper with a single line of text.",
 "style_description":{"aesthetics":"Swiss minimalism, generous negative space","lighting":"Soft even light","medium":"Letterpress print","art_style":"Minimal editorial typography","color_palette":["#D8D3CA","#2B2A27"]},
 "compositional_deconstruction":{"background":"Uncoated warm grey paper with fine fibres",
  "elements":[{"type":"text","bbox":[440,120,520,880],"text":"GROUPE DE RECHERCHE","desc":"Thin serif capitals, wide letter spacing, centred","color_palette":["#2B2A27"]}]}}
```

## Paramètres qui changent vraiment le résultat
- **Profil** (Turbo 12 étapes / Default 20 / Quality 48) — ils diffèrent par le nombre d'étapes et la planification du bruit.
- **Format** — la bbox se rapporte au cadre entier ; si tu changes le format, les cadres « s'étirent » avec lui.

## Sources (consultées le 2026-10-05)
- Ideogram — prompting (dépôt du modèle ouvert) : https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md
- Ideogram — JSON Prompting (4.0) : https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0
- ComfyUI — Ideogram 4.0 Day-0 : https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui
- Notre propre test sur le Spark (2026-10-04).
