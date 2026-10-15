# Woosh (Sony AI) — jak promptować

## Jak model słucha
Model zbudowany specjalnie do **efektów dźwiękowych**: tekst → efekt oraz **wideo → zsynchronizowany dźwięk** (foley do klipu), w tym drugim z opcjonalnym tekstem, który podpowiada, co ma brzmieć. Autorzy nie publikują osobnego przewodnika promptowania — poniższe opiera się na przykładach z ich strony demonstracyjnej.

## Struktura opisu
**Krótki opis zdarzenia dźwiękowego i jego źródła**, ok. 8–15 słów: co brzmi + co się z tym dzieje. Przykłady z demonstracji autorów:
- „Emergency vehicle driving with siren on”
- „An engine humming and brakes squealing”
- „Starting a motorcycle”
- „A crowd applauds”
- (wideo + tekst) „A propeller plane flies over a snowy landscape, its engine roaring”

## Wideo → dźwięk
- Klip jest analizowany w oknie **do 8 s**; wynik jest przycinany do długości klipu.
- Bez tekstu model zgaduje dźwięk z obrazu; krótki tekst pomaga, gdy obraz jest niejednoznaczny.

## Na co jest wrażliwy / pułapki
- **Wyjście mono, 48 kHz.**
- **Głośność bywa bardzo niska** — Studio niczego nie normalizuje; podnieś poziom w montażu.
- Długie, poetyckie opisy pomagają mniej niż konkretne źródło i działanie.

## Parametry, które realnie zmieniają wynik
- **Tryb**: szybki (tekst → 5 s efektu w ok. 0,4 s; wideo → ok. 3 s) / jakość (ok. 8–12 s).

## Licencja
Wagi CC-BY-NC — tylko niekomercyjnie.

## Źródła (dostęp 2026-10-05)
- Sony AI — Woosh (strona projektu, przykłady): https://sonyresearch.github.io/Woosh/
- GitHub — SonyResearch/Woosh: https://github.com/SonyResearch/Woosh
- Sony AI — Introducing Woosh: https://ai.sony/blog/introducing-woosh-sony-ais-sound-effect-foundation-model
- Czasy i format: test własny na Sparku.
