from libs.api import centarra
from utils.config import conf_get
import json

substitutes = conf_get('libs/substitutes.json')


def dump_subs():
    with open('libs/substitutes.json', 'w') as out:
        json.dump(substitutes, out)
