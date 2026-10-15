<!-- Szablon medium dla promptmakera: WIDEO. Sekcje obrazu (z media/obraz.md, Bezdroża) + czas, ruch, dźwięk.
     Karta modelu ma pierwszeństwo co do formatu (np. akapit chronologiczny w LTX, sekcje i znaczniki w H3). -->
# Wideo

## Medium: wideo (jedno ujęcie)

### Budowa promptu

Te same sekcje co w obrazie — `STYLE` (medium i faktura, wspólne dla całego utworu), `CAMERA`, `SUBJECT`, `OUTFIT`, `ACTION`, `SETTING`, `DETAILS` — plus:

- `MOTION:` — co się rusza i jak, **w kolejności zdarzeń** od początku do końca ujęcia. W ujęciu 5–10 s: jedno, najwyżej dwa zdarzenia. ← Czas i rytm, Postacie i ludzie, Materia.
- `CAMERA MOVE:` — statyczna / panorama / jazda / z ręki / zbliżenie; tempo; czy kamera reaguje na to, co się dzieje. ← Kamera.
- `SOUND:` — tylko dla modeli z dźwiękiem (karta): źródła dźwięku, przestrzeń, odległość; dialog dokładnym brzmieniem w cudzysłowie, kto mówi i jak; muzyka czy jej brak. ← Dźwięk, Głos i słowo, Muzyka.

Jeśli karta modelu każe pisać jednym akapitem (np. chronologiczny opis), zachowaj tę samą treść i kolejność, tylko bez etykiet.

### Zasady przekładu

- **Ujęcie to czas.** Opisuj chronologicznie; jedno ujęcie = jedna ciągłość. Długie, złożone akcje model gubi — podziel je na ujęcia.
- **Ruch fizyczny, nie emocjonalny**: „woda wolno wlewa się pod drzwi”, nie „napięcie rośnie”.
- **Obraz startowy / klatki kluczowe / referencje**: gdy uczestnik ma już obraz, prompt opisuje głównie ruch, czas i dźwięk, a nie to, co już widać (szczegóły — karta modelu).
- **Przejście „bez cięcia”** (przestrzeń zmienia się w trakcie ruchu kamery): opisz jako jedno ciągłe ujęcie — ruch kamery, przestrzeń A na początku, zmiana w połowie, przestrzeń B na końcu; światło zmienia się naturalnie.
- **Dialog**: dokładne słowa, język (polski — sprawdź w karcie, jak model sobie radzi), sposób mówienia.
- Wszystkie zasady z obrazu obowiązują: to, co jest (nie wykluczenia), konkret techniczny, zwięzłość, `STYLE` dosłownie wspólny dla serii.
