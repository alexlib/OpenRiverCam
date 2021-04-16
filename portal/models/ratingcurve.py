from sqlalchemy import Integer, ForeignKey, String, Column, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class RatingCurve(Base, SerializerMixin):
    __tablename__ = "ratingcurve"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    site_id = Column(Integer, ForeignKey("site.id"))
    ratingpoints = relationship("RatingPoint")
    # rating curve defined as Q = a(h-h0)**b
    a = Column(Float)
    b = Column(Float)
    h0 = Column(Float)
    site = relationship("Site", foreign_keys=[site_id])

    def __str__(self):
        return "{}".format(self.id)

    def __repr__(self):
        return "{}".format(self.__str__())


class RatingPoint(Base, SerializerMixin):
    __tablename__ = "ratingpoint"
    id = Column(Integer, primary_key=True)
    ratingcurve_id = Column(Integer, ForeignKey("ratingcurve.id"))
    movie_id = Column(Integer, ForeignKey("movie.id"))
    include = Column(Boolean, default=True)
    movie = relationship("Movie", foreign_keys=[movie_id])