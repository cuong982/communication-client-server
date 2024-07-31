import json
import asyncio
import logging

import aio_pika
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("logs/message_processor.log"),
        logging.StreamHandler()
    ]
)

# Configuration
RABBITMQ_URL = "amqp://root:password@rabbitmq:5672/"
QUEUE_NAME = "messages"


async def process_message(message):
    async with message.process():
        message_body = message.body.decode()
        data = json.loads(message_body)
        print(f"Processing message: {data}")

        # Implement time-based acceptance logic
        current_hour = datetime.now().hour
        if data['type'] == 'text' and 5 <= current_hour < 24:
            print("Text message accepted")
            # Generate and send a text reply
        elif data['type'] == 'voice' and 8 <= current_hour < 12:
            print("Voice message accepted")
            # Generate and send a voice reply
        elif data['type'] == 'video' and 20 <= current_hour < 24:
            print("Video message accepted")
            # Generate and send a video reply
        else:
            print(f"Message rejected: {data['type']} not accepted at this time")


async def connect_to_rabbitmq():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            return connection
        except aio_pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMQ, retrying...")
            await asyncio.sleep(5)


async def main():
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()
    queue = await channel.declare_queue("messages", durable=True)
    await queue.consume(process_message, no_ack=False)
    print("Waiting for messages...")

    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
