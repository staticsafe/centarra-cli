"""
Another library for accessing the Centarra API... Because one wasn't enough.
"""

import requests
from libs import config

CENTARRA_BASE_URL = "https://billing.centarra.com"

def centarra(url, **kwargs):
    if kwargs == {}:
        r = requests.get(CENTARRA_BASE_URL + url,
            auth=(config['centarra_username'], config['centarra_api_key']))
    else:
        r = requests.post(CENTARRA_BASE_URL + url, data=kwargs,
            auth=(config['centarra_username'], config['centarra_api_key']))
    try:
        resp = r.json()
        return resp
    except:  # TODO vague, simplejson.decoder.JSONDecodeError
        #raise ValueError("JSON data was not returned by Centarra. Data recieved: %s" % r.text)
        raise ApiError(r.status_code)

class ApiError(Exception):
    def __init__(self, code):
        self.code = code

def flashed():
    flashes = requests.get(CENTARRA_BASE_URL + "/notifications.json",
                                 auth=(config['centarra_username'], config['centarra_api_key'])).json()
    if not flashes['messages']:
        return "No flashed response was given indicating the status of this request. Run `flashed' to see if a new response was given since."
    return '\n'.join(['[{}]: {}'.format(msg['type'], msg['message']) for msg in flashes['messages']])