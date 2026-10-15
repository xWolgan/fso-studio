# WAN 2.2 — jak promptować

## Jak model słucha
WAN 2.2 (14B; dwa modele: „high noise” buduje kompozycję i ruch, „low noise” dopracowuje detal) generuje wideo **bez dźwięku**. Lubi **szczegółowe, opisowe prompty** (przykłady autorów mają często ponad 100 słów); rozumie angielski i chiński. Mocna strona: ogromna liczba LoRA społeczności.

## Struktura promptu i kolejność
`[obiekt/postać] + [akcja] + [otoczenie] + [ruch kamery] + [światło] + [styl] + [ruch w otoczeniu i tempo]`

Ruch kamery i ruch postaci łącz w jednym zdaniu, np. „The dancer spins in place while the camera smoothly orbits clockwise around her”. Słownik kamery: slow tracking shot, orbit, dolly-in / dolly-out, pan left/right, tilt up/down, crane, handheld follow, static camera, drone pullback.

**Obraz → wideo:** opisuj ruch i zmianę, nie to, co już widać na obrazie.

## Na co jest wrażliwy / pułapki
- **Negatywny prompt działa tylko w trybie pełnej jakości** (CFG 3,5–4). W trybie szybkim (LoRA lightx2v, 4 kroki, CFG 1) jest ignorowany.
- Negatywy dodawaj reaktywnie: najpierw generacja bez nich, potem dopisz konkretny artefakt, który się pojawił (np. „morphing, warping, flickering, face deformation”).
- Natywnie **16 kl./s**, liczba klatek postaci 4n+1 (np. 81 klatek ≈ 5 s); 480p lub 720p. Dłuższe klipy niż ok. 5 s wychodzą poza to, na czym model był uczony.

## Przykład (struktura)
„An old fisherman mends a net on a wooden jetty, his fingers moving quickly through the knots. Gulls circle above, the water glitters. The camera slowly dollies in from a medium shot to a close-up of his hands. Late afternoon golden light, long shadows. Naturalistic documentary style, gentle wind moving the net.”

## Parametry, które realnie zmieniają wynik
- **Tryb**: szybki (lightx2v, 4 kroki; ok. 28 s na 2 s klipu na Sparku) / pełna jakość (20 kroków; ok. 210 s).
- **LoRA** — gdy będą dostępne w Studiu, każda ma zalecaną siłę.

## Źródła (dostęp 2026-10-05)
- Wan-Video / Wan2.2 (oficjalne repozytorium): https://github.com/Wan-Video/Wan2.2
- VEED — Wan 2.2 Prompting Guide: https://www.veed.io/learn/wan-2-2-prompting-guide
- Dreamina — Wan 2.2 Prompt Guide: https://dreamina.capcut.com/ai-video/wan-2-2-prompt
- Pomiary: test własny na Sparku.
