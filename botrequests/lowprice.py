import random
import re

import botrequests.requests_api
from config_data import config
from log.loguru_log import *

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": config.RAPID_API_KEY
}

@logger.catch()
def get_city(name_city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": name_city}
    response_new = botrequests.requests_api.request_to_api(url, headers, querystring)
    cities = list()
    for city in response_new['suggestions'][0]['entities']:
        clear_destination = ', '.join((city['name'], re.findall('(\\w+)[\n<]', city['caption'] + '\n')[-1]))
        cities.append({'city_name': clear_destination, 'destination_id': city['destinationId']})
    return cities

@logger.catch()
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
    result_list = list(filter(lambda x: 'ratePlan' in x, result_list))
    result_sort = sorted(result_list, key=lambda price: int(price['ratePlan']['price']['current'][1:]), reverse=rev)
    return result_sort[:num]

@logger.catch()
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
