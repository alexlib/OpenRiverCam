import pika
import json

# define cross section
x = [
    192087.75935984775424,
    192087.637668401439441,
    192087.515976955008227,
    192087.345608930045273,
    192087.223917483701371,
    192087.077887748018838,
    192086.980534590955358,
    192086.85884314449504,
    192086.761489987518871,
    192086.566783673217287,
    192086.469430516182911,
    192086.323400780500378,
    192086.177371044788742,
    192086.080017887725262,
    192085.885311573481886,
    192085.690605259296717,
    192085.641928680706769,
]
y = [
    313193.458014087867923,
    313194.09080960357096,
    313194.820958279015031,
    313195.478092092089355,
    313196.183902480057441,
    313196.962727739592083,
    313197.741552993596997,
    313198.374348516052123,
    313199.055820613284595,
    313199.785969295422547,
    313200.491779681993648,
    313201.197590066993143,
    313201.95207703957567,
    313202.730902298353612,
    313203.363697814638726,
    313204.166861362638883,
    313204.970024902664591,
]
z = [
    1.88,
    1.67,
    1.3,
    1.0,
    0.49,
    0.34,
    0.0,
    0.2,
    0.6,
    0.9,
    1.05,
    1.0,
    1.1,
    1.3,
    1.5,
    2.4,
    2.5,
]
coords = list(zip(x, y, z))

# make coords entirely jsonifiable by getting rid of tuple construct
coords = [list(c) for c in coords]

bathymetry = {
    "site": "Hommerich",  # dict, site, relational, because a bathymetry profile belongs to a site.
    "crs": 28992,  # int, epsg code in [m], only projected coordinate systems are supported
    "coords": coords,  # list of (x, y, z) tuples defined in crs [m], coords are not valid in the example
}

velocity = {
    "file": {
        "bucket": "example",
        "identifier": "velocity.nc"
    }
}

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
        },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
connection.close()
