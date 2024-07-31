import asyncio
import websockets
from config import WEBSOCKET_SERVER_URL


class WebSocketClient:
    def __init__(self):
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(WEBSOCKET_SERVER_URL)

    async def send_message(self, message):
        await self.websocket.send(message)

    async def receive_message(self):
        return await self.websocket.recv()

    async def disconnect(self):
        await self.websocket.close()
