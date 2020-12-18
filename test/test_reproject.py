import os
import pika
import json

camera = {
    "name": "Foscam E9900P",  # user-chosen name for camera
    "lensParameters": {  # the lens parameters need to be known or calibrated
        "k1": -10.0e-6,
        "c": 2,
        "f": 8.0,
    }
}

gcps = {
    "src": [(992, 366), (1545, 403), (1773, 773), (943, 724)],
    "dst": [(0.25, 6.7), (4.25, 6.8), (4.5, 3.5), (0.0, 3.5)],
    "z_0": 100.0,  # reference height of zero water level compared to the crs used (z is crs related, h is staff gauge related)
    "h_ref": 2.0,  # actual water level during taking of the gcp points, as measured on the staff gauge
}

corners = {
    "up_left": (200, 100),
    "down_left": (1850, 150),
    "down_right": (1890, 900),
    "up_right": (50, 970),
}

site = {
    "name": "Hommerich",  # str, name of user
    "uuid": "<uuid string>",  # some uuid for relational database purposes
    "position": (192087, 313192),  # approximate geographical location of site in crs (x, y) coordinates in metres.
    "crs": 28992,  # int, coordinate ref system as EPSG code
}

bbox = {
    "crs": {
        "properties": {
            "code": 32737
        }, "type": "EPSG"
    }, "features": [{"geometry": {"coordinates": [[[-6.171107, 9.763121], [9.018206, 11.710014], [10.082358, 3.407686], [-5.106955, 1.460793], [-6.171107, 9.763121]]], "type": "Polygon"}, "properties": {"ID": 0}, "type": "Feature"}], "type": "FeatureCollection"
}

camera_config = {
    "camera": camera,  # dict, camera object, relational, because a camera configuration belongs to a certain camera.
    "site": site,  # dict, site object, relational because we need to know to whcih site a camera_config belongs. you can have multiple camera configs per site.
    "time_start": "2020-12-16T00:00:00",  # start time of valid range
    "time_end": "2020-12-31T00:00:00",  # end time of valid range, can for instance be used to find the right camera config with a given movie
    "gcps": gcps,    # dict, gcps dictionary, see above
    # "corners": corners,  # dict containining corner pixel coordinates, see above
    "aoi": {
        "bbox": bbox,  # dict in geojson format, with crs projection, order of corner points is up-left, down-left, down-right, up-right, -up-left
        "rows": 10,  # int, amount of rows (from left bank to right bank) for interrogation window
        "cols": 30,  # int, amount of cols (from upstream to downstream) for interrogation window
    },
    "resolution": 0.01,  # resolution to be used in reprojection to AOI
    "lensPosition": [-3.0, 8.0, 110.0],  # we could also make this a geojson but it is just one point (x, y, z)
}

body = {
    "type": "get_aoi",
    "kwargs": {
        "camera_config": camera_config,
    }
}
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()

channel.queue_declare(queue="processing")
channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
print(" [x] Sent 'get_aoi'")
connection.close()

