from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class Site(Base, SerializerMixin):
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    position_crs = Column(Integer)
    position_x = Column(Float)
    position_y = Column(Float)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    def get_task_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "position": [self.position_x, self.position_y],
            "crs": self.position_crs
        }
