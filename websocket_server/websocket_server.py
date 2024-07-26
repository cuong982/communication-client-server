import asyncio

import aio_pika
import websockets
import json


# Configuration
REDIS_URL = "redis://redis:6379/0"
RABBITMQ_URL = "amqp://root:password@rabbitmq:5672//"
QUEUE_NAME = "messages"
MAX_CONNECTIONS = 50
MAX_CONCURRENT_MESSAGES = 500
HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 10  # seconds
DATABASE_URL = "postgresql://postgres:postgres@db/postgres"
# Database connection pool
db_pool = None

# In-memory store for active connections and message tracking
active_connections = {}
message_sent_flags = {}

# Semaphore to limit concurrent message processing
semaphore = asyncio.Semaphore(MAX_CONCURRENT_MESSAGES)


async def setup_rabbitmq():
    try:
        connection = await aio_pika.connect_robust("amqp://root:password@rabbitmq:5672//")
        print("-----------", connection)
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_NAME, durable=True)
        return connection, channel
    except aio_pika.exceptions.AMQPConnectionError:
        print("Failed to connect to RabbitMQ, retrying...")
        await asyncio.sleep(5)


async def heartbeat(websocket):
    while True:
        try:
            await websocket.send(json.dumps({"type": "ping"}))
            pong = await asyncio.wait_for(websocket.recv(), HEARTBEAT_TIMEOUT)
            pong_data = json.loads(pong)
            if pong_data.get("type") != "pong":
                raise ValueError("Invalid pong response")
            await asyncio.sleep(HEARTBEAT_INTERVAL)
        except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed):
            print("Connection lost during heartbeat")
            break


async def register(websocket, path, channel):
    client_id = path.strip("/")
    if client_id in active_connections:
        await websocket.send(json.dumps({"error": "Already connected"}))
        return
    if len(active_connections) >= MAX_CONNECTIONS:
        await websocket.send(json.dumps({"error": "Max connections reached"}))
        return

    active_connections[client_id] = websocket
    message_sent_flags[client_id] = False  # Initially, no message sent
    await websocket.send(json.dumps({"message": "Connected"}))
    print(f"{client_id} connected.")

    try:
        async for message in websocket:
            await handle_message(client_id, websocket, message, channel)
    finally:
        await unregister(client_id)


async def unregister(client_id):
    if client_id in active_connections:
        del active_connections[client_id]
        message_sent = message_sent_flags.pop(client_id, False)
        if not message_sent:
            print(f"{client_id} disconnected without sending a message.")
        print(f"{client_id} disconnected.")


async def handle_message(client_id, websocket, message, channel):
    async with semaphore:
        print(f"Processing message from {client_id}")
        # Mark that the client has sent at least one message
        message_sent_flags[client_id] = True

        # Process the message
        message_data = json.loads(message)
        message_type = message_data.get("type")
        content = message_data.get("content", "")

        # Send the message to RabbitMQ
        await send_message_to_queue(client_id, content, message_type, channel)

        # Reply based on the type of message received
        reply = {"type": message_type, "content": f"{message_type} message reply"}
        await websocket.send(json.dumps(reply))
        print(f"Completed processing message from {client_id} with reply: {reply}")


async def send_message_to_queue(client_id, content, message_type, channel):
    message_body = json.dumps({
        "client_id": client_id,
        "content": content,
        "type": message_type
    })
    message = aio_pika.Message(
        body=message_body.encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )
    await channel.default_exchange.publish(message, routing_key=QUEUE_NAME)


async def main():
    connection, channel = await setup_rabbitmq()
    server = await websockets.serve(lambda ws, path: register(ws, path, channel), "0.0.0.0", 8000)
    print("WebSocket server started")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
