import telebot
from telebot import types
from telegram.config import token

TOKEN = ''
bot = telebot.TeleBot(token)

with open('text.txt', 'r') as file:
    BOOK = file.read() # открываем книгу и записываем её в BOOK

def pages_keyboard(start, stop):
    """Формируем Inline-кнопки для перехода по страницам.
    """
    keyboard = types.InlineKeyboardMarkup()
    btns = []
    if start > 0: btns.append(types.InlineKeyboardButton(
        text='', callback_data='to_{}'.format(start - 700)))
    if stop < len(BOOK): btns.append(types.InlineKeyboardButton(
        text='', callback_data='to_{}'.format(stop)))
    keyboard.add(*btns)
    return keyboard # возвращаем объект клавиатуры

@bot.message_handler(commands=['start'])
def start(m):
    """Отвечаем на команду /start
    """
    bot.send_message(m.chat.id, BOOK[:700], parse_mode='Markdown',
        reply_markup=pages_keyboard(0, 700))

@bot.callback_query_handler(func=lambda c: c.data)
def pages(c):
    """Редактируем сообщение каждый раз, когда пользователь переходит по
    страницам.
    """
    bot.edit_message_text(
        chat_id=c.message.chat.id,
        message_id=c.message.message_id,
        text=BOOK[int(c.data[3:]):int(c.data[3:]) + 100],
        parse_mode='Markdown',
        reply_markup=pages_keyboard(int(c.data[3:]),
            int(c.data[3:]) + 100))

bot.polling()