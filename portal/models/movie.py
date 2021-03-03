import os
import pika
import json
import enum
from sqlalchemy import event, Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from models.base import Base
from models.example_data import movie as movie_example


class MovieType(enum.Enum):
    MOVIE_TYPE_NORMAL = 0
    MOVIE_TYPE_CONFIG = 1


class MovieStatus(enum.Enum):
    MOVIE_STATUS_NEW = 0
    MOVIE_STATUS_EXTRACTED = 1
    MOVIE_STATUS_READY = 2
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


@event.listens_for(Movie, 'after_insert')
@event.listens_for(Movie, 'after_update')
def receive_after_update(mapper, connection, target):
    if target.status == MovieStatus.MOVIE_STATUS_NEW:
        print('Queue extract task for movie {}'.format(target.id))
        queue_task("extract_frames", target)
    elif target.status == MovieStatus.MOVIE_STATUS_READY and target.actual_water_level is not None:
        print('Queue run task for movie {}'.format(target.id))
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
        body=json.dumps({"type": type, "kwargs": {"movie": get_task_json(movie)}})
    )
    connection.close()

def get_task_json(movie):
    movie_example['id'] = movie.id
    if movie.actual_water_level is not None:
        # Decimal can't be JSON encoded with default encoder.
        movie_example['h_a'] = float(movie.actual_water_level)
    return movie_example