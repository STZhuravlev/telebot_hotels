from telebot import types
from loader import bot

def get_count_hotel(message):
    """
    def get_count_hotel - получаем количество отелей, которое выведем на экран пользователю
    Для этого используем кнопки
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='1', callback_data=1))
    markup.add(types.InlineKeyboardButton(text='2', callback_data=2))
    markup.add(types.InlineKeyboardButton(text='3', callback_data=3))
    markup.add(types.InlineKeyboardButton(text='4', callback_data=4))
    markup.add(types.InlineKeyboardButton(text='5', callback_data=5))
    bot.send_message(message.chat.id, text="Какое количество отелей вывести на экран?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['1', '2', '3', '4', '5'])
def query_handler(call):
    answer = ''
    if call.data == '1':
        answer = '1 отель'
        user_dict[call.message.chat.id].count_hotel = 1
    elif call.data == '2':
        answer = '2 отеля'
        user_dict[call.message.chat.id].count_hotel = 2
    elif call.data == '3':
        answer = '3 отеля'
        user_dict[call.message.chat.id].count_hotel = 3
    elif call.data == '4':
        answer = '4 отеля'
        user_dict[call.message.chat.id].count_hotel = 4
    elif call.data == '5':
        answer = '5 отелей'
        user_dict[call.message.chat.id].count_hotel = 5
    bot.send_message(call.message.chat.id, f'Вы выбрали {answer}')
    get_loading_photo(call.message)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)  # убирает кнопки