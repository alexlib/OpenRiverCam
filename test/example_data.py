import numpy as np

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
    "aoi": {"bbox": bbox, "rows": 10, "cols": 30}
}

# define cross section
x = np.flipud(
    [
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
)
y = np.flipud(
    [
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
)
z = np.flipud(
    [
        101.88,
        101.67,
        101.3,
        101.0,
        100.49,
        100.34,
        100.0,
        100.2,
        100.6,
        100.9,
        101.05,
        101.0,
        101.1,
        101.3,
        101.5,
        102.4,
        102.5,
    ]
)
coords = list(zip(x, y, z))

# make coords entirely jsonifiable by getting rid of tuple construct
coords = [list(c) for c in coords]

bathymetry = {
    "crs": 28992,  # int, epsg code in [m], only projected coordinate systems are supported
    "coords": coords,  # list of (x, y, z) tuples defined in crs [m], coords are not valid in the example
}

movie = {
    "id": 1,
    "type": "normal",  # str, defines what the movie is used for, either "configuration" or "normal"
    "camera_config": camera_config,  # dict, camera_config object, relational, because a movie belongs to a given camera_config (which in turn belongs to a site).
    "file": {  # file contains the actual filename, and the bucket in which it sits.
        "bucket": "example",
        "identifier": "example_video.mp4",
    },
    "timestamp": "2021-01-01T00:05:30Z",
    "resolution": "1920x1080",
    "fps": 25.0,  # float
    "bathymetry": bathymetry,  # currently not yet used
    "h_a": 3.4,  # float, water level with reference to gauge plate zero level
}