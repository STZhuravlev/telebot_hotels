import telebot

token = '5016636848:AAHDnRgJKrdtY9cs7Cy67uSrDnKyl1BswqQ'
bot = telebot.TeleBot(token)
max_count_photo = 5


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


@bot.message_handler(content_types=['text'])
def get_city(message):
    global city
    city = message.text
    bot.send_message(message.from_user.id, "Какое количество отелей вывести на экран?(Максимальное количество - 5)")
    bot.register_next_step_handler(message, get_count_pnoto)


@bot.message_handler(content_types=['text'])
def get_count_pnoto(message):
    global count_photo
    try:
        count_photo = int(message.text)
        if count_photo > max_count_photo:
            count_photo = max_count_photo
        elif count_photo < 0:
            count_photo = 0
        bot.send_message(message.from_user.id, "Загрузить фото для отеля?")
        bot.register_next_step_handler(message, get_loading_photo)
    except ValueError:
        bot.send_message(message.from_user.id, "Необходимо ввести число")
        get_city(message)


@bot.message_handler(content_types=['text'])
def get_loading_photo(message):
    global loading_photo
    loading_photo = message.text
    bot.send_message(message.from_user.id,
                     f"Вы искали запрос по городу {city}. Количество отлей - {count_photo}. Выгрузить фото - {loading_photo}")


bot.polling(none_stop=True, interval=0)
