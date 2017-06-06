import sys
import argparse
import telebot
from telebot import types
import telegram.config

# Bot code
from telegram import work

bot = telebot.TeleBot(telegram.config.token)


def writeChat(chat_id, outMessage):
    bot.send_message(chat_id, outMessage)


@bot.message_handler(content_types=["text"]) 
def core(message): # Название функции не играет никакой роли, в принципе

    if message.text == 'files':
        files = work.Class().get_files()

    bot.send_message(message.chat.id, files)

    
    # markup = types.ReplyKeyboardMarkup() #ReplyKeyboardHide()
    # markup.row(1,2)
    # markup.row(3,4,5)
    # bot.send_message(message.chat.id, "Choose your commands:", reply_markup=markup)



if __name__ == '__main__':
    bot.polling(none_stop=True)