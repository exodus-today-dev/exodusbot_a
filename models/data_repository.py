from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, String, Integer, DateTime, Date, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text
from sqlalchemy import desc

from datetime import datetime, date


import config

db = create_engine(config.DATABASE_URL)
base = declarative_base()
base.metadata.create_all(db)
Session = sessionmaker(db)
session = Session()
