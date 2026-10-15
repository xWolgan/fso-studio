# LTX 2.3 — jak promptować

## Jak model słucha
LTX 2.3 (Lightricks, 22B) generuje wideo z dźwiękiem; może też przyjąć **obraz** i **dźwięk** jako wejście (ruch synchronizowany z nagraniem). Czyta prompt jak model językowy: **kolejność słów ustala priorytet**. Najlepiej działa **jeden płynny akapit w czasie teraźniejszym**, pisany jak opis ujęcia dla operatora — proza, nie lista słów kluczowych. Wersja destylowana pracuje przy CFG 1 (negatyw nie działa).

## Struktura promptu i kolejność
Styl / medium (jeśli nie fotorealizm) podaj w pierwszej frazie, potem:
1. Główna akcja w jednym zdaniu.
2. Szczegóły ruchu i gestów — chronologicznie.
3. Wygląd postaci / obiektów (precyzyjnie).
4. Tło i otoczenie.
5. Kąt i ruch kamery.
6. Światło i kolor.
7. Zmiany i zdarzenia nagłe.
8. Dźwięk: akustyka miejsca, barwa głosu, ambient; dialog w cudzysłowie.

Długość: proporcjonalnie do długości klipu — praktycznie ok. 80–220 słów (oficjalne źródła się różnią: przewodnik 2.3 mówi, że długie, szczegółowe prompty wygrywają, blog o trzymaniu się promptu radzi zmieścić się w ok. 200 słowach; przewodnik 2.5 podaje 4–8 zdań na proste ujęcie). Krótki prompt przy długim klipie = model „przelatuje” przez akcję. **Jedno główne działanie na 2–3 sekundy** klipu. Bez etykiet typu „Sound:” — dźwięk wpleć w prozę.

## Na co jest wrażliwy / pułapki
- Za dużo zdarzeń w krótkim klipie → model wybiera część albo miesza.
- „Muzyka/dźwięk bez mowy” bywa słabszej jakości (autorzy zaznaczają to w karcie modelu).
- Wymiary podzielne przez 32, liczba klatek postaci 8n+1 (Studio dobiera to samo).

## Przykład (struktura)
„A woman in a grey raincoat stops at the edge of a pier and looks down at the water. She slowly crouches, touches the wet wooden planks with her palm and then stands up again. She is in her forties, short dark hair, no make-up. Behind her, a grey sea and a lighthouse in the fog. The camera starts in a wide shot and slowly pushes in to a medium shot. Overcast, soft light, desaturated blue-grey palette. Wind gusts and waves hit the pylons, a distant foghorn sounds, and she quietly says in Polish, "Już tu nie wrócę."”

## Parametry, które realnie zmieniają wynik
- **Długość** (klatki 8n+1), **proporcje**, **seed**. W workflow Studia tekst → wideo, obraz → wideo i obraz + nagranie mają dwa etapy (pół rozdzielczości + upscaler ×2); pierwsza i ostatnia klatka — jeden przebieg w pełnej rozdzielczości.

## Źródła (dostęp 2026-10-05)
- LTX — LTX-2.3 Prompt Guide: https://ltx.io/blog/ltx-2-3-prompt-guide
- LTX — How to improve LTX-2.3 prompt adherence: https://ltx.io/blog/how-to-improve-ltx-2-3-prompt-adherence
- Hugging Face — Lightricks/LTX-2.3 (karta modelu): https://huggingface.co/Lightricks/LTX-2.3/blob/main/README.md
- deAPI — LTX-2.3 guide: https://deapi.ai/blog/ltx-2-3-video-generation-guide
