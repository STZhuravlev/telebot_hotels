from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def kb_count_hotel():
    """
    def kb_count_hotel - клавиатура для получения количества выводимых отелей на экран
    """
    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(InlineKeyboardButton(text='1', callback_data=1), InlineKeyboardButton(text='2', callback_data=2),
               InlineKeyboardButton(text='3', callback_data=3),InlineKeyboardButton(text='4', callback_data=4),
               InlineKeyboardButton(text='5', callback_data=5))

    return markup


