import sqlite3
import time
from datetime import date, datetime, timedelta

from telebot import types
from telebot.types import Message
from telegram_bot_calendar import LSTEP, DetailedTelegramCalendar

import botrequests.bestdeal
import botrequests.lowprice
import database.databaseSQL
from keyboards.inline.city import kb_city
from keyboards.inline.count_hotel import kb_count_hotel
from keyboards.inline.count_photos import kb_count_photos
from keyboards.inline.loading_photo import kb_loading_photo
from loader import bot
from log.loguru_log import *
from utils.dict_class import User, user_dict


@logger.catch()
@bot.message_handler(commands=['history'])
def history_info(message: Message):
    """
    def history_info - выводим историю поиска отелей
    """

    bot.send_message(message.from_user.id, "Выводим историю поиска отелей")
    conn = sqlite3.connect('Too_Easy_Travel.db')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM history_search WHERE user_id={message.from_user.id}')
    request_history = cur.fetchall()
    if request_history:
        for elem in request_history[-10:]:
            bot.send_message(message.from_user.id,
                             f"""Команда: {elem[1][1:]}; 
Дата и время запроса: {elem[2]}; 
Найденные отели: {elem[3]};""")
        bot.send_message(message.from_user.id, "Ваши последние 10 запросов")
    else:
        bot.send_message(message.from_user.id, "Ваша история поиска отелей пуста ")
    conn.close()


@logger.catch()
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
    msg = bot.send_message(message.from_user.id,
                           "В каком городе будем искать отели? (Ввод города производите на английском языке)")
    bot.register_next_step_handler(msg, city_list)


@logger.catch()
def name_city(message):
    """
    def name_city - делаем повторный запрос города в случае, когда запрос не распознан
    """
    msg = bot.send_message(message.chat.id,
                           'Введите название города для поиска отеля? (Ввод города производите на английском языке)')
    bot.register_next_step_handler(msg, city_list)


@logger.catch()
def city_list(message):
    """
    def city_list - формирует список городов для клавиатуры
    """
    cities = botrequests.lowprice.get_city(message.text)
    user_dict[message.chat.id].city_list = cities
    if cities:
        bot.send_message(message.from_user.id, 'Выберите город :', reply_markup=kb_city(cities))
    else:
        msg = bot.send_message(message.chat.id, 'Не распознаный запрос')
        time.sleep(1)
        name_city(msg)


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.isnumeric())
def answer(call):
    """
        def answer - получаем с клавиатуры город где будем искать отели
        А так же id города
    """
    user_dict[call.message.chat.id].city_id = call.data
    for elem in user_dict[call.message.chat.id].city_list:
        if elem['destination_id'] == call.data:
            bot.send_message(call.message.chat.id, f"Вы выбрали {elem['city_name']}")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки
    if user_dict[call.message.chat.id].command == "/bestdeal":
        msg = bot.send_message(call.from_user.id,
                               "Введите минимальную цену проживания в отеле за сутки. (Цены указаны в долларах)")
        bot.register_next_step_handler(msg, min_price_def)
    else:
        get_count_hotel(call.message)


@logger.catch()
def min_price_def(message):
    """
    def min_price_def - получаем минимальную цену для фильтрации отелей
    """
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
                                       "К сожеления отелей с такой ценой нет. Введите цену меньше. (Цены указаны в долларах)")
                bot.register_next_step_handler(msg, min_price_def)
            else:
                user_dict[message.chat.id].bestdeal_list = bestdeal_list
                msg = bot.send_message(message.from_user.id,
                                       "Введите максимальную цену проживания в отеле за сутки. (Цены указаны в долларах)")
                bot.register_next_step_handler(msg, max_price_def)


@logger.catch()
def min_price_verify(message):
    """
    def min_price_verify - верификация значения минимальная цена
    На случай, когда пользователь вводит не число или число меньше 0
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести  положительное число")
    bot.register_next_step_handler(msg, min_price_def)


@logger.catch()
def max_price_def(message):
    """
        def max_price_def - получаем максимальную цену для фильтрации отелей
    """

    max_price = message.text
    if not max_price.isdigit():
        max_price_verify(message)
    else:
        max_price = int(message.text)
        if max_price < int(user_dict[message.chat.id].bestdeal_list[0]['ratePlan']['price']['current'][1:]):
            msg = bot.send_message(message.from_user.id,
                                   f"Отелей в таком диапазоне нет. Цена должна превышать {user_dict[message.chat.id].bestdeal_list[0]['ratePlan']['price']['current']}")
            bot.register_next_step_handler(msg, max_price_def)
        else:
            user_dict[message.chat.id].max_price = max_price
            bestdeal_list = botrequests.bestdeal.max_price(user_dict[message.chat.id].bestdeal_list,
                                                           user_dict[message.chat.id].max_price)
            # Сортируем bestdeal_list для по distance для поиска минимального и максимального расстояние от центра
            bestdeal_list = sorted(bestdeal_list,
                                   key=lambda distance: float(distance['landmarks'][0]['distance'].split()[0]))
            user_dict[message.chat.id].bestdeal_list = bestdeal_list
            msg = bot.send_message(message.from_user.id,
                                   "Введите минимальное расстояние отеля от центра. (Расстояние указано в километрах)")
            bot.register_next_step_handler(msg, min_distance_def)


@logger.catch()
def max_price_verify(message):
    """
    def max_price_verify - верификация значения максимальная цена
    На случай, когда пользователь вводит не число
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число ")
    bot.register_next_step_handler(msg, max_price_def)


@logger.catch()
def min_distance_def(message):
    """
    def min_distance_def - получаем минимальное  расстояние от центра для фильтрации отелей
    """

    min_distance = message.text
    if not min_distance.isdigit():
        min_distance_verify(message)
    else:
        min_distance = int(message.text)
        if min_distance < 0:
            min_distance_verify(message)
        else:
            if min_distance > float(
                    user_dict[message.chat.id].bestdeal_list[-1]['landmarks'][0]['distance'].split()[0]):
                msg = bot.send_message(message.from_user.id,
                                       f"Отелей в таком диапазоне нет. Растояние не должно превышать {user_dict[message.chat.id].bestdeal_list[-1]['landmarks'][0]['distance'].split()[0]}")
                bot.register_next_step_handler(msg, min_distance_def)
            else:
                user_dict[message.chat.id].min_distance = min_distance
                bestdeal_list = botrequests.bestdeal.min_distance(user_dict[message.chat.id].bestdeal_list,
                                                                  min_distance)
                user_dict[message.chat.id].bestdeal_list = bestdeal_list
                msg = bot.send_message(message.from_user.id,
                                       "Введите максимальное расстояние отеля от центра. (Расстояние указано в километрах)")
                bot.register_next_step_handler(msg, max_distance_def)


@logger.catch()
def min_distance_verify(message):
    """
    def min_distance_verify - верификация значения минимальное расстояние от центра
    На случай, когда пользователь вводит не число иличисло меньше 0
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести положительное число")
    bot.register_next_step_handler(msg, min_distance_def)


@logger.catch()
def max_distance_def(message):
    """
        def max_distance_def - получаем максимальную расстояние от центра для фильтрации отелей
    """
    max_distance = message.text
    if not max_distance.isdigit():
        max_distance_verify(message)
    else:
        max_distance = int(message.text)
        if max_distance < float(user_dict[message.chat.id].bestdeal_list[0]['landmarks'][0]['distance'].split()[0]):
            msg = bot.send_message(message.from_user.id,
                                   f"Отелей в таком диапазоне нет. Расстояние должно превышать {user_dict[message.chat.id].bestdeal_list[0]['landmarks'][0]['distance'].split()[0]}")
            bot.register_next_step_handler(msg, max_distance_def)
        else:
            user_dict[message.chat.id].max_distance = max_distance
            bestdeal_list = botrequests.bestdeal.max_distance(user_dict[message.chat.id].bestdeal_list,
                                                              user_dict[message.chat.id].max_distance)
            user_dict[message.chat.id].bestdeal_list = bestdeal_list
            get_count_hotel(message)


@logger.catch()
def max_distance_verify(message):
    """
    def max_distance_verify - верификация значения максимальная цена
    На случай, когда пользователь вводит не число
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число")
    bot.register_next_step_handler(msg, max_distance_def)


@logger.catch()
def get_count_hotel(message):
    """
    def get_count_hotel - вызываем клавиатуру для получения количества отелей для вывода на экран
    """
    bot.send_message(message.chat.id, text="Какое количество отелей вывести на экран?", reply_markup=kb_count_hotel())


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data in ['1hotel', '2hotel', '3hotel', '4hotel', '5hotel'])
def query_handler(call):
    """
       def query_handler - получаем с клавиатуры количество выводимых на экран отелей
       """
    answer = ''
    if call.data == '1hotel':
        answer = '1 отель'
        user_dict[call.message.chat.id].count_hotel = 1
    elif call.data == '2hotel':
        answer = '2 отеля'
        user_dict[call.message.chat.id].count_hotel = 2
    elif call.data == '3hotel':
        answer = '3 отеля'
        user_dict[call.message.chat.id].count_hotel = 3
    elif call.data == '4hotel':
        answer = '4 отеля'
        user_dict[call.message.chat.id].count_hotel = 4
    elif call.data == '5hotel':
        answer = '5 отелей'
        user_dict[call.message.chat.id].count_hotel = 5
    bot.send_message(call.message.chat.id, f'Вы выбрали {answer}')
    get_loading_photo(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки


@logger.catch()
def get_loading_photo(message):
    """
    def get_loading_photo - вызываем клавиатуру для запроса у пользователя загружать фотографии или нет

    """
    bot.send_message(message.chat.id, text="Хотите загрузить фото для отеля?", reply_markup=kb_loading_photo())


@logger.catch()
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


@logger.catch()
def get_count_photos(message):
    """
    get_count_photos - вызываем клавиатуру для получения количества фотографий для вывода на экран

    """

    bot.send_message(message.chat.id, text="Какое количество фотографий отеля вывести на экран?",
                     reply_markup=kb_count_photos())


@logger.catch()
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


@logger.catch()
def set_date_in(message):
    """
    def set_date_in - функция вызова даты заезда
    """
    bot.send_message(message.chat.id, "Выберите дату заезда")
    date_min = date.today()
    date_max = date_min + timedelta(days=90)
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date_min, max_date=date_max).build()
    bot.send_message(message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


@logger.catch()
def set_date_input(chat_id, date_in):
    """
    def set_date_input - записываем дату заезда
    """
    user_dict[chat_id].date_in = date_in


@logger.catch()
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


@logger.catch()
def get_date_input(chat_id):
    """
    def get_date_input - получаем дату заезда
    """
    return (user_dict[chat_id].date_in)


@logger.catch()
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


@logger.catch()
def set_date_output(chat_id, date_out):
    """
    def set_date_output - записываем дату выезда
    """
    user_dict[chat_id].date_out = date_out


@logger.catch()
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


@logger.catch()
def hotel_information(message):
    """
    def hotel_information - вывод информации по отелям на экран пользователя
    hotel_list - получаем список отелей
    photo_list - получаем список фотографий отелей
    """
    if user_dict[message.chat.id].command == "/bestdeal":
        hotel_list = user_dict[message.chat.id].bestdeal_list
    else:
        hotel_list = botrequests.lowprice.hotel_info(user_dict[message.chat.id].city_id,
                                                     user_dict[message.chat.id].count_hotel,
                                                     user_dict[message.chat.id].command)
        if not isinstance(hotel_list, list):
            bot.send_message(message.chat.id, f'Ошибка: {hotel_list}')
    city_list = []
    hotel_list = hotel_list[:user_dict[message.chat.id].count_hotel]
    for hotel in hotel_list:
        bot.send_message(message.chat.id, f'''Название отеля - {hotel['name']}
Адрес - {hotel['address']['countryName']},{hotel['address']['streetAddress'] if 'streetAddress' in hotel['address'] else 'Нет названия улицы'}
Расположение от центра  - {hotel['landmarks'][0]['distance']}
Цена  за ночь - {hotel['ratePlan']['price']['current']} 
Цена за весь период - {int(hotel['ratePlan']['price']['current'][1:]) * int((datetime.strptime(user_dict[message.chat.id].date_out, "%Y-%m-%d") - datetime.strptime(user_dict[message.chat.id].date_in, "%Y-%m-%d")).days)}
Ссылка на отель - https://ru.hotels.com/ho{hotel['id']}
            ''', disable_web_page_preview=True)
        if user_dict[message.chat.id].loading_photo == 'Да':
            bot.send_message(message.chat.id, 'Фото отеля')
            photos_id_hotel = hotel['id']
            photo_list = botrequests.lowprice.hotel_photo(photos_id_hotel, user_dict[message.chat.id].count_photo)
            photo_hotel_list = []
            for photo in photo_list:
                photo_url = photo['baseUrl']
                photo_for_user = photo_url.replace('{size}', 'z')
                photo_hotel_list.append(photo_for_user)
            bot.send_media_group(message.chat.id,
                                 media=[types.InputMediaPhoto(el_photo) for el_photo in photo_hotel_list])
        city_list.append(hotel['name'])
    city_list = "; ".join(city_list)

    database.databaseSQL.sqlite_create(user_dict[message.chat.id].id, user_dict[message.chat.id].command,
                                       user_dict[message.chat.id].data, city_list)
