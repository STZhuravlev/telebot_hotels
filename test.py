import telebot
import requests
import json
from datetime import datetime

token = '5016636848:AAHDnRgJKrdtY9cs7Cy67uSrDnKyl1BswqQ'
bot = telebot.TeleBot(token)

max_count = 5

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
    '''def get_city - получаем название города где будем искать отели'''
    try:
        hotel_info_dict = dict()
        town = message.text.title()
        hotel_info_dict['city'] = town
        bot.send_message(message.from_user.id, "Какое количество отелей вывести на экран?(Максимальное количество - 5)")
        bot.register_next_step_handler(message, get_count_hotel,hotel_info_dict)
    except ValueError:
        bot.send_message(message.from_user.id, "Что-то пошло не так")

@bot.message_handler(content_types=['text'])
def get_count_hotel(message,hotel_info_dict):
    '''def get_count_hotel - получаем количество отелей, коотрое выведем на экран пользователю
    А так же проверяем на минимальное и максимальное количество выводимых отелей на экран
    Минимальное количество - 1
    Максимальное количество - 5'''
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

@bot.message_handler(content_types=['text'])
def verify_count_hotel(message,hotel_info_dict):
    '''def verify_count_pnoto - верификация значения количество отелей
    На случай, когда пользователь вводит не число'''
    bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(message, get_count_hotel,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def get_loading_photo(message,hotel_info_dict):
    '''def get_loading_photo - спрашивает у пользователя загружать фотографии или нет'''
    loading_photo = message.text.capitalize()
    if loading_photo == 'Да' or loading_photo == 'Нет':
        hotel_info_dict['loading_photo'] = loading_photo
        if loading_photo == 'Да':
            bot.send_message(message.from_user.id, "Какое количество фотографий отеля вывести на экран?(Максимальное количество - 5)")
            bot.register_next_step_handler(message, get_count_photos,hotel_info_dict)
        else:
            bot.send_message(message.from_user.id, "Введите  дату заезда в отель в формате ГГГГ-ММ-ДД")
            bot.register_next_step_handler(message, get_data_first, hotel_info_dict)
    else:
        verify_loading_photo(message,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def verify_loading_photo(message,hotel_info_dict):
    '''def verify_loading_photo - верификация на ответ ДА или НЕТ
    Если ответ не совпадает, бот переспраштвает до тех пор пока не получит необходимый ответ'''
    bot.send_message(message.from_user.id, "ДА ли НЕТ")
    bot.register_next_step_handler(message, get_loading_photo,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def get_count_photos(message,hotel_info_dict):
    '''get_count_photos - получаем количество фотографий, которое выведем на экран
       Максимаотное коичество - 5
       Минимальное количество - 1'''
    try:
        count_photo = int(message.text)
        if count_photo > max_count:
            hotel_info_dict['count_photo'] = max_count
        elif count_photo < 1:
            hotel_info_dict['count_photo'] = 1
        else:
            hotel_info_dict['count_photo'] = count_photo
        bot.send_message(message.from_user.id, "Введите  дату заезда в отель в формате ГГГГ-ММ-ДД")
        bot.register_next_step_handler(message, get_data_first, hotel_info_dict)
    except ValueError:
        verify_count_photo(message,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def verify_count_photo(message,hotel_info_dict):
    '''def verify_count_pnoto - верификация значения количества фотографий
    На случай, когда пользователь вводит не число'''
    bot.send_message(message.from_user.id, "Необходимо ввести число от 1 до 5")
    bot.register_next_step_handler(message, get_count_photos,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def get_data_first(message,hotel_info_dict):
    data_first = message.text
    try:
        data_first = datetime.strptime(data_first, "%Y-%m-%d")
        if data_first<datetime.today():
            new_data_first(message, hotel_info_dict)
        else:
            hotel_info_dict['data_first'] = data_first
            bot.send_message(message.from_user.id, f"Введите  дату выезда из отеля в формате ГГГГ-ММ-ДД")
            bot.register_next_step_handler(message, get_data_second, hotel_info_dict)
    except ValueError:
        ver_data_first(message,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def new_data_first(message,hotel_info_dict):
    bot.send_message(message.from_user.id, f"Нельзя ввести прошедшую дату или сегодняшнюю")
    bot.register_next_step_handler(message, get_data_first, hotel_info_dict)

@bot.message_handler(content_types=['text'])
def ver_data_first(message,hotel_info_dict):
    bot.send_message(message.from_user.id, f"Нарушен формат даты ГГГГ-ММ-ДД (Пример - 2020-08-28")
    bot.register_next_step_handler(message, get_data_first, hotel_info_dict)

@bot.message_handler(content_types=['text'])
def get_data_second(message, hotel_info_dict):
    data_second = message.text
    try:
        data_second = datetime.strptime(data_second, "%Y-%m-%d")
        if data_second<=hotel_info_dict['data_first']:
            new_data_second(message, hotel_info_dict)
        else:
            hotel_info_dict['data_second'] = data_second
            bot.send_message(message.from_user.id, f"Ищем отели")
            find_hotel(message, hotel_info_dict)
    except ValueError:
        ver_data_second(message,hotel_info_dict)

@bot.message_handler(content_types=['text'])
def new_data_second(message,hotel_info_dict):
    bot.send_message(message.from_user.id, f"Дата заезда ментше даты выезда. Выберите другую дату выезда")
    bot.register_next_step_handler(message, get_data_second, hotel_info_dict)

@bot.message_handler(content_types=['text'])
def ver_data_second(message,hotel_info_dict):
    bot.send_message(message.from_user.id, f"Нарушен формат даты")
    bot.register_next_step_handler(message, get_data_second, hotel_info_dict)

@bot.message_handler(content_types=['text'])
def find_hotel(message,hotel_info_dict):
    '''def find_hotel - вывод информации на экран
    SEARCH - поиск ID города
    LIST - поиск информации (включая ID) по отелю в необходимом нам городе
    PHOTO - вывод фотографий отеля, использую ID отеля'''
    url_search = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring_search = {"query": hotel_info_dict['city']}
    headers = {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": "527b11d531msh6c265bd924a04d8p1167b4jsnef881ce84a9f"
    }
    try:
        response_search = requests.get(url_search, headers=headers, params=querystring_search)
        response_new_search = json.loads(response_search.text)
        response_hotel_city_group = list(filter(lambda x: x['group'] == 'CITY_GROUP', response_new_search['suggestions']))
        destination_Id_filter =list(filter(lambda city: city['type'] == 'CITY', response_hotel_city_group[0]['entities']))
        new_destination_Id = [elem_city['destinationId']   for elem_city in destination_Id_filter if hotel_info_dict['city'][:3] in elem_city['caption'].replace(hotel_info_dict['city'][:3], '', 1) ]

        url_list = "https://hotels4.p.rapidapi.com/properties/list"
        querystring_list = {"destinationId": new_destination_Id[0], "pageNumber": "1", "pageSize": "25",
                            "checkIn": "2020-01-08",
                            "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
        response_list = requests.get(url_list, headers=headers, params=querystring_list)
        response_new_list = json.loads(response_list.text)
        result_list = response_new_list['data']['body']['searchResults']['results']
        result_sort = sorted(result_list, key=lambda price: price['ratePlan']['price']['current'], reverse=False)

        url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        for x in range(hotel_info_dict['count_hotel']):
            bot.send_message(message.from_user.id, f'''{x + 1}.Название отеля - {result_sort[x]['name']}
Адрес - {result_sort[x]['address']['countryName']},{result_sort[x]['address']['streetAddress'] if  'streetAddress'  in  result_sort[x]['address']  else 'Нет названия улицы'}
Расположение от центра  - {result_sort[x]['landmarks'][0]['distance']}
Цена  за ночь - {result_sort[x]['ratePlan']['price']['current']} 
Цена за весь период {int(result_sort[x]['ratePlan']['price']['current'][1:]) * int((hotel_info_dict['data_second'] - hotel_info_dict['data_first']).days)}
''')
            if hotel_info_dict['loading_photo'] == 'Да':
                bot.send_message(message.from_user.id, 'Фото отеля')
                photos_id_hotel = result_sort[x]['id']
                querystring = {"id": photos_id_hotel}
                response_photos = requests.get(url_photos, headers=headers, params=querystring)
                response__new_photos = json.loads(response_photos.text)
                photos = response__new_photos['hotelImages']
                for photo in range(hotel_info_dict['count_photo']):
                    photo_url = photos[photo]['baseUrl']
                    photo_for_user = photo_url.replace('{size}', 'z')
                    bot.send_photo(message.from_user.id, photo_for_user)

    except IndexError:
        bot.send_message(message.from_user.id, "Что-то пошло не так, уточните название города")

bot.polling(none_stop=True, interval=0)
