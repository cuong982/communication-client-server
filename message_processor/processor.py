import json
import asyncio
import aio_pika
from aio_pika import connect_robust

from message_processor.utils.logging import logger

# Configuration
RABBITMQ_URL = "amqp://root:password@rabbitmq/"
QUEUE_NAME = "messages"


async def process_message(message):
    async with message.process():
        message_body = message.body.decode()
        data = json.loads(message_body)
        print(f"Processing message: {data}")
        logger.info(f"Processing message: {data}")

        # Implement your business logic here
        # For example, handle message types or route to different services
        if data['type'] == 'text':
            print("Processing text message")
        elif data['type'] == 'voice':
            print("Processing voice message")
        elif data['type'] == 'video':
            print("Processing video message")
        else:
            print(f"Unknown message type: {data['type']}")


async def main():
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Declare the queue
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    await queue.consume(process_message, no_ack=False)

    print(f"Waiting for messages in {QUEUE_NAME}. To exit press CTRL+C")
    try:
        await asyncio.Future()  # Run forever
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
