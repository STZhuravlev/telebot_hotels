# import os
import random
import botrequests.requests_api
from config_data import config

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": config.RAPID_API_KEY
}

# print(os.getenv('APIKEY'))
# print(config.RAPID_API_KEY)


def city_id(name_city):
    """
    def city_id - получаем id города, в котором будем искать отели
    """

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": name_city}
    response_new = botrequests.requests_api.request_to_api(url, headers, querystring)
    if not response_new:
        return None, None
    response_hotel_city_group = list(filter(lambda x: x['group'] == 'CITY_GROUP', response_new['suggestions']))
    destination_id_filter = list(filter(lambda city: city['type'] == 'CITY', response_hotel_city_group[0]['entities']))
    if not destination_id_filter:
        return None, None
    else:
        for elem_city in destination_id_filter:
            my_city = elem_city['caption'].replace(name_city[0:3], '', 1)
            if name_city[0:3] in my_city:
                return elem_city['destinationId'], elem_city['name']


def hotel_info(destination_id, num, command):
    """
    def hotel_info - получаем информацию по отелям
    """
    if command == '/highprice':
        rev = True
    else:
        rev = False
    url_list = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
    response_new = botrequests.requests_api.request_to_api(url_list, headers, querystring)
    if not response_new:
        return None
    result_list = response_new['data']['body']['searchResults']['results']
    result_sort = sorted(result_list, key=lambda price: int(price['ratePlan']['price']['current'][1:]), reverse=rev)
    return result_sort[:num]


def hotel_photo(photos_id_hotel, num):
    """
    def hotel_photo -  получаем фотографии отеля
    """
    url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": photos_id_hotel}
    response_new = botrequests.requests_api.request_to_api(url_photos, headers, querystring)
    if not response_new:
        return None
    photos = response_new['hotelImages']
    random.shuffle(photos)
    return photos[:num]
