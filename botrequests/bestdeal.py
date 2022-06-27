import requests
import json
import os

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": os.getenv('APIKEY')
}


def min_price(destination_id, min_price):
    """
    def min_price - отфильтровываем список отелей по минимальной цене
    Если такой нет возвращаем пустой список для повторного запроса минимальной цены
    """
    url_list = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
    response_list = requests.get(url_list, headers=headers, params=querystring)
    response_new_list = json.loads(response_list.text)
    result_list = response_new_list['data']['body']['searchResults']['results']
    result_filter = list(filter(lambda price: int(price['ratePlan']['price']['current'][1:]) >= min_price, result_list))
    return result_filter


def max_price(list_filter, max_price):
    """
    def max_price - отфильтровываем список отелей по максимальной цене

    """
    result_filter = list(filter(lambda price: int(price['ratePlan']['price']['current'][1:]) <= max_price, list_filter))
    return result_filter

def min_distance(list_filter, min_distance):
    """
       def min_distance - отфильтровываем список отелей по минимальному расстоянию от центра
       Если такого нет возвращаем пустой список для повторного запроса минимального расстояния
       """
    result_filter = list(filter( lambda price: float(price ['landmarks'][0]['distance'].split()[0]) >=min_distance, list_filter))
    return result_filter

def max_distance(list_filter, max_distance):
    """
    def max_distance - отфильтровываем список отелей по максимальному расстоянию от центра

    """
    result_filter = list(filter( lambda price: float(price ['landmarks'][0]['distance'].split()[0]) <=max_distance, list_filter))
    return result_filter