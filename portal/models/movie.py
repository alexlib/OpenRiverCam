import os
import pika
import json
import enum
from sqlalchemy import (
    event,
    Integer,
    ForeignKey,
    String,
    Column,
    DateTime,
    Enum,
    Float,
    Text,
)
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from models.bathymetry import Bathymetry


class MovieType(enum.Enum):
    MOVIE_TYPE_NORMAL = 0
    MOVIE_TYPE_CONFIG = 1


class MovieStatus(enum.Enum):
    MOVIE_STATUS_NEW = 0
    MOVIE_STATUS_EXTRACTED = 1
    MOVIE_STATUS_PROCESSING = 2
    MOVIE_STATUS_FINISHED = 3
    MOVIE_STATUS_ERROR = 4


class Movie(Base, SerializerMixin):
    __tablename__ = "movie"
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey("configuration.id"))
    file_bucket = Column(String)
    file_name = Column(String)
    timestamp = Column(DateTime)
    type = Column(Enum(MovieType), default=MovieType.MOVIE_TYPE_NORMAL)
    actual_water_level = Column(Float)
    bathymetry_id = Column(Integer, ForeignKey("bathymetry.id"))
    status = Column(Enum(MovieStatus), default=MovieStatus.MOVIE_STATUS_NEW)
    error_message = Column(Text)
    discharge_q05 = Column(Float)
    discharge_q25 = Column(Float)
    discharge_q50 = Column(Float)
    discharge_q75 = Column(Float)
    discharge_q95 = Column(Float)

    config = relationship("CameraConfig")
    bathymetry = relationship("Bathymetry")

    def __str__(self):
        return "{}/{}".format(self.file_bucket, self.file_name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    def get_task_json(self):
        # Camera config relation might not have been loaded yet during the after_update event.
        if not self.config and self.config_id:
            movie = Movie.query.get(self.id)
            self.config = movie.config

        return {
            "id": self.id,
            "camera_config": self.config.get_task_json() if self.config else None,
            "file": {
                "bucket": self.file_bucket,
                "identifier": self.file_name
            },
            "timestamp": '{}Z'.format(str(self.timestamp.isoformat())),
            "bathymetry": self.bathymetry.get_task_json() if self.bathymetry else None,
            "h_a": float(self.actual_water_level) if self.actual_water_level else None
        }

@event.listens_for(Movie, "before_insert")
@event.listens_for(Movie, "before_update")
def receive_before_insert(mapper, connection, target):
    # Select most recent bathymetry for target site.
    if not target.bathymetry_id:
        bathymetry = Bathymetry.query.filter(Bathymetry.site_id == target.config.camera.site_id).order_by(Bathymetry.id.desc()).first()
        if bathymetry:
            target.bathymetry_id = bathymetry.id
        else:
            raise Exception('Could not find bathymetry for site')
    if (
        target.status == MovieStatus.MOVIE_STATUS_EXTRACTED
        and target.actual_water_level is not None
    ):
        target.status = MovieStatus.MOVIE_STATUS_PROCESSING


@event.listens_for(Movie, "after_insert")
@event.listens_for(Movie, "after_update")
def receive_after_update(mapper, connection, target):
    if target.status == MovieStatus.MOVIE_STATUS_NEW:
        queue_task("extract_frames", target)
    elif (
        target.status == MovieStatus.MOVIE_STATUS_PROCESSING
        and target.actual_water_level is not None
    ):
        queue_task("run", target)


def queue_task(type, movie):
    connection = pika.BlockingConnection(
        pika.URLParameters(os.getenv("AMQP_CONNECTION_STRING"))
    )
    channel = connection.channel()
    channel.queue_declare(queue="processing")
    channel.basic_publish(
        exchange="",
        routing_key="processing",
        body=json.dumps({"type": type, "kwargs": {"movie": movie.get_task_json() }}),
    )
    connection.close()
