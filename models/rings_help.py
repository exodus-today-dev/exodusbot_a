from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Date, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from sqlalchemy import desc

from datetime import datetime, date
from models.data_repository import base


class Rings_Help(base):
    __tablename__ = 'rings_help'

    rings_id = Column(Integer, primary_key=True)
    needy_id = Column(Integer, unique=True)
    help_array = Column(ARRAY(Integer))
