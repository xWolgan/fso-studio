# MiniMax H3 — jak promptować

## Jak model słucha
H3 generuje **obraz i dźwięk stereo razem** (dialogi, efekty, ambient, muzyka). Prompt to **scenariusz z osią czasu**, nie opis obrazka: kolejne ujęcia, ruch kamery, kto mówi i co słychać. Prompt pisz **po angielsku** (dialogi i napisy na ekranie mogą być w swoim języku — dosłownie). Pracuje przy CFG 1: **nie ma negatywnego promptu**, a nazwanie niechcianej rzeczy dodaje ją do opisu.

## Struktura promptu (oficjalny układ trzech pól)
```
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:04.000, the camera cuts to ...

overall_soundscape: ...

non_diegetic_music: ...
```
Pola rozdzielone pustą linią, w tej kolejności.
- **integrated_multimodal_description** — ujęcia `[Shot 1]`, `[Shot 2]`… z obrazem, akcją, ruchem kamery i dźwiękiem diegetycznym (dialogi, efekty, muzyka w scenie) w jednym bloku. Najpierw cała scena (miejsce, postać, co się dzieje), potem ujęcia.
- **overall_soundscape** — 1–4 zdania: ambient, odgłosy akcji, dźwięki niewerbalne. `N/A` tylko przy pełnej ciszy.
- **non_diegetic_music** — 1–3 zdania o muzyce słyszanej tylko przez widza; `N/A`, jeśli jej nie ma.
- **Dialog:** w znacznikach `<d>`, z ID mówiącego i tagiem języka w nawiasach kwadratowych: `(S1) says: <d>[English] Exact words.</d>` (nie `<d>English: …</d>`); w środku `<d>` tylko tag języka i słowa, kwestię zakończ kropką/?/!. Każdy głos ma stały ID `(S1)`, `(S2)`, powtarzany w każdym ujęciu, w którym mówi; głos (wiek, płeć, barwa, tempo) opisz przy pierwszym wystąpieniu, poza `<d>`. Postać, która nie mówi, nie dostaje ID.
- **Napis na ekranie:** w cudzysłowie, dosłownie, w oryginalnym języku.
- **Głos zza kadru:** „says in an off-screen voiceover” + informacja, że usta pozostają zamknięte.
- **Kamera:** typ ruchu + amplituda + tempo, naturalnym językiem w zdaniu ujęcia (np. „the camera pushes in with small amplitude at slow speed”); słownik: static, zoom in/out, push in / pull out, pan, truck, tilt, pedestal, arc, tracking, shake slightly/strongly, POV, roll.
- **Ujęcia:** `[Shot 1]` bez czasu; kolejne z czasem cięcia `At MM:SS.mmm` (rosnąco, mniejszym niż długość klipu). Każde cięcie = nowa informacja (miejsce, stan, punkt widzenia).
- **Obraz → wideo — linię wyrównania piszesz sam.** Studio/węzeł ComfyUI nic nie dopisuje do promptu (węzeł tylko oznacza obrazy jako `<Picture n>`). Gdy podajesz klatki, **pierwsza linia promptu** to dosłownie (potem pusta linia, potem trzy pola):
  - tylko pierwsza klatka (I2VA):
    `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
  - pierwsza i ostatnia (FL2VA) — `S.SS` = długość klipu z dwoma miejscami po przecinku, `N` = numer ostatniego ujęcia:
    `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
  - tylko ostatnia klatka (L2VA):
    `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`
  - bez klatek (tekst → wideo): bez tej linii.
- **Inspiracje (Ref2VA):** gdy podasz obrazy/wideo/dźwięki-inspiracje, model używa innego formatu — sześć sekcji `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music` ze znacznikami `<Picture n>`, `<Video n>`, `<Audio n>`; pierwsza/ostatnia klatka są wtedy ignorowane. Szczegóły zna asystent promptów Studia.

## Na co jest wrażliwy / pułapki
- „No on-screen text” dopisuje słowo „tekst” do opisu → zamiast tego „the sign above the door is blank”.
- Długość ujęć: jedno wyraźne działanie na ujęcie. Klip oficjalnie 4–15 s (w Studiu domyślnie 10 s); model był uczony na ok. 5–15 s — **ustawiaj co najmniej 5 s**.
- Polski nie należy do stabilnie wspieranych języków dialogu — kwestie krótkie i proste (`<d>[Polish] …</d>`); w opisie nie mieszaj polskiego z angielskim (model może czytać opis na głos).
- Rozdzielczość natywna: krótszy bok 768 px; w Studiu 480p (domyślnie) lub 720p.

## Przykład (struktura)
```
integrated_multimodal_description: [Shot 1] Cinematic live-action. A narrow kitchen at night, one lamp on. Medium shot, static camera. An old woman with a low, slightly hoarse voice slowly peels an apple at the table; the knife scrapes softly. (S1) says: <d>[Polish] Jeszcze chwilę.</d> She closes her lips and keeps peeling silently. [Shot 2] At 00:04.000, the camera cuts to a close-up of her hands and pushes in with small amplitude at slow speed; the peel falls in one long ribbon onto the oilcloth.

overall_soundscape: A refrigerator hum, a distant tram outside, the soft scrape of the knife.

non_diegetic_music: N/A
```

## Parametry, które realnie zmieniają wynik
- **Tryb**: szybki (LoRA turbo, 8 kroków; z inspiracjami i klatkami kluczowymi 4 kroki; ok. 40–44 s na 2 s klipu na Sparku; nieco słabszy dźwięk i ruch) / pełna jakość (20 kroków; ok. 84 s).
- **Długość** i **proporcje** (natywnie 768 px krótszego boku).

## Źródła (dostęp 2026-10-05)
- MiniMax — Video Prompt Writing Guide (linie wyrównania, format `<d>[Language] …</d>`): https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_base_en.md
- ComfyUI — kod węzłów H3 (węzeł nie dopisuje linii wyrównania): https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py
- ComfyUI — MiniMax H3 Prompt Guide (oficjalny format): https://docs.comfy.org/tutorials/video/minimax/minimax-h3-prompt-guide
- RunDiffusion — H3 Prompt Guide: https://www.rundiffusion.com/minimax-h3-prompt-guide
- DEV — H3 camera motion, timing, audio: https://dev.to/jaysean_brambila_1f12d6cc/minimax-h3-prompt-engineering-camera-motion-timing-and-native-audio-1a8g
- Pomiary czasu: test własny na Sparku.
