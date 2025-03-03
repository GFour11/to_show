from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, DateTime, String, ARRAY, Integer, Boolean


Base = declarative_base()


class LondonApartment(Base):

    __tablename__ = "London"

    id = Column(Integer, primary_key=True, index=True)
    name_of_listing = Column(String, nullable=False)
    bedrooms = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    images = Column(ARRAY(String))
    price = Column(String)
    time = Column(DateTime)
    link = Column(String, unique=True)

    def to_dict(self):
        return self.__dict__


class NetherlandApartment(Base):

    __tablename__ = "Netherland"

    id = Column(Integer, primary_key=True, index=True)
    name_of_listing = Column(String, nullable=False)
    bedrooms = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    images = Column(ARRAY(String))
    price = Column(String)
    time = Column(DateTime)
    link = Column(String, unique=True)

    def to_dict(self):
        return self.__dict__


class Proxies(Base):

    __tablename__ = "Proxies"

    id = Column(Integer, primary_key=True, index=True)
    proxy = Column(String)
    is_active = Column(Boolean, default=True)
