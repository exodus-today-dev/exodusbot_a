#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import telebot
from telebot import types

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


import time

import config

bot = telebot.TeleBot(config.API_TOKEN)




#--------------------------------- DB ------------------------------



from models import session, Exodus_Users, Events, update_event
from events import invitation_help_orange, invitation_help_red, notice_of_intent


user_dict = {}
bot.remove_webhook()

def read():
    all_users = session.query(Exodus_Users).count()
    all = session.query(Events).filter_by(sent = False)
    current_date = date.today()
    for event in all:
        if event.type == 'orange':
            update_event(event.event_id,True)
            invitation_help_orange(event.event_id)
        if event.type == 'red':
            update_event(event.event_id,True)
            invitation_help_red(event.event_id)
        if event.type == 'notice':
            update_event(event.event_id,True)
            notice_of_intent(event.event_id)
        if event_type == 'obligation_sended' and (current_date == event.reminder_date or
                                                  current_date > event.reminder_date):
            obligation_sended_notice(event.event_id) # 6.4
        if event_type == 'obligation_recieved' and (current_date == event.reminder_date or
                                                    current_date > event.reminder_date):
            obligation_recieved_notice(event.event_id) # ?
        if event_type == 'obligation_money_requested' and (current_date == event.reminder_date or
                                                           current_date > event.reminder_date):
            obligation_money_requested_notice(event.event_id)
        if (event_type == 'reminder_in' or event_type == 'reminder_out') and \
           (current_date == event.reminder_date or current_date > event.reminder_date):
            reminder(event.event_id) # 6.3, 6.7, 6.8


while True:
    try:
        read()
    except Exception as error:
        print(error)
    time.sleep(1)

#bot.polling()
