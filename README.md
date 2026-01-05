# PS-Uber Eats 🍕

System mikroserwisowy symulujący platformę do zamawiania jedzenia online.

## 🚀 Architektura

Projekt składa się z 3 mikroserwisów:

- **Order Service** – REST API z pełnym CRUD + PostgreSQL
- **Payment Service** – konsument wiadomości z RabbitMQ
- **Delivery Service** – konsument wiadomości z RabbitMQ

Komunikacja między serwisami odbywa się asynchronicznie przez RabbitMQ.

## 📦 Technologie

- **Python 3.11**
- **FastAPI + Uvicorn** – REST API
- **RabbitMQ** – kolejka komunikatów (AMQP)
- **PostgreSQL** – baza danych zamówień
- **Docker + Docker Compose** – konteneryzacja i uruchamianie serwisów
- **Frontend** – HTML, CSS, JavaScript (Vanilla JS)

## 🛠️ Uruchomienie

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

## 🌐 Frontend

Aplikacja posiada prosty interfejs webowy umożliwiający zarządzanie zamówieniami.

### Uruchomienie frontendu

1. Upewnij się, że Docker Compose jest uruchomiony (`docker-compose up -d`)
2. Otwórz plik `frontend/index.html` w przeglądarce

### Funkcjonalności interfejsu

- **Dashboard ze statystykami** – liczba zamówień, łączna wartość, status połączenia z API
- **Tworzenie zamówień** – formularz dodawania nowych zamówień
- **Lista zamówień** – tabelka z wszystkimi zamówieniami z bazy danych
- **Edycja zamówień** – modal umożliwiający edycję istniejących zamówień
- **Usuwanie zamówień** – przycisk usuwania z potwierdzeniem
- **Auto-refresh** – automatyczne odświeżanie listy co 3 sekundy
- **Monitoring statusu** – wskaźnik pokazujący czy backend działa (🟢/🔴)

### Struktura frontendu

```
frontend/
├── index.html    # Struktura HTML interfejsu
├── style.css     # Stylowanie (gradient, karty, tabela)
└── script.js     # Logika (fetch API, CRUD operations)
```

### Zabezpieczenia

- **CORS** – Order Service ma włączony CORS dla żądań z przeglądarki
- **Walidacja formularzy** – nie można dodać zamówienia z ceną ≤ 0

## 🧪 Funkcjonalności

- **Order Service** – obsługa zamówień z pełnym CRUD (tworzenie, odczyt, aktualizacja, usuwanie)
- **Payment Service** – odbiór zamówień i symulacja płatności
- **Delivery Service** – odbiór zamówień i symulacja procesu dostawy
- **Asynchroniczna komunikacja** między serwisami przy użyciu RabbitMQ
- **Dane zamówień** przechowywane w PostgreSQL
- **Interfejs webowy** do zarządzania zamówieniami

## 📊 Przepływ danych

```
Użytkownik → [Order Service REST API]
                ↓
           [PostgreSQL Database]
                ↓
           [RabbitMQ Queue: "orders"]
                ↓
      [Payment Service] (odbiera wiadomości)
                ↓
      [Delivery Service] (odbiera wiadomości)
```

Każda operacja (CREATE, UPDATE, DELETE) w Order Service:
1. Zapisuje dane w **PostgreSQL**
2. Wysyła wiadomość do **RabbitMQ** (asynchronicznie)
3. Payment i Delivery odbierają wiadomości i przetwarzają

## 🔧 Porty

- **Order Service:** 8000
- **Payment Service:** 8001
- **Delivery Service:** 8002
- **PostgreSQL:** 5432
- **RabbitMQ:** 5672 (AMQP) + 15672 (Management UI)

## 📝 RabbitMQ Management

Panel zarządzania: http://localhost:15672
- Login: `guest`
- Hasło: `guest`

Tutaj możesz zobaczyć kolejki, wiadomości i konsumentów.

## 🎯 Spełnione wymagania projektu

### ✅ Ocena 3.0 (dostateczny)
- ✅ Podstawowe operacje sieciowe – **HTTP (TCP), AMQP (RabbitMQ)**
- ✅ Protokoły aplikacyjne – **REST API (HTTP), RabbitMQ (AMQP na porcie 5672)**
- ✅ Dokumentacja – **README.md**

### ✅ Ocena 4.0 (dobry)
- ✅ **REST API z pełnym CRUD** – CREATE, READ, UPDATE, DELETE
- ✅ **Połączenie z PostgreSQL** – zamówienia zapisywane w bazie
- ✅ **Integracja z RabbitMQ** – asynchroniczna komunikacja między serwisami
- ✅ Wszystkie wymogi z 3.0

### ✅ Ocena 5.0 (bardzo dobry)
- ✅ **3 Mikroserwisy** – Order, Payment, Delivery
- ✅ **RabbitMQ** – asynchroniczna kolejka komunikatów
- ✅ **Asynchroniczna komunikacja** – Order wysyła wiadomości, Payment i Delivery odbierają
- ✅ **Frontend** – pełny interfejs do zarządzania zamówieniami
- ✅ Wszystkie wymogi z 3.0 i 4.0

## 📋 Struktura projektu

```
PS-Uber Eats/
├── docker-compose.yml       # Konfiguracja wszystkich serwisów
├── README.md               # Dokumentacja
│
├── order/
│   ├── Dockerfile
│   ├── requirements.txt    # fastapi, uvicorn, aio-pika, psycopg2-binary
│   └── main.py            # REST API + PostgreSQL + RabbitMQ
│
├── payment/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py            # Konsument RabbitMQ
│
├── delivery/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py            # Konsument RabbitMQ
│
└── frontend/
    ├── index.html         # Interfejs użytkownika
    ├── style.css          # Stylowanie aplikacji
    └── script.js          # Logika frontendu (fetch API)
```

## 🐛 Troubleshooting

### Restart wszystkich serwisów

```bash
docker-compose restart
```

### Pełny rebuild kontenerów

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Sprawdzenie logów poszczególnych serwisów

```bash
docker-compose logs order
docker-compose logs payment
docker-compose logs delivery
```

### Sprawdzenie statusu

```bash
docker-compose ps
```

## 🎓 Autor

Projekt stworzony jako symulacja platformy zamawiania jedzenia online.
