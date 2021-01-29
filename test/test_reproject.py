import os
import pika
import json
from example_data import camera_config, movie

body = {
    "type": "get_aoi",
    "kwargs": {
        "camera_config": camera_config,
    },
}
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()
channel.queue_declare(queue="processing")
channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
print(" [x] Sent 'get_aoi'")

body = {
    "type": "extract_project_frames",
    "kwargs": {
        "movie": movie,
    },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))

connection.close()
