#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from telebot import types

from datetime import datetime, date

import config

bot = telebot.TeleBot(config.API_TOKEN)

#bot.remove_webhook()


#--------------------------------- DB ------------------------------


from models import read_exodus_user, create_event, session, Exodus_Users, Events, Intention,\
 read_event, update_exodus_user, create_exodus_user, read_rings_help, create_rings_help, \
 create_intention, update_rings_help, read_intention, read_intention_by_id,update_intention
from events import show_all_members, invitation_help_orange, invitation_help_red
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
    ref = '{}+{}'.format(from_id,to_id)
    link = 'https://t.me/exodus_official_bot?start={}'.format(make_hash(ref))	
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
    NY = datetime(now.year,now.month+1,1) # я знаю, тут нет проверки 12 месяца, я дурак ага  
    d = NY-now
    return(d.days)

    
# ------------------------------------------------------------------		




# -------------- G L O B A L   M E N U ---------
def global_menu(message, dont_show_status=False):
    """2.0"""
    bot.clear_step_handler(message)
    user = session.query(Exodus_Users).filter_by(telegram_id=message.chat.id).first()

    if user is None:
        welcome(message)	
	
	
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
    
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Редактировать реквезиты')
    btn2 = types.KeyboardButton(text='Настройки уведомлений')
#    btn3 = types.KeyboardButton(text='Валюта')
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
#    markup.row(btn3,btn4)                    # ________________ TODO
    markup.row(btn4)                    # ________________ TODO
    bot_text = 'Ваши текущие Настройки:\n\
\n\
Валюта: <текущая валюта>\n\
Уведомления: <статус уведомлений>\n\
\n\
Реквизиты:\n\
\n\
1. <название> <значение>  (по умолчанию)\n\
2. <название> <значение>\n\
...'
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)
	
def configuration_check(message):
    """3"""
    
    text = message.text
    if text == 'Редактировать реквезиты':
        bot.send_message(message.chat.id, 'Редактировать реквезиты')   # TODO
        global_menu(message)
        return
    elif text == 'Настройки уведомлений':
        bot.send_message(message.chat.id, 'Настройки уведомлений')     # TODO
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

	
def transactions_menu(message):
    """2.4"""
    
    user = read_exodus_user(message.chat.id)
	
    intention = read_intention(from_id=message.chat.id)
    my_intent = 0.0 
    if intention is not None:
        for pay in intention:
            my_intent = my_intent + pay.payment        
		
    intention = read_intention(from_id=message.chat.id, status=0)
    my_intention = 0.0	
    if intention is not None:
        for pay in intention:
            my_intention = my_intention + pay.payment
        
    intention = read_intention(to_id=message.chat.id)
    me_intent = 0.0	
    if intention is not None:
        for pay in intention:
            me_intent = me_intent + pay.payment
        
    intention = read_intention(to_id=message.chat.id, status=0)
    me_intention = 0.0	
    if intention is not None:
        for pay in intention:
            me_intention = me_intention + pay.payment	

    status = get_status(user.status)                 # TODO
    bot_text = 'С момента смены вашего статуса на {0}:\n\
\n\
В пользу других:\n\
Мои намерения: {2} {1}\n\
Мои обязательства: {3} {1}\n\
\n\
В мою пользу:\n\
Намерения: {4} {1}\n\
Обязательства: {5} {1}'.format(status,
										user.currency, 
										my_intent, 
										my_intention,
										me_intent, 
										me_intention)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В пользу других')
    btn2 = types.KeyboardButton(text='В мою пользу')
    btn3 = types.KeyboardButton(text='За всё время')
    btn4 = types.KeyboardButton(text='Не исполненные')
    btn5 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1,btn2)
    markup.row(btn3,btn4)
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
    btn1 = types.KeyboardButton(text='Ссылка на мой профиль')
    btn2 = types.KeyboardButton(text='В мою пользу ({})'.format(0))
    btn3 = types.KeyboardButton(text='В пользу других ({})'.format(0))
    btn4 = types.KeyboardButton(text='Главное меню')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)                   
    markup.row(btn4)                    # ________________ TODO
    bot_text = 'Я сети Эксодус с {data}\n\
Меня пригласил: {ref}\n\
\n\
В мою пользу (12):\n\
Намерений: <сумма> <валюта>\n\
Обязательств: <сумма> <валюта>\n\
Исполнено: <сумма> <валюта>\n\
\n\
В пользу других (123):\n\
Намерений: <сумма> <валюта>\n\
Обязательств: <сумма> <валюта>\n\
Исполнено: <сумма> <валюта>'.format(	data=user.create_date.strftime("%d %B %Y %I:%M%p"),
										ref=ref)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,members_check)  
    return
	
def members_check(message):
    text = message.text
#    bot.delete_message(message.chat.id, message.message_id)
    if text == 'Ссылка на мой профиль':
        members_menu_profile_link(message)
        return
    elif text[0:12] == 'В мою пользу': 
        global_menu(message)					# TODO
        return
    elif text[0:15] == 'В пользу других':
        global_menu(message)					# TODO
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
    
    bot_text = 'Вами записано {} намерений и {} обязательств в пользу {} участников:'.format(0,0,0)        # TODO
    bot.clear_step_handler(message)
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Намерения')
    btn2 = types.KeyboardButton(text='Обязательства')
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_other_check)  
    return

def for_other_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text[0:9] == 'Намерения':
        for_other_wizard_intention(message)
    elif text[0:13] == 'Обязательства':
        bot.send_message(message.chat.id, 'Обязательства')
        global_menu(message)
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
#    user = read_exodus_user(message.chat.id)

    intention_number = message.text
    if not intention_number.isdigit():
        msg = bot.send_message(message.chat.id, 'Номер должен быть в виду цифры:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return
    intention = read_intention_by_id(intention_id=intention_number, from_id=message.chat.id, status=1)
    if intention is None:
        msg = bot.send_message(message.chat.id, 'Введённый номер не соовпадает с существующими намерениями:')
        bot.register_next_step_handler(msg, for_other_wizard_intention_check)
        return        
    transaction[message.chat.id] = intention_number   
    intention_for_needy(message)
    return


def intention_for_needy(message):
    """6.7"""
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
    global_menu(message,True)
    return

def remind_later(message):
#  create_event       ---------------------------- TODO Создать уведомление - бот вышлет это через сутки
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
        intention_for_needy(message)
        return
    if not payment.isdigit():
        msg = bot.send_message(chat_id, 'Сумма должна быть только в виде цифр.')
        bot.register_next_step_handler(msg, edit_intention_check)
        return
    update_intention(intention_id=intention_id,payment=payment)
    intention_for_needy(message)
    return

	
def cancel_intention(message):
    intention_id = transaction[message.chat.id]
    intention = read_intention_by_id(intention_id)
    user_to = read_exodus_user(telegram_id=intention.user_to)
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
        intention_for_needy(message)
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
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось <D1> дней:\n'.format(n=n,
							first_name=user_to.first_name,
							last_name=user_to.last_name,
							payment=intent.payment,
							currency=intent.currency)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)	
	
	
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)	
    bot.register_next_step_handler(msg,for_other_wizard_obligation_check)  
    return

def for_other_wizard_obligation_check(message):
    global_menu(message)
    return





	
def for_my_wizard(message):
    """4.2"""
    bot_text = '{} участников записали в вашу пользу {} намерений и {} обязательств:'.format(0,0,0)        # TODO

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Намерения')
    btn2 = types.KeyboardButton(text='Обязательства')
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_my_check)  
    return


def for_my_check(message):
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text[0:9] == 'Намерения':
        bot.send_message(message.chat.id, 'Намерения')                    # TODO
        global_menu(message)
    elif text[0:13] == 'Обязательства':
        bot.send_message(message.chat.id, 'Обязательства')                # TODO
        global_menu(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return



def for_my_wizard_intention(message):
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось <D1> дней:\n'.format(n=n,
							first_name=user_to.first_name,
							last_name=user_to.last_name,
							payment=intent.payment,
							currency=intent.currency)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)	
	
	
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)	
    bot.register_next_step_handler(msg,for_my_wizard_intention_check)  
    return

def for_my_wizard_intention_check(message):
    global_menu(message)
    return


def for_my_wizard_obligation(message):
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось <D1> дней:\n'.format(n=n,
							first_name=user_to.first_name,
							last_name=user_to.last_name,
							payment=intent.payment,
							currency=intent.currency)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)	
	
	
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)	
    bot.register_next_step_handler(msg,for_my_wizard_intention_check)  
    return

def for_my_wizard_obligation_check(message):
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
    bot_text ='Не исполненными считаются те обязательства, которые не подтвердил получатель.'
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='В мою пользу ({})'.format(0))
    btn2 = types.KeyboardButton(text='В пользу других ({})'.format(0))
    btn3 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    markup.row(btn3)
    msg = bot.send_message(message.chat.id, bot_text, reply_markup=markup)
    bot.register_next_step_handler(msg,for_all_time_check)  
    return

def not_executed_check(message):	
    text = message.text
    bot.delete_message(message.chat.id, message.message_id)
    if text[0:12] == 'В мою пользу':
        not_executed_wizard_to_me(message)
    elif text[0:15] == 'В пользу других':
        bot.send_message(message.chat.id, '2')                # TODO
        global_menu(message)
    elif text == 'Назад':
        bot.clear_step_handler(message)
        transactions_menu(message)
        return
    else:
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, for_my_check)    
    return
    


def not_executed_wizard_to_me(message):
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось <D1> дней:\n'.format(n=n,
							first_name=user_to.first_name,
							last_name=user_to.last_name,
							payment=intent.payment,
							currency=intent.currency)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)	
	
	
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)	
    bot.register_next_step_handler(msg,not_executed_wizard_to_me_check)  
    return

def not_executed_wizard_to_me_check(message):
    global_menu(message)
    return


def not_executed_wizard_for_all(message):
    intentions = read_intention(from_id=message.chat.id, status=1)
    n = 0
    bot_text = ''
    for intent in intentions:
        n = n + 1
        user_to = read_exodus_user(telegram_id = intent.to_id)
        text = '{n}. {first_name} {last_name} {payment} {currency}, \
осталось <D1> дней:\n'.format(n=n,
							first_name=user_to.first_name,
							last_name=user_to.last_name,
							payment=intent.payment,
							currency=intent.currency)
        bot_text = bot_text + text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(text='Показать еще 10')
    btn2 = types.KeyboardButton(text='Назад')
    markup.row(btn1,btn2)
    bot.send_message(message.chat.id, bot_text, reply_markup=markup)	
	
	
    bot_text = 'Введите номер, чтобы посмотреть подробную информацию или изменить:'
    msg = bot.send_message(message.chat.id, bot_text)	
    bot.register_next_step_handler(msg,not_executed_wizard_for_all_check)  
    return

def not_executed_wizard_for_all_check(message):
    global_menu(message)
    return	
	
def members_menu_profile_link(message):
    user = read_exodus_user(message.chat.id)
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
            start_orange_invitation(message,user_to)
        elif user_to.status == 'red':
            start_red_invitation(message,user_to)
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

    user = user_to
    ring = read_rings_help(user_to.telegram_id)
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
    temp_dict[message.chat.id] = user_to        # TODO ---------- убрать этот костыль, так как при большом кол-во пользователей будет съедать память
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
    bot_text = 'Записано Ваше намерение помогать участнику {} {} на сумму {} {}\n\
\n\
Участник {} {} {}\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
\n\
За три дня до наступления периода бот напомнит о намерении и попросит перевести его в статус "обязательства".\
'.format(	user.first_name,
			user.last_name,
			invitation_sum,
			user.currency,
			user.first_name,
			user.last_name,
			status, 
			user.current_payments,
			user.max_payments,                #---------- TODO
			user.currency,
			invitation_sum,
			user.currency,
			users_count)    
    create_intention(message.chat.id, user.telegram_id, invitation_sum, user.currency,status=1)
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
            start_orange_invitation(message,temp_dict[message.chat.id])
        elif temp_dict[message.chat.id].step == 'red':
            start_red_invitation(message,temp_dict[message.chat.id])
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, show_all_members_check)
		





		
#----------------------- 6.2 RED ---------------------------			
def start_red_invitation(message,user_to):
    """6.2"""

    user = user_to
    ring = read_rings_help(user_to.telegram_id)
    if ring is None:
        users_count = 0
    else:
        users_count = len(ring.help_array)

    status = 'Красный \U0001F534'                  #_____________________ ДНИ ВЪЕБИ СЮДА
    bot_text = 'Участник {} {} - {}\n\
Период: Ежемесячно\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
Осталось <C> дней из <D>\n\
Обсуждение: <Ссылка>\n\
\n\
Вы можете помочь этому участнику?\n\
Минимальная сумма {} {}'.format(	user.first_name, 
											user.last_name,
											status,
											user.current_payments,
											user.max_payments,
											user.currency,
											user.max_payments-user.current_payments,
											user.currency,
											users_count,
											user.min_payments,
											user.currency)

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
    bot_text = 'Записано Ваше намерение помогать участнику {} {} на сумму {} {}\n\
\n\
Участник {} {} {}\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
Осталось <C> дней из <D>\n\
\n\
За три дня до наступления периода бот напомнит о намерении и попросит перевести его в статус "обязательства".\
'.format(	user.first_name,
			user.last_name,
			invitation_sum,
			user.currency,
			user.first_name,
			user.last_name,
			status, 
			user.current_payments,
			user.max_payments,                #---------- TODO
			user.currency,
			invitation_sum,
			user.currency,
			users_count)    
    create_intention(message.chat.id, user.telegram_id, invitation_sum, user.current_payments, status=1)
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
    bot_text = 'Ваш текущий статус: Красный \U0001F534\n\
\n\
Собрано {} из {} {}\n\
Ожидается {} {}\n\
Всего участников: {}\n\
Осталось {} дней из {}\n\
Обсуждение: <Ссылка>\n\
\n\
Если вы хотите пригласить кого-то помогать вам, перешлите ему эту ссылку:'.format(user.current_payments,user.max_payments,user.currency,user.max_payments-user.current_payments,user.currency,all_users,days_end,user.days)		
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
    bot.send_message(message.chat.id, 'Ссылка на чат:\n В РАЗРАБОТКЕ TODO')
    user = user_dict[message.chat.id]
    bot_text = 'Пожалуйста проверьте введенные данные:\n\
\n\
Статус: Красный\n\
Обсуждение: <ссылка на чат>\n\
В течение {}\n\
Минимально: {} {}\n\
Необходимая сумма: {} {}'.format(user.days,user.min_payments,user.currency,user.max_payments,user.currency)
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
        update_exodus_user(telegram_id = message.chat.id, status = 'red', start_date = date.today(), days = user_dict[message.chat.id].days, min_payments = user_dict[message.chat.id].min_payments, max_payments = user_dict[message.chat.id].max_payments)
        global_menu(message)	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, red_edit_wizard_step4) 






	

	
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
        all_users = rows = session.query(Exodus_Users).all()
        users_count = session.query(Exodus_Users).count()
        for users in all_users:
						#TODO
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
								sent=False)			
        global_menu(message)
        return	
    else: 
        msg = bot.send_message(message.chat.id, 'Выберите пункт меню')
        bot.register_next_step_handler(msg, orange_step_final)
        return
#-------------------------------------------		
	

	
	
	
	


		

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
	



bot.polling(none_stop=True)
