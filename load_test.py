import asyncio
import websockets
import json
import random
import string

# Configuration
NUM_CLIENTS = 100
TOTAL_MESSAGES = 1000
SERVER_URL = "ws://localhost:8000"  # Replace with your WebSocket server URL
MESSAGE_TYPES = ["text", "voice", "video"]


async def send_message(client_id, websocket):
    message_type = random.choice(MESSAGE_TYPES)
    content = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    message = json.dumps({
        "type": message_type,
        "content": content
    })
    await websocket.send(message)
    print(f"Client {client_id} sent: {message}")
    response = await websocket.recv()
    print(f"Client {client_id} received: {response}")


async def client_behavior(client_id):
    async with websockets.connect(f"{SERVER_URL}/{client_id}") as websocket:
        for _ in range(TOTAL_MESSAGES // NUM_CLIENTS):
            await send_message(client_id, websocket)
            await asyncio.sleep(random.uniform(0.1, 2))  # Random delay between messages


async def main():
    # Launch all client tasks
    tasks = [client_behavior(client_id) for client_id in range(NUM_CLIENTS)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
