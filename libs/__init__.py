import json
import time
import os
import sys

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME + '/.config/centasdgfasdfi/')
HISTORY_FILE = os.path.join(CONFIG_DIR, '.cli_history')
SUBSTITUTES_FILE = os.path.join(CONFIG_DIR, 'substitutes.json')
USER_SUBSTITUTES_FILE = os.path.join(CONFIG_DIR, 'user_substitutes.json')
CONFIGURATION_FILE = os.path.join(CONFIG_DIR, 'config.json')
LANGUAGE_FILE = 'languages/%s.json'

if not os.path.exists(CONFIG_DIR):
    try:
        os.makedirs(CONFIG_DIR)
    except os.error:
        print("Configuration directory {} could not be created or written to.".format(CONFIG_DIR))
        sys.exit(2)
if not os.path.exists(HISTORY_FILE):
    open(HISTORY_FILE, 'w+').close()
if not os.path.exists(SUBSTITUTES_FILE):
    with open(SUBSTITUTES_FILE, 'w+') as out:
        json.dump({}, out)
if not os.path.exists(USER_SUBSTITUTES_FILE):
    with open(USER_SUBSTITUTES_FILE, 'w+') as out:
        json.dump({}, out)
if not os.path.exists(CONFIGURATION_FILE):
    print("Welcome to Centarra-CLI, for accessing Centarra's comfortable management panel from the comfort of your shell.")
    print("First, we're going to need to get some configuration over with.")
    #if not 'y' == raw_input("Do you have a Centarra account? [y/N]"):
        # POST /create with arguments username, password, email. error argument is the error in the form.
    configuration = {"centarra_username": raw_input("Enter your Centarra username: "),
                     "centarra_api_key": raw_input("Enter your Centarra API key, from http://billing.centarra.com/profile/index : "),
                     "language": "en_US",
                     "debug_mode": False}
    with open(CONFIGURATION_FILE, 'w') as out:
        json.dump(configuration, out)

class Sub():

    def __init__(self, f):
        self.f = f
        js = open(f, "r+")
        self.data = json.load(js)

    def dump_subs(self):
        with open(self.f, 'w') as out:
            json.dump(self.data, out)

class UserSubstitutions(Sub):

    def fetch(self, key):
        return self.data.get(key, None)

    def sub(self, var, val, multiword=False):
        if not var in self.data:
            self.data[var] = {"value": val, "multiword": multiword}
            self.dump_subs()

class Substitutions(Sub):

    def swap(self, type_, key, intended=int):
        #if intended and type(key) is intended:
        #    return key
        key = str(key).lower()
        res = self.data.get(type_, {}).get(key, {}).get("value", False)
        if not res:
            res = self.loop(type_, key + " ")  # Prefer it with a space afterwards. this prevents against 512 => 5120 mb
        if not res:
            res = self.loop(type_, key)
        if not res:
            return key
        return res

    def loop(self, type_, key):
        for check in self.data.get(type_, {}):
            dc = self.data.get(type_, {})[check]
            if key in str(check):
                return dc['value']

    def sub(self, type_, var, val):
        if not type_ in self.data:
            self.data[type_] = {}
        self.data[type_][str(var).lower()] = {"value": val, "expiry": time.time() + (60 * 60 * 24)}
        self.dump_subs()

substitutes = Substitutions(SUBSTITUTES_FILE)
user_substitutes = UserSubstitutions(USER_SUBSTITUTES_FILE)


def conf_get(file):
    js = open(file, "r+")
    data = json.load(js)
    return data

config = conf_get(CONFIGURATION_FILE)
language = conf_get(LANGUAGE_FILE % config['language'])

from libs.api import centarra, flashed