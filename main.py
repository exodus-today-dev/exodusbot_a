#!/usr/bin/python

from datetime import timedelta

import telebot
from aiohttp import web
from telebot import types

from events import obligation_sended_notice
from models import *
from status_codes import *
from symbols import *

bot = telebot.TeleBot(config.API_TOKEN)

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
def global_menu(message, dont_show_status=True):
    """2.0"""
    bot.clear_step_handler(message)
    user = read_exodus_user(message.chat.id)
    if user is None:
        create_exodus_user(message.chat.id, message.chat.first_name, message.chat.last_name,
                           message.chat.username, status="green")
    user = read_exodus_user(message.chat.id)
    link = create_link(user.telegram_id, user.telegram_id)

    text_req = '\nРеквизиты:'
    requisites = read_requisites_user(message.chat.id)

    if requisites == []:
        text_req += '\nВы не указали реквизиты'
    else:
        n = 0
        for requisite in requisites:
            n += 1
            text_req += f'\n{n}. {requisite.name} - {requisite.value}'

    list_my_socium = get_my_socium(message.chat.id)

    if user is None:
        welcome(message)
    else:
        if user.status == "green":
            status = GREEN_BALL + f"\n\nВ моей сети: {len(list_my_socium)}"
        elif user.status == "orange":
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
            status = f'{ORANGE_BALL}\n({left_sum}{HEART_RED} / {right_sum}{HELP})\n' + f"\nВ моей сети: {len(list_my_socium)}\n"
            status += text_req
            status += "\n\nСсылка на обсуждение \U0001F4E2"
            if user.link == '' or user.link == None:
                status += "\n"  # ссылка на обсуждение
            else:
                status += f"\n{user.link}"  # ссылка на обсуждение # ссылка на обсуждение
            status += f"\n\nСсылка для помощи \U0001F4E9\n{link}"

        elif 'red' in user.status:
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
            status = f'{RED_BALL}\n({right_sum}{HELP})\n' + f"\nВ моей сети: {len(list_my_socium)}\n"
            status += text_req
            status += "\n\nСсылка на обсуждение \U0001F4E2"
            if user.link == '' or user.link == None:
                status += "\n"  # ссылка на обсуждение
            else:
                status += f"\n{user.link}"  # ссылка на обсуждение # ссылка на обсуждение
            status += f"\n\nСсылка для помощи \U0001F4E9\n{link}"
        else:
            orange_green_wizard(message)
            dont_show_status = True

    status_button = get_status(user.status)

    transactions_in = read_intention_for_user(to_id=message.chat.id, statuses=(1, 11, 12)).all()
    set_transactions_in = set()
    for i in transactions_in:
        set_transactions_in.add(i.from_id)

    transactions_out = read_intention_for_user(from_id=message.chat.id, statuses=(1, 11, 12)).all()
    set_transactions_from = set()
    for i in transactions_out:
        set_transactions_from.add(i.to_id)

    intentions_history_in = read_history_intention(to_id=message.chat.id)
    intentions_history_from = read_history_intention(from_id=message.chat.id)

    for row in intentions_history_in.all():
        set_transactions_in.add(row.from_id)
    list_users_in_count = len(set_transactions_in)

    for row in intentions_history_from.all():
        set_transactions_from.add(row.to_id)
    list_users_from_count = len(set_transactions_from)

    not_executed_from = read_event_to_id_status(message.chat.id, "obligation_sended")
    not_executed_to = read_event_from_id_status(message.chat.id, "obligation_sended")

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton(text=f'{SPIRAL_CALENDAR} Органайзер')
        btn3 = types.KeyboardButton(text=f'{MAN}{status_button} Профиль')
        btn4 = types.KeyboardButton(text=f'{PEOPLES} Участники')
        btn5 = types.KeyboardButton(text=f'{QUESTION} FAQ')
        btn6 = types.KeyboardButton(text=f'{SPEECH_BALOON} Чат поддержки')
        btn7 = types.KeyboardButton(text=f'{GLOBE} Помочь')
        btn8 = types.KeyboardButton(text='{} {} {} {}'.format(MAN, RIGHT_ARROW, list_users_from_count, PEOPLES))
        btn9 = types.KeyboardButton(text='{} {} {} {}'.format(list_users_in_count, PEOPLES, RIGHT_ARROW, MAN))
        #btn10 = types.KeyboardButton(text=f'{requisites_count} {SPEAK_HEAD} {HELP}')
        #btn10 = types.KeyboardButton(text=f'{SPEAK_HEAD} {len(not_executed)} {HANDSHAKE} {RIGHT_ARROW} {LIKE}')
        btn10 = types.KeyboardButton(text=f'{HANDSHAKE}{RIGHT_ARROW}{LIKE}\n\
    {len(not_executed_from)}{RIGHT_ARROW}{MAN}{RIGHT_ARROW}{len(not_executed_to)}')
        markup.row(btn3, btn9, btn5)
        markup.row(btn4, btn8, btn6)
        markup.row(btn2, btn10, btn7)

        if not dont_show_status:
            bot.send_message(message.chat.id, 'Ваш статус: {}'.format(status))
        bot.send_message(message.chat.id, 'Меню:', reply_markup=markup)

    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton(text=f'{SPIRAL_CALENDAR} Organiser')
        btn3 = types.KeyboardButton(text=f'{MAN}{status_button} Profile')
        btn4 = types.KeyboardButton(text=f'{PEOPLES} Participants')
        btn5 = types.KeyboardButton(text=f'{QUESTION} FAQ')
        btn6 = types.KeyboardButton(text=f'{SPEECH_BALOON} Support chat')
        btn7 = types.KeyboardButton(text=f'{GLOBE} Get help')
        btn8 = types.KeyboardButton(text='{} {} {} {}'.format(MAN, RIGHT_ARROW, list_users_from_count, PEOPLES))
        btn9 = types.KeyboardButton(text='{} {} {} {}'.format(list_users_in_count, PEOPLES, RIGHT_ARROW, MAN))
        # btn10 = types.KeyboardButton(text=f'{requisites_count} {SPEAK_HEAD} {HELP}')
        # btn10 = types.KeyboardButton(text=f'{SPEAK_HEAD} {len(not_executed)} {HANDSHAKE} {RIGHT_ARROW} {LIKE}')
        btn10 = types.KeyboardButton(text=f'{HANDSHAKE}{RIGHT_ARROW}{LIKE}\n\
        {len(not_executed_from)}{RIGHT_ARROW}{MAN}{RIGHT_ARROW}{len(not_executed_to)}')
        markup.row(btn3, btn9, btn5)
        markup.row(btn4, btn8, btn6)
        markup.row(btn2, btn10, btn7)

        if not dont_show_status:
            bot.send_message(message.chat.id, 'Your status: {}'.format(status))
        bot.send_message(message.chat.id, 'Menu:', reply_markup=markup)


def global_check(message):
    """2.0.1"""
    text = message.text
    # if text == 'Мой статус':
    #     status_menu(message)
    if 'Органайзер' in text or "Organiser" in text:
        transactions_menu(message)
    elif 'Профиль' in text or 'Profile' in text:
        configuration_menu(message)
    elif 'Участники' in text or 'Participants' in text:
        members_menu(message)
    elif 'FAQ' in text:
        instruction_menu(message)
    elif 'Support' in text or 'поддержки' in text:
        help_menu(message)
    elif 'Помочь' in text or 'Get' in text:
        call_people_menu(message)
    elif f'{MAN} {RIGHT_ARROW} 0' in text:
        bot.send_message(message.chat.id, f'В пользу других нет записей')
        return
    elif f'{MAN} {RIGHT_ARROW}' in text:
        members_list_in_network_menu(message, message.chat.id, 'out')
        return
    elif f'0 {PEOPLES} {RIGHT_ARROW}' in text:
        bot.send_message(message.chat.id, f'В Вашу пользу нет записей')
        return
    elif f'{PEOPLES} {RIGHT_ARROW}' in text:
        members_list_in_network_menu(message, message.chat.id, 'in')
        return
    # elif f'0 {SPEAK_HEAD} {HELP}' in text:
    #     bot.send_message(message.chat.id, 'Никто помощь пока не запрашивал')
    #     return
    elif f'{RIGHT_ARROW}{MAN}{RIGHT_ARROW}' in text:
        not_approve_intention_12(message)
        return
    # elif f'0 {SPEAK_HEAD} {HELP}' in text:
    #     bot.send_message(message.chat.id, 'Никто помощь пока не запрашивал')
    #     return
    # elif f'{SPEAK_HEAD} {HELP}' in text:
    #     show_help_requisites(message)
    #     return


# -------------------------------------------------------------------
def not_approve_intention_12(message):
    user_id = message.chat.id
    not_executed_from = read_event_to_id_status(user_id, "obligation_sended")
    not_executed_to = read_event_from_id_status(user_id, "obligation_sended")

    if not_executed_from != [] or not_executed_to != []:
        text = ''
        if not_executed_from != []:
            text += f"Пожалуйста, проверьте и подтвердите {HANDSHAKE}:\n"
            for row in not_executed_from:
                user_from = read_exodus_user(row.from_id)
                text += f'{row.event_id}. {user_from.first_name} {user_from.last_name} {row.current_payments}{HANDSHAKE} {RIGHT_ARROW} {LIKE}\n'

        if not_executed_to != []:
            text += f"\nПовторить уведомление об исполнении {HANDSHAKE}:\n"
            for row in not_executed_to:
                user_from = read_exodus_user(row.to_id)
                text += f'{row.event_id}. {user_from.first_name} {user_from.last_name} {row.current_payments}{HANDSHAKE} {RIGHT_ARROW} {LIKE}\n'

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn2 = types.KeyboardButton(text='Назад')
        markup.row(btn2)

        text += '\n\n' \
                   'Введите номер Участника, чтобы ' \
                   'посмотреть подробную информацию:'
        msg = bot.send_message(message.chat.id, text, reply_markup=markup)

        bot.register_next_step_handler(msg, check_not_approve_intention_12)
    else:
        text = f"Нет неподтвержденных {HANDSHAKE}"
        bot.send_message(message.chat.id, text)
        global_menu(message)


def check_not_approve_intention_12(message):
    text = message.text
    user_id = message.chat.id

    if text == 'Назад':
        global_menu(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        try:
            selected_id = int(text)
            event = read_event(selected_id)
            if user_id == event.to_id:
                obligation_sended_notice(selected_id)

            elif user_id == event.from_id:
                user_from_notif = read_exodus_user(user_id)
                bot_text_from = f"{user_from_notif.first_name} {user_from_notif.last_name} исполнил в вашу пользу {event.current_payments}{HANDSHAKE}.\n\
Пожалуйста, проверьте и подтвердите {HANDSHAKE}{RIGHT_ARROW}{LIKE}"
                bot.send_message(event.to_id, bot_text_from)

                user_to = read_exodus_user(event.to_id)
                bot.send_message(user_id, f"{user_to.first_name} {user_to.last_name} отправлено повторное уведомление об исполненном {HANDSHAKE}")

            global_menu(message)
        except:
            msg = bot.send_message(message.chat.id, exception_message(message))
            bot.register_next_step_handler(msg, not_approve_intention_12)
        return
    return


def call_people_menu(message):
    list_my_socium = list(get_my_socium(message.chat.id))
    list_my_socium.append(message.chat.id)
    len_my_socium = len(list_my_socium)

    keyboard_inline = []
    btn_inline = []

    # for i in range(len_my_socium):
    #     keyboard_inline.append(types.InlineKeyboardMarkup())
    #     btn_inline.append(types.InlineKeyboardButton("Позвать", callback_data="show_people_link_"+str(list_my_socium[i])))

    user_id = message.chat.id
    lang = read_user_language(user_id)
    if lang == 'ru':
        bot_text = 'В моей сети нуждаются в помощи:'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text='Назад')
    else:
        bot_text = 'My network needs help:'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text='Back')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    for i, id_help in enumerate(list_my_socium):
        user = read_exodus_user(id_help)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        keyboard_inline.append(types.InlineKeyboardMarkup())
        if lang == 'ru':
            btn_inline.append(types.InlineKeyboardButton(f"Сгенерировать ссылку для {user.first_name}",
                                                         callback_data="show_people_link_" + str(id_help)))
        else:
            btn_inline.append(types.InlineKeyboardButton(f"Generate a link for {user.first_name}",
                                                         callback_data="show_people_link_" + str(id_help)))

        status = user.status
        if status == "orange":
            string_name = f'\n<a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            string_name = f'\n<a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP}'
        else:
            continue

        keyboard_inline[i].add(btn_inline[i])

        bot.send_message(message.chat.id, string_name, parse_mode="html", disable_web_page_preview=True,
                         reply_markup=keyboard_inline[i])

    bot.register_next_step_handler(msg, show_people_link)


def show_people_link(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if 'Назад' in text or 'Back' in text:
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, global_menu)
        return
    return


def help_menu(message):
    help_text = "Узнать подробнее о системе Эксодус можно, присоединившись к нашему каналу https://t.me/Exodus_canal_1\n\n\
Вы можете сообщить про неясности или ошибки, возникающие в ходе освоения и доработки бота: https://t.me/Exodus_canal_1/4"
    bot.send_message(message.chat.id, help_text)


def instruction_menu(message, text=START_TEXT):
    # text_instruction = TEXT_INSTRUCTIONS
    # bot.send_message(message.chat.id, text_instruction, parse_mode="Markdown")
    # bot_text = 'Настройки:'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton(text='Про бота')
    btn3 = types.KeyboardButton(text='Условные обозначения')
    btn2 = types.KeyboardButton(text='Описание меню')
    btn4 = types.KeyboardButton(text='Как начать пользоваться')
    btn5 = types.KeyboardButton(text='Возможные кейсы')
    btn6 = types.KeyboardButton(text='Главное меню')

    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)

    bot_text = text
    msg = bot.send_message(message.chat.id, bot_text, parse_mode="markdown", reply_markup=markup)
    # with open('./static_files/test_03d.mp4',"rb") as misc:
    #     f=misc.read()
    # bot.send_video(message.chat.id, f)
    bot.register_next_step_handler(msg, check_instruction_menu)


def check_instruction_menu(message):
    text = message.text
    if text == 'Про бота':
        text = TEXT_ABOUT
        instruction_menu(message, text)
        return
    elif text == 'Условные обозначения':
        text = TEXT_CONVENTION
        instruction_menu(message, text)
        return
    elif text == 'Описание меню':
        text = TEXT_MENU
        instruction_menu(message, text)
        return
    elif text == 'Как начать пользоваться':
        text = TEXT_HOW_START
        instruction_menu(message, text)
        return
    elif text == 'Возможные кейсы':
        text = TEXT_CASE
        instruction_menu(message, text)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return


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


def configuration_menu(message, text=None):
    """2.3-3"""
    # user = read_exodus_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    user = read_exodus_user(telegram_id=message.chat.id)
    status = get_status(user.status)

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text=f'{status} Статус')
        btn3 = types.KeyboardButton(text=f'{CREDIT_CARD} Реквизиты')
        btn2 = types.KeyboardButton(text=f'{SPEECH_BALOON} Изменить ссылку на чат')
        btn4 = types.KeyboardButton(text='Главное меню')
        btn5 = types.KeyboardButton(text=f'{FOOTPRINTS} Выйти из бота')
        btn6 = types.KeyboardButton(text=f'Изменить язык')
    else:
        btn1 = types.KeyboardButton(text=f'{status} Status')
        btn3 = types.KeyboardButton(text=f'{CREDIT_CARD} Requisites')
        btn2 = types.KeyboardButton(text=f'{SPEECH_BALOON} Change the chat link')
        btn4 = types.KeyboardButton(text='Global menu')
        btn5 = types.KeyboardButton(text=f'{FOOTPRINTS} Log out of the bot')
        btn6 = types.KeyboardButton(text=f'Change language')

    markup.row(btn1, btn2, btn3)
    markup.row(btn5, btn6, btn4)

    if text:
        bot_text = text
    else:
        bot_text = generate_user_info_text(user)
    msg = bot.send_message(message.chat.id, bot_text, parse_mode="html", reply_markup=markup)
    bot.register_next_step_handler(msg, configuration_check)


def configuration_check(message):
    """3"""
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    text = message.text

    if 'Статус' in text or 'Status' in text:
        status_menu(message)
        return
    elif 'Реквизиты' in text or 'Requisites' in text:
        requisites_wizard(message)
        return
    elif 'Изменить ссылку' in text or 'Change the chat link' in text:
        edit_link_menu(message)
        return
    elif text == 'Настройки уведомлений':
        bot.send_message(message.chat.id, 'Настройки уведомлений')  # TODO
        global_menu(message)
        return
    elif 'Главное меню' in text or 'Global menu' in text:
        global_menu(message)
        return
    elif "Выйти" in text or 'Log out' in text:
        # quit_user_from_exodus(message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text='Да, удалить профиль')
        btn2 = types.KeyboardButton(text='Нет, я остаюсь')
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, 'Вы собираетесь выйти из бота и удалить свой профиль?',
                               reply_markup=markup)  # TODO
        bot.register_next_step_handler(msg, check_quit_bot)
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
    elif "Изменить язык" in text:
        update_user_language(message.chat.id, "en")
        configuration_menu(message, text='Change language to english!')
        return
    elif "Change" in text:
        update_user_language(message.chat.id, "ru")
        configuration_menu(message, text='Вы изменили язык на русский!')
        return
    elif "/start" in text:
        welcome_base(message)
        return


def check_quit_bot(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    my_socium = get_my_socium(message.chat.id)
    if "Да" in text:
        user = read_exodus_user(message.chat.id)
        first_name = user.first_name
        last_name = user.last_name
        quit_user_from_exodus(message.chat.id)
        # удаляем клавиатуру и остаемся в том же меню
        bot.send_message(message.chat.id, 'Вы удалили свой профиль.', reply_markup=types.ReplyKeyboardRemove())
        for id in my_socium:
            bot.send_message(id, '{} {} удалил свой профиль.'.format(first_name, last_name))
        # global_menu(message)
        return
    elif "Нет" in text:
        bot.send_message(message.chat.id, 'Спасибо, что остаетесь с нами!')
        configuration_menu(message)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, configuration_menu)


def edit_link_menu(message):
    user_id = message.chat.id
    user = read_exodus_user(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lang = read_user_language(user_id)
    if lang == 'ru':
        btn1 = types.KeyboardButton(text='Назад')
        markup.row(btn1)
        if user.link is None or user.link == '':
            link = 'не задана'
        else:
            link = user.link
        bot_text = 'Текущая ссылка: {}\nВведите новую ссылку на чат'.format(link)
    else:
        btn1 = types.KeyboardButton(text='Back')
        markup.row(btn1)
        if user.link is None or user.link == '':
            link = 'not set'
        else:
            link = user.link
        bot_text = 'The current reference is: {}\nInsert a new link to the chat'.format(link)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_link_check)


def edit_link_check(message):
    link = message.text
    user_id = message.chat.id
    lang = read_user_language(user_id)

    if link == 'Назад' or 'Back' in link:
        configuration_menu(message)
        return

    if lang == 'ru':
        bot_text = 'Ваша новая ссылка на чат:\n{}'.format(link)
    else:
        bot_text = 'Your new link to the chat:\n{}'.format(link)

    update_exodus_user(user_id, link=link)
    bot.send_message(user_id, bot_text)
    configuration_menu(message)


def requisites_wizard(message):
    user_id = message.chat.id

    lang = read_user_language(user_id)

    requisites = read_requisites_user(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    tmp_list = []

    if requisites != []:
        for requisite in requisites:
            if requisite.is_default:
                tmp_list.append(requisite.name + (' (по умолчанию)' if lang == "ru" else ' (is default)'))
            else:
                tmp_list.append(requisite.name)
        for word in tmp_list:
            btn = types.KeyboardButton(word)
            markup.row(btn)

    if lang == "ru":
        btn3 = types.KeyboardButton('Добавить реквизиты')
        btn4 = types.KeyboardButton('Назад')
        markup.row(btn3, btn4)
        msg = bot.send_message(user_id, 'Выберите реквизиты для редактирования:', reply_markup=markup)
    else:
        btn3 = types.KeyboardButton('Add requisites')
        btn4 = types.KeyboardButton('Back')
        markup.row(btn3, btn4)
        msg = bot.send_message(user_id, 'Select the requisites to edit:', reply_markup=markup)

    bot.register_next_step_handler(msg, requisites_wizard_check)


def requisites_wizard_check(message):
    user_id = message.chat.id
    bot.delete_message(user_id, message.message_id)
    text = message.text

    requisites = read_requisites_user(user_id)
    tmp_list = []
    if requisites != []:
        lang = read_user_language(message.chat.id)
        for requisite in requisites:
            if requisite.is_default:
                tmp_list.append(requisite.name + (' (по умолчанию)' if lang == "ru" else ' (is default)'))
            else:
                tmp_list.append(requisite.name)
    if text in tmp_list:
        select_requisite(message)
        return
    elif text == 'Add requisites':
        add_requisite_name(message)
        return
    elif text == 'Назад' or 'Back' in text:
        configuration_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(user_id, exception_message(message))
        bot.register_next_step_handler(msg, requisites_wizard_check)
        return


def select_requisite(message):
    text = message.text

    if text.find('по умолчанию') > -1 or text.find('is default') > -1 :
        bot.send_message(message.chat.id, 'Реквизиты по умолчанию:')
        text = text[:-15]
    requisite = read_requisites_name(message.chat.id, text)
    text_bot = f"Название: {requisite.name}\n\
Значение: {requisite.value}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Редактировать данные')
    btn2 = types.KeyboardButton(text='Сделать реквизитами по умолчанию')
    btn3 = types.KeyboardButton(text='Удалить')
    btn4 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
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
    elif text == 'Назад' or 'Back' in text:
        requisites_wizard(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, select_requisite_check)
        return
    return


def delete_requisite(message, requisite):
    bot_text = f"вы собираетесь удалить реквизиты:\n\
\n\
Название: {requisite.name}\n\
Значение: {requisite.value}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
        requisites_wizard(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, delete_requisite_check, requisite)
        return
    return


def add_requisite_name(message, edit_id=0):
    bot_text = 'Введите название реквизита (например "Карта Сбербанка", "Счет в SKB" или "PayPal")'
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, add_requisite_value, edit_id)
    return


def add_requisite_value(message, edit_id=0):
    requisite_name = message.text
    bot_text = 'Введите только номер счета, карты или идентификатор (чтобы его легче было скопировать)'
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, pre_save_requisite, requisite_name, edit_id)
    return


def pre_save_requisite(message, requisite_name, edit_id=0):
    requisite_value = message.text
    bot_text = f'Название: {requisite_name}\n\
Значение: {requisite_value}\n\
Данные введены верно?'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, pre_save_requisite_check)
        return
    return


def transactions_menu(message):
    """2.4"""
    user_id = message.chat.id
    user = read_exodus_user(message.chat.id)

    intention = read_intention(from_id=user_id, status=1)
    my_intent = 0.0
    my_intent_count = 0
    if intention is not None:
        my_intent_count = intention.count()
        for pay in intention:
            my_intent = my_intent + pay.payment

    intention = read_intention(from_id=user_id, status=11)
    my_obligation = 0.0
    my_obligation_count = 0
    if intention is not None:
        my_obligation_count = intention.count()
        for pay in intention:
            my_obligation = my_obligation + pay.payment

    intention = read_intention(to_id=user_id, status=1)
    me_intent = 0.0
    me_intent_count = 0
    if intention is not None:
        me_intent_count = intention.count()
        for pay in intention:
            me_intent = me_intent + pay.payment

    intention = read_intention(to_id=user_id, status=11)
    me_obligation = 0.0
    me_obligation_count = 0
    if intention is not None:
        me_obligation_count = intention.count()
        for pay in intention:
            me_obligation = me_obligation + pay.payment

    status = get_status(user.status)
    bot_text = f"Органайзер {status}"
    #     bot_text = f"Статус: {status}\n\
    # \n\
    # {HEART_RED}: \n\
    # {PLUS}: {me_intent} {user.currency}\n\
    # {MINUS}: {my_intent} {user.currency}\n\
    # \n\
    # {HANDSHAKE}: \n\
    # {PLUS}: {me_obligation} {user.currency}\n\
    # {MINUS}: {my_obligation} {user.currency}\n"

    history_intention_from = read_history_intention(from_id=user_id)
    history_intention_to = read_history_intention(to_id=user_id)

    if history_intention_from is not None:
        from_count = history_intention_from.count()
        sum_from = 0
        for intention in history_intention_from:
            sum_from += intention.payment
    else:
        from_count = 0
        sum_from = 0

    if history_intention_to is not None:
        to_count = history_intention_to.count()
        sum_to = 0
        for intention in history_intention_to:
            sum_to += intention.payment
    else:
        to_count = 0
        sum_to = 0

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(
        text=f'{me_intent_count}{HEART_RED} / {me_obligation_count}{HANDSHAKE} {RIGHT_ARROW} {MAN}')
    btn2 = types.KeyboardButton(
        text=f'{MAN} {RIGHT_ARROW} {my_intent_count}{HEART_RED} / {my_obligation_count}{HANDSHAKE}')
    #    btn3 = types.KeyboardButton(text='За всё время')
    # btn1 = types.KeyboardButton(text=f'{HEART_RED}{MAN}{RIGHT_ARROW}{my_intent_count}{PEOPLES}')
    # btn2 = types.KeyboardButton(text=f'{HEART_RED}{me_intent_count}{PEOPLES}{RIGHT_ARROW}{MAN}')
    # btn3 = types.KeyboardButton(text=f'{HANDSHAKE}{MAN}{RIGHT_ARROW}{my_obligation_count}{PEOPLES}')
    # btn4 = types.KeyboardButton(text=f'{HANDSHAKE}{me_obligation_count}{PEOPLES}{RIGHT_ARROW}{MAN}')
    btn5 = types.KeyboardButton(
        text=f'{to_count}/{sum_to}{LIKE}{RIGHT_ARROW}{MAN}{RIGHT_ARROW}{from_count}/{sum_from}{LIKE}')

    lang = read_user_language(message.chat.id)
    if lang =="ru":
        btn6 = types.KeyboardButton(text='Главное меню')
    else:
        btn6 = types.KeyboardButton(text='Global menu')

    markup.row(btn1, btn2)
    markup.row(btn5, btn6)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, transactions_check)


def transactions_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if f'{RIGHT_ARROW} {MAN}' in text:
        for_my_wizard(message)
        return
    elif f'{MAN} {RIGHT_ARROW}' in text:
        for_other_wizard(message)
        return
    # elif text == 'За всё время':
    #     for_all_time_wizard(message)
    #     return
    # elif text == 'Не исполненные':
    #     not_executed_wizard(message)
    #     return
    elif f'{LIKE}' in text:
        history_intention(message)
        return
    elif 'Global menu' in text or 'Главное меню'in text:
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        bot.send_message(message.chat.id, exception_message(message))
        global_menu(message)
        return


def history_intention(message):
    user_id = message.chat.id
    history_intention_from = read_history_intention(from_id=user_id)
    history_intention_to = read_history_intention(to_id=user_id)

    if history_intention_from.count() != 0:
        # from_count = history_intention_from.count()
        text_from = ''
        for intention in history_intention_from:
            user_from = read_exodus_user(intention.to_id)
            text_from += f'{intention.create_date.date().strftime("%d-%m-%Y")}     {intention.payment}{LIKE} вы {RIGHT_ARROW} {user_from.first_name} {user_from.last_name}\n'
    else:
        text_from = 'За все время исполнили вы - 0'

    if history_intention_to.count() != 0:
        # to_count = history_intention_to.count()
        text_to = ''
        for intention in history_intention_to:
            user_to = read_exodus_user(intention.from_id)
            text_to += f'{intention.create_date.date().strftime("%d-%m-%Y")}     {intention.payment}{LIKE} {user_to.first_name} {user_to.last_name} {RIGHT_ARROW} вам\n'
    else:
        text_to = 'За все время исполнили в вашу пользу - 0'

    bot_text = f'Ваша история исполненных обязательств:\n\
{text_to}\n\n\
{text_from}'
    bot.send_message(message.chat.id, bot_text)
    transactions_menu(message)
    return


def members_menu(message, meta_txt=None):
    """2.5"""

    user_id = message.chat.id
    len_my_socium = len(get_my_socium(user_id))
    user = read_exodus_user(user_id)

    lang = read_user_language(user_id)

    ref = user.ref
    if ref != '':
        referal = read_exodus_user(user.ref)
        ref = '{} {}'.format(referal.first_name, referal.last_name)
    else:
        ref = ''

    # transactions_in_count = read_intention_for_user(to_id=message.chat.id, statuses=(1, 11, 12)).count()
    # transactions_out_count = read_intention_for_user(from_id=message.chat.id, statuses=(1, 11, 12)).count()
    # requisites_count = get_requisites_count(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton(text='Мой профиль')
    # btn2 = types.KeyboardButton(text='{} ({})'.format(PLUS, transactions_in_count))
    # btn3 = types.KeyboardButton(text='{} ({})'.format(MINUS, transactions_out_count))
    # btn4 = types.KeyboardButton(text='Запросы помощи({})'.format(requisites_count))
    if lang == "ru":
        btn5 = types.KeyboardButton(text='Главное меню')
        btn6 = types.KeyboardButton(text=f'Моя сеть {PEOPLES} {len_my_socium}')
        btn7 = types.KeyboardButton(text='Расширить сеть')
        bot_text = "Участники:"
    else:
        btn5 = types.KeyboardButton(text='Global menu')
        btn6 = types.KeyboardButton(text=f'My network {PEOPLES} {len_my_socium}')
        btn7 = types.KeyboardButton(text='Expand your network')
        bot_text = "Participants:"
    markup.row(btn6, btn7, btn5)

    # currency = user.currency
    # intentions_out_sum = sum_out_intentions(user_id)
    # intentions_in_sum = sum_in_intentions(user_id)
    # obligations_in_sum = sum_in_obligations(user_id)
    # executed_in_sum = sum_in_executed(user_id)
    # obligations_out_sum = sum_out_obligations(user_id)
    # executed_out_sum = sum_out_executed(user_id)

    # transactions_in_count = count_in_transactions(user_id)
    # transactions_out_count = count_out_transactions(user_id)

    # bot_text = 'Я в сети Эксодус с {data}\n' \
    #            'Меня пригласил: {ref}\n' \
    #            '\n' \
    #            '{PLUS} ({tr_in}):\n' \
    #            '  {HEART_RED}: {int_in} {currency}\n' \
    #            '  {HANDSHAKE}: {obl_in} {currency}\n' \
    #            '  Исполнено: {exe_in} {currency}\n' \
    #            '\n' \
    #            '{MINUS} ({tr_out}):\n' \
    #            '  {HEART_RED}: {int_out} {currency}\n' \
    #            '  {HANDSHAKE}: {obl_out} {currency}\n' \
    #            '  Исполнено: {exe_out} {currency}'.format(
    #     data=user.create_date.strftime("%d %B %Y"),
    #     ref=ref, currency=currency, int_in=intentions_in_sum,
    #     obl_in=obligations_in_sum, exe_in=executed_in_sum,
    #     int_out=intentions_out_sum, obl_out=obligations_out_sum,
    #     exe_out=executed_out_sum, tr_in=transactions_in_count,
    #     tr_out=transactions_out_count, HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE,
    #     PLUS=PLUS, MINUS=MINUS)

    if meta_txt is None:
        msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    else:
        msg = bot.send_message(message.chat.id, text=meta_txt, reply_markup=markup)
    bot.register_next_step_handler(msg, members_check)
    return


# new # >>>

def check_intentions_member_id(from_user, to_user):
    flag_in = False
    intentions = read_intention_for_user(to_id=to_user, statuses=(1, 11, 12, 13)).all()
    for row in intentions:
        if row.from_id == from_user:
            flag_in = True
            break
    return flag_in


def print_list_check_intentions_member_id(message, member_id):
    intentions = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12, 13))
    user = read_exodus_user(member_id)
    string_name = f'{PEOPLES} {RIGHT_ARROW} {user.first_name}\n'

    for row in intentions.all():
        user = read_exodus_user(row.from_id)

        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        status = user.status
        if status == 'green':
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {GREEN_BALL}'
        elif status == "orange":
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            d0 = user.start_date
            d1 = date.today()
            delta = d1 - d0
            days_end = user.days - delta.days
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP} / {days_end} дней'
        if row.status == 1:
            string_name += f' {RIGHT_ARROW} {row.payment} {HEART_RED}'
        elif row.status == 11 or row.status == 12:
            string_name += f' {RIGHT_ARROW} {row.payment} {HANDSHAKE}'
        elif row.status == 13:
            string_name += f' {RIGHT_ARROW} {row.payment} {LIKE}'

    if len(string_name) < 4000:
        bot.send_message(message.chat.id, string_name, parse_mode='html')

    return


def print_members_list_in_network(message, member_id, direction):
    # """ 5.2 """

    # alert #empty.check

    intentions = None

    if direction == 'in':
        # intentions = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12)).distinct("from_id")
        intentions = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12))
        intentions_history = read_history_intention(to_id=member_id)
        user = read_exodus_user(member_id)
        string_name = f'{PEOPLES} {RIGHT_ARROW} {user.first_name}\n'

    elif direction == 'out':
        # intentions = read_intention_for_user(from_id=member_id, statuses=(1, 11, 12)).distinct("to_id")
        intentions = read_intention_for_user(from_id=member_id, statuses=(1, 11, 12))
        intentions_history = read_history_intention(from_id=member_id)
        user = read_exodus_user(member_id)
        string_name = f'{user.first_name} {RIGHT_ARROW} {PEOPLES}\n'

    list_users = set()

    for row in intentions.all():

        if direction == 'in':
            list_users.add(row.from_id)
        elif direction == 'out':
            list_users.add(row.to_id)

    for row in intentions_history.all():

        if direction == 'in':
            list_users.add(row.from_id)
        elif direction == 'out':
            list_users.add(row.to_id)

    for row in list_users:

        user = read_exodus_user(row)

        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        status = user.status
        if status == 'green':
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {GREEN_BALL}'
        elif status == "orange":
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            d0 = user.start_date
            d1 = date.today()
            delta = d1 - d0
            days_end = user.days - delta.days
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP} / {days_end} дней'

    # сообщение в телеграмме не может быть длиннее 4096 символов. 14 юзеров - это 400 символов.
    # нужно привязать пагинацию
    if len(string_name) < 4000:
        bot.send_message(message.chat.id, string_name, parse_mode='html')

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

    # to_collect = float(user.max_payments) - \
    #              float(sum_in_obligations(user.telegram_id)) - \
    #              float(sum_in_intentions(user.telegram_id))
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12))
    # already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    to_collect_text = '  сколько ещё нужно собрать: {}'.format(right_sum)

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
                        '{PLUS}({tr_in}):\n' \
                        '  {HEART_RED}: {int_in} {currency}\n' \
                        '  {HANDSHAKE}: {obl_in} {currency}\n' \
                        '  Исполнено: {exe_in} {currency}\n' \
                        '\n' \
                        '{MINUS} ({tr_out}):\n' \
                        '  {HEART_RED}: {int_out} {currency}\n' \
                        '  {HANDSHAKE}: {obl_out} {currency}\n' \
                        '  Исполнено: {exe_out} {currency}'.format(
        data=data.strftime("%d %B %Y"), ref=ref,
        first_name=first_name, last_name=last_name,
        status=status, currency=currency, int_in=intentions_in_sum,
        obl_in=obligations_in_sum, exe_in=executed_in_sum,
        int_out=intentions_out_sum, obl_out=obligations_out_sum,
        exe_out=executed_out_sum, tr_in=transactions_in_count,
        tr_out=transactions_out_count, HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE,
        PLUS=PLUS, MINUS=MINUS)

    return user_info_preview


def generate_user_info_text(user, self_id=''):
    """ 5.2 """

    # ref = user.ref
    # if ref != '':
    #     referal = read_exodus_user(user.ref)
    #     ref = '{} {}'.format(referal.first_name, referal.last_name)
    # else:
    #     ref = ''
    #
    # data = user.create_date
    # first_name = user.first_name
    # last_name = user.last_name
    # status = get_status(user.status)
    # currency = user.currency
    #
    # intentions_out_sum = sum_out_intentions(user.telegram_id)
    # intentions_in_sum = sum_in_intentions(user.telegram_id)
    # obligations_in_sum = sum_in_obligations(user.telegram_id)
    # executed_in_sum = sum_in_executed(user.telegram_id)
    # obligations_out_sum = sum_out_obligations(user.telegram_id)
    # executed_out_sum = sum_out_executed(user.telegram_id)
    #
    # transactions_in_count = count_in_transactions(user.telegram_id)
    # transactions_out_count = count_out_transactions(user.telegram_id)
    #
    # user_info_text = 'В сети Эксодус с {data}\n' \
    #                  'Пригласил: {ref}\n' \
    #                  'Со мной в круге:\n' \
    #                  '\n' \
    #                  'Имя участника: {first_name} {last_name}\n' \
    #                  'Статус: {status}\n' \
    #                  '\n'.format(data=data.strftime("%d %B %Y"), ref=ref,
    #                              first_name=first_name, last_name=last_name,
    #                              status=status)
    #
    # if user.status != 'green':
    #     status_info_text = generate_status_info_text(user)
    #     user_info_text += status_info_text + '\n'
    #
    # if in_my_circle_alpha(user.telegram_id, self_id):
    #     user_info_text += '{PLUS} ({tr_in}):\n' \
    #                       '  {HEART_RED}: {int_in} {currency}\n' \
    #                       '  {HANDSHAKE}: {obl_in} {currency}\n' \
    #                       '  Исполнено: {exe_in} {currency}\n' \
    #                       '\n' \
    #                       '{MINUS} ({tr_out}):\n' \
    #                       '  {HEART_RED}: {int_out} {currency}\n' \
    #                       '  {HANDSHAKE}: {obl_out} {currency}\n' \
    #                       '  Исполнено: {exe_out} {currency}'.format(
    #         HEART_RED=HEART_RED, HANDSHAKE=HANDSHAKE,
    #         currency=currency, int_in=intentions_in_sum,
    #         obl_in=obligations_in_sum, exe_in=executed_in_sum,
    #         int_out=intentions_out_sum, obl_out=obligations_out_sum,
    #         exe_out=executed_out_sum, tr_in=transactions_in_count,
    #         tr_out=transactions_out_count, PLUS=PLUS, MINUS=MINUS)
    #
    # else:
    #     user_info_text += f'Информация о {HEART_RED} и {HANDSHAKE} доступна ' \
    #                       'только для участников в моей сети.'

    ref = user.ref
    if ref != '':
        referal = read_exodus_user(user.ref)
        ref = '{} {}'.format(referal.first_name, referal.last_name)
    else:
        ref = ''

    data = user.create_date
    first_name = user.first_name
    last_name = user.last_name
    status = get_status(user.status)
    currency = user.currency
    telegram_id = user.telegram_id

    intentions_out_sum = sum_out_intentions(telegram_id)
    intentions_in_sum = sum_in_intentions(telegram_id)
    obligations_in_sum = sum_in_obligations(telegram_id)
    executed_in_sum = sum_in_executed(telegram_id)
    obligations_out_sum = sum_out_obligations(telegram_id)
    executed_out_sum = sum_out_executed(telegram_id)

    transactions_in_count = count_in_transactions(telegram_id)
    transactions_out_count = count_out_transactions(telegram_id)

    link = create_link(telegram_id, telegram_id)
    requisites = read_requisites_user(telegram_id)
    if requisites == []:
        req_name = 'не указан'
        req_value = 'не указан'
    else:
        req_name = requisites[0].name
        req_value = requisites[0].value

    already_payments_oblig = get_intention_sum(telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    lang = read_user_language(telegram_id)
    if lang == "ru":
        if user.link == '' or user.link == None:
            user_info_text = f'{first_name} {last_name} {status} / {GLOBE} <a href="{link}">Позвать</a> / {CREDIT_CARD} {req_name} <a href="{req_value}">{req_value}</a>\n'
        else:
            user_info_text = f'{first_name} {last_name} {status} / {GLOBE} <a href="{link}">Позвать</a> / {SPEECH_BALOON} {user.link} / {CREDIT_CARD} {req_name} <a href="{req_value}">{req_value}</a>\n'
    else:
        if user.link == '' or user.link == None:
            user_info_text = f'{first_name} {last_name} {status} / {GLOBE} <a href="{link}">Get help</a> / {CREDIT_CARD} {req_name} <a href="{req_value}">{req_value}</a>\n'
        else:
            user_info_text = f'{first_name} {last_name} {status} / {GLOBE} <a href="{link}">Get help</a> / {SPEECH_BALOON} {user.link} / {CREDIT_CARD} {req_name} <a href="{req_value}">{req_value}</a>\n'

    if user.status == 'green':
        if user.link == '' or user.link == None:
            user_info_text = f'{first_name} {last_name} {status}\n'
        else:
            user_info_text = f'{first_name} {last_name} {status} / {SPEECH_BALOON} {user.link}\n'
        user_info_text += f'{MAN} {RIGHT_ARROW} {transactions_out_count} {PEOPLES}: {intentions_out_sum} {HEART_RED} / {obligations_out_sum} {HANDSHAKE}'

    elif user.status == 'orange':
        user_info_text += f'{transactions_in_count} {PEOPLES} {RIGHT_ARROW} {MAN} ({left_sum} {HEART_RED} / {right_sum} {HELP})\n'
        user_info_text += f'{MAN} {RIGHT_ARROW} {transactions_out_count} {PEOPLES}: {intentions_out_sum} {HEART_RED} / {obligations_out_sum} {HANDSHAKE}'

    elif 'red' in user.status:
        d0 = user.start_date
        d1 = date.today()
        delta = d1 - d0
        days_end = user.days - delta.days
        if lang == "ru":
            user_info_text += f'{transactions_in_count} {PEOPLES} {RIGHT_ARROW} {MAN} ({right_sum} {HELP} / {days_end} дней)\n'
        else:
            user_info_text += f'{transactions_in_count} {PEOPLES} {RIGHT_ARROW} {MAN} ({right_sum} {HELP} / {days_end} days)\n'

    return user_info_text


def members_list_in_network_menu(message, member_id, direction, g_menu=True):
    """ 5.2 """
    if (direction == "in") and (not g_menu) and check_intentions_member_id(message.chat.id, member_id):
        print_list_check_intentions_member_id(message, member_id)
    else:
        print_members_list_in_network(message, member_id, direction)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn2)

    bot_text = '\n' \
               'Введите номер Участника, чтобы ' \
               'посмотреть подробную информацию:'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, members_list_in_network_check,
                                   member_id, direction, g_menu)


def selected_member_action_menu(message, member_id):
    """ 5.2 """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    transactions_in = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12)).all()
    set_transactions_in = set()
    for i in transactions_in:
        set_transactions_in.add(i.from_id)

    transactions_out = read_intention_for_user(from_id=member_id, statuses=(1, 11, 12)).all()
    set_transactions_from = set()
    for i in transactions_out:
        set_transactions_from.add(i.to_id)

    intentions_history_in = read_history_intention(to_id=member_id)
    intentions_history_from = read_history_intention(from_id=member_id)

    for row in intentions_history_in.all():
        set_transactions_in.add(row.from_id)
    list_users_in_count = len(set_transactions_in)

    if check_intentions_member_id(message.chat.id, member_id):
        list_users_in_count = read_intention_for_user(to_id=member_id, statuses=(1, 11, 12, 13)).count()

    for row in intentions_history_from.all():
        set_transactions_from.add(row.to_id)
    list_users_from_count = len(set_transactions_from)

    user = read_exodus_user(member_id)
    first_name = user.first_name

    btn1 = types.KeyboardButton(text=f'{MAN} {first_name}')
    btn2 = types.KeyboardButton(text=f'{list_users_in_count} {PEOPLES} {RIGHT_ARROW} {first_name}')
    btn3 = types.KeyboardButton(text=f'{first_name} {RIGHT_ARROW} {list_users_from_count} {PEOPLES}')

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn4 = types.KeyboardButton(text='Главное меню')
        btn5 = types.KeyboardButton(text=f'Сеть {PEOPLES} {first_name}')
        btn6 = types.KeyboardButton(text=f'Помочь {first_name}')
        bot_text = '\nВыберите пункт меню'
    else:
        btn4 = types.KeyboardButton(text='Global menu')
        btn5 = types.KeyboardButton(text=f'Network {PEOPLES} {first_name}')
        btn6 = types.KeyboardButton(text=f'Help {first_name}')
        bot_text = '\nSelect menu item'

    markup.row(btn1, btn5, btn6)
    markup.row(btn3, btn2, btn4)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, selected_member_action_check,
                                   member_id)


def selected_member_action_check(message, member_id):  # bookmark
    """ 5.2 """
    text = message.text
    user = read_exodus_user(member_id)
    first_name = user.first_name

    if MAN in text:
        members_menu_profile_link(message, member_id, "selected_member_action_check")
        return
    elif f'{PEOPLES} {RIGHT_ARROW}' in text:
        members_list_in_network_menu(message, member_id, 'in', False)
        return
    elif f'{first_name} {RIGHT_ARROW}' in text:
        members_list_in_network_menu(message, member_id, 'out', False)
    elif text == 'Global menu' or 'Главное меню' in text:
        global_menu(message)
    elif 'Сеть' in text or 'Network' in text:
        show_other_socium(message, member_id)
    elif 'Помочь' in text or 'Help' in text:
        link = create_link(user.telegram_id, user.telegram_id)
        lang = read_user_language(message.chat.id)
        if lang == 'ru':
            bot_text = f"\n\nСсылка для помощи \U0001F4E9\n{link}"
        else:
            bot_text = f"\n\nLink for help \U0001F4E9\n{link}"
        bot.send_message(message.chat.id, bot_text)
        selected_member_action_menu(message, member_id)

    elif "/start" in text:
        welcome_base(message)

    else:
        bot.send_message(message.chat.id, exception_message(message))
        selected_member_action_menu(message, member_id)


def members_list_in_network_check(message, member_id, direction, g_menu):
    """ 5.2 """
    text = message.text

    # if text == 'Показать еще 10':  # bug # дважды печатает список
    #     print_members_list_in_network(message, member_id, direction)
    #     members_list_in_network_menu(message, member_id, direction)
    #     return

    if text == 'Назад':
        if g_menu:
            global_menu(message)
            return
        else:
            selected_member_action_menu(message, member_id)
            return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark

            # members_list = get_members_list(member_id, direction)
            # selected_id = int(text)
            # user = read_exodus_user(members_list[selected_id])
            # user_info_text = generate_user_info_text(user, message.chat.id)
            # bot.send_message(message.chat.id, user_info_text, parse_mode='html')
            # selected_member_action_menu(message, members_list[selected_id])

            selected_id = int(text)
            user = read_exodus_user_by_exodus_id(selected_id)
            telegram_id = user.telegram_id
            user_info_text = generate_user_info_text(user, message.chat.id)
            bot.send_message(message.chat.id, user_info_text, parse_mode='html')
            selected_member_action_menu(message, telegram_id)

        except:
            msg = bot.send_message(message.chat.id, exception_message(message))
            bot.register_next_step_handler(msg,
                                           members_list_in_network_check,
                                           member_id, direction, g_menu)

        return
    return


# new # <<<

def show_other_socium(message, user_id):
    # print(user_id)
    # bot.delete_message(message.chat.id, message.message_id)
    list_my_socium = get_my_socium(user_id)

    string_name = ''
    for id_help in list_my_socium:
        user = read_exodus_user(id_help)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        status = user.status
        if status == 'green':
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {GREEN_BALL}'
        elif status == "orange":
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            d0 = user.start_date
            d1 = date.today()
            delta = d1 - d0
            days_end = user.days - delta.days
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP} / {days_end} дней'

    bot_text = 'В сети участника:{}'.format(string_name) + '\n\n' \
                                                           'Введите номер Участника, чтобы ' \
                                                           'посмотреть подробную информацию:'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup, parse_mode="html",
                           disable_web_page_preview=True)
    bot.register_next_step_handler(msg, check_other_socium, user_id)


def check_other_socium(message, member_id):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)

    if 'Назад' in text or 'Back' in text:
        selected_member_action_menu(message, member_id)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        try:
            selected_id = int(text)
            user = read_exodus_user_by_exodus_id(selected_id)
            telegram_id = user.telegram_id

            list_my_socium = get_my_socium(member_id)
            if telegram_id in list_my_socium:
                user_info_text = generate_user_info_text(user, message.chat.id)
                bot.send_message(message.chat.id, user_info_text, parse_mode='html')
                selected_member_action_menu(message, telegram_id)
            else:
                bot.send_message(message.chat.id, "*Этого пользователя нет в вашей сети. Введите корректный номер*",
                                 parse_mode="Markdown")
                show_other_socium(message, member_id)
        except:
            bot.send_message(message.chat.id, "*Этого пользователя нет в вашей сети. Введите корректный номер*",
                             parse_mode="Markdown")
            show_other_socium(message, member_id)
        return


def show_my_socium(message):
    # bot.delete_message(message.chat.id, message.message_id)
    list_my_socium = get_my_socium(message.chat.id)

    string_name = ''
    list_exodus_id_my_socium = []
    for id_help in list_my_socium:
        user = read_exodus_user(id_help)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        status = user.status
        if status == 'green':
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {GREEN_BALL}'
        elif status == "orange":
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            d0 = user.start_date
            d1 = date.today()
            delta = d1 - d0
            days_end = user.days - delta.days
            string_name = string_name + f'\n{user.exodus_id}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP} / {days_end} дней'
        list_exodus_id_my_socium.append(user.exodus_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        bot_text = 'В моей сети:{}'.format(string_name) + '\n\n' \
                                                          'Введите номер Участника, чтобы ' \
                                                          'посмотреть подробную информацию:'
        btn1 = types.KeyboardButton(text='Назад')
    else:
        bot_text = 'In my network: {}'.format(string_name) + '\n\n' \
                                                                'Enter the Member number to ' \
                                                                'view detailed information:'
        btn1 = types.KeyboardButton(text='Back')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup, parse_mode="html",
                           disable_web_page_preview=True)
    bot.register_next_step_handler(msg, check_my_socium, list_exodus_id_my_socium)


def check_my_socium(message, list_exodus_id_my_socium):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if 'Назад' in text or 'Back' in text:
        members_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark

            selected_id = int(text)
            if selected_id not in list_exodus_id_my_socium:
                lang = read_user_language(message.chat.id)
                if lang == "ru":
                    bot.send_message(message.chat.id, "*Этого пользователя нет в вашей сети. Введите корректный номер*",
                                 parse_mode="Markdown")
                else:
                    bot.send_message(message.chat.id, "*This user is not on your network. Enter the correct number*",
                                 parse_mode="Markdown")
                show_my_socium(message)
            else:
                user = read_exodus_user_by_exodus_id(selected_id)
                telegram_id = user.telegram_id
                user_info_text = generate_user_info_text(user, message.chat.id)
                bot.send_message(message.chat.id, user_info_text, parse_mode='html')
                selected_member_action_menu(message, telegram_id)
        except:
            bot.send_message(message.chat.id, exception_message(message))
            show_my_socium(message)
        return


def expand_my_socium(message):
    list_my_socium = get_my_socium(message.chat.id)

    list_expand_socium = []

    # пробегаем мою сеть
    for id_my in list_my_socium:
        # для каждого из моей сети строим его сеть
        other_socium = get_my_socium(id_my)
        # пробегаем его сеть
        for id_other in other_socium:
            # если очередного юзера нет в моей сети
            if id_other not in list_my_socium:
                user = read_exodus_user(id_other)
                # если этому юзеру нужна помощь(оранжевый), то дабвляем в расширенный список сети
                if user.status == "orange":
                    list_expand_socium.append(id_other)

    list_expand_socium = set(list_expand_socium)
    list_expand_socium.discard(message.chat.id)

    lang = read_user_language(message.chat.id)

    if len(list_expand_socium) == 0:
        if lang == 'ru':
            meta_txt = "Нет новых участников"
        else:
            meta_txt = "No new members"
        members_menu(message, meta_txt=meta_txt)
        return
    else:
        string_name = ''
        for i, id_help in enumerate(list_expand_socium):
            user = read_exodus_user(id_help)
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

            string_name = string_name + '\n{}. {} {} {}  {}/{}'.format(i + 1, user.first_name, user.last_name,
                                                                       get_status(user.status), str(left_sum) + HEART_RED,
                                                                       str(right_sum) + HELP)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if lang == 'ru':
            bot_text = 'Расширение сети:{}'.format(string_name) + '\n\n' \
                                                                  'Введите номер Участника, чтобы ' \
                                                                  'посмотреть подробную информацию:'
            btn1 = types.KeyboardButton(text='Назад')

        else:
            bot_text = 'Network extension: {}'. format (string_name) + '\n\n' \
                                                                        'Enter the Member number to ' \
                                                                        'view detailed information:'
            btn1 = types.KeyboardButton(text='Back')

        markup.row(btn1)
        msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        bot.register_next_step_handler(msg, check_expand_my_socium, list_expand_socium)


def check_expand_my_socium(message, list_expand_socium):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)

    if 'Назад' in text or 'Back' in text:
        members_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        try:
            # bookmark #debug.bookmark #dev.bookmark
            members_list = list(list_expand_socium)
            selected_id = int(text) - 1

            user = read_exodus_user(members_list[selected_id])
            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
            # bot.delete_message(user_id, message.message_id)

            ring = read_rings_help(user.telegram_id)
            lang = read_user_language(message.chat.id)

            if ring is None:
                all_users = 0
            else:
                try:
                    all_users = len(set(ring.help_array_orange))
                except:
                    all_users = 0
            if lang == 'ru':
                bot_text = '{} Имя участника: {} {}\nСтатус: {}\n\U0001F4B0 {}/{} {}\nУже помогают: {}\n'.format(MAN,
                                                                                                                 user.first_name,
                                                                                                                 user.last_name,
                                                                                                                 ORANGE_BALL,
                                                                                                                 left_sum,
                                                                                                                 right_sum,
                                                                                                                 user.currency,
                                                                                                                 all_users)

                bot_text += "\nСсылка на обсуждение \U0001F4E2"
                if user.link == '' or user.link == None:
                    bot_text += "\n"  # ссылка на обсуждение
                else:
                    bot_text += f"\n{user.link}"  # ссылка на обсуждение # ссылка на обсуждение

                link = create_link(user.telegram_id, user.telegram_id)
                bot_text += f"\n\nСсылка для помощи \U0001F4E9\n{link}"
            else:
                bot_text = '{} Member name: {} {}\nStatus: {}\n\U0001F4B0 {}/{} {}\nAlready help: {}\n'.format(MAN,
                                                                                                                 user.first_name,
                                                                                                                 user.last_name,
                                                                                                                 ORANGE_BALL,
                                                                                                                 left_sum,
                                                                                                                 right_sum,
                                                                                                                 user.currency,
                                                                                                                 all_users)

                bot_text += "\nLink to discussion \U0001F4E2"
                if user.link == '' or user.link == None:
                    bot_text += "\n"  # ссылка на обсуждение
                else:
                    bot_text += f"\n{user.link}"  # ссылка на обсуждение # ссылка на обсуждение

                link = create_link(user.telegram_id, user.telegram_id)
                bot_text += f"\n\nLink for help \U0001F4E9\n{link}"

            # bot.send_message(user_id, bot_text)  # общий текст
            members_menu(message, meta_txt=bot_text)
        except:
            # msg = bot.send_message(message.chat.id, exception_message(message))
            members_menu(message, meta_txt=exception_message(message))
        return


def members_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    # if text == 'Мой профиль':
    #     members_menu_profile_link(message, message.chat.id)
    #     return
    # elif text == f'{PLUS} (0)':
    #     msg = bot.send_message(message.chat.id, f'В Вашу пользу нет записей')
    #     bot.register_next_step_handler(msg, members_check)
    #     return
    # elif f'{PLUS}' in text:
    #     members_list_in_network_menu(message, message.chat.id, 'in')
    #     return
    # elif text == f'{MINUS} (0)':
    #     msg = bot.send_message(message.chat.id, f'В пользу других нет записей')
    #     bot.register_next_step_handler(msg, members_check)
    #     return
    # elif f'{MINUS}' in text:
    #     members_list_in_network_menu(message, message.chat.id, 'out')
    #     return
    # elif 'Запросы помощи' in text:
    #     show_help_requisites(message)
    #     return
    if text == 'Главное меню' or text == "Global menu":
        global_menu(message)
        return

    elif 'Моя сеть' in text or 'My network' in text:
        show_my_socium(message)
        return

    elif 'Расширить сеть' in text or 'Expand your network' in text:
        expand_my_socium(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
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

    n = 0
    bot_text_int = ''
    if intentions is None:
        bot_text_int = ''
    else:
        for intent in intentions:
            n = n + 1
            user_to = read_exodus_user(telegram_id=intent.to_id)
            bot_text_int += '{n}. {first_name} {last_name} {status} {payment} {HEART_RED}\n'.format(
                n=intent.intention_id,
                first_name=user_to.first_name,
                last_name=user_to.last_name,
                status=get_status(user_to.status),
                payment=intent.payment,
                HEART_RED=HEART_RED)

    bot_text_obl = ''
    if obligations is None:
        bot_text_int = ''
    else:
        for obl in obligations:
            n = n + 1
            user_to = read_exodus_user(telegram_id=obl.to_id)
            bot_text_obl += '{n}. {first_name} {last_name} {status} {payment} {HANDSHAKE}\n'.format(n=obl.intention_id,
                                                                                                    first_name=user_to.first_name,
                                                                                                    last_name=user_to.last_name,
                                                                                                    status=get_status(
                                                                                                        user_to.status),
                                                                                                    payment=obl.payment,
                                                                                                    HANDSHAKE=HANDSHAKE)

    bot_text = f"Вами записано {intentions_count} {HEART_RED} и {obligations_count} {HANDSHAKE}:\n\
{bot_text_int}\n\n\
{bot_text_obl}\n\n\
Введите номер, чтобы посмотреть подробную информацию или изменить:"

    bot.clear_step_handler(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    #    markup.row(btn1,btn2)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, all_check_int_obl_minus)
    return


# новая проверка меню с твоими исходящими операциями
def all_check_int_obl_minus(message):
    number = message.text
    if number == 'Назад':
        transactions_menu(message)
        return
    if not number.isdigit():
        bot.send_message(message.chat.id, 'Номер должен быть в виде числа:')
        for_other_wizard(message)
        return
    intention = read_intention_by_id(intention_id=number)
    if intention is None or intention.status not in [1, 11]:
        bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HEART_RED} или {HANDSHAKE}:')
        for_other_wizard(message)
        return
    transaction[message.chat.id] = number
    if intention.status == 1:
        intention_for_needy(message, reminder_call=False, intention_id=None, show_back=True)
    elif intention.status == 11:
        obligation_for_needy(message, reminder_call=False, intention_id=None)
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
    elif text == 'Назад' or 'Back' in text:
        bot.clear_step_handler(message)
        transactions_menu(message)
        return

    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
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
def intention_for_needy(message, reminder_call, intention_id, show_back=False):
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=f'В {HANDSHAKE}')
    btn2 = types.KeyboardButton(text='Изменить')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    btn4 = types.KeyboardButton(text=f'Отменить {HEART_RED}')
    btn5 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1, btn2, btn4)
    if show_back:
        btn6 = types.KeyboardButton(text='Назад')
        markup.row(btn3, btn5, btn6)
    else:
        markup.row(btn3, btn5)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, intention_for_needy_check, intention_id)
    return


def intention_for_needy_check(message, intention_id):
    # 6.7
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == f'В {HANDSHAKE}':
        intention_to_obligation(message, intention_id)
        return
    elif text == 'Изменить':
        edit_intention(message)
        return
    elif text == 'Напомнить позже':
        remind_later(message, event_status='intention', reminder_type='reminder_out', intention_id=intention_id)
        global_menu(message)
        return
    elif text == f'Отменить {HEART_RED}':
        cancel_intention(message, intention_id)
        return
    elif 'Главное меню' in text:
        global_menu(message)
        return
    elif 'Назад' in text or 'Back' in text:
        for_other_wizard(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return

    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, global_menu)
    return


def intention_to_obligation(message, intention_id):
    #intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    user_from = read_exodus_user(telegram_id=message.chat.id)

    update_intention(intention_id, status=11)
    update_event_status_code(intention.event_id, NEW_OBLIGATION)

    # создаем событие для намерения на будущий месяц
    create_event(from_id=message.chat.id,
                 first_name=None,
                 last_name=None,
                 status='future_event',
                 type='future_event',
                 min_payments=None,
                 current_payments=intention.payment,
                 max_payments=None,
                 currency=None,
                 users=None,
                 to_id=intention.to_id,
                 reminder_date=datetime.now(),
                 sent=False,
                 status_code=FUTURE_EVENT)

    # отправка сообщения
    already_payments_oblig = get_intention_sum(user_to.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user_to.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user_to.max_payments)
    right_sum = user_to.max_payments - already_payments_oblig if user_to.max_payments - already_payments_oblig > 0 else 0
    status_to = get_status(user_to.status)
    ring = read_rings_help(user_to.telegram_id)

    if ring is None:
        users_count = 0
    else:
        try:
            users_count = len(set(ring.help_array_orange))
        except:
            users_count = 0

    #     bot_text = f"Вы перевели в {HANDSHAKE} свое {HEART_RED} помогать участнику {user_to.first_name} {user_to.last_name} на сумму: {intention.payment} {intention.currency}\n\
    # Когда участник {user_to.first_name} {user_to.last_name} решит что делать с Вашим {HANDSHAKE}, вы получите уведомление."

    bot_text = f"Вы {HEART_RED}  {RIGHT_ARROW}  {HANDSHAKE} {intention.payment}  {RIGHT_ARROW}  {user_to.first_name} {user_to.last_name}\n\
{user_to.first_name} {user_to.last_name} {status_to}\n\
({left_sum}{HEART_RED} / {right_sum}{HELP} {LEFT_ARROW} {users_count} {PEOPLES})\n\
Ждите уведомления."

    bot.send_message(message.chat.id, bot_text)

    # рассылка уведомлений моему кругу о том, что я начал кому то помогать, кроме того, кто запросил
    list_needy_id = get_my_socium(intention.to_id)
    list_needy_id.discard(message.chat.id)

    bot_text_for_all = f"{user_from.first_name} {user_from.last_name} перевел свое {HEART_RED} в {HANDSHAKE} участнику {user_to.first_name} {user_to.last_name} на сумму: {intention.payment} {intention.currency}\n\
{user_to.first_name} {user_to.last_name} {status_to}\n\
({left_sum}{HEART_RED} / {right_sum}{HELP} {LEFT_ARROW} {users_count} {PEOPLES})"

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
    # user = read_exodus_user(message.chat.id)

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
        global_menu(message)
    return


def edit_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text='Назад')
        bot_text = f"Ваше {HEART_RED} было на сумму {intention.payment}\n\
Введите новую сумму (только число) в валюте {intention.currency}"
    else:
        btn1 = types.KeyboardButton(text='Back')
        bot_text = f"Your {HEART_RED} was for the amount of {intention.payment}\n\
Enter a new amount (number only) in the currency {intention.currency}"

    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_intention_check)
    return


def edit_intention_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    intention_id = transaction[message.chat.id]
    payment = message.text
    if payment == 'Назад' or 'Back' in text:
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return
    if not is_digit(payment):
        lang = read_user_language(message.chat.id)
        if lang == "ru":
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['en'])
        bot.register_next_step_handler(msg, edit_intention_check)
        return
    update_intention(intention_id=intention_id, payment=payment)
    intention_for_needy(message, reminder_call=False, intention_id=None)
    return


def cancel_intention(message, intention_id):
    #intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Вы хотите отменить свое {HEART_RED} участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency}?"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Нет')
    btn2 = types.KeyboardButton(text='Да')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, cancel_intention_check, intention_id)
    return


def cancel_intention_check(message, intention_id):
    #intention_id = transaction[message.chat.id]
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

        # удаление из оранжевого статуса и всего круга
        delete_from_orange_help_array(intention.to_id, message.chat.id)
        delete_from_help_array_all(intention.to_id, message.chat.id)

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
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, global_menu)
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # btn1 = types.KeyboardButton(text='Другие реквизиты')  # TODO сделать и подвязать реквизиты
    btn2 = types.KeyboardButton(text='Да, я отправил деньги')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    # markup.row(btn1)
    markup.row(btn2, btn3)
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Да')
    btn2 = types.KeyboardButton(text='Нет')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, obligation_sent_confirm_check)
    return


def obligation_sent_confirm_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Да':
        obligation_sent_confirm_yes(message)
        return
    elif text == 'Нет':
        obligation_for_needy(message, reminder_call=False, intention_id=None)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, for_my_check)
    return


def obligation_sent_confirm_yes(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Спасибо!\n\
{user_to.first_name} {user_to.last_name} отправлено уведомление, что {intention.payment} {HANDSHAKE} исполнено."
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
        try:
            all_users = len(set(ring.help_array_all))
        except:
            all_users = 0
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

    user_from_notif = read_exodus_user(message.chat.id)
    bot_text_from = f"{user_from_notif.first_name} {user_from_notif.last_name} исполнил в вашу пользу {intention.payment}{HANDSHAKE}.\n\
Пожалуйста, проверьте и подтвердите {HANDSHAKE}{RIGHT_ARROW}{LIKE}"
    bot.send_message(user_to.telegram_id, bot_text_from)

    global_menu(message)
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

    bot_text_int = ''
    if intentions is None:
        bot_text_int = ''
    else:
        for intent in intentions:
            user = read_exodus_user(telegram_id=intent.from_id)
            bot_text_int += f"{intent.intention_id}. {user.first_name} {user.last_name} {intent.payment} {HEART_RED}\n"

    n = 0
    bot_text_obl = ''
    if obligations is None:
        bot_text_obl = ''
    else:
        for obl in obligations:
            n = n + 1
            user = read_exodus_user(telegram_id=obl.from_id)
            bot_text_obl += f"{obl.intention_id}. {user.first_name} {user.last_name} {obl.payment} {HANDSHAKE}\n"

    bot_text = f"В Вашу пользу {intentions_count} {HEART_RED} и {obligations_count} {HANDSHAKE}:\n\
{bot_text_int}\n\n\
{bot_text_obl}\n\n\
Введите номер, чтобы посмотреть подробную информацию или изменить:"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn2)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, all_check_int_obl_plus)

    return


# новый функционал меню плюса в кошельке
def all_check_int_obl_plus(message):
    number = message.text
    if number == 'Назад':
        transactions_menu(message)
        return
    if not number.isdigit():
        bot.send_message(message.chat.id, 'Номер должен быть в виде числа:')
        for_my_wizard(message)
        return
    intention = read_intention_by_id(intention_id=number)
    if intention is None or intention.status not in [1, 11]:
        bot.send_message(message.chat.id, f'Введённый номер не соовпадает с существующими {HEART_RED} или {HANDSHAKE}:')
        for_my_wizard(message)
        return
    transaction[message.chat.id] = number
    if intention.status == 1:
        user = read_exodus_user(telegram_id=intention.from_id)
        bot_text = f"{intention.create_date.strftime('%d %B %Y')}\n\
{user.first_name} {user.last_name}  {RIGHT_ARROW}  {HEART_RED} {intention.payment}"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text=f'Попросить {HEART_RED} {RIGHT_ARROW} {HANDSHAKE}')
        btn2 = types.KeyboardButton(text='Назад')
        btn3 = types.KeyboardButton(text='Главное меню')
        markup.row(btn1, btn2, btn3)
        msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        bot.register_next_step_handler(msg, new_check_intention_send, intention)
    elif intention.status == 11:
        for_me_obligation(message, reminder_call=False, intention_id=None)
    return


def new_check_intention_send(message, intention):
    text = message.text
    if text == 'Назад':
        transactions_menu(message)
        return
    elif 'Попросить' in text:
        to_id = intention.to_id
        from_id = intention.from_id
        user_to = read_exodus_user(to_id)
        bot.send_message(to_id, f'Отправлен запрос на {HEART_RED} {RIGHT_ARROW} {HANDSHAKE}')
        bot.send_message(from_id,
                         f'Просьба {HEART_RED} {RIGHT_ARROW} {HANDSHAKE} для {user_to.first_name} {user_to.last_name} на сумму {intention.payment}')
        for_my_wizard(message)
        return
    elif 'Главное' in text:
        global_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, all_check_int_obl_plus)


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
    elif text == 'Назад' or 'Back' in text:
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, for_my_check)
    return


def for_my_wizard_intention(message):
    intentions = read_intention(to_id=message.chat.id, status=1)
    bot_text = f"{HEART_RED} {PLUS}:\n"
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
    bot_text = f"{HANDSHAKE} {PLUS}:\n"
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

    bot_text = f"{user_from.first_name} {user_from.last_name} {status_from} {RIGHT_ARROW} {HANDSHAKE} {intention.payment}\n"
    if "red" in user_to.status:
        bot_text += f"Вы: {status} \n\
({right_sum}{HELP})"
    else:
        bot_text += f"Вы: {status} \n\
({left_sum}{HEART_RED} / {right_sum}{HELP})"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Запрос на исполнение')
    btn2 = types.KeyboardButton(text='Хранить')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, for_me_obligation_check, intention_id)
    return


def for_me_obligation_check(message, obligation_id):
    """ 6.8 """
    text = message.text
    # bot.delete_message(message.chat.id, message.message_id)
    if text == 'Запрос на исполнение':
        obligation_to_execution(message, obligation_id)
        return
    elif text == 'Хранить':
        keep_obligation(message, obligation_id)
        return
    elif text == 'Напомнить позже':
        remind_later(message, event_status=None, reminder_type='reminder_in', intention_id=obligation_id, to_menu=True)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    # else:
    #     msg = bot.send_message(message.chat.id, exception_message(message))
    #     bot.register_next_step_handler(msg, for_me_obligation_check, obligation_id)
    #     return
    return


def obligation_to_execution(message, obligation_id):
    """ 6.8 """
    # intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=obligation_id)

    user = read_exodus_user(telegram_id=intention.from_id)
    # update_intention(intention_id=obligation_id, status=15)
    bot_text = f'Участнику {user.first_name} {user.last_name} направлено уведомление с просьбой исполнить ' \
               f'{HANDSHAKE} на сумму {intention.payment} {intention.currency}.'

    payment = intention.payment
    currency = intention.currency
    # intentions = read_intention(to_id=obligation_id)
    # users_count = len(intentions.all())
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        all_users = 0
    else:
        try:
            all_users = len(set(ring.help_array_all))
        except:
            all_users = 0

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

    global_menu(message)

    return


def keep_obligation(message, obligation_id):
    # intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=obligation_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f'{HANDSHAKE} участника {user.first_name} {user.last_name} на ' \
               f'сумму  {intention.payment} {intention.currency} будет хранится у вас, ' \
               f'пока вы не примите решение.\n' \
               f'Посмотреть все {HANDSHAKE} можно в разделе главного меню "Органайзер"'
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
    elif text == 'Назад' or 'Back' in text:
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=f"{PLUS} ({for_me_intent})")
    btn2 = types.KeyboardButton(text=f"{MINUS} ({for_other_intent})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, not_executed_check)
    return


def not_executed_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if f"{PLUS}" in text:
        not_executed_wizard_to_me(message)
    elif f"{MINUS}" in text:
        not_executed_wizard_for_all(message)
    elif text == 'Назад' or 'Back' in text:
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
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
    user = read_exodus_user(telegram_id=intention.from_id)
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
Отправитель: {user.first_name} {user.last_name} {get_status(user.status)}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"  # TODO реквезиты
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Я получил эту сумму")
    btn2 = types.KeyboardButton(text="Повторный запрос на исполнение")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, executed_not_confirm_me_check)
    return


def executed_not_confirm_me_check(message):
    text = message.text
    if text == 'Назад':
        not_executed_wizard_to_me(message)
        return
    if 'Я получил эту сумму' in text:
        executed_confirm(message)
        return
    if text == 'Повторный запрос на исполнение':
        repeat_executed_request(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, not_executed_wizard_to_me)
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
Получатель: {user.first_name} {user.last_name} {get_status(user.status)}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Да, я получил")
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
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
        msg = bot.send_message(message.chat.id, exception_message(message))
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
    not_executed_wizard_to_me(message)
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text="Я отправил эту сумму")
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
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
        msg = bot.send_message(message.chat.id, exception_message(message))
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
        try:
            all_users = len(set(ring.help_array_all))
        except:
            all_users = 0

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


def members_menu_profile_link(message, member_id, name_return_func=""):
    user_id = message.chat.id
    user = read_exodus_user(member_id)
    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    # bot.delete_message(user_id, message.message_id)

    if user.status == 'green':
        bot_text = '\U0001F464 Имя участника: {} {}\n\
Статус: {}'.format(user.first_name, user.last_name, GREEN_BALL)

    elif user.status == 'orange':
        ring = read_rings_help(user.telegram_id)
        if ring is None:
            all_users = 0
        else:
            try:
                all_users = len(set(ring.help_array_orange))
            except:
                all_users = 0
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

    bot_text += "\nСсылка на обсуждение \U0001F4E2"
    if user.link == '' or user.link == None:
        bot_text += "\n"  # ссылка на обсуждение
    else:
        bot_text += f"\n{user.link}"  # ссылка на обсуждение # ссылка на обсуждение
    if user.status != 'green':
        link = create_link(user.telegram_id, user.telegram_id)
        bot_text += f"\n\nСсылка для помощи \U0001F4E9\n{link}"

    bot.send_message(user_id, bot_text)  # общий текст
    if 'selected_member_action_check' in name_return_func:
        selected_member_action_menu(message, member_id)
    else:
        global_menu(message)


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
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, config_wizzard_currency)


def welcome_base(message):
    """1.0"""
    bot.clear_step_handler(message)
    referral = ref_info(message.text)
    #     bot.send_message(message.chat.id, f"Добро пожаловать в бот Exodus.\n\n\
    # Зелёный статус {GREEN_BALL} - сообщает о том, что вы готовы помогать участникам сети.\n\
    # Оранжевый статус {ORANGE_BALL} - сообщает участникам сети, что вам необходима ежемесячная денежная поддержка.")
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

        bot.send_message(message.chat.id, bot_text, parse_mode="html")

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
        create_exodus_user(message.chat.id, message.chat.first_name, message.chat.last_name,
                           message.chat.username, status="green", ref=ref)
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
        try:
            users_count = len(set(ring.help_array_orange))
        except:
            users_count = 0

    bot_text = generate_user_info_text(user) + '\nВы можете помочь этому участнику?'

    #    status = ORANGE_BALL
    #     bot_text = 'Участник {first_name} {last_name} {status}\n\
    # Период: Ежемесячно\n\
    # {current}/{all}\n\
    # Обсуждение:\n\
    # {link}\n\
    # Уже помогают: {users_count}\n\
    # \n\
    # Вы можете помочь этому участнику?'.format(first_name=user.first_name,
    #                                           last_name=user.last_name,
    #                                           status=status,
    #                                           current=left_sum,
    #                                           all=right_sum,
    #                                           link=link,
    #                                           users_count=users_count)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn2, btn3)
    markup.row(btn1, btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup, parse_mode="html")
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
            create_exodus_user(message.chat.id, message.chat.first_name, message.chat.last_name,
                               message.chat.username, status="green", ref=ref)
        orange_invitation_wizard(message, user_to, event_id)

    elif 'Главное меню' in text:
        global_menu(message)

    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, orange_invitation_check)


def orange_invitation_wizard(message, user_to, event_id=None):
    """6.1.2"""
    temp_dict[message.chat.id] = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text='Назад')
        msg = bot.send_message(message.chat.id, 'Введите сумму помощи в {}:'.format(user.currency),
                               reply_markup=markup)
    else:
        btn1 = types.KeyboardButton(text='Back')
        msg = bot.send_message(message.chat.id, 'Enter the amount of assistance in {}:'.format(user.currency),
                               reply_markup=markup)
    markup.row(btn1)
    bot.register_next_step_handler(msg, orange_invitation_wizard_check, event_id)


def orange_invitation_wizard_check(message, event_id=None):  # ------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if invitation_sum == 'Назад' or 'Back' in invitation_sum:
        start_orange_invitation(message, user.telegram_id)
        return
    if not is_digit(invitation_sum):
        lang = read_user_language(message.chat.id)
        if lang == "ru":
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['en'])

        bot.register_next_step_handler(msg, orange_invitation_wizard_check)
        return

    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array_orange = []
        array_orange.append(message.chat.id)
        create_rings_help(user.telegram_id, help_array_orange=array_orange, help_array_all=array_orange)
    else:
        array_orange = ring.help_array_orange
        array_orange.append(message.chat.id)
        update_orange_rings_help(user.telegram_id, array_orange)

        array_all = ring.help_array_all
        array_all.append(message.chat.id)
        update_rings_help_array_all(user.telegram_id, array_all)

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
    global_menu(message)


# ------------------------------------------------------


def show_all_members(message, user_to):
    bot.delete_message(message.chat.id, message.message_id)
    user = user_to
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        users_count = 0
    elif ring.help_array_red is None:
        users_count = 0
    else:
        if "red" in user.status:
            user_list = set(ring.help_array_red)
            users_count = len(user_list)
        else:
            user_list = set(ring.help_array_orange)
            users_count = len(user_list)

        # узнаем кто со мной в сети
        list_my_socium = get_my_socium(message.chat.id)

        string_name = ''
        for id_help in user_list:
            if id_help in list_my_socium or id_help == message.chat.id:
                user_id_help = read_exodus_user(id_help)
                status = get_status(user_id_help.status)
                string_name = string_name + f'\n{user_id_help.first_name} {user_id_help.last_name} {status}'
    bot_text = 'Участнику {} {} помогают {} {}:\n'.format(user.first_name, user.last_name, users_count, PEOPLES)

    bot_text = bot_text + string_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
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
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
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
            try:
                users_count = len(set(ring.help_array_orange))
            except:
                users_count = 0
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days

    bot_text = generate_user_info_text(user) + '\nВы можете помочь этому участнику?'

    #     bot_text = f'Участник {user.first_name} {user.last_name} {status}\n\
    # Осталось {days_end} дней из {user.days}\n\
    # {left_sum}/{right_sum} {user.currency}\n\
    # Обсуждение:\n\
    # {user.link}\n\
    # Уже помогают: {users_count}\n\
    # \n\
    # Вы можете помочь этому участнику?\n'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn2, btn3)
    markup.row(btn1, btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup, parse_mode="html")
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
            create_exodus_user(message.chat.id, message.chat.first_name, message.chat.last_name,
                               message.chat.username, status="green", ref=ref)
        red_invitation_wizard(message, user_to, event_id)

    elif 'Главное меню' in text:
        global_menu(message)

    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, red_invitation_check)


def red_invitation_wizard(message, user_to, event_id=None):
    """6.1.2"""
    temp_dict[message.chat.id] = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text='Назад')
        msg = bot.send_message(message.chat.id, 'Введите сумму помощи в {}:'.format(user.currency),
                               reply_markup=markup)
    else:
        btn1 = types.KeyboardButton(text='Back')
        msg = bot.send_message(message.chat.id, 'Enter the amount of assistance in {}:'.format(user.currency),
                               reply_markup=markup)
    markup.row(btn1)
    bot.register_next_step_handler(msg, red_invitation_wizard_check, event_id)


def red_invitation_wizard_check(message, event_id=None):  # ------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if invitation_sum == 'Назад' or 'Back' in invitation_sum:
        start_red_invitation(message, user.telegram_id)
        return
    if not is_digit(invitation_sum):
        lang = read_user_language(message.chat.id)
        if lang == "ru":
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(message.chat.id, TEXT_SUM_DIGIT['en'])
        bot.register_next_step_handler(msg, red_invitation_wizard_check)
        return

    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array_red = []
        array_red.append(message.chat.id)
        create_rings_help(user.telegram_id, help_array_red=array_red)
    else:
        array_red = ring.help_array_red
        array_red.append(message.chat.id)
        update_rings_help_array_red(user.telegram_id, array_red)

        array_all = ring.help_array_all
        array_all.append(message.chat.id)
        update_rings_help_array_all(user.telegram_id, array_all)
    # ring = read_rings_help(user.telegram_id)
    # users_count = session.query(Exodus_Users).count()
    # ring = read_rings_help(user.telegram_id)
    # if ring is None:
    #     all_users = 0
    # else:
    #     all_users = len(set(ring.help_array))

    # already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    # already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    # left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    # right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

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
                     sent=True,
                     reminder_date=date.today(),
                     status_code=APPROVE_RED_STATUS,
                     intention=Intention(from_id=message.chat.id, to_id=user.telegram_id,
                                         payment=invitation_sum, currency=user.currency, status=11,
                                         create_date=datetime.now()))  # someday: intention_id
    else:
        update_event_status_code(event_id, APPROVE_RED_STATUS)
        update_event_type(event_id, 'notice')
        update_event(event_id, True)
        create_intention(message.chat.id, user.telegram_id, invitation_sum, user.currency, status=11, event_id=event_id)

    # рассылка уведомлений моему кругу о том, что я начал кому то помогать, кроме того, кто запросил
    list_needy_id = get_my_socium(message.chat.id)
    list_needy_id.discard(user.telegram_id)
    user_from = read_exodus_user(telegram_id=message.chat.id)
    status_from = get_status(user_from.status)

    already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days

    status = RED_BALL
    bot_text = f'Записано Ваше {HANDSHAKE} участнику {user.first_name} {user.last_name} на сумму {invitation_sum} {user.currency}\n\
{user.first_name} {user.last_name}: {status} \n\
({right_sum}{HELP} за {days_end} дней)'

    # рассылка уведомлений моему кругу о том, что я начал кому то помогать, кроме того, кто запросил
    bot_text_for_all = f"{user_from.first_name} {user_from.last_name}  {RIGHT_ARROW}  {HANDSHAKE} {invitation_sum} {user.first_name} {user.last_name}\n\
{user.first_name} {user.last_name}: {status} \n\
({right_sum}{HELP} за {days_end} дней)"

    for id in list_needy_id:
        bot.send_message(id, bot_text_for_all)

    # сообщение, что ты записал обязательство кому-то
    bot.send_message(message.chat.id, bot_text)

    # сообщение, получателю, что кто то записал обязательство в его пользу
    text_for_u = f"{user_from.first_name} {user_from.last_name} {status_from}  {RIGHT_ARROW}  {HANDSHAKE} {invitation_sum}\n\
Ваш статус: {status} \n\
({right_sum}{HELP})"
    bot.send_message(user.telegram_id, text_for_u)

    link = user.link
    user_id = user.telegram_id

    # автоматический возврат к текущему статусу
    if right_sum == 0:
        if 'orange' in user.status:
            if read_rings_help(user.telegram_id) is None:
                create_rings_help(user.telegram_id, [])

            # удаляем статусы для запроса помощи
            delete_event_new_status(user_id)

            if 'red' in user.status and user.min_payments != 0:
                count_unfreez_intentions = unfreeze_intentions(user)
            else:
                # list_statuses = [1, 11, 12, 13, 15]
                # # удаляем все активные записи для красного
                # for status in list_statuses:
                #     delete_intention(to_id=message.chat.id, status=status)

                count_unfreez_intentions = 0

            update_exodus_user(user_id, status='orange', link=link)

            # создаем список с моей сетью
            list_needy_id = get_my_socium(user_id)

            if count_unfreez_intentions == 0:
                for users in list_needy_id:
                    # TODO           рассылка кругу лиц из таблицы rings
                    if users != user_id:
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
                                     to_id=user_id,
                                     sent=False,
                                     reminder_date=date.today(),
                                     status_code=NEW_ORANGE_STATUS)  # someday: intention_id

            for row in list_needy_id:
                try:
                    bot.send_message(row, '{} {} вернулся к {}'.format(user.first_name, user.last_name, ORANGE_BALL))
                except:
                    continue

            already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
            already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
            left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
            right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

            # сообщение Вам, что вы вернулись автоматически
            text = f"Вы вернулись к {ORANGE_BALL}\n({left_sum}{HEART_RED} / {right_sum}{HELP})"
            bot.send_message(user_id, text)

            global_menu(message)
            return

        else:
            # создаем список с теми, у кого мы в списке help_array
            try:
                list_needy_id = set(read_rings_help(user_id).help_array_all)
            except:
                list_needy_id = []

            list_send_notify = read_rings_help_in_help_array_all(user_id)

            for row in list_send_notify:
                list_needy_id.add(row.needy_id)

            for row in list_needy_id:
                try:
                    bot.send_message(row, '{} {} вернулся к {}'.format(user.first_name, user.last_name, GREEN_BALL))
                    # закрываем намерения и event
                    intention = read_intention(from_id=row, to_id=user_id).all()
                    for id in intention:
                        update_intention(id.intention_id, status=0)
                        update_event_status_code(id.event_id, CLOSED)
                except:
                    continue

            # удаляем статусы для запроса помощи
            delete_event_new_status(user_id)

            if 'red' in user.status:
                # удаляем данные из буфферной таблицы
                delete_temp_intention(user_id)

                # очищаем массив помощников для красного
                update_rings_help_array_red(user_id, [])

            else:
                # очищаем массив помощников для оранжевого
                update_orange_rings_help(user_id, [])

            update_exodus_user(telegram_id=user_id, status='green', min_payments=0, max_payments=0)

            # сообщение Вам, что вы вернулись автоматически
            text = f"Вы вернулись к {GREEN_BALL}"
            bot.send_message(user_id, text)

            global_menu(message)
            return

    global_menu(message)


# ---------------------------------------------------------


def orange_status_wizard(message):
    user = read_exodus_user(message.chat.id)
    #     already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    #     already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    #     left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    #     right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0
    #     ring = read_rings_help(user.telegram_id)
    #     link = create_link(user.telegram_id, user.telegram_id)
    #     if ring is None:
    #         all_users = 0
    #     else:
    #         try:
    #             all_users = len(set(ring.help_array_orange))
    #         except:
    #             all_users = 0
    #     bot_text = f'Ваш статус: {ORANGE_BALL}\n\
    # {left_sum}/{right_sum} {user.currency}\n\
    # Уже помогают: {all_users}\n\
    # Период: Ежемесячно\n\n\
    # Ссылка на обсуждение \U0001F4E2 \n{user.link}\
    # \n\nСсылка для помощи \U0001F4E9\n{link}'

    lang = read_user_language(message.chat.id)
    if lang =="ru":
        bot_text = f'{ORANGE_BALL} {MONEY_BAG} {user.max_payments}, ежемесячно'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text=f'Изменить данные {MONEY_BAG}')
        btn2 = types.KeyboardButton(text='Изменить статус')
        btn3 = types.KeyboardButton(text='Назад')
    else:
        bot_text = f'{ORANGE_BALL} {MONEY_BAG} {user.max_payments}, every month'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text=f'Change data {MONEY_BAG}')
        btn2 = types.KeyboardButton(text='Change status')
        btn3 = types.KeyboardButton(text='Back')
    markup.row(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, orange_menu_check)


def orange_menu_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if 'Изменить данные' in text or 'data' in text:
        edit_orange_data(message)
    elif text == 'Изменить статус' or 'status' in text:
        green_red_wizard(message)
    elif text == 'Назад' or 'Back' in text:
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, orange_menu_check)


def edit_orange_data(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lang = read_user_language(message.chat.id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text='Да')
        btn2 = types.KeyboardButton(text='Нет')
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, f'{ORANGE_BALL} Вы собираетесь изменить данные {MONEY_BAG}\n\
Пожалуйста подтвердите действие', reply_markup=markup)
    else:
        btn1 = types.KeyboardButton(text='Yes')
        btn2 = types.KeyboardButton(text='No')
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, f'{ORANGE_BALL} You are going to change the data {MONEY_BAG}\n\
Please confirm the action', reply_markup=markup)
    bot.register_next_step_handler(msg, check_edit_orange_data)


def check_edit_orange_data(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    # user = read_exodus_user(message.chat.id)
    if 'Да' in text or 'Yes' in text:
        markup = types.ReplyKeyboardRemove(selective=False)
        lang = read_user_language(message.chat.id)
        if lang == "ru":
            msg = bot.send_message(message.chat.id,
                                   f'{ORANGE_BALL}Введите цифрами сумму{MONEY_BAG}, которая вам необходима на базовые нужды ежемесячно',
                                   reply_markup=markup)
        else:
            msg = bot.send_message(message.chat.id,
                                   f'{ORANGE_BALL}Enter the amount{MONEY_BAG} in numbers you need for basic needs on a monthly basis',
                                   reply_markup=markup)
        bot.register_next_step_handler(msg, edit_orange_need_payments)
    elif 'Нет' in text or 'No' in text:
        orange_status_wizard(message)

    elif text == 'Главное меню':
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)


def edit_orange_need_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    new_sum = message.text

    lang = read_user_language(chat_id)
    if not is_digit(new_sum):
        if lang == "ru":
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['en'])
        bot.register_next_step_handler(msg, edit_orange_need_payments)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "ru":
        btn1 = types.KeyboardButton(text=f'Изменить данные {MONEY_BAG}')
        btn2 = types.KeyboardButton(text='Отмена')
        btn3 = types.KeyboardButton(text='Сохранить')
        bot_text = f'{ORANGE_BALL} Проверьте введенные данные:\n\
Ежемесячная необходимая сумма {MONEY_BAG} = {new_sum} {user.currency}'
    else:
        btn1 = types.KeyboardButton(text=f'Change data {MONEY_BAG}')
        btn2 = types.KeyboardButton(text='Cancel')
        btn3 = types.KeyboardButton(text='Save')
        bot_text = f'{ORANGE_BALL} Check the entered data:\n\
The monthly required amount {MONEY_BAG} = {new_sum} {user.currency}'

    markup.row(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_orange_final, new_sum)


def edit_orange_final(message, new_sum):
    text = message.text
    # bot.delete_message(message.chat.id, message.message_id)
    if 'Изменить данные' in text:
        bot.send_message(message.chat.id, 'Вы выбрали редактирование')
        edit_orange_data(message)
        return
    elif 'Change' in text:
        bot.send_message(message.chat.id, 'You have selected editing')
        edit_orange_data(message)
        return
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Настройки не сохранены')
        orange_status_wizard(message)
        return
    elif text == 'Cancel':
        bot.send_message(message.chat.id, 'Settings are not saved')
        orange_status_wizard(message)
        return
    elif text == 'Сохранить':
        bot.send_message(message.chat.id, 'Настройки сохранены')
        user = read_exodus_user(message.chat.id)
        link = user.link
        update_exodus_user(message.chat.id, max_payments=float(new_sum), link=link)
        orange_status_wizard(message)
        return
    elif text == 'Save':
        bot.send_message(message.chat.id, 'The settings are saved')
        user = read_exodus_user(message.chat.id)
        link = user.link
        update_exodus_user(message.chat.id, max_payments=float(new_sum), link=link)
        orange_status_wizard(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, edit_orange_final)
        return


def green_red_wizard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=GREEN_BALL)
    btn2 = types.KeyboardButton(text=RED_BALL)
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2, btn3)
    msg = bot.send_message(message.chat.id, 'Выберите новый статус', reply_markup=markup)
    bot.register_next_step_handler(msg, green_red_check)


def green_red_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == GREEN_BALL:
        green_edit_wizard(message)
    elif text == RED_BALL:
        check_red_edit_wizard(message)
    elif text == 'Назад' or 'Back' in text:
        orange_status_wizard(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, green_red_check)


def green_edit_wizard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Сохранить')
    btn2 = types.KeyboardButton(text='Отмена')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, f'Вы собираетесь сменить статус на {GREEN_BALL}\n\
Пожалуйста подтвердите смену статуса:\n\
\n\
Если ваш статус был {ORANGE_BALL} или {RED_BALL}, все {HEART_RED} участников в Вашу пользу будут автоматически удалены.\n\
\n\
Все {HANDSHAKE} участников в Вашу пользу останутся в силе. Посмотреть все {HANDSHAKE} можно в разделе главного меню "Органайзер"',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, green_edit_wizard_check)


def green_edit_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Сохранить':
        bot.send_message(message.chat.id, 'Статус сохранён')

        # создаем список с теми, у кого мы в списке help_array
        try:
            list_needy_id = set(read_rings_help(message.chat.id).help_array_all)
        except:
            list_needy_id = []
        telegram_name = read_exodus_user(message.chat.id)

        list_send_notify = read_rings_help_in_help_array_all(message.chat.id)

        for row in list_send_notify:
            list_needy_id.add(row.needy_id)

        # удалим себя из списка на всякий случай
        list_needy_id.discard(message.chat.id)
        for row in list_needy_id:
            try:
                bot.send_message(row,
                                 '{} {} сменил статус на {}'.format(telegram_name.first_name, telegram_name.last_name,
                                                                    GREEN_BALL))
                # закрываем намерения и event
                intention = read_intention(from_id=row, to_id=message.chat.id).all()
                for id in intention:
                    update_intention(id.intention_id, status=0)
                    update_event_status_code(id.event_id, CLOSED)
            except:
                continue

        # удаляем статусы для запроса помощи
        delete_event_new_status(message.chat.id)

        # удаляем события, которые были записаны на будущий месяц
        delete_event_future()

        if 'red' in read_exodus_user(message.chat.id).status:
            # удаляем данные из буфферной таблицы
            delete_temp_intention(message.chat.id)

            # очищаем массив помощников для красного
            update_rings_help_array_red(message.chat.id, [])

        else:
            # очищаем массив помощников для оранжевого
            update_orange_rings_help(message.chat.id, [])

        update_exodus_user(telegram_id=message.chat.id, status='green', min_payments=0, max_payments=0)

        global_menu(message)
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Статус не сохранён')
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, green_edit_wizard_check)


# ------------------------
def green_status_wizard(message):
    """2.0.1"""
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    lang = read_user_language(user_id)
    if lang == "ru":
        btn1 = types.KeyboardButton(text='Изменить статус')
        btn2 = types.KeyboardButton(text='Назад')
        markup.row(btn1, btn2)
        msg = bot.send_message(user_id,
                               f'Ваш статус: {GREEN_BALL}\nСписок участников с которыми Вы связаны, '
                               'можно посмотреть в разделе главного меню "Участники"',
                               reply_markup=markup)
    else:
        btn1 = types.KeyboardButton(text='Change status')
        btn2 = types.KeyboardButton(text='Back')
        markup.row(btn1, btn2)
        msg = bot.send_message(user_id,
                               f'Your status: {GREEN_BALL}\nList of participants you are associated with, '
                                'can be viewed in the main menu section "Participants"',
                               reply_markup=markup)
    bot.register_next_step_handler(msg, green_status_wizard_check)


def green_status_wizard_check(message):
    user_id = message.chat.id
    bot.delete_message(user_id, message.message_id)
    text = message.text
    if text == 'Изменить статус' or "Change" in text:
        select_orange_red(message)
    elif text == 'Назад' or 'Back' in text:
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(user_id, exception_message(message))
        bot.register_next_step_handler(msg, green_status_wizard_check)


def select_orange_red(message):
    user_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=ORANGE_BALL)
    btn2 = types.KeyboardButton(text=RED_BALL)

    lang = read_user_language(user_id)
    if lang == "ru":
        btn3 = types.KeyboardButton(text='Назад')
        markup.row(btn1, btn2, btn3)
        msg = bot.send_message(user_id, "Выберите новый статус:", reply_markup=markup)
    else:
        btn3 = types.KeyboardButton(text='Back')
        markup.row(btn1, btn2, btn3)
        msg = bot.send_message(user_id, "Select a new status:", reply_markup=markup)
    bot.register_next_step_handler(msg, check_orange_red)


def check_orange_red(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == ORANGE_BALL:
        # bot.send_message(message.chat.id, f"Вы меняете статус на {ORANGE_BALL}:")
        orange_edit_wizard(message)
    elif text == RED_BALL:
        check_red_edit_wizard(message)
    elif text == 'Назад' or 'Back' in text:
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, check_orange_red)


def red_status_wizard(message):
    user = read_exodus_user(message.chat.id)

    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days

    # already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
    # already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
    # left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
    # right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

    bot_text = f'{RED_BALL} {user.max_payments}, осталось {days_end} дней'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=f'Изменить данные {MONEY_BAG}')
    user_status = user.status
    if 'orange' in user_status:
        btn2 = types.KeyboardButton(text=f'Вернуться к {ORANGE_BALL}')  # orange
    if 'green' in user_status:
        btn2 = types.KeyboardButton(text=f'Вернуться к {GREEN_BALL}')  # green
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2, btn3)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, red_status_wizard_check)


def red_status_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if 'Изменить данные' in text:
        edit_red_data(message)
    elif 'Вернуться' in text:
        green_orange_check(message)
    elif text == 'Назад' or 'Back' in text:
        configuration_menu(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, red_status_wizard_check)


def edit_red_data(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Да')
    btn2 = types.KeyboardButton(text='Нет')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, f'{RED_BALL} Вы собираетесь изменить данные {MONEY_BAG}\n\
Пожалуйста подтвердите действие', reply_markup=markup)
    bot.register_next_step_handler(msg, check_edit_red_data)


def check_edit_red_data(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    # user = read_exodus_user(message.chat.id)
    if 'Да' in text:
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id,
                               f'{RED_BALL} Введите цифрами сумму {MONEY_BAG}, которую вам необходимо набрать экстренно',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, edit_red_need_payments)
    elif 'Нет' in text:
        red_status_wizard(message)

    elif text == 'Главное меню':
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)


def edit_red_need_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    lang = read_user_language(chat_id)
    new_sum = message.text

    if not is_digit(new_sum):
        if lang == "ru":
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['en'])
        bot.register_next_step_handler(msg, edit_red_need_payments)
        return

    if lang == "ru":
        msg = bot.send_message(chat_id,
                               f'{RED_BALL} Введите цифрами число дней, за которые вам необходимо набрать эту сумму')
    else:
        msg = bot.send_message(chat_id,
                               f'{RED_BALL} Enter numbers for the number of days you need to collect this amount')
    bot.register_next_step_handler(msg, edit_red_data_day, new_sum)


def edit_red_data_day(message, new_sum):
    # user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    days = message.text
    if not days.isdigit():
        msg = bot.send_message(chat_id,
                               'Кол-во дней должны быть в виде цифр. Введите кол-во дней, в течении которых вам необходимо собрать эту сумму:')
        bot.register_next_step_handler(msg, edit_red_data_day, new_sum)
        return

    bot_text = f'{RED_BALL}Пожалуйста проверьте введенные данные:\n\
Необходимая сумма: {new_sum} за {days} дней'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=f'Изменить данные {MONEY_BAG}')
    btn2 = types.KeyboardButton(text='Отмена')
    btn3 = types.KeyboardButton(text='Сохранить статус')
    markup.row(btn1, btn2, btn3)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, edit_red_data_final, new_sum, days)


def edit_red_data_final(message, new_sum, days):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if 'Изменить данные' in text:
        edit_red_data(message)
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Настройки не сохранены')
        red_status_wizard(message)

    elif text == 'Сохранить статус':
        bot.send_message(message.chat.id, 'Настройки сохранены')

        user = read_exodus_user(message.chat.id)
        link = user.link

        update_exodus_user(telegram_id=message.chat.id, link=link,
                           start_date=date.today(),
                           days=days, max_payments=new_sum)
        red_status_wizard(message)
    elif "/start" in text:
        welcome_base(message)
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, edit_red_data_final, new_sum, days)


# ------------------ RED WIZARD 2.2 ---------------
def check_red_edit_wizard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Да, изменить')
    btn2 = types.KeyboardButton(text='Нет, вернуться назад')
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, f'Вы собираетесь сменить статус на {RED_BALL}\n\
Пожалуйста подтвердите смену статуса', reply_markup=markup)
    bot.register_next_step_handler(msg, check_answer_red_wizard)


def check_answer_red_wizard(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    user = read_exodus_user(message.chat.id)
    if text == 'Да, изменить':
        red_edit_wizard(message)
    elif text == 'Нет, вернуться назад':
        if user.status == 'orange':
            green_red_wizard(message)
        elif user.status == 'green':
            select_orange_red(message)

    elif text == 'Главное меню':
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)


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
    lang = read_user_language(chat_id)

    text = message.text

    if not is_digit(text):
        if lang == "ru":
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['ru'])
        else:
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['en'])
        bot.register_next_step_handler(msg, red_edit_wizard_step1)
        return
    user_dict[chat_id].max_payments = float(text)
    if lang == "ru":
        msg = bot.send_message(chat_id,
                               f'{RED_BALL} Введите цифрами число дней, за которые вам необходимо набрать эту сумму')
    else:
        msg = bot.send_message(chat_id,
                               f'{RED_BALL} Enter numbers for the number of days you need to collect this amount')
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

#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton(text='Пропустить')
#     markup.row(btn1)
#
#     msg = bot.send_message(message.chat.id, 'Введите ссылку на чат:', reply_markup=markup)
#     bot.register_next_step_handler(msg, red_edit_wizard_step35)
#
#
# def red_edit_wizard_step35(message):
#     if message.text != 'Пропустить':
#         link = message.text
#     else:
#         link = None

    user = user_dict[message.chat.id]
    bot_text = f'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {RED_BALL}\n\
В течении: {user.days}\n\
Необходимая сумма: {user.max_payments} {user.currency}'
    bot.send_message(message.chat.id, bot_text)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Редактировать')
    btn2 = types.KeyboardButton(text='Отмена')
    btn3 = types.KeyboardButton(text='Сохранить статус')
    markup.row(btn1, btn3, btn2)
    bot_text = 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, red_edit_wizard_step4)


def red_edit_wizard_step4(message):
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

        update_exodus_user(telegram_id=message.chat.id, status='red' + str(user.status),
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
                             sent=False,
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
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, red_edit_wizard_step4)


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
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, red_status_wizard_check)

    # ------------------ ORANGE GREEN WIZARD-------


def orange_green_wizard(message):
    #    bot.delete_message(message.chat.id, message.message_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text=ORANGE_BALL)
    btn2 = types.KeyboardButton(text=GREEN_BALL)
    markup.row(btn1, btn2)
    msg = bot.send_message(message.chat.id, 'Пожалуйста выберите Ваш статус', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_green_wizard_step1)


def orange_green_wizard_step1(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    if message.text == ORANGE_BALL:
        bot.send_message(message.chat.id, f'Вы выбрали {ORANGE_BALL} статус', reply_markup=markup)
        # orange_edit_wizard(message)
        msg = bot.send_message(message.chat.id,
                               'Какая сумма вам необходима на базовые нужды?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_need_payments)
        return
    if message.text == GREEN_BALL:
        bot.send_message(message.chat.id,
                         f'Ваш статус: {GREEN_BALL}\nСписок участников с которыми Вы связаны, можно посмотреть в разделе главного меню "Участники"',
                         reply_markup=markup)
        update_exodus_user(telegram_id=message.chat.id, status='green', min_payments=0, max_payments=0)
        # global_menu(message)
        requisites = read_requisites_user(message.chat.id)
        if requisites == []:
            #add_requisite_name(message)
            create_requisites_user(telegram_id=message.chat.id, name="Спросить лично", value="0")
            global_menu(message)
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
        #link = user.link
        if 'red' in user.status:
            payments = user.min_payments
        else:
            payments = user.max_payments
        bot.send_message(message.chat.id, 'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {}\n\
Период: Ежемесячно\n\
Необходимая сумма: {} {}'.format(ORANGE_BALL, payments, user.currency))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # user = read_exodus_user(message.chat.id)
        if user.status == '':
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1, btn2)
        else:
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Отмена')
            btn3 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1, btn3, btn2)
        msg = bot.send_message(message.chat.id, f'Опубликовать эти данные?\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_final)
    else:
        check_orange_green_edit_wizard(message)


def check_orange_green_edit_wizard(message):
    user_id = message.chat.id
    lang = read_user_language(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if lang == "ru":
        btn1 = types.KeyboardButton(text='Да, изменить')
        btn2 = types.KeyboardButton(text='Нет, вернуться назад')
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, f'Вы собираетесь сменить статус на {ORANGE_BALL}\n\
Пожалуйста подтвердите смену статуса', reply_markup=markup)
    else:
        btn1 = types.KeyboardButton(text='Yes, change')
        btn2 = types.KeyboardButton(text='No, go back')
        markup.row(btn1, btn2)
        msg = bot.send_message(message.chat.id, f'You are going to change your status to {ORANGE_BALL}\n\
Please confirm the status change', reply_markup=markup)
    bot.register_next_step_handler(msg, check_answer_orange_green_wizard)


def check_answer_orange_green_wizard(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    user = read_exodus_user(message.chat.id)
    if text == 'Да, изменить':
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id,
                               'Какая сумма вам необходима на базовые нужды в {}?'.format(user.currency),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_need_payments)
    elif 'Yes, change' in text:
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(message.chat.id,
                               'How much do you need for basic needs in {}?'.format(user.currency),
                               reply_markup=markup)
        bot.register_next_step_handler(msg, orange_step_need_payments)
    elif text == 'Нет, вернуться назад' or 'No, go' in text:
        select_orange_red(message)

    elif text == 'Главное меню':
        global_menu(message)
    elif "/start" in text:
        welcome_base(message)


def orange_step_need_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    lang = read_user_language(chat_id)

    text = message.text

    if lang == "ru":
        if not is_digit(text):
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['ru'])
            bot.register_next_step_handler(msg, orange_step_need_payments)
            return
        update_exodus_user(chat_id, max_payments=float(text))

        if 'red' in user.status and user.min_payments != 0:
            payments = user.min_payments
        else:
            payments = user.max_payments
        bot.send_message(message.chat.id, 'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: {}\n\
Период: Ежемесячно\n\
Необходимая сумма: {} {}'.format(ORANGE_BALL, payments, user.currency))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # user = read_exodus_user(message.chat.id)
        if user.status == '':
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1, btn2)
        else:
            btn1 = types.KeyboardButton(text='Редактировать')
            btn2 = types.KeyboardButton(text='Отмена')
            btn3 = types.KeyboardButton(text='Сохранить')
            markup.row(btn1, btn3, btn2)
        msg = bot.send_message(message.chat.id, f'Опубликовать эти данные?\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
    else:
        if not is_digit(text):
            msg = bot.send_message(chat_id, TEXT_SUM_DIGIT['en'])
            bot.register_next_step_handler(msg, orange_step_need_payments)
            return
        update_exodus_user(chat_id, max_payments=float(text))

        if 'red' in user.status and user.min_payments != 0:
            payments = user.min_payments
        else:
            payments = user.max_payments
        bot.send_message(message.chat.id, 'Please check the entered data:\n\
\n\
Status: {}\n\
Period: Monthly\n\
Necessary amount: {} {}'.format(ORANGE_BALL, payments, user.currency))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # user = read_exodus_user(message.chat.id)
        if user.status == '':
            btn1 = types.KeyboardButton(text='Edit')
            btn2 = types.KeyboardButton(text='Save')
            markup.row(btn1, btn2)
        else:
            btn1 = types.KeyboardButton(text='Edit')
            btn2 = types.KeyboardButton(text='Cancel')
            btn3 = types.KeyboardButton(text='Save')
            markup.row(btn1, btn3, btn2)
        msg = bot.send_message(message.chat.id, f'Publish this data?\n\
All users who are connected to you inside the Exodus bot will receive a notification.', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_step_final)


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


def orange_step_final(message):
    text = message.text
    chat_id = message.chat.id
    lang = read_user_language(chat_id)

    # bot.delete_message(message.chat.id, message.message_id)
    if text == 'Редактировать' or 'Edit' in text:
        if lang == "ru":
            bot.send_message(message.chat.id, 'Вы выбрали редактирование')
        else:
            bot.send_message(message.chat.id, 'You have selected editing')
        orange_edit_wizard(message)
        return
    if text == 'Отмена' or 'Cancel' in text:
        if lang == "ru":
            bot.send_message(message.chat.id, 'Настройки не сохранены')
        else:
            bot.send_message(message.chat.id, 'Settings are not saved')
        global_menu(message)
        return
    if text == 'Сохранить' or 'Save' in text:
        if lang == "ru":
            bot.send_message(message.chat.id, 'Настройки сохранены')
        else:
            bot.send_message(message.chat.id, 'Settings are saved')

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

        update_exodus_user(message.chat.id, status='orange')

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
                lang_row = read_user_language(row)
                if lang_row == "ru":
                    bot.send_message(row,
                                     '{} {} сменил статус на {}'.format(telegram_name.first_name, telegram_name.last_name,
                                                                        ORANGE_BALL))
                else:
                    bot.send_message(row,
                                     '{} {} changed the status to {}'.format(telegram_name.first_name, telegram_name.last_name,
                                                                        ORANGE_BALL))
            except:
                continue

        # global_menu(message)
        requisites = read_requisites_user(message.chat.id)
        if requisites == []:
            #add_requisite_name(message)
            create_requisites_user(telegram_id=message.chat.id, name="Ask in person", value="0")
            global_menu(message)
        else:
            global_menu(message)
        return
    elif "/start" in text:
        welcome_base(message)
        return
    else:
        msg = bot.send_message(message.chat.id, exception_message(message))
        bot.register_next_step_handler(msg, orange_step_final)
        return


# -------------------------------------------
def show_help_requisites(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users_dict = get_help_requisites(message.chat.id)
    # print(message.chat.id)
    # if len(users_dict) == 0:
    #     txt = 'Никто помощь пока не запрашивал'
    #     #members_menu(message, meta_txt=txt)
    #     bot.send_message(message.chat.id, txt)
    #     global_menu(message)
    # else:

    # btns = [types.KeyboardButton(un) for un in users_dict.keys()]
    # for btn in btns:
    #     markup.row(btn)
    i = 0
    bot_text = 'Запросы помощи:\n'
    for un in users_dict.keys():
        i += 1
        user = read_exodus_user(telegram_id=un)
        already_payments_oblig = get_intention_sum(user.telegram_id, statuses=(11, 12, 13))
        already_payments_intent = get_intention_sum(user.telegram_id, statuses=(1,))
        left_sum = max(already_payments_intent, already_payments_oblig - user.max_payments)
        right_sum = user.max_payments - already_payments_oblig if user.max_payments - already_payments_oblig > 0 else 0

        # bot_text += f"{i}. {user.first_name} {user.last_name} {status} {left_sum}/{right_sum}\n"
        status = user.status
        if status == 'green':
            bot_text = bot_text + f'\n{i}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {GREEN_BALL}'
        elif status == "orange":
            bot_text = bot_text + f'\n{i}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {ORANGE_BALL} {left_sum} {HEART_RED} / {right_sum} {HELP}'
        elif "red" in status:
            bot_text = bot_text + f'\n{i}. <a href="tg://user?id={user.telegram_id}">{user.first_name} {user.last_name}</a> {RED_BALL} {right_sum} {HELP}'

    btn1 = types.KeyboardButton('Назад')
    markup.row(btn1)
    txt = '\n\nВведите номер Участника, чтобы посмотреть подробную информацию:'
    bot_text += txt
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup, parse_mode="html")
    bot.register_next_step_handler(msg, restart_invitation)
    return


def restart_invitation(message):
    users_dict = get_help_requisites(message.chat.id)
    list_keys = list(users_dict.keys())
    number = message.text
    bot.delete_message(message.chat.id, message.message_id)

    if 'Назад' in number:
        # members_menu(message)
        global_menu(message)
        return

    elif not number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виде числа:')
        show_help_requisites(message)
        return
    # elif number not in users_dict.keys():
    elif int(number) >= len(list_keys) + 1:
        txt = 'Этого пользователя нет в списке'
        msg = bot.send_message(message.chat.id, txt)
        show_help_requisites(message)
        return
    elif users_dict[list_keys[int(number) - 1]]['status_code'] == NEW_ORANGE_STATUS:
        start_orange_invitation(message, users_dict[list_keys[int(number) - 1]]['from_id'],
                                event_id=users_dict[list_keys[int(number) - 1]]['event_id'])
        return
    elif users_dict[list_keys[int(number) - 1]]['status_code'] == NEW_RED_STATUS:
        start_red_invitation(message, users_dict[list_keys[int(number) - 1]]['from_id'],
                             event_id=users_dict[list_keys[int(number) - 1]]['event_id'])
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

@bot.message_handler(func=lambda message: str(message.text).lower() == 'messagepeople')
def message_handler_notifications(message):
    list_id_for_message = read_all_exodus_user()
    message = "*Уважаемые участники тестирования бота Эксодус. Большое спасибо вам за обратную связь!\n\n" \
              "Мы завершили тестирование и готовим бота к запуску в рабочем режиме в течении недели. \n\n" \
              "Тестовая база данных будет обнулена и потребуется новая регистрация. \n\n" \
              "О моменте перезагрузки мы сообщим дополнительно. \n\n" \
              "Все вопросы можно задать в нашем чате поддержки: https://t.me/Exodus_Help\n\n" \
              "Команда разработчиков.*"
    for id in list_id_for_message:
        bot.send_message(id, message, parse_mode='markdown')
    return


@bot.callback_query_handler(func=lambda call: call.data[:17] == 'show_people_link_')
def help_link_generate_menu(call):
    user_id = int(call.data[17:])
    user = read_exodus_user(user_id)
    status = get_status(user.status)
    link = create_link(call.message.chat.id, user_id)
    bot_text = f'Ссылка для помощи {user.first_name} {user.last_name} {status}\n{link}'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=bot_text)
    # return


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
    # print("call",call.message)
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
                  'что вы подтвердили иcполнение {HANDSHAKE} на сумму {sum}.'.format(first_name=first_name,
                                                                                     last_name=last_name,
                                                                                     HANDSHAKE=HANDSHAKE,
                                                                                     sum=event.current_payments)

        bot.send_message(call.message.chat.id, message)

        update_intention_from_all_params(event.from_id, event.to_id, int(event.current_payments), 13)
        # create_history_intention(event.from_id, event.to_id, int(event.current_payments))

        global_menu(call.message)

    elif call.data[0:18] == '6_10_remind_later_':

        global_menu(call.message)
    elif call.data[0:23] == '6_10_send_confirmation_':

        event_id = call.data[23:]
        update_event_type(event_id, 'obligation_recieved')
        event = read_event(event_id)
        user = read_exodus_user(telegram_id=event.from_id)
        user_to = read_exodus_user(telegram_id=event.to_id)
        first_name = user.first_name
        last_name = user.last_name

        message = 'Спасибо! Участнику {first_name} {last_name} будет отправлено уведомление о том, ' \
                  'что вы подтвердили иcполнение {HANDSHAKE} на сумму {sum}.'.format(first_name=first_name,
                                                                                     last_name=last_name,
                                                                                     HANDSHAKE=HANDSHAKE,
                                                                                     sum=event.current_payments)

        bot.send_message(event.from_id,
                         '{HANDSHAKE} {right} {first_name} {last_name} на сумму {sum} исполнено'.format(
                             HANDSHAKE=HANDSHAKE,
                             right=RIGHT_ARROW,
                             first_name=user_to.first_name,
                             last_name=user_to.last_name,
                             sum=event.current_payments))

        bot.send_message(call.message.chat.id, message)

        update_intention_from_all_params(event.from_id, event.to_id, int(event.current_payments), 13)
        # create_history_intention(event.from_id, event.to_id, int(event.current_payments))

        global_menu(call.message)
    elif call.data[0:26] == '6_10_no_send_confirmation_':

        event_id = call.data[26:]
        event = read_event(event_id)
        user = read_exodus_user(telegram_id=event.to_id)
        first_name = user.first_name
        message = 'Участнику {first_name} выслано повторное уведомление исполнить {HANDSHAKE} на сумму {sum} {currency}.' \
                  'Вы можете посмотреть все {HANDSHAKE} в разделе главного меню "Органайзер"'.format(
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
