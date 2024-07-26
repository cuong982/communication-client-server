import pika
import json

def consume_messages(callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='message_queue')

    def on_message(ch, method, properties, body):
        message = json.loads(body)
        callback(message)

    channel.basic_consume(queue='message_queue', on_message_callback=on_message, auto_ack=True)
    print('Waiting for messages...')
    channel.start_consuming()
