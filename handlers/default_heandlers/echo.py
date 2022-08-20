from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def helper(message: Message) -> None:
    """
    def helper - вызывает команду для помощи в управление командами бота
    """
    bot.send_message(message.from_user.id, "Для перехода в меню нажмите /help.")


