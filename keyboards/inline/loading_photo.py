from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_loading_photo() -> InlineKeyboardMarkup:
    """
    def kb_count_hotel - клавиатура для вывода фотографий на экран
    """
    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(InlineKeyboardButton(text='Да', callback_data='Да'),
               InlineKeyboardButton(text='Нет', callback_data='Нет'))

    return markup
