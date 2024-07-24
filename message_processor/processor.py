import json
import asyncio
from aio_pika import connect_robust

from datetime import datetime

# Configuration
RABBITMQ_URL = "amqp://root:password@rabbitmq/"
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
