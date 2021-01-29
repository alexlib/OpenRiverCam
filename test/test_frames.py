import os
import pika
import json

body = {
    "type": "extract_frames",
    "kwargs": {
        "movie": {"file": {"bucket": "example", "identifier": "example_video.mp4"}, "id": 1 },
        "camera": {
            "name": "Foscam E9900P",
            "configuration": {},
            "lensParameters": {
                "k1": -10.0e-6,
                "c": 2,
                "f": 8.0,
            },
        },
    },
}


connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()

channel.queue_declare(queue="processing")
channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
print(" [x] Sent 'frames'")
connection.close()
