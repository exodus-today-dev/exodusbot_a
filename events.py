import telebot
from telebot import types
from datetime import datetime, date

import config


API_TOKEN = config.API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

from models import read_exodus_user, read_event
from models import session, Exodus_Users


def invitation_help_orange(event_id, edit=False, call=''):
    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    all_users = session.query(Exodus_Users).count()  # ------------ TODO
    status = 'Оранжевый \U0001f7e0'
    bot_text = 'Участник {} {} - {}\n\
Период: Ежемесячно\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {} {}'.format(user.first_name,
                                user.last_name,
                                status,
                                user.current_payments,
                                user.max_payments,
                                user.currency,
                                user.max_payments - user.current_payments,
                                user.currency,
                                all_users,
                                user.min_payments,
                                user.currency)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Показать участников: {}'.format(all_users),
                                          callback_data='orange_invitation-1-{}'.format(event.event_id)))
    keyboard.row(*row)
    row = []
    row.append(types.InlineKeyboardButton('Нет', callback_data='orange_invitation-2-{}'.format(event.event_id)))
    row.append(types.InlineKeyboardButton('Да', callback_data='orange_invitation-3-{}'.format(event.event_id)))
    keyboard.row(*row)
    if edit:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=bot_text,
                              reply_markup=keyboard)

    else:
        bot.send_message(event.to_id, bot_text, reply_markup=keyboard)
    return True


def show_all_members(call, event_id, status):  # ------------------ TODO
    key = telebot.types.InlineKeyboardMarkup()
    if status == 'orange':
        but = telebot.types.InlineKeyboardButton(text="Назад", callback_data='orange_invitation-0-{}'.format(event_id))
    elif status == 'red':
        but = telebot.types.InlineKeyboardButton(text="Назад", callback_data='red_invitation-0-{}'.format(event_id))
    key.add(but)
    bot_text = 'Участнику <А> помогают <Q> участников:\n\
\n\
В моей сети:\n\
1. <Имя>\n\
2. <Имя>\n\
...\n\
\n\
Остальные участники:\n\
1. <Имя>\n\
2. <Имя>\n\
...'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=bot_text,
                          reply_markup=key)


def invitation_help_red(event_id, edit=False, call=''):
    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    all_users = session.query(Exodus_Users).count()  # ------------ TODO
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days
    status = 'Красный \U0001F534'
    bot_text = 'Участник {} {} - {}\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
\n\
Осталось {} дней из {}\n\
Обсуждение: <Ссылка>\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {} {}'.format(user.first_name,
                                user.last_name,
                                status,
                                user.current_payments,
                                user.max_payments,
                                user.currency,
                                user.max_payments - user.current_payments,
                                user.currency,
                                all_users,
                                days_end,
                                user.days,
                                user.min_payments,
                                user.currency)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Показать участников: {}'.format(all_users),
                                          callback_data='red_invitation-1-{}'.format(event.event_id)))
    keyboard.row(*row)
    row = []
    row.append(types.InlineKeyboardButton('Нет', callback_data='red_invitation-2-{}'.format(event.event_id)))
    row.append(types.InlineKeyboardButton('Да', callback_data='red_invitation-3-{}'.format(event.event_id)))
    keyboard.row(*row)
    if edit:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=bot_text,
                              reply_markup=keyboard)

    else:
        bot.send_message(event.to_id, bot_text, reply_markup=keyboard)
    return True
