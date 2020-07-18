from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Date, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from sqlalchemy import desc

from datetime import datetime, date
from models.data_repository import base

class Intention(base):
    __tablename__ = 'intention'

    intention_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    to_id = Column(Integer)
    payment = Column(Float)
    currency = Column(String)
    create_date = Column(DateTime)
    status = Column(Integer)

    # event_id_int = Column(Integer(), ForeignKey('events.event_id'))
