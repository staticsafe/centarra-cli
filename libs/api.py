"""
Another library for accessing the Centarra API... Because one wasn't enough.
"""

import requests
from utils import config

CENTARRA_BASE_URL = "https://billing.centarra.com"

def centarra(url, **kwargs):
    if kwargs == {}:
        m = requests.get
    else:
        m = requests.post
    r = m(CENTARRA_BASE_URL + url, params=kwargs,
        auth=(config['centarra_username'], config['centarra_api_key']))
    return r.json()
