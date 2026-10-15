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
