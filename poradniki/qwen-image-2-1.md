# Qwen-Image 2.1 — jak promptować

## Jak model słucha
Duży model obrazu z bardzo dobrym rozumieniem długich opisów i **renderowaniem tekstu** (gęsty drobny tekst, układy plakatów, slajdów, infografik). Pracuje przy CFG 1 — negatywny prompt nie działa. Ma wbudowany, **domyślnie wyłączony** „rozszerzacz promptu”: mały LLM najpierw przemyśli, a potem przepisze Twój prompt na dłuższy, zanim powstanie obraz — to trwa dłużej, ok. 1–2 min (w Studiu: przełącznik „model sam rozbudowuje prompt”).

## Struktura promptu
- **Tekst → obraz:** proza: co jest na obrazie → kompozycja → światło i kolor → styl/medium. Napisy: podaj **dokładne słowa** (w cudzysłowie) i opisz, gdzie i jak mają być ułożone (krój, wielkość, kolejność).
- **Edycja (obrazy referencyjne):** odwołuj się do obrazów po numerze: `<image1>`, `<image2>`…; mów wprost, co zostaje bez zmian, a co się zmienia. Wzór z dokumentacji: „Keep the character and pose in `<image1>` unchanged, put this light blue denim shirt from `<image2>` on the character, preserve the original facial features, hair, body shape and pose”.
- **Zmiana fragmentu:** zamaluj obszar kolorem na obrazie wejściowym i w poleceniu odwołaj się do koloru: „change the jacket in the red area”.

## Na co jest wrażliwy / pułapki
- Rozszerzacz promptu zmienia Twoje słowa — przy pracy nad konkretnym kadrem zostaw go wyłączonego; włącz, jeśli chcesz zobaczyć interpretację modelu.
- Napisy podawaj dosłownie; parafraza = inny napis.

## Przykłady (struktura)
- „A slide-style infographic on off-white background. Title at the top in bold sans-serif: "Ruch wody". Below, three columns with small line icons and one-line captions. Muted blue and grey palette.”
- Edycja: „Keep the room in `<image1>` unchanged. Replace the view outside the window with the winter landscape from `<image2>`, matching the evening light of the room.”

## Parametry, które realnie zmieniają wynik
- **Kroki**: domyślnie 25 (CFG 1).
- **Rozszerzanie promptu**: tak/nie (patrz wyżej).

## Źródła (dostęp 2026-10-05)
- ComfyUI — Qwen-Image 2.1: https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1
- Qwen-Image 2.1 Prompt Enhancer (opis trybów T2I / edycja): https://github.com/benjiyaya/ComfyUI-Qwen-Image-2.1-Prompt-Enhancer/
