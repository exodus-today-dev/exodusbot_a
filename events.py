import telebot
from telebot import types
import config

bot = telebot.TeleBot(config.API_TOKEN)

from models import *
from symbols import *
from status_codes import *


def create_future_intention(event):
    update_event(event.event_id, True)
    create_event(from_id=event.from_id,
                 first_name=None,  # TODO not needed
                 last_name=None,  # TODO not needed
                 status='orange',
                 type='notice',
                 min_payments=None,
                 current_payments=None,
                 max_payments=None,
                 currency=None,
                 users=0,
                 to_id=event.to_id,
                 sent=True,
                 reminder_date=date.today(),
                 status_code=APPROVE_ORANGE_STATUS,
                 intention=Intention(from_id=event.from_id, to_id=event.to_id,
                                     payment=event.current_payments, currency='USD', status=1,
                                     create_date=datetime.now()))


def invitation_help_orange(event_id):
    event = read_event(event_id)
    user = read_exodus_user(event.to_id)
    bot_text = f"Уведомление о запросе на ежемесячную помощь для {user.first_name} {user.last_name}"
    # print('Отправлено-orange-{}-{}-{}'.format(event_id, event.from_id, event.to_id))
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
    bot_text = f"Запрос на экстренную помощь для {user.first_name} {user.last_name}"
    # print('Отправлено-red-{}-{}-{}'.format(event_id, event.from_id, event.to_id))
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
    user_needy = read_exodus_user(telegram_id=event.to_id)
    intent = read_intention(event.from_id, event.to_id, 1)[
        -1]  # берем последний элемент из списка, чтобы обеспечить корреткность событий
    # print('Отправлено-{}'.format(event_id))

    try:
        status = get_status(user_needy.status)
        status_from = get_status(user.status)
    except:
        status = ''
        status_from = ''

    ring = read_rings_help(user_needy.telegram_id)
    already_payments_oblig = get_intention_sum(user_needy.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user_needy.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user_needy.max_payments)
    right_sum = user_needy.max_payments - already_payments_oblig if user_needy.max_payments - already_payments_oblig > 0 else 0

    if ring is None:
        users_count = 0
    else:
        try:
            users_count = len(set(ring.help_array_orange))
        except:
            users_count = 0

    bot_text = f"{intent.create_date.strftime('%d %B %Y')}\n\
{user.first_name} {user.last_name} {status_from}  {RIGHT_ARROW} {intent.payment}{HEART_RED}\n\
Вы - {status}\n\
({left_sum}{HEART_RED}/{right_sum}{HELP} {LEFT_ARROW} {users_count} {PEOPLES})"

    bot.send_message(event.to_id, bot_text)

    list_needy_id = get_my_socium(event.to_id)
    list_needy_id.discard(event.from_id)

#     bot_text_for_all = f"{intent.create_date.strftime('%d %B %Y')}\n\
# {user.first_name} {user.last_name} {status_from}  {RIGHT_ARROW}  {HEART_RED} {user_needy.first_name} {user_needy.last_name} на сумму: {intent.payment}\n\n\
# {user_needy.first_name} {user_needy.last_name} - {status}\n\
# {left_sum}/{right_sum}\n\
# Помогают: {users_count}"

    bot_text_for_all = f"{user.first_name} {user.last_name} {status_from}  {RIGHT_ARROW}  {intent.payment}{HEART_RED} {user_needy.first_name} {user_needy.last_name} {status}\n\
({left_sum}{HEART_RED}/{right_sum}{HELP} {LEFT_ARROW} {users_count} {PEOPLES})"

    print(bot_text_for_all)

    for id in list_needy_id:
        bot.send_message(id, bot_text_for_all)


# 6.4
def obligation_sended_notice(event_id):
    event = read_event(event_id)

    user = read_exodus_user(telegram_id=event.from_id)
    status_from = get_status(user.status)
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

    message = '{first_name} {last_name} {status_from} {RIGHT_ARROW} ' \
              '{HANDSHAKE} на сумму {sum}.\n\n' \
              'Пожалуйста, проверьте Ваши реквизиты {req_name} {req_value} и ' \
              'подтвердите получение:'.format(first_name=first_name,
                                              last_name=last_name,
                                              status_from=status_from, RIGHT_ARROW=RIGHT_ARROW,
                                              HANDSHAKE=HANDSHAKE,
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
    status = get_status(user.status)

    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    # confirmation_of_an_obligation(event.from_id, user.first_name, event.current_payments, event.currency)
    bot_text = f"{user.first_name} {user.last_name} подтвердил, что ваше {HANDSHAKE} на сумму {event.current_payments} {event.currency} исполнено.\n\n\
{user.first_name} {user.last_name} - {status}\n\
({left_sum} {HEART_RED}/{right_sum} {HELP})"
    bot.send_message(event.from_id, bot_text)
    # update_event(event_id, True)


# 6.10
def reminder_for_6_10(event_id):
    event = read_event(event_id)

    user = read_exodus_user(telegram_id=event.from_id)
    first_name = user.first_name

    message = 'Требуется ваше действие!' \
              '{first_name} исполнил ' \
              '{HANDSHAKE} на сумму {sum} {currency}.' \
              'Это произошло болеее 5 дней назад, но вы так и не подтвердили получение средств.\n\n' \
              'Пожалуйста, проверьте Ваши реквизиты и ' \
              'подтвердите получение:'.format(first_name=first_name, HANDSHAKE=HANDSHAKE,
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
    message = f"Запрос на исполнение {HANDSHAKE}"
    keyboard = types.InlineKeyboardMarkup()
    row = [types.InlineKeyboardButton('Подробнее',
                                      callback_data='obligation_money_requested-{}'.format(event_id))]
    keyboard.row(*row)
    bot.send_message(event.from_id, message, reply_markup=keyboard)
    return


def reminder(event_id, direction=None):
    event = read_event(event_id)
    # user = read_exodus_user(telegram_id=event.from_id)

    keyboard = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton('Прочитать',
                                          callback_data='reminder_{}'.format(event_id)))
    keyboard.row(*row)
    if direction == 'out':
        message = "Для вас есть уведомление:"
        bot.send_message(event.from_id, message, reply_markup=keyboard)
    elif direction == 'in':
        intention = read_intention_by_id(event.to_id)
        user_from = read_exodus_user(intention.from_id)
        user_from_status = get_status(user_from.status)
        message = f"{user_from.first_name} {user_from.last_name} {user_from_status} {RIGHT_ARROW} {intention.payment} {HANDSHAKE}"
        bot.send_message(intention.to_id, message, reply_markup=keyboard)


def check_border_first_date():
    """Проверяет, что уведомление попало на первый день месяца,
    что влечет за собой удаление намерения/обязательства и исключение из круга"""
    intentions = session.query(Intention).filter(Intention.status.in_((1, 11, 12, 13))).all()

    for intention in intentions:
        event = read_event(intention.event_id)
        if event.status_code != BEFORE_3_DAYS:
            continue
        if intention.status == 1:
            update_intention(intention.intention_id, status=0)
            update_event_status_code(intention.event_id, CLOSED)
            delete_from_help_array_all(intention.to_id, intention.from_id)
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
        elif intention.status == 12:
            update_intention(intention.intention_id, status=0)
            update_event_status_code(intention.event_id, CLOSED)

        elif intention.status == 13:
            update_intention(intention.intention_id, status=0)


def check_border_before_3_days():
    # уведомления за 3 дня до 1го числа
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
