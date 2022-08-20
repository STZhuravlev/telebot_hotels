from typing import Any, List

import botrequests.requests_api
from config_data import config
from log.loguru_log import *

headers = {
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
    "X-RapidAPI-Key": config.RAPID_API_KEY
}


@logger.catch()
def min_price(destination_id: int, min_price: int) -> Any:
    """
    def min_price - отфильтровываем список отелей по минимальной цене
    Если такой нет возвращаем пустой список для повторного запроса минимальной цены
    """
    url_list = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": destination_id, "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
                   "checkOut": "2020-01-15", "adults1": "1", "sortOrder": "PRICE"}
    response_new = botrequests.requests_api.request_to_api(url_list, headers, querystring)
    if not response_new:
        return None
    result_list = response_new['data']['body']['searchResults']['results']
    result_list = list(
        filter(lambda x: 'ratePlan' in x, result_list))  # исключаем из списка отсутствующие ключи ratePlan
    result_sorted = sorted(result_list, key=lambda price: int(
        price['ratePlan']['price']['current'][1:]))  # сортируем по цене для поиска самой низкой цены
    result_filter = list(
        filter(lambda price: int(price['ratePlan']['price']['current'][1:]) >= min_price, result_sorted))
    return result_filter


@logger.catch()
def max_price(list_filter: list, max_price: int) -> List:
    """
    def max_price - отфильтровываем список отелей по максимальной цене

    """
    result_filter = list(filter(lambda price: int(price['ratePlan']['price']['current'][1:]) <= max_price, list_filter))
    return result_filter


@logger.catch()
def min_distance(list_filter: list, min_distance: int) -> List:
    """
       def min_distance - отфильтровываем список отелей по минимальному расстоянию от центра
       Если такого нет возвращаем пустой список для повторного запроса минимального расстояния
       """
    result_filter = list(
        filter(lambda price: float(price['landmarks'][0]['distance'].split()[0]) > min_distance, list_filter))
    return result_filter


@logger.catch()
def max_distance(list_filter: list, max_distance: int) -> List:
    """
    def max_distance - отфильтровываем список отелей по максимальному расстоянию от центра

    """
    result_filter = list(
        filter(lambda price: float(price['landmarks'][0]['distance'].split()[0]) < max_distance, list_filter))
    return result_filter
