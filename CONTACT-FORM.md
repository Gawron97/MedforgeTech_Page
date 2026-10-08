# Formularz kontaktowy — podłączenie Twojego Workera

Frontend jest przygotowany w `index.html` (PL) i `en.html` (EN), ze wspólnymi
stylami i obsługą formularza w `contact-form.js`. Kliknięcie w sekcji kontaktowej rozwija formularz,
a link w stopce przewija do sekcji kontaktu bez rozwijania formularza. Kod Workera nie jest częścią zmian.
Plik `.assetsignore` wyklucza instrukcje i lokalne pliki konfiguracyjne z publikowanych zasobów.

## Organizacja plików

- `index.html` / `en.html`: osobne strony PL/EN i stałe teksty formularza.
- `script.js`: menu mobilne, nagłówek i rok w stopce.
- `contact-form.js`: wspólna logika formularza bez tekstów językowych.
- `locales/pl.json` / `locales/en.json`: komunikaty używane przez formularz.
- `contact-config.js`: publiczne ustawienia połączenia z Workerem i Turnstile.

`contact-form.js` jest ładowany jako moduł. Elementy HTML i stan formularza są
przechowywane na poziomie modułu, a zdarzenia wskazują bezpośrednio nazwane funkcje.
`initContactForm()` ładuje komunikaty i podpina zdarzenia. Kolejne bloki obsługują
walidację, Turnstile i wysyłanie wiadomości. Otwieranie panelu obsługuje natywny
element HTML `<details>` po kliknięciu `<summary>`.

Formularz wybiera JSON na podstawie `<html lang="pl">` lub `<html lang="en">`.
Oba słowniki mają te same klucze. Nie trzeba zmieniać JS, aby poprawić komunikat.
Jeśli JSON się nie załaduje, pozostaje komunikat awaryjny z odpowiedniego HTML-a
i wysyłanie jest zablokowane. Podgląd uruchamiaj przez serwer HTTP, nie `file://`.

## Konfiguracja frontendu

W `contact-config.js` ustaw:

- `endpoint`: domyślnie `/api/contact`, obsługiwany przez Twojego Workera w tej samej domenie.
- `turnstileSiteKey`: publiczny klucz widgetu Cloudflare Turnstile dla domeny strony.

Klucz jest celowo pusty. Do czasu jego ustawienia formularz pokazuje komunikat
o niedostępności i blokuje wysyłanie. Po konfiguracji przycisk staje się aktywny
dopiero po otrzymaniu tokenu Turnstile. Widget ładuje się przy otwarciu formularza.
Sekret Turnstile i dane do wysyłki maili przechowuj wyłącznie po stronie Workera.

## Żądanie

Frontend wysyła `POST /api/contact` z nagłówkiem `Content-Type: application/json`:

```json
{
  "name": "Jan Kowalski",
  "email": "jan@example.com",
  "message": "Chciałbym omówić projekt prototypu…",
  "turnstileToken": "token-z-widgetu",
  "language": "pl"
}
```

`language` ma wartość `pl` lub `en`. Wymagane pola mają limity:
imię 100 znaków, e-mail 254 znaki, wiadomość 5000 znaków.
Frontend usuwa spacje z początku i końca wartości.
Worker musi samodzielnie sprawdzić typy, wymagane pola, format e-maila,
limity długości i rozmiaru żądania oraz odrzucić puste wartości po przycięciu spacji.

## Odpowiedź

Dopiero po zaakceptowaniu wysyłki przez usługę pocztową zwróć HTTP 200:

```json
{ "success": true }
```

Błędy zwracaj jako JSON z odpowiednim statusem, np.:

```json
{ "success": false, "error": "Invalid request" }
```

Frontend rozpoznaje HTTP 400/422 (nieprawidłowe dane), 403 (weryfikacja),
429 (zbyt wiele prób) oraz pozostałe błędy. Użytkownik widzi komunikaty w języku
strony; surowe komunikaty z backendu nie są wyświetlane.
Samo HTTP 200 bez `success: true` nie jest uznawane za powodzenie.

Przy sukcesie pola są czyszczone. Przy błędzie pozostają wypełnione.
W trakcie wysyłki pola i przycisk są blokowane. Po 15 sekundach frontend przerywa
oczekiwanie; nie ponawia żądania automatycznie, bo Worker mógł już wysłać mail.
Token Turnstile jest resetowany po każdej próbie i trzeba otrzymać nowy.

## Odbiorca i nadawca — konfiguracja Workera

- Stały odbiorca: **`project@medforgetech.pl`**.
- Nadawca: zatwierdzony adres Twojej domeny, np. `formularz@medforgetech.pl`.
- `Reply-To`: zweryfikowany adres e-mail wpisany przez użytkownika.
- Treść: imię, e-mail, wiadomość i opcjonalnie język formularza.

Odbiorcę ustaw w konfiguracji Workera. Frontend nie przesyła adresu docelowego;
nie pozwalaj klientowi go wybierać. Nie używaj e-maila użytkownika jako nadawcy.
Przy treści HTML escapuj dane użytkownika; w nagłówkach odrzucaj znaki CR/LF.

## Turnstile i ochrona endpointu

Przed wysłaniem maila Worker musi zweryfikować token poprzez Siteverify,
sprawdzić `success`, oczekiwany `hostname` i `action: "contact"`.
Odrzuć brak tokenu, token nieprawidłowy lub wygasły. Dodaj ograniczenie liczby prób
i dopuszczaj wyłącznie zamierzone pochodzenie żądań. Frontend nie zastępuje
weryfikacji serwerowej ani ograniczania ruchu.

Jeśli wybierzesz endpoint w innej domenie, Worker musi obsługiwać preflight
`OPTIONS` i CORS dla konkretnej domeny strony. Wariant `/api/contact` tego nie wymaga.
Obecny `wrangler.jsonc` nadal zawiera wyłącznie konfigurację plików statycznych;
przy podłączaniu backendu skonfiguruj wejście Workera i routing `/api/contact`.

Dokumentacja:

- [Turnstile — renderowanie widgetu](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/)
- [Turnstile — walidacja serwerowa](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)
- [Turnstile — klucze testowe](https://developers.cloudflare.com/turnstile/troubleshooting/testing/)

Przed uruchomieniem sprawdź oba języki, telefon, poprawne wysłanie,
błąd backendu, wygasły token i limit prób. Testy z atrapą API potwierdzają
zachowanie interfejsu; rzeczywistą dostawę maila sprawdzisz po podłączeniu Workera.
