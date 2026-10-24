# Fit Balance — frontend

Responsywna aplikacja React + Vite dla klientów katalogu produktów. Wymagany Node.js 20.19+ lub 22.12+.

## Uruchomienie

W katalogu `frontend`:

```sh
npm install
npm run dev
```

Na Windows przy blokowaniu skryptów PowerShell użyj `npm.cmd` zamiast `npm`.
Otwórz adres wyświetlony przez Vite (domyślnie http://localhost:5173).
Backend musi działać osobno, domyślnie pod http://127.0.0.1:8000.
Vite przekazuje żądania `/api` do backendu, więc lokalnie nie trzeba zmieniać CORS.
Inny adres backendu można ustawić przez `API_PROXY_TARGET` w `frontend/.env.local` (wzór w `.env.example`).

## Funkcje i integracja

- Wyszukiwanie po nazwie z opóźnieniem 350 ms, sortowanie i paginacja po stronie API: `GET /api/v1/products?name=…&sort_by=name|kcal&order=asc|desc&page=1&limit=12`.
- Szczegóły pobierane przez `GET /api/v1/products/{product_id}` oraz przeliczanie kalorii i wszystkich dostępnych składników na podaną porcję w jednostce produktu.
- Ulubione przechowywane jako identyfikatory w localStorage tej przeglądarki. W widoku ulubionych dane są ponownie pobierane z API.
- Obsługa ładowania, pustych wyników, awarii API, brakujących zdjęć i nieznanych wartości odżywczych. Bez przykładowych produktów udających dane API.
- Interfejs po polsku, układ mobilny, dostępne przyciski i modal zamykany klawiszem Escape.

Kategorie wyświetlane są z `category_path`. Endpoint hierarchii oznaczony w backendzie jako testowy nie jest używany. Publiczny model produktu nie udostępnia składu ani alergenów, więc interfejs nie deklaruje ich dostępności. Aplikacja nie zawiera funkcji zarządzania katalogiem ani moderacji.

## Budowanie

```sh
npm run build
npm run preview
```

Pliki wynikowe trafiają do `frontend/dist`. Proxy deweloperskie działa tylko w `npm run dev`. Hosting produkcyjny (również test przez `preview`) wymaga przekazywania `/api` do backendu przez serwer reverse proxy lub ustawienia `VITE_API_BASE_URL` przed budowaniem i odpowiedniego CORS po stronie API. Fonty Google są opcjonalne; bez sieci używany jest font systemowy.
