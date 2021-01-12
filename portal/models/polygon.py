from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, Float, Text
from sqlalchemy_serializer import SerializerMixin
from models.base import Base

class Polygon(Base, SerializerMixin):
    __tablename__ = 'polygon'
    id = Column(Integer, primary_key=True)
    ul_x = Column(Float)
    ul_y = Column(Float)
    dl_x = Column(Float)
    dl_y = Column(Float)
    dr_x = Column(Float)
    dr_y = Column(Float)
    ur_x = Column(Float)
    ur_y = Column(Float)