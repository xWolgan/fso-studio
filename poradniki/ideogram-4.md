# Ideogram 4 — jak promptować

## Jak model słucha
Ideogram 4 (otwarte wagi) był trenowany **wyłącznie na opisach w strukturze JSON** — z ramkami położenia (bbox), paletami kolorów i dosłownym tekstem do wyrysowania. Zwykły, krótki prompt prozą „nie działa”: autorzy piszą wprost, że zwykle wywołuje ostrzeżenie bezpieczeństwa. W naszym teście na Sparku krótki prompt dał szary obraz z narysowanym (z literówkami) napisem „Image blocked by safety filter”; ten sam pomysł zapisany w JSON — czysty, precyzyjny plakat.

## Struktura promptu (kolejność kluczy ma znaczenie)
```json
{
  "high_level_description": "1–2 zdania o całym obrazie",
  "style_description": {
    "aesthetics": "...",
    "lighting": "...",
    "photo": "... (TYLKO dla fotografii; wtedy medium: photograph)",
    "medium": "...",
    "color_palette": ["#1B1B2F", "#E4DED3"]
  },
  "compositional_deconstruction": {
    "background": "...",
    "elements": [
      {"type": "obj",  "bbox": [y_min, x_min, y_max, x_max], "desc": "...", "color_palette": ["#..."]},
      {"type": "text", "bbox": [y_min, x_min, y_max, x_max], "text": "DOSŁOWNY NAPIS", "desc": "krój, wielkość, ułożenie", "color_palette": ["#..."]}
    ]
  }
}
```
- Wymagane jest tylko `compositional_deconstruction` (z `background` i `elements`); `high_level_description` mocno zalecane.
- `style_description`: wymagane `aesthetics`, `lighting`, `medium`; dokładnie **jedno z** `photo` (fotografia) **albo** `art_style` (wszystko inne). Kolejność: fotografia — `aesthetics, lighting, photo, medium, color_palette`; nie-fotografia — `aesthetics, lighting, medium, art_style, color_palette`.
- Elementy: `obj` → `type, bbox, desc, color_palette`; `text` → `type, bbox, text, desc, color_palette`. Napis do wyrysowania idzie do pola **`text`**, opis wyglądu do `desc`.
- **bbox**: `[y_min, x_min, y_max, x_max]`, liczby 0–1000, początek w lewym górnym rogu. Np. `[80, 100, 300, 900]` = pas u góry obrazu, prawie na całą szerokość.
- **Kolory**: tylko wielkie litery `#RRGGBB`; w stylu do 16, w elemencie do 5.

## Na co jest wrażliwy / pułapki
- Proza zamiast JSON → halucynacje i fałszywe „zablokowane przez filtr”.
- Zła kolejność kluczy, małe litery w hex, brak `text` przy elemencie tekstowym — model był uczony na spójnym formacie.
- Polskie znaki wpisuj normalnie (bez zapisu typu `ą`).
- Przycisk „szablon” w Studiu wstawia szkielet — dopasuj go: przy grafice zamień `photo` na `art_style` (za `medium`), przy napisach dopisz pole `text`.

## Przykład (struktura, nie pomysł)
```json
{"high_level_description":"A typographic poster on warm grey paper with a single line of text.",
 "style_description":{"aesthetics":"Swiss minimalism, generous negative space","lighting":"Soft even light","medium":"Letterpress print","art_style":"Minimal editorial typography","color_palette":["#D8D3CA","#2B2A27"]},
 "compositional_deconstruction":{"background":"Uncoated warm grey paper with fine fibres",
  "elements":[{"type":"text","bbox":[440,120,520,880],"text":"GRUPA POSZUKIWAWCZA","desc":"Thin serif capitals, wide letter spacing, centred","color_palette":["#2B2A27"]}]}}
```

## Parametry, które realnie zmieniają wynik
- **Profil** (Turbo 12 kroków / Default 20 / Quality 48) — różnią się liczbą kroków i rozkładem szumu.
- **Proporcje** — bbox odnosi się do całego kadru; przy zmianie proporcji ramki „rozciągają się” razem z nim.

## Źródła (dostęp 2026-10-05)
- Ideogram — prompting (repozytorium otwartego modelu): https://github.com/ideogram-oss/ideogram4/blob/main/docs/prompting.md
- Ideogram — JSON Prompting (4.0): https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/4.-json-prompting-ideogram-4.0
- ComfyUI — Ideogram 4.0 Day-0: https://blog.comfy.org/p/ideogram-4-day-0-support-in-comfyui
- Test własny na Sparku (2026-10-04).
