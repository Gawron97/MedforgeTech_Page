# MedForge Tech

Samodzielna, statyczna strona firmowa: HTML, CSS i JavaScript. Bez frameworka, procesu budowania, instalowania pakietów, bazy danych ani logowania.

## Pliki

```text
index.html       polska wersja strony
en.html          angielska wersja strony
styles.css       wspólne style i układ responsywny
script.js        menu mobilne, cień nagłówka i aktualny rok
favicon.png      ikona strony
fonts/           lokalne fonty Open Sans
images/          zdjęcia strony
```

Obie wersje mają własny nagłówek, menu, przełącznik PL/EN, sekcje treści oraz stopkę. Fonty i zdjęcia są lokalne; strona nie potrzebuje zewnętrznego kreatora, osadzenia ani CDN.

## Lokalny podgląd

Można otworzyć `index.html` w przeglądarce. Do podglądu przez HTTP, jeżeli masz Python, uruchom w katalogu projektu:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Następnie otwórz `http://127.0.0.1:8000/`. Angielska wersja to `http://127.0.0.1:8000/en.html`. Ctrl+C zatrzymuje serwer. Jeśli serwer już działa na tym porcie, skorzystaj z niego lub wybierz inny port.

## GitHub i Cloudflare Pages

Projekt można umieścić w repozytorium GitHub, a potem podłączyć repozytorium do Cloudflare Pages. Nie wykonano jeszcze publikacji ani konfiguracji kont.

Konfiguracja Pages dla obecnego układu plików:

| Pole | Wartość |
| --- | --- |
| Framework preset | None / brak frameworka |
| Production branch | gałąź z aktualną stroną, np. `main` |
| Root directory | domyślny katalog główny repozytorium |
| Build command | `exit 0` |
| Build output directory | `.` |

W katalogu wyjściowym znajduje się już `index.html`, więc nie trzeba tworzyć `dist/`, uruchamiać npm ani dodawać konfiguracji Workerów. Prześlij razem z HTML wszystkie style, skrypt, zdjęcia, fonty i favicon. Repozytorium nie powinno zawierać lokalnych kopii zapasowych, danych logowania ani `.git` jako przesyłanego pliku.

Oficjalna instrukcja: [Static HTML — Cloudflare Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

## Edytowanie i ograniczenia

- Treść PL zmieniaj w `index.html`, EN w `en.html`; wersje językowe są tłumaczone ręcznie.
- Wygląd zmieniaj w `styles.css`, zachowanie menu w `script.js`.
- Kontakt to link `mailto:kontakt@medforgetech.pl`, który otwiera aplikację pocztową. Potwierdź, że adres działa przed publikacją. Strona nie wysyła formularzy po stronie serwera.
- Sklep i obsługa zamówień nie są częścią tego projektu. Jeśli chcesz zachować dotychczasowy sklep, można później dodać odnośnik do jego rzeczywistego adresu.
- Część zdjęć przedstawia obszary działalności i nie powinna być traktowana jako potwierdzenie konkretnych realizacji lub certyfikacji firmy.
- Przed publikacją sprawdź treść, adres kontaktowy i prawa do użytych zdjęć.

Nie ma tu konfiguracji poprzedniego frameworka ani dodatków do osadzania strony w kreatorze.
