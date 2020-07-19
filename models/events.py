from sqlalchemy import Column, String, Integer, Date, Float, Boolean

from models.data_repository import base


# добавил внешнюю связь для двух таблиц events и intention, в надежде, что это поможет при обновлении статуса с 12 на 13
class Events(base):
    __tablename__ = 'events'

    event_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    status = Column(String)
    type = Column(String)
    min_payments = Column(Float)
    current_payments = Column(Float)
    max_payments = Column(Float)
    currency = Column(String)
    users = Column(Integer)
    to_id = Column(Integer)
    reminder_date = Column(Date)
    # intention_id = Column(Integer(), ForeignKey('intention.intention_id'))
    sent = Column(Boolean)
    status_code = Column(Integer)
    # child = relationship("Intention", uselist=False, backref='events')
