import random
import string
from locust import HttpUser, TaskSet, task, between
import websocket
import json

MESSAGE_TYPES = ["text", "voice", "video"]
SERVER_URL = "ws://websocket_server:8000"


class WebSocketUserTask(TaskSet):

    @task
    def websocket_task(self):
        """
        This method represents a task that interacts with a WebSocket server.
        """
        self.perform_websocket_interaction()

    def perform_websocket_interaction(self):
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        ws = websocket.create_connection(f'{SERVER_URL}/{content}')
        try:
            message_type = random.choice(MESSAGE_TYPES)

            message = {
                "type": message_type,
                "content": content
            }
            self.send_message(ws, message)
            self.receive_messages(ws)
        finally:
            ws.close()

    def send_message(self, ws, message):
        """
        Send a message to the WebSocket server.
        """
        ws.send(json.dumps(message))
        print(f"Sent message: {message}")

    def receive_messages(self, ws):
        """
        Receive and handle messages from the WebSocket server.
        """
        while True:
            try:
                message = ws.recv()
                data = json.loads(message)
                print("Received message:", data)
                if "check_connection" in data and data["check_connection"] == "PING":
                    self.send_pong(ws)
                else:
                    self.handle_response(data)
            except websocket.WebSocketConnectionClosedException:
                print("Connection closed by the server.")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    def send_pong(self, ws):
        """
        Send a PONG response to a PING message.
        """
        pong_message = json.dumps({"check_connection": "PONG"})
        ws.send(pong_message)
        print("Sent PONG:", pong_message)

    def handle_response(self, response):
        """
        Handle the response received from the WebSocket server.
        """
        print(f"Handling response: {response}")


class WebSocketUser(HttpUser):
    tasks = [WebSocketUserTask]
    wait_time = between(0, 0.1)  # Simulate a delay between tasks

    def on_start(self):
        print("WebSocketUser started")

    def on_stop(self):
        print("WebSocketUser stopped")
