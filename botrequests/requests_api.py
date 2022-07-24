import requests
import json


def request_to_api(url, headers, querystring):
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        if response.status_code == requests.codes.ok:
            response_new = json.loads(response.text)
            return response_new
    except ValueError:
        pass
