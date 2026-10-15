<!-- Karta modelu dla promptmakera. modele: qwen-image-2-1-edycja, qwen-image-edit-2511 -->
# Edycja obrazu poleceniem: Qwen-Image 2.1 Edit i Qwen-Image-Edit 2511

> Dwa RÓŻNE modele z różną składnią odwołań do obrazów. Najpierw sprawdź, który wybrał uczestnik.
> **2.1 Edit → `<image1>`, `<image2>`**. **Edit 2511 → „image 1”, „image 2”** (nigdy `<image1>`).

## Czym jest i do czego się nadaje (w tym: czego NIE robi dobrze)
- **Qwen-Image 2.1 Edit** (`qwen-image-2-1-edycja`) — ten sam model 7B co generacja 2.1, z enkoderem Qwen3-VL 8B; do 10 obrazów referencyjnych oficjalnie, w Studiu **2** [1][2] (oficjalne), [20] (nasza konfiguracja). Licencja niekomercyjna. Zachowanie tożsamości osób i produktów, edycja lokalna przez zamalowanie fragmentu kolorem [1][2].
- **Qwen-Image-Edit 2511** (`qwen-image-edit-2511`) — starsza linia Edit (20B, enkoder Qwen2.5-VL 7B), Apache 2.0; w Studiu do 2 obrazów [5][21]. Nowości wobec 2509: mniej „dryfu” obrazu, lepsza spójność postaci (w tym zdjęcia grupowe z dwóch osobnych osób), wbudowane efekty popularnych LoRA (sterowanie światłem, nowe punkty widzenia), zamiana materiałów w projektach przemysłowych, linie konstrukcyjne [5][6] (oficjalne).
- Linia Edit (2509) jest najlepsza przy **1–3 obrazach**; obsługuje też jako wejście mapy głębi, krawędzi, punktów kluczowych (pozy) [7] (oficjalne, wersja 2509 — dla 2511 niepotwierdzone).
- Czego NIE robią dobrze:
  - 2.1: spójność przy wielu referencjach słabnie od ok. 3 obrazów; przy profilu fryzura potrafi się „przesunąć” [10] (społeczność, wczesna recenzja); skargi na światło, referencje i stałość twarzy [11] (społeczność, sam tytuł wątku). Ma skłonność do przerysowania większej części kadru, niż proszono [12] (społeczność).
  - 2511: przesunięcie/zoom obrazu względem wejścia („pixel drift”), „plastikowa skóra” [16][17] (społeczność); tryb szybki gubi fakturę (porównanie futra 40 vs 4 kroki) [14] (społeczność).
  - Oba: polskie znaki w napisach — niepotwierdzone.

## Co uczestnik ustawia w Studiu (pola, wejścia, parametry z naszego YAML — i jak wpływają na prompt)
Źródło: YAML + workflowy [20][21] (nasza konfiguracja).

**Qwen-Image 2.1 Edit**
- **obraz 1** (wymagany) = **płótno**: to on jest edytowany; wynik ma **jego rozmiar** (workflow `resolution: 0` → natywny rozmiar zaokrąglony do wielokrotności 32) [2][3][20]. Duże zdjęcie = wolno (3000×4000 ≈ 12 MP) [2] (oficjalne).
- **obraz 2** (opcjonalny) = źródło materiału, stroju, postaci, stylu.
- **polecenie** — jedno pole → `TextEncodeQwenImage21`. Enkoder **sam wstawia przed każdym obrazem znacznik `<image1>`, `<image2>`** [4] (kod ComfyUI) — dlatego w poleceniu odwołujesz się dokładnie tak: `<image1>`, `<image2>` [2] (oficjalne).
- Brak negatywu (pusty, CFG 1) [2][20]. **kroki** 10–50, domyślnie 25; lokalne drobne zmiany działają już przy niskich krokach, przebudowa całego kadru potrzebuje pełnych 25 [2] (oficjalne).
- **„model sam rozbudowuje polecenie”** (domyślnie WYŁ.) — oficjalny PE-I2I (Qwen3.5 9B, patrzy na obrazy) z oficjalnym system promptem w naszym workflow, z trybem myślenia (od 12.10; oficjalnie PE jest do niego trenowany — ok. 1–2 min dłużej) [20]. Gdy promptmaker pisze precyzyjne polecenie — zostaw WYŁ.

**Qwen-Image-Edit 2511**
- **obraz 1** = płótno; przed edycją skalowany węzłem `FluxKontextImageScale` do ok. 1 MP (najbliższa z rozdzielczości Kontext) — wynik ma ten rozmiar, nie oryginalny [21][13].
- **obraz 2** = referencja (materiał, postać, scena).
- **polecenie** → `TextEncodeQwenImageEditPlus`. Enkoder dokleja przed tekstem „Picture 1: [obraz] Picture 2: [obraz]” i system „Describe the key features of the input image…, then explain how the user's text instruction should alter or modify the image” [8] (kod ComfyUI).
- **tryb**: **szybki** (domyślny) = LoRA Lightning 4 kroki, CFG 1, ok. 30 s; **jakość** = 40 kroków, CFG 4, ok. 7 min [21]. Negatyw pusty, nieedytowalny. Workflow ma już `index_timestep_zero` (metoda referencji przeciw dryfowi/„plastikowi”) [21][17].
- Oficjalne repo: „bez przepisania polecenia edycja bywa niestabilna” [9] (oficjalne) — u nas przepisywaczem jest promptmaker.

## Format promptu (język, długość, struktura, znaczniki, negatyw, wagi)
- **Język: angielski** (prosta proza). Oficjalny PE-I2I: opis po chińsku tylko dla polecenia po chińsku, po angielsku dla wszystkich innych języków [20] (oficjalne). 2511: oficjalne przykłady po angielsku i chińsku [5][9]. Polski — nie.
- **Tekst w obrazie** — w podwójnych cudzysłowach, dosłownie, w swoim języku, z zachowaniem wielkich liter; nie tłumacz [9][20] (oficjalne). Język napisu: (1) jeśli uczestnik podał słowa/język — te; (2) jeśli obraz ma już tekst — język dominujący w obrazie; (3) inaczej — język polecenia uczestnika. Jednojęzycznie, bez par „PL/EN” [20].
- **Forma: polecenie, nie opis gotowego obrazu.** Zacznij od operacji (Replace / Change / Remove / Add / Turn / Place / Relight / Restore…) [20] (oficjalne). Opis „jak generator” sprawia, że model ignoruje wejście [15] (społeczność, Edit Plus).
- **Jeden akapit, bez list, JSON, nagłówków; bez proporcji i rozdzielczości** [20].
- **Długość:** zwięźle — oficjalny rozszerzacz Edit (2511) każe skracać i ograniczać opisowość [9] (oficjalne). 2.1: tyle, ile trzeba, by nic nie było do zgadywania; prosta zamiana = 1–3 zdania; „nowa scena z tym motywem” (sesja, plakat, kompozycja z dwóch obrazów) = buduj scenę, światło i układ szerzej [20] (oficjalne).
- **Struktura (4 części)**: operacja → cel (co, gdzie: „the man on the right”) → specyfikacja zmiany (konkret: kolor, materiał, styl) → **klauzula zachowania** („keep … unchanged”) [15][13][20].
- **Klauzula zachowania krótko i hurtem**: nazwij to, co zostaje, **typem i miejscem**, nie opisuj wyglądu („keep the face, pose, background and lighting unchanged”). Im dokładniej opiszesz coś, co miało zostać, tym bardziej model to przerysuje [20] (oficjalne).
- **Twierdząco**: „keep the background identical to the input” zamiast „do not change the background” [20] (oficjalne).
- **Negatyw**: brak w polu (2.1: CFG 1; 2511: pusty, nieedytowalny) [20][21]. Wag `( :1.3)` nie używaj — obie ścieżki mają `disable_weights=True`, nawiasy idą jako tekst [18] (kod ComfyUI).

**Odwołania do obrazów**
- **2.1:** przy ≥ 2 obrazach **obowiązkowo `<image1>`, `<image2>`** — nie „image 1”, „first image”, „obraz 1” [20][2] (oficjalne). Przy jednym obrazie znacznik nie jest wymagany (oficjalny PE każe go używać dopiero od 2 obrazów) — pisz „the image”; enkoder i tak oznacza pojedynczy obraz jako `<image1>` [4], więc `<image1>` też nie jest błędem. Określ rolę każdego obrazu: który jest płótnem (kompozycja i reszta zostają), co bierzesz z którego [20].
- **2511:** „image 1”, „image 2” (domyślne polecenie w naszym workflow) [21]; enkoder nazywa je wewnętrznie „Picture 1/2” [8], oficjalny przykład SGLang używa „Figure 1/2” [9] — wszystkie trzy to zwykły tekst, wybierz jedno i trzymaj się go (skuteczność porównawcza niepotwierdzona). Kolejność obrazów ma znaczenie [5][13].
- Tożsamość z referencji: **wskaż obraz, nie opisuj twarzy słowami** — opis słowny każe regenerować i psuje podobieństwo [20] (oficjalne).

## Szkielet promptu
Zmiana na jednym obrazie (2.1 i 2511):
```
[Operacja] [cel + położenie w kadrze] [na co: konkret — kolor/materiał/kształt/styl, w mocnym, wyraźnym stopniu]. [Jeśli coś znika lub się przesuwa: co pojawia się w odsłoniętym miejscu]. Keep [co zostaje: typ + miejsce, hurtem] unchanged.
```
Dwa obrazy — Qwen-Image 2.1:
```
Using <image1> as the canvas, [operacja] [cel w <image1>] with [element] from <image2>, [jak ma się dopasować: skala, światło, perspektywa]. Keep [twarz/poza/tło/światło] of <image1> unchanged.
```
Dwa obrazy — Edit 2511:
```
[Operacja] the [cel] in image 1 [with / to] the [element] from image 2, [dopasowanie: światło, skala, perspektywa]. Keep [co zostaje] in image 1 unchanged.
```
Zmiana medium/stylu:
```
Turn the image into [medium] with [2–4 cechy widoczne: kreska, wypełnienie, faktura podłoża, paleta]. Keep the composition, [postacie/obiekty] and their positions unchanged.
```

## Co działa
- **Pełna siła edycji + zamrożenie reszty**: oficjalna zasada PE-I2I — zmień dokładnie nazwany atrybut **mocno i jednoznacznie**, wszystko inne na wierności wejścia. Dwa błędy symetryczne: „przeciek” (zmiana czegoś nienazwanego) i „niedoedytowanie” (wynik wygląda jak wejście) [20] (oficjalne).
- **„change nothing else in the frame”** na końcu — bo 2.1 przerysowuje więcej, niż proszono [12] (społeczność).
- **Zamiana**: „Replace Y with X” [9] (oficjalne). **Jedna operacja na polecenie**, złożone rzeczy łańcuchem (wynik → nowe wejście) [15] (społeczność).
- **Usuwanie**: opisz obiekt i miejsce („the second person from the left”), a odsłonięte miejsce wypełnij spójnie z otoczeniem, ze światłem i cieniem [15][20].
- **Edycja lokalna (2.1)**: uczestnik zamalowuje fragment obrazu 1 kolorem (np. czerwonym) przed wgraniem; w poleceniu nazwij kolor: „…in the red-marked area”; jeśli ten kolor może pojawić się w wyniku, dopisz kolor docelowy [2] (oficjalne).
- **Tekst**: zacytuj stary i nowy napis; zablokuj typografię (krój, kolor, miejsce), bo inaczej dryfuje do domyślnego fontu [15] (społeczność, Edit Plus); oficjalnie: pozycja/kolor/układ tylko, jeśli uczestnik o to prosi [9].
- **Zdjęcia osób**: tożsamość (wiek, płeć, fryzura, mimika, strój) zostaje, zmiany mimiki „subtelne i naturalne” [9] (oficjalne). Skóra: „natural pores, fine detail, texture that matches the lighting of the scene” [17] (społeczność).
- **Stare zdjęcie**: oficjalny szablon „Restore and colorize the photo.” [9] (oficjalne).
- **Światło (2511)**: sterowanie światłem i nowy punkt widzenia są wbudowane [5][6]; społeczność zaczyna takie polecenia od „Relight …” + opis światła [16] (społeczność, niepotwierdzone).
- **Referencje o podobnym kadrze, perspektywie i świetle** łączą się lepiej [13] (społeczność).
- **Tryb szybki 2511 do prób, jakość do finału** — Lightning zmienia fakturę [13][14] (społeczność).

## Biasy i pułapki
- **Pomylona składnia odwołań** (`<image1>` w 2511 albo „image 1” w 2.1) — najczęstszy błąd w tej parze modeli [2][4][8].
- **Przeciek**: wyostrzenie, które zmienia kolory; styl, który zmienia twarz; zmiana stroju, która gubi dodatek; „pomocne” sprzątanie kadru [20] (oficjalne). Nie każ robić niczego, o co uczestnik nie prosił.
- **Medium wejścia jest „tożsamością”**: zdjęcie zostaje zdjęciem, rysunek rysunkiem, chyba że polecenie jawnie celuje w medium [20] (oficjalne). Chcesz zmiany medium — nazwij ją wprost i mocno.
- **Dryf / zoom (2511)**: obraz potrafi się przesunąć o kilka pikseli lub przybliżyć [16]; dlatego klauzula „keep the framing and camera angle unchanged” przy edycjach lokalnych (społeczność).
- **„Plastikowa” skóra (2511)** — zgłaszane na Reddicie [17] (społeczność); u nas już włączone `index_timestep_zero` [21]; w poleceniu proś o fakturę skóry.
- **Rozmiar wyniku**: 2.1 = rozmiar obrazu 1; 2511 = ~1 MP wg obrazu 1. Zmiana proporcji poleceniem nie zadziała — rozszerzenie płótna nazwij jawnie „outpainting” (2.1) [20] albo przytnij obraz wcześniej [15].
- **Wiele postaci z dwóch zdjęć**: 2511 jest w tym lepszy niż 2509 [5]; 2.1 słabnie przy ≥ 3 referencjach [10].

## Poza fotorealizmem
- **Zmiana stylu**: opisz styl jego **kluczowymi cechami wizualnymi**, nie samą nazwą [9] (oficjalne); przy kilku zmianach naraz — opis stylu na końcu polecenia [9]. Przykład składni: „Make this look like a watercolor painting.” [19] (społeczność) — rozwiń o cechy: plamy pigmentu, białe papierowe prześwity, miękkie krawędzie.
- **Styl z obrazu 2**: przy stylizacji z referencji opisz styl referencji i zachowaj treść płótna [9] (oficjalne). 2.1: „Render <image1> in the visual style of <image2>: [cechy]. Keep the content and composition of <image1> unchanged.”
- **Siła**: zmiana medium musi być **jednoznaczna** — inaczej wynik wygląda jak wejście („niedoedytowanie”) [20]. Nazwij ślad narzędzia: kreska, kreskowanie, wypełnienie płaskim kolorem, raster, ziarno, rysy.
- **Archiwalność / taśma**: opisz efekty widoczne (ziarno, przebarwienie, rysy, zmiękczone krawędzie) i co zostaje nietknięte. Odwrotny kierunek ma oficjalny szablon („Restore and colorize the photo.”) [9].
- **Kolaż**: 2 obrazy → „Place [element] from <image2> / image 2 onto [miejsce] in <image1> / image 1 as a [cut-out paper / torn photo] collage element, [krawędź, cień]” — sama składnia umieszczania jest oficjalna [13][19], efekt kolażowy niepotwierdzony testem.
- LoRA stylu: Studio ich tu nie wystawia [20][21].

## Ruch / czas / dźwięk
Nie dotyczy. Gdy edycja ma dać klatkę do wideo (np. pierwsza/ostatnia klatka) — pilnuj stałego kadru i kąta kamery („keep the framing, camera angle and all positions unchanged”), żeby obie klatki pasowały.

## Sprawdź przed wysłaniem
- [ ] Który model? **2.1 → `<image1>`/`<image2>`** (jeden obraz: znacznik zbędny, „the image”); **2511 → „image 1”/„image 2”**.
- [ ] Zaczyna się od operacji (czasownik), nie od opisu gotowego obrazu.
- [ ] Zmiana nazwana konkretnie i mocno; rola każdego obrazu jasna (płótno vs źródło).
- [ ] Klauzula zachowania: krótko, hurtem, twierdząco („keep … unchanged”), bez opisywania wyglądu tego, co zostaje.
- [ ] Napisy w `"…"`, dosłownie, jednojęzycznie, wg reguły języka.
- [ ] Jedna operacja; złożone — łańcuchem w kilku krokach.
- [ ] Brak: wag, JSON, proporcji, negatywów typu „no …”.
- [ ] Tożsamość z referencji — wskazana obrazem, nie opisana słowami.
- [ ] 2511: szybki do prób, jakość do finału. 2.1: duże obrazy wejściowe = wolno.

## Źródła
[1] Qwen/Qwen-Image-2.1 — karta modelu — https://huggingface.co/Qwen/Qwen-Image-2.1 — oficjalne
[2] ComfyUI Docs — Qwen-Image-2.1 ComfyUI Native Workflow Example — https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1 — oficjalne (ComfyUI)
[3] ComfyUI — comfy_extras/nodes_qwen.py (TextEncodeQwenImage21: resolution 0 = rozmiar natywny ×32) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_qwen.py — oficjalne (kod)
[4] ComfyUI — comfy/text_encoders/qwen_image21.py (znaczniki `<imageN>` wstawiane przed obrazami) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image21.py — oficjalne (kod)
[5] Qwen/Qwen-Image-Edit-2511 — karta modelu — https://huggingface.co/Qwen/Qwen-Image-Edit-2511 — oficjalne
[6] Qwen blog — Qwen-Image-Edit-2511: Improve Consistency — https://qwen.ai/blog?id=qwen-image-edit-2511 — oficjalne (treść wg fragmentów wyszukiwarki; strona renderowana JS)
[7] Qwen/Qwen-Image-Edit-2509 — karta modelu — https://huggingface.co/Qwen/Qwen-Image-Edit-2509 — oficjalne (wersja 2509)
[8] ComfyUI — comfy_extras/nodes_qwen.py + comfy/text_encoders/qwen_image.py (TextEncodeQwenImageEditPlus: „Picture N:”, szablon systemowy) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen_image.py — oficjalne (kod)
[9] QwenLM/Qwen-Image — README + src/examples/tools/prompt_utils.py (polish_edit_prompt) — https://github.com/QwenLM/Qwen-Image — oficjalne
[10] OrcaRouter — Qwen-Image 2.1 shipped quietly: inside the PE-I2I rewriter — https://www.orcarouter.ai/blog/qwen-image-2-1-open-weights-research-license — społeczność
[11] HF dyskusja #11 — 光影，参考能力，脸不变能力仍不及预期 — https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/11 — społeczność (sam tytuł)
[12] SpicyAPI — Qwen Image 2.1 Review — https://spicyapi.ai/reviews/qwen-image-2-1 — społeczność (sprzedawca)
[13] RunComfy — Qwen Image Edit 2511 in ComfyUI — https://www.runcomfy.com/comfyui-workflows/qwen-image-edit-2511-in-comfyui-precision-instruction-editing — społeczność
[14] Wyniki wyszukiwania: porównanie 40 kroków vs Lightning 4 kroki (futro) — https://huggingface.co/lightx2v/Qwen-Image-Edit-2511-Lightning — oficjalne (LoRA) / społeczność (porównanie)
[15] deAPI — Qwen Image Edit Plus prompting guide — https://deapi.ai/blog/qwen-image-edit-plus-prompting-guide-how-to-write-edit-instructions-that-actually-work — społeczność (wersja Edit Plus)
[16] MyAIForce — Fixing Pixel Drift / Qwen Image Edit 2511 Relighting — https://myaiforce.com/qwen-image-edit-2511-relighting/ — społeczność (strona niedostępna przy weryfikacji; treść z wyszukiwarki)
[17] AIStudyNow — Qwen Image Edit 2511 ComfyUI Workflow (index_timestep_zero, skóra) — https://aistudynow.com/qwen-image-edit-2511-comfyui-workflow/ — społeczność
[18] ComfyUI — comfy/text_encoders/qwen3vl.py, qwen_image.py (`disable_weights=True`) — https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/qwen3vl.py — oficjalne (kod)
[19] Scenario — Advanced Editing with Qwen Models — https://help.scenario.com/articles/5117943220-advanced-editing-with-qwen-models — społeczność
[20] Nasza konfiguracja: modele/obraz/qwen-image-2-1-edycja.yaml; workflows/obraz/qwenimage21_edycja-obrazu.api.json (węzeł 459:479 = oficjalny system prompt PE-I2I „Edit Prompt Enhancer — General (v2)”, 459:474 resolution 0) — nasza konfiguracja / oficjalne
[21] Nasza konfiguracja: modele/obraz/qwen-image-edit-2511.yaml; workflows/obraz/qwenedit2511_edycja-obrazu.api.json (FluxKontextImageScale, index_timestep_zero, Lightning, CFG 1/4, 4/40 kroków) — nasza konfiguracja
