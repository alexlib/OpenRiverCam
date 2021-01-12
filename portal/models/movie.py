from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
import enum
from models.base import Base

class MovieType(enum.Enum):
    MOVIE_TYPE_NORMAL = 0
    MOVIE_TYPE_CONFIG = 1

class MovieStatus(enum.Enum):
    MOVIE_STATUS_NEW = 0
    MOVIE_STATUS_EXTRACTED = 1
    MOVIE_STATUS_READY = 2
    MOVIE_STATUS_PROCESSED = 3

class Movie(Base, SerializerMixin):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('configuration.id'))
    file_bucket = Column(String)
    file_name = Column(String)
    timestamp = Column(DateTime)
    type = Column(Enum(MovieType))
    resolution = Column(String)
    fps = Column(Float)
    actual_water_level = Column(Float)
    bathymetry_id = Column(Integer, ForeignKey('bathymetry.id'))
    status = Column(Enum(MovieStatus))

    def __str__(self):
        return "{}/{}".format(self.file_bucket, self.file_name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())