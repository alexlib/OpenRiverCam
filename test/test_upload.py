import os
import pika
import json

body = {
    "type": "upload_file",
    "kwargs": {
        "fn": "/home/hcwinsemius/OpenRiverCam/example_video.mp4",
        "bucket": "example",
    },
}

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()

channel.queue_declare(queue="processing")
channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
print(" [x] Sent 'Upload!'")
connection.close()
