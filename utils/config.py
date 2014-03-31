# not much to this place...
import json


def conf_get(file):
    js = open(file, "r+")
    data = json.load(js)
    return data

config = conf_get('config.json')
language = conf_get('languages/%s.json' % config['language'])
