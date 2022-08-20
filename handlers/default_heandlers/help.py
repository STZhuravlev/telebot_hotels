from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message) -> None:
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.send_message(message.from_user.id, '\n'.join(text))

@bot.message_handler(state=None)
def helper(message: Message) -> None:
    """
    def helper - вызывает команду для помощи в управление командами бота
    """
    bot.send_message(message.from_user.id, "Для перехода в меню нажмите /help.")
