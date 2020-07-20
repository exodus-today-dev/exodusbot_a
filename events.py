import telebot
from telebot import types
from datetime import datetime, date
import config

bot = telebot.TeleBot(config.API_TOKEN)

from models import *


def invitation_help_orange(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='orange_invitation-{}'.format(user.telegram_id)))
    keyboard.row(*row)

    # создаем список с теми, у кого мы в списке help_array
    list_needy_id = set(read_rings_help(event.from_id).help_array)

    list_send_notify = read_rings_help_in_help_array(event.from_id)

    for i in list_send_notify:
        list_needy_id.add(i.needy_id)

    for j in list_needy_id:
        try:
            bot.send_message(j, bot_text, reply_markup=keyboard)
        except:
            continue

    #bot.send_message(event.to_id, bot_text, reply_markup=keyboard)

    return True


def invitation_help_red(event_id):

    event = read_event(event_id)
    user = read_exodus_user(event.from_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='red_invitation-{}'.format(user.telegram_id)))
    keyboard.row(*row)

    # создаем список с теми, у кого мы в списке help_array
    list_needy_id = set(read_rings_help(event.from_id).help_array)

    list_send_notify = read_rings_help_in_help_array(event.from_id)

    for i in list_send_notify:
        list_needy_id.add(i.needy_id)

    for j in list_needy_id:
        try:
            bot.send_message(j, bot_text, reply_markup=keyboard)
        except:
            continue

    return True


def notice_of_intent(event_id):
    """Information about a function.
    """
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.from_id)
    intent = read_intention(event.from_id, event.to_id, 1)[-1]  # берем последний элемент из списка, чтобы обеспечить корреткность событий

    bot_text = f"{intent.create_date.strftime('%d %B %Y')}/{intent.create_date.strftime('%I:%M%p')}\n\
Участник {user.first_name} {user.last_name} записал свое намерение помогать вам на сумму: {intent.payment} {event.currency}"
    bot.send_message(event.to_id, bot_text)


# 6.4
def obligation_sended_notice(event_id):
    event = read_event(event_id)

    user = read_exodus_user(telegram_id=event.from_id)
    first_name = user.first_name
    last_name = user.last_name
    intent = read_intention_with_payment(event.from_id, event.to_id, event.current_payments, 12)  # check status

    intention_id = intent.intention_id
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    requisites = read_requisites_user(user_to.telegram_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value

    sum = intent.payment
    currency = intent.currency

    # requisites = read_requisites_by_user_id(telegram_id=event.to_id)
    # requisites_name = requisites.name
    # requisites_value = requisites.value

    message = 'Участник {first_name} {last_name} исполнил ' \
              'обязательства на сумму {sum} {currency}.\n\n' \
              'Пожалуйста, проверьте ваши реквизиты {req_name} {req_value} и ' \
              'подтвердите получение:'.format(first_name=first_name,
                                              last_name=last_name,
                                              sum=sum, currency=currency,
                                              req_name=req_name,
                                              req_value=req_value)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Напомнить позже',
                                          callback_data='remind_later_{}'.format(event.event_id)))
    row.append(types.InlineKeyboardButton('Да, я получил',
                                          callback_data='send_confirmation_{}'. \
                                          format(event.event_id)))
    keyboard.row(*row)

    bot.send_message(event.to_id, message, reply_markup=keyboard)
    return True


# 6.9
def obligation_recieved_notice(event_id):
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.to_id)
    print(user.first_name)
    confirmation_of_an_obligation(event.from_id, user.first_name, event.current_payments, event.currency)
    # update_event(event_id, True)


# 6.10
def reminder_for_6_10(event_id):
    event = read_event(event_id)

    user = read_exodus_user(telegram_id=event.from_id)
    first_name = user.first_name

    message = 'Требуется ваше действие!' \
              'Участник {first_name} исполнил ' \
              'обязательство на сумму {sum} {currency}.' \
              'Это произошло болеее 5 дней назад, но вы так и не подтвердили получение средств.\n\n' \
              'Пожалуйста, проверьте ваши реквизиты и ' \
              'подтвердите получение:'.format(first_name=first_name,
                                              sum=event.current_payments, currency=event.currency)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Напомнить позже',
                                          callback_data='6_10_remind_later_{}'.format(event.event_id)))

    row.append(types.InlineKeyboardButton('Да, я получил',
                                          callback_data='6_10_send_confirmation_{}'. \
                                          format(event.event_id)))

    row.append(types.InlineKeyboardButton('Нет, я не получил',
                                          callback_data='6_10_no_send_confirmation_{}'. \
                                          format(event.event_id)))

    keyboard.row(*row)

    bot.send_message(event.to_id, message, reply_markup=keyboard)
    return True


def obligation_money_requested_notice(event_id):
    pass  # 6.3


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


def confirmation_of_an_obligation(chat_id, name: str, amount: int, currency: int) -> None:
    """Information about a function.
    """
    bot.send_message(chat_id,
                     f"Участник {name} подтвердил, что ваше обязательство на сумму {amount} {currency} исполнено.")


def cancellation_of_intent(message, name: str, amount: int, currency: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id,
                     f"Участник {name} отменил свое намерение помогать вам на сумму {amount} {currency}.")


def network_member_new_intent(message, newname: str, name: str, amount: int, currency: int, status: str, x: int, y: int,
                              z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id,
                     f"Новый участник {newname} записал намерение помогать Участнику {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")


def cancel_intent_on_network_member(message, newname: str, name: str, amount: int, currency: int, status: str, x: int,
                                    y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id,
                     f"Участник {newname} отменил свое намерение помогать Участнику {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}.\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")


def new_network_member_commitment(message, newname: str, name: str, amount: int, currency: int, status: str, x: int,
                                  y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id,
                     f"Новый участник {newname} перевел намерение в обязательство перед Участником {name} на сумму {amount} {currency}.\n\nУчастник {name} {status}.\nСобрано {x} из {y} {currency}.\nОжидается {z} {currency}.\nВсего участников: {q}.")


def network_member_commitment_fulfilled(message, newname: str, name: str, amount: int, currency: int, status: str,
                                        x: int, y: int, z: int, q: int) -> None:
    """Information about a function.
    """
    bot.send_message(message.chat.id,
                     f"Участник {newname} выполнил обязательство перед Участником {name} на сумму {amount} {currency}.\n\nУчастник {name}.\nСобрано {x} из {y} {status}.\nОжидается {z} {currency}.\nВсего участников: {q}.")
