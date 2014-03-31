from libs.api import centarra
from utils.config import conf_get
import json

vps = centarra('/vps/list')
substitutes = {}

for i in vps['vpslist']:
    substitutes[i['name']] = [str(i['id']), False]
    substitutes[i['nickname']] = [str(i['id']), False]

substitutes = dict(substitutes.items() + conf_get('libs/substitutes.json').items())


def dump_subs():
    with open('libs/substitutes.json', 'w') as out:
        json.dump(substitutes, out)
