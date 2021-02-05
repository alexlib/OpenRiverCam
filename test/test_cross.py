import pika
import json
from example_data import movie

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()
channel.queue_declare(queue="processing")

body = {
    "type": "compute_q",
    "kwargs": {
        "movie": movie,
        "quantile": [0.1, 0.5, 0.9],
    },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
connection.close()
