from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Date, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from sqlalchemy import desc

from datetime import datetime, date

from models.data_repository import base


class Requisites(base):
    __tablename__ = 'requisites'

    requisites_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    name = Column(String(128), nullable=False)
    value = Column(String(128), nullable=False)
    is_default = Column(Boolean)
