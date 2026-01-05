from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aio_pika
import json
import psycopg2
import os
import httpx
from contextlib import contextmanager

app = FastAPI()

# Dodaj CORS - musi być przed definicją endpointów
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBIT_URL = "amqp://guest:guest@rabbitmq/"
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/PLN"

# Konfiguracja bazy danych z environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("DB_NAME", "uber_eats"),
    "user": os.getenv("DB_USER", "uber"),
    "password": os.getenv("DB_PASSWORD", "uber")
}

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Inicjalizacja tabeli orders w bazie danych"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    product VARCHAR(255) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

async def get_exchange_rate():
    """Pobiera aktualny kurs EUR z zewnętrznego API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXCHANGE_API_URL, timeout=5.0)
            data = response.json()
            return data["rates"]["EUR"]
    except Exception as e:
        print(f"Exchange API error: {e}")
        return 0.22  # Fallback rate

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/exchange-rate")
async def get_current_exchange_rate():
    """Endpoint zwracający aktualny kurs PLN -> EUR"""
    rate = await get_exchange_rate()
    return {
        "from": "PLN",
        "to": "EUR",
        "rate": rate,
        "source": "exchangerate-api.com"
    }

@app.post("/orders")
async def create_order(order: dict):
    user = order.get("user")
    product = order.get("product")
    price = order.get("price")

    if not all([user, product, price]):
        raise HTTPException(status_code=400, detail="Missing required fields: user, product, price")

    try:
        # Pobierz kurs wymiany z zewnętrznego API
        eur_rate = await get_exchange_rate()
        price_eur = round(float(price) * eur_rate, 2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (user_name, product, price) VALUES (%s, %s, %s) RETURNING id",
                (user, product, price)
            )
            order_id = cursor.fetchone()[0]

        order_response = {
            "id": order_id,
            "user_name": user,
            "product": product,
            "price": float(price),
            "price_eur": price_eur,
            "exchange_rate": eur_rate
        }

        # Wyślij do RabbitMQ
        try:
            connection = await aio_pika.connect_robust(RABBIT_URL)
            channel = await connection.channel()
            queue = await channel.declare_queue("orders", durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"action": "create", "order": order_response}).encode()
                ),
                routing_key="orders"
            )

            await connection.close()
        except Exception as e:
            print(f"RabbitMQ error: {e}")

        return order_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/orders")
async def get_orders():
    try:
        # Pobierz kurs wymiany
        eur_rate = await get_exchange_rate()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_name, product, price, created_at FROM orders ORDER BY id")
            rows = cursor.fetchall()

        orders = []
        for row in rows:
            price_pln = float(row[3])
            orders.append({
                "id": row[0],
                "user_name": row[1],
                "product": row[2],
                "price": price_pln,
                "price_eur": round(price_pln * eur_rate, 2),
                "created_at": str(row[4])
            })

        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    try:
        eur_rate = await get_exchange_rate()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_name, product, price, created_at FROM orders WHERE id = %s", (order_id,))
            row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Order not found")

        price_pln = float(row[3])
        return {
            "id": row[0],
            "user_name": row[1],
            "product": row[2],
            "price": price_pln,
            "price_eur": round(price_pln * eur_rate, 2),
            "created_at": str(row[4])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/orders/{order_id}")
async def update_order(order_id: int, updated_order: dict):
    user = updated_order.get("user")
    product = updated_order.get("product")
    price = updated_order.get("price")

    if not all([user, product, price]):
        raise HTTPException(status_code=400, detail="Missing required fields: user, product, price")

    try:
        eur_rate = await get_exchange_rate()
        price_eur = round(float(price) * eur_rate, 2)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE orders SET user_name = %s, product = %s, price = %s WHERE id = %s",
                (user, product, price, order_id)
            )

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Order not found")

        order_response = {
            "id": order_id,
            "user_name": user,
            "product": product,
            "price": float(price),
            "price_eur": price_eur
        }

        # Wyślij update do RabbitMQ
        try:
            connection = await aio_pika.connect_robust(RABBIT_URL)
            channel = await connection.channel()
            queue = await channel.declare_queue("orders", durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"action": "update", "order": order_response}).encode()
                ),
                routing_key="orders"
            )

            await connection.close()
        except Exception as e:
            print(f"RabbitMQ error: {e}")

        return order_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_name, product, price FROM orders WHERE id = %s", (order_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Order not found")

            deleted_order = {
                "id": row[0],
                "user_name": row[1],
                "product": row[2],
                "price": float(row[3])
            }

            cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))

        # Wyślij delete do RabbitMQ
        try:
            connection = await aio_pika.connect_robust(RABBIT_URL)
            channel = await connection.channel()
            queue = await channel.declare_queue("orders", durable=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"action": "delete", "order_id": order_id}).encode()
                ),
                routing_key="orders"
            )

            await connection.close()
        except Exception as e:
            print(f"RabbitMQ error: {e}")

        return deleted_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
