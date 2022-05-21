import telebot
import os
# pip install python-telegram-bot-calendar
from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import botrequests.lowprice

bot = telebot.TeleBot(os.getenv('TOKEN'))
max_count = 5

@bot.message_handler(commands=['lowprice'])
def first_command(message):
    '''def first_command - делаем запрос в каком городе будем искать отели '''
    bot.send_message(message.from_user.id, "В каком городе будем искать отели?")
    bot.register_next_step_handler(message, get_city)


@bot.message_handler(content_types=['text'])
def help(message):
    bot.send_message(message.from_user.id, """1. Узнать топ самых дешёвых отелей в городе (команда /lowprice).
2. Узнать топ самых дорогих отелей в городе (команда /highprice).
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра
(самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
4. Узнать историю поиска отелей (команда /history)""")

@bot.message_handler(content_types=['text'])
def help(message):
    bot.send_message(message.from_user.id, "Для перехода в меню напиши /help.")

def get_city(message):
    '''def get_city - получаем название города где будем искать отели
    Делаем запрос на количество отелей выводимых на экран'''
    try:
        hotel_info_dict = dict()
        town = message.text.capitalize()
        city_id, name_city = botrequests.lowprice.city_id(town)
        if city_id is not None:
            hotel_info_dict['city_id'] = city_id
            bot.send_message(message.from_user.id, f'Ищем отели в городе {name_city}')
            bot.send_message(message.from_user.id, "Какое количество отелей вывести на экран?(Максимальное количество - 5)")
            bot.register_next_step_handler(message, get_count_hotel,hotel_info_dict)
        else:
            bot.send_message(message.from_user.id, 'Поиск не распознаёт название города, повторите попытку')
            first_command(message)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")

def get_count_hotel(message, hotel_info_dict):
    '''def get_count_hotel - получаем количество отелей, коотрое выведем на экран пользователю
    А так же проверяем на минимальное и максимальное количество выводимых отелей на экран
    Минимальное количество - 1
    Максимальное количество - 5
    Делаем запрос на вывод фотографий отелей на экран'''
    try:
        count_hotel = int(message.text)
        if count_hotel > max_count:
            hotel_info_dict['count_hotel'] = max_count
        elif count_hotel < 1:
            hotel_info_dict['count_hotel']= 1
        else:
            hotel_info_dict['count_hotel']= count_hotel
        bot.send_message(message.from_user.id, "Загрузить фото для отеля?")
        bot.register_next_step_handler(message, get_loading_photo, hotel_info_dict)
    except ValueError:
        verify_count_hotel(message, hotel_info_dict)

def verify_count_hotel(message,hotel_info_dict):
    '''def verify_count_pnoto - верификация значения количество отелей
    На случай, когда пользователь вводит не число'''
    bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(message, get_count_hotel,hotel_info_dict)

def get_loading_photo(message,hotel_info_dict):
    '''def get_loading_photo - спрашивает у пользователя загружать фотографии или нет
     Делаем запрос на количествовывода фотографий отелей на экран, если ответ ДА
    Переходим к календарю для выбора даты заезда'''
    loading_photo = message.text.capitalize()
    if loading_photo == 'Да' or loading_photo == 'Нет':
        hotel_info_dict['loading_photo'] = loading_photo
        if loading_photo == 'Да':
            bot.send_message(message.from_user.id, "Какое количество фотографий отеля вывести на экран?(Максимальное количество - 5)")
            bot.register_next_step_handler(message, get_count_photos,hotel_info_dict)
        else:
            calendar_check_in(message,hotel_info_dict)
    else:
        verify_loading_photo(message,hotel_info_dict)

def verify_loading_photo(message,hotel_info_dict):
    '''def verify_loading_photo - верификация на ответ ДА или НЕТ
    Если ответ не совпадает, бот переспраштвает до тех пор пока не получит необходимый ответ'''
    bot.send_message(message.from_user.id, "ДА ли НЕТ")
    bot.register_next_step_handler(message, get_loading_photo,hotel_info_dict)

def get_count_photos(message,hotel_info_dict):
    '''get_count_photos - получаем количество фотографий, которое выведем на экран
       Максимаотное коичество - 5
       Минимальное количество - 1
       Переходим к календарю для выбора даты заезда'       '''
    try:
        count_photo = int(message.text)
        if count_photo > max_count:
            hotel_info_dict['count_photo'] = max_count
        elif count_photo < 1:
            hotel_info_dict['count_photo'] = 1
        else:
            hotel_info_dict['count_photo'] = count_photo
        calendar_check_in(message,hotel_info_dict)
    except ValueError:
        verify_count_photo(message,hotel_info_dict)

def verify_count_photo(message,hotel_info_dict):
    '''def verify_count_pnoto - верификация значения количества фотографий
    На случай, когда пользователь вводит не число'''
    bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(message, get_count_photos,hotel_info_dict)


def calendar_check_in(message,hotel_info_dict):
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today(),
                                              max_date=date.today() + timedelta(days=90), locale='ru').build()
    bot.send_message(message.chat.id, f"Заезд: Выберите {LSTEP[step]}", reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal1(c):
    result, key, step = DetailedTelegramCalendar(calendar_id=1,min_date=date.today(),max_date=date.today()+timedelta(days=90), locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Заезд: Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали  {result} дату заезда",
                              c.message.chat.id,
                              c.message.message_id)

def calendar_check_out(message,hotel_info_dict):
    calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
    bot.send_message(message.chat.id,
                     f"Calendar 2: Выберите {LSTEP[step]}",
                     reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal1(c):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выезд: Выберите {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result} дату выезда",
                              c.message.chat.id,
                              c.message.message_id)
bot.polling(none_stop=True, interval=0)