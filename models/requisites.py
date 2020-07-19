from sqlalchemy import Column, String, Integer, Boolean

from models.data_repository import base


class Requisites(base):
    __tablename__ = 'requisites'

    requisites_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    name = Column(String(128), nullable=False)
    value = Column(String(128), nullable=False)
    is_default = Column(Boolean)
