<!-- Karta modelu dla promptmakera. modele: z-image-turbo -->
# Z-Image Turbo (Tongyi-MAI / Alibaba) — szybki tekst → obraz

## Czym jest i do czego się nadaje (w tym: czego NIE robi dobrze)
- Model 6B (single-stream DiT, S3-DiT), wersja **destylowana na 8 kroków**, bez CFG; Apache 2.0 [1][4] (oficjalne). Enkoder tekstu: Qwen3 4B [5] (nasza konfiguracja).
- W Studiu: **kilka sekund na obraz — do szukania kierunku i szkiców** [5] (nasza konfiguracja). Finalną jakość, gęsty tekst i trudną kompozycję porównaj z Qwen-Image 2.1.
- Mocne strony: fotorealizm i estetyka (destylat często przewyższa nauczyciela na 100 krokach w ocenie jakości) [4] (oficjalne), **dwujęzyczny tekst w obrazie: chiński i angielski** [1][4] (oficjalne).
- Czego NIE robi dobrze:
  - **różnorodność niska** — oficjalna tabela: Turbo „diversity: low”; w OneIG różnorodność 0,139 vs 0,194 w modelu bazowym [1][4] (oficjalne). Zmiana seeda często daje bardzo podobny obraz [10] (społeczność);
  - **styl**: Turbo „excels in photorealistic image generation”, a „wide range of artistic styles” karta przypisuje modelowi bazowemu Z-Image [1] (oficjalne); wynik OneIG-Style nieco niższy niż w bazie [4];
  - wiedza o świecie, rozumienie intencji, złożone rozumowanie — ograniczone (oficjalnie mówią to o 6B bez rozszerzacza) [4];
  - **negatyw nie działa w ogóle** [2] (oficjalne);
  - tekst w innych językach niż zh/en — polskie znaki **niepotwierdzone**.

## Co uczestnik ustawia w Studiu (pola, wejścia, parametry z naszego YAML — i jak wpływają na prompt)
Źródło: `modele/obraz/z-image-turbo.yaml` + `workflows/obraz/zimage-turbo_tekst-na-obraz.api.json` [5] (nasza konfiguracja).
- **prompt** — jedno pole → `CLIPTextEncode` z enkoderem Qwen3 4B. ComfyUI owija go w szablon czatu `<|im_start|>user … <|im_end|><|im_start|>assistant`, **bez system promptu i bez rozszerzacza** [6] (kod ComfyUI). Nikt nie poprawi promptu po drodze — piszesz go od razu w formie „rozszerzonej”.
- **Brak negatywu**: gałąź negatywna to `ConditioningZeroOut`, CFG 1 [5]. Oficjalnie: model nie używa negatywnych promptów [2].
- **Brak ucinania**: oficjalny kod diffusers ucina tekst do 512 tokenów (zalecają podnieść do 1024) [2], ale tokenizer ComfyUI nie ma tego limitu [6] (kod). Długi prompt dojdzie w całości.
- **proporcje** — 16:9 (domyślnie), 21:9, 3:2, 4:3, 1:1, 3:4, 2:3, 9:16; ok. **1 MP**, wymiary ×16 [5]. Natywny rozmiar demo: 1024×1024 [1].
- **seed** — przy niskiej różnorodności to słaba dźwignia; zmiany robi **treść promptu** [1][10].
- **kroki** (zaawansowane) — 4–16, domyślnie 8 (sampler res_multistep, shift 3) [5]. Oficjalnie 9 w diffusers = 8 przejść DiT [1]; praktycy: 8–12, więcej tylko gdy zostaje szum [9] (społeczność). Mniej kroków = szkic.

## Format promptu (język, długość, struktura, znaczniki, negatyw, wagi)
- **Język: angielski** (albo chiński). Trening na opisach dwujęzycznych zh/en [4] (oficjalne); brak dowodu, że chiński daje lepszy obraz [7] (społeczność). Uczestnik ma czytać prompt → angielski. Polski — nie.
- **Długi, szczegółowy opis.** Oficjalnie: „works best with long and detailed prompts” [2]. Praktycy: 80–250 słów jako złoty środek, „setki słów są OK” [9] (społeczność). Teza o „dryfie uwagi po 75–100 tokenach” [8] jest sprzeczna z oficjalnym zaleceniem — ignoruj.
- **Rejestr: rzeczowy, obiektywny opis**, nie poezja. Długie opisy treningowe pisano „plain and objective linguistic style” [4] (oficjalne), a fine-tuning (SFT) robiono na promptach przepuszczonych przez oficjalny rozszerzacz PE [4] — więc model najlepiej rozumie prompty w stylu tego rozszerzacza.
- **Zasady oficjalnego rozszerzacza (pe.py)** [3] (oficjalne, oryginał po chińsku):
  1. zablokuj elementy nienaruszalne: podmiot, liczba, czynność, stan, nazwy, kolory, teksty;
  2. jeśli prośba wymaga pomysłu („zaprojektuj…”, „pokaż jak…”) — najpierw wymyśl konkretne, widzialne rozwiązanie i opisz je;
  3. dodaj profesjonalne detale: **kompozycja, światło i atmosfera świetlna, materiał/faktura, schemat kolorów, warstwy przestrzeni**;
  4. **tekst do wyrenderowania — dosłownie, w angielskich podwójnych cudzysłowach `"…"`**; przy plakacie/menu/UI opisz cały tekst, krój i układ; przy szyldzie/ekranie: treść, położenie, wielkość, materiał;
  5. **zakaz metafor i retoryki emocjonalnej**, zakaz metatagów („8K”, „masterpiece”) i poleceń rysowania.
- **Proza, pełne zdania, nie lista tagów**; boostery z ery SD („masterpiece, best quality, trending on artstation”) nic nie dają [3][11] (oficjalne / społeczność).
- **Negatyw**: wszystko pozytywnie — „sharp focus” zamiast „no blur”, „empty street, only wet cobblestones” zamiast „no people” [2][12] (oficjalne / społeczność).
- **Wagi `(słowo:1.3)` — NIE.** Tokenizer Z-Image w ComfyUI ma `disable_weights=True` — nawiasy i liczby trafiają do modelu jako tekst [6] (kod).
- **Nie mieszaj sprzecznych stylów** (fotorealizm + kreskówka + obraz olejny) [11][12] (społeczność).

## Szkielet promptu
```
[medium i styl: photograph / ink drawing / watercolour painting / collage… + 1 określenie techniki]. [plan i kąt: wide shot / close-up, eye level / high angle], [kompozycja: gdzie stoi podmiot w kadrze].
[podmiot: kto/co, ile, wiek jako etap życia, 2–3 cechy wyglądu], [ubiór/powierzchnia: kolor + materiał], [czynność lub stan].
[otoczenie: 2–3 konkretne elementy z położeniem; pierwszy plan / tło].
[światło: źródło, kierunek, jakość, pora], [paleta: 2–3 kolory z określeniem].
[faktura obrazu: ziarno / pociągnięcia / włókno papieru / raster — jeśli dotyczy]; [dla foto: JEDEN aparat lub obiektyw + JEDEN film].
[tekst w kadrze: gdzie, jakim krojem, reads "DOKŁADNY TEKST" — albo nic].
[ograniczenia pozytywnie: only one figure in the frame / plain untextured background].
```

## Co działa
- **Język operatora**: plan, kąt, rozmieszczenie, światło — model mocno na to reaguje [9][12] (społeczność).
- **Konkret zamiast przymiotników oceniających**: „beautiful”, „nice”, „epic” nie dają nic [11][12] (społeczność); oficjalny PE każe tłumaczyć intencję na widzialne fakty [3].
- **Słownik fotograficzny zamiast „realistic”**: konkretny aparat/obiektyw i film (np. „Kodak Portra 400”, „Ilford HP5”), faktura skóry („visible pores, slight asymmetry”) — przypisane fotografowi z r/StableDiffusion [11] (społeczność). Maks. **jedna** fraza aparatu i **jedna** filmu/światła — więcej rozmywa efekt [11].
- **Rola + 2–3 cechy** zamiast jednego „nacechowanego” słowa („CEO”, „witch” ciągną stereotyp płci, ciała, makijażu) [9] (społeczność). Zamiast „businessman” → „office worker” + cechy.
- **Proste, nie zagracone tło**, gdy liczy się podmiot [9].
- **Tekst w kadrze**: krótki, w cudzysłowie, z miejscem i krojem; wcześnie w prompcie; jeden język na napis; dopisz „no other text in the image” w formie pozytywnej („the rest of the wall is blank”) [3][9][11].
- **Wariacje**: zmieniaj treść promptu (kadr, kąt, porę, rozmieszczenie), nie tylko seed — destylat wraca do tej samej kompozycji [1][10]. Krótszy prompt = więcej swobody układu, długi = kotwiczy kompozycję [10] (społeczność, w kontekście LoRA różnorodności).
- **Stały seed przy dopracowaniu**, zmiana jednej rzeczy naraz [9].

## Biasy i pułapki
- **Domyślnie „stockowa fotografia urody”**: gładkie, symetryczne twarze, połysk — gdy brak aparatu, filmu i niedoskonałości [11] (społeczność). Trening z nagrodą m.in. za „AI-content detection perception” (realizm, „nie wygląda na AI”) i estetykę [4] (oficjalne) — model ciągnie do wypolerowanego realizmu.
- **Niska różnorodność**: kolejne seedy ≈ ten sam kadr, ta sama twarz [1][4][10]. Jeśli uczestnik chce serii — każdy wariant opisz inaczej.
- **Ludzie**: dookreśl wiek, budowę, pochodzenie, ubiór; nie zostawiaj tego modelowi (nacechowane słowa → stereotyp) [9]. Czy model ma domyślną etniczność twarzy — **niepotwierdzone** (przykłady w karcie HF są z chińskimi postaciami [1]).
- **„Plastik”** = zwykle brak słów o fakturze (pory, splot tkaniny, ziarno, pociągnięcia) [11] (społeczność).
- **Przeładowanie** listą detali i sprzecznymi poleceniami → chaos [12] (społeczność).
- **Polskie znaki w napisach**: niepotwierdzone (oficjalnie tylko zh/en) [1][4]. Krótko, sprawdź wynik; kluczowe napisy → Ideogram 4 lub Qwen-Image 2.1 w Studiu [13] (nasza konfiguracja).
- **Kroki**: przy zbyt wielu krokach destylaty bywają przepalone/zartefaktowane (niepotwierdzone dla naszych 4–16); trzymaj 8.

## Poza fotorealizmem
- Turbo to model nastawiony na fotorealizm [1] — styl trzeba **wymusić konsekwentnie**: medium jako pierwsze słowa, ślad narzędzia w opisie, **zero słownictwa aparatu** (obiektyw, przysłona, „shot on…”, film stock) przy rysunku/malarstwie — inaczej wraca zdjęcie [11][12] (społeczność, wniosek z zakazu mieszania stylów).
- Frazy z presetów praktyków (niepotwierdzone kontrolnie) [11] (społeczność):
  - akwarela: „watercolor painting, loose brushwork, pigment pooling”;
  - komiks: „western comic book style, strong inked outlines, bold graphic look”;
  - analog: „analog film photograph, grainy texture, warm tonal shifts, slight vignette”;
  - anime: „anime artwork, studio anime key visual”; manga z rastrem; pixel art; witraż; art déco.
- **Pixel art** model bazowo potrafi (LoRA tylko dodaje detal) [14] (społeczność).
- Mnogość LoRA stylu (anime, „artist style”) na Civitai dla Turbo [15] (społeczność) sugeruje, że czyste style ilustracyjne bez LoRA są słabsze; Studio nie wystawia tu LoRA [5].
- **Taśma / ziarno / archiwum**: jeden film + opis widocznych śladów (ziarno, przebarwienia, rysy, winieta); to rejestr, w którym Turbo jest najpewniejszy [11].
- **Abstrakcja / kolaż**: opisz rzeczowo kształty, krawędzie, płaszczyzny koloru, fakturę papieru i ich położenie; bez metafor (PE ich zakazuje [3]). Efekt — niepotwierdzony testem; jeśli nie wychodzi, przejdź na Qwen-Image 2.1.
- **Nastrój z wiersza** przetłumacz na światło, paletę, kadr i materię — metafora wprost zostanie zignorowana albo dosłownie narysowana [3].

## Ruch / czas / dźwięk
Nie dotyczy. Szkic do pierwszej klatki wideo: proporcje jak wideo (16:9), prosty układ, miejsce na ruch; po wyborze kierunku zrób finał w Qwen-Image 2.1.

## Sprawdź przed wysłaniem
- [ ] Angielski, pełne zdania, rzeczowo — bez metafor i ocen („beautiful”, „epic”).
- [ ] Medium/styl na początku; przy nie-foto zero słów o aparacie i filmie.
- [ ] Plan, kąt, rozmieszczenie, światło (źródło + kierunek), paleta, faktura.
- [ ] Ludzie: wiek, budowa, ubiór, cechy wprost; bez nacechowanych etykiet.
- [ ] Napisy krótkie, w `"…"`, z miejscem i krojem — albo żadnych.
- [ ] Brak: negatywów („no…”), wag `( :1.3)`, „masterpiece/8K”, list tagów.
- [ ] ~80–250 słów.
- [ ] Wariant = inny opis, nie tylko inny seed.

## Źródła
[1] Tongyi-MAI/Z-Image-Turbo — karta modelu — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo — oficjalne
[2] Tongyi-MAI/Z-Image-Turbo — dyskusja #8 „PROMPTING GUIDE” (przypięta, odpowiedzi autorów) — https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8 — oficjalne
[3] Tongyi-MAI Space — pe.py (szablon rozszerzacza promptu) — https://huggingface.co/spaces/Tongyi-MAI/Z-Image-Turbo/blob/main/pe.py — oficjalne
[4] Z-Image: An Efficient Image Generation Foundation Model with Single-Stream Diffusion Transformer (arXiv 2511.22699) — https://arxiv.org/abs/2511.22699 — oficjalne
[5] Nasza konfiguracja: modele/obraz/z-image-turbo.yaml; workflows/obraz/zimage-turbo_tekst-na-obraz.api.json (Qwen3 4B, CFG 1, res_multistep, shift 3, ConditioningZeroOut) — nasza konfiguracja
[6] ComfyUI — comfy/text_encoders/z_image.py (szablon czatu, `disable_weights=True`, brak limitu długości) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/z_image.py — oficjalne (kod)
[7] Wyniki wyszukiwania: Chinese vs English prompt (brak kontrolnego porównania) — https://aioz.network/blog/z-image-turbo-a-bilingual-image-generation-model-for-text-rich-visuals-2 — społeczność
[8] Fliki — teza o dryfie po 75–100 tokenach (patrz [11]) — https://fliki.ai/blog/z-image-turbo-prompting-guide — społeczność
[9] illuminatianon — Z-Image-Turbo Prompting Guide (gist + komentarze) — https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32 — społeczność
[10] Floyo — Z-Image Turbo Text to Image With Diversity LoRA — https://www.floyo.ai/workflows/z-image-turbo-text-to-image-with-div-efye86mk80ax — społeczność
[11] Fliki — Z-Image Turbo Prompting Guide: 25 Style Presets, Realism Secrets — https://fliki.ai/blog/z-image-turbo-prompting-guide — społeczność (sprzedawca, cytuje r/StableDiffusion)
[12] fal — Z-Image Turbo prompt guide — https://fal.ai/learn/devs/z-image-turbo-prompt-guide — społeczność (sprzedawca)
[13] Nasza konfiguracja: notatki własne (niepublikowane) (Ideogram 4 do napisów), modele/obraz/ — nasza konfiguracja
[14] elusarca — pixel art style LoRA for Z-Image Turbo — https://huggingface.co/reverentelusarca/elusarca-pixel-art-style-lora-zimage-turbo — społeczność
[15] Civitai — Anime Style Lora For Z-Image-Turbo — https://civitai.com/models/2186181/anime-style-lora-for-z-image-turbo — społeczność
