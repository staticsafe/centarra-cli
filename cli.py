#!/usr/bin/python

import commands
from utils import hook
import sys
from utils import config

print("Welcome to the Centarra-CLI, for managing your account via a clean command-line interface.\r\n")
print("See the `help' command for help on commands available here!\r\n")

if not config['centarra_username']:
    print('Please enter in your Centarra username and api-key before continuing')
    sys.exit(0)

import readline

def completer(text, state):
    options = [i for i in hook.commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

readline.parse_and_bind("tab: complete")
readline.set_completer(completer)

try:
    while True:
        line = raw_input('>>> ')
        print(hook.dispatch(line))
except KeyboardInterrupt:
    print("\r\nExiting program")
except EOFError:
    print("\r\nExiting program")
