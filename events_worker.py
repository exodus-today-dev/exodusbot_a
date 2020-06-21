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
from events import invitation_help_orange, invitation_help_red


user_dict = {}
bot.remove_webhook()

def read():
    all_users = session.query(Exodus_Users).count()
    all = session.query(Events).filter_by(sent = False)
    for event in all:
        if event.type == 'orange':
            update_event(event.event_id,True)
            invitation_help_orange(event.event_id)
        if event.type == 'red':
            update_event(event.event_id,True)
            invitation_help_red(event.event_id)




			
while True:
    try:
        read()
    except Exception as error:
        print(error)
    time.sleep(1)

#bot.polling()
