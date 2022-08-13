import os

from dotenv import find_dotenv, load_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')
RAPID_API_KEY = os.getenv('APIKEY')
DEFAULT_COMMANDS = (
    ('lowprice', "Узнать топ самых дешёвых отелей в городе"),
    ('highprice', "Узнать топ самых дорогих отелей в городе"),
    ('bestdeal',
     "Узнать топ отелей, наиболее подходящих по цене и расположению от центра (самые дешёвые и находятся ближе всего к центру)"),
    ('history', "Узнать историю поиска отелей"),
)
