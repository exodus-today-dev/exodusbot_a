from datetime import datetime, date

from sqlalchemy import text, desc, or_

from models.events import Events
from models.exodus_user import Exodus_Users
from models.intention import Intention
from models.requisites import Requisites
from models.rings_help import Rings_Help

from models.data_repository import session
from models.data_repository import db
from models.status_codes import *


# Create
def create_exodus_user(telegram_id, first_name, last_name, username, ref='', link='', min_payments=0,
                       current_payments=0, max_payments=0, currency='USD', status='', days=0, start_date=date.today()):
    exodus_user = Exodus_Users(telegram_id=telegram_id,
                               first_name=first_name,
                               last_name=last_name,
                               username=username,
                               ref=ref,
                               link=link,
                               min_payments=min_payments,
                               current_payments=current_payments,
                               max_payments=max_payments,
                               currency=currency,
                               status=status,
                               days=days,
                               start_date=start_date,
                               create_date=datetime.now())

    try:
        session.add(exodus_user)
        session.commit()
    except:
        session.rollback()
        raise


# Read
def read_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    return exodus_user


# Update
def update_exodus_user(telegram_id, first_name=None, last_name=None, username=None, ref=None, link=None,
                       min_payments=None, current_payments=None, max_payments=None, currency=None, status=None,
                       days=None, start_date=None):
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

    try:
        session.commit()
    except:
        session.rollback()
        raise


# Delete
def delete_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    try:
        session.delete(exodus_user)
        session.commit()
    except:
        session.rollback()
        raise


def create_event(from_id, first_name, last_name, status, type, min_payments, current_payments,
                 max_payments, currency, users, to_id, reminder_date, sent=False, status_code=None):
    event = Events(from_id=from_id,
                   first_name=first_name,
                   last_name=last_name,
                   status=status,
                   type=type,
                   min_payments=min_payments,
                   current_payments=current_payments,
                   max_payments=max_payments,
                   currency=currency,
                   users=users,
                   to_id=to_id,
                   reminder_date=reminder_date,
                   # intention_id = intention_id,
                   sent=False,
                   status_code=status_code)

    try:
        session.add(event)
        session.commit()
    except:
        session.rollback()
        raise


def update_event(event_id, sent):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.sent = sent

    try:
        session.commit()
    except:
        session.rollback()
        raise


def update_event_reminder_date(event_id, reminder_date):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.reminder_date = reminder_date
    try:
        session.commit()
    except:
        session.rollback()
        raise


def update_event_type(event_id, type):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.type = type
    try:
        session.commit()
    except:
        session.rollback()
        raise


def read_event(event_id):
    event = session.query(Events).filter_by(event_id=event_id).first()
    return event


def create_rings_help(needy_id, help_array):
    ring = Rings_Help(needy_id=needy_id, help_array=help_array)
    try:
        session.add(ring)

        session.commit()
    except:
        session.rollback()
        raise


def read_rings_help(needy_id):
    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()
    return ring


def read_rings_help_in_help_array(telegram_id):
    list_send_notify = session.query(Rings_Help).filter(Rings_Help.help_array.any(telegram_id)).all()
    return list_send_notify


def update_rings_help(needy_id, help_array):
    #    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()      # так почему-то не работатет
    #    ring.help_array = help_array
    #    session.commit()
    with db.connect() as conn:
        u = text('UPDATE rings_help SET help_array = :q WHERE needy_id = :id')  # так работает
        conn.execute(u, q=help_array, id=needy_id)


def create_intention(from_id, to_id, payment, currency, status=None):
    intention = Intention(from_id=from_id, to_id=to_id, payment=payment, currency=currency, status=status,
                          create_date=datetime.now())

    try:
        session.add(intention)
        session.commit()
    except:
        session.rollback()
        raise


def read_intention_with_payment(from_id, to_id, payment, status):
    intention = session.query(Intention).filter_by(from_id=from_id, to_id=to_id, payment=payment, status=status).first()
    return intention


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


def read_intention_one(from_id, to_id, status):
    intention = session.query(Intention).filter_by(from_id=from_id, to_id=to_id, status=status).first()
    return intention


def read_intention_by_id(intention_id):
    intention = session.query(Intention).filter_by(intention_id=intention_id).first()
    return intention


def update_intention(intention_id, status=None, payment=None):
    intention = session.query(Intention).filter_by(intention_id=intention_id).first()
    if status is not None:
        intention.status = status
    if payment is not None:
        intention.payment = payment
    try:
        session.commit()
    except:
        session.rollback()
        raise


def update_intention_from_all_params(from_id, to_id, payment, status=None):
    intention = session.query(Intention).filter_by(from_id=from_id, to_id=to_id, payment=payment).first()
    if status is not None:
        intention.status = status
    try:
        session.commit()
    except:
        session.rollback()
        raise


# -----------------------requisites-------------------
# Create
def create_requisites_user(telegram_id, name='', value='', is_default=False):
    requisites = Requisites(telegram_id=telegram_id,
                            name=name,
                            value=value,
                            is_default=is_default)

    try:
        session.add(requisites)

        session.commit()
    except:
        session.rollback()
        raise


# Read
def read_requisites_user(telegram_id):
    requisites_user = session.query(Requisites).filter_by(telegram_id=telegram_id).order_by(
        desc(Requisites.is_default)).all()
    return requisites_user


def read_requisites_name(telegram_id, requisites_name):
    search = f"%{requisites_name}%"
    requisites_user = session.query(Requisites).filter(Requisites.name.like(search)).filter_by(
        telegram_id=telegram_id).first()
    return requisites_user


def get_help_requisites(telegram_id):
    help_requisites = session.query(Events).filter(
        or_(Events.status_code == NEW_ORANGE_STATUS, Events.status_code == NEW_RED_STATUS),
        Events.to_id == telegram_id)

    ret = []
    for row in help_requisites:
        ret.append(row.from_id)

    return ret


def get_requisites_count(telegram_id):
    count = session.query(Events).filter_by(to_id=telegram_id).count()
    return count


# Update
def update_requisites_user(requisites_id, name='', value='', is_default=False):
    requisites_user = session.query(Requisites).filter_by(requisites_id=requisites_id).first()
    requisites_user.name = name
    requisites_user.value = value
    requisites_user.is_default = is_default

    try:
        session.commit()
    except:
        session.rollback()
        raise


# Delete
def delete_requisites_user(requisites_id):
    requisites_user = session.query(Requisites).filter_by(requisites_id=requisites_id).first()

    try:
        session.delete(requisites_user)
        session.commit()
    except:
        session.rollback()
        raise
