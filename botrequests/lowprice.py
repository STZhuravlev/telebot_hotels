import requests
import json
import os
import random

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": os.getenv('APIKEY')
}


def city_id(name_city):
    '''def city_id - получаем id города, в котором будем искать отели'''
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": name_city}
    response = requests.get(url, headers=headers, params=querystring)
    response_new = json.loads(response.text)
    response_hotel_city_group = list(filter(lambda x: x['group'] == 'CITY_GROUP', response_new['suggestions']))
    destination_Id_filter = list(filter(lambda city: city['type'] == 'CITY', response_hotel_city_group[0]['entities']))
    if not destination_Id_filter:
        return None
    else:
        for elem_city in destination_Id_filter:
            my_city = elem_city['caption'].replace(name_city[0:3], '', 1)
            if name_city[0:3] in my_city:
                return elem_city['destinationId'], elem_city['name']


def hotel_info(destinationId, num):
    '''def hotel_info - получаем информацию по отелям'''
    url_list = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destinationId, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
    response_list = requests.get(url_list, headers=headers, params=querystring)
    response_new_list = json.loads(response_list.text)
    result_list = response_new_list['data']['body']['searchResults']['results']
    result_sort = sorted(result_list, key=lambda price: price['ratePlan']['price']['current'], reverse=False)
    return result_sort[:num]


def hotel_photo(photos_id_hotel, num):
    ''' def hotel_photo -  получаем фотографии отеля'''
    url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": photos_id_hotel}
    response_photos = requests.get(url_photos, headers=headers, params=querystring)
    response__new_photos = json.loads(response_photos.text)
    photos = response__new_photos['hotelImages']
    random.shuffle(photos)
    return photos[:num]
