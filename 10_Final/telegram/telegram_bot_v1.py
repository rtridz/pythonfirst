import random
import telebot
import time
from telebot import types

from telegram import utils
from telegram.config import token, database_name
from telegram.dbhelper import DBHelper

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def handle_start(message):
     bot.send_message(message.chat.id, "Привет! Я могу тебя удивить")



@bot.message_handler(commands=['q'])
def questions(message):
    for i in ['1','2','3','4']:

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in ['OloLOlolO', 'Trolololo']])

        keyboard = None
        bot.send_message(message.chat.id, i,
                         reply_markup=keyboard)

        time.sleep(1)





# @bot.message_handler(content_types=["text"])

@bot.message_handler(commands=['text'])
def handle_text(message):

    bot.send_message(message.chat.id, "Я буду выполнять действите с этими данными: " + message.text)

    keyboard = types.InlineKeyboardMarkup()
    callback_button1 = types.InlineKeyboardButton(text="Еще раз", callback_data="1")

    keyboard.add(callback_button1)
    bot.send_message(message.chat.id, "Попробовать еще раз с этим словом?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_inline(call):

        if call.message:
            if call.data == "1":
                bot.send_message(message.chat.id, "На этот раз я буду работать с: " + message.text)
                bot.send_message(message.chat.id, "Давай я тогда попробую такой вариант?", reply_markup=keyboard)

if __name__ == '__main__':
    # utils.count_rows()
    # random.seed()
    bot.polling(none_stop=True)