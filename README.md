# FitBalance

**FitBalance** to aplikacja internetowa umożliwiająca wyszukiwanie i przeglądanie produktów spożywczych, ze szczególnym uwzględnieniem ich wartości odżywczych oraz kategoryzacji.

Aplikacja pozwala użytkownikom wyszukiwać produkty, porównywać ich wartości odżywcze oraz podejmować bardziej świadome decyzje żywieniowe.

## Architektura backendu

Backend aplikacji został zbudowany w **Pythonie z wykorzystaniem frameworka FastAPI**, zgodnie z zasadami **Domain-Driven Design (DDD)**, co zapewnia modularność, łatwość utrzymania oraz możliwość dalszego rozwoju systemu.

Architektura aplikacji opiera się na podziale na domeny biznesowe, z wyraźnym oddzieleniem logiki biznesowej, warstwy aplikacyjnej oraz infrastruktury.

### Technologie

- **Python** – język programowania backendu
- **FastAPI** – framework do budowania REST API
- **SQLAlchemy (Async)** – asynchroniczna komunikacja z bazą danych i mapowanie obiektowo-relacyjne (ORM)
- **SQLite** – relacyjna baza danych (planowana migracja do PostgreSQL)
- **Redis** – infrastruktura komunikacji między komponentami
- **Docker i Docker Compose** – konteneryzacja i zarządzanie usługami
- **JWT, Sesja** – uwierzytelnianie i autoryzacja

### Wykorzystane wzorce i koncepcje architektoniczne

- **Domain-Driven Design (DDD)** – modelowanie logiki biznesowej z wykorzystaniem modeli domenowych i kontekstów ograniczonych (Bounded Contexts)
- **CQRS** – rozdzielenie operacji modyfikujących stan systemu od operacji odczytu
- **Event-Driven Architecture** – asynchroniczna komunikacja i przetwarzanie zdarzeń domenowych
- **Transactional Outbox Pattern** – niezawodne zapisywanie i przetwarzanie komunikatów
- **Repository Pattern** – oddzielenie logiki domenowej od mechanizmów przechowywania danych
- **Optimistic Concurrency Control** – kontrola współbieżnych modyfikacji danych

## Funkcjonalności

- Wyszukiwanie i filtrowanie produktów spożywczych
- Przeglądanie informacji o wartościach odżywczych
- Hierarchiczna kategoryzacja produktów
- Dodawanie i edytowanie produktów
- Uwierzytelnianie użytkowników i zarządzanie uprawnieniami
- Zgłaszanie błędów i nieprawidłowości dotyczących produktów
- Wersjonowanie hierarchii kategorii i zarządzanie procesem ich publikacji

## Status projektu

🚧 **Projekt w trakcie rozwoju**

FitBalance jest aktywnie rozwijany.