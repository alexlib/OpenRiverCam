from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class MovieType(enum.Enum):
    MOVIE_TYPE_CONFIG = 1
    MOVIE_TYPE_NORMAL = 2

class Movie(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    config_id = Column(Integer, ForeignKey('configuration.id'))
    file_bucket = Column(String)
    file_name = Column(String)
    timestamp = Column(DateTime)
    type = Column(Enum(MovieType))

    def __str__(self):
        return "{}/{}".format(self.file_bucket, self.file_name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

class CameraConfig(Base):
    __tablename__ = 'configuration'
    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey('camera.id'))
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    movie_setting_resolution = Column(String)
    movie_setting_fps = Column(Float)
    gcps_src = Column(Integer, ForeignKey('polygon.id'))
    gcps_dst = Column(Integer, ForeignKey('polygon.id'))
    gcps_z_0 = Column(Float)
    gcps_h_ref = Column(Float)
    corners = Column(Integer, ForeignKey('polygon.id'))
    aoi_bbox = Column(Text)

    def __str__(self):
        return "{}".format(self.id)

    def __repr__(self):
        return "{}".format(self.__str__())