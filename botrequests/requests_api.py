import requests
import json
from log.loguru_log import *


@logger.catch()
def request_to_api(url, headers, querystring):
    response = requests.get(url, headers=headers, params=querystring, timeout=15)
    if response.status_code == requests.codes.ok:
        response_new = json.loads(response.text)
        return response_new
