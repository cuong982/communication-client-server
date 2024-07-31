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
        ws = websocket.create_connection(SERVER_URL)
        try:
            message_type = random.choice(MESSAGE_TYPES)
            content = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            message = json.dumps({
                "type": message_type,
                "content": content
            })
            self.send_message(ws, message)
            response = self.receive_message(ws)
            print(f"Received message: {response}")
            self.handle_response(response)
        finally:
            ws.close()

    def send_message(self, ws, message):
        """
        Send a message to the WebSocket server.
        """
        ws.send(json.dumps(message))
        print(f"Sent message: {message}")

    def receive_message(self, ws):
        """
        Receive a message from the WebSocket server.
        """
        try:
            message = ws.recv()
            return json.loads(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None

    def handle_response(self, response):
        """
        Handle the response received from the WebSocket server.
        """
        if response:
            # Process the response here
            print(f"Handling response: {response}")
            if response.get("type") == "update":
                print(f"Received update: {response['data']}")
            else:
                print("Received other type of message.")
        else:
            print("No response to handle.")


class WebSocketUser(HttpUser):
    tasks = [WebSocketUserTask]
    wait_time = between(1, 2)  # Simulate a delay between tasks

    def on_start(self):
        print("WebSocketUser started")

    def on_stop(self):
        print("WebSocketUser stopped")
