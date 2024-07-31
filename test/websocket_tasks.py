import json
import random
import string

from locust import task, TaskSet
from websocket_client import WebSocketClient

MESSAGE_TYPES = ["text", "voice", "video"]


class WebSocketUserTask(TaskSet):
    async def on_start(self):
        self.client = WebSocketClient()
        await self.client.connect()

    @task
    async def send_message(self):
        message_type = random.choice(MESSAGE_TYPES)
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        message = json.dumps({
            "type": message_type,
            "content": content
        })
        await self.client.send_message(json.dumps(message))
        response = await self.client.receive_message()
        print(f"Received message: {response}")

    async def on_stop(self):
        await self.client.disconnect()
