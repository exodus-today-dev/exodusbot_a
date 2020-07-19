from sqlalchemy import Column, String, Integer, DateTime, Date, Float

from models.data_repository import base


class Exodus_Users(base):
    __tablename__ = 'exodus_users'

    exodus_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)
    ref = Column(String)
    link = Column(String)
    currency = Column(String)
    status = Column(String)
    min_payments = Column(Float)
    current_payments = Column(Float)
    max_payments = Column(Float)
    create_date = Column(DateTime)
    days = Column(Integer)
    start_date = Column(Date)
