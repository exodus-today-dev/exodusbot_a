from sqlalchemy import Column, Integer, ARRAY

from models.data_repository import base


class Rings_Help(base):
    __tablename__ = 'rings_help'

    rings_id = Column(Integer, primary_key=True)
    needy_id = Column(Integer, unique=True)
    help_array = Column(ARRAY(Integer))
