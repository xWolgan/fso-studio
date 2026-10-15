# Z-Image Turbo — jak promptować

## Jak model słucha
Szybki model destylowany (8 kroków, CFG 1). Najlepiej reaguje na **długie, konkretne opisy** pisane jak instrukcja dla operatora, a nie listę przymiotników. **Negatywny prompt nie działa** (przy CFG 1 jest ignorowany) — wszystko, co ma być w kadrze albo czego ma w nim nie być, opisuje się pozytywnie.

## Struktura promptu i kolejność bloków
`[medium i styl] → [plan, kąt i kompozycja] → [obiekt/postać: wygląd] → [ubiór, materiały, kolory] → [otoczenie/tło] → [światło i paleta] → [faktura; dla zdjęcia: jeden aparat/obiektyw i jeden film] → [tekst w kadrze] → [ograniczenia opisane pozytywnie]`

Pisz **po angielsku**, pełnymi zdaniami, rzeczowo — nie listą tagów. Autorzy zalecają długie, szczegółowe prompty; społeczność wskazuje ok. 80–250 słów jako dobry zakres. W Studiu prompt nie jest ucinany (limit 512 tokenów dotyczy tylko oficjalnego kodu diffusers, nie ComfyUI) i nikt go po drodze nie rozbudowuje.

Medium podaj na początku — model ciągnie do fotorealizmu; przy rysunku czy malarstwie nie używaj słów o aparacie i filmie, bo wróci zdjęcie. Nastrój przełóż na światło, paletę, kadr i materię — bez metafor i ocen („beautiful”, „masterpiece”, „8K”).

## Na co jest wrażliwy / pułapki
- Ogólniki („piękny”, „epicki”) dają generyczny wynik; szczegół działa.
- Zamiast „bez ludzi” — opisz, co jest w kadrze („pusta ulica, tylko mokry bruk i latarnie”).
- Bardzo szybki (kilka sekund) — dobry do szukania kierunku; finalną jakość porównaj z Qwen-Image 2.1.
- **Niska różnorodność:** zmiana seeda często daje prawie ten sam obraz. Wariant = inaczej opisany kadr (plan, kąt, pora, rozmieszczenie), nie tylko inny seed.
- Tekst w obrazie: krótko, dosłownie w cudzysłowie `"…"`, z miejscem i krojem. Pewnie tylko po angielsku i chińsku; polskie znaki — niepotwierdzone (napisy lepiej w Ideogram 4 lub Qwen-Image 2.1).
- Wag `(słowo:1.3)` nie ma — nawiasy i liczby trafią do modelu jako tekst.
- Bez opisu faktury (pory, splot tkaniny, ziarno) ludzie wychodzą „plastikowi” i stockowi.

## Przykłady (struktura)
- „Photograph, close-up portrait at eye level, centred composition, shallow depth of field. A middle-aged man with grey stubble, tired half-closed eyes and visible skin pores, in a dark wool coat. Behind him a blurred tram stop at dusk. Cold blue ambient light with a warm sodium streetlamp from the left. Shot on a 50mm lens, Kodak Portra 400, fine film grain.”
- „Documentary photograph, wide shot from a high angle. An empty concrete courtyard after rain, only wet concrete and puddles reflecting an overcast sky. A single red bicycle leaning against the wall in the right third. Flat diffuse light, muted grey palette with one red accent.”

## Parametry, które realnie zmieniają wynik
- **Kroki** (zaawansowane, 4–16, domyślnie 8) — model jest uczony na 8 krokach; mniej = szkic, więcej nie zawsze znaczy lepiej.
- **Seed** — słaba dźwignia (niska różnorodność); stały seed przydaje się, by zobaczyć wpływ każdej zmiany w prompcie.

## Źródła (dostęp 2026-10-05)
- Tongyi-MAI/Z-Image-Turbo — karta modelu: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo
- Tongyi-MAI/Z-Image-Turbo — „PROMPTING GUIDE” (odpowiedzi autorów): https://huggingface.co/Tongyi-MAI/Z-Image-Turbo/discussions/8
- Z-Image-Turbo Prompting Guide (społeczność): https://gist.github.com/illuminatianon/c42f8e57f1e3ebf037dd58043da9de32
- deAPI — Z-Image Turbo prompting: https://deapi.ai/blog/z-image-turbo-prompting-guide-formula-tips-and-5-example-prompts
- fal — Z-Image Turbo prompt guide: https://fal.ai/learn/devs/z-image-turbo-prompt-guide
