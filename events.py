import telebot
from telebot import types
from datetime import datetime, date
import config

bot = telebot.TeleBot(config.API_TOKEN)

from models import read_exodus_user, read_event
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



def notice_of_intent(message, name: str, date: str, time: str, amount: int, currency: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id, f"{date}/{time}\nУчастник {name} записал свое намерение помогать вам на сумму: {amount} {currency}")

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

