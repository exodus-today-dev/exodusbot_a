from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, DateTime, Date, Float, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from datetime import datetime, date


db_string = "postgres://exodusdb:666777@localhost:5432/exodusdb"

db = create_engine(db_string)  
base = declarative_base()

Session = sessionmaker(db)  
session = Session()

base.metadata.create_all(db)

class Exodus_Users(base):  
    __tablename__ = 'exodus_users'

    exodus_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer,unique=True)
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
    sent = Column(Boolean)
	
class Intention (base):
    __tablename__ = 'intention'
	
    intention_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    to_id = Column(Integer)
    payment = Column(Float)
    currency = Column(String)
    create_date = Column(DateTime)
    status = Column(Integer)
	

	
class Rings_Help(base):
    __tablename__ = 'rings_help'

    rings_id = Column(Integer, primary_key=True)
    needy_id = Column(Integer,unique=True)
    help_array = Column(ARRAY(Integer))
	
Session = sessionmaker(db)  
session = Session()

base.metadata.create_all(db)













# Create 
def create_exodus_user(telegram_id, first_name, last_name, username, ref='', link='', min_payments=0, current_payments=0, max_payments=0,currency='USD', status='', days=0, start_date=date.today()):
    exodus_user = Exodus_Users(	telegram_id = telegram_id, 
								first_name = first_name, 
								last_name = last_name, 
								username = username, 
								ref = ref,
								link = link,
								min_payments = min_payments,
								current_payments = current_payments,
								max_payments = max_payments,
								currency = currency, 
								status = status,
								days = days,
								start_date = start_date,
								create_date = datetime.now())
    session.add(exodus_user)  
    session.commit()

# Read
def read_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first() 
    return exodus_user

# Update
def update_exodus_user(telegram_id, first_name=None, last_name=None, username=None, ref=None, link=None, min_payments=None,current_payments=None,max_payments=None, currency=None, status=None, days=None, start_date=None):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    if first_name is not None:
        exodus_user.first_name = first_name
    if last_name is not None:
        exodus_user.last_name = last_name
    if ref is not None:
        exodus_user.ref = ref
    if link is not None:
        exodus_user.link = link
    if username is not None:
        exodus_user.username = username
    if min_payments is not None:
        exodus_user.min_payments = min_payments
    if current_payments is not None:
        exodus_user.current_payments = current_payments
    if max_payments is not None:
        exodus_user.max_payments = max_payments
    if currency is not None:
        exodus_user.currency = currency
    if status is not None:
        exodus_user.status = status
    if days is not None:
        exodus_user.days = days		
    if start_date is not None:
        exodus_user.start_date = start_date		
		
    session.commit()


# Delete
def delete_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    session.delete(exodus_user)  
    session.commit()  

	
	
	
	
	
def create_event(from_id, first_name, last_name, status, type, min_payments, current_payments, max_payments, currency, users, to_id, sent=False):
    event = Events(	from_id = from_id, 
					first_name = first_name, 
					last_name = last_name, 
					status = status, 
					type = type, 
					min_payments = min_payments, 
					current_payments = current_payments,
					max_payments = max_payments, 
					currency = currency, 
					users = users, 
					to_id = to_id, 
					sent=False)
    session.add(event)  
    session.commit()

def update_event(event_id,sent):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.sent = sent			
    session.commit()

	
	
def read_event(event_id):
    event = session.query(Events).filter_by(event_id=event_id).first()
    return event
	

def create_rings_help(needy_id, help_array):
    ring = Rings_Help(needy_id = needy_id, help_array = help_array)
    session.add(ring)
    session.commit()	
	
def read_rings_help(needy_id):
    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()
    return ring
    	
def update_rings_help(needy_id, help_array):
#    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()      # так почему-то не работатет
#    ring.help_array = help_array
#    session.commit()
    with db.connect() as conn:
        u = text('UPDATE rings_help SET help_array = :q WHERE needy_id = :id')  # так работает
        conn.execute(u, q=help_array, id=needy_id)
	
	
def create_intention(from_id,to_id,payment,currency,status=None):
    intention = Intention(from_id = from_id, to_id = to_id, payment = payment, currency = currency, status=status, create_date=datetime.now())
    session.add(intention)
    session.commit()


def read_intention(from_id=None, to_id=None, status=None):
    if from_id is not None:
        if status is not None:
            intention = session.query(Intention).filter_by(from_id=from_id, status=status)
        else:
            intention = session.query(Intention).filter_by(from_id=from_id)
    if to_id is not None:
        if status is not None:
            intention = session.query(Intention).filter_by(to_id=to_id, status=status)
        else:
            intention = session.query(Intention).filter_by(to_id=to_id)
    return intention
    
def read_intention_by_id(intention_id, from_id=None, status=None):
    if from_id is not None:
        if status is not None:
            intention = session.query(Intention).filter_by(intention_id=intention_id, from_id=from_id, status=status).first()
        else:
            intention = session.query(Intention).filter_by(intention_id=intention_id, from_id=from_id).first()
    else:
        if status is not None:
            intention = session.query(Intention).filter_by(intention_id=intention_id, status=status).first()
        else:
            intention = session.query(Intention).filter_by(intention_id=intention_id).first()
    return intention    
    