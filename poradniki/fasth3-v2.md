# FastH3 V2 — jak promptować

## Jak model słucha
FastH3 V2 to destylowana (DMD2) wersja MiniMax H3 od zespołu FastVideo: obraz i dźwięk w **dokładnie 8 krokach**. **Prompt piszesz tak samo jak dla H3** — ta sama struktura trzech pól, znaczniki `<d>`, ID mówiących, opis po angielsku. Szczegóły: poradnik `minimax-h3`.

## Struktura promptu
Jak w H3: najpierw cała scena (miejsce, postać, co się dzieje), potem ujęcia z czasem, ruchem kamery i dźwiękiem w jednym bloku; osobno ambient i muzyka spoza sceny.

## Na co jest wrażliwy / pułapki
- **Liczba kroków jest stała (8)** — model jest trenowany dokładnie na 8 kroków; zmiana pogarsza jakość.
- Długość „przyciąga się” do siatki 17 klatek (17k+5) przy 24 kl./s; krótszy bok natywnie 768 px, wymiary zaokrąglane do wielokrotności 32.
- **Na Sparku FastH3 V2 jest ok. 20–30% wolniejszy niż zwykły H3 w trybie szybkim** (najpewniej brak szybkich jąder dla rzadkiej uwagi na GB10) — warto porównać oba na tym samym prompcie i seedzie.
- Jak w H3: brak negatywnego promptu; nie nazywaj tego, czego ma nie być.

## Przykład
Ten sam co w poradniku H3 — format jest identyczny.

## Parametry, które realnie zmieniają wynik
- **Długość** i **proporcje**. Kroki — nie zmieniać.

## Źródła (dostęp 2026-10-05)
- ComfyUI — FastVideo FastH3: https://docs.comfy.org/tutorials/video/minimax/minimax-h3-fastvideo
- Hugging Face — FastVideo-FastH3-8-Step-V2: https://huggingface.co/FastVideo/FastVideo-FastH3-8-Step-V2
- Kombitz — FastH3 V2 w ComfyUI: https://www.kombitz.com/2026/09/16/fasth3-v2-8-step-minimax-h3-video-generation-in-comfyui/
- Pomiary: test własny na Sparku.
