# Qwen-Image-Edit 2511 — jak promptować

## Jak model słucha
Model edycji obrazu poleceniem, nastawiony na **zachowanie spójności** (tożsamość postaci, styl, układ) i edycję tekstu w obrazie. Pierwszy obraz jest traktowany jako **główny** (płótno) — to on się zmienia; drugi jest referencją (w Studiu: do dwóch obrazów). Wynik ma rozmiar ok. 1 MP w proporcjach obrazu 1 (Studio skaluje go przed edycją), nie rozmiar oryginału. Polecenie pisz **po angielsku**, prostą prozą, jako polecenie (czasownik na początku), nie opis gotowego obrazu.

## Struktura polecenia
`[operacja: Replace / Change / Remove / Add…] + [cel i miejsce w kadrze] + [na co / z którego obrazu, konkretnie] + [co ma zostać bez zmian]`
- Do obrazów odwołuj się jako **„image 1”, „image 2”** — w kolejności wgrania (nie `<image1>` — to składnia Qwen-Image 2.1 Edit).
- Zawsze dopisz, co zostaje — krótko, hurtem i twierdząco: „Keep the face, pose, background and lighting unchanged.” Nie opisuj szczegółowo wyglądu tego, co ma zostać (model zacznie to przerysowywać).
- Tożsamość osoby z referencji wskaż obrazem („the woman from image 2”), nie opisuj twarzy słowami.
- Wzór: „Place the person from image 2 into the scene in image 1, matching the lighting and perspective. Keep the rest of image 1 unchanged.”
- Napis w obrazie: w cudzysłowie, dosłownie, w swoim języku („Replace the text "OPEN" with "ZAMKNIĘTE"”); polskie znaki — niepotwierdzone.
- Jedna operacja na polecenie; złożoną edycję zrób łańcuchem (wynik → nowe wejście).

## Na co jest wrażliwy / pułapki
- Ogólne polecenie („zrób ładniej”) = niespodziewane zmiany w całym obrazie. Im konkretniej, tym mniej zmienia się reszta.
- Referencje o podobnym kadrze i perspektywie łączą się lepiej.
- Obraz potrafi się lekko przesunąć lub przybliżyć względem wejścia — przy edycjach lokalnych dopisz „keep the framing and camera angle unchanged”.
- Skóra bywa „plastikowa” — przy portretach poproś o naturalną fakturę skóry.
- Wag `(słowo:1.3)` i negatywów nie ma — nawiasy trafią do modelu jako tekst.
- Tryb szybki (Lightning, 4 kroki, CFG 1, ok. 30 s) — do prób, gubi fakturę; tryb jakości (40 kroków, CFG 4, ok. 7 min) — wyraźnie dokładniejszy w detalu.

## Przykłady (struktura)
- „Change the season in image 1 to late autumn: bare trees, wet leaves on the ground. Keep the buildings, the people and the camera angle unchanged.”
- „Replace the sofa fabric in image 1 with the material from image 2. Keep the shape of the sofa, the room and the lighting unchanged.”

## Parametry, które realnie zmieniają wynik
- **Tryb** szybki / jakość. **Seed** — przy stałym seedzie widać wpływ samego polecenia.

## Źródła (dostęp 2026-10-05)
- Qwen/Qwen-Image-Edit-2511 — karta modelu: https://huggingface.co/Qwen/Qwen-Image-Edit-2511
- QwenLM/Qwen-Image — README i przepisywacz poleceń edycji: https://github.com/QwenLM/Qwen-Image
- Scenario — Advanced Editing with Qwen Models: https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models
- Replicate — qwen-image-edit-2511: https://replicate.com/qwen/qwen-image-edit-2511
- RunComfy — Qwen Image Edit 2511 in ComfyUI: https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing
