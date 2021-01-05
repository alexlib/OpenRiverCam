import os
import pika
import json

camera_type = {
    "name": "Foscam E9900P",  # user-chosen name for camera
    "lensParameters": {  # the lens parameters need to be known or calibrated
        "k1": -10.0e-6,
        "c": 2,
        "f": 8.0,
    },
}

gcps = {
    "src": [[992, 366], [1545, 403], (1773, 773), (943, 724)],
    "dst": [
        [192087 + 0.25, 313192 + 6.7],
        [192087 + 4.25, 313192 + 6.8],
        [192087 + 4.5, 313192 + 3.5],
        [192087 + 0.0, 313192 + 3.5],
    ],
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
    "position": (
        192087,
        313192,
    ),  # approximate geographical location of site in crs (x, y) coordinates in metres.
    "crs": 28992,  # int, coordinate ref system as EPSG code
}

bbox = {
    "crs": {"properties": {"code": 28992}, "type": "EPSG"},
    "features": [
        {
            "geometry": {
                "coordinates": [
                    [
                        [192080.892471, 313201.741073],
                        [192096.0625, 313203.78125],
                        [192097.18358, 313195.445295],
                        [192082.013551, 313193.405118],
                        [192080.892471, 313201.741073],
                    ]
                ],
                "type": "Polygon",
            },
            "properties": {"ID": 0},
            "type": "Feature",
        }
    ],
    "type": "FeatureCollection",
}


# bbox = {
#     "crs": {"properties": {"code": 32737}, "type": "EPSG"},
#     "features": [
#         {
#             "geometry": {
#                 "coordinates": [
#                     [
#                         [-6.171107, 9.763121],
#                         [9.018206, 11.710014],
#                         [10.082358, 3.407686],
#                         [-5.106955, 1.460793],
#                         [-6.171107, 9.763121],
#                     ]
#                 ],
#                 "type": "Polygon",
#             },
#             "properties": {"ID": 0},
#             "type": "Feature",
#         }
#     ],
#     "type": "FeatureCollection",
# }

camera_config = {
    "camera_type": camera_type,  # dict, camera object, relational, because a camera configuration belongs to a certain camera.
    "site": site,  # dict, site object, relational because we need to know to whcih site a camera_config belongs. you can have multiple camera configs per site.
    "time_start": "2020-12-16T00:00:00",  # start time of valid range
    "time_end": "2020-12-31T00:00:00",  # end time of valid range, can for instance be used to find the right camera config with a given movie
    "gcps": gcps,  # dict, gcps dictionary, see above
    "corners": corners,  # dict containining corner pixel coordinates, see above
    "resolution": 0.01,  # resolution to be used in reprojection to AOI
    "lensPosition": [
        -3.0 + 192087,
        8.0 + 313192,
        110.0,
    ],  # we could also make this a geojson but it is just one point (x, y, z)
}

camera_config["aoi"] = {"bbox": bbox, "rows": 10, "cols": 30}

movie = {
    "type": "normal",  # str, defines what the movie is used for, either "configuration" or "normal"
    "camera_config": camera_config,  # dict, camera_config object, relational, because a movie belongs to a given camera_config (which in turn belongs to a site).
    "file": {  # file contains the actual filename, and the bucket in which it sits.
        "bucket": "example",
        "identifier": "example_video.mp4",
    },
    "timestamp": "2021-01-01T00:05:30Z",
    "resolution": "1920x1080",
    "fps": 25.0,  # float
    "bathymetry": [0.0, 0.0, 0.0],  # currently not yet used
    "h_a": 3.4,  # float, water level with reference to gauge plate zero level
}

connection = pika.BlockingConnection(
    pika.URLParameters("amqp://admin:password@127.0.0.1:5672")
)
channel = connection.channel()
channel.queue_declare(queue="processing")


body = {
    "type": "compute_piv",
    "kwargs": {
        "movie": movie,
        "file": {
            "bucket": "example",
            "identifier": "velocity.nc"

        },
        "piv_kwargs": {
            "window_size": 60,
            "overlap": 30,
            "search_area_size": 60,
        },
    },
}

channel.basic_publish(exchange="", routing_key="processing", body=json.dumps(body))
connection.close()
