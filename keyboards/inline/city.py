from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_city(cities):
    """
    def kb_city - клавиатура для вывода городов по запросу пользователя
    """
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'{city["destination_id"]}'))
    return destinations