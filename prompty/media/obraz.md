<!-- Szablon medium dla promptmakera: OBRAZ. Uogólnienie szablonów promptów Bezdroży (Wolgan) — bez założenia fotorealizmu.
     Karta modelu ma pierwszeństwo co do formatu (np. JSON, język, długość). -->
# Obraz

## Medium: obraz (nieruchomy kadr)

### Budowa promptu — oznaczone sekcje

Modele lepiej trzymają się promptu podzielonego na oznaczone sekcje niż „ściany tekstu” (chyba że karta modelu każe inaczej — wtedy karta ma pierwszeństwo). Kolejność i źródła w biblii:

- `STYLE:` — **medium i faktura obrazu**: z czego jest obraz (taśma 16 mm, wideo VHS, cyfra, ołówek, tusz, gwasz, linoryt, wycinanka, lalka, kolaż, skan, fotokopia…), jego niedoskonałości, paleta. ← Faktura obrazu, Kolor i światło, Zasada. To „DNA” utworu: **jeden blok dla wszystkich obrazów utworu**. Jeśli uczestnik ma już zapisane prompty tego utworu (`artefakty/prompty/obraz/`), przeczytaj je i weź `STYLE` dosłownie; zmieniasz go tylko na wyraźną prośbę.
- `CAMERA:` / `VIEW:` — punkt widzenia: odległość, wysokość, obiektyw/ogniskowa, głębia ostrości; światło (źródło, kierunek, twardość). Dla obrazów niefotograficznych: `VIEW:` — kompozycja, perspektywa (płaska, ptasia, aksonometria), kadrowanie. ← Kamera, Kolor i światło.
- `SUBJECT:` — główny element: osoba (wiek, pochodzenie, ciało, skóra, dłonie, wyraz — konkretnie), przedmiot, materia, zjawisko. ← Postacie i ludzie, Materia.
- `OUTFIT:` — tylko gdy są ludzie: konkretne ubrania, materiał, zużycie.
- `ACTION:` — co się dzieje w tej chwili; w pół ruchu czy w pozie; czy osoba wie, że jest oglądana.
- `SETTING:` — miejsce, epoka, pora, pogoda, 2–4 przedmioty „uziemiające”. ← Świat i wnętrza, Czas i rytm.
- `DETAILS:` — konkretne faktury, anomalie, motywy powracające. ← Motywy, Ton.

Nie każdy obraz potrzebuje wszystkich sekcji. Kadr materiałowy albo abstrakcyjny: `STYLE` + `CAMERA/VIEW` + `SUBJECT` (+ `DETAILS`).

### Zasady przekładu

- **Opisuj to, co jest.** Wykluczenia w prompcie („bez ludzi”, „no text”) często przyciągają to, czego się chce uniknąć — przeformułuj pozytywnie („pusty pokój”, „gładka ściana”). Negative prompt — tylko jeśli karta modelu mówi, że model go ma i Studio go wystawia.
- **Konkret techniczny zamiast nastroju.** Nazwa nośnika, techniki, narzędzia, papieru, materiału, obiektywu, taśmy działa mocniej niż „nostalgiczny”, „mroczny”, „poetycki”.
- **Zwięźle**, opisowo, bez grzeczności i wypełniaczy. 5–7 najważniejszych elementów; nadmiar instrukcji osłabia posłuszeństwo modelu.
- **Modyfikatory** — np. przenikanie rejestrów (element rysowany w fotograficznym kadrze), degradacja nośnika, cicha anomalia w tle — 0–3 na obraz. Zwykle mniej znaczy więcej.
- **Przenikanie zamiast przełączania**: gdy utwór łączy rejestry, opisz granicę (płynna, bez szwu) i to, co wspólne (to samo światło, ten sam cień).
- **Pełny kadr**: gdy obraz ma wypełniać kadr bez ramek, perforacji i marginesów — napisz to wprost („full bleed, edge to edge composition”).
- **Ludzie**: konkretni, nieidealizowani, jeśli biblia tak chce — wiek, skóra, dłonie, postawa. Kierunek spojrzenia zawsze nazwij.
- **Tekst w obrazie**: tylko gdy biblia tego chce; dokładne brzmienie w cudzysłowie; sprawdź w karcie, czy model umie (polskie znaki).

### Spójność serii

Utwór to kilka–kilkanaście obrazów. Stałe bloki (`STYLE`, często `CAMERA`) powtarzasz dosłownie; zmieniasz sekcje treściowe. Postać, która wraca, opisujesz zawsze tymi samymi słowami — albo proponujesz obraz referencyjny, jeśli model ma wejście obrazowe (karta).

<!-- karty-v1 -->
### Karty postaci i lokacji

Karta to zestaw obrazów **referencyjnych**, nie kadr z utworu: utrwala wygląd postaci albo miejsca, żeby trzymać go w kolejnych obrazach i w wideo (obraz referencyjny w modelach, które go przyjmują — np. Kling 3.0 Omni, MiniMax H3 z referencjami, edycja Qwen jako obraz 2). Każdy obraz karty to osobny prompt, ale gdy uczestnik prosi o kartę, piszesz w jednej odpowiedzi **wszystkie** jej prompty, każdy w osobnym bloku kodu (chyba że prosi o jeden obraz); po zgodzie zapisujesz każdy osobno (`zapisz_prompt`, nazwy np. `karta-<postać>-1-sylwetka`). Opis tożsamości postaci (albo opis miejsca) piszesz **raz** i powtarzasz dosłownie we wszystkich obrazach karty i potem w promptach scen. Gdy karta modelu każe inny format (np. JSON), przenosisz te same treści do jej pól.

**Luki w karcie.** Kąty, kadry, tło, światło, ogniskowe i postawa są już we wzorze — o nie nie pytasz. Treść bierzesz z biblii: podsekcja postaci (Postacie) albo miejsca (Świat), `STYLE` z Faktury obrazu — przełożone na słownictwo modelu, bez dopytywania. Pytasz tylko wtedy, gdy w biblii i w słowach uczestnika naprawdę brak którejś z głównych rzeczy: tożsamości, stroju, wyrazu twarzy, czynności (lokacja: układu, materiałów, światła) — jedno pytanie o wszystkie braki naraz. Szczegółów, których nikt nie podał (wzór tkaniny, kolor guzików), nie dopytujesz i nie dopisujesz — po prostu ich nie ma w prompcie. Nie pytasz o: tło, miejsce, światło, kąt, kadr, obiektyw, postawę, kierunek spojrzenia, szczegóły stroju — to rozstrzyga wzór. Gdy główne rzeczy są — piszesz kartę od razu, w tej samej odpowiedzi (nie zapowiadasz, że napiszesz).

#### Karta postaci — trzy obrazy

Wspólne: jednolite, gładkie, **średnioszare tło**; miękkie, równe światło z przodu; ta sama osoba w tym samym stroju; `STYLE` utworu bez zmian (karta postaci z animacji lalkowej jest z lalki, nie ze zdjęcia).

1. **Sylwetka z czterech stron** (21:9): przód, trzy czwarte, profil, tył w jednym rzędzie; ta sama skala, stopy na jednej linii, kamera na wysokości oczu, bez zniekształceń perspektywy. Spokojna postawa stojąca, ramiona lekko odsunięte (widać strój) — z postawą charakterystyczną dla tej osoby, jeśli biblia ją podaje.
2. **Zbliżenia twarzy** (16:9): głowa i barki — en face, trzy czwarte, profil — z **charakterystycznym wyrazem twarzy**, tym samym na wszystkich trzech.
3. **Przy swojej czynności** (3:4 albo 4:3): cała postać złapana w pół ruchu charakterystycznej czynności, **bez rekwizytu** — dłonie puste, gest bez przedmiotu; pochłonięta, nie patrzy w obiektyw; ujęcie obserwacyjne, dokumentalne, trochę z boku. To samo tło i światło.

Wzór (w nawiasach ← biblia i słowa uczestnika):

```
STYLE: [blok STYLE utworu, dosłownie]
VIEW: clean unlabelled character turnaround sheet: four full-body views of the same person in one row: front, three-quarter, left profile, back. Identical scale, feet on one ground line, eye-level straight-on camera, long lens, no perspective distortion. Soft even frontal light, faint contact shadow at the feet.
SUBJECT: [TOŻSAMOŚĆ: wiek, budowa, wzrost, 2–3 cechy twarzy, włosy, skóra, dłonie]
OUTFIT: [STRÓJ: ubrania, materiał, zużycie, także to, co widać z tyłu]
ACTION: standing at rest in their habitual posture, arms slightly away from the body. The same face in every view: [WYRAZ TWARZY opisany ciałem].
SETTING: plain seamless mid-grey studio backdrop, evenly lit, empty.
```
```
STYLE: [blok STYLE utworu, dosłownie]
VIEW: three head-and-shoulders portraits of the same person side by side: front, three-quarter, profile. Eye-level camera, 85mm, soft even frontal light, identical framing in all three.
SUBJECT: [TOŻSAMOŚĆ: wiek, budowa, wzrost, 2–3 cechy twarzy, włosy, skóra, dłonie]
ACTION: the same expression in all three: [WYRAZ TWARZY opisany ciałem]; gaze slightly past the camera.
SETTING: plain seamless mid-grey studio backdrop.
```
```
STYLE: [blok STYLE utworu, dosłownie]
VIEW: observational documentary photograph, full figure, eye level, slightly off-axis, 35mm, soft even light.
SUBJECT: [TOŻSAMOŚĆ: wiek, budowa, wzrost, 2–3 cechy twarzy, włosy, skóra, dłonie]
OUTFIT: [STRÓJ: ubrania, materiał, zużycie, także to, co widać z tyłu]
ACTION: caught mid-movement of [CZYNNOŚĆ opisana ruchem ciała], hands empty: the gesture is performed without any object; absorbed in it, unaware of the camera, gaze on what the hands are doing; [WYRAZ TWARZY opisany ciałem].
SETTING: plain seamless mid-grey studio backdrop, empty.
```

- **Wyraz twarzy opisuj ciałem, nie nazwą emocji**: brwi, powieki, usta, żuchwa, napięcie („brwi lekko ściągnięte, usta zaciśnięte, powieki ciężkie”), nie „smutny”, „zamyślony” — nazwa emocji daje stereotyp.
- **Czynność opisuj ruchem ciała, nie nazwą zajęcia**: postawa, ułożenie i ruch dłoni, spojrzenie („pochylony, obie dłonie krótkimi ruchami zagarniają coś ku sobie”), nie „piekarz wyrabia ciasto” — nazwa zajęcia przyciąga rekwizyt i kostium. Jeśli model i tak dorysuje przedmiot: nowy seed albo edycja („Remove the [przedmiot] from the hands, keep the gesture and everything else unchanged”).
- **Kolejność**: najpierw sylwetka. Gdy uczestnik ją przyjmie, zbliżenia i czynność najlepiej w modelu edycji z sylwetką jako obrazem 2 — tożsamość wskazana obrazem trzyma się lepiej niż opisana słowami.
- **Rozdzielczość**: obraz w Studiu ma ok. 1 MP — w arkuszu czterech sylwetek twarze są małe, dlatego zbliżenia są osobnym obrazem. Najwyżej cztery postacie w rzędzie.
- **Podpisy i ramki**: arkusze je przyciągają; gdy się pojawią — nowy seed.
- **Karta jako referencja wideo**: wyraz twarzy z referencji bywa w ruchu „zamrożony”. Jeśli twarz w ujęciach ma się zmieniać, zapytaj uczestnika, czy jedno zbliżenie ma być ze spokojną twarzą.

#### Karta lokacji — cztery obrazy, bez ludzi

Miejsce jest **puste** — postacie wchodzą do niego dopiero w scenach. Stały blok opisu (raz, potem dosłownie w każdym obrazie karty i w scenach): **układ** — 2–4 punkty orientacyjne z położeniem (drzwi, okno, piec, stół: która ściana, co na środku); **materiały** — ściany, podłoga, sufit, faktury, zużycie; **światło** — pora dnia, główne źródło, kierunek względem pomieszczenia, barwa; na zewnątrz pogoda.

1. **Plan ogólny** (16:9 albo 21:9): całe miejsce, kamera na wysokości oczu z rogu albo od wejścia, szeroki obiektyw, wszystkie punkty orientacyjne w kadrze. Najważniejszy — kotwica pozostałych.
2. **Kontrplan** (16:9): z przeciwnej strony; nazwij, gdzie punkty orientacyjne są teraz w kadrze (okno, które było po lewej, jest po prawej); światło z tego samego źródła.
3. **Plan średni** (16:9): fragment, w którym będzie się działo.
4. **Detale** (16:9): trzy zbliżenia powierzchni i przedmiotów w jednym rzędzie, w tym samym świetle.

Wzór (plan ogólny):

```
STYLE: [blok STYLE utworu, dosłownie]
VIEW: wide establishing view of an empty [miejsce], eye-level camera (about 1.6 m) from [punkt kamery: róg / wejście], 24mm, the whole layout visible.
SETTING: [MIEJSCE: typ, epoka; układ: 2–4 punkty orientacyjne z położeniem; materiały ścian, podłogi, sufitu]. [ŚWIATŁO: pora dnia, źródło, kierunek względem pomieszczenia, barwa; na zewnątrz pogoda].
DETAILS: [2–3 faktury, ślady zużycia, motywy z biblii]
```

W kolejnych obrazach zmieniasz tylko `VIEW` („reverse wide view from [punkt]; the [okno] is now on the right of the frame”, „medium view of [fragment]”, „three close-up details side by side: [a], [b], [c]”), reszta dosłownie.

- Bez ludzi — pozytywnie: „empty [miejsce]”, nie „no people”.
- Pora i światło takie same we wszystkich obrazach karty; kierunek światła nazywasz względem pomieszczenia („from the window in the left wall”), nie kadru.
- Kolejne ujęcia najwierniej powstają z planu ogólnego w modelu edycji (Qwen-Image-Edit 2511 umie zmienić punkt widzenia): małe obroty kamery wychodzą dobrze, odwrócenie o 180° słabo — kontrplan pewniej z promptu.
- Miejsce, które w utworze mignie raz, karty nie potrzebuje.
