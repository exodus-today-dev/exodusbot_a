import telebot
from telebot import types
from datetime import datetime, date
import config

bot = telebot.TeleBot(config.API_TOKEN)

from models import read_exodus_user, read_event, read_intention
from models import session, Exodus_Users


def invitation_help_orange(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"


    keyboard = types.InlineKeyboardMarkup()
    row=[]
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='orange_invitation-{}'.format(user.telegram_id)))
    keyboard.row(*row)
    bot.send_message(event.to_id, bot_text, reply_markup=keyboard)
    return True

	
def invitation_help_red(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"


    keyboard = types.InlineKeyboardMarkup()
    row=[]
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='orange_invitation-{}'.format(event.event_id)))
    keyboard.row(*row)
    bot.send_message(event.to_id, bot_text, reply_markup=keyboard)
    return True

	
def notice_of_intent(event_id):
    """Information about a function.
    """
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.from_id)
    intent = read_intention(event.from_id,event.to_id,1).first()   #create_date
    bot_text = f"{intent.create_date.strftime('%d %B %Y')}/{intent.create_date.strftime('%I:%M%p')}\n\
Участник {user.first_name} {user.last_name} записал свое намерение помогать вам на сумму: {intent.payment} {event.currency}"
    bot.send_message(event.to_id, bot_text)

# 6.4
def obligation_sended_notice(event_id):
    event = read_event(event_id)

    user = read_exodus_user(telegram_id=event.from_id)
    first_name = user.first_name
    last_name = user.last_name
    intent = read_intention(event.from_id, event.to_id, 12).first() # check status
    sum = intent.payment
    currency = intent.currency

    requisites = read_requisites_by_user_id(telegram_id=event.to_id)
    requisites_name = requisites.name
    requisites_value = requisites.value

    message = 'Участник {first_name} {last_name} исполнил ' \
              'обязательства на сумму {sum} {currency}.\n\n' \
              'Пожалуйста, проверьте ваши реквизиты {req_name} {req_value} и ' \
              'подтвердите получение:'.format(first_name=first_name,
                                              last_name=last_name,
                                              sum=sum, currency=currency,
                                              req_name=requisites_name,
                                              req_value=requisites_value)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Напомнить позже',
                                          callback_data='remind_later_{}'))
    row.append(types.InlineKeyboardButton('Да, я получил',
                                          callback_data='send_confirmation_{}'. \
                                          format(event.to_id)))
    keyboard.row(*row)

    bot.send_message(event.to_id, message, reply_markup=keyboard)
    return True


def obligation_recieved_notice(event_id):
    pass # 6.9


def obligation_money_requested_notice(event_id):
    pass # 6.3


def reminder(event_id):
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.from_id)

    message = "Для вас есть уведомление:"
    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Прочитать',
                                          callback_data='reminder_{}'))
    keyboard.row(*row)
    bot.send_message(event.to_id, message, reply_markup=keyboard)


def confirmation_of_an_obligation(message, name: str, amount: int, currency: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Участник {name} подтвердил, что ваше обязательство на сумму {amount} {currency} исполнено.")

def cancellation_of_intent(message, name: str, amount: int, currency: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Участник {name} отменил свое намерение помогать вам на сумму {amount} {currency}.")

def network_member_new_intent(message, newname: str, name: str, amount: int, currency: int, status: str, x: int, y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Новый участник {newname} записал намерение помогать Участнику {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")

def cancel_intent_on_network_member(message, newname: str, name: str, amount: int, currency: int, status: str, x: int, y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Участник {newname} отменил свое намерение помогать Участнику {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}.\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")

def new_network_member_commitment(message, newname: str, name: str, amount: int, currency: int, status: str, x: int, y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Новый участник {newname} перевел намерение в обязательство перед Участником {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}.\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")

def network_member_commitment_fulfilled(message, newname: str, name: str, amount: int, currency: int, status: str, x: int, y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"Участник {newname} выполнил обязательство перед Участником {name} на сумму {amount} {currency}.\n\nУчастник {Имя} {name}.\nСобрано {x} из {y} {status}.\nОжидается {z} {currency}.\nВсего участников: {q }.")

