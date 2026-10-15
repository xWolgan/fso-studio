<!-- Karta modelu dla promptmakera. modele: wan-2-2, wan-2-2-tekst, wan-2-2-obraz, wan-2-2-klatki -->
# WAN 2.2 (Alibaba Wan-AI, 14B MoE) — wideo bez dźwięku

## Czym jest i do czego się nadaje
- Otwarty model wideo (Apache 2.0) w trzech trybach Studia: **tekst → wideo** (T2V-A14B), **obraz → wideo** (I2V-A14B), **pierwsza + ostatnia klatka** (ten sam I2V-A14B, węzeł `WanFirstLastFrameToVideo`) [1][2][3].
- Dwa „eksperci”: high-noise układa kompozycję i ruch na początku odszumiania, low-noise dopracowuje detal [3] (oficjalne). Dlatego o ruchu i kadrze decyduje to, co prompt mówi jasno i na początku.
- Wan 2.2 był uczony na danych estetycznych z etykietami **światła, kompozycji, kontrastu, tonacji barwnej** — reaguje na słownik operatorski [3] (oficjalne).
- Mocne strony: płynny ruch jednej akcji, czytelne ruchy kamery, słownik światła i kadru, stylizacje „materiałowe” (filc, plastelina, lalki, stop-motion, piksel, rysunek liniowy) — przykłady stylizacji w przewodniku Alibaby są zrobione właśnie Wanem 2.2 [7] (oficjalne).
- **Czego NIE robi dobrze:**
  - dźwięku — w ogóle (dźwięk mają dopiero Wan 2.5+, zamknięte) [1][7];
  - wielu zdarzeń w jednym klipie, montażu wewnątrz klipu, długich choreografii — jedno ujęcie = jedna ciągła akcja [7] (oficjalne), [19] (społeczność);
  - czytelnego tekstu w kadrze (wychodzi przybliżony) [7] (oficjalne);
  - bardzo szybkiego, gwałtownego ruchu — artefakty, zwłaszcza w trybie szybkim [8] (oficjalne), [17] (społeczność);
  - długości ponad ~5 s (81 klatek) — patrz „Ruch / czas” [5][21];
  - pełnych obrotów kamery 360° w 5 s — bywają ignorowane; orbitę trzymać w łuku < 45° [7] (oficjalne), [15] (społeczność).

## Co uczestnik ustawia w Studiu
Jedna pozycja „WAN 2.2”; wariant wybiera się sam wg podanych klatek [1] (nasza konfiguracja):
- **brak klatek** → tekst → wideo (`wan-2-2-tekst`);
- **pierwsza klatka** → obraz → wideo (`wan-2-2-obraz`);
- **pierwsza + ostatnia klatka** → przejście między nimi (`wan-2-2-klatki`).

Pola:
- **prompt** — JEDNO pole, trafia prosto do enkodera umT5-XXL (`CLIPTextEncode`), bez rozszerzania promptu przez LLM (oficjalne repo zaleca „prompt extension” — u nas jej nie ma, więc to Ty piszesz prompt w stylu rozszerzonym) [2][3] (nasza konfiguracja / oficjalne).
- **Brak pola negative promptu.** Negatyw jest na stałe wpisany w workflow — domyślny negatyw Wana w oficjalnym angielskim tłumaczeniu z README Wan2.1 („Bright tones, overexposed, static, … walking backwards”; w T2V dopisane „nudity, NSFW”) [2][6]. Wszystko, czego ma NIE być, pisz w promptcie jako ograniczenie pozytywne (patrz niżej).
- **proporcje** — 16:9 (domyślnie), 4:3, 1:1, 3:4, 9:16; ok. 0,4 MP (np. 16:9 ≈ 848×480 = 480p, wymiary ×16) [1]. 480p to rozdzielczość, na której model jest oficjalnie wspierany [3]. Kadr pionowy: w trybie szybkim ruch bywa jeszcze słabszy (pojedyncze zgłoszenie) [9] (społeczność).
- **długość** — 1–8 s, domyślnie 5 s; 16 kl./s; T2V/I2V krok 0,5 s (klatki 16n+1), „klatki” krok 0,25 s (4n+1) [1]. Natywnie 81 klatek = 5 s [5] (oficjalne).
- **tryb**:
  - **szybki** (domyślny) — LoRA lightx2v 4 kroki, CFG 1, ok. 30 s → **negatyw nie działa** (przy CFG 1 ComfyUI pomija gałąź negatywną) [2][11][12];
  - **jakość** — 20 kroków, CFG 3,5 (klatki: CFG 4, shift 8), ok. 3,5 min → negatyw działa [1][2].
- **seed** — stały seed do porównywania wersji promptu (zmieniaj jedną rzecz naraz) [12][19] (społeczność).

Wpływ na prompt: w obraz → wideo i klatkach **wygląd i styl daje obraz**, prompt opisuje ruch. W T2V prompt niesie wszystko.

## Format promptu
- **Język: angielski.** Model jest dwujęzyczny zh/en (umT5); oficjalne przykłady i oficjalny rozszerzacz I2V zawsze piszą po angielsku [3][4] (oficjalne). Polski nie jest językiem treningowym (niepotwierdzone, jak działa — nie ryzykuj). Chiński bywa polecany tylko dla modelu **Wan 2.1 FLF2V** („uczony głównie na chińskich parach”) [6] — to INNY model niż nasze klatki (u nas Wan 2.2 I2V), więc nie dotyczy; uczestnik i tak musi umieć przeczytać prompt.
- **Proza, pełne zdania, czas teraźniejszy.** Bez list tagów w stylu SD, bez JSON, bez znaczników sekcji.
- **Długość:**
  - T2V: ok. 60–120 słów (oficjalny rozszerzacz: „60–200”, przykłady ~60–90 słów) [4] (oficjalne); praktycy: 80–120 słów [15][16] (społeczność); inny: 25–80 [17] — przyjmij **~60–110**.
  - Obraz → wideo / klatki: **≤ 100 słów**, tylko ruch [4] (oficjalne). Często wystarczy 1–3 zdania.
  - Limit enkodera w oryginalnym kodzie: 512 tokenów [5]; ComfyUI nie ucina [13] — dłuższe prompty i tak nie pomagają.
- **Oficjalna formuła (Alibaba)** [7]:
  - podstawowa: Podmiot + Scena + Ruch;
  - zaawansowana: Podmiot (opis) + Scena (opis) + Ruch (opis: amplituda, tempo, efekt) + Kontrola estetyki (źródło światła, rodzaj światła, plan, kąt, obiektyw, ruch kamery) + Stylizacja;
  - obraz → wideo: **Ruch + Ruch kamery** (obraz definiuje podmiot, scenę i styl).
- **Kolejność wg oficjalnego rozszerzacza T2V** [4] (oficjalne):
  1. jeśli jest styl nie-filmowy — **styl na samym początku**;
  2. potem do **4** krótkich tagów estetyki oddzielonych przecinkami (pora, źródło światła, miękkość, kąt światła, tonacja, plan, kąt kamery, kompozycja), zakończonych kropką;
  3. potem 2–4 zdania: podmiot z wyglądem → akcja krok po kroku → tło i jego ruch.
  Uwaga: dla stylów 2D/ilustracji oficjalny rozszerzacz **nie dodaje** terminów filmowych (światło, obiektyw) [4].
- Model mocniej waży **początek promptu**; detale z końca bywają pomijane (społeczność, nietestowane kontrolnie) [17]. Najważniejsze — na przód.
- **Bez „literatury”.** Oficjalny rozszerzacz zakazuje opisów nastroju i atmosfery („pełen napięcia”, „melancholijny klimat”) [4]. Nastrój z wiersza tłumacz na światło, kolor, tempo, kadr, materię.
- **Negative prompt:** nie istnieje w polu uczestnika. Wykluczenia pisz pozytywnie: „only one person in the frame”, „the camera stays fixed”, „she remains seated” [12] (społeczność).
- **Wagi `(słowo:1.3)` — NIE używaj.** ComfyUI parsuje nawiasy także dla umT5 (nawias = waga 1,1, nawias znika z tekstu) [13] (kod), ale czy to cokolwiek poprawia w Wanie — niepotwierdzone. Konsekwencja: **nie używaj nawiasów okrągłych w ogóle** (zmienią się w wagi). Dopowiedzenia — przecinkiem.
- Cudzysłów do tekstu w kadrze — tylko gdy tekst jest konieczny; i tak wyjdzie przybliżony [7].

## Szkielet promptu
Tekst → wideo:
```
[styl / medium / technika — tylko jeśli nie-fotograficzny]. [pora], [źródło i rodzaj światła], [tonacja], [plan], [kąt lub kompozycja]. [podmiot: kto/co, ile, 2–3 cechy wyglądu, materiał]. [akcja: jeden ruch rozpisany krok po kroku, z tempem: slowly/quickly/gradually]. [ruch kamery: jeden, z kierunkiem i tempem — albo „The camera stays fixed.”]. [tło: 1–2 elementy i ich ruch: wiatr, woda, dym, światło]. [faktura obrazu: ziarno / papier / farba — jeśli dotyczy]. [ograniczenie pozytywne: czego ma nie być, np. tylko jedna postać].
```
Obraz → wideo:
```
[ruch kamery z tempem, albo „Static camera.”]. [podmiot widoczny na obrazie, nazwany krótko] [akcja krok po kroku z tempem i stanem końcowym: „until …”]. [ruch drugiego planu]. [co zostaje nieruchome].
```
Pierwsza + ostatnia klatka:
```
[ruch kamery prowadzący od kadru A do kadru B]. [co się dzieje pomiędzy: jedna przemiana / jedno przejście, w kolejności]. [tempo: gradually / smoothly / suddenly]. [element wspólny obu klatek, który ma pozostać stały].
```

## Co działa
- **Słownik estetyki z oficjalnego rozszerzacza** (kopiuj dosłownie) [4]:
  - pora: Day time, Night time, Dawn time, Sunrise time;
  - źródło: Daylight, Artificial lighting, Moonlight, Practical lighting, Firelight, Fluorescent lighting, Overcast lighting, Sunny lighting;
  - miękkość: Soft lighting, Hard lighting; kąt światła: Top lighting, Side lighting, Underlighting, Edge lighting;
  - tonacja: Warm colors, Cool colors, Mixed colors;
  - plan: Extreme close-up shot, Close-up shot, Medium close-up shot, Medium shot, Medium wide shot, Wide shot, Extreme wide shot;
  - kąt: Over-the-shoulder shot, Low angle shot, High angle shot, Dutch angle shot, Aerial shot, Overhead shot (pomiń, jeśli opisujesz ruch kamery);
  - kompozycja: Center composition, Balanced composition, Left-heavy / Right-heavy composition, Symmetrical composition, Short-side composition.
- Dodatkowo z przewodnika Alibaby [7]: High contrast / Low contrast, Low saturation / High saturation, Golden hour sunlight, Rim light, Backlight, Long-focus lens, Wide-angle lens, Ultra-wide-angle fisheye, Tilt-shift lens, Establishing shot, Clean single shot.
- **Ruch kamery** — słowa z przewodnika [7]: camera pushes in / pulls out, camera moves left/right, camera moves forward, camera tilts up, camera pans, tracking shot, orbiting camera movement (łuk < 45°), drone shot, **fixed camera**. Znaczenia wg Alibaby: najazd = bliskość/napięcie, odjazd = skala/samotność, prowadzenie = towarzyszenie, orbita = waga postaci, statyczna = skupienie [7].
- **Zawsze nazwij kamerę** — także „static camera / fixed camera”. Bez tego model dopisuje własny dryf lub lekki najazd (dwa niezależne poradniki, nietestowane kontrolnie) [17][19].
- **Jeden ruch kamery + jedna akcja.** Łączenie dolly + tilt zawiodło w teście; model faworyzuje pierwszy ruch i wygasza kolejne [15] (społeczność). Ważniejszy ruch — pierwszy.
- **Ruch rozpisany jako proces**: amplituda + tempo + efekt („slowly lifts her hand, the sleeve slides down”) [4][7] (oficjalne). Przysłówki tempa: slowly, quickly, gradually, suddenly [7].
- **Ruch tła** (wiatr w trawie, płynące chmury, dym) — oficjalny rozszerzacz dodaje go, gdy scena jest statyczna [4].
- **Stan końcowy** ruchu („until the door is fully open”) ogranicza dryf pod koniec klipu [19] (społeczność).
- **Obraz → wideo: nie opisuj tego, co widać.** Oficjalny rozszerzacz I2V usuwa opisy statyczne i zostawia tylko ruch; najczęstszy błąd to prompt jak do generatora obrazów [4] (oficjalne), [19] (społeczność).
- **Klatki:** prompt ma pasować do obu klatek [14] (oficjalne ComfyUI); opisz przejście, nie same kadry.
- Głębia: przeciwstaw ruch pierwszego planu nieruchomemu tłu (lub odwrotnie) [16][18] (społeczność).
- Niebo: oficjalny rozszerzacz zamienia każde niebo na „clear blue sky”, „żeby uniknąć prześwietlenia” [4] — wskazówka, że jasne niebo łatwo się przepala; przy jasnych plenerach rozważ low contrast / overcast.

## Biasy i pułapki
- **Tryb szybki (lightx2v) = zwolnione tempo.** Zespół lightx2v przyznaje: ruch wolniejszy niż w modelu bazowym [9]; domyślne workflow ComfyUI z tą LoRA „zamieniają sceny w slow motion” [10]; LoRA zmienia też styl [9] (społeczność), przy bardzo dużym ruchu daje artefakty i potrafi odwrócić kierunek jazdy pojazdów [8] (oficjalne). Obejście promptem: wyraźne czasowniki i tempo („quickly”, „briskly”), mniej elementów ruchu. Gdy tempo kluczowe → tryb jakość.
- **Negatyw (tylko tryb jakość) działa przeciw stylizacji.** Domyślny negatyw (u nas po angielsku, oficjalne tłumaczenie z README Wan 2.1) zawiera m.in. „style, works, paintings, images” oraz „static, still picture” [5][6]. Wniosek (niepotwierdzone testem): w trybie jakość malarskość/„dzieło” jest lekko odpychana, a całkowity bezruch karany. Przy stylach nie-fotograficznych **mocniej nazywaj technikę** i porównaj oba tryby na tym samym seedzie.
- **Ciążenie ku realizmowi** — autorzy LoRA anime piszą o „silnym biasie Wana 2.2 w stronę realistycznych generacji” i wstawianiu estetyki 3D [20] (społeczność). Styl musi stać na początku i być powtórzony w opisie faktury.
- **Domyślna „czysta” estetyka** — bez wskazówek faktury obraz wychodzi gładki i równo oświetlony; ziarno, rozmycie ruchu i światło sceny trzeba nazwać [17] (społeczność, nietestowane).
- **Nie dodawaj podmiotów** — oficjalny rozszerzacz zabrania dopisywania postaci, których nie ma (np. ludzi do pejzażu) [4]. Pejzaż bez ludzi pisz jako „no people, empty …”.
- **Domyślnie dzień** — oficjalny rozszerzacz wybiera „Day time”, gdy prompt nie mówi inaczej [4]; nocy/świtu nie zostawiaj domysłowi.
- **Liczba postaci** — podaj liczbę; wiele postaci i ich interakcje to ryzyko [18] (społeczność). Negatyw zawiera „many people in the background, three legs, walking backwards” [6] — to znane słabości.
- **Sprzeczne ujęcia** (close-up + wide shot w jednym) psują wynik [17]; sprzeczne ruchy też [18].
- **Ekstremalne przemiany** (dzień → noc w 5 s, kilka metamorfoz) — słabo [18] (społeczność). W klatkach: jedna przemiana.
- **Nawiasy okrągłe** znikają i zmieniają wagi [13] — patrz „Format”.
- Prawdziwe osoby z nazwiska — unikać [7] (oficjalne).
- Rozbieżności w poradnikach: część pisze o „24 fps” — to dotyczy modelu **TI2V-5B** [3]; nasz 14B ma 16 kl./s [5]. Formuły dźwięku, wielu ujęć („Shot 1 [0–3 s]”), „Image 1” — to **Wan 2.5–3.0**, nie 2.2 [7]. Nie przenoś ich.

## Poza fotorealizmem
- Oficjalnie wymienione stylizacje (przykłady zrobione Wanem 2.2) [7]: **felt style, 3D cartoon style, pixel style / 8-bit, puppet animation, claymation style, black and white animation, stop-motion animation, line art illustration**, surreal style; efekty: **tilt-shift photography, time-lapse photography**, bokeh; w przykładach: **VHS glitch aesthetic, CRT scanline effect** [7].
- Oficjalny przykład stylu 2D z rozszerzacza: nazwa techniki na początku + opis kreski i cieniowania na końcu („smooth linework”, „cel-shaded”), **bez** terminów filmowego światła [4]. Ten wzór stosuj do rysunku, gwaszu, linorytu, wycinanki: technika → treść → opis śladu narzędzia (kreska, plama, faktura papieru).
- Akwarela, tusz, olej, kolaż, wycinanka — w oficjalnych materiałach **nie wymienione**; skuteczność nieznana (niepotwierdzone). Opisuj materialnie: papier, pigment, krawędź, warstwy.
- Taśma / archiwum: praktycy używają „16mm grain”, „35mm film grain”, „high contrast black and white”, „bleach-bypass”, „kodak portra” [16] (społeczność, bez testów porównawczych). Do archiwalności dodaj epokę i nośnik (np. „1960s 16mm footage, scratches”) — działanie niepotwierdzone.
- Abstrakcja: model chce podmiotu i akcji; abstrakcję opisuj jako materię w ruchu (dym, atrament w wodzie, światło przez szkło) z kamerą (niepotwierdzone — wniosek z formuły Podmiot+Scena+Ruch [7]).
- **Najpewniejsza droga do nie-fotorealizmu: obraz → wideo lub klatki** z obrazem w docelowej technice (zrobionym innym modelem / ręcznie). Styl daje obraz, prompt tylko ruch [4][19]. Mimo to raz nazwij technikę w promptcie (np. „the charcoal drawing comes alive…”), żeby model jej nie „urealniał” [20] (społeczność).
- Ruch w stylizacjach: „stop-motion” sugeruje skokowy ruch, „hand-drawn animation” — klatkowanie; przy 16 kl./s i trybie szybkim efekt bywa płynny i wolny (niepotwierdzone).

## Ruch / czas / dźwięk
- **Dźwięku brak.** Nie pisz dialogów, muzyki ani opisów dźwięku — model ich nie wygeneruje, a słowa zajmują miejsce [1]. Usta mówiącej postaci mogą się ruszać („speaks”) bez głosu [4].
- **Długość:** 5 s (81 klatek przy 16 kl./s) to natywne maksimum [1][5]. Studio pozwala do 8 s, ale powyżej ~81 klatek akcja ma tendencję do cofania się do stanu początkowego (zgłoszenia użytkowników) [21] (społeczność). Dłuższe ujęcie = kilka klipów (ostatnia klatka → pierwsza następnego, albo tryb klatek) [21].
- W 5 s mieści się **jeden ruch kamery + jedna akcja podmiotu** [19] (społeczność); krótszy klip = jeszcze mniej.
- **Tempo:** słowa tempa działają (slowly/quickly, slow-motion, time-lapse) [7][16]; w trybie szybkim całość i tak zwalnia [9][10].
- Kolejność zdań = kolejność zdarzeń: najpierw kadr otwierający, potem ruch kamery, potem „odsłona” [15][16] (społeczność).

## Sprawdź przed wysłaniem
- [ ] Po angielsku, proza, bez nawiasów okrągłych, bez wag, bez tagów sekcji.
- [ ] T2V ~60–110 słów; obraz/klatki ≤ 100 słów i **tylko ruch** (nie opisujesz tego, co widać).
- [ ] Styl nie-fotograficzny — na samym początku i powtórzony faktura/kreska.
- [ ] Najważniejsze na początku; maks. 4 tagi estetyki; bez sprzecznych planów.
- [ ] Dokładnie **jeden** ruch kamery (albo „static/fixed camera”) i **jedna** akcja z tempem i stanem końcowym.
- [ ] Liczba postaci podana; brak dopisanych podmiotów.
- [ ] Zero słów nastroju/atmosfery — przetłumaczone na światło, kolor, ruch, materię.
- [ ] Wykluczenia jako zdania pozytywne (pola negatywu nie ma).
- [ ] Brak dźwięku, dialogów, napisów do odczytania, nazwisk prawdziwych osób.
- [ ] Długość ≤ 5 s; przy ważnym tempie ruchu — zasugeruj tryb „jakość”; przy stylizacji — porównanie trybów na tym samym seedzie.

## Źródła
[1] Studio FSO — `modele/wideo/wan-2-2.yaml`, `wan-2-2-tekst.yaml`, `wan-2-2-obraz.yaml`, `wan-2-2-klatki.yaml`  — nasza konfiguracja
[2] Studio FSO — `workflows/wideo/wan_2_2_tekst-na-wideo.api.json`, `wan_2_2_obraz-na-wideo.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka.api.json`, `wan_2_2_pierwsza-i-ostatnia-klatka_jakosc.api.json`  — nasza konfiguracja
[3] Wan2.2 README — https://github.com/Wan-Video/Wan2.2 — oficjalne
[4] Wan2.2 `wan/utils/system_prompt.py` (prompty systemowe rozszerzacza T2V/I2V) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/utils/system_prompt.py — oficjalne
[5] Wan2.2 `wan/configs/shared_config.py` (sample_neg_prompt, 16 fps, 81 klatek, text_len 512) — https://github.com/Wan-Video/Wan2.2/blob/main/wan/configs/shared_config.py — oficjalne
[6] Wan2.1 README (angielskie tłumaczenie domyślnego negatywu; FLF2V a chiński) — https://github.com/Wan-Video/Wan2.1 — oficjalne
[7] Alibaba Cloud Model Studio — Text-to-video / image-to-video prompt guide — https://www.alibabacloud.com/help/en/model-studio/text-to-video-prompt — oficjalne
[8] lightx2v — Wan2.2-Lightning (karta modelu) — https://huggingface.co/lightx2v/Wan2.2-Lightning — oficjalne (autorzy LoRA)
[9] lightx2v — dyskusja #26 o wolnym ruchu — https://huggingface.co/lightx2v/Wan2.2-Lightning/discussions/26 — społeczność + autorzy
[10] rzgar — Wan2.2 I2V LightX2V Slow-Mo Fix — https://huggingface.co/rzgar/Wan2.2_I2V_LightX2V_Slow-Mo_Fix — społeczność
[11] Civitai — artykuł o Lightning LoRA, CFG 1 i NAG — https://civitai.com/articles/18711 — społeczność
[12] Hugging Face Forum — How to get the most out of prompts for WAN models — https://discuss.huggingface.co/t/how-to-get-the-most-out-of-prompts-for-wan-models/170354 — społeczność
[13] ComfyUI — `comfy/sd1_clip.py` (parsowanie nawiasów/wag) i `comfy/text_encoders/wan.py` (tokenizer umT5) — https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/sd1_clip.py , https://github.com/comfyanonymous/ComfyUI/blob/master/comfy/text_encoders/wan.py — oficjalne (kod ComfyUI)
[14] ComfyUI Docs — Wan2.2 tutorial — https://docs.comfy.org/tutorials/video/wan/wan2_2 — oficjalne (ComfyUI)
[15] aistudynow — How to Write Better WAN 2.2 Prompts, Tested in ComfyUI — https://aistudynow.com/how-to-write-better-wan-2-2-prompts-tested-in-comfyui/ — społeczność
[16] ViewComfy — Wan 2.2 prompt guide with examples — https://www.viewcomfy.com/blog/wan2.2_prompt_guide_with_examples — społeczność
[17] wan27.org — Wan 2.2 Prompt Guide — https://wan27.org/blog/wan-2-2-prompt-guide — społeczność (serwis komercyjny, twierdzenia nietestowane)
[18] VEED — Wan 2.2 Prompting Guide — https://www.veed.io/learn/wan-2-2-prompting-guide — społeczność
[19] Unifically — Wan 2.2 Image-to-Video Prompt Guide — https://unifically.com/blogs/wan-2.2-image-to-video-prompt-guide — społeczność
[20] CivArchive — Anime style Wan 2.2 I2V (LoRA, uwagi o biasie realizmu) — https://civarchive.com/models/2222779/anime-style-wan-22-i2v — społeczność
[21] Hugging Face — Phr00t WAN2.2-14B-Rapid-AllInOne, dyskusja #198 (81 klatek, cofanie akcji) — https://huggingface.co/Phr00t/WAN2.2-14B-Rapid-AllInOne/discussions/198 — społeczność
