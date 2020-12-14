from datetime import date, datetime
from operator import or_

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, DateTime, ARRAY, text, desc, \
    ForeignKey, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import config
from status_codes import *

db = create_engine(config.DATABASE_URL)
base = declarative_base()

Session = sessionmaker(db)
session = Session()
base.metadata.create_all(db)


# region Модели бд ORM

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
    status_code = Column(String)
    # child = relationship("Intention", uselist=False, backref='events')
    intention = relationship("Intention", uselist=False, backref='events')


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


class Intention(base):
    __tablename__ = 'intention'

    intention_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    to_id = Column(Integer)
    payment = Column(Float)
    currency = Column(String)
    create_date = Column(DateTime)
    status = Column(Integer)
    event_id = Column(Integer, ForeignKey('events.event_id'))
    event = relationship('Events', back_populates="intention")
    # event_id_int = Column(Integer(), ForeignKey('events.event_id'))


class HistoryIntention(base):
    __tablename__ = 'history_intention'

    intention_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    to_id = Column(Integer)
    payment = Column(Float)
    currency = Column(String)
    create_date = Column(DateTime)
    from_intention = Column(Integer)


class Requisites(base):
    __tablename__ = 'requisites'

    requisites_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    name = Column(String(128), nullable=False)
    value = Column(String(128), nullable=False)
    is_default = Column(Boolean)


class Rings_Help(base):
    __tablename__ = 'rings_help'

    rings_id = Column(Integer, primary_key=True)
    needy_id = Column(Integer, unique=True)
    help_array_orange = Column(ARRAY(Integer))
    help_array_red = Column(ARRAY(Integer))
    help_array_all = Column(ARRAY(Integer))


class Temp_Intention(base):
    __tablename__ = 'temp_intention'

    id = Column(Integer, primary_key=True)
    to_id = Column(Integer)
    status = Column(Integer)
    intention_array = Column(ARRAY(Integer))


class User_Language(base):
    __tablename__ = 'user_language'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    language = Column(String(128))


# endregion

Session = sessionmaker(db)
session = Session()
base.metadata.create_all(db)


def quit_user_from_exodus(telegram_id):
    delete_exodus_user(telegram_id)
    delete_event_for_quit(telegram_id)
    delete_intention_for_quit(telegram_id)
    delete_requisites_for_quit(telegram_id)
    delete_rings_help_for_quit(telegram_id)
    delete_temp_intention(telegram_id)
    delete_user_language(telegram_id)


# region user_language

def create_user_language(user_id, language):
    temp = User_Language(user_id=user_id, language=language)
    session.add(temp)
    session.commit()


def read_user_language(user_id):
    user = session.query(User_Language).filter_by(user_id=user_id).first()
    if user:
        return session.query(User_Language).filter_by(user_id=user_id).first().language
    else:
        create_user_language(user_id, "en")
        return session.query(User_Language).filter_by(user_id=user_id).first().language


def update_user_language(user_id, language):
    user = session.query(User_Language).filter_by(user_id=user_id).first()
    user.language = language
    session.commit()


def delete_user_language(user_id):
    user_lang = session.query(User_Language).filter_by(user_id=user_id).first()
    if user_lang != None:
        session.delete(user_lang)
        session.commit()

# endregion


# region temp_intention

def create_temp_intention(to_id, status, intention_array):
    temp = Temp_Intention(to_id=to_id, status=status, intention_array=intention_array)
    session.add(temp)
    session.commit()


def delete_temp_intention(to_id):
    try:
        temp_intention = session.query(Temp_Intention).filter_by(to_id=to_id).all()
        for intention in temp_intention:
            session.delete(intention)
        session.commit()
    except:
        session.rollback()


def read_all_temp_intention(to_id):
    return session.query(Temp_Intention).filter_by(to_id=to_id).all()


# endregion

# region exodus_user
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

    # try:
    #     session.add(exodus_user)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise

    session.add(exodus_user)
    session.commit()


# Read
def read_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    return exodus_user


def read_all_exodus_user():
    user_ids = [user.telegram_id for user in session.query(Exodus_Users.telegram_id).distinct()]
    return user_ids


def read_exodus_user_by_exodus_id(exodus_id):
    exodus_user = session.query(Exodus_Users).filter_by(exodus_id=exodus_id).first()
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

    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise

    session.commit()


# Delete
def delete_exodus_user(telegram_id):
    exodus_user = session.query(Exodus_Users).filter_by(telegram_id=telegram_id).first()
    if exodus_user != None:
        session.delete(exodus_user)
        session.commit()


# endregion

# region events

def create_event(from_id, first_name, last_name, status, type, min_payments, current_payments,
                 max_payments, currency, users, to_id, reminder_date, sent=False, status_code=None, intention=None):
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
                   sent=sent,
                   status_code=status_code,
                   intention=intention)

    # try:
    #     session.add(event)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.add(event)
    session.commit()


def update_event(event_id, sent):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.sent = sent

    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


def update_event_reminder_date(event_id, reminder_date):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.reminder_date = reminder_date
    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise

    session.commit()


def update_event_type(event_id, type):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.type = type
    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


def update_event_status_code(event_id, status_code):
    event = session.query(Events).filter_by(event_id=event_id).first()
    event.status_code = status_code

    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


def read_event(event_id):
    event = session.query(Events).filter_by(event_id=event_id).first()
    return event


def read_event_to_id_status(to_id, type):
    events = session.query(Events).filter(Events.to_id == to_id, Events.type == type).all()
    return events


def read_event_from_id_status(from_id, type):
    events = session.query(Events).filter(Events.from_id == from_id, Events.type == type).all()
    return events


def delete_event_new_status(to_id):
    session.query(Events).filter(Events.to_id == to_id,
                                 or_(Events.status_code == NEW_ORANGE_STATUS,
                                     Events.status_code == NEW_RED_STATUS)).delete()
    session.commit()


def delete_event_future():
    session.query(Events).filter(Events.status_code == FUTURE_EVENT).delete()
    session.commit()


def delete_event_for_quit(telegram_id):
    event_to_id = session.query(Events).filter_by(to_id=telegram_id).all()
    if event_to_id != []:
        for event in event_to_id:
            session.delete(event)
        session.commit()

    event_from_id = session.query(Events).filter_by(from_id=telegram_id).all()
    if event_to_id != []:
        for event in event_from_id:
            session.delete(event)
        session.commit()


# endregion

# region rings_help

def create_rings_help(needy_id, help_array_orange=[], help_array_red=[], help_array_all=[]):
    ring = Rings_Help(needy_id=needy_id, help_array_orange=help_array_orange, help_array_red=help_array_red,
                      help_array_all=help_array_all)
    # try:
    #     session.add(ring)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.add(ring)
    session.commit()


def read_rings_help(needy_id):
    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()
    return ring


def read_rings_help_in_help_array_all(telegram_id):
    list_send_notify = session.query(Rings_Help).filter(Rings_Help.help_array_all.any(telegram_id)).all()
    return list_send_notify


def update_orange_rings_help(needy_id, help_array_orange):
    #    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()      # так почему-то не работатет
    #    ring.help_array = help_array
    #    session.commit()
    with db.connect() as conn:
        u = text('UPDATE rings_help SET help_array_orange = :q WHERE needy_id = :id')  # так работает
        conn.execute(u, q=help_array_orange, id=needy_id)


def update_rings_help_array_red(needy_id, help_array_red):
    #    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()      # так почему-то не работатет
    #    ring.help_array = help_array
    #    session.commit()
    with db.connect() as conn:
        u = text('UPDATE rings_help SET help_array_red = :q WHERE needy_id = :id')  # так работает
        conn.execute(u, q=help_array_red, id=needy_id)


def update_rings_help_array_all(needy_id, help_array_all):
    #    ring = session.query(Rings_Help).filter_by(needy_id=needy_id).first()      # так почему-то не работатет
    #    ring.help_array = help_array
    #    session.commit()
    with db.connect() as conn:
        u = text('UPDATE rings_help SET help_array_all = :q WHERE needy_id = :id')  # так работает
        conn.execute(u, q=help_array_all, id=needy_id)


def delete_rings_help_for_quit(telegram_id):
    array = read_rings_help_in_help_array_all(telegram_id)
    if array != []:
        for help in array:
            with db.connect() as conn:
                help_array_all = set(help.help_array_all)
                help_array_all.discard(telegram_id)
                help_array_all = list(help_array_all)
                if help_array_all == None:
                    help_array_all = []
                u = text('UPDATE rings_help SET help_array_all = :q WHERE rings_id = :id')  # так работает
                conn.execute(u, q=help_array_all, id=help.rings_id)

    needy_id = read_rings_help(telegram_id)
    if needy_id != None:
        session.delete(needy_id)
        session.commit()


def delete_from_orange_help_array(needy_id, delete_id):
    """
    :param needy_id: в пользу кого была помощь
    :param delete_id: кто перестал помогать и вышел из круга
    :return:
    """
    try:
        rings_help = set(read_rings_help(needy_id).help_array_orange)
    except:
        rings_help = set()
    rings_help.discard(delete_id)
    update_orange_rings_help(needy_id, list(rings_help))


def delete_from_help_array_all(needy_id, delete_id):
    """
    :param needy_id: в пользу кого была помощь
    :param delete_id: кто перестал помогать и вышел из круга
    :return:
    """
    try:
        rings_help = set(read_rings_help(needy_id).help_array_all)
    except:
        rings_help = set()
    rings_help.discard(delete_id)
    update_rings_help_array_all(needy_id, list(rings_help))


# endregion

# region intention

def create_intention(from_id, to_id, payment, currency, status=None, event_id=None):
    intention = Intention(from_id=from_id, to_id=to_id, payment=payment, currency=currency, status=status,
                          create_date=datetime.now(), event_id=event_id)

    # try:
    #     session.add(intention)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.add(intention)
    session.commit()


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


def read_intention_by_event_id(event_id):
    intention = session.query(Intention).filter_by(event_id=event_id).first()
    return intention

def update_intention(intention_id, status=None, payment=None):
    intention = session.query(Intention).filter_by(intention_id=intention_id).first()
    if status is not None:
        intention.status = status
    if payment is not None:
        intention.payment = payment
    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


def update_intention_from_all_params(from_id, to_id, payment, status):
    intention = session.query(Intention).filter_by(from_id=from_id, to_id=to_id, payment=payment, status=12).first()
    old_status = intention.status
    if old_status is not None and old_status != 13:
        intention.status = status
        session.commit()
        if read_history_intention_from_all_params(from_id, to_id, payment, intention.intention_id) is None:
            create_history_intention(from_id, to_id, payment, intention.intention_id)
    session.commit()



def read_intention_for_user(from_id=None, to_id=None, statuses=None):
    if from_id is not None:
        intentions = session.query(Intention).filter(Intention.from_id == from_id,
                                                     Intention.status.in_(statuses))
        return intentions

    elif to_id is not None:
        intentions = session.query(Intention).filter(Intention.to_id == to_id,
                                                     Intention.status.in_(statuses))
        return intentions


def get_intention_sum(to_id, statuses=None):
    intentions = session.query(Intention).filter(Intention.to_id == to_id,
                                                 Intention.status.in_(statuses))

    if intentions.count() == 0:
        return 0

    sum = 0
    for row in intentions.all():
        sum += row.payment

    return sum


def update_intetion_status_from_event(event_id, status):
    intention = session.query(Intention).filter_by(event_id=event_id)
    intention.status = status

    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


def delete_intention(to_id, status):
    try:
        session.query(Intention).filter_by(to_id=to_id, status=status).delete()
        session.commit()
    except:
        session.rollback()


def delete_intention_for_quit(telegram_id):
    try:
        intention_to_id = session.query(Intention).filter_by(to_id=telegram_id).all()
        for intention in intention_to_id:
            session.delete(intention)
        session.commit()
    except:
        session.rollback()

    try:
        intention_from_id = session.query(Intention).filter_by(from_id=telegram_id).all()
        for intention in intention_from_id:
            session.delete(intention)
        session.commit()
    except:
        session.rollback()


# endregion


# region history_intention
def create_history_intention(from_id, to_id, payment, from_intention, currency="USD"):
    intention = HistoryIntention(from_id=from_id, to_id=to_id, payment=payment, currency=currency,
                                 create_date=datetime.now(), from_intention=from_intention)

    session.add(intention)
    session.commit()


def read_history_intention(from_id=None, to_id=None, create_date=None):
    if from_id is not None:
        intentions = session.query(HistoryIntention).filter(HistoryIntention.from_id == from_id)
        return intentions

    elif to_id is not None:
        intentions = session.query(HistoryIntention).filter(HistoryIntention.to_id == to_id)
        return intentions


def read_history_intention_from_all_params(from_id, to_id, payment, from_intention):
    intention = session.query(HistoryIntention).filter_by(from_id=from_id, to_id=to_id, payment=payment,
                                                          from_intention=from_intention).first()
    return intention


# endregion


# region requisites
# Create
def create_requisites_user(telegram_id, name='', value='', is_default=False):
    requisites = Requisites(telegram_id=telegram_id,
                            name=name,
                            value=value,
                            is_default=is_default)

    # try:
    #     session.add(requisites)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.add(requisites)
    session.commit()


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
    user_names = session.query(Exodus_Users, Events)
    user_names = user_names.filter(Events.from_id == telegram_id,
                                   or_(Events.status_code == NEW_ORANGE_STATUS, Events.status_code == NEW_RED_STATUS))
    user_names = user_names.join(Events, Events.to_id == Exodus_Users.telegram_id)

    result = {}
    for u, e in user_names:
        result[u.telegram_id] = {'from_id': e.to_id, 'status_code': e.status_code, 'event_id': e.event_id}

    return result


def get_requisites_count(telegram_id):
    count = session.query(Events).filter(Events.from_id == telegram_id,
                                         or_(Events.status_code == NEW_ORANGE_STATUS,
                                             Events.status_code == NEW_RED_STATUS)).count()
    return count


# Update
def update_requisites_user(requisites_id, name='', value='', is_default=False):
    requisites_user = session.query(Requisites).filter_by(requisites_id=requisites_id).first()
    requisites_user.name = name
    requisites_user.value = value
    requisites_user.is_default = is_default

    # try:
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise
    session.commit()


# Delete
def delete_requisites_user(requisites_id):
    requisites_user = session.query(Requisites).filter_by(requisites_id=requisites_id).first()

    # try:
    #     session.delete(requisites_user)
    #     session.commit()
    # except:
    #     session.rollback()
    #     raise

    session.delete(requisites_user)
    session.commit()


def delete_requisites_for_quit(telegram_id):
    requisites_user = session.query(Requisites).filter_by(telegram_id=telegram_id).first()

    if requisites_user is not None:
        session.delete(requisites_user)
        session.commit()


# endregion


# создаем список с моей сетью
def get_my_socium(telegram_id):
    # создаем список с теми, кто помогает мне
    try:
        list_needy_id = set(read_rings_help(telegram_id).help_array_all)
    except:
        list_needy_id = set()
    list_send_notify = read_rings_help_in_help_array_all(telegram_id)
    # добавляем в список тех, кому помогаю я
    for row in list_send_notify:
        list_needy_id.add(row.needy_id)

    # добавляем в список людей, которые вместе со мной помогат кому то
    for row in list_send_notify:
        for id in row.help_array_all:
            list_needy_id.add(id)
            # люди, которым помогает кто-то из тех, с кем мы вместе помогаем кому то
            list_other_needy = read_rings_help_in_help_array_all(id)
            for id_other in list_other_needy:
                list_needy_id.add(id_other.needy_id)

    # удаляем себя из списка
    list_needy_id.discard(telegram_id)

    return list_needy_id


def freez_events(to_id):
    session.query(Events).filter_by(to_id=to_id, status_code=NEW_ORANGE_STATUS).update(
        {'status_code': NEW_ORANGE_STATUS_F})
    session.query(Events).filter_by(to_id=to_id, status_code=NEW_RED_STATUS).update(
        {'status_code': NEW_RED_STATUS_F})
    session.query(Events).filter_by(to_id=to_id, status_code=APPROVE_ORANGE_STATUS).update(
        {'status_code': APPROVE_ORANGE_STATUS_F})
    session.query(Events).filter_by(to_id=to_id, status_code=APPROVE_RED_STATUS).update(
        {'status_code': APPROVE_RED_STATUS_F})

    session.commit()


def unfreez_events(to_id):
    session.query(Events).filter_by(to_id=to_id, status_code=NEW_ORANGE_STATUS_F).update(
        {'status_code': NEW_ORANGE_STATUS})
    session.query(Events).filter_by(to_id=to_id, status_code=NEW_RED_STATUS_F).update(
        {'status_code': NEW_RED_STATUS})
    session.query(Events).filter_by(to_id=to_id, status_code=APPROVE_ORANGE_STATUS_F).update(
        {'status_code': APPROVE_ORANGE_STATUS})
    session.query(Events).filter_by(to_id=to_id, status_code=APPROVE_RED_STATUS_F).update(
        {'status_code': APPROVE_RED_STATUS})

    session.commit()
