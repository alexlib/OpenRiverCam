import os
import pika
import json

velocity = {"file": {"bucket": "example", "identifier": "velocity.nc"}}

body = {
    "type": "filter_piv",
    "kwargs": {
        "velocity": velocity,
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
