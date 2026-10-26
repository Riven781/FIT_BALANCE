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
Vite przekazuje żądania `/api` i `/category-hierarchy` do backendu, więc lokalnie nie trzeba zmieniać CORS.
Inny adres backendu można ustawić przez `API_PROXY_TARGET` w `frontend/.env.local` (wzór w `.env.example`).

## Funkcje i integracja

- Wyszukiwanie po nazwie z opóźnieniem 350 ms, sortowanie i paginacja po stronie API: `GET /api/v1/products?name=…&sort_by=name|kcal&order=asc|desc&page=1&limit=12`.
- Szczegóły pobierane przez `GET /api/v1/products/{product_id}` oraz przeliczanie kalorii i wszystkich dostępnych składników na podaną porcję w jednostce produktu.
- Ulubione przechowywane jako identyfikatory w localStorage tej przeglądarki. W widoku ulubionych dane są ponownie pobierane z API.
- Obsługa ładowania, pustych wyników, awarii API, brakujących zdjęć i nieznanych wartości odżywczych. Bez przykładowych produktów udających dane API.
- Interfejs po polsku, układ mobilny, dostępne przyciski i modal zamykany klawiszem Escape.

Kategorie pobierane są przez `GET /category-hierarchy/{id}`. API nie udostępnia endpointu wyboru aktywnej hierarchii, dlatego `VITE_CATEGORY_HIERARCHY_ID` w `frontend/.env.local` wskazuje jej identyfikator (domyślnie `1`, zgodnie ze skryptem inicjalizacji danych). Używana jest tylko hierarchia ze statusem `ACTIVE`. Przy innym identyfikatorze ustaw zmienną i uruchom ponownie Vite; błąd kategorii nie blokuje wyszukiwania wszystkich produktów.

Filtr kategorii pozwala wybierać pełną ścieżkę z listy, odkrywać podkategorie przyciskami i wracać do kategorii nadrzędnej. Wyszukiwanie po nazwie i sortowanie działają w ramach wyboru. Katalog wysyła `category_id` do endpointu produktów (backend uwzględnia potomków); ulubione są filtrowane po `category_path`. Zmiana kategorii resetuje paginację do strony 1. Filtr można usunąć bez kasowania wpisanej nazwy.

Kod filtra znajduje się w `src/components/CategoryFilter.jsx`, pobieranie w `src/hooks/useCategories.js`, a budowanie ścieżek w `src/utils/categories.js`. Testy ścieżek i filtrowania ulubionych uruchomisz przez `npm test`.

Menu `src/components/CategoryTree.jsx` rozdziela wybór całej gałęzi (kliknięcie nazwy) od rozwinięcia podkategorii (strzałka). Dzięki temu można wybrać zarówno „Słodycze i przekąski”, jak i samo „Słodycze”. Filtr nadal przekazuje jeden `category_id`: potomków uwzględnia backend, zgodnie z testami `tests/query/test_product_query.py`.

Jeżeli wszystkie filtry kategorii zwracają puste wyniki, sprawdź powiązania `ProductCategoryClosure` po stronie backendu. W zbadanej lokalnej bazie tabela była pusta mimo istniejących kategorii i przypisań produktów. W testach zapytań i integracji jest ona jawnie wypełniana. Sam frontend nie może odtworzyć powiązań produktów, gdy API zwraca puste `category_path`. Propozycja uzupełnienia brakujących relacji znajduje się w `scripts/repair-category-closure.sql`; wymaga osobnej zgody na zmianę bazy poza `frontend/`. Skrypt sprawdzono wyłącznie na kopii w pamięci, także pod kątem ponownego uruchomienia bez duplikatów.

Publiczny model produktu nie udostępnia składu ani alergenów. Aplikacja nie zawiera funkcji zarządzania katalogiem ani moderacji.

## Budowanie

Kod jest podzielony na `src/App.jsx` (widok i obsługa katalogu), `src/components/` (karty, zdjęcia i szczegóły produktów), `src/api.js` (REST) oraz `src/utils/` (formatowanie danych). `src/main.jsx` uruchamia aplikację. Style są sformatowane w blokach; `readability.css` zawiera poprawki czytelności i uproszczone karty mobilne.

Na telefonie karty tworzą dwie kolumny, gdy dostępna szerokość pozwala pomieścić dwie karty po 150 px z odstępem. Zdjęcia, pełne nazwy i kcal pozostają widoczne; pozostałe wartości są dostępne w szczegółach.

Hook `src/hooks/usePagination.js` obsługuje numer strony i przewijanie. Przejście strzałką w prawo ustawia widok na początku nowych wyników dopiero po ich załadowaniu. Strzałka w lewo nie uruchamia przewijania. Dotychczasowe karty pozostają widoczne podczas pobierania, a przyciski paginacji są wtedy zablokowane.

Formatowanie kodu: `npm run format`. Sprawdzenie formatowania: `npm run format:check`.

```sh
npm run build
npm run preview
```

Pliki wynikowe trafiają do `frontend/dist`. Proxy deweloperskie działa tylko w `npm run dev`. Hosting produkcyjny (również test przez `preview`) wymaga przekazywania `/api` oraz `/category-hierarchy` do backendu przez serwer reverse proxy lub ustawienia `VITE_API_BASE_URL` przed budowaniem i odpowiedniego CORS po stronie API. Fonty Google są opcjonalne; bez sieci używany jest font systemowy.
