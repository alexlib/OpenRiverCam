from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class Bathymetry(Base, SerializerMixin):
    __tablename__ = "bathymetry"
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("site.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)

    coordinates = relationship("BathymetryCoordinate")
    site = relationship("Site")

    def __str__(self):
        return "{}".format(self.id)

    def __repr__(self):
        return "{}".format(self.__str__())

    def get_task_json(self):
        return {
            "coords": list(map(lambda c: [c.x, c.y, c.z], self.coordinates))
        }

class BathymetryCoordinate(Base, SerializerMixin):
    __tablename__ = "bathymetrycoordinate"
    id = Column(Integer, primary_key=True)
    bathymetry_id = Column(Integer, ForeignKey("bathymetry.id"), nullable=False)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
