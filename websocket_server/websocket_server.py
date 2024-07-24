import asyncio
import websockets
import json
import redis.asyncio as aioredis

# Configuration
REDIS_URL = "redis://redis:6379/0"
MAX_CONNECTIONS = 50

# In-memory store for active connections
active_connections = {}


async def register(websocket, path):
    # Register a new client
    try:
        # Extract client ID from the path
        client_id = path.strip("/")
        if client_id in active_connections:
            await websocket.send(json.dumps({"error": "Already connected"}))
            return
        if len(active_connections) >= MAX_CONNECTIONS:
            await websocket.send(json.dumps({"error": "Max connections reached"}))
            return

        active_connections[client_id] = websocket
        await websocket.send(json.dumps({"message": "Connected"}))
        print(f"{client_id} connected.")

        async for message in websocket:
            await handle_message(client_id, message)

    finally:
        await unregister(client_id)


async def unregister(client_id):
    # Unregister a client
    if client_id in active_connections:
        del active_connections[client_id]
        print(f"{client_id} disconnected.")


async def handle_message(client_id, message):
    # Process incoming message
    print(f"Received message from {client_id}: {message}")
    # Example: Store message in Redis or process it
    # ...


async def main():
    redis = aioredis.from_url(REDIS_URL)
    server = await websockets.serve(register, "0.0.0.0", 8000)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
