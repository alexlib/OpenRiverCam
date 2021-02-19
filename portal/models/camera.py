from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
import enum
from models.base import Base


class CameraStatus(enum.Enum):
    CAMERA_STATUS_INACTIVE = 0
    CAMERA_STATUS_ACTIVE = 1


class Camera(Base, SerializerMixin):
    __tablename__ = "camera"
    id = Column(Integer, primary_key=True)
    camera_type_id = Column(Integer, ForeignKey("cameratype.id"))
    site_id = Column(Integer, ForeignKey("site.id"))
    status = Column(Enum(CameraStatus))

    site = relationship("Site")
    camera_type = relationship("CameraType")

    def __str__(self):
        return "{}({}) at {}".format(self.camera_type.name, self.id, self.site.name)

    def __repr__(self):
        return "{}".format(self.__str__())


class CameraConfig(Base, SerializerMixin):
    __tablename__ = "configuration"
    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("camera.id"))
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    movie_setting_resolution = Column(String)
    movie_setting_fps = Column(Float)
    gcps_src = Column(Integer, ForeignKey("polygon.id"))
    gcps_dst = Column(Integer, ForeignKey("polygon.id"))
    gcps_z_0 = Column(Float)
    gcps_h_ref = Column(Float)
    corners = Column(Integer, ForeignKey("polygon.id"))
    aoi_bbox = Column(Text)
    aoi_rows = Column(Integer)
    aoi_cols = Column(Integer)
    aoi_resolution = Column(Float)
    lens_position_crs = Column(Integer)
    lens_position_x = Column(Float)
    lens_position_y = Column(Float)
    lens_position_z = Column(Float)

    camera = relationship("Camera")

    def __str__(self):
        return "{} - configuration {}".format(self.camera.__str__(), self.id)

    def __repr__(self):
        return "{}".format(self.__str__())


class CameraType(Base, SerializerMixin):
    __tablename__ = "cameratype"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    lens_k1 = Column(Float)
    lens_c = Column(Float)
    lens_f = Column(Float)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
