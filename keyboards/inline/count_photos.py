from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_count_photos():
    """
    def kb_count_photos - клавиатура для получения количества выводимых фотографий на экран
    """
    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(InlineKeyboardButton(text='1', callback_data='1photo'), InlineKeyboardButton(text='2', callback_data='2photo'),
               InlineKeyboardButton(text='3', callback_data='3photo'),InlineKeyboardButton(text='4', callback_data='4photo'),
               InlineKeyboardButton(text='5', callback_data='5photo'))

    return markup