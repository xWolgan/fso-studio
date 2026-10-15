# OmniVoice — jak promptować

## Jak model słucha
Model mowy (k2-fsa) dla ponad 600 języków — **dobrze mówi po polsku** (w naszym teście zgodność słów 0,93). Trzy sposoby pracy: zwykła synteza, **projektowanie głosu** z listy cech (bez nagrania) i **klonowanie głosu** z krótkiego nagrania. Tekst czyta tak, jak jest zapisany — interpunkcja kształtuje frazę.

## Projektowanie głosu (cechy z listy)
Cechy oddzielone przecinkami, **jedna cecha z każdej kategorii**:
- płeć: male / female
- wiek: child, teenager, young adult, middle-aged, elderly
- wysokość: very low pitch, low pitch, moderate pitch, high pitch, very high pitch
- styl: whisper
- akcent angielski: American, British, Australian, Canadian, Indian… (tylko przy angielskim tekście)

Przykład: `female, middle-aged, low pitch` albo `male, elderly, whisper`. Opisów prozą („ciepły, zmęczony głos”) model w tym trybie **nie rozumie**.

W Studiu tekst próbki (pole „tekst próbki”) musi być w języku wybranym w polu „język”: model najpierw czyta go nowym głosem, a potem klonuje to nagranie i nim mówi Twój tekst. Akcent działa więc tylko przy angielskim tekście. Każde uruchomienie projektuje głos od nowa — żeby mieć ten sam głos w wielu kwestiach, pobierz „wzorzec” i użyj go w klonowaniu.

## Klonowanie głosu
- Nagranie **3–10 s**, czysta mowa, najlepiej z chwilą ciszy na końcu. Dłuższe spowalnia i może pogorszyć klon.
- **Transkrypcja próbki** — dokładnie to, co słychać w nagraniu (bez niej Studio nic nie wygeneruje).
- Nagranie w **tym samym języku**, w którym ma mówić klon — inaczej pojawia się akcent.
- Pogłos, taśma, telefon z próbki się nie przenoszą — model „czyści” dźwięk.

## Tekst: wymowa, pauzy, dźwięki niewerbalne
- Interpunkcja = fraza i pauzy (kropka, przecinek, myślnik, wielokropek) — pauza z interpunkcji jest prawdopodobna, nie pewna. Tekst zawsze kończ kropką, pytajnikiem albo wykrzyknikiem (inaczej model chętniej ucina końcówkę).
- **Dźwięki niewerbalne w nawiasach ostrych:** `<laughter>`, `<sigh>` (oraz np. `<question-en>`, `<surprise-ah>`, `<dissatisfaction-hnn>` — po polsku najpewniejsze są `<laughter>` i `<sigh>`). **Nie pisz `[laughter]`** — w Studiu nawiasy kwadratowe mają inne znaczenie.
- **Pauza o dokładnej długości:** `[pause:1.5s]`, `[pause:500ms]` — pewniejsza niż kropka.
- **Zmiana języka fragmentu:** `[en:]` przed fragmentem po angielsku.
- **Każdy inny `[…]` znika** (Studio traktuje go jako nazwę postaci) — nie wpisuj didaskaliów typu `[wzdycha]`. Zapis fonetyczny z dokumentacji modelu (`[B EY1 S]`) w Studiu nie działa.
- **Liczby, daty i skróty pisz słownie** (normalizacja tekstu jest wyłączona).

## Na co jest wrażliwy / pułapki
- Cechy spoza listy są ignorowane; szept i niska wysokość nie działają z „child”.
- Emocji nie da się zadać opisem — niesie ją tylko próbka (klon), tekst i interpunkcja.
- Bez próbki i bez cech (zwykła synteza) model przy każdym seedzie wybiera **inny głos**.
- Nowa linia nie jest pauzą — wersy oddzielaj interpunkcją albo `[pause:…]`.
- Bardzo długi tekst warto dzielić na akapity (osobne generacje) — łatwiej poprawiać, mniejsze ryzyko zmiany głosu w trakcie.

## Parametry, które realnie zmieniają wynik
- **tempo mowy** 0,5–2,0 (>1 szybciej, <1 wolniej; nieco wolniej pomaga, gdy model ucina końcówki). Stałej długości w sekundach Studio nie wystawia.
- **seed** — wyniki mocno się różnią; spróbuj 2–3 i zapisz udany.

## Licencja
CC-BY-NC — tylko niekomercyjnie.

## Źródła (dostęp 2026-10-05)
- k2-fsa/OmniVoice (README): https://github.com/k2-fsa/OmniVoice
- OmniVoice — voice design: https://github.com/k2-fsa/OmniVoice/blob/master/docs/voice-design.md
- TTS Audio Suite — OmniVoice Tags Guide (składnia znaczników w Studiu): https://github.com/diodiogod/TTS-Audio-Suite/blob/85da51e0/docs/OMNIVOICE_TAGS_GUIDE.md
- Test polszczyzny: własny, na Sparku.
