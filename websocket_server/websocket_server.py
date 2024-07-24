import asyncio
import websockets
import json
import redis.asyncio as aioredis
import random

# Configuration
REDIS_URL = "redis://redis:6379/0"
MAX_CONNECTIONS = 50
MAX_CONCURRENT_MESSAGES = 500
HEARTBEAT_INTERVAL = 30  # seconds
HEARTBEAT_TIMEOUT = 10  # seconds

# In-memory store for active connections and message tracking
active_connections = {}
message_sent_flags = {}

# Semaphore to limit concurrent message processing
semaphore = asyncio.Semaphore(MAX_CONCURRENT_MESSAGES)


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


async def register(websocket, path):
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
            await handle_message(client_id, websocket, message)
    finally:
        await unregister(client_id)


async def unregister(client_id):
    if client_id in active_connections:
        del active_connections[client_id]
        message_sent = message_sent_flags.pop(client_id, False)
        if not message_sent:
            print(f"{client_id} disconnected without sending a message.")
        print(f"{client_id} disconnected.")


async def handle_message(client_id, websocket, message):
    async with semaphore:
        print(f"Processing message from {client_id}")
        # Mark that the client has sent at least one message
        message_sent_flags[client_id] = True

        # Process the message
        message_data = json.loads(message)
        message_type = message_data.get("type")

        if message_type == "text":
            response_time = random.uniform(0, 1)
            await asyncio.sleep(response_time)
            reply = {"type": "text", "content": "Text message reply"}
        elif message_type == "voice":
            response_time = random.uniform(1, 2)
            await asyncio.sleep(response_time)
            reply = {"type": "voice", "content": "Voice message reply with text and voice"}
        elif message_type == "video":
            response_time = random.uniform(2, 3)
            await asyncio.sleep(response_time)
            reply = {"type": "video", "content": "Video message reply with text, voice, and image"}
        else:
            reply = {"error": "Unknown message type"}

        await websocket.send(json.dumps(reply))
        print(f"Completed processing message from {client_id} with reply: {reply}")


async def main():
    redis = aioredis.from_url(REDIS_URL)
    server = await websockets.serve(register, "0.0.0.0", 8000)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
