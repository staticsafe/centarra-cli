"""
Another library for accessing the Centarra API... Because one wasn't enough.
"""

import requests
from utils.config import config

CENTARRA_BASE_URL = "https://billing.centarra.com"

def centarra(url, **kwargs):
    if kwargs == {}:
        r = requests.get(CENTARRA_BASE_URL + url,
            auth=(config['centarra_username'], config['centarra_api_key']))
    else:
        r = requests.post(CENTARRA_BASE_URL + url, data=kwargs,
            auth=(config['centarra_username'], config['centarra_api_key']))
    try:
        return r.json()
    except:  # TODO vague, simplejson.decoder.JSONDecodeError
        #raise ValueError("JSON data was not returned by Centarra. Data recieved: %s" % r.text)
        raise ApiError(r.status_code)

class ApiError(Exception):
    def __init__(self, code):
        self.code = code
