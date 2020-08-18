#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

from datetime import timedelta

import telebot
from aiohttp import web
from telebot import types

# from db_controller.controller import *
from models import *
from status_codes import *
from symbols import *

bot = telebot.TeleBot(config.API_TOKEN)

# bot.remove_webhook()


# --------------------------------- DB ------------------------------


user_dict = {}

event_dict = {}

temp_dict = {}

transaction = {}


# ------------------------------------------------------------------

# проверка на то, что строка - это число и с плавающей точкой тоже
def is_digit(string):
    if string.isdigit():
        if int(string) == abs(int(string)):
            return True
    else:
        try:
            if float(string):
                if float(string) == abs(float(string)):
                    return True
        except ValueError:
            return False


def make_hash(text):
    hash = text.encode().hex()
    return hash


def ref_info(text):
    text = text[7:]
    bytes_object = bytes.fromhex(text)
    text = bytes_object.decode("ASCII")
    text = text.split('+')
    return text


def create_link(from_id, to_id):
    botname = bot.get_me().username
    ref = '{}+{}'.format(from_id, to_id)
    link = f"https://t.me/{botname}?start={make_hash(ref)}"
    return link


def create_csv_file(user_id):
    return


def get_left_days():
    now = datetime.today()
    NY = datetime(now.year, now.month + 1, 1)  # я знаю, тут нет проверки 12 месяца, я дурак ага
    d = NY - now
    return (d.days)


# ------------------------------------------------------------------		


# -------------- G L O B A L   M E N U ---------
def global_menu(message, dont_show_status=False):
    """2.0"""
    bot.clear_step_handler(message)
    user = read_exodus_user(message.chat.id)
    if user is None:
        create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username)
    user = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()

    if user is None:
        welcome(message)
    else:
        if user.status == "green":
            status = GREEN_BALL
        elif user.status == "orange":
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
            status = f'{ORANGE_BALL}\n{left_sum}/{right_sum}'
        elif 'red' in user.status:
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
            status = f'{RED_BALL}\n{left_sum}/{right_sum}'
        else:
            orange_green_wizard(message)
            dont_show_status = True
    markup = types.ReplyKeyboardMarkup()
    btn2 = types.KeyboardButton(text='\U0001f4ca Транзакции')
    btn3 = types.KeyboardButton(text='\U0001f527 Настройки')
    btn4 = types.KeyboardButton(text='\U0001f465 Участники')
    markup.row(btn2)
    markup.row(btn3, btn4)
    if not dont_show_status:
        bot.send_message(message.chat.id, 'Ваш статус: {}'.format(status))
    bot.send_message(message.chat.id, 'Меню:', reply_markup=markup)


def global_check(message):
    """2.0.1"""
    text = message.text
    # if text == 'Мой статус':
    #     status_menu(message)
    if 'Транзакции' in text:
        transactions_menu(message)
    elif 'Настройки' in text:
        configuration_menu(message)
    elif 'Участники' in text:
        members_menu(message)


# -------------------------------------------------------------------

def status_menu(message):
    """2.2"""
    user = read_exodus_user(message.chat.id)
    if user is not None:
        if user.status == 'green':
            green_status_wizard(message)
        elif user.status == 'orange':
            orange_status_wizard(message)
        elif 'red' in user.status:
            red_status_wizard(message)
        else:
            bot.send_message(message.chat.id, 'ОШИБКА СТАТУСА')
            global_menu(message)
    else:
        welcome(message)
    return


def status_check(message):
    if message.text == 'Главное меню':
        global_menu(message)
        return


def configuration_menu(message):
    """2.3-3"""
    user = read_exodus_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton(text='Статус')
    btn3 = types.KeyboardButton(text='Реквизиты')
    btn2 = types.KeyboardButton(text='Изменить ссылку на чат')
    btn4 = types.KeyboardButton(text='Главное меню')

    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)

    bot_text = f'Настройки:\n\
\n\
Валюта: {user.currency}\n\
\n\
Реквизиты:'
    requisites = read_requisites_user(message.chat.id)
    if requisites == []:
        bot_text = bot_text + '\nВы не указали реквезиты'
    else:
        n = 0
        for requisite in requisites:
            n += 1
            bot_text += f'\n{n}. {requisite.name} - {requisite.value}'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, configuration_check)


def configuration_check(message):
    """3"""
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    text = message.text

    if text == 'Статус':
        status_menu(message)
        return
    elif text == 'Реквизиты':
        requisites_wizard(message)
        return
    elif text == 'Изменить ссылку на чат':
        edit_link_menu(message)
        return
    elif text == 'Настройки уведомлений':
        bot.send_message(message.chat.id, 'Настройки уведомлений')  # TODO
        global_menu(message)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return
    elif text == 'Валюта':
        user = read_exodus_user(message.chat.id)
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton(text='USD')
        btn2 = types.KeyboardButton(text='Euro')
        btn3 = types.KeyboardButton(text='Гривны')
        btn4 = types.KeyboardButton(text='Рубли')
        btn5 = types.KeyboardButton(text='GBR')
        btn6 = types.KeyboardButton(text='CAD')
        btn7 = types.KeyboardButton(text='Главное меню')
        markup.row(btn1, btn2, btn3)
        markup.row(btn4, btn5, btn6)
        markup.row(btn7)
        msg = bot.send_message(message.chat.id, 'Валюта по умолчанию: {}\nВыберите Другую валюту'.format(user.currency),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, config_wizzard_currency)
        return
    elif "/start" in text:
        welcome_base(message)
        return


def edit_link_menu(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)

    user = read_exodus_user(message.chat.id)
    if user.link is None or user.link == '':
        link = 'не задана'
    else:
        link = user.link
    bot_text = 'Текущая ссылка: {}\nВведите новую ссылку на чат'.format(link)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_link_check)


def edit_link_check(message):
    link = message.text
    bot_text = 'Ваша новая ссылка на чат\n{}'.format(link)
    update_exodus_user(message.chat.id, link=link)
    bot.send_message(message.chat.id, bot_text)
    configuration_menu(message)


def requisites_wizard(message):
    requisites = read_requisites_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    tmp_list = []
    if requisites != []:
        for requisite in requisites:
            if requisite.is_default:
                tmp_list.append(requisite.name + ' (по умолчанию)')
            else:
                tmp_list.append(requisite.name)
        for word in tmp_list:
            btn = types.KeyboardButton(word)
            markup.row(btn)

    btn3 = types.KeyboardButton('Добавить реквизиты')
    btn4 = types.KeyboardButton('Назад')
    markup.row(btn3, btn4)

    msg = bot.send_message(message.chat.id, 'Выберите реквизиты для редактирования:', reply_markup=markup)
    bot.register_next_step_handler(msg, requisites_wizard_check)


def requisites_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    requisites = read_requisites_user(message.chat.id)
    tmp_list = []
    if requisites != []:
        for requisite in requisites:
            if requisite.is_default:
                tmp_list.append(requisite.name + ' (по умолчанию)')
            else:
                tmp_list.append(requisite.name)
    if text in tmp_list:
        select_requisite(message)
        return
    elif text == 'Добавить реквизиты':
        add_requisite_name(message)
        return
    elif text == 'Назад':
        configuration_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Пошло что-то не так. Попробуйте снова')
        bot.register_next_step_handler(msg, requisites_wizard_check)
        return


def select_requisite(message):
    text = message.text

    if text.find('по умолчанию') > -1:
        bot.send_message(message.chat.id, 'Реквизиты по умолчанию:')
        text = text[:-15]
    requisite = read_requisites_name(message.chat.id, text)
    text_bot = f"Название: {requisite.name}\n\
Значение: {requisite.value}"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать данные')
    btn2 = types.KeyboardButton(text='Сделать реквизитами по умолчанию')
    btn3 = types.KeyboardButton(text='Удалить')
    btn4 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, text_bot, reply_markup=markup)
    bot.register_next_step_handler(msg, select_requisite_check, requisite)
    return


def select_requisite_check(message, requisite):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать данные':
        add_requisite_name(message, requisite.requisites_id)
        return
    elif text == 'Сделать реквизитами по умолчанию':
        unmark_default_requisites(message.chat.id)
        update_requisites_user(requisite.requisites_id, requisite.name, requisite.value, True)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        requisites_wizard(message)
        return
    elif text == 'Удалить':
        delete_requisite(message, requisite)
        return
    elif text == 'Назад':
        requisites_wizard(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Пошло что-то не так. Попробуйте снова')
        bot.register_next_step_handler(msg, select_requisite_check)
        return
    return


def delete_requisite(message, requisite):
    bot_text = f"вы собираетесь удалить реквизиты:\n\
\n\
Название: {requisite.name}\n\
Значение: {requisite.value}"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Да, удалить')
    btn2 = types.KeyboardButton(text='Нет')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, delete_requisite_check, requisite)


def delete_requisite_check(message, requisite):
    text = message.text
    if text == 'Да, удалить':
        delete_requisites_user(requisite.requisites_id)
        bot.send_message(message.chat.id, "Реквизит удалён")
        bot.clear_step_handler(message)
        requisites_wizard(message)
        return
    elif text == 'Нет':
        select_requisite(message, requisite.name)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Пошло что-то не так. Попробуйте снова')
        bot.register_next_step_handler(msg, delete_requisite_check, requisite)
        return
    return


def add_requisite_name(message, edit_id=0):
    bot_text = f'Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")'
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, add_requisite_value, edit_id)
    return


def add_requisite_value(message, edit_id=0):
    requisite_name = message.text
    bot_text = f'Введите только номер счета, карты или идентификатор (чтобы его легче было скопировать)'
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, pre_save_requisite, requisite_name, edit_id)
    return


def pre_save_requisite(message, requisite_name, edit_id=0):
    requisite_value = message.text
    bot_text = f'Название: {requisite_name}\n\
Значение: {requisite_value}\n\
Данные введены верно?'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Нет')
    btn2 = types.KeyboardButton(text='Да')
    btn3 = types.KeyboardButton(text='Да, сделать реквизитами по умолчанию')
    btn4 = types.KeyboardButton(text='Отмена')
    markup.row(btn1, btn2)
    markup.row(btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, pre_save_requisite_check, requisite_name, requisite_value, edit_id)
    return


# ---------------------
def unmark_default_requisites(telegram_id):
    all = read_requisites_user(telegram_id)
    for row in all:
        update_requisites_user(row.requisites_id, row.name, row.value, False)
    return


# ---------------------


def pre_save_requisite_check(message, requisite_name, requisite_value, edit_id=0):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    to_req_settings = read_requisites_user(message.chat.id)
    if text == 'Нет':
        add_requisite_name(message)
        return
    elif text == 'Да':
        if edit_id != 0:
            update_requisites_user(edit_id, requisite_name, requisite_value)
        else:
            create_requisites_user(telegram_id=message.chat.id, name=requisite_name, value=requisite_value)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        if not to_req_settings:
            global_menu(message)
            return
        requisites_wizard(message)
        return
    elif text == 'Да, сделать реквизитами по умолчанию':
        unmark_default_requisites(message.chat.id)
        if edit_id != 0:
            update_requisites_user(edit_id, requisite_name, requisite_value, True)
        else:
            create_requisites_user(message.chat.id, requisite_name, requisite_value, True)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        if not to_req_settings:
            global_menu(message)
            return
        requisites_wizard(message)
        return
    elif text == 'Отмена':
        if not to_req_settings:
            add_requisite_name(message)
            return
        configuration_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Пошло что-то не так. Попробуйте снова')
        bot.register_next_step_handler(msg, pre_save_requisite_check)
        return
    return


def transactions_menu(message):
    """2.4"""

    user = read_exodus_user(message.chat.id)

    intention = read_intention(from_id=message.chat.id, status=1)
    my_intent = 0.0
    if intention is not None:
        for pay in intention:
            my_intent = my_intent + pay.payment

    intention = read_intention(from_id=message.chat.id, status=11)
    my_obligation = 0.0
    if intention is not None:
        for pay in intention:
            my_obligation = my_obligation + pay.payment

    intention = read_intention(to_id=message.chat.id, status=1)
    me_intent = 0.0
    if intention is not None:
        for pay in intention:
            me_intent = me_intent + pay.payment

    intention = read_intention(to_id=message.chat.id, status=11)
    me_obligation = 0.0
    if intention is not None:
        for pay in intention:
            me_obligation = me_obligation + pay.payment

    status = get_status(user.status)  # TODO
    bot_text = f"Статус: {status}\n\
\n\
{HEART_RED}: \n\
В мою пользу: {me_intent} {user.currency}\n\
В пользу других: {my_intent} {user.currency}\n\
\n\
{HANDSHAKE}: \n\
В мою пользу: {me_obligation} {user.currency}\n\
В пользу других: {my_obligation} {user.currency}\n"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В пользу других')
    btn2 = types.KeyboardButton(text='В мою пользу')
    #    btn3 = types.KeyboardButton(text='За всё время')
    btn4 = types.KeyboardButton(text='Не исполненные')
    btn5 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1, btn2)
    #    markup.row(btn3,btn4)
    markup.row(btn4)
    markup.row(btn5)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, transactions_check)


def transactions_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'В пользу других':
        for_other_wizard(message)
        return
    elif text == 'В мою пользу':
        for_my_wizard(message)
        return
    # elif text == 'За всё время':
    #     for_all_time_wizard(message)
    #     return
    elif text == 'Не исполненные':
        not_executed_wizard(message)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        global_menu(message)
        return


def members_menu(message, meta_txt=None):
    """2.5"""

    user = read_exodus_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    ref = ''
    if user.ref != '':
        referal = read_exodus_user(user.ref)
        ref = '{} {}'.format(referal.first_name, referal.last_name)

    transactions_in_count = read_intention_for_user(to_id=message.chat.id, statuses=(1, 11, 12)).count()
    transactions_out_count = read_intention_for_user(from_id=message.chat.id, statuses=(1, 11, 12)).count()
    requisites_count = get_requisites_count(message.chat.id)

    btn1 = types.KeyboardButton(text='Мой профиль')
    btn2 = types.KeyboardButton(text='В мою пользу ({})'.format(transactions_in_count))
    btn3 = types.KeyboardButton(text='В пользу других ({})'.format(transactions_out_count))
    btn4 = types.KeyboardButton(text='Запросы помощи({})'.format(requisites_count))
    btn5 = types.KeyboardButton(text='Главное меню')
    btn6 = types.KeyboardButton(text='Моя сеть')
    markup.row(btn1, btn6)
    markup.row(btn2, btn3)
    # markup.row(btn3)
    markup.row(btn4)  # ________________ TODO
    markup.row(btn5)

    currency = user.currency

    user_id = message.chat.id

    intentions_out_sum = sum_out_intentions(user_id)
    intentions_in_sum = sum_in_intentions(user_id)
    obligations_in_sum = sum_in_obligations(user_id)
    executed_in_sum = sum_in_executed(user_id)
    obligations_out_sum = sum_out_obligations(user_id)
    executed_out_sum = sum_out_executed(user_id)

    # transactions_in_count = count_in_transactions(user_id)
    # transactions_out_count = count_out_transactions(user_id)

    bot_text = 'Я в сети Эксодус с {data}\n ' \
               'Меня пригласил: {ref}\n' \
               '\n' \
               'В мою пользу ({tr_in}):\n' \
               '  {HEART_RED}: {int_in} {currency}\n' \
               '  {HANDSHAKE}: {obl_in} {currency}\n' \
               '  Исполнено: {exe_in} {currency}\n' \
               '\n' \
               'В пользу других ({tr_out}):\n' \
               '  {HEART_RED}: {int_out} {currency}\n' \
               '  {HANDSHAKE}: {obl_out} {currency}\n' \
               '  Исполнено: {exe_out} {currency}'.format(
        data=user.create_date.strftime("%d %B %Y"),
        ref=ref, currency=currency, int_in=intentions_in_sum,
        obl_in=obligations_in_sum, exe_in=executed_in_sum,
        int_out=intentions_out_sum, obl_out=obligations_out_sum,
        exe_out=executed_out_sum, tr_in=transactions_in_count,
        tr_out=transactions_out_count, HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE)

    if meta_txt is None:
        msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    else:
        msg = bot.send_message(message.chat.id, text=meta_txt, reply_markup=markup)
    bot.register_next_step_handler(msg, members_check)
    return


# new # >>>

def print_members_list_in_network(message, member_id, direction):
    # """ 5.2 """

    # alert #empty.check

    intentions = None

    if direction == 'in':
        # intentions = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12)).distinct("from_id")
        intentions = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12))
    elif direction == 'out':
        # intentions = read_intention_for_user(from_id=member_id, statuses=(1, 11, 12)).distinct("to_id")
        intentions = read_intention_for_user(from_id=member_id, statuses=(1, 11, 12))

    msg_text = ''

    for i, row in enumerate(intentions.all()):
        # warning
        #  no.pagination.by.10

        # warning
        #  crash: if no user found

        user = None

        if direction == 'in':
            user = read_exodus_user(row.from_id)
        elif direction == 'out':
            user = read_exodus_user(row.to_id)
        try:
            status = get_status(user.status)  # TODO отваливается при пустом или не существующем пользователе
        except:
            status = ''

        msg_text = msg_text + '{i}. {first_name} {last_name} {status}\n'.format(
            i=i + 1, first_name=user.first_name,
            last_name=user.last_name, status=status)

    # сообщение в телеграмме не может быть длиннее 4096 символов. 14 юзеров - это 400 символов.
    # нужно привязать пагинацию
    if len(msg_text) < 4000:
        bot.send_message(message.chat.id, msg_text)

    return


def get_members_list(member_id, direction):
    intentions = None

    if direction == 'in':
        intentions = read_intention(to_id=member_id).distinct('from_id')
    elif direction == 'out':
        intentions = read_intention(from_id=member_id).distinct('to_id')

    output_list = [0, ]

    for i, row in enumerate(intentions.all()):
        if direction == 'in':
            output_list.append(row.from_id)
        elif direction == 'out':
            output_list.append(row.to_id)

    return output_list


def sum_in_intentions(user_id):
    sum = 0
    intentions = read_intention(to_id=user_id, status=1)
    for row in intentions:
        sum += row.payment
    return sum


def sum_out_intentions(user_id):
    sum = 0
    intentions = read_intention(from_id=user_id, status=1)
    for row in intentions:
        sum += row.payment
    return sum


def count_in_transactions(user_id):
    count = 0
    intentions = read_intention(to_id=user_id, status=1)
    count += intentions.count()
    obligations = read_intention(to_id=user_id, status=11)
    count += obligations.count()
    obligations = read_intention(to_id=user_id, status=12)
    count += obligations.count()
    # executed = read_intention(to_id=user_id, status=13)
    # count += executed.count()
    return count


def count_out_transactions(user_id):
    count = 0
    intentions = read_intention(from_id=user_id, status=1)
    count += intentions.count()
    obligations = read_intention(from_id=user_id, status=11)
    count += obligations.count()
    obligations = read_intention(from_id=user_id, status=12)
    count += obligations.count()
    # executed = read_intention(from_id=user_id, status=13)
    # count += executed.count()
    return count


def sum_in_obligations(user_id):
    sum = 0
    obligations = read_intention(to_id=user_id, status=11)
    for row in obligations:
        sum += row.payment
    obligations = read_intention(to_id=user_id, status=12)
    for row in obligations:
        sum += row.payment
    return sum


def sum_out_obligations(user_id):
    sum = 0
    obligations = read_intention(from_id=user_id, status=11)
    for row in obligations:
        sum += row.payment
    obligations = read_intention(from_id=user_id, status=12)
    for row in obligations:
        sum += row.payment
    return sum


def sum_in_executed(user_id):
    sum = 0
    executed = read_intention(to_id=user_id, status=13)
    for row in executed:
        sum += row.payment
    return sum


def sum_out_executed(user_id):
    sum = 0
    executed = read_intention(from_id=user_id, status=13)
    for row in executed:
        sum += row.payment
    return sum


def in_my_circle_alpha(other_id, self_id):
    result = False
    out_trans = read_intention(from_id=self_id,
                               to_id=other_id)
    in_trans = read_intention(from_id=other_id,
                              to_id=self_id)
    if in_trans.count() > 0 or out_trans.count() > 0:
        result = True
    return result


def generate_status_info_text(user):
    # warning
    # ТЗ. какая математика у этих подсчётов?
    #     перепроверить все

    status_info_text = ''
    max_payment_text = ''
    min_payment_text = ''

    to_collect = float(user.max_payments) - \
                 float(sum_in_obligations(user.telegram_id)) - \
                 float(sum_in_intentions(user.telegram_id))

    to_collect_text = '  сколько ещё нужно собрать: {}'.format(to_collect)

    if 'red' in user.status:
        days = timedelta(days=user.days)
        end_date = user.start_date + days
        end_date_text = '  до какой даты: {}'.format(end_date)

        status_info_text = to_collect_text + '\n' + end_date_text + '\n'
    elif user.status == 'orange':
        max_payment_text = '  сколько нужно в месяц: {}'.format(user.max_payments)
        status_info_text = max_payment_text + '\n' + \
                           to_collect_text + '\n'

    return status_info_text


def generate_user_info_preview(user_id):
    user = read_exodus_user(user_id)

    ref = user.ref
    data = user.create_date
    first_name = user.first_name
    last_name = user.last_name
    status = get_status(user.status)
    currency = user.currency

    intentions_out_sum = sum_out_intentions(user_id)
    intentions_in_sum = sum_in_intentions(user_id)
    obligations_in_sum = sum_in_obligations(user_id)
    executed_in_sum = sum_in_executed(user_id)
    obligations_out_sum = sum_out_obligations(user_id)
    executed_out_sum = sum_out_executed(user_id)

    transactions_in_count = count_in_transactions(user_id)
    transactions_out_count = count_out_transactions(user_id)

    user_info_preview = 'Имя участника: {first_name} {last_name}\n' \
                        'В сети Эксодус с {data}\n' \
                        'Пригласил: {ref}\n' \
                        '\n' \
                        'Статус: {status}\n' \
                        '\n' \
                        'В его пользу ({tr_in}):\n' \
                        '  {HEART_RED}: {int_in} {currency}\n' \
                        '  {HANDSHAKE}: {obl_in} {currency}\n' \
                        '  Исполнено: {exe_in} {currency}\n' \
                        '\n' \
                        'В пользу других ({tr_out}):\n' \
                        '  {HEART_RED}: {int_out} {currency}\n' \
                        '  {HANDSHAKE}: {obl_out} {currency}\n' \
                        '  Исполнено: {exe_out} {currency}'.format(
        data=data.strftime("%d %B %Y"), ref=ref,
        first_name=first_name, last_name=last_name,
        status=status, currency=currency, int_in=intentions_in_sum,
        obl_in=obligations_in_sum, exe_in=executed_in_sum,
        int_out=intentions_out_sum, obl_out=obligations_out_sum,
        exe_out=executed_out_sum, tr_in=transactions_in_count,
        tr_out=transactions_out_count, HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE)

    return user_info_preview


def generate_user_info_text(user, self_id):
    """ 5.2 """

    ref = user.ref
    if type(ref) is int:
        referal = read_exodus_user(user.ref)
        ref = '{} {}'.format(referal.first_name, referal.last_name)
    else:
        ref = ''
    data = user.create_date
    first_name = user.first_name
    last_name = user.last_name
    status = get_status(user.status)
    currency = user.currency

    intentions_out_sum = sum_out_intentions(user.telegram_id)
    intentions_in_sum = sum_in_intentions(user.telegram_id)
    obligations_in_sum = sum_in_obligations(user.telegram_id)
    executed_in_sum = sum_in_executed(user.telegram_id)
    obligations_out_sum = sum_out_obligations(user.telegram_id)
    executed_out_sum = sum_out_executed(user.telegram_id)

    transactions_in_count = count_in_transactions(user.telegram_id)
    transactions_out_count = count_out_transactions(user.telegram_id)

    user_info_text = 'В сети Эксодус с {data}\n' \
                     'Пригласил: {ref}\n' \
                     'Со мной в круге:\n' \
                     '\n' \
                     'Имя участника: {first_name} {last_name}\n' \
                     'Статус: {status}\n' \
                     '\n'.format(data=data.strftime("%d %B %Y"), ref=ref,
                                 first_name=first_name, last_name=last_name,
                                 status=status)

    if user.status != 'green':
        status_info_text = generate_status_info_text(user)
        user_info_text += status_info_text + '\n'

    if in_my_circle_alpha(user.telegram_id, self_id):
        user_info_text += 'В его пользу ({tr_in}):\n' \
                          '  {HEART_RED}: {int_in} {currency}\n' \
                          '  {HANDSHAKE}: {obl_in} {currency}\n' \
                          '  Исполнено: {exe_in} {currency}\n' \
                          '\n' \
                          'В пользу других ({tr_out}):\n' \
                          '  {HEART_RED}: {int_out} {currency}\n' \
                          '  {HANDSHAKE}: {obl_out} {currency}\n' \
                          '  Исполнено: {exe_out} {currency}'.format(
            HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE,
            currency=currency, int_in=intentions_in_sum,
            obl_in=obligations_in_sum, exe_in=executed_in_sum,
            int_out=intentions_out_sum, obl_out=obligations_out_sum,
            exe_out=executed_out_sum, tr_in=transactions_in_count,
            tr_out=transactions_out_count)
    else:
        user_info_text += f'Информация о {HEART_RED} и {HANDSHAKE} доступна ' \
                          'только для участников в моей сети.'
    return user_info_text


def members_list_in_network_menu(message, member_id, direction):
    """ 5.2 """
    print_members_list_in_network(message, member_id, direction)

    markup = types.ReplyKeyboardMarkup()

    # btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn2)

    bot_text = '\n' \
               'Введите номер Участника, чтобы ' \
               'посмотреть подробную информацию:'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, members_list_in_network_check,
                                   member_id, direction)


def selected_member_action_menu(message, member_id):
    """ 5.2 """
    markup = types.ReplyKeyboardMarkup()

    transactions_in_count = count_in_transactions(member_id)
    transactions_out_count = count_out_transactions(member_id)

    btn1 = types.KeyboardButton(text='Профиль участника')
    btn2 = types.KeyboardButton(text='В пользу этого участника '
                                     '({tr_in})'.format(
        tr_in=transactions_in_count))
    btn3 = types.KeyboardButton(text='Этот участник в пользу других '
                                     '({tr_out})'.format(
        tr_out=transactions_out_count))
    btn4 = types.KeyboardButton(text='Главное меню')

    btn5 = types.KeyboardButton(text='Сеть участника')

    markup.row(btn1, btn5)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)

    bot_text = '\nВыберите пункт меню'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, selected_member_action_check,
                                   member_id)


def selected_member_action_check(message, member_id):  # bookmark
    """ 5.2 """
    text = message.text

    if text == 'Профиль участника':
        members_menu_profile_link(message, member_id)
    elif text[:24] == 'В пользу этого участника':
        members_list_in_network_menu(message, member_id, 'in')
    elif text[:29] == 'Этот участник в пользу других':
        members_list_in_network_menu(message, member_id, 'out')
    elif text == 'Главное меню':
        global_menu(message)

    elif 'Сеть участника' in text:
        show_other_socium(message, member_id)

    elif "/start" in text:
        welcome_base(message)

    else:
        bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        selected_member_action_menu(message, member_id)


def members_list_in_network_check(message, member_id, direction):
    """ 5.2 """
    text = message.text

    # if text == 'Показать еще 10':  # bug # дважды печатает список
    #     print_members_list_in_network(message, member_id, direction)
    #     members_list_in_network_menu(message, member_id, direction)
    #     return

    if text == 'Назад':
        members_menu(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark

            members_list = get_members_list(member_id, direction)
            selected_id = int(text)
            user = read_exodus_user(members_list[selected_id])
            user_info_text = generate_user_info_text(user, message.chat.id)
            bot.send_message(message.chat.id, user_info_text)
            selected_member_action_menu(message, members_list[selected_id])

        except:
            msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
            bot.register_next_step_handler(msg,
                                           members_list_in_network_check,
                                           member_id, direction)

        return
    return


# new # <<<

def show_other_socium(message, user_id):
    # print(user_id)
    list_my_socium = get_my_socium(user_id)

    string_name = ''
    for i, id_help in enumerate(list_my_socium):
        user = read_exodus_user(id_help)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        string_name = string_name + '\n{}. {} {} {}  {}/{}'.format(i + 1, user.first_name, user.last_name,
                                                                   get_status(user.status), left_sum, right_sum)

    bot_text = 'В сети участника:{}'.format(string_name) + '\n\n' \
                                                           'Введите номер Участника, чтобы ' \
                                                           'посмотреть подробную информацию:'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, check_other_socium, user_id)


def show_my_socium(message):
    list_my_socium = get_my_socium(message.chat.id)

    string_name = ''
    for i, id_help in enumerate(list_my_socium):
        user = read_exodus_user(id_help)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        string_name = string_name + '\n{}. {} {} {}  {}/{}'.format(i + 1, user.first_name, user.last_name,
                                                                   get_status(user.status), left_sum, right_sum)

    bot_text = 'В моей сети:{}'.format(string_name) + '\n\n' \
                                                      'Введите номер Участника, чтобы ' \
                                                      'посмотреть подробную информацию:'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, check_my_socium)


def check_my_socium(message):
    text = message.text
    #    bot.delete_message(message.chat.id, message.message_id)
    if 'Назад' in text:
        members_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark

            members_list = list(get_my_socium(message.chat.id))
            selected_id = int(text) - 1
            user = read_exodus_user(members_list[selected_id])
            user_info_text = generate_user_info_text(user, message.chat.id)
            msg = bot.send_message(message.chat.id, user_info_text)
            selected_member_action_menu(message, members_list[selected_id])
        except:
            msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
            bot.register_next_step_handler(msg, check_my_socium)
        return


def check_other_socium(message, member_id):
    text = message.text
    if 'Назад' in text:
        selected_member_action_menu(message, member_id)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark

            members_list = list(get_my_socium(member_id))
            selected_id = int(text) - 1
            user = read_exodus_user(members_list[selected_id])
            user_info_text = generate_user_info_text(user, message.chat.id)
            msg = bot.send_message(message.chat.id, user_info_text)
            selected_member_action_menu(message, members_list[selected_id])
        except:
            msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
            bot.register_next_step_handler(msg,
                                           check_other_socium, member_id)
        return


def members_check(message):
    text = message.text
    #    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Мой профиль':
        members_menu_profile_link(message, message.chat.id)
        return
    elif text == 'В мою пользу (0)':
        msg = bot.send_message(message.chat.id, f'В Вашу пользу нет записей')
        bot.register_next_step_handler(msg, members_check)
        return
    elif text[0:12] == 'В мою пользу':
        members_list_in_network_menu(message, message.chat.id, 'in')
        return
    elif text == 'В пользу других (0)':
        msg = bot.send_message(message.chat.id, f'В пользу других нет записей')
        bot.register_next_step_handler(msg, members_check)
        return
    elif text[0:15] == 'В пользу других':
        members_list_in_network_menu(message, message.chat.id, 'out')
        return
    elif 'Запросы помощи' in text:
        show_help_requisites(message)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return

    elif 'Моя сеть' in text:
        show_my_socium(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, members_check)
        return
    return


# -------------


def for_other_wizard(message):
    """4.1"""

    members = []
    user_id = message.chat.id
    intentions = read_intention(from_id=user_id, status=1)
    intentions_count = intentions.count()
    for inten in intentions:
        members.append(inten.to_id)
    obligations = read_intention(from_id=user_id, status=11)
    obligations_count = obligations.count()
    for obligation in obligations:
        members.append(obligation.to_id)
    count = len(set(members))

    bot_text = f"Вами записано {intentions_count} {HEART_RED} и {obligations_count} {HANDSHAKE} в пользу {count} участников:"
    bot.clear_step_handler(message)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"{HEART_RED} ({intentions_count})")
    btn2 = types.KeyboardButton(text=f"{HANDSHAKE} ({obligations_count})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, for_other_check)
    return


def for_other_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == f'{HEART_RED} (0)':
        msg = bot.send_message(message.chat.id, f'у Вас нет {HEART_RED}')
        bot.register_next_step_handler(msg, for_other_check)
    elif text == f'{HANDSHAKE} (0)':
        msg = bot.send_message(message.chat.id, f'у Вас нет {HANDSHAKE}')
        bot.register_next_step_handler(msg, for_other_check)
    elif f'{HEART_RED}' in text:
        for_other_wizard_intention(message)
    elif HANDSHAKE in text:
        bot.send_message(message.chat.id, HANDSHAKE)
        for_other_wizard_obligation(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_other_check)
        return
    return


def for_other_wizard_intention(message):
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    left_days = get_left_days()
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id=intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось {left_days} дней:\n'.format(n=intent.intention_id,
                                     first_name=user_to.first_name,
                                     last_name=user_to.last_name,
                                     payment=intent.payment,
                                     currency=intent.currency,
                                     left_days=left_days)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, for_other_wizard_intention_check)
    return


def for_other_wizard_intention_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        for_other_wizard(message)
        return
    if not is_digit(intention_number):
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виду цифры:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HEART_RED}:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return
    transaction[message.chat.id] = intention_number
    intention_for_needy(message, reminder_call=False, intention_id=None)
    return


# bookmark
def intention_for_needy(message, reminder_call, intention_id):
    """6.7"""

    if reminder_call is True:
        intention = read_intention_by_id(intention_id)
    else:
        # bot.delete_message(message.chat.id, message.message_id)
        intention_id = transaction[message.chat.id]
        intention = read_intention_by_id(intention_id)

    user_to = read_exodus_user(telegram_id=intention.to_id)
    status = get_status(user_to.status)

    bot_text = 'Ваше {HEART_RED} в пользу {first_name} {last_name} {status}\n\
На сумму {payment} {currency}'.format(HEART_RED=HEART_RED,
                                      intention_id=intention_id,
                                      first_name=user_to.first_name,
                                      last_name=user_to.last_name,
                                      status=status,
                                      payment=intention.payment,
                                      currency=intention.currency)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f'В {HANDSHAKE}')
    btn2 = types.KeyboardButton(text='Редактировать')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    btn4 = types.KeyboardButton(text=f'Отменить {HEART_RED}')
    btn5 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, intention_for_needy_check, intention_id)
    return


def intention_for_needy_check(message, intention_id=None):
    # 6.7
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == f'В {HANDSHAKE}':
        intention_to_obligation(message)
    elif text == 'Редактировать':
        edit_intention(message)
        return
    elif text == 'Напомнить позже':
        remind_later(message, event_status='intention', reminder_type='reminder_out', intention_id=intention_id)
        global_menu(message)
    elif text == f'Отменить {HEART_RED}':
        cancel_intention(message)
        return
    elif 'Главное меню' in text:
        global_menu(message, True)

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_my_check)
    return


def intention_to_obligation(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    user_from = read_exodus_user(telegram_id=message.chat.id)
    #     bot_text = f"Вы перевели в {HANDSHAKE} свое {HEART_RED} помогать участнику {user_to.first_name} {user_to.last_name} на сумму: {intention.payment} {intention.currency}\n\
    # Когда участник {user_to.first_name} {user_to.last_name} решит что делать с Вашим {HANDSHAKE}, вы получите уведомление."

    bot_text = f"Вы {HEART_RED}  {RIGHT_ARROW}  {HANDSHAKE} {intention.payment}  {RIGHT_ARROW}  {user_to.first_name} {user_to.last_name}\n\
Ждите уведомления."
    update_intention(intention_id, status=11)
    update_event_status_code(intention.event_id, NEW_OBLIGATION)
    # отправка сообщения
    bot.send_message(message.chat.id, bot_text)

    # рассылка уведомлений моему кругу о том, что я начал кому то помогать, кроме того, кто запросил
    list_needy_id = get_my_socium(intention.to_id)
    list_needy_id.discard(message.chat.id)
    bot_text_for_all = f"{user_from.first_name} {user_from.last_name} перевел свое {HEART_RED} в {HANDSHAKE} участнику {user_to.first_name} {user_to.last_name} на сумму: {intention.payment} {intention.currency}"
    for id in list_needy_id:
        bot.send_message(id, bot_text_for_all)

    remind_later(message, event_status=None, reminder_type='reminder_in', intention_id=intention_id, to_menu=True,
                 now=True)
    # global_menu(message)
    return


# bookmark
def remind_later(message, event_status=None, reminder_type=None, intention_id=None, to_menu=False, now=False):
    """ 6.3, 6.7, 6.8 """
    #  create_event       ---------------------------- TODO Создать уведомление - бот вышлет это через сутки

    if now:
        reminder_date = date.today()
    else:
        reminder_date = date.today() + timedelta(days=1)
    # reminder_date = date.today()
    user = read_exodus_user(message.chat.id)

    # reminder_type = 'reminder_in'  # 6.8
    # reminder_type = 'reminder_out'  # 6.3, 6.7
    # status = 'obligation' # 6.3
    # status = 'intention'  # 6.7

    create_event(from_id=message.chat.id,
                 first_name=None,
                 last_name=None,
                 status=event_status,
                 type=reminder_type,
                 min_payments=None,
                 current_payments=None,
                 max_payments=None,
                 currency=None,
                 users=None,
                 to_id=intention_id,
                 reminder_date=reminder_date,
                 sent=False,
                 status_code=REMIND_LATER)  # someday: intention_id

    # message = "Участнику {first_name} {last_name} отправлено ваше решение " \
    #          "исполнить обязательства на сумму {sum} {currency}.". \
    #          format(first_name=None, last_name=None, sum=None, currency=None)
    if to_menu:
        global_menu(message, True)
    return


def edit_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    bot_text = f"Ваше {HEART_RED} было на сумму {intention.payment}\n\
Введите новую сумму (только число) в валюте {intention.currency}"
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_intention_check)
    return


def edit_intention_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    intention_id = transaction[message.chat.id]
    payment = message.text
    if payment == 'Назад':
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return
    if not is_digit(payment):
        msg = bot.send_message(message.chat.id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg, edit_intention_check)
        return
    update_intention(intention_id=intention_id, payment=payment)
    intention_for_needy(message, reminder_call=False, intention_id=None)
    return


def cancel_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Вы хотите отменить свое {HEART_RED} участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency}?"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Нет')
    btn2 = types.KeyboardButton(text='Да')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, cancel_intention_check)
    return


def cancel_intention_check(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Ваше {HEART_RED} участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency} отменено."
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Нет':
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return
    elif text == 'Да':
        update_intention(intention_id, status=0)
        update_event_status_code(intention.event_id, CLOSED)
        bot.send_message(message.chat.id, bot_text)

        user_from = read_exodus_user(message.chat.id)

        text_for_needy = '{} {} отменил своё {} в Вашу пользу на сумму {} {}'.format(
            user_from.first_name, user_from.last_name, HEART_RED, intention.payment, intention.currency)
        bot.send_message(intention.to_id, text_for_needy)

        # рассылка уведомлений
        list_needy_id = get_my_socium(message.chat.id)

        list_needy_id.discard(intention.to_id)
        # удаление из круга
        delete_from_help_array(intention.to_id, message.chat.id)

        text_for_all = '{} {} отменил своё {} {} {} на сумму {} {}'.format(
            user_from.first_name, user_from.last_name, HEART_RED, user_to.first_name, user_to.last_name,
            intention.payment, intention.currency)

        for row in list_needy_id:
            try:
                bot.send_message(row, text_for_all)
            except:
                continue

        global_menu(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_my_check)
    return


def for_other_wizard_obligation(message):
    intentions = read_intention(from_id=message.chat.id, status=11)
    n = 0
    bot_text = ''
    left_days = get_left_days()
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id=intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось {left_days} дней:\n'.format(n=intent.intention_id,
                                     first_name=user_to.first_name,
                                     last_name=user_to.last_name,
                                     payment=intent.payment,
                                     currency=intent.currency,
                                     left_days=left_days)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, for_other_wizard_obligation_check)
    return


def for_other_wizard_obligation_check(message):
    obligation_number = message.text
    if obligation_number == 'Назад':
        for_other_wizard(message)
        return
    if not obligation_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виду цифры:')
        bot.register_next_step_handler(msg, for_other_wizard_obligation_check)
        return
    # intention = read_intention_by_id(intention_id=obligation_number, from_id=message.chat.id, status=11)
    intention = read_intention_by_id(intention_id=obligation_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HEART_RED}:')
        bot.register_next_step_handler(msg, for_other_wizard_obligation_check)
        return
    transaction[message.chat.id] = obligation_number
    obligation_for_needy(message, reminder_call=False, intention_id=None)
    return


def obligation_for_needy(message, reminder_call, intention_id):
    """6.3"""

    if reminder_call is True:
        intention = read_intention_by_id(intention_id)
    else:
        # bot.delete_message(message.chat.id, message.message_id)
        intention_id = transaction[message.chat.id]
        #        intention = read_intention_by_id(intention_id)
        intention = read_intention_by_id(intention_id)

    user_to = read_exodus_user(telegram_id=intention.to_id)
    status = get_status(user_to.status)
    requisites = read_requisites_user(user_to.telegram_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value

    bot_text = f"У Вас {HANDSHAKE} перед участником {user_to.first_name} {user_to.last_name} {status} на сумму {intention.payment} {intention.currency}\n\
Деньги можно отправить на реквизиты:"
    # отдельное сообщени для реквизитов -
    # <значение> (чтобы удобно скопировать)
    markup = types.ReplyKeyboardMarkup()
    # btn1 = types.KeyboardButton(text='Другие реквизиты')  # TODO сделать и подвязать реквизиты
    btn2 = types.KeyboardButton(text='Да, я отправил деньги')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    # markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.send_message(message.chat.id, f"{req_name}")
    bot_text = f"{req_value}"
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    # Может тут добавить добавление в словарь на всякий случай
    transaction[message.chat.id] = intention_id

    bot.register_next_step_handler(msg, obligation_for_needy_check, intention_id)
    return


def obligation_for_needy_check(message, intention_id):
    # 6.3
    text = message.text
    # if text == 'Другие реквизиты':
    #     select_requisites(message)  # TODO сделать и подвязать реквизиты
    if text == 'Да, я отправил деньги':
        obligation_sent_confirm(message)
        return
    elif text == 'Напомнить позже':
        remind_later(message, event_status='obligation', reminder_type='reminder_out',
                     intention_id=intention_id, to_menu=True)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)
    return


def select_requisites(message):  # TODO сделать и подвязать реквизиты
    global_menu(message)
    return


def obligation_sent_confirm(message):
    bot.delete_message(message.chat.id, message.message_id)
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    requisites = read_requisites_user(user_to.telegram_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value
    bot_text = f"Пожалуйста подтвердите, что вы отправили {intention.payment} {intention.currency}\
	Участнику {user_to.first_name} {user_to.last_name} на реквизиты {req_name} {req_value}:"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Да')
    btn2 = types.KeyboardButton(text='Нет')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, obligation_sent_confirm_check)
    return


def obligation_sent_confirm_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Да':
        obligation_sent_confirm_yes(message)
    elif text == 'Нет':
        obligation_for_needy(message, reminder_call=False, intention_id=None)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_my_check)
    return


def obligation_sent_confirm_yes(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Спасибо!\n\
Участнику  {user_to.first_name} {user_to.last_name} будет отправлено уведомление об исполненном {HANDSHAKE} на сумму {intention.payment} {intention.currency}."
    bot.send_message(message.chat.id, bot_text)
    update_intention(intention_id=intention_id, status=12)

    intention_id = transaction[message.chat.id]  # recode: intention_id as
    intention = read_intention_by_id(intention_id)  # argument
    user = read_exodus_user(intention.to_id)

    intentions = read_intention(to_id=intention.to_id)
    users_count = len(intentions.all())
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        all_users = len(set(ring.help_array))
    reminder_date = date.today()

    # 6.4
    create_event(from_id=message.chat.id,
                 first_name=None,
                 last_name=None,
                 status=None,
                 type='obligation_sended',
                 min_payments=None,
                 current_payments=intention.payment,
                 max_payments=None,
                 currency=intention.currency,
                 users=all_users,
                 to_id=intention.to_id,
                 sent=False,
                 reminder_date=reminder_date,
                 status_code=OBLIGATION_APPROVED)

    # bot_text = f"Спасибо! Получателю {user.first_name} {user.last_name} " \
    #            f"будет отправлено уведомление о том, что деньги отправлены."
    # bot.send_message(message.chat.id, bot_text)
    #
    #
    # executed_not_confirm_check(message)

    global_menu(message, True)
    return


def for_my_wizard(message):
    """4.2"""
    members = []
    user_id = message.chat.id
    intentions = read_intention(to_id=user_id, status=1)
    intentions_count = intentions.count()
    for inten in intentions:
        members.append(inten.from_id)
    obligations = read_intention(to_id=user_id, status=11)
    obligations_count = obligations.count()
    for obligation in obligations:
        members.append(obligation.from_id)
    count = len(set(members))
    bot_text = f"{count} участников записали в Вашу пользу {intentions_count} {HEART_RED} и {obligations_count} {HANDSHAKE}:"

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"{HEART_RED} ({intentions_count})")
    btn2 = types.KeyboardButton(text=f"{HANDSHAKE} ({obligations_count})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, for_my_check)
    return


def for_my_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == f'{HEART_RED} (0)':
        msg = bot.send_message(message.chat.id, f'у Вас нет {HEART_RED}')
        bot.register_next_step_handler(msg, for_my_check)
    elif text == f'{HANDSHAKE} (0)':
        msg = bot.send_message(message.chat.id, f'у Вас нет {HANDSHAKE}')
        bot.register_next_step_handler(msg, for_my_check)
    elif HEART_RED in text:
        for_my_wizard_intention(message)
    elif HANDSHAKE in text:
        for_my_wizard_obligation(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_my_check)
    return


def for_my_wizard_intention(message):
    intentions = read_intention(to_id=message.chat.id, status=1)
    bot_text = f"{HEART_RED} в мою пользу:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id=intent.from_id)
        text = f"{intent.intention_id}. {user.first_name} {user.last_name} {intent.payment} {intent.currency}\n"
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, for_my_wizard_intention_check)
    return


def for_my_wizard_intention_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        for_my_wizard(message)
        return
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виде цифры:')
        bot.register_next_step_handler(msg, for_my_wizard_intention_check)
        return
    intention = read_intention_by_id(intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HEART_RED}:')
        bot.register_next_step_handler(msg, for_my_wizard_intention_check)
        return
    transaction[message.chat.id] = intention_number
    # intention_for_me(message)

    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f"{intention.create_date.strftime('%d %B %Y')}\n\
    {user.first_name} {user.last_name}  {RIGHT_ARROW}  {HEART_RED} {intention.payment}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, intention_for_me_check)

    return


# def intention_for_me(message):
#     intention_id = transaction[message.chat.id]
#     intention = read_intention_by_id(intention_id)
#     user = read_exodus_user(telegram_id=intention.from_id)
#     bot_text = f"{intention.create_date.strftime('%d %B %Y %I:%M%p')}\n\
# Участник {user.first_name} {user.last_name} записал свое намерение помогать вам на {intention.payment} {intention.currency}"
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton(text='Назад')
#     markup.row(btn1)
#     msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
#     bot.register_next_step_handler(msg, intention_for_me_check)
#     return


def intention_for_me_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    obligation_number = message.text
    if obligation_number == 'Назад':
        for_my_wizard_intention(message)
        return
    msg = bot.send_message(message.chat.id, 'Что б вернутся назад нажмите назад')
    bot.register_next_step_handler(msg, intention_for_me_check)
    return


def for_my_wizard_obligation(message):
    intentions = read_intention(to_id=message.chat.id, status=11)
    n = 0
    bot_text = f"{HANDSHAKE} в мою пользу:\n"
    for intent in intentions:
        n = n + 1
        user = read_exodus_user(telegram_id=intent.from_id)
        text = f"{intent.intention_id}. {user.first_name} {user.last_name} {intent.payment} {intent.currency}\n"
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, for_my_wizard_obligation_check)
    return


def for_my_wizard_obligation_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        for_my_wizard(message)
        return
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виде цифры:')
        bot.register_next_step_handler(msg, for_my_wizard_obligation_check)
        return
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HANDSHAKE}:')
        bot.register_next_step_handler(msg, for_my_wizard_obligation_check)
        return
    transaction[message.chat.id] = intention_number
    # intention_for_me(message) #bookmark # for_me_obligation(message)
    for_me_obligation(message, reminder_call=True, intention_id=intention.intention_id)
    return


def for_me_obligation(message, reminder_call, intention_id):
    """6.8"""

    if reminder_call is True:
        intention = read_intention_by_id(intention_id=intention_id)
    else:
        intention_id = transaction[message.chat.id]
        intention = read_intention_by_id(intention_id=intention_id)

    user_from = read_exodus_user(telegram_id=intention.from_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    status = get_status(user_to.status)
    already_payments_oblig = get_intention_sum(user_to.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user_to.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user_to.max_payments)
    right_sum = user_to.max_payments - already_payments_oblig if user_to.max_payments - already_payments_oblig > 0 else 0
    status_from = get_status(user_from.status)

    bot_text = f"{user_from.first_name} {user_from.last_name} {status_from} {RIGHT_ARROW} {HANDSHAKE} {intention.payment}\n\
Ваш статус: {status} \n\
{left_sum}/{right_sum} {user_to.currency}"

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Запрос на исполнение')
    btn2 = types.KeyboardButton(text='Хранить')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, for_me_obligation_check, intention_id)
    return


def for_me_obligation_check(message, obligation_id):
    """ 6.8 """
    text = message.text
    # bot.delete_message(message.chat.id, message.message_id)
    if text == 'Запрос на исполнение':
        obligation_to_execution(message, obligation_id)
    elif text == 'Хранить':
        keep_obligation(message, obligation_id)
    elif text == 'Напомнить позже':
        remind_later(message, event_status=None, reminder_type='reminder_in', intention_id=obligation_id, to_menu=True)
    elif text == 'Главное меню':
        global_menu(message, True)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_me_obligation_check, obligation_id)
    return


def obligation_to_execution(message, obligation_id):
    """ 6.8 """
    # intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=obligation_id)

    user = read_exodus_user(telegram_id=intention.from_id)
    update_intention(intention_id=obligation_id, status=15)
    bot_text = f'Участнику {user.first_name} {user.last_name} отправлено ваше решение исполнить ' \
               f'{HANDSHAKE} на сумму {intention.payment} {intention.currency}.'

    payment = intention.payment
    currency = intention.currency
    intentions = read_intention(to_id=obligation_id)
    # users_count = len(intentions.all())
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        all_users = len(set(ring.help_array))
    from_id = intention.from_id
    reminder_date = date.today()

    create_event(from_id=from_id,
                 first_name=None,
                 last_name=None,
                 status=None,
                 type='obligation_money_requested',
                 min_payments=None,
                 current_payments=payment,
                 max_payments=None,
                 currency=currency,
                 users=all_users,
                 to_id=message.chat.id,
                 reminder_date=reminder_date,
                 sent=False,
                 intention=intention)

    bot.send_message(message.chat.id, bot_text)

    global_menu(message, True)

    return


def keep_obligation(message, obligation_id):
    # intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=obligation_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f'{HANDSHAKE} участника {user.first_name} {user.last_name} на ' \
               f'сумму  {intention.payment} {intention.currency} будет хранится у вас, ' \
               f'пока вы не примите решение.\n' \
               f'Посмотреть все {HANDSHAKE} можно в разделе главного меню ' \
               f'"транзакции" > "{HANDSHAKE}"'
    bot.send_message(message.chat.id, bot_text)
    global_menu(message)
    return


# def for_all_time_wizard(message):
#     """4.3"""
#     bot_text = 'За все время использования бота:\n\
# \n\
# В пользу других:\n\
# Мои намерения: <сумма> <валюта>\n\
# Мои обязательства: <сумма> <валюта>\n\
# Исполнено на сумму: <сумма> <валюта>\n\
# \n\
# В мою пользу:\n\
# Намерения: <сумма> <валюта>\n\
# Обязательства: <сумма> <валюта>\n\
# Исполнено на сумму: <сумма> <валюта>'
#     markup = types.ReplyKeyboardMarkup()
#     btn1 = types.KeyboardButton(text='В пользу других')
#     btn2 = types.KeyboardButton(text='В мою пользу')
#     btn3 = types.KeyboardButton(text='Скачать статистику (csv)')
#     btn4 = types.KeyboardButton(text='Назад')
#     markup.row(btn1, btn2)
#     markup.row(btn3)
#     markup.row(btn4)
#     msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
#     bot.register_next_step_handler(msg, for_all_time_check)
#     return


def for_all_time_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'В пользу других':
        bot.send_message(message.chat.id, 'not work yet')  # TODO
        global_menu(message)
    elif text == 'В мою пользу':
        bot.send_message(message.chat.id, 'not work yet')  # TODO
        global_menu(message)
    elif text == 'Скачать статистику (csv)':
        bot.send_message(message.chat.id, 'not work yet')  # TODO
        global_menu(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, for_my_check)
    return


def not_executed_wizard(message):
    """4.4"""
    user_id = message.chat.id
    intentions = read_intention(to_id=user_id, status=12)
    if intentions is None:
        for_me_intent = 0
    else:
        for_me_intent = intentions.count()

    intentions = read_intention(from_id=user_id, status=12)
    if intentions is None:
        for_other_intent = 0
    else:
        for_other_intent = intentions.count()
    bot_text = f'Не исполненными считаются те {HANDSHAKE}, которые не подтвердил получатель.'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"В мою пользу ({for_me_intent})")
    btn2 = types.KeyboardButton(text=f"В пользу других ({for_other_intent})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, not_executed_check)
    return


def not_executed_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text[0:12] == 'В мою пользу':
        not_executed_wizard_to_me(message)
    elif text[0:15] == 'В пользу других':
        not_executed_wizard_for_all(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, not_executed_check)
    return


def not_executed_wizard_to_me(message):
    intentions = read_intention(to_id=message.chat.id, status=12)
    bot_text = f"Я не подтвердил {intentions.count()} {HANDSHAKE} в мою пользу:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id=intent.from_id)
        text = f"{intent.intention_id}. {user.first_name} {user.last_name} {intent.payment} {intent.currency}\n"
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, not_executed_wizard_to_me_check)
    return


def not_executed_wizard_to_me_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        not_executed_wizard(message)
        return
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виде цифры:')
        bot.register_next_step_handler(msg, not_executed_wizard_to_me_check)
        return
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HANDSHAKE}:')
        bot.register_next_step_handler(msg, not_executed_wizard_to_me_check)
        return
    transaction[message.chat.id] = intention_number
    executed_not_confirm_me(message)
    return


def executed_not_confirm_me(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.to_id)
    requisites = read_requisites_user(intention.to_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value
    bot_text = f"Я не подтвердил исполненное {HANDSHAKE} в мою пользу:\n\
\n\
Дата: {intention.create_date.strftime('%d %B %Y')}\n\
Время: {intention.create_date.strftime('%I:%M%p')}\n\
Отправитель: {user.first_name} {user.last_name} {get_status}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"  # TODO реквезиты
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text="Я получил эту сумму")
    btn2 = types.KeyboardButton(text="Повторный запрос на исполнение")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, executed_not_confirm_check)
    return


def executed_not_confirm_me_check(message):
    text = message.text
    if text == 'Назад':
        not_executed_wizard_for_all(message)
        return
    if text == 'Я получил эту сумму':
        executed_confirm(message)
        return
    if text == 'Повторный запрос на исполнение':
        repeat_executed_request(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, executed_not_confirm_check)
    return


def executed_confirm(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    requisites = read_requisites_user(message.chat.id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value
    bot_text = f"Пожалуйста подтвердите, что вы проверили свои реквизиты и убедились в том, что получили деньги:\n\
\n\
Дата: {intention.create_date.strftime('%d %B %Y')}\n\
Время: {intention.create_date.strftime('%I:%M%p')}\n\
Получатель: {user.first_name} {user.last_name} {get_status}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text="Да, я получил")
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, executed_confirm_check)
    return


def executed_confirm_check(message):
    text = message.text
    if text == 'Назад':
        executed_not_confirm_me(message)
        return
    if text == 'Да, я получил':
        executed_confirm_confirmed(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, executed_confirm_check)
    return


def executed_confirm_confirmed(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f"Спасибо! Участнику {user.first_name} {user.last_name} будет отправлено уведомление о том, что его " \
               f"{HANDSHAKE} исполнено. "
    # create_event        TODO 
    not_executed_wizard_for_all(message)
    return


def repeat_executed_request(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f"Спасибо! Отправителю {user.first_name} {user.last_name} будет отправлено уведомление о том, что " \
               f"деньги все еще не получены. "
    # create_event        TODO 
    not_executed_wizard_for_all(message)
    return


def not_executed_wizard_for_all(message):
    intentions = read_intention(from_id=message.chat.id, status=12)
    bot_text = f"{intentions.count()} моих {HANDSHAKE} в пользу других не было подтверждено:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id=intent.to_id)
        text = f"{intent.intention_id}. {user.first_name} {user.last_name} {intent.payment} {intent.currency}\n"
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)
    bot.register_next_step_handler(msg, not_executed_wizard_for_all_check)
    return


def not_executed_wizard_for_all_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        not_executed_wizard(message)
        return
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виде цифры:')
        bot.register_next_step_handler(msg, not_executed_wizard_for_all_check)
        return
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HANDSHAKE}:')
        bot.register_next_step_handler(msg, not_executed_wizard_for_all_check)
        return
    transaction[message.chat.id] = intention_number
    executed_not_confirm(message)
    return


def executed_not_confirm(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.to_id)
    requisites = read_requisites_user(intention.to_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value
    bot_text = f"Исполненное мной {HANDSHAKE} не было подтверждено:\n\
\n\
Дата: {intention.create_date.strftime('%d %B %Y')}\n\
Время: {intention.create_date.strftime('%I:%M%p')}\n\
Получатель: {user.first_name} {user.last_name} {get_status(user.status)}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"  # TODO реквезиты
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text="Я отправил эту сумму")
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, executed_not_confirm_check)
    return


def executed_not_confirm_check(message):
    text = message.text
    if text == 'Назад':
        not_executed_wizard_for_all(message)
        return
    if text == 'Я отправил эту сумму':
        executed_was_sent(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, executed_not_confirm_check)
    return


def executed_was_sent(message):
    intention_id = transaction[message.chat.id]  # recode: intention_id as
    intention = read_intention_by_id(intention_id)  # argument
    user = read_exodus_user(intention.to_id)

    intentions = read_intention(to_id=intention.to_id)
    users_count = len(intentions.all())
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        all_users = len(set(ring.help_array))
    reminder_date = date.today()

    # 6.4
    create_event(from_id=message.chat.id,
                 first_name=None,
                 last_name=None,
                 status=None,
                 type='obligation_sended',
                 min_payments=None,
                 current_payments=intention.payment,
                 max_payments=None,
                 currency=intention.currency,
                 users=all_users,
                 to_id=intention.to_id,
                 sent=False,
                 reminder_date=reminder_date)

    bot_text = f"Спасибо! Получателю {user.first_name} {user.last_name} " \
               f"будет отправлено уведомление о том, что деньги отправлены."
    bot.send_message(message.chat.id, bot_text)

    # not_executed_wizard(message)
    not_executed_wizard_for_all(message)

    return


def members_menu_profile_link(message, member_id):
    user_id = message.chat.id
    user = read_exodus_user(member_id)
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    bot.delete_message(user_id, message.message_id)
    if user.status == 'green':
        bot_text = '\U0001F464 Имя участника: {} {}\n\
Статус: {}'.format(user.first_name, user.last_name, GREEN_BALL)

    elif user.status == 'orange':
        ring = read_rings_help(user.telegram_id)
        if ring is None:
            all_users = 0
        else:
            all_users = len(set(ring.help_array))
        bot_text = '\U0001F464 Имя участника: {} {}\n\
Статус: {}\n\
\U0001F4B0 {}/{} {}\nУже помогают: {}\n'.format(user.first_name,
                                                user.last_name,
                                                ORANGE_BALL,
                                                left_sum,
                                                right_sum,
                                                user.currency,
                                                all_users)

    elif 'red' in user.status:
        ring = read_rings_help(user.telegram_id)
        if ring is None:
            all_users = 0
        elif ring.help_array_red is None:
            all_users = 0
        else:
            all_users = len(set(ring.help_array_red))
        d0 = user.start_date
        d1 = date.today()
        delta = d1 - d0
        bot_text = '\U0001F464 Имя участника: {} {}\n\
Статус: {}\n\
\U0001F4B0 {}/{} {}\nУже помогают: {}'.format(user.first_name,
                                              user.last_name,
                                              RED_BALL,
                                              left_sum,
                                              right_sum,
                                              user.currency,
                                              all_users)  # ------------ TODO

    else:
        bot_text = 'СТАТУС НЕ УКАЗАН. ОШИБКА'

    bot.send_message(user_id, bot_text)  # общий текст

    bot.send_message(user_id, "Ссылка на обсуждение \U0001F4E2")  # ссылка на обсуждение
    if user.link == '' or user.link == None:
        bot.send_message(user_id, "-")  # ссылка на обсуждение
    else:
        bot.send_message(user_id, user.link)  # ссылка на обсуждение

    if user.status != 'green':
        link = create_link(user.telegram_id, user.telegram_id)
        bot.send_message(user_id, "Ссылка для помощи \U0001F4E9")  # отправка сообщений с ссылкой-приглашением
        bot.send_message(user_id, link)  # отправка сообщений с ссылкой-приглашением

    global_menu(message, True)


def config_wizzard_currency(message):
    """3.2"""
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'USD':
        update_exodus_user(message.chat.id, currency='USD')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: USD')
        global_menu(message)
    elif text == 'Euro':
        update_exodus_user(message.chat.id, currency='Euro')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Euro')
        global_menu(message)
    elif text == 'Гривны':
        update_exodus_user(message.chat.id, currency='Гривны')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Гривны')
        global_menu(message)
    elif text == 'Рубли':
        update_exodus_user(message.chat.id, currency='Рубли')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Рубли')
        global_menu(message)
    elif text == 'GBR':
        update_exodus_user(message.chat.id, currency='GBR')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: GBR')
        global_menu(message)
    elif text == 'CAD':
        update_exodus_user(message.chat.id, currency='CAD')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: CAD')
        global_menu(message)
    elif text == 'Главное меню':
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, config_wizzard_currency)


def welcome_base(message):
    """1.0"""
    bot.clear_step_handler(message)
    referral = ref_info(message.text)
    bot.send_message(message.chat.id, "Добро пожаловать в бот Exodus.")
    if referral[0] != '':
        user_from = read_exodus_user(referral[0])
        user_to = read_exodus_user(referral[1])
        if user_from.status == 'green':
            start_without_invitation(message, ref=user_from.telegram_id)
            return

        bot_text = '{} {} приглашает вас помогать {} {}'.format(user_from.first_name,
                                                                                   user_from.last_name,
                                                                                   user_to.first_name,
                                                                                   user_to.last_name)
        bot.send_message(message.chat.id, bot_text)

        if user_to.status == 'orange':
            start_orange_invitation(message, user_to.telegram_id, ref=user_from.telegram_id)
        elif 'red' in user_to.status:
            start_red_invitation(message, user_to.telegram_id, ref=user_from.telegram_id)
    else:
        start_without_invitation(message)


@bot.message_handler(commands=['start'])
def welcome(message):
    """1.0"""
    welcome_base(message)


def start_without_invitation(message, ref=""):
    """1.1"""

    exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
    if not exists:
        create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username, ref=ref)
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
    if exists.status == '':
        orange_green_wizard(message)
    else:
        global_menu(message)


# ----------------------------- 6.1 ORANGE ----------------------
def start_orange_invitation(message, user_to, event_id=None, ref=None):
    """6.1"""
    # print(user_to)
    user = read_exodus_user(telegram_id=user_to)
    ring = read_rings_help(user.telegram_id)
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    intention = read_intention_one(message.chat.id, user.telegram_id, 1)
    link = user.link
    if intention is not None:
        bot_text = f'Вы уже помогаете участнику {user.first_name} {user.last_name}.'
        bot.send_message(message.chat.id, bot_text)
        transaction[message.chat.id] = intention.intention_id
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return

    if ring is None:
        users_count = 0
    else:
        users_count = len(set(ring.help_array))

    status = ORANGE_BALL
    bot_text = 'Участник {first_name} {last_name} {status}\n\
Период: Ежемесячно\n\
{current}/{all}\n\
Обсуждение:\n\
{link}\n\
Уже помогают: {users_count}\n\
\n\
Вы можете помочь этому участнику?'.format(first_name=user.first_name,
                                          last_name=user.last_name,
                                          status=status,
                                          current=left_sum,
                                          all=right_sum,
                                          link=link,
                                          users_count=users_count)

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    temp_dict[
        message.chat.id] = user  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    temp_dict[
        message.chat.id].step = 'orange'  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память

    bot.register_next_step_handler(msg, orange_invitation_check, event_id=event_id, ref=ref)


def orange_invitation_check(message, event_id=None, ref=None):
    """6.1.1"""
    user_to = temp_dict[
        message.chat.id]  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    text = message.text
    if text[0:19] == 'Показать участников':
        show_all_members(message, user_to)
    elif text == 'Нет'.format(0):
        if event_id is None:
            create_event(from_id=message.chat.id,
                         first_name=message.from_user.first_name,
                         last_name=message.from_user.last_name,
                         status='orange',
                         type='orange',
                         min_payments=None,
                         current_payments=None,
                         max_payments=None,
                         currency=None,
                         users=0,
                         to_id=user_to.telegram_id,
                         sent=False,
                         reminder_date=date.today(),
                         status_code=NEW_ORANGE_STATUS)
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            start_without_invitation(message)
        else:
            global_menu(message)
    elif text == 'Да'.format(0):
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username, ref=ref)
        orange_invitation_wizard(message, user_to, event_id)

    elif 'Главное меню' in text:
        global_menu(message, True)

    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, orange_invitation_check)


def orange_invitation_wizard(message, user_to, event_id=None):
    """6.1.2"""
    temp_dict[message.chat.id] = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, 'Введите сумму помощи в {}:'.format(user.currency),
                           reply_markup=markup)
    bot.register_next_step_handler(msg, orange_invitation_wizard_check, event_id)


def orange_invitation_wizard_check(message, event_id=None):  # ------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if message.text == 'Назад':
        start_orange_invitation(message, user.telegram_id)
        return
    if not is_digit(invitation_sum):
        msg = bot.send_message(message.chat.id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg, orange_invitation_wizard_check)
        return

    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array = []
        array.append(message.chat.id)
        create_rings_help(user.telegram_id, array)
    else:
        array = ring.help_array
        array.append(message.chat.id)
        update_rings_help(user.telegram_id, array)

    bot_text = f'Ваше {HEART_RED} принято'

    if event_id is None:
        create_event(from_id=message.chat.id,
                     first_name=user.first_name,  # TODO not needed
                     last_name=user.last_name,  # TODO not needed
                     status='orange',
                     type='notice',
                     min_payments=None,
                     current_payments=user.current_payments,
                     max_payments=user.max_payments,
                     currency=user.currency,
                     users=0,
                     to_id=user.telegram_id,
                     sent=False,
                     reminder_date=date.today(),
                     status_code=APPROVE_ORANGE_STATUS,
                     intention=Intention(from_id=message.chat.id, to_id=user.telegram_id,
                                         payment=invitation_sum, currency=user.currency, status=1,
                                         create_date=datetime.now()))  # someday: intention_id
    else:
        update_event_status_code(event_id, APPROVE_ORANGE_STATUS)
        update_event_type(event_id, 'notice')
        update_event(event_id, False)
        create_intention(message.chat.id, user.telegram_id, invitation_sum, user.currency, status=1, event_id=event_id)

    bot.send_message(message.chat.id, bot_text)
    global_menu(message, True)


# ------------------------------------------------------


def show_all_members(message, user_to):
    bot.delete_message(message.chat.id, message.message_id)
    user = user_to
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        users_count = 0
        first_name = []
        last_name = []
    elif ring.help_array_red is None:
        users_count = 0
        first_name = []
        last_name = []
    else:
        if "red" in user.status:
            users_count = len(set(ring.help_array_red))
        else:
            users_count = len(set(ring.help_array))

        # узнаем кто со мной в сети
        list_my_socium = get_my_socium(message.chat.id)

        first_name = []
        last_name = []
        for id_help in set(ring.help_array):
            if id_help in list_my_socium or id_help == message.chat.id:
                first_name.append(read_exodus_user(id_help).first_name)
                last_name.append(read_exodus_user(id_help).last_name)
    bot_text = 'Участнику {} {} помогают {} участников:\n'.format(user.first_name, user.last_name, users_count)

    string_name = ''
    for i in range(len(first_name)):
        string_name = string_name + '\n{} {}'.format(first_name[i], last_name[i])

    bot_text = bot_text + '\n\
В моей сети:{}'.format(string_name)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, show_all_members_check)


def show_all_members_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    if message.text == 'Назад':
        if temp_dict[message.chat.id].step == 'orange':
            start_orange_invitation(message, temp_dict[message.chat.id].telegram_id)
        elif 'red' in temp_dict[message.chat.id].step:
            start_red_invitation(message, temp_dict[message.chat.id].telegram_id)
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, show_all_members_check)


# ----------------------- 6.2 RED ---------------------------
def start_red_invitation(message, user_to, event_id=None, ref=None):
    """6.2"""
    user = read_exodus_user(telegram_id=user_to)
    status = get_status(user.status)
    ring = read_rings_help(user.telegram_id)
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    intention = read_intention_one(message.chat.id, user.telegram_id, 1)
    if intention is not None:
        bot_text = f'Вы уже помогаете участнику {user.first_name} {user.last_name}.'
        bot.send_message(message.chat.id, bot_text)
        transaction[message.chat.id] = intention.intention_id
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return

    # user = user_to
    # ring = read_rings_help(user.telegram_id)
    # ring = read_rings_help(user_to)
    if ring is None:
        users_count = 0
    elif ring.help_array_red is None:
        users_count = 0
    else:
        if "red" in user.status:
            users_count = len(set(ring.help_array_red))
        else:
            users_count = len(set(ring.help_array))
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days

    bot_text = f'Участник {user.first_name} {user.last_name} {status}\n\
Осталось {days_end} дней из {user.days}\n\
{left_sum}/{right_sum} {user.currency}\n\
Обсуждение:\n\
{user.link}\n\
Уже помогают: {users_count}\n\
\n\
Вы можете помочь этому участнику?\n'

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    temp_dict[
        message.chat.id] = user  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    temp_dict[
        message.chat.id].step = 'red'  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память

    bot.register_next_step_handler(msg, red_invitation_check, event_id=event_id, ref=ref)


def red_invitation_check(message, event_id=None, ref=None):
    """6.1.1"""
    user_to = temp_dict[
        message.chat.id]  # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    text = message.text
    if text[0:19] == 'Показать участников':
        show_all_members(message, user_to)
    elif text == 'Нет'.format(0):
        if event_id is None:
            create_event(from_id=message.chat.id,
                         first_name=message.from_user.first_name,
                         last_name=message.from_user.last_name,
                         status='red',
                         type='red',
                         min_payments=None,
                         current_payments=None,
                         max_payments=None,
                         currency=None,
                         users=0,
                         to_id=user_to.telegram_id,
                         sent=True,
                         reminder_date=date.today(),
                         status_code=NEW_RED_STATUS)
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            start_without_invitation(message)
        else:
            global_menu(message)
    elif text == 'Да'.format(0):
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username, ref=ref)
        red_invitation_wizard(message, user_to, event_id)

    elif 'Главное меню' in text:
        global_menu(message, True)

    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, red_invitation_check)


def red_invitation_wizard(message, user_to, event_id=None):
    """6.1.2"""
    temp_dict[message.chat.id] = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, 'Введите сумму помощи в {}:'.format(user.currency),
                           reply_markup=markup)
    bot.register_next_step_handler(msg, red_invitation_wizard_check, event_id)


def red_invitation_wizard_check(message, event_id=None):  # ------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if message.text == 'Назад':
        start_red_invitation(message, user.telegram_id)
        return
    if not is_digit(invitation_sum):
        msg = bot.send_message(message.chat.id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg, red_invitation_wizard_check)
        return

    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array = []
        array.append(message.chat.id)
        create_rings_help(user.telegram_id, help_array_red=array)
    else:
        array = ring.help_array
        array.append(message.chat.id)
        update_rings_help_array_red(user.telegram_id, array)
    # ring = read_rings_help(user.telegram_id)
    # users_count = session.query(Exodus_Users).count()
    # ring = read_rings_help(user.telegram_id)
    # if ring is None:
    #     all_users = 0
    # else:
    #     all_users = len(set(ring.help_array))

    # d0 = user.start_date
    # d1 = date.today()
    # delta = d1 - d0
    # days_end = user.days - delta.days
    #
    # already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    # already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    # left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    # right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    status = RED_BALL
    bot_text = f'Записано Ваше {HANDSHAKE} участнику {user.first_name} {user.last_name} на сумму {invitation_sum} {user.currency}'

    if event_id is None:
        create_event(from_id=message.chat.id,
                     first_name=user.first_name,  # TODO not needed
                     last_name=user.last_name,  # TODO not needed
                     status='red',
                     type='notice',
                     min_payments=None,
                     current_payments=invitation_sum,
                     max_payments=user.max_payments,
                     currency=user.currency,
                     users=0,
                     to_id=user.telegram_id,
                     sent=False,
                     reminder_date=date.today(),
                     status_code=APPROVE_RED_STATUS,
                     intention=Intention(from_id=message.chat.id, to_id=user.telegram_id,
                                         payment=invitation_sum, currency=user.currency, status=11,
                                         create_date=datetime.now()))  # someday: intention_id
    else:
        update_event_status_code(event_id, APPROVE_RED_STATUS)
        update_event_type(event_id, 'notice')
        update_event(event_id, False)
        create_intention(message.chat.id, user.telegram_id, invitation_sum, user.currency, status=11, event_id=event_id)

    # рассылка уведомлений моему кругу о том, что я начал кому то помогать, кроме того, кто запросил
    list_needy_id = get_my_socium(message.chat.id)
    list_needy_id.discard(user.telegram_id)
    user_from = read_exodus_user(telegram_id=message.chat.id)
    status_from = get_status(user_from.status)

    bot_text_for_all = f"{user_from.first_name} {user_from.last_name}  {RIGHT_ARROW}  {HANDSHAKE} {invitation_sum} {user.first_name} {user.last_name}"
    for id in list_needy_id:
        bot.send_message(id, bot_text_for_all)

    # сообщение, что ты записал обязательство кому-то
    bot.send_message(message.chat.id, bot_text)

    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    # сообщение, получателю, что кто то записал обязательство в его пользу
    text_for_u = f"{user_from.first_name} {user_from.last_name} {status_from}  {RIGHT_ARROW}  {HANDSHAKE} {invitation_sum}\n\
Ваш статус: {status} \n\
{left_sum}/{right_sum} {user.currency}"
    bot.send_message(user.telegram_id, text_for_u)

    global_menu(message, True)


# ---------------------------------------------------------


def orange_status_wizard(message):
    user = read_exodus_user(message.chat.id)
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        all_users = len(set(ring.help_array))
    bot_text = 'Ваш статус: {}\n\
{}/{} {}\n\
Ссылка на обсуждение: {}\n\
\n\
Период: Ежемесячно\n\
\n\
Уже помогают: {}'.format(ORANGE_BALL,
                         left_sum,
                         right_sum,
                         user.currency,
                         user.link,
                         all_users)
    bot.send_message(message.chat.id, bot_text)
    link = create_link(user.telegram_id, user.telegram_id)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать')
    btn2 = types.KeyboardButton(text='Изменить статус')
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    link = create_link(user.telegram_id, user.telegram_id)
    msg = bot.send_message(message.chat.id, link, reply_markup=markup)
    bot.register_next_step_handler(msg, orange_menu_check)


def orange_menu_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать':
        orange_edit_wizard(message)
    elif text == 'Изменить статус':
        green_red_wizard(message)
    elif text == 'Назад':
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, orange_menu_check)


def green_red_wizard(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=GREEN_BALL)
    btn2 = types.KeyboardButton(text=RED_BALL)
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, 'Выберите новый статус', reply_markup=markup)
    bot.register_next_step_handler(msg, green_red_check)


def green_red_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == GREEN_BALL:
        green_edit_wizard(message)
    elif text == RED_BALL:
        red_edit_wizard(message)
    elif text == 'Назад':
        orange_status_wizard(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, green_red_check)


def green_edit_wizard(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Сохранить')
    btn2 = types.KeyboardButton(text='Отмена')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, f'Вы собираетесь сменить статус на {GREEN_BALL}\n\
Пожалуйста подтвердите смену статуса:\n\
\n\
Если ваш статус был {ORANGE_BALL} или {RED_BALL}, все {HEART_RED} участников в Вашу пользу будут автоматически удалены.\n\
\n\
Все {HANDSHAKE} участников в Вашу пользу останутся в силе. Посмотреть все {HANDSHAKE} можно в разделе главного меню "Транзакции" > "Все {HANDSHAKE}"',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, green_edit_wizard_check)


def green_edit_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Сохранить':
        bot.send_message(message.chat.id, 'Статус сохранён')

        # создаем список с теми, у кого мы в списке help_array
        list_needy_id = set(read_rings_help(message.chat.id).help_array)
        telegram_name = read_exodus_user(message.chat.id)

        list_send_notify = read_rings_help_in_help_array(message.chat.id)

        for row in list_send_notify:
            list_needy_id.add(row.needy_id)

        for row in list_needy_id:
            try:
                bot.send_message(row, '{} {} сменил статус на {}'.format(telegram_name.first_name, telegram_name.last_name, GREEN_BALL))
                # закрываем намерения и event
                intention = read_intention(from_id=row, to_id=message.chat.id).all()
                for id in intention:
                    update_intention(id.intention_id, status=0)
                    update_event_status_code(id.event_id, CLOSED)
            except:
                continue

        # удаляем статусы для запроса помощи
        delete_event_new_status(message.chat.id)

        if 'red' in read_exodus_user(message.chat.id).status:
            # удаляем данные из буфферной таблицы
            delete_temp_intention(message.chat.id)

            # очищаем массив помощников для красного
            update_rings_help_array_red(message.chat.id, [])

        update_exodus_user(telegram_id=message.chat.id, status='green', min_payments=0, max_payments=0)

        global_menu(message)
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Статус не сохранён')
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, green_edit_wizard_check)


# ------------------------
def green_status_wizard(message):
    """2.0.1"""
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Изменить статус')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id,
                           f'Ваш статус: {GREEN_BALL}\nСписок участников с которыми Вы связаны, '
                           'можно посмотреть в разделе главного меню "Участники"',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, green_status_wizard_check)


def green_status_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Изменить статус':
        select_orange_red(message)
    elif text == 'Назад':
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, green_status_wizard_check)


def select_orange_red(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=ORANGE_BALL)
    btn2 = types.KeyboardButton(text=RED_BALL)
    btn3 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, "Выберите новый статус:", reply_markup=markup)
    bot.register_next_step_handler(msg, check_orange_red)


def check_orange_red(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == ORANGE_BALL:
        bot.send_message(message.chat.id, f"Вы меняете статус на {ORANGE_BALL}:")
        orange_edit_wizard(message)
    elif text == RED_BALL:
        red_edit_wizard(message)
    elif text == 'Главное меню':
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, check_orange_red)


def red_status_wizard(message):
    user = read_exodus_user(message.chat.id)
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        all_users = len(set(ring.help_array))
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    bot_text = f'Ваш статус: {RED_BALL}\n\
{left_sum}/{right_sum} {user.currency}\n\
Ссылка на обсуждение:\n\
{user.link}\n\
\n\
Осталось {days_end} дней из {user.days}\n\
Уже помогают: {all_users}\n\
\n\
Если вы хотите пригласить кого-то помогать вам, перешлите ему эту ссылку:'
    bot.send_message(message.chat.id, bot_text)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать')
    # btn2 = types.KeyboardButton(text='Изменить статус')
    user_status = user.status
    if 'orange' in user_status:
        btn2 = types.KeyboardButton(text=f'Вернуться к {ORANGE_BALL}')  # orange
    if 'green' in user_status:
        btn2 = types.KeyboardButton(text=f'Вернуться к {GREEN_BALL}')  # green
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    link = create_link(user.telegram_id, user.telegram_id)
    msg = bot.send_message(message.chat.id, link, reply_markup=markup)
    bot.register_next_step_handler(msg, red_status_wizard_check)


def red_status_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать':
        red_edit_wizard(message)
    elif 'Вернуться' in text:
        green_orange_check(message)
    elif text == 'Назад':
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, red_status_wizard_check)


# ------------------ RED WIZARD 2.2 ---------------
def red_edit_wizard(message):
    """2.2"""
    user = read_exodus_user(message.chat.id)
    # сохраняем сумму запроса от оранжевого
    update_exodus_user(telegram_id=message.chat.id, min_payments=user.max_payments)

    if read_rings_help(user.telegram_id) is None:
        create_rings_help(user.telegram_id, [])
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, 'Введите сумму в {}, которая Вам необходима:'.format(user.currency),
                           reply_markup=markup)
    bot.register_next_step_handler(msg, red_edit_wizard_step1)


def red_edit_wizard_step1(message):
    user = read_exodus_user(message.chat.id)
    user_dict[message.chat.id] = user
    chat_id = message.chat.id

    max_payments_red = message.text
    if not is_digit(max_payments_red):
        msg = bot.send_message(chat_id,
                               'Сумма должна быть только в виде цифр. Введите сумму в {}, которая Вам необходима:'.format(
                                   user.currency))
        bot.register_next_step_handler(msg, red_edit_wizard_step1)
        return
    user_dict[message.chat.id].max_payments = float(max_payments_red)
    msg = bot.send_message(message.chat.id, 'Введите кол-во дней, в течении которых вам необходимо собрать эту сумму:')
    bot.register_next_step_handler(msg, red_edit_wizard_step3)


# def red_edit_wizard_step2(message):
#     user = read_exodus_user(message.chat.id)
#     chat_id = message.chat.id
#     min_payments = message.text
#
#     if not is_digit(min_payments):
#         msg = bot.send_message(chat_id,
#                                'Сумма должна быть только в виде цифр. Введите сумму в {}, которая Вам необходима:'.format(
#                                    user.currency))
#         bot.register_next_step_handler(msg, red_edit_wizard_step2)
#         return
#
#     msg = bot.send_message(message.chat.id, 'Введите кол-во дней, в течение которых вам необходимо собрать эту сумму:')
#     bot.register_next_step_handler(msg, red_edit_wizard_step3)


def red_edit_wizard_step3(message):
    # user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    days = message.text
    if not days.isdigit():
        msg = bot.send_message(chat_id,
                               'Кол-во дней должны быть в виде цифр. Введите кол-во дней, в течении которых вам необходимо собрать эту сумму:')
        bot.register_next_step_handler(msg, red_edit_wizard_step3)
        return
    user_dict[message.chat.id].days = days

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Пропустить')
    markup.row(btn1)

    msg = bot.send_message(message.chat.id, 'Введите ссылку на чат:', reply_markup=markup)
    bot.register_next_step_handler(msg, red_edit_wizard_step35)


def red_edit_wizard_step35(message):
    if message.text != 'Пропустить':
        link = message.text
    else:
        link = None
    user = user_dict[message.chat.id]
    bot_text = f'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {RED_BALL}\n\
Обсуждение: {link}\n\
В течении: {user.days}\n\
Необходимая сумма: {user.max_payments} {user.currency}'
    bot.send_message(message.chat.id, bot_text)

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать')
    btn2 = types.KeyboardButton(text='Отмена')
    btn3 = types.KeyboardButton(text='Сохранить статус')
    markup.row(btn1, btn2)
    markup.row(btn3)
    bot_text = 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, red_edit_wizard_step4, link)


def red_edit_wizard_step4(message, link):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать':
        red_edit_wizard(message)
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Настройки не сохранены')
        global_menu(message)

    elif text == 'Сохранить статус':
        bot.send_message(message.chat.id, 'Настройки сохранены')

        user = read_exodus_user(message.chat.id)
        # удаляем эти события, чтобы при возврате к оранжевому счетчик запросов помощи не возрастал
        delete_event_new_status(message.chat.id)
        freeze_intentions(user)

        update_exodus_user(telegram_id=message.chat.id, status='red' + str(user.status), link=link,
                           start_date=date.today(),
                           days=user_dict[message.chat.id].days, min_payments=None,
                           max_payments=user_dict[message.chat.id].max_payments)

        user = read_exodus_user(message.chat.id)
        # all_users = session.query(Exodus_Users).all()
        # users_count = session.query(Exodus_Users).count()

        # создаем список с моей сетью
        list_needy_id = get_my_socium(message.chat.id)

        for users in list_needy_id:
            # TODO           рассылка кругу лиц из таблицы rings
            if users != message.chat.id:
                t_user = read_exodus_user(users)
                create_event(from_id=users,
                             first_name=t_user.first_name,
                             last_name=t_user.last_name,
                             status='red',
                             type='red',
                             min_payments=None,
                             current_payments=user.current_payments,
                             max_payments=user.max_payments,
                             currency=user.currency,
                             users=len(list_needy_id),
                             to_id=message.chat.id,
                             sent=True,
                             reminder_date=date.today(),
                             status_code=NEW_RED_STATUS)  # someday: intention_id

        telegram_name = read_exodus_user(message.chat.id)
        for row in list_needy_id:
            try:
                bot.send_message(row, '{} {} сменил статус на {}'.format(telegram_name.first_name,
                                                                                  telegram_name.last_name, RED_BALL))
            except:
                continue

        global_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, red_edit_wizard_step4, link)


# def green_orange_wizard(message):
#     markup = types.ReplyKeyboardMarkup()
#     btn1 = types.KeyboardButton(text='Зелёный \U0001F7E2')
#     btn2 = types.KeyboardButton(text='Оранжевый \U0001f7e0')
#     btn3 = types.KeyboardButton(text='Назад')
#     markup.row(btn1, btn2)
#     markup.row(btn3)
#     msg = bot.send_message(message.chat.id, 'Выберите новый статус', reply_markup=markup)
#     bot.register_next_step_handler(msg, green_orange_check)

def green_orange_check(message):
    # bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if GREEN_BALL in text:
        green_edit_wizard(message)
    elif ORANGE_BALL in text:
        orange_edit_wizard(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, red_status_wizard_check)

    # ------------------ ORANGE GREEN WIZARD-------


def orange_green_wizard(message):
    #    bot.delete_message(message.chat.id, message.message_id)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=ORANGE_BALL)
    btn2 = types.KeyboardButton(text=GREEN_BALL)
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, 'Пожалуйста выберите Ваш статус', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_green_wizard_step1)


def orange_green_wizard_step1(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    if message.text == ORANGE_BALL:
        bot.send_message(message.chat.id, f'Вы выбрали {ORANGE_BALL} статус', reply_markup=markup)
        orange_edit_wizard(message)
        return
    if message.text == GREEN_BALL:
        bot.send_message(message.chat.id,
                         f'Ваш статус: {GREEN_BALL}\nСписок участников с которыми Вы связаны, можно посмотреть в разделе главного меню "Участники"',
                         reply_markup=markup)
        update_exodus_user(telegram_id=message.chat.id, status='green', min_payments=0, max_payments=0)
        global_menu(message, True)
        requisites = read_requisites_user(message.chat.id)
        if not requisites:
            add_requisite_name(message)
    else:
        orange_green_wizard(message)


# -------------------------------------------


# ------------------ ORANGE WIZARD-------
def orange_edit_wizard(message):
    user = read_exodus_user(message.chat.id)
    if read_rings_help(user.telegram_id) is None:
        create_rings_help(user.telegram_id, [])
    if 'red' in user.status and user.min_payments != 0:
        bot.send_message(message.chat.id,
                         f'Ваш статус возвращается на {ORANGE_BALL}')
        link = user.link
        if 'red' in user.status:
            payments = user.min_payments
        else:
            payments = user.max_payments
        bot.send_message(message.chat.id, 'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {}\n\
Период: Ежемесячно\n\
Необходимая сумма: {} {}'.format(ORANGE_BALL, payments, user.currency))
        markup = types.ReplyKeyboardMarkup()
        # user = read_exodus_user(message.chat.id)
        if user.status == '':
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1)
            markup.row(btn2)
        else:
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Отмена')
            btn3 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1, btn2)
            markup.row(btn3)
        msg = bot.send_message(message.chat.id, 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_final, link)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id,
                               'Какая сумма вам необходима на базовые нужды в {}?'.format(user.currency),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_need_payments)


def orange_step_need_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id

    max_payments_orange = message.text
    if not is_digit(max_payments_orange):
        msg = bot.send_message(chat_id,
                               'Сумма должна быть только в виде цифр. Введите сумму в {}, которую вы бы хотели получать в течении месяца:'.format(
                                   user.currency))
        bot.register_next_step_handler(msg, orange_step_need_payments)
        return
    update_exodus_user(message.chat.id, max_payments=float(max_payments_orange))

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Пропустить')
    markup.row(btn1)

    msg = bot.send_message(message.chat.id, 'Введите ссылку на чат:', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_step_link)


def orange_step_link(message):
    user = read_exodus_user(message.chat.id)
    if message.text != 'Пропустить':
        link = message.text
    else:
        link = None
    if 'red' in user.status and user.min_payments != 0:
        payments = user.min_payments
    else:
        payments = user.max_payments
    bot.send_message(message.chat.id, 'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {}\n\
Период: Ежемесячно\n\
Необходимая сумма: {} {}'.format(ORANGE_BALL, payments, user.currency))
    markup = types.ReplyKeyboardMarkup()
    # user = read_exodus_user(message.chat.id)
    if user.status == '':
        btn1 = types.KeyboardButton(text='Редактировать')
        btn2 = types.KeyboardButton(text='Сохранить')
        markup.row(btn1)
        markup.row(btn2)
    else:
        btn1 = types.KeyboardButton(text='Редактировать')
        btn2 = types.KeyboardButton(text='Отмена')
        btn3 = types.KeyboardButton(text='Сохранить')
        markup.row(btn1, btn2)
        markup.row(btn3)
    msg = bot.send_message(message.chat.id, 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_step_final, link)


# Минимальная сумма

# def orange_step_min_payments(message):
#     user = read_exodus_user(message.chat.id)
#     chat_id = message.chat.id
#
#     msg = bot.send_message(chat_id, 'Пожалуйста проверьте введенные данные:\n \
# \n \
# Статус: Оранжевый\n \
# Период: Ежемесячно.\n \
# Необходимая сумма: {} {}'.format(user.max_payments, user.currency))
#     markup = types.ReplyKeyboardMarkup()
#     # user = read_exodus_user(message.chat.id)
#     if user.status == '':
#         btn1 = types.KeyboardButton(text='Редактировать')
#         btn2 = types.KeyboardButton(text='Сохранить')
#         markup.row(btn1)
#         markup.row(btn2)
#     else:
#         btn1 = types.KeyboardButton(text='Редактировать')
#         btn2 = types.KeyboardButton(text='Отмена')
#         btn3 = types.KeyboardButton(text='Сохранить')
#         markup.row(btn1, btn2)
#         markup.row(btn3)
#     msg = bot.send_message(chat_id, 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
# Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
#     bot.register_next_step_handler(msg, orange_step_final)


def orange_step_final(message, link):
    text = message.text
    # bot.delete_message(message.chat.id, message.message_id)
    if text == 'Редактировать':
        bot.send_message(message.chat.id, 'Вы выбрали редактирование')
        orange_edit_wizard(message)
        return
    if text == 'Отмена':
        bot.send_message(message.chat.id, 'Настройки не сохранены')
        global_menu(message)
        return
    if text == 'Сохранить':
        bot.send_message(message.chat.id, 'Настройки сохранены')

        # удаляем статусы для запроса помощи
        delete_event_new_status(message.chat.id)

        user = read_exodus_user(message.chat.id)
        if 'red' in user.status and user.min_payments != 0:
            count_unfreez_intentions = unfreeze_intentions(user)
        else:
            # list_statuses = [1, 11, 12, 13, 15]
            # # удаляем все активные записи для красного
            # for status in list_statuses:
            #     delete_intention(to_id=message.chat.id, status=status)

            count_unfreez_intentions = 0

        update_exodus_user(message.chat.id, status='orange', link=link)

        # создаем список с моей сетью
        list_needy_id = get_my_socium(message.chat.id)

        if count_unfreez_intentions == 0:
            for users in list_needy_id:
                # TODO           рассылка кругу лиц из таблицы rings
                if users != message.chat.id:
                    t_user = read_exodus_user(users)
                    create_event(from_id=users,
                                 first_name=t_user.first_name,
                                 last_name=t_user.last_name,
                                 status='orange',
                                 type='orange',
                                 min_payments=None,
                                 current_payments=user.current_payments,
                                 max_payments=user.max_payments,
                                 currency=user.currency,
                                 users=len(list_needy_id),
                                 to_id=message.chat.id,
                                 sent=False,
                                 reminder_date=date.today(),
                                 status_code=NEW_ORANGE_STATUS)  # someday: intention_id

        telegram_name = read_exodus_user(message.chat.id)
        for row in list_needy_id:
            try:
                bot.send_message(row, '{} {} сменил статус на {}'.format(telegram_name.first_name, telegram_name.last_name, ORANGE_BALL))
            except:
                continue

        global_menu(message)
        requisites = read_requisites_user(message.chat.id)
        if not requisites:
            add_requisite_name(message)
        # return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, "Пошло что-то не так. Попробуйте снова")
        bot.register_next_step_handler(msg, orange_step_final)
        return


# -------------------------------------------
def show_help_requisites(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users_dict = get_help_requisites(message.chat.id)
    # print(message.chat.id)
    if len(users_dict) == 0:
        txt = 'Никто помощь пока не запрашивал'
        members_menu(message, meta_txt=txt)
    else:
        btns = [types.KeyboardButton(un) for un in users_dict.keys()]
        for btn in btns:
            markup.row(btn)
        btn1 = types.KeyboardButton('Назад')
        markup.row(btn1)
        txt = 'Выберите пользователя, чтобы ответить на его запрос:'
        msg = bot.send_message(message.chat.id, txt, reply_markup=markup)
        bot.register_next_step_handler(msg, restart_invitation, users_dict)
        return


def restart_invitation(message, users_dict):
    if 'Назад' in message.text:
        members_menu(message)
        return
    elif message.text not in users_dict.keys():
        txt = 'Этого пользователя нет в списке'
        msg = bot.send_message(message.chat.id, txt)
        bot.register_next_step_handler(msg, show_help_requisites)
        return
    elif users_dict[message.text]['status_code'] == NEW_ORANGE_STATUS:
        start_orange_invitation(message, users_dict[message.text]['from_id'],
                                event_id=users_dict[message.text]['event_id'])
        return
    elif users_dict[message.text]['status_code'] == NEW_RED_STATUS:
        start_red_invitation(message, users_dict[message.text]['from_id'],
                             event_id=users_dict[message.text]['event_id'])
        return
    global_menu(message)


def freeze_intentions(user):
    to_id = user.telegram_id

    # обновляем статусы в таблице events с окончанием F
    freez_events(to_id)

    list_statuses = [1, 11, 12, 13, 15]
    for status in list_statuses:
        intentions = read_intention(to_id=to_id, status=status)
        status_dict = [id.intention_id for id in intentions]
        # заполняем буфферную таблицу для каждого юзера, intention_id и статусами соответсвующими
        create_temp_intention(to_id, status, status_dict)
        for intention in intentions:
            # зануляем все статусы согласно intention_id
            update_intention(intention.intention_id, 0)


def unfreeze_intentions(user):
    to_id = user.telegram_id
    # возвращаем сумму запроса от оранжевого
    update_exodus_user(telegram_id=to_id, max_payments=user.min_payments)
    # размораживаем события в таблице events
    unfreez_events(to_id)

    list_statuses = [1, 11, 12, 13, 15]
    # удаляем все активные записи для красного
    for status in list_statuses:
        delete_intention(to_id=to_id, status=status)

    count_intentions = 0
    # считываем все данные из буфферной таблицы для конкретного юзера
    list_temp_intention = read_all_temp_intention(to_id)
    for temp_intention in list_temp_intention:
        if len(temp_intention.intention_array) != 0:
            for intention_id in temp_intention.intention_array:
                count_intentions += 1
                # возвращаем статусы, замороженные от оранжевого, в исходные значения
                try:
                    update_intention(intention_id, temp_intention.status)
                except:
                    continue

    # удаляем данные из буфферной таблицы
    delete_temp_intention(to_id)

    # очищаем массив помощников для красного
    update_rings_help_array_red(to_id, [])

    return count_intentions


# -------------------------------------------

@bot.callback_query_handler(func=lambda call: call.data[0:18] == 'orange_invitation-')
def orange_invitation(call):
    global_menu(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_id = call.data.split('-')[1]
    event_id = call.data.split('-')[2]
    # update_event_status_code(event_id, CLOSED)
    start_orange_invitation(call.message, user_id, event_id)
    return


@bot.callback_query_handler(func=lambda call: call.data[0:15] == 'red_invitation-')
def red_invitation(call):
    global_menu(call.message)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user_id = call.data.split('-')[1]
    event_id = call.data.split('-')[2]
    start_red_invitation(call.message, user_id, event_id)
    return


@bot.callback_query_handler(func=lambda call: 'obligation_money_requested-' in call.data)
def obligation_money_requested_notice_call(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    event_id = call.data.split('-')[1]
    event = read_event(event_id)
    obligation_for_needy(call.message, reminder_call=True, intention_id=event.intention.intention_id)
    return


# 6.4
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data[0:13] == 'remind_later_':
        event_id = call.data[13:]
        reminder_date = date.today() + timedelta(days=1)
        update_event_reminder_date(event_id, reminder_date)
        global_menu(call.message)
    elif call.data[0:18] == 'send_confirmation_':
        event_id = call.data[18:]
        update_event_type(event_id, 'obligation_recieved')
        event = read_event(event_id)
        user = read_exodus_user(telegram_id=event.from_id)
        first_name = user.first_name
        last_name = user.last_name
        message = 'Спасибо! Участнику {first_name} {last_name} будет отправлено уведомление о том, ' \
                  'что вы подтвердили иcполнение {HANDSHAKE}.'.format(first_name=first_name,
                                                                      last_name=last_name,
                                                                      HANDSHAKE=HANDSHAKE)

        bot.send_message(call.message.chat.id, message)

        update_intention_from_all_params(event.from_id, event.to_id, int(event.current_payments), 13)

        global_menu(call.message)

    elif call.data[0:18] == '6_10_remind_later_':

        global_menu(call.message)
    elif call.data[0:23] == '6_10_send_confirmation_':

        event_id = call.data[23:]
        update_event_type(event_id, 'obligation_recieved')
        event = read_event(event_id)
        user = read_exodus_user(telegram_id=event.from_id)
        first_name = user.first_name
        message = 'Спасибо! Участнику {first_name} будет отправлено уведомление о том, ' \
                  'что вы подтвердили иcполнение {HANDSHAKE}.'.format(first_name=first_name, HANDSHAKE=HANDSHAKE)

        bot.send_message(event.from_id,
                         '{HANDSHAKE} на сумму {sum} {currency} исполнено'.format(HANDSHAKE=HANDSHAKE,
                                                                                  sum=event.current_payments,
                                                                                  currency=event.currency))
        bot.send_message(call.message.chat.id, message)

        update_intention_from_all_params(event.from_id, event.to_id, int(event.current_payments), 13)

        global_menu(call.message)
    elif call.data[0:26] == '6_10_no_send_confirmation_':

        event_id = call.data[26:]
        event = read_event(event_id)
        user = read_exodus_user(telegram_id=event.to_id)
        first_name = user.first_name
        message = 'Участнику {first_name} выслано повторное уведомление исполнить {HANDSHAKE} на сумму {sum} {currency}.' \
                  'Вы можете посмотреть все {HANDSHAKE} в разделе главного меню "Транзакции" > {HANDSHAKE}.'.format(
            first_name=first_name, sum=event.current_payments, currency=event.currency, HANDSHAKE=HANDSHAKE)

        bot.send_message(event.from_id,
                         'Исполните {HANDSHAKE} на сумму {sum} {currency}'.format(HANDSHAKE=HANDSHAKE,
                                                                                  sum=event.current_payments,
                                                                                  currency=event.currency))
        bot.send_message(call.message.chat.id, message)

        global_menu(call.message)

    # bookmark # callback
    elif call.data[0:9] == 'reminder_':
        event_id = call.data.split('_')[1]
        event = read_event(event_id)
        if event.type == 'reminder_in':
            # 6.8
            for_me_obligation(call.message, reminder_call=True,
                              intention_id=event.to_id)
            pass
        elif event.type == 'reminder_out':
            if event.status == 'intention':
                # 6.7
                intention_for_needy(call.message, reminder_call=True,
                                    intention_id=event.to_id)
            elif event.status == 'obligation':
                # 6.3
                obligation_for_needy(call.message, reminder_call=True,
                                     intention_id=event.to_id)
        else:
            global_menu(call.message)
    else:
        global_menu(call.message)
    return


@bot.message_handler(func=lambda message: True, content_types=['text'])
def menu(message):
    bot.delete_message(message.chat.id, message.message_id)
    global_check(message)
    status_check(message)
    configuration_check(message)


#    transactions_check(message)
#    members_check(message)		


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if config.DEBUG:
    bot.remove_webhook()
    bot.polling(none_stop=True)
else:
    from web_hook import run_with_web_hooks

    app = web.Application()
    run_with_web_hooks(app=app, bot=bot)
