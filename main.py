import telebot
import os
from botrequests.lowprice import get_city
bot = telebot.TeleBot(os.getenv('TOKEN'))

@bot.message_handler(content_types=['text'])
def get_info(message):
    if message.text == "/help":
        bot.send_message(message.from_user.id, """1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра
(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать историю поиска отелей (команда /history)""")
    elif message.text == "/lowprice":
        bot.send_message(message.from_user.id, "В каком городе будем искать отель?")
        bot.register_next_step_handler(message, get_city)
    else:
        bot.send_message(message.from_user.id, "Для перехода в меню напиши /help.")

bot.polling(none_stop=True, interval=0)