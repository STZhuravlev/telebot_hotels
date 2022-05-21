import requests
import json
from datetime import datetime
import os

headers = {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": os.getenv('APIKEY')
    }


def city_id(name_city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": name_city}
    response = requests.get(url, headers=headers, params=querystring)
    response_new = json.loads(response.text)
    response_hotel_city_group = list(filter(lambda x: x['group'] == 'CITY_GROUP', response_new['suggestions']))
    destination_Id_filter =list(filter(lambda city: city['type'] == 'CITY', response_hotel_city_group[0]['entities']))
    if not destination_Id_filter:
        return None
    else:
        for elem_city in destination_Id_filter:
            my_city = elem_city['caption'].replace(name_city[0:3], '', 1)
            if name_city[0:3] in my_city:
                    return elem_city['destinationId'], elem_city['name']


# print (city_id('new'.capitalize()))






# def get_data_first(message,hotel_info_dict):
#     data_first = message.text
#     try:
#         data_first = datetime.strptime(data_first, "%Y-%m-%d")
#         if data_first<datetime.today():
#             new_data_first(message, hotel_info_dict)
#         else:
#             hotel_info_dict['data_first'] = data_first
#             bot.send_message(message.from_user.id, f"Введите  дату выезда из отеля в формате ГГГГ-ММ-ДД")
#             bot.register_next_step_handler(message, get_data_second, hotel_info_dict)
#     except ValueError:
#         ver_data_first(message,hotel_info_dict)
#
# def new_data_first(message,hotel_info_dict):
#     bot.send_message(message.from_user.id, f"Нельзя ввести прошедшую дату или сегодняшнюю")
#     bot.register_next_step_handler(message, get_data_first, hotel_info_dict)
#
# def ver_data_first(message,hotel_info_dict):
#     bot.send_message(message.from_user.id, f"Нарушен формат даты ГГГГ-ММ-ДД (Пример - 2020-08-28")
#     bot.register_next_step_handler(message, get_data_first, hotel_info_dict)
#
# def get_data_second(message, hotel_info_dict):
#     data_second = message.text
#     try:
#         data_second = datetime.strptime(data_second, "%Y-%m-%d")
#         if data_second<=hotel_info_dict['data_first']:
#             new_data_second(message, hotel_info_dict)
#         else:
#             hotel_info_dict['data_second'] = data_second
#             bot.send_message(message.from_user.id, f"Ищем отели")
#             find_hotel(message, hotel_info_dict)
#     except ValueError:
#         ver_data_second(message,hotel_info_dict)
#
# def new_data_second(message,hotel_info_dict):
#     bot.send_message(message.from_user.id, f"Дата заезда ментше даты выезда. Выберите другую дату выезда")
#     bot.register_next_step_handler(message, get_data_second, hotel_info_dict)
#
# def ver_data_second(message,hotel_info_dict):
#     bot.send_message(message.from_user.id, f"Нарушен формат даты")
#     bot.register_next_step_handler(message, get_data_second, hotel_info_dict)

def find_hotel(message,hotel_info_dict):
    '''def find_hotel - вывод информации на экран
    SEARCH - поиск ID города
    LIST - поиск информации (включая ID) по отелю в необходимом нам городе
    PHOTO - вывод фотографий отеля, использую ID отеля'''
#     url_search = "https://hotels4.p.rapidapi.com/locations/v2/search"
#     querystring_search = {"query": hotel_info_dict['city']}
#     headers = {
#         "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
#         "X-RapidAPI-Key": os.getenv('APIKEY')
#     }
#     try:
#         response_search = requests.get(url_search, headers=headers, params=querystring_search)
#         response_new_search = json.loads(response_search.text)
#         response_hotel_city_group = list(filter(lambda x: x['group'] == 'CITY_GROUP', response_new_search['suggestions']))
#         destination_Id_filter =list(filter(lambda city: city['type'] == 'CITY', response_hotel_city_group[0]['entities']))
#         new_destination_Id = [elem_city['destinationId']   for elem_city in destination_Id_filter if hotel_info_dict['city'][:3] in elem_city['caption'].replace(hotel_info_dict['city'][:3], '', 1) ]
#
#         url_list = "https://hotels4.p.rapidapi.com/properties/list"
#         querystring_list = {"destinationId": new_destination_Id[0], "pageNumber": "1", "pageSize": "25",
#                             "checkIn": "2020-01-08",
#                             "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
#         response_list = requests.get(url_list, headers=headers, params=querystring_list)
#         response_new_list = json.loads(response_list.text)
#         result_list = response_new_list['data']['body']['searchResults']['results']
#         result_sort = sorted(result_list, key=lambda price: price['ratePlan']['price']['current'], reverse=False)
#
#         url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
#         for x in range(hotel_info_dict['count_hotel']):
#             bot.send_message(message.from_user.id, f'''{x + 1}.Название отеля - {result_sort[x]['name']}
# Адрес - {result_sort[x]['address']['countryName']},{result_sort[x]['address']['streetAddress'] if  'streetAddress'  in  result_sort[x]['address']  else 'Нет названия улицы'}
# Расположение от центра  - {result_sort[x]['landmarks'][0]['distance']}
# Цена  за ночь - {result_sort[x]['ratePlan']['price']['current']}
# Цена за весь период {int(result_sort[x]['ratePlan']['price']['current'][1:]) * int((hotel_info_dict['data_second'] - hotel_info_dict['data_first']).days)}
# ''')
#             if hotel_info_dict['loading_photo'] == 'Да':
#                 bot.send_message(message.from_user.id, 'Фото отеля')
#                 photos_id_hotel = result_sort[x]['id']
#                 querystring = {"id": photos_id_hotel}
#                 response_photos = requests.get(url_photos, headers=headers, params=querystring)
#                 response__new_photos = json.loads(response_photos.text)
#                 photos = response__new_photos['hotelImages']
#                 for photo in range(hotel_info_dict['count_photo']):
#                     photo_url = photos[photo]['baseUrl']
#                     photo_for_user = photo_url.replace('{size}', 'z')
#                     bot.send_photo(message.from_user.id, photo_for_user)
#
#     except IndexError:
#         bot.send_message(message.from_user.id, "Что-то пошло не так, уточните название города")
#
# bot.polling(none_stop=True, interval=0)
