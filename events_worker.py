#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
from datetime import date, timedelta

import telebot
from telebot import types

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import time

import config

bot = telebot.TeleBot(config.API_TOKEN)

# --------------------------------- DB ------------------------------


from models_.exodus_user import Exodus_Users
from models_.events import Events
from models_.data_repository import session
from db_controller.controller import update_event
from events import invitation_help_orange, invitation_help_red, notice_of_intent, obligation_sended_notice, \
    obligation_recieved_notice, obligation_money_requested_notice, reminder, reminder_for_6_10

user_dict = {}
bot.remove_webhook()

# завели списки, чтобы добавить туда event_id отправленных уведомлений
list_event_id_obligation_sended = []
list_event_id_obligation_recieved = []
list_event_id_for_6_10 = []


def read():
    all_users = session.query(Exodus_Users).count()
    all = session.query(Events).filter_by(sent=False)
    current_date = date.today()

    for event in all:
        if event.type == 'orange':
            update_event(event.event_id, True)
            invitation_help_orange(event.event_id)
        if event.type == 'red':
            update_event(event.event_id, True)
            invitation_help_red(event.event_id)
        if event.type == 'notice':
            update_event(event.event_id, True)
            notice_of_intent(event.event_id)
        # 6.4
        if event.type == 'obligation_sended' and (current_date == event.reminder_date or
                                                  current_date > event.reminder_date) and event.event_id not in list_event_id_obligation_sended:
            list_event_id_obligation_sended.append(event.event_id)

            obligation_sended_notice(event.event_id)


        # 6.9
        if event.type == 'obligation_recieved' and (current_date == event.reminder_date or
                                                    current_date > event.reminder_date):
            list_event_id_obligation_recieved.append(event.event_id)

            obligation_recieved_notice(event.event_id)
            update_event(event.event_id, True)

        if event.type == 'obligation_money_requested' and (current_date == event.reminder_date or
                                                           current_date > event.reminder_date):
            obligation_money_requested_notice(event.event_id)
        if (event.type == 'reminder_in' or event.type == 'reminder_out') and \
                (current_date == event.reminder_date or current_date > event.reminder_date):
            reminder(event.event_id)  # 6.3, 6.7, 6.8

        # 6.10
        if event.type == 'obligation_sended' and (current_date - timedelta(days=5)) == event.reminder_date or (
                current_date - timedelta(days=5)) > event.reminder_date and event.event_id not in list_event_id_for_6_10:
            list_event_id_for_6_10.append(event.event_id)
            reminder_for_6_10(event.event_id)


while True:
    try:
        read()
    except Exception as error:
        print(error)
    time.sleep(1)

# bot.polling()
