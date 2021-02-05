import os
import pika
import json
from example_data import movie

body = {
    "type": "filter_piv",
    "kwargs": {
        "movie": movie,
    },
}


connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()

channel.queue_declare(queue="processing")
channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
print(" [x] Sent 'filter_piv'")
connection.close()
