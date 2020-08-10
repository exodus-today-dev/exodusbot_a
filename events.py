import telebot
from telebot import types
from datetime import datetime, date, timedelta
import config

bot = telebot.TeleBot(config.API_TOKEN)

from models import *


def invitation_help_orange(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.to_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"
    print('Отправлено-orange-{}-{}-{}'.format(event_id, event.from_id, event.to_id))
    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='orange_invitation-{}-{}'.format(
        user.telegram_id, event_id)))
    keyboard.row(*row)
    bot.send_message(event.from_id, bot_text, reply_markup=keyboard)
    return True


def invitation_help_red(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.to_id)
    bot_text = f"Приглашение помогать {user.first_name} {user.last_name}"
    print('Отправлено-red-{}-{}-{}'.format(event_id, event.from_id, event.to_id))
    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Подробнее', callback_data='red_invitation-{}-{}'.format(
        user.telegram_id, event_id)))
    keyboard.row(*row)
    bot.send_message(event.from_id, bot_text, reply_markup=keyboard)
    return True


def notice_of_intent(event_id):
    """Information about a function.
    """
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.from_id)
    intent = read_intention(event.to_id, event.to_id, 1)[-1]  # берем последний элемент из списка, чтобы обеспечить корреткность событий
    print('Отправлено-{}'.format(event_id))
    bot_text = f"{intent.create_date.strftime('%d %B %Y')}\n\
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
    # 6.3
    event = read_event(event_id)
    # user = read_exodus_user(event.intention.to_id)
    message = "Для вас есть уведомление:"
    keyboard = types.InlineKeyboardMarkup()
    row = [types.InlineKeyboardButton('Подробнее',
                                      callback_data='obligation_money_requested-{}'.format(event_id))]
    keyboard.row(*row)
    bot.send_message(event.from_id, message, reply_markup=keyboard)
    return


def reminder(event_id, direction=None):
    event = read_event(event_id)
    user = read_exodus_user(telegram_id=event.from_id)

    message = "Для вас есть уведомление:"
    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Прочитать',
                                          callback_data='reminder_{}'.format(event_id)))
    keyboard.row(*row)
    if direction == 'out':
        bot.send_message(event.from_id, message, reply_markup=keyboard)
    elif direction == 'in':
        intention = read_intention_by_id(event.to_id)
        bot.send_message(intention.to_id, message, reply_markup=keyboard)


def check_border_first_date():
    """Проверяет, что уведомление попало на первый день месяца,
    что влечет за собой удаление намерения/обязательства и исключение из круга"""
    intentions = session.query(Intention).filter(Intention.status.in_((1, 11, 12))).all()

    for intention in intentions:
        event = read_event(intention.event_id)
        if event.status_code != BEFORE_3_DAYS:
            continue
        if intention.status == 1:
            update_intention(intention.intention_id, status=0)
            update_event_status_code(intention.event_id, CLOSED)
        elif intention.status == 11:
            update_event_status_code(intention.event_id, LAST_REMIND)
            create_event(from_id=intention.from_id,
                         first_name=None,
                         last_name=None,
                         status='obligation',
                         type='reminder_out',
                         min_payments=None,
                         current_payments=None,
                         max_payments=None,
                         currency=None,
                         users=None,
                         to_id=intention.intention_id,
                         reminder_date=datetime.now(),
                         sent=False,
                         status_code=REMIND_LATER)


def check_border_before_3_days():
    # уведомдения за 3 дня до 1го числа
    intentions = session.query(Intention).filter(Intention.status.in_((1, 11))).all()

    for intention in intentions:
        event = read_event(intention.event_id)
        if event.status_code not in (APPROVE_RED_STATUS, APPROVE_ORANGE_STATUS, NEW_OBLIGATION):
            continue
        if intention.status == 1:
            update_event_status_code(intention.event_id, BEFORE_3_DAYS)
            create_event(from_id=intention.from_id,
                         first_name=None,
                         last_name=None,
                         status='intention',
                         type='reminder_out',
                         min_payments=None,
                         current_payments=None,
                         max_payments=None,
                         currency=None,
                         users=None,
                         to_id=intention.intention_id,
                         reminder_date=datetime.now(),
                         sent=False,
                         status_code=REMIND_LATER)
        elif intention.status == 11:
            update_event_status_code(intention.event_id, BEFORE_3_DAYS)
            create_event(from_id=intention.from_id,
                         first_name=None,
                         last_name=None,
                         status='obligation',
                         type='reminder_out',
                         min_payments=None,
                         current_payments=None,
                         max_payments=None,
                         currency=None,
                         users=None,
                         to_id=intention.intention_id,
                         reminder_date=datetime.now(),
                         sent=False,
                         status_code=REMIND_LATER)


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
