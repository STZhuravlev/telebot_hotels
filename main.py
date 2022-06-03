import telebot
import os
from datetime import date, timedelta, datetime
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import botrequests.lowprice

bot = telebot.TeleBot(os.getenv('TOKEN'))
user_dict = dict()
max_count = 5


@bot.message_handler(commands=['lowprice'])
def first_command(message):
    """
    def first_command - делаем запрос в каком городе будем искать отели
    """
    msg = bot.send_message(message.from_user.id, "В каком городе будем искать отели?")
    bot.register_next_step_handler(msg, get_city)


@bot.message_handler(commands=['help'])
def help(message):
    """
    def help - вызывает помощь по командам бота
    """
    bot.send_message(message.from_user.id, """1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра
(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать историю поиска отелей (команда /history)""")


@bot.message_handler(content_types=['text'])
def help(message):
    """
    def help - вызывает команду для помощи в управление командами бота
    """
    bot.send_message(message.from_user.id, "Для перехода в меню напиши /help.")


def get_city(message):
    """
    def get_city - получаем название города где будем искать отели
    Делаем запрос на количество отелей выводимых на экран
    """
    try:
        city = message.text.capitalize()
        city_id, name_city = botrequests.lowprice.city_id(city)
        if city_id is not None:
            user_dict[message.chat.id] = {'city_id': city_id}
            msg = bot.send_message(message.from_user.id, f'Ищем отели в городе {name_city}')
            bot.send_message(message.from_user.id,
                             "Какое количество отелей вывести на экран?(Максимальное количество - 5)")
            bot.register_next_step_handler(msg, get_count_hotel)
        else:
            msg = bot.send_message(message.from_user.id, 'Поиск не распознаёт название города, повторите попытку')
            first_command(msg)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


def get_count_hotel(message):
    """
    def get_count_hotel - получаем количество отелей, коотрое выведем на экран пользователю
    А так же проверяем на минимальное и максимальное количество выводимых отелей на экран
    Минимальное количество - 1
    Максимальное количество - 5
    Делаем запрос на вывод фотографий отелей на экран
    """
    try:
        count_hotel = int(message.text)
        if count_hotel > max_count:
            user_dict[message.chat.id].update({'count_hotel': max_count})
        elif count_hotel < 1:
            user_dict[message.chat.id].update({'count_hotel': 1})
        else:
            user_dict[message.chat.id].update({'count_hotel': count_hotel})
        msg = bot.send_message(message.from_user.id, "Загрузить фото для отеля?")
        bot.register_next_step_handler(msg, get_loading_photo)
    except ValueError:
        verify_count_hotel(message)


def verify_count_hotel(message):
    """
    def verify_count_pnoto - верификация значения количество отелей
    На случай, когда пользователь вводит не число
    """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(msg, get_count_hotel)


def get_loading_photo(message):
    """
    def get_loading_photo - спрашивает у пользователя загружать фотографии или нет
     Делаем запрос на количествовывода фотографий отелей на экран, если ответ ДА
    Переходим к календарю для выбора даты заезда
    """
    loading_photo = message.text.capitalize()
    if loading_photo == 'Да' or loading_photo == 'Нет':
        user_dict[message.chat.id].update({'loading_photo': loading_photo})
        if loading_photo == 'Да':
            msg = bot.send_message(message.from_user.id,
                                   "Какое количество фотографий отеля вывести на экран?(Максимальное количество - 5)")
            bot.register_next_step_handler(msg, get_count_photos)
        else:
            set_date_in(message)
    else:
        verify_loading_photo(message)


def verify_loading_photo(message):
    """
    def verify_loading_photo - верификация на ответ ДА или НЕТ
    Если ответ не совпадает, бот переспраштвает до тех пор пока не получит необходимый ответ
    """
    msg = bot.send_message(message.from_user.id, "ДА ли НЕТ")
    bot.register_next_step_handler(msg, get_loading_photo)


def get_count_photos(message):
    """
    get_count_photos - получаем количество фотографий, которое выведем на экран
       Максимаотное коичество - 5
       Минимальное количество - 1
       Переходим к календарю для выбора даты заезда'
       """
    try:
        count_photo = int(message.text)
        if count_photo > max_count:
            user_dict[message.chat.id].update({'count_photo': max_count})
        elif count_photo < 1:
            user_dict[message.chat.id].update({'count_photo': 1})
        else:
            user_dict[message.chat.id].update({'count_photo': count_photo})
        set_date_in(message)
    except ValueError:
        verify_count_photo(message)


def verify_count_photo(message):
    """
    def verify_count_pnoto - верификация значения количества фотографий
    На случай, когда пользователь вводит не число
   """
    msg = bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(msg, get_count_photos)


def set_date_in(message):
    """
    def set_date_in - функция вызова даты заезда
    """
    bot.send_message(message.from_user.id, "Выберите дату заезда")
    date_min = date.today()
    date_max = date_min + timedelta(days=90)
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=date_min, max_date=date_max).build()
    bot.send_message(message.chat.id, f"Выберите {LSTEP[step]}", reply_markup=calendar)


def set_date_input(chat_id, date_in):
    """
    def set_date_input - записываем дату заезда
    """
    user_dict[chat_id].update({'date_in': date_in})


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
    return (user_dict[chat_id]['date_in'])


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
    user_dict[chat_id].update({'date_out': date_out})


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
        hotel_list = botrequests.lowprice.hotel_info(user_dict[message.chat.id]['city_id'], max_count)
        for hotel in range(user_dict[message.chat.id]['count_hotel']):
            bot.send_message(message.chat.id, f'''{hotel + 1}.Название отеля - {hotel_list[hotel]['name']}
            Адрес - {hotel_list[hotel]['address']['countryName']},{hotel_list[hotel]['address']['streetAddress'] if 'streetAddress' in hotel_list[hotel]['address'] else 'Нет названия улицы'}
            Расположение от центра  - {hotel_list[hotel]['landmarks'][0]['distance']}
            Цена  за ночь - {hotel_list[hotel]['ratePlan']['price']['current']} 
            Цена за весь период - {int(hotel_list[hotel]['ratePlan']['price']['current'][1:]) *
                                   int((datetime.strptime(user_dict[message.chat.id]['date_out'], "%Y-%m-%d") - datetime.strptime(user_dict[message.chat.id]['date_in'], "%Y-%m-%d")).days)}
            Ссылка на отель - https://ru.hotels.com/ho{hotel_list[hotel]['id']}
            ''', disable_web_page_preview=True)
            if user_dict[message.chat.id]['loading_photo'] == 'Да':
                bot.send_message(message.chat.id, 'Фото отеля')
                photos_id_hotel = hotel_list[hotel]['id']
                photo_list = botrequests.lowprice.hotel_photo(photos_id_hotel, max_count)
                for photo in range(user_dict[message.chat.id]['count_photo']):
                    photo_url = photo_list[photo]['baseUrl']
                    photo_for_user = photo_url.replace('{size}', 'z')
                    bot.send_photo(message.chat.id, photo_for_user)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")


bot.polling(none_stop=True, interval=0)
