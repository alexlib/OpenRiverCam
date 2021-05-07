from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class Site(Base, SerializerMixin):
    __tablename__ = "site"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    position_crs = Column(Integer, nullable=False)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

    def get_task_json(self):
        """
        Get dict with main properties of the site for the JSON content towards the processing node.

        :return: dict
        """
        return {
            "id": self.id,
            "name": self.name,
            "position": [self.position_x, self.position_y],
            "crs": self.position_crs
        }
