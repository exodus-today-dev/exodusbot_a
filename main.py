#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.


from datetime import datetime, date, timedelta

import telebot
from aiohttp import web
from telebot import types

import config

bot = telebot.TeleBot(config.API_TOKEN)

# bot.remove_webhook()


# --------------------------------- DB ------------------------------

from models import (read_exodus_user, create_event, session,
                    Exodus_Users, update_exodus_user, create_exodus_user,
                    read_rings_help, create_rings_help, create_intention,
                    update_rings_help, read_intention, read_intention_by_id,
                    update_intention,read_requisites_user, create_requisites_user,
					read_requisites_name,update_requisites_user, delete_requisites_user,
					read_intention_one, update_event_reminder_date, update_event_type, read_event)

from events import invitation_help_orange, invitation_help_red


user_dict = {}
event_dict = {}

temp_dict = {}



transaction = {}

#------------------------------------------------------------------

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


def get_status(text):
    if text == "green":
        status = 'Зелёный \U0001F7E2'
    elif text == "orange":
        status = 'Оранжевый \U0001f7e0'
    elif text == "red":
        status = 'Красный \U0001F534'
    return status


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
        create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
    user = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()

    if user is None:
        welcome(message)
    else:
        if user.status == "green":
            status = 'Зелёный \U0001F7E2'
        elif user.status == "orange":
            status = 'Оранжевый \U0001f7e0'
        elif user.status == "red":
            status = 'Красный \U0001F534'
        else:
            orange_green_wizard(message)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Мой статус')
    btn2 = types.KeyboardButton(text='Транзакции')
    btn3 = types.KeyboardButton(text='Настройки')
    btn4 = types.KeyboardButton(text='Участники')
    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    if not dont_show_status:
        bot.send_message(message.chat.id, 'Ваш текущий статус {}'.format(status))
    bot.send_message(message.chat.id, 'Меню:', reply_markup=markup)

	
def global_check(message):
    """2.0.1"""
    text = message.text
    if text == 'Мой статус':	
        status_menu(message)
    elif text == 'Транзакции':
        transactions_menu(message)
    elif text == 'Настройки':
        configuration_menu(message)
    elif text == 'Участники':
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
        elif user.status == 'red':
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
    btn1 = types.KeyboardButton(text='Редактировать реквизиты')
#    btn2 = types.KeyboardButton(text='Настройки уведомлений')
#    btn3 = types.KeyboardButton(text='Валюта')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
#    markup.row(btn2)
#    markup.row(btn3,btn4)                    # ________________ TODO
    markup.row(btn4)                   
    bot_text = f'Ваши текущие Настройки:\n\
\n\
Валюта: {user.currency}\n\
Уведомления: <статус уведомлений>\n\
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
    if text == 'Редактировать реквизиты':
        requisites_wizard(message)
        return
    elif text == 'Настройки уведомлений':
        bot.send_message(message.chat.id, 'Настройки уведомлений')     # TODO
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
        markup.row(btn1,btn2,btn3)
        markup.row(btn4,btn5,btn6)
        markup.row(btn7)
        msg = bot.send_message(message.chat.id, 'Валюта по умолчанию: {}\nВыберите Другую валюту'.format(user.currency), reply_markup=markup)
        bot.register_next_step_handler(msg, config_wizzard_currency)
        return	

		
def requisites_wizard(message):
    requisites = read_requisites_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    tmp_list = []
    if requisites != []:          
        for requisite in requisites:
            if requisite.is_default:
                tmp_list.append(requisite.name+' (по умолчанию)')
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
                tmp_list.append(requisite.name+' (по умолчанию)')
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
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, requisites_wizard_check)
        return		
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
    markup.row(btn1,btn2)
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
        update_requisites_user(requisite.requisites_id,requisite.name,requisite.value, True)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        requisites_wizard(message)
        return
    elif text == 'Удалить':
        delete_requisite(message,requisite)
        return	
    elif text == 'Назад':
        requisites_wizard(message)
        return		
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, select_requisite_check)
        return		        
    return

def delete_requisite(message,requisite):
    bot_text = f"вы собираетесь удалить реквизиты:\n\
\n\
Название: {requisite.name}\n\
Значение: {requisite.value}"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Да, удалить')
    btn2 = types.KeyboardButton(text='Нет')
    markup.row(btn1,btn2)
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
        select_requisite(message,requisite.name)
        return
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
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
    markup.row(btn1,btn2)
    markup.row(btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, pre_save_requisite_check, requisite_name, requisite_value, edit_id)
    return
	

#---------------------
def unmark_default_requisites(telegram_id):
    all = read_requisites_user(telegram_id)
    for row in all:
        update_requisites_user(row.requisites_id, row.name, row.value, False)
    return
#---------------------	
	
	
	
def pre_save_requisite_check(message, requisite_name, requisite_value, edit_id=0):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
	
    if text == 'Нет':
        add_requisite_name(message)
        return
    elif text == 'Да':
        if edit_id != 0:
            update_requisites_user(edit_id,requisite_name,requisite_value)
        else:
            create_requisites_user(telegram_id=message.chat.id, name=requisite_name, value=requisite_value)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        requisites_wizard(message)
        return
    elif text == 'Да, сделать реквизитами по умолчанию':
        unmark_default_requisites(message.chat.id)
        if edit_id != 0:
            update_requisites_user(edit_id,requisite_name,requisite_value, True)
        else:
            create_requisites_user(message.chat.id, requisite_name, requisite_value, True)
        bot.send_message(message.chat.id, 'Реквизиты сохранены')
        requisites_wizard(message)
        return
    elif text == 'Отмена':
        configuration_menu(message)
        return		
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
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

    status = get_status(user.status)                 # TODO
    bot_text = f"С момента смены вашего статуса на {status}:\n\
\n\
В пользу других:\n\
Мои намерения: {my_intent} {user.currency}\n\
Мои обязательства: {my_obligation} {user.currency}\n\
\n\
В мою пользу:\n\
Намерения: {me_intent} {user.currency}\n\
Обязательства: {me_obligation} {user.currency}"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В пользу других')
    btn2 = types.KeyboardButton(text='В мою пользу')
#    btn3 = types.KeyboardButton(text='За всё время')
    btn4 = types.KeyboardButton(text='Не исполненные')
    btn5 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1,btn2)
#    markup.row(btn3,btn4)
    markup.row(btn4)
    markup.row(btn5)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,transactions_check)  

	
def transactions_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'В пользу других':
        for_other_wizard(message)
        return
    elif text == 'В мою пользу': 
        for_my_wizard(message)
        return
    elif text == 'За всё время':
        for_all_time_wizard(message)
        return
    elif text == 'Не исполненные':
        not_executed_wizard(message)
        return
    elif text == 'Главное меню':
        global_menu(message)
        return


	
def members_menu(message):
    """2.5"""
    
    user = read_exodus_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup()
    ref = ''
    if user.ref != '': 
        referal = read_exodus_user(user.ref)
        ref='{} {}'.format(referal.first_name,referal.last_name)

    transactions_in_count = count_in_transactions(message.chat.id)
    transactions_out_count = count_out_transactions(message.chat.id)

    btn1 = types.KeyboardButton(text='Ссылка на мой профиль')
    btn2 = types.KeyboardButton(text='В мою пользу ({})'.format(transactions_in_count))
    btn3 = types.KeyboardButton(text='В пользу других ({})'.format(transactions_out_count))
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)                   
    markup.row(btn4)                    # ________________ TODO

    currency = user.currency

    user_id = message.chat.id

    intentions_out_sum = sum_out_intentions(user_id)
    intentions_in_sum = sum_in_intentions(user_id)
    obligations_in_sum = sum_in_obligations(user_id)
    executed_in_sum = sum_in_executed(user_id)
    obligations_out_sum = sum_out_obligations(user_id)
    executed_out_sum = sum_out_executed(user_id)

    transactions_in_count = count_in_transactions(user_id)
    transactions_out_count = count_out_transactions(user_id)

    bot_text = 'Я в сети Эксодус с {data}\n '\
               'Меня пригласил: {ref}\n' \
               '\n' \
               'В мою пользу ({tr_in}):\n' \
               '  Намерений: {int_in} {currency}\n' \
               '  Обязательств: {obl_in} {currency}\n' \
               '  Исполнено: {exe_in} {currency}\n' \
               '\n' \
               'В пользу других ({tr_out}):\n' \
               '  Намерений: {int_out} {currency}\n' \
               '  Обязательств: {obl_out} {currency}\n' \
               '  Исполнено: {exe_out} {currency}'.format(
                    data=user.create_date.strftime("%d %B %Y %I:%M%p"),
					ref=ref, currency=currency, int_in=intentions_in_sum,
                    obl_in=obligations_in_sum, exe_in=executed_in_sum,
                    int_out=intentions_out_sum, obl_out=obligations_out_sum,
                    exe_out=executed_out_sum, tr_in=transactions_in_count,
                    tr_out=transactions_out_count)

    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, members_check)
    return

# new # >>>

def print_members_list_in_network(message, member_id, direction):
    #""" 5.2 """

    #alert #empty.check

    intentions = None

    if direction == 'in':
        intentions = read_intention(to_id=member_id).distinct("from_id")
    elif direction == 'out':
        intentions = read_intention(from_id=member_id).distinct("to_id")

    for i, row in enumerate(intentions.all()):
            #warning
            #  no.pagination.by.10

            #warning
            #  crash: if no user found

            user = None

            if direction == 'in':
                user = read_exodus_user(row.from_id)
            elif direction == 'out':
                user = read_exodus_user(row.to_id)
            try:
                status = get_status(user.status)                #TODO отваливается при пустом или не существующем пользователе
            except:
                status = ''
            msg_text = '{i}. {first_name} {last_name}, {status}'.format(
                i=i+1, first_name=user.first_name,
                last_name=user.last_name, status=status)
            msg = bot.send_message(message.chat.id, msg_text)

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
    executed = read_intention(to_id=user_id, status=13)
    count += executed.count()
    return count

def count_out_transactions(user_id):
    count = 0
    intentions = read_intention(from_id=user_id, status=1)
    count += intentions.count()
    obligations = read_intention(from_id=user_id, status=11)
    count += obligations.count()
    obligations = read_intention(from_id=user_id, status=12)
    count += obligations.count()
    executed = read_intention(from_id=user_id, status=13)
    count += executed.count()
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
    #warning
    # ТЗ. какая математика у этих подсчётов?
    #     перепроверить все

    status_info_text = ''
    max_payment_text = ''
    min_payment_text = ''

    to_collect = float(user.max_payments) - \
                 float(sum_in_obligations(user.telegram_id)) - \
                 float(sum_in_intentions(user.telegram_id))

    to_collect_text = '  сколько ещё нужно собрать: {}'.format(to_collect)

    if user.status == 'red':
        days = timedelta(days=user.days)
        end_date = user.start_date + days
        end_date_text = '  до какой даты: {}'.format(end_date)

        status_info_text = to_collect_text + '\n' + end_date_text + '\n'
    elif user.status == 'orange':
        max_payment_text = '  сколько нужно в месяц: {}'.format(user.max_payments)
        min_payment_text = '  минимальный платёж: {}'.format(user.min_payments)
        status_info_text = max_payment_text + '\n' + \
                           to_collect_text + '\n' + \
                           min_payment_text + '\n'

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

    user_info_preview = 'Имя участника {first_name} {last_name}\n' \
                        'В сети Эксодус с {data}\n' \
                        'Пригласил: {ref}\n' \
                        '\n' \
                        'Статус: {status}\n' \
                        '\n' \
                        'В его пользу ({tr_in}):\n' \
                        '  Намерений: {int_in} {currency}\n' \
                        '  Обязательств: {obl_in} {currency}\n' \
                        '  Исполнено: {exe_in} {currency}\n' \
                        '\n' \
                        'В пользу других ({tr_out}):\n' \
                        '  Намерений: {int_out} {currency}\n' \
                        '  Обязательств: {obl_out} {currency}\n' \
                        '  Исполнено: {exe_out} {currency}'.format(
                                data=data.strftime("%d %B %Y %I:%M%p"), ref=ref,
                                first_name=first_name, last_name=last_name,
                                status=status, currency=currency, int_in=intentions_in_sum,
                                obl_in=obligations_in_sum, exe_in=executed_in_sum,
                                int_out=intentions_out_sum, obl_out=obligations_out_sum,
                                exe_out=executed_out_sum, tr_in=transactions_in_count,
                                tr_out=transactions_out_count)

    return user_info_preview

def generate_user_info_text(user, self_id):
    """ 5.2 """

    ref = user.ref
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
                     'Имя участника {first_name} {last_name}\n' \
                     'Статус: {status}\n' \
                     '\n'.format(data=data.strftime("%d %B %Y %I:%M%p"), ref=ref,
                                 first_name=first_name, last_name=last_name,
                                 status=status)

    if user.status != 'green':
        status_info_text = generate_status_info_text(user)
        user_info_text += status_info_text + '\n'

    if in_my_circle_alpha(user.telegram_id, self_id):
        user_info_text += 'В его пользу ({tr_in}):\n' \
                          '  Намерений: {int_in} {currency}\n' \
                          '  Обязательств: {obl_in} {currency}\n' \
                          '  Исполнено: {exe_in} {currency}\n' \
                          '\n' \
                          'В пользу других ({tr_out}):\n' \
                          '  Намерений: {int_out} {currency}\n' \
                          '  Обязательств: {obl_out} {currency}\n' \
                          '  Исполнено: {exe_out} {currency}'.format(
                                currency=currency, int_in=intentions_in_sum,
                                obl_in=obligations_in_sum, exe_in=executed_in_sum,
                                int_out=intentions_out_sum, obl_out=obligations_out_sum,
                                exe_out=executed_out_sum, tr_in=transactions_in_count,
                                tr_out=transactions_out_count)
    else:
        user_info_text += 'Информация о намерениях и обязательствах доступна ' \
                          'только для участников в моей сети.'
    return user_info_text


def members_list_in_network_menu(message, member_id, direction):
    """ 5.2 """

    print_members_list_in_network(message, member_id, direction)

    markup = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton(text='Показать ещё 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)

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

    btn1 = types.KeyboardButton(text='Ссылка на профиль')
    btn2 = types.KeyboardButton(text='В пользу этого участника '
                                     '({tr_in})'.format(
                                     tr_in=transactions_in_count))
    btn3 = types.KeyboardButton(text='Этот участник в пользу других '
                                     '({tr_out})'.format(
                                     tr_out=transactions_out_count))
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)

    bot_text = '\nВыберите пункт меню'
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)

    bot.register_next_step_handler(msg, selected_member_action_check,
                                   member_id)


def selected_member_action_check(message, member_id): #bookmark
    """ 5.2 """
    text = message.text

    if text == 'Ссылка на профиль':
        members_menu_profile_link(message, member_id)
    elif text[:24] == 'В пользу этого участника':
        members_list_in_network_menu(message, member_id, 'in')
    elif text[:29] == 'Этот участник в пользу других':
        members_list_in_network_menu(message, member_id, 'out')
    elif text == 'Главное меню':
        global_menu(message)
    else:
        selected_member_action_menu(message, member_id)


def members_list_in_network_check(message, member_id, direction):
    """ 5.2 """
    text = message.text

    if text == 'Показать ещё 10': #bug # дважды печатает список
        print_members_list_in_network(message, member_id, direction)
        members_list_in_network_menu(message, member_id, direction)
        return
    elif text == 'Назад':
        members_menu(message)
        return
    else:
        try:
            #bookmark #debug.bookmark #dev.bookmark

            members_list = get_members_list(member_id, direction)
            selected_id = int(text)
            user = read_exodus_user(members_list[selected_id])
            user_info_text = generate_user_info_text(user, message.chat.id)
            msg = bot.send_message(message.chat.id, user_info_text)
            selected_member_action_menu(message, members_list[selected_id])
        except:
            msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
            bot.register_next_step_handler(msg,
                                           members_list_in_network_check,
                                           member_id, direction)
        return
    return


# new # <<<

def members_check(message):
    text = message.text
#    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Ссылка на мой профиль':
        members_menu_profile_link(message, message.chat.id)
        return
    elif text[0:12] == 'В мою пользу':
        members_list_in_network_menu(message, message.chat.id, 'in')
        return
    elif text[0:15] == 'В пользу других':
        members_list_in_network_menu(message, message.chat.id, 'out')
        return
    elif text == 'Главное меню':
        global_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, members_check)  
        return		
    return        
    


	
#------------- 


def for_other_wizard(message):
    """4.1"""

    members = []
    user_id = message.chat.id
    intentions = read_intention(from_id = user_id, status=1)
    intentions_count = intentions.count()
    for inten in intentions:
        members.append(inten.to_id)
    obligations = read_intention(from_id = user_id, status=11)
    obligations_count = obligations.count()
    for obligation in obligations:
        members.append(obligation.to_id)
    count = len(set(members))

    bot_text = f"Вами записано {intentions_count} намерений и {obligations_count} обязательств в пользу {count} участников:"
    bot.clear_step_handler(message)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"Намерения ({intentions_count})")
    btn2 = types.KeyboardButton(text=f"Обязательства ({obligations_count})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_other_check)  
    return

def for_other_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Намерения (0)':
        msg = bot.send_message(message.chat.id, 'у Вас нет намерений')
        bot.register_next_step_handler(msg, for_other_check)
    elif text == 'Обязательства (0)':
        msg = bot.send_message(message.chat.id, 'у Вас нет обязательств')
        bot.register_next_step_handler(msg, for_other_check)
    elif text[0:9] == 'Намерения':
        for_other_wizard_intention(message)
    elif text[0:13] == 'Обязательства':
        bot.send_message(message.chat.id, 'Обязательства')
        for_other_wizard_obligation(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
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
        user_to = read_exodus_user(telegram_id = intent.to_id)
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
    bot.register_next_step_handler(msg,for_other_wizard_intention_check)  
    return

def for_other_wizard_intention_check(message):
    intention_number = message.text
    if intention_number == 'Назад':
        for_other_wizard(message)
        return    
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виду цифры:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими намерениями:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return        
    transaction[message.chat.id] = intention_number   
    intention_for_needy(message, reminder_call=False, intention_id=None)
    return

#bookmark
def intention_for_needy(message, reminder_call, intention_id):
    """6.7"""

    if reminder_call is True:
        intention = read_intention_by_id(intention_id)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        intention_id = transaction[message.chat.id]
        intention = read_intention_by_id(intention_id)

    user_to = read_exodus_user(telegram_id=intention.to_id)
    status = get_status(user_to.status)
    
    bot_text='Ваше намерение-{intention_id} в пользу:\n\
участника {first_name} {last_name} со статусом {status}\n\
На сумму {payment} {currency}'.format(  intention_id=intention_id,
										first_name=user_to.first_name,
                                        last_name=user_to.last_name,
                                        status=status,
                                        payment=intention.payment,
                                        currency=intention.currency)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В обязательство')
    btn2 = types.KeyboardButton(text='Редактировать')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    btn4 = types.KeyboardButton(text='Отменить намерение')
    markup.row(btn1,btn2)
    markup.row(btn3,btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,intention_for_needy_check)  
    return

def intention_for_needy_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'В обязательство':
        intention_to_obligation(message)
    elif text == 'Редактировать':
        edit_intention(message)
        return
    elif text == 'Напомнить позже':
        remind_later(message)
        return
    elif text == 'Отменить намерение':
        cancel_intention(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return

def intention_to_obligation(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Вы перевели в обязательство свое намерение помогать участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency}\n\
Когда участник {user_to.first_name} {user_to.last_name} решит что делать с вашим обязательством, вы получите уведомление."
    update_intention(intention_id, status=11)
    bot.send_message(message.chat.id,bot_text)
    global_menu(message, True)
    return

#bookmark
def remind_later(message, intention_id, reminder_type, reminder_status):
    """ 6.3, 6.7, 6.8 """
#  create_event       ---------------------------- TODO Создать уведомление - бот вышлет это через сутки


    reminder_date = date.today() + timedelta(days=1)

    # reminder_type = 'reminder_in'   # 6.8
    # reminder_type = 'reminder_out'  # 6.3, 6.7
    # status = 'obligation' # 6.3
    # status = 'intention'  # 6.7

    create_event(from_id = message.chat.id,
                 first_name = None,
                 last_name = None,
                 status = reminder_status,
                 type = reminder_type,
                 min_payments = None,
                 current_payments = None,
                 max_payments = None,
                 currency = None,
                 users = None,
                 to_id = intention_id,
                 reminder_date = reminder_date,
                 sent=False)  # someday: intention_id

    #message = "Участнику {first_name} {last_name} отправлено ваше решение " \
    #          "исполнить обязательства на сумму {sum} {currency}.". \
    #          format(first_name=None, last_name=None, sum=None, currency=None)
    global_menu(message)
    return

def edit_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    bot_text = f"Ваше намерение было на сумму {intention.payment}\n\
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
    if not payment.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg, edit_intention_check)
        return
    update_intention(intention_id=intention_id,payment=payment)
    intention_for_needy(message, reminder_call=False, intention_id=None)
    return

	
def cancel_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)
    bot_text = f"Вы хотите отменить свое намерение помогать участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency}?"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Нет')
    btn2 = types.KeyboardButton(text='Да')
    markup.row(btn1,btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,cancel_intention_check)  
    return

def cancel_intention_check(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.user_to)
    bot_text = f"Ваше намерение помогать участнику {user_to.first_name} {user_to.last_name} на {intention.payment} {intention.currency} отменено."
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Нет':
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return
    elif text == 'Да':
        update_intention(intention_id, status=0)
        bot.send_message(message.chat.id, bot_text)
        global_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return


def for_other_wizard_obligation(message):
    intentions = read_intention(from_id=message.chat.id, status=11)
    n = 0
    bot_text = ''
    left_days = get_left_days()
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
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
    bot.register_next_step_handler(msg,for_other_wizard_obligation_check) 
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
    intention = read_intention_by_id(intention_id=obligation_number, from_id=message.chat.id, status=11)
    if intention is None:
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими намерениями:')
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
        bot.delete_message(message.chat.id, message.message_id)
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
        

       			  
          
    bot_text = f"У Вас обязательство перед участником {user_to.first_name} {user_to.last_name} статус {status} на сумму {intention.payment} {intention.currency}\n\
Деньги можно отправить на реквизиты:"
# отдельное сообщени для реквизитов - 
# <значение> (чтобы удобно скопировать)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Другие реквизиты')       # TODO сделать и подвязать реквизиты
    btn2 = types.KeyboardButton(text='Да, я отправил деньги')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
	
    bot.send_message(message.chat.id, f"{req_name}")
    bot_text = f"{req_value}"
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    
    bot.register_next_step_handler(msg,obligation_for_needy_check)  
    return

	
def obligation_for_needy_check(message):
    text = message.text
    if text == 'Другие реквизиты':
        select_requisites(message)             # TODO сделать и подвязать реквизиты
    elif text == 'Да, я отправил деньги':
        obligation_sent_confirm(message)
        return
    elif text == 'Напомнить позже':
        remind_later(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return

	
def select_requisites(message):              # TODO сделать и подвязать реквизиты
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
    bot.register_next_step_handler(msg,obligation_sent_confirm_check)  
    return


def obligation_sent_confirm_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Да':
        obligation_sent_confirm_yes(message)  
    elif text == 'Нет':
        obligation_for_needy(message, reminder_call=False, intention_id=None)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check) 
    return
	

def obligation_sent_confirm_yes(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.to_id)	
    bot_text = f"Спасибо!\n\
Участнику  {user_to.first_name} {user_to.last_name} будет отправлено уведомление о исполненном обязательстве на сумму {user_to.first_name} {user_to.last_name}."
    bot.send_message(message.chat.id, bot_text)
    update_intention(intention_id=intention_id,status=12)
    global_menu(message)
    return


	

def for_my_wizard(message):
    """4.2"""
    members = []
    user_id = message.chat.id
    intentions = read_intention(to_id = user_id, status=1)
    intentions_count = intentions.count()
    for inten in intentions:
        members.append(inten.from_id)
    obligations = read_intention(to_id = user_id, status=11)
    obligations_count = obligations.count()
    for obligation in obligations:
        members.append(obligation.from_id)
    count = len(set(members))
    bot_text = f"{count} участников записали в вашу пользу {intentions_count} намерений и {obligations_count} обязательств:"        # TODO

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"Намерения ({intentions_count})")
    btn2 = types.KeyboardButton(text=f"Обязательства ({obligations_count})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_my_check)  
    return


def for_my_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Намерения (0)':
        msg = bot.send_message(message.chat.id, 'у Вас нет намерений')
        bot.register_next_step_handler(msg, for_my_check)
    elif text == 'Обязательства (0)':
        msg = bot.send_message(message.chat.id, 'у Вас нет обязательств')
        bot.register_next_step_handler(msg, for_my_check)
    elif text[0:9] == 'Намерения':
        for_my_wizard_intention(message)
    elif text[0:13] == 'Обязательства':
        for_my_wizard_obligation(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return



def for_my_wizard_intention(message):
    intentions = read_intention(to_id=message.chat.id, status=1)
    bot_text = f"Намерения в мою пользу:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id = intent.from_id)
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
    bot.register_next_step_handler(msg,for_my_wizard_intention_check)  
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
    intention = read_intention_by_id(intention_id=intention_number)
    if intention is None:
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими намерениями:')
        bot.register_next_step_handler(msg, for_my_wizard_intention_check)
        return
    transaction[message.chat.id] = intention_number
    intention_for_me(message)
    return


def intention_for_me(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user = read_exodus_user(telegram_id = intention.from_id)
    bot_text = f"{intention.create_date.strftime('%d %B %Y %I:%M%p')}\n\
Участник {user.first_name} {user.last_name} записал свое намерение помогать вам на {intention.payment} {intention.currency}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,intention_for_me_check)
    return


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
    bot_text = f"Обязательства в мою пользу:\n"
    for intent in intentions:
        n = n + 1
        user = read_exodus_user(telegram_id = intent.from_id)
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
    bot.register_next_step_handler(msg,for_my_wizard_intention_check)  
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
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими обязательством:')
        bot.register_next_step_handler(msg, for_my_wizard_obligation_check)
        return
    transaction[message.chat.id] = intention_number
    # intention_for_me(message) #bookmark # for_me_obligation(message)
    for_me_obligation(message, reminder_call=False, intention_id=None)
    return


def for_me_obligation(message, reminder_call, intention_id):
    """6.8"""

    if reminder_call is True:
        intention = read_intention_by_id(intention_id=intention_id)
    else:
        intention_id = transaction[message.chat.id]
        intention = read_intention_by_id(intention_id=intention_id)

    user = read_exodus_user(telegram_id=intention.from_id)

    bot_text = f"Участник {user.first_name} {user.last_name} записал обязательство в вашу пользу на сумму {intent.payment} {intent.currency}"

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Запрос на исполнение')
    btn2 = types.KeyboardButton(text='Хранить')
    btn3 = types.KeyboardButton(text='Напомнить позже')
    markup.row(btn1)
    markup.row(btn2,btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, for_me_obligation_check, obligation_id)
    return


def for_me_obligation_check(message, obligation_id):
    """ 6.8 """
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Запрос на исполнение':
        obligation_to_execution(message, obligation_id)
    elif text == 'Хранить':
        keep_obligation(message)
    elif text == 'Напомнить позже':
        remind_later(message, obligation_id)
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_me_obligation_check, intention_id)
    return


def obligation_to_execution(message, obligation_id):
    """ 6.8 """
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)

    user = read_exodus_user(telegram_id=intention.from_id)
    update_intention(intention_id=intention_id, status=15)
    bot_text = f'Участнику {user.first_name} {user.last_name} отправлено ваше решение исполнить ' \
               f'обязательство на сумму {intention.payment} {intention.currency}.'

    payment = intention.payment
    currency = intention.currency
    intentions = read_intention(to_id=obligation_id)
    users_count = len(intentions.all())
    to_id = intention.to_id
    reminder_date = date.today()

    create_event(from_id = message.chat.id,
                 first_name = None,
                 last_name = None,
                 status = None,
                 type = 'obligation_money_requested',
                 min_payments = None,
                 current_payments = payment,
                 max_payments = None,
                 currency = currency,
                 users = users_count,
                 to_id = to_id,
                 reminder_date = reminder_date,
                 sent=False)

    msg = bot.send_message(message.chat.id, bot_text)

    global_menu(message)

    return


def keep_obligation(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f'Обязательство участника {user.first_name} {user.last_name} на ' \
               f'сумму  {intent.payment} {intent.currency} будет хранится у вас, ' \
               f'пока вы не примите решение.\n' \
               f'Посмотреть все обязательства можно в разделе главного меню ' \
               f'"транзакции" > "обязательства"'
    global_menu(message)
    return



def for_all_time_wizard(message):
    """4.3"""
    bot_text ='За все время использования бота:\n\
\n\
В пользу других:\n\
Мои намерения: <сумма> <валюта>\n\
Мои обязательства: <сумма> <валюта>\n\
Исполнено на сумму: <сумма> <валюта>\n\
\n\
В мою пользу:\n\
Намерения: <сумма> <валюта>\n\
Обязательства: <сумма> <валюта>\n\
Исполнено на сумму: <сумма> <валюта>'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В пользу других')
    btn2 = types.KeyboardButton(text='В мою пользу')
    btn3 = types.KeyboardButton(text='Скачать статистику (csv)')
    btn4 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    markup.row(btn4)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_all_time_check)  
    return

def for_all_time_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'В пользу других':
        bot.send_message(message.chat.id, 'not work yet')                # TODO
        global_menu(message)
    elif text == 'В мою пользу':
        bot.send_message(message.chat.id, 'not work yet')                # TODO
        global_menu(message)
    elif text == 'Скачать статистику (csv)':
        bot.send_message(message.chat.id, 'not work yet')                # TODO
        global_menu(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return
    

	
def not_executed_wizard(message):
    """4.4"""
    user_id = message.chat.id
    intentions = read_intention(to_id = user_id, status=12)
    if intentions is None:
        for_me_intent = 0
    else:
        for_me_intent = intentions.count()
	
    intentions = read_intention(from_id = user_id, status=12)
    if intentions is None:
        for_other_intent = 0
    else:
        for_other_intent = intentions.count()
    bot_text ='Не исполненными считаются те обязательства, которые не подтвердил получатель.'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text=f"В мою пользу ({for_me_intent})")
    btn2 = types.KeyboardButton(text=f"В пользу других ({for_other_intent})")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,not_executed_check)  
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
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, not_executed_check)    
    return
    


def not_executed_wizard_to_me(message):
    intentions = read_intention(to_id=message.chat.id, status=12)
    bot_text = f"Я не подтвердил {intentions.count()} обязательств в мою пользу:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id = intent.from_id)
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
    bot.register_next_step_handler(msg,not_executed_wizard_to_me_check)  
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
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими обязательством:')
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
    bot_text = f"Я не подтвердил исполненное обязательство в мою пользу:\n\
\n\
Дата: {intention.create_date.strftime('%d %B %Y')}\n\
Время: {intention.create_date.strftime('%I:%M%p')}\n\
Отправитель: {user.first_name} {user.last_name} {get_status}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"                                       # TODO реквезиты
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text="Я получил эту сумму")
    btn2 = types.KeyboardButton(text="Повторный запрос на исполнение")
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,executed_not_confirm_check)  
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
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
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
    bot.register_next_step_handler(msg,executed_confirm_check)  
    return

	
def executed_confirm_check(message):
    text = message.text
    if text == 'Назад':
        executed_not_confirm_me(message)
        return
    if text == 'Да, я получил':
        executed_confirm_confirmed(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, executed_confirm_check)  
    return		
	

def executed_confirm_confirmed(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f"Спасибо! Участнику {user.first_name} {user.last_name} будет отправлено уведомление о том, что его обязательство исполнено."
    # create_event        TODO 
    not_executed_wizard_for_all(message)
    return
	
def repeat_executed_request(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id=intention_id)
    user = read_exodus_user(telegram_id=intention.from_id)
    bot_text = f"Спасибо! Отправителю {user.first_name} {user.last_name} будет отправлено уведомление о том, что деньги все еще не получены."
    # create_event        TODO 
    not_executed_wizard_for_all(message)
    return	
	
	
def not_executed_wizard_for_all(message):
    intentions = read_intention(from_id=message.chat.id, status=12)
    bot_text = f"{intentions.count()} моих обязательств в пользу других не было подтверждено:\n"
    for intent in intentions:
        user = read_exodus_user(telegram_id = intent.to_id)
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
    bot.register_next_step_handler(msg,not_executed_wizard_for_all_check)  
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
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими обязательством:')
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
    bot_text = f"Исполненное мной обязательство не было подтверждено:\n\
\n\
Дата: {intention.create_date.strftime('%d %B %Y')}\n\
Время: {intention.create_date.strftime('%I:%M%p')}\n\
Получатель: {user.first_name} {user.last_name} {get_status(user.status)}\n\
Сумма: {intention.payment} {intention.currency}\n\
Реквизиты: {req_name} {req_value}"                                       # TODO реквезиты
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text="Я отправил эту сумму")
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,executed_not_confirm_check)  
    return

	
def executed_not_confirm_check(message):
    text = message.text
    if text == 'Назад':
        not_executed_wizard_for_all(message)
        return
    if text == 'Я отправил эту сумму':
        executed_was_sent(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, executed_not_confirm_check)  
    return		


def executed_was_sent(message):
    intention_id = transaction[message.chat.id]     # recode: intention_id as
    intention = read_intention_by_id(intention_id)  #   argument
    user = read_exodus_user(intention.to_id)

    intentions = read_intention(to_id=intention.to_id)
    users_count = len(intentions.all())
    reminder_date = date.today()

    # 6.4
    create_event(from_id = message.chat.id,
                 first_name = None,
                 last_name = None,
                 status = None,
                 type = 'obligation_sended',
                 min_payments = None,
                 current_payments = payment,
                 max_payments = None,
                 currency = currency,
                 users = users_count,
                 to_id = to_id,
                 sent=False,
                 reminder_date = reminder_date)

    bot_text = f"Спасибо! Получателю {user.first_name} {user.last_name} " \
               f"будет отправлено уведомление о том, что деньги отправлены."
    bot.send_message(message.chat.id, bot_text)

    # not_executed_wizard(message)
    not_executed_wizard_for_all(message)

    return
    
	
	
	
def members_menu_profile_link(message, member_id):
    user = read_exodus_user(member_id)
    bot.delete_message(message.chat.id, message.message_id)
    if user.status == 'green':	
        bot_text = 'Имя участника {} {}\n\
Статус: Зелёный \U0001F7E2'.format(user.first_name,user.last_name)
    elif user.status == 'orange':
        bot_text = 'Имя участника {} {}\n\
Статус: Оранжевый \U0001f7e0\n\
\n\
Период: Ежемесячно\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}'.format(	user.first_name,
								user.last_name, 
								user.current_payments, 
								user.max_payments, 
								user.currency,
								user.max_payments-user.current_payments,
								user.currency,
							    0)               # ------------ TODO
    elif user.status == 'red':
        d0 = user.start_date
        d1 = date.today()
        delta = d1 - d0
        days_end = user.days - delta.days
        bot_text = 'Имя участника {} {}\n\
Статус: Красный \U0001F534\n\
\n\
Требуется помощь на сумму {} {}\n\
Осталось {} дней из {}\n\
Уже помогает: {} человек'.format(	user.first_name,
								user.last_name,
								user.max_payments, 
								user.currency,
								days_end,
								user.days,
							    0)               # ------------ TODO	
    else:
        bot_text = 'СТАТУС НЕ УКАЗАН. ОШИБКА'
    bot.send_message(message.chat.id, bot_text)
    link = create_link(user.telegram_id,user.telegram_id)
    bot.send_message(message.chat.id, link)
    global_menu(message,True)	
	
	
def config_wizzard_currency(message):
    """3.2"""
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text == 'USD':
        update_exodus_user(message.chat.id, currency = 'USD')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: USD')
        global_menu(message)
    elif text == 'Euro':
        update_exodus_user(message.chat.id, currency = 'Euro')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Euro')
        global_menu(message)
    elif text == 'Гривны':
        update_exodus_user(message.chat.id, currency = 'Гривны')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Гривны')
        global_menu(message)
    elif text == 'Рубли':
        update_exodus_user(message.chat.id, currency = 'Рубли')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: Рубли')
        global_menu(message)
    elif text == 'GBR':
        update_exodus_user(message.chat.id, currency = 'GBR')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: GBR')
        global_menu(message)
    elif text == 'CAD':
        update_exodus_user(message.chat.id, currency = 'CAD')
        bot.send_message(message.chat.id, 'Валюта по умолчанию: CAD')
        global_menu(message)
    elif text == 'Главное меню':
        global_menu(message)
        return	
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, config_wizzard_currency)	









@bot.message_handler(commands=['start'])
def welcome(message):
    """1.0"""
    bot.clear_step_handler(message)
    referal = ref_info(message.text)
    bot.send_message(message.chat.id,"Добро пожаловать в бот Exodus.")
    if referal[0] != '':
        user_from = read_exodus_user(referal[0])
        user_to = read_exodus_user(referal[1])
        bot_text = 'Участник {} {} приглашает вас помогать участнику {} {}'.format(	user_from.first_name,
																					user_from.last_name,
																					user_to.first_name,
																					user_to.last_name)
        bot.send_message(message.chat.id,bot_text)
        if user_to.status == 'orange':
            start_orange_invitation(message,user_to.telegram_id)
        elif user_to.status == 'red':
            start_red_invitation(message,user_to.telegram_id)
    else:
        start_without_invitation(message)

			
			
def start_without_invitation(message):
    """1.1"""
	
    exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
    if not exists:
        create_exodus_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
    if exists.status == '':
        orange_green_wizard(message)
    else:
        global_menu(message)    			
			


#----------------------------- 6.1 ORANGE ----------------------			
def start_orange_invitation(message,user_to):
    """6.1"""
    user = read_exodus_user(telegram_id=user_to)
    ring = read_rings_help(user.telegram_id)
	
    intention = read_intention_one(message.chat.id, user.telegram_id, 1)
    if intention is not None:
        bot_text = f'Вы уже помогаете участнику {user.first_name} {user.last_name}.'
        bot.send_message(message.chat.id, bot_text)
        transaction[message.chat.id] = intention.intention_id
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return		
	
    if ring is None:
        users_count = 0
    else:
        users_count = len(ring.help_array)

    status = 'Оранжевый \U0001f7e0'
    bot_text = 'Участник {first_name} {last_name} - {status}\n\
Период: Ежемесячно\n\
Собрано {current} из {max} {currency}\n\
Ожидается {need} {currency}\n\
Всего участников: {users_count}\n\
\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {min} {currency}'.format(first_name = user.first_name, 
								last_name = user.last_name,
								status = status,
								current = user.current_payments,
								max = user.max_payments,
								currency = user.currency,
								need = user.max_payments-user.current_payments,
								users_count = users_count,
								min = user.min_payments)

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    markup.row(btn1)
    markup.row(btn2, btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    temp_dict[message.chat.id] = user       # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    temp_dict[message.chat.id].step = 'orange'        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память

    bot.register_next_step_handler(msg, orange_invitation_check)    

	
def orange_invitation_check(message):
    """6.1.1"""    
    user_to = temp_dict[message.chat.id]        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    text = message.text
    if text[0:19] == 'Показать участников':
        show_all_members(message,user_to)	
    elif text == 'Нет'.format(0):        
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            start_without_invitation(message)
        else:
            global_menu(message)
    elif text == 'Да'.format(0):
        orange_invitation_wizard(message,user_to)
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, orange_invitation_check)	

		

def orange_invitation_wizard(message, user_to): 
    """6.1.2"""
    temp_dict[message.chat.id]  = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, 'Введите минимальную сумму помощи в {}:'.format(user.currency),reply_markup=markup)
    bot.register_next_step_handler(msg, orange_invitation_wizard_check)
	
	

def orange_invitation_wizard_check(message):   #------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if message.text == 'Назад':
        start_orange_invitation(message,user)
        return
    if not invitation_sum.isdigit():
        msg = bot.send_message(message.chat.id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg,orange_invitation_wizard_check)
        return
    elif float(invitation_sum) < user.min_payments:
        msg = bot.send_message(message.chat.id, 'Пожалуйста введите другую сумму.\n\
Минимальная сумма {} {}'.format(user.min_payments,user.currency))
        bot.register_next_step_handler(msg,orange_invitation_wizard_check)
        return
	
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array = []
        array.append(message.chat.id)
        create_rings_help(user.telegram_id,array)
    else:
        array = ring.help_array	
        array.append(message.chat.id)
        update_rings_help(user.telegram_id,array)
    ring = read_rings_help(user.telegram_id)
    users_count = len(ring.help_array)
    status = 'Оранжевый \U0001f7e0'
    bot_text = f'Участник {user.first_name} {user.last_name} - {status}\n\
Период: Ежемесячно\n\
Собрано {user.current_payments} из {user.max_payments} {user.currency}\n\
Ожидается {user.max_payments-user.current_payments} {user.currency}\n\
Всего участников: {users_count}\n\
Обсуждение: {user.link}\n\
\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {user.min_payments} {user.currency}'
 
    create_intention(message.chat.id, user.telegram_id, invitation_sum, user.currency,status=1)
    create_event(	from_id=message.chat.id, 
					first_name=user.first_name,            # TODO not needed
					last_name=user.last_name,             # TODO not needed
					status='orange', 
					type='notice', 
					min_payments=user.min_payments, 
					current_payments=user.current_payments, 
					max_payments=user.max_payments,
					currency=user.currency, 
					users=0, 
					to_id=user.telegram_id, 
					sent=False,
                    reminder_date = date.today()) # someday: intention_id
    bot.send_message(message.chat.id, bot_text)
    global_menu(message,True)		
			
#------------------------------------------------------		




def show_all_members(message,user_to):
    bot.delete_message(message.chat.id, message.message_id)
    user = user_to
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        users_count = 0
    else:
        users_count = len(ring.help_array)
    bot_text = 'Участнику {} {} помогают {} участников:\n'.format(user.first_name,user.last_name,users_count)

    bot_text = bot_text + '\n\
В моей сети:\n\
1. <Имя>\n\
2. <Имя>\n\
...\n\
\n\
Остальные участники:\n\
1. <Имя>\n\
2. <Имя>\n\
...'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg, show_all_members_check)  

def show_all_members_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    if message.text == 'Назад':
        if temp_dict[message.chat.id].step == 'orange':
            start_orange_invitation(message,temp_dict[message.chat.id].telegram_id)
        elif temp_dict[message.chat.id].step == 'red':
            start_red_invitation(message,temp_dict[message.chat.id].telegram_id)
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, show_all_members_check)
		





		
#----------------------- 6.2 RED ---------------------------			
def start_red_invitation(message,user_to):
    """6.2"""
    user = read_exodus_user(telegram_id=user_to)
    ring = read_rings_help(user.telegram_id)
	
    intention = read_intention_one(message.chat.id, user.telegram_id, 1)
    if intention is not None:
        bot_text = f'Вы уже помогаете участнику {user.first_name} {user.last_name}.'
        bot.send_message(message.chat.id, bot_text)
        transaction[message.chat.id] = intention.intention_id
        intention_for_needy(message, reminder_call=False, intention_id=None)
        return	

    user = user_to
    ring = read_rings_help(user_to.telegram_id)
    if ring is None:
        users_count = 0
    else:
        users_count = len(ring.help_array)
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days
    status = get_status(user.status)
    bot_text = f'Участник {user.first_name} {user.last_name} - {status}\n\
Период: Ежемесячно\n\
Собрано {user.current_payments} из {user.max_payments} {user.currency}\n\
Ожидается {user.max_payments-user.current_payments} {user.currency}\n\
Всего участников: {users_count}\n\
Осталось {days_end} дней из {user.days}\n\
Обсуждение: {user.link}\n\
\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {user.min_payments} {user.currency}'

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать участников ({})'.format(users_count))
    btn2 = types.KeyboardButton(text='Нет')
    btn3 = types.KeyboardButton(text='Да')
    markup.row(btn1)
    markup.row(btn2, btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    temp_dict[message.chat.id] = user_to        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    temp_dict[message.chat.id].step = 'red'        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память

    bot.register_next_step_handler(msg, red_invitation_check)    

	
def red_invitation_check(message):
    """6.1.1"""    
    user_to = temp_dict[message.chat.id]        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
    text = message.text
    if text[0:19] == 'Показать участников':
        show_all_members(message,user_to)	
    elif text == 'Нет'.format(0):        
        exists = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()
        if not exists:
            start_without_invitation(message)
        else:
            global_menu(message)
    elif text == 'Да'.format(0):
        red_invitation_wizard(message,user_to)
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, red_invitation_check)	
		
		

def red_invitation_wizard(message, user_to): 
    """6.1.2"""
    temp_dict[message.chat.id]  = user_to
    user = user_to
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Назад')
    markup.row(btn1)
    msg = bot.send_message(message.chat.id, 'Введите минимальную сумму помощи в {}:'.format(user.currency),reply_markup=markup)
    bot.register_next_step_handler(msg, red_invitation_wizard_check)
	
	

def red_invitation_wizard_check(message):   #------------------ TODO
    user = temp_dict[message.chat.id]
    invitation_sum = message.text
    if message.text == 'Назад':
        start_red_invitation(message,user)
        return
    if not invitation_sum.isdigit():
        msg = bot.send_message(message.chat.id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg,red_invitation_wizard_check)
        return
    elif float(invitation_sum) < user.min_payments:
        msg = bot.send_message(message.chat.id, 'Пожалуйста введите другую сумму.\n\
Минимальная сумма {} {}'.format(user.min_payments,user.currency))
        bot.register_next_step_handler(msg,red_invitation_wizard_check)
        return
	
    ring = read_rings_help(user.telegram_id)
    if ring is None:
        array = []
        array.append(message.chat.id)
        create_rings_help(user.telegram_id,array)
    else:
        array = ring.help_array	
        array.append(message.chat.id)
        update_rings_help(user.telegram_id,array)
    ring = read_rings_help(user.telegram_id)
    users_count = len(ring.help_array)
    status = 'Красный \U0001F534'
    bot_text = f'Записано Ваше намерение помогать участнику {user.first_name} {user.last_name} на сумму {invitation_sum} {user.currency}\n\
\n\
Участник {user.first_name} {user.last_name} {status}\n\
Собрано {user.current_payments} из {user.max_payments} {user.currency}\n\
Ожидается {invitation_sum} {user.currency}\n\
Всего участников: {users_count}\n\
Осталось <C> дней из <D>\n\
\n\
За три дня до наступления периода бот напомнит о намерении и попросит перевести его в статус "обязательства".'

    create_intention(message.chat.id, user.telegram_id, invitation_sum, user.current_payments, status=1)
    create_event(	from_id=message.chat.id, 
					first_name=user.first_name,            # TODO not needed
					last_name=user.last_name,             # TODO not needed
					status='red', 
					type='notice', 
					min_payments=user.min_payments, 
					current_payments=user.current_payments, 
					max_payments=user.max_payments,
					currency=user.currency, 
					users=0, 
					to_id=user.telegram_id, 
					sent=False,
                    reminder_date = date.today())  # someday: intention_id
    bot.send_message(message.chat.id, bot_text)
    global_menu(message,True)	
	
#---------------------------------------------------------			
		

			
			
			
			
			
			
			
			
			
			
			
		


	
		










	
def orange_status_wizard(message):
    user = read_exodus_user(message.chat.id)
    all_users = session.query(Exodus_Users).count()
    bot_text = 'Ваш текущий статус: Оранжевый \U0001f7e0\n\
\n\
Период: Ежемесячно\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
\n\
Если вы хотите пригласить кого-то помогать вам, перешлите ему эту ссылку:'.format(user.current_payments,user.max_payments,user.currency,user.max_payments-user.current_payments,user.currency,all_users)		
    bot.send_message(message.chat.id, bot_text)
    link = create_link(user.telegram_id,user.telegram_id)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать')
    btn2 = types.KeyboardButton(text='Изменить статус')
    btn3 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    link = create_link(user.telegram_id,user.telegram_id)	
    msg = bot.send_message(message.chat.id, link, reply_markup=markup)
    bot.register_next_step_handler(msg, orange_menu_check)  	

	
def orange_menu_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать':
        orange_edit_wizard(message)	
    elif text == 'Изменить статус':
        green_red_wizard(message)	
    elif text == 'Главное меню':
        global_menu(message,True)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, orange_menu_check)   

def green_red_wizard(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Зелёный \U0001F7E2')
    btn2 = types.KeyboardButton(text='Красный \U0001F534')
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, 'Выберите новый статус', reply_markup=markup)		
    bot.register_next_step_handler(msg, green_red_check)

def green_red_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Зелёный \U0001F7E2':
        green_edit_wizard(message)
    elif text == 'Красный \U0001F534':
        red_edit_wizard(message)
    elif text == 'Назад':
        orange_status_wizard(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, green_red_check)     
    

	
	
def green_edit_wizard(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Сохранить')
    btn2 = types.KeyboardButton(text='Отмена')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, 'Вы собираетесь сменить статус на Зеленый\n\
Пожалуйста подтвердите смену статуса:\n\
\n\
Если ваш статус был Оранжевый или красный, все намерения участников в вашу пользу будут автоматически удалены.\n\
\n\
Все обязательства участников в вашу пользу останутся в силе. Посмотреть все обязательства можно в разделе главного меню "Транзакции" > "Все обязательства"', reply_markup=markup)		
    bot.register_next_step_handler(msg, green_edit_wizard_check)   
 
def green_edit_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Сохранить':
        bot.send_message(message.chat.id, 'Статус сохранён')
        update_exodus_user(telegram_id = message.chat.id, status = 'green')
        global_menu(message)
    elif text == 'Отмена':
        bot.send_message(message.chat.id, 'Статус не сохранён')
        global_menu(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, green_edit_wizard_check)
 

 
 
#------------------------
def green_status_wizard(message):
    """2.0.1"""
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Изменить статус')
    btn2 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    msg = bot.send_message(message.chat.id, 'Ваш текущий статус - \U0001F7E2 (зелёный)\nСписок участников с которыми Вы связаны, можно посмотреть в разделе главного меню "Участники"', reply_markup=markup)		
    bot.register_next_step_handler(msg, green_status_wizard_check)   

def green_status_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Изменить статус':
        select_orange_red(message)	
    elif text == 'Главное меню':
        global_menu(message,True)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, green_status_wizard_check)

def select_orange_red(message):
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton(text='Оранжевый \U0001f7e0')
        btn2 = types.KeyboardButton(text='Красный \U0001F534')
        btn3 = types.KeyboardButton(text='Главное меню')
        markup.row(btn1,btn2)
        markup.row(btn3)
        msg = bot.send_message(message.chat.id, "Выберите новый статус:", reply_markup=markup)
        bot.register_next_step_handler(msg, check_orange_red)

def check_orange_red(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Оранжевый \U0001f7e0':
        bot.send_message(message.chat.id, "Вы меняете статус на Оранжевый \U0001f7e0:")
        orange_edit_wizard(message)	
    elif text == 'Красный \U0001F534':
        red_edit_wizard(message)	
    elif text == 'Главное меню':
        global_menu(message)
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, check_orange_red)    		

		
		
		
def red_status_wizard(message):
    user = read_exodus_user(message.chat.id)
    all_users = session.query(Exodus_Users).count()
    d0 = user.start_date
    d1 = date.today()
    delta = d1 - d0
    days_end = user.days - delta.days
    bot_text = f'Ваш текущий статус: Красный \U0001F534\n\
\n\
Собрано {user.current_payments} из {user.max_payments} {user.currency}\n\
Ожидается {user.max_payments-user.current_payments} {user.currency}\n\
Всего участников: {all_users}\n\
Осталось {days_end} дней из {user.days}\n\
Обсуждение: {user.link}\n\
\n\
Если вы хотите пригласить кого-то помогать вам, перешлите ему эту ссылку:'
    bot.send_message(message.chat.id, bot_text)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать')
    btn2 = types.KeyboardButton(text='Изменить статус')
    btn3 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    link = create_link(user.telegram_id,user.telegram_id)
    msg = bot.send_message(message.chat.id, link, reply_markup=markup)
    bot.register_next_step_handler(msg, red_status_wizard_check)  	

	
def red_status_wizard_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Редактировать':
        red_edit_wizard(message)	
    elif text == 'Изменить статус':
        green_orange_wizard(message)	
    elif text == 'Главное меню':
        global_menu(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, red_status_wizard_check)   		
		
		
		
#------------------ RED WIZARD 2.2 ---------------
def red_edit_wizard(message):
    """2.2"""
    user = read_exodus_user(message.chat.id)
    if read_rings_help(user.telegram_id) is None:
        create_rings_help(user.telegram_id,[])
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, 'Введите сумму в {}, которая Вам необходима:'.format(user.currency), reply_markup=markup)
    bot.register_next_step_handler(msg, red_edit_wizard_step1)    		
	

def red_edit_wizard_step1(message):
    user = read_exodus_user(message.chat.id)
    user_dict[message.chat.id] = user
    chat_id = message.chat.id
    max_payments = message.text
    if not max_payments.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр. Введите сумму в {}, которая Вам необходима:'.format(user.currency))
        bot.register_next_step_handler(msg, red_edit_wizard_step1)
        return
    user_dict[message.chat.id].max_payments = float(max_payments)
    msg = bot.send_message(message.chat.id, 'Введите минимальную сумму помощи в {}'.format(user.currency))
    bot.register_next_step_handler(msg, red_edit_wizard_step2)

	
def red_edit_wizard_step2(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    min_payments = message.text
    if not min_payments.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр. Введите сумму в {}, которая Вам необходима:'.format(user.currency))
        bot.register_next_step_handler(msg, red_edit_wizard_step2)
        return
    user_dict[message.chat.id].min_payments = float(min_payments)
    msg = bot.send_message(message.chat.id, 'Введите кол-во дней, в течение которых вам необходимо собрать эту сумму:')
    bot.register_next_step_handler(msg, red_edit_wizard_step3)

	
def red_edit_wizard_step3(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    days = message.text
    if not days.isdigit():
        msg = bot.send_message(chat_id, 'Кол-во дней должны быть в виде цифр. Введите кол-во дней, в течение которых вам необходимо собрать эту сумму:')
        bot.register_next_step_handler(msg, red_edit_wizard_step3)
        return
    user_dict[message.chat.id].days = days
    msg = bot.send_message(message.chat.id, 'Введите ссылку на чат:')
    bot.register_next_step_handler(msg, red_edit_wizard_step35)	

	

def red_edit_wizard_step35(message):
    link = message.text
    user = user_dict[message.chat.id]
    bot_text = f'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: Красный\n\
Обсуждение: {link}\n\
В течение {user.days}\n\
Минимально: {user.min_payments} {user.currency}\n\
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
        update_exodus_user(telegram_id = message.chat.id, status = 'red',link=link, start_date = date.today(), days = user_dict[message.chat.id].days, min_payments = user_dict[message.chat.id].min_payments, max_payments = user_dict[message.chat.id].max_payments)
        global_menu(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, red_edit_wizard_step4, link) 






	

	
def green_orange_wizard(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Зелёный \U0001F7E2')
    btn2 = types.KeyboardButton(text='Оранжевый \U0001f7e0')
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1, btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, 'Выберите новый статус', reply_markup=markup)		
    bot.register_next_step_handler(msg, green_orange_check)

def green_orange_check(message):
    bot.delete_message(message.chat.id, message.message_id)
    text = message.text
    if text == 'Зелёный \U0001F7E2':
        green_edit_wizard(message)
    elif text == 'Оранжевый \U0001f7e0':
        orange_edit_wizard(message)
    elif text == 'Назад':
        red_status_wizard(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, green_orange_check) 
		

		

		


#------------------ ORANGE GREEN WIZARD-------
def orange_green_wizard(message):
#    bot.delete_message(message.chat.id, message.message_id)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Оранжевый \U0001f7e0')
    btn2 = types.KeyboardButton(text='Зелёный \U0001F7E2')
    markup.row(btn1,btn2)
    msg = bot.send_message(message.chat.id, 'Пожалуйста выберите Ваш статус', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_green_wizard_step1)

	
def orange_green_wizard_step1(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    if message.text == 'Оранжевый \U0001f7e0':
        bot.send_message(message.chat.id, 'Вы выбрали Оранжевый \U0001f7e0 статус', reply_markup=markup)
        orange_edit_wizard(message)
        return	
    if message.text == 'Зелёный \U0001F7E2':
        bot.send_message(message.chat.id, 'Ваш текущий статус - \U0001F7E2 (зелёный)\nСписок участников с которыми Вы связаны, можно посмотреть в разделе главного меню "Участники"', reply_markup=markup)		
        update_exodus_user(telegram_id=message.chat.id, status='green')
        global_menu(message,True)
    else:
        orange_green_wizard(message)
#-------------------------------------------	
	
	
	
	
	
#------------------ ORANGE WIZARD-------
def orange_edit_wizard(message):
    user = read_exodus_user(message.chat.id)
    if read_rings_help(user.telegram_id) is None:
        create_rings_help(user.telegram_id,[])
    markup = types.ReplyKeyboardRemove(selective=False)
    msg = bot.send_message(message.chat.id, 'Введите сумму в {}, которую вы бы хотели получать в течение месяца:'.format(user.currency), reply_markup=markup)
    bot.register_next_step_handler(msg, orange_step_need_payments)


def orange_step_need_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    max_payments = message.text
    if not max_payments.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр. Введите сумму в {}, которую вы бы хотели получать в течение месяца:'.format(user.currency))
        bot.register_next_step_handler(msg, orange_step_need_payments)
        return
    update_exodus_user(message.chat.id,max_payments=float(max_payments))
    msg = bot.send_message(message.chat.id, 'Введите минимальную сумму помощи в {}'.format(user.currency))
    bot.register_next_step_handler(msg, orange_step_min_payments)


def orange_step_min_payments(message):
    user = read_exodus_user(message.chat.id)
    chat_id = message.chat.id
    min_payments = message.text
    if not min_payments.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр. Введите минимальную сумму помощи в {}'.format(user.currency))
        bot.register_next_step_handler(msg, orange_step_min_payments)
        return
    update_exodus_user(message.chat.id,min_payments=float(min_payments))
    msg = bot.send_message(chat_id, 'Пожалуйста проверьте введенные данные:\n \
\n \
Статус: Оранжевый\n \
Период: Ежемесячно.\n \
Минимально: {} {}\n \
Необходимая сумма: {} {}'.format(user.min_payments,user.currency,user.max_payments,user.currency))
    markup = types.ReplyKeyboardMarkup()
    user = read_exodus_user(message.chat.id)
    if user.status == '':
        btn1 = types.KeyboardButton(text='Редактировать')
        btn2 = types.KeyboardButton(text='Сохранить')
        markup.row(btn1)
        markup.row(btn2)
    else:
        btn1 = types.KeyboardButton(text='Редактировать')
        btn2 = types.KeyboardButton(text='Отмена')
        btn3 = types.KeyboardButton(text='Сохранить')
        markup.row(btn1,btn2)
        markup.row(btn3)
    msg = bot.send_message(chat_id, 'Вы хотите изменить свой статус и опубликовать эти данные?\n\
Все пользователи, которые связаны с вами внутри Эксодус бота, получат уведомление.', reply_markup=markup)
    bot.register_next_step_handler(msg, orange_step_final)
		
		
def orange_step_final(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
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
        update_exodus_user(message.chat.id,status='orange')
        user = read_exodus_user(message.chat.id)
        all_users = session.query(Exodus_Users).all()
        users_count = session.query(Exodus_Users).count()
        for users in all_users:
						#TODO           пока что рассылка всем
            if users.telegram_id != message.chat.id:
                create_event(	from_id = message.chat.id, 
								first_name = user.first_name, 
								last_name = user.last_name, 
								status = 'orange', 
								type = 'orange', 
								min_payments = user.min_payments, 
								current_payments = user.current_payments, 
								max_payments = user.max_payments,
								currency = user.currency, 
								users = users_count, 
								to_id = users.telegram_id, 
								sent=False,
                                reminder_date = date.today())  # someday: intention_id
        global_menu(message)
        return	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, orange_step_final)
        return
#-------------------------------------------		
	

	
@bot.message_handler(commands=['add'])
def welcome(message):
    """1.0"""
    create_event(	from_id = message.chat.id, 
					first_name = 'Loh',             # TODO не нужно
					last_name = 'Pidr',             # TODO не нужно
					status = 'orange',              
					type = 'orange', 
					min_payments = 1,
					current_payments = 4, 
					max_payments = 100,
					currency = 'USD', 
					users = 0, 
					to_id = message.chat.id, 
					sent=False,
                    reminder_date=date.today()) # someday intention_id
    return
	

	
	
@bot.callback_query_handler(func=lambda call: call.data[0:18] == 'orange_invitation-')
def orange_invitation(call):
    global_menu(call.message)
    bot.delete_message(call.message.chat.id,call.message.message_id)
    user_id = call.data[18:]    
    start_orange_invitation(call.message,user_id)
    return

@bot.callback_query_handler(func=lambda call: call.data[0:15] == 'red_invitation-')
def red_invitation(call):
    global_menu(call.message)
    bot.delete_message(call.message.chat.id,call.message.message_id)
    user_id = call.data[15:]    
    start_red_invitation(call.message,user_id)
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
        user = read_exodus_user(telegram_id=event.to_id)
        first_name = user.first_name
        last_name = user.last_name
        message = 'Спасибо! Участнику {first_name} {last_name} будет отправлено уведомление о том, ' \
                  'что вы подтвердили иcполнение обязательства.'.format(first_name=first_name,
                                                                        last_name=last_name)

        bot.send_message(call.message.chat.id, message)
        global_menu(call.message)
    #bookmark # callback
    elif call.data[0:9] == 'reminder_':
        event_id = call.data[9:]
        event = read_event(event_id)
        if event.type == 'reminder_in':
            # 6.8
            for_me_obligation(message, reminder_call=True,
                              intention_id=event.to_id)
            pass
        elif event.type == 'reminder_out':
            if event.status == 'intention':
                # 6.7
                intention_for_needy(message, reminder_call=True,
                                    intention_id=event.to_id)
            elif event.status == 'obligation':
                # 6.3
                obligation_for_needy(message, reminder_call=True,
                                     intention_id=event.to_id)
                pass
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
