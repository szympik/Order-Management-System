from fastapi import FastAPI
import aio_pika
import asyncio
import json
from contextlib import asynccontextmanager

RABBIT_URL = "amqp://guest:guest@rabbitmq/"

async def consume_payment_done():
    """Konsumuje potwierdzone płatności i symuluje dostawę"""
    retry_count = 0
    max_retries = 10
    
    while retry_count < max_retries:
        try:
            print(f"Delivery Service: Connecting to RabbitMQ... (attempt {retry_count + 1}/{max_retries})")
            connection = await aio_pika.connect_robust(RABBIT_URL)
            channel = await connection.channel()
            queue = await channel.declare_queue("orders", durable=True)
            
            print("Delivery Service: Connected! Listening for orders...")
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            data = json.loads(message.body.decode())
                            action = data.get("action", "create")
                            
                            if action == "create":
                                order = data.get("order", {})
                                print(f" DELIVERY STARTED: Order #{order.get('id')} - {order.get('product')} to {order.get('user')}")
                            elif action == "update":
                                order = data.get("order", {})
                                print(f" DELIVERY UPDATE: Order #{order.get('id')} delivery rescheduled")
                            elif action == "delete":
                                order_id = data.get("order_id")
                                print(f" DELIVERY CANCELLED: Order #{order_id}")
                        except Exception as e:
                            print(f"Delivery Service: Error processing message: {e}")
            
        except Exception as e:
            retry_count += 1
            print(f"Delivery Service: Connection error: {e}")
            if retry_count < max_retries:
                wait_time = min(retry_count * 2, 30)
                print(f"Delivery Service: Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                print("Delivery Service: Max retries reached, giving up")
                break

# Background task storage
background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Delivery Service: Starting up...")
    task = asyncio.create_task(consume_payment_done())
    background_tasks.add(task)
    yield
    # Shutdown
    print("Delivery Service: Shutting down...")
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"service": "delivery", "status": "listening", "queue": "orders"}

@app.get("/health")
def health():
    return {"status": "healthy"}
