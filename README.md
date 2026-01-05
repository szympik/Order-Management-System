# System Zarządzania Zamówieniami

System mikroserwisowy symulujący platformę do zamawiania jedzenia online.

---

## Architektura

Projekt składa się z 3 mikroserwisów:

- Order Service  REST API z pełnym CRUD + PostgreSQL
- Payment Service  konsument wiadomości z RabbitMQ
- Delivery Service  konsument wiadomości z RabbitMQ

Komunikacja między serwisami odbywa się asynchronicznie przez RabbitMQ.

---

## Technologie

- Python 3.11
- FastAPI + Uvicorn  REST API
- RabbitMQ  kolejka komunikatów (AMQP)
- PostgreSQL  baza danych zamówień
- Docker + Docker Compose  konteneryzacja i uruchamianie serwisów

---

## Uruchomienie

### Zbudowanie i uruchomienie wszystkich serwisów

```bash
docker-compose up --build -d
```

### Sprawdzenie statusu kontenerów

```bash
docker-compose ps
```

### Podgląd logów poszczególnych serwisów

```bash
docker-compose logs -f
```

---

## Funkcjonalności

- Order Service  obsługa zamówień z pełnym CRUD (tworzenie, odczyt, aktualizacja, usuwanie)
- Payment Service  odbiór zamówień i symulacja płatności
- Delivery Service  odbiór zamówień i symulacja procesu dostawy
- Asynchroniczna komunikacja między serwisami przy użyciu RabbitMQ
- Dane zamówień przechowywane w PostgreSQL

---

## Struktura danych

```
PS/ 
 docker-compose.yml 
 README.md 
 
 order/ 
   Dockerfile 
   requirements.txt 
   main.py 
 payment/ 
   Dockerfile 
   requirements.txt 
   main.py 
 delivery/ 
   Dockerfile 
   requirements.txt 
   main.py 
 frontend/ 
    index.html 
    style.css 
    script.js
```

---

## Przepływ danych

```
Użytkownik  [Order Service REST API]
                
           [PostgreSQL Database]
                
           [RabbitMQ Queue: "orders"]
                
      [Payment Service] (odbiera wiadomości)
                
      [Delivery Service] (odbiera wiadomości)
```

---

## Porty

- Order Service: 8000
- Payment Service: 8001
- Delivery Service: 8002
- PostgreSQL: 5432
- RabbitMQ: 5672 (AMQP) + 15672 (Management UI)

---

## Autor

Projekt stworzony jako symulacja platformy zamawiania jedzenia online.
