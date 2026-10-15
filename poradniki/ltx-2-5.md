# LTX 2.5 — jak promptować

## Jak model słucha
LTX 2.5 (Lightricks, sierpień 2026) — następca LTX 2.3, z dźwiękiem i **natywnym wieloujęciem**: w jednej generacji potrafi zrobić kilka połączonych ujęć, zachowując postać, scenę, światło, styl i głos. Zasady pisania jak w 2.3: **jeden chronologiczny akapit**, czas teraźniejszy, proza.

## Struktura promptu (sześć elementów z przewodnika Lightricks)
1. **Ujęcie** — plan i terminy operatorskie.
2. **Scena** — światło, kolor, faktura.
3. **Akcja** — jako naturalna sekwencja od początku do końca.
4. **Postacie** — wiek, włosy, ubiór, emocje pokazane fizycznie (gestem, mimiką).
5. **Ruch kamery.**
6. **Dźwięk** — dialog w cudzysłowie, ambient, efekty.

Długość: oficjalnie ok. 4–8 zdań przy prostym ujęciu, więcej przy scenach złożonych — o ile każde zdanie dodaje konkretny szczegół obrazu albo dźwięku. Bez etykiet typu „Sound:”/„Audio:” — dźwięk wpleć w prozę obok akcji, która go wywołuje. Ruch kamery nazywaj zawsze (brak ruchu = „the camera remains static”), inaczej model chętnie sam robi najazd.

**Wiele ujęć (2–4, tylko tekst → wideo):** cała scena jako jeden akapit; każde cięcie nazwij słowami („A hard cut transitions to…”, „The view cuts to a close-up of…”), w nowym ujęciu opisz ponownie, kto w nim jest, i powiedz, czy dźwięk ciągnie się przez cięcie.

## Na co jest wrażliwy / pułapki
- Cięcia muszą być nazwane — inaczej model robi jedno długie ujęcie.
- Postać bez ponownego opisu po cięciu może „przeskoczyć” wyglądem.
- Obraz → wideo: zacznij od zdania zgodnego z obrazem (plan, podmiot, miejsce), potem ruch — jednym ujęciem. Tożsamość postaci z obrazu bywa zmieniana.
- „Rozbudowa” (model sam rozbudowuje prompt) dokłada „kinowy” połysk i ruch kamery, czasem odchodzi od treści — przy stylizacji zostaw ją wyłączoną.

## Przykład (struktura)
„Medium shot of a man in a worn leather jacket sitting alone in an empty bus at night, his face lit by passing streetlights. He looks at a folded letter in his hands and slowly unfolds it. A hard cut transitions to a close-up of the letter: handwritten lines, a coffee stain in the corner. The view cuts back to the man, the same leather jacket, as he folds the letter again and looks out of the window. The engine drone and the rattle of the windows continue across both cuts as he exhales softly.”

## Parametry, które realnie zmieniają wynik
- **Długość**, **proporcje**, **seed**.
- **Rozbudowa** (zaawansowane, domyślnie wyłączona) — przepisuje prompt modelem Gemma 4 E2B; dodaje ok. 1–2 min.

## Źródła (dostęp 2026-10-05)
- LTX — LTX-2.5 Prompt Guide: https://ltx.io/blog/ltx-2-5-prompt-guide
- LTX Docs — Prompting Guide: https://docs.ltx.io/api-documentation/implementation-guides/prompting-guide
- deAPI — LTX-2.5 Prompt Guide (wieloujęcia, dźwięk): https://deapi.ai/blog/ltx-2-5-prompting-guide-multi-shot-scenes-native-audio-and-prompts-that-actually-cut
- Runware — LTX-2.5 prompting: https://runware.ai/docs/models/lightricks-ltx-2-5-pro/guides/prompting
- Hugging Face — Lightricks/LTX-2.5: https://huggingface.co/Lightricks/LTX-2.5
