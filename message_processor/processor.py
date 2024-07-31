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
PREFETCH_COUNT = 1  # Number of messages to fetch at a time


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        message_body = message.body.decode()
        data = json.loads(message_body)
        logging.info(f"Processing message: {data}")

        # Implement time-based acceptance logic
        current_hour = datetime.now().hour
        if data['type'] == 'text' and 5 <= current_hour < 24:
            logging.info("Text message accepted")
            # Generate and send a text reply
        elif data['type'] == 'voice' and 8 <= current_hour < 12:
            logging.info("Voice message accepted")
            # Generate and send a voice reply
        elif data['type'] == 'video' and 20 <= current_hour < 24:
            logging.info("Video message accepted")
            # Generate and send a video reply
        else:
            logging.info(f"Message rejected: {data['type']} not accepted at this time")


async def connect_to_rabbitmq():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            return connection
        except aio_pika.exceptions.AMQPConnectionError:
            logging.error("Failed to connect to RabbitMQ, retrying...")
            await asyncio.sleep(5)


async def main():
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()

    # Set QoS
    await channel.set_qos(prefetch_count=PREFETCH_COUNT)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(process_message, no_ack=False)
    logging.info("Waiting for messages...")

    try:
        await asyncio.Future()  # Keep the event loop running
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
