import pika
import json
from example_data import bathymetry

velocity = {"file": {"bucket": "example", "identifier": "velocity.nc"}}

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()
channel.queue_declare(queue="processing")

body = {
    "type": "compute_q",
    "kwargs": {
        "velocity": velocity,
        "bathymetry": bathymetry,
        "z_0": 100.0,
        "h_a": 0.9,
        "quantile": [0.1, 0.5, 0.9],
    },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
connection.close()
