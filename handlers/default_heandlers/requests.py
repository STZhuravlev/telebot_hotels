from telebot.types import Message
from telebot import types

import database.databaseSQL
import sqlite3
from datetime import date, timedelta, datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import botrequests.lowprice
import botrequests.bestdeal
from keyboards.inline.count_hotel import kb_count_hotel
from keyboards.inline.loading_photo import kb_loading_photo
from keyboards.inline.count_photos import kb_count_photos
from loader import bot
from utils.dict_class import user_dict, User


# import keyboards.inline.count_hotel

@bot.message_handler(commands=['history'])
def history_info(message: Message):
    """
    def history_info - выводим историю поиска отелей
    """
    try:
        bot.send_message(message.from_user.id, "Выводим историю поиска отелей")
        conn = sqlite3.connect('Too_Easy_Travel.db')
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM history_search WHERE user_id={message.from_user.id}')
        for i in cur.fetchall():
            bot.send_message(message.from_user.id,
                             f'Команда = {i[1]}, Дата и время запроса = {i[2]}, Найденные отели = {i[3]} ')
        conn.close()
    except sqlite3.OperationalError:
        bot.send_message(message.from_user.id, "База данных ещё пуста")


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def first_command(message: Message):
    """
    def first_command - делаем запрос в каком городе будем искать отели
    """
    user_dict[message.chat.id] = User()
    user_dict[message.chat.id].id = message.chat.id
    now = datetime.now()
    data_now = now.strftime("%d-%m-%Y %H:%M")
    user_dict[message.chat.id].data = data_now
    user_dict[message.chat.id].command = message.text
    msg = bot.send_message(message.from_user.id, "В каком городе будем искать отели?")
    bot.register_next_step_handler(msg, get_city)


def get_city(message):
    """
    def get_city - получаем название города где будем искать отели
    Делаем запрос на количество отелей выводимых на экран
    """
    try:
        city = message.text.capitalize()
        city_id, name_city = botrequests.lowprice.city_id(city)
        if city_id is not None:
            user_dict[message.chat.id].city_id = city_id
            bot.send_message(message.from_user.id, f'Ищем отели в городе {name_city}')
            if user_dict[message.chat.id].command == "/bestdeal":
                msg = bot.send_message(message.from_user.id,
                                       "Введите минимальную цену проживания в отеле за сутки")
                bot.register_next_step_handler(msg, min_price_def)
            else:
                get_count_hotel(message)
        else:
            msg = bot.send_message(message.from_user.id, 'Поиск не распознаёт название города, повторите ввод города')
            bot.register_next_step_handler(msg, get_city)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def min_price_def(message):
    """
    def min_price_def - получаем минимальную цену для фильтрации отелей
    """
    try:
        min_price = message.text
        if not min_price.isdigit():
            min_price_verify(message)
        else:
            min_price = int(message.text)
            if min_price < 0:
                min_price_verify(message)
            else:
                user_dict[message.chat.id].min_price = min_price
                bestdeal_list = botrequests.bestdeal.min_price(user_dict[message.chat.id].city_id, min_price)
                if not bestdeal_list:
                    msg = bot.send_message(message.from_user.id,
                                           "К сожеления отелей с такой ценой нет. Введите цену меньше")
                    bot.register_next_step_handler(msg, min_price_def)
                else:
                    user_dict[message.chat.id].bestdeal_list = bestdeal_list
                    msg = bot.send_message(message.from_user.id,
                                           "Введите максимальную цену проживания в отеле за сутки")
                    bot.register_next_step_handler(msg, max_price_def)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def min_price_verify(message):
    """
    def min_price_verify - верификация значения минимальная цена
    На случай, когда пользователь вводит не число или число меньше 0
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести  положительное число")
    bot.register_next_step_handler(msg, min_price_def)


def max_price_def(message):
    """
        def max_price_def - получаем максимальную цену для фильтрации отелей
    """
    try:
        max_price = message.text
        if not max_price.isdigit():
            max_price_verify(message)
        else:
            max_price = int(message.text)
            if max_price < user_dict[message.chat.id].min_price:
                user_dict[message.chat.id].max_price = user_dict[message.chat.id].min_price
            else:
                user_dict[message.chat.id].max_price = max_price

            bestdeal_list = botrequests.bestdeal.max_price(user_dict[message.chat.id].bestdeal_list,
                                                           user_dict[message.chat.id].max_price)
            user_dict[message.chat.id].bestdeal_list = bestdeal_list
            msg = bot.send_message(message.from_user.id, "Введите минимальное расстояние отеля от центра")
            bot.register_next_step_handler(msg, min_distance_def)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def max_price_verify(message):
    """
    def max_price_verify - верификация значения максимальная цена
    На случай, когда пользователь вводит не число
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число ")
    bot.register_next_step_handler(msg, max_price_def)


def min_distance_def(message):
    """
    def min_distance_def - получаем минимальное  расстояние от центра для фильтрации отелей
    """
    try:
        min_distance = message.text
        if not min_distance.isdigit():
            min_distance_verify(message)
        else:
            min_distance = int(message.text)
            if min_distance < 0:
                min_distance_verify(message)
            else:
                user_dict[message.chat.id].min_distance = min_distance
                bestdeal_list = botrequests.bestdeal.min_distance(user_dict[message.chat.id].bestdeal_list,
                                                                  min_distance)
                if not bestdeal_list:
                    msg = bot.send_message(message.from_user.id,
                                           "К сожеления отелей на таком расстоянии нет. Введите больше расстояние")
                    bot.register_next_step_handler(msg, min_distance_def)
                else:
                    user_dict[message.chat.id].bestdeal_list = bestdeal_list
                    msg = bot.send_message(message.from_user.id, "Введите максимальное расстояние отеля от центра")
                    bot.register_next_step_handler(msg, max_distance_def)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def min_distance_verify(message):
    """
    def min_distance_verify - верификация значения минимальное расстояние от центра
    На случай, когда пользователь вводит не число иличисло меньше 0
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести положительное число")
    bot.register_next_step_handler(msg, min_distance_def)


def max_distance_def(message):
    """
        def max_distance_def - получаем максимальную расстояние от центра для фильтрации отелей
    """
    try:
        max_distance = message.text
        if not max_distance.isdigit():
            max_distance_verify(message)
        else:
            max_distance = int(message.text)
            if max_distance < user_dict[message.chat.id].min_distance:
                user_dict[message.chat.id].max_distance = user_dict[message.chat.id].min_distance
            else:
                user_dict[message.chat.id].max_distance = max_distance
            bestdeal_list = botrequests.bestdeal.max_distance(user_dict[message.chat.id].bestdeal_list,
                                                              user_dict[message.chat.id].max_distance)
            user_dict[message.chat.id].bestdeal_list = bestdeal_list
            get_count_hotel(message)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def max_distance_verify(message):
    """
    def max_distance_verify - верификация значения максимальная цена
    На случай, когда пользователь вводит не число
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число")
    bot.register_next_step_handler(msg, max_distance_def)


def get_count_hotel(message):
    """
    def get_count_hotel - вызываем клавиатуру для получения количества отелей для вывода на экран
    """
    bot.send_message(message.chat.id, text="Какое количество отелей вывести на экран?", reply_markup=kb_count_hotel())


@bot.callback_query_handler(func=lambda call: call.data in ['1', '2', '3', '4', '5'])
def query_handler(call):
    """
       def query_handler - получаем с клавиатуры количество выводимых на экран отелей
       """
    answer = ''
    if call.data == '1':
        answer = '1 отель'
        user_dict[call.message.chat.id].count_hotel = 1
    elif call.data == '2':
        answer = '2 отеля'
        user_dict[call.message.chat.id].count_hotel = 2
    elif call.data == '3':
        answer = '3 отеля'
        user_dict[call.message.chat.id].count_hotel = 3
    elif call.data == '4':
        answer = '4 отеля'
        user_dict[call.message.chat.id].count_hotel = 4
    elif call.data == '5':
        answer = '5 отелей'
        user_dict[call.message.chat.id].count_hotel = 5
    bot.send_message(call.message.chat.id, f'Вы выбрали {answer}')
    get_loading_photo(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки


def get_loading_photo(message):
    """
    def get_loading_photo - вызываем клавиатуру для запроса у пользователя загружать фотографии или нет

    """

    bot.send_message(message.chat.id, text="Хотите загрузить фото для отеля?", reply_markup=kb_loading_photo())


@bot.callback_query_handler(func=lambda call: call.data in ['Да', 'Нет'])
def query_handler(call):
    """
    def query_handler - получаем с клавиатуры  ответ от пользователя загружать фотографии или нет

    """
    if call.data == 'Да':
        user_dict[call.message.chat.id].loading_photo = call.data
        get_count_photos(call.message)
    elif call.data == 'Нет':
        user_dict[call.message.chat.id].loading_photo = call.data
        set_date_in(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки


def get_count_photos(message):
    """
    get_count_photos - вызываем клавиатуру для получения количества фотографий для вывода на экран

    """

    bot.send_message(message.chat.id, text="Какое количество фотографий отеля вывести на экран?", reply_markup=kb_count_photos())


@bot.callback_query_handler(func=lambda call: call.data in ['1photo', '2photo', '3photo', '4photo', '5photo'])
def query_handler(call):
    """
    query_handler - получаем с клавиатуры количество фотографий, которое выведем на экран

    """

    if call.data == '1photo':
        user_dict[call.message.chat.id].count_photo = 1
    elif call.data == '2photo':
        user_dict[call.message.chat.id].count_photo = 2
    elif call.data == '3photo':
        user_dict[call.message.chat.id].count_photo = 3
    elif call.data == '4photo':
        user_dict[call.message.chat.id].count_photo = 4
    elif call.data == '5photo':
        user_dict[call.message.chat.id].count_photo = 5
    set_date_in(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки


def set_date_in(message):
    """
    def set_date_in - функция вызова даты заезда
    """
    bot.send_message(message.chat.id, "Выберите дату заезда")
    date_min = date.today()
    date_max = date_min + timedelta(days=90)
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date_min, max_date=date_max).build()
    bot.send_message(message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


def set_date_input(chat_id, date_in):
    """
    def set_date_input - записываем дату заезда
    """
    user_dict[chat_id].date_in = date_in


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal(callback_query):
    """
    Функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ,
    передает ответ в БД, и переходит к следующему шагу
    """
    date_min = date.today()
    date_max = date.today() + timedelta(days=90)
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date_min,
                                                 max_date=date_max).process(callback_query.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              callback_query.message.chat.id,
                              callback_query.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              callback_query.message.chat.id,
                              callback_query.message.message_id)
        set_date_input(chat_id=callback_query.message.chat.id, date_in=str(result))
        date_out(callback_query.message.chat.id)


def get_date_input(chat_id):
    """
    def get_date_input - получаем дату заезда
    """
    return (user_dict[chat_id].date_in)


def date_out(chat_id):
    """
    def date_out - функция вызова даты въезда
    """
    date_today_min = (datetime.strptime(get_date_input(chat_id=chat_id), "%Y-%m-%d") + timedelta(
        days=1)).date()
    date_today_max = date_today_min + timedelta(days=90)
    bot.send_message(chat_id, "Выберите дату выезда")
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru', min_date=date_today_min,
                                              max_date=date_today_max).build()
    bot.send_message(chat_id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


def set_date_output(chat_id, date_out):
    """
    def set_date_output - записываем дату выезда
    """
    user_dict[chat_id].date_out = date_out


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal(callback_query):
    """
    def cal - функция обработчик календаря, выводит клавиатуру с календарем и ожидает ответ,
    передает ответ в БД, и переходит к следующему шагу
    """
    date_today_min = (datetime.strptime(get_date_input(chat_id=callback_query.message.chat.id), "%Y-%m-%d") + timedelta(
        days=1)).date()
    date_today_max = date_today_min + timedelta(days=90)
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                 min_date=date_today_min, max_date=date_today_max).process(
        callback_query.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              callback_query.message.chat.id,
                              callback_query.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              callback_query.message.chat.id,
                              callback_query.message.message_id)
        set_date_output(chat_id=callback_query.message.chat.id, date_out=str(result))
        hotel_information(callback_query.message)


def hotel_information(message):
    """
    def hotel_information - вывод информации по отелям на экран пользователя
    hotel_list - получаем список отелей
    photo_list - получаем список фотографий отелей
    """
    try:
        if user_dict[message.chat.id].command == "/bestdeal":
            hotel_list = user_dict[message.chat.id].bestdeal_list
        else:
            hotel_list = botrequests.lowprice.hotel_info(user_dict[message.chat.id].city_id,
                                                         user_dict[message.chat.id].count_hotel,
                                                         user_dict[message.chat.id].command)
        city_list = []
        hotel_list = hotel_list[:user_dict[message.chat.id].count_hotel]
        for hotel in hotel_list:
            bot.send_message(message.chat.id, f'''Название отеля - {hotel['name']}
            Адрес - {hotel['address']['countryName']},{hotel['address']['streetAddress'] if 'streetAddress' in hotel['address'] else 'Нет названия улицы'}
            Расположение от центра  - {hotel['landmarks'][0]['distance']}
            Цена  за ночь - {hotel['ratePlan']['price']['current']} 
            Цена за весь период - {int(hotel['ratePlan']['price']['current'][1:]) *
                                   int((datetime.strptime(user_dict[message.chat.id].date_out, "%Y-%m-%d") - datetime.strptime(user_dict[message.chat.id].date_in, "%Y-%m-%d")).days)}
            Ссылка на отель - https://ru.hotels.com/ho{hotel['id']}
            ''', disable_web_page_preview=True)
            if user_dict[message.chat.id].loading_photo == 'Да':
                bot.send_message(message.chat.id, 'Фото отеля')
                photos_id_hotel = hotel['id']
                photo_list = botrequests.lowprice.hotel_photo(photos_id_hotel, user_dict[message.chat.id].count_photo)
                for photo in photo_list:
                    photo_url = photo['baseUrl']
                    photo_for_user = photo_url.replace('{size}', 'z')
                    bot.send_photo(message.chat.id, photo_for_user)
            city_list.append(hotel['name'])
        city_list = "; ".join(city_list)

        database.databaseSQL.sqlite_create(user_dict[message.chat.id].id, user_dict[message.chat.id].command,
                                           user_dict[message.chat.id].data, city_list)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")
