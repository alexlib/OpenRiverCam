import os
import pika
import json
from example_data import movie

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()
channel.queue_declare(queue="processing")


body = {
    "type": "compute_piv",
    "kwargs": {
        "movie": movie,
        "file": {"bucket": "example", "identifier": "velocity.nc"},
        "piv_kwargs": {
            "window_size": 60,
            "overlap": 30,
            "search_area_size": 60,
            "sig2noise_method": "peak2peak",
        },
    },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
connection.close()
