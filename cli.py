#!/usr/bin/python

import commands

import os
import json

if not os.path.exists('languages/.cli_history'):
    open('languages/.cli_history', 'a').close()
if not os.path.exists('libs/substitutes.json'):
    with open('libs/substitutes.json', 'w+') as out:
        json.dump({}, out)

from utils import hook
import sys
from utils import config

def completer(text, state):
    options = [i for i in hook.commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

def shell():
    import readline

    print("Welcome to the Centarra-CLI, for managing your account via a clean command-line interface.\r\n")
    print("See the `help' command for help on commands available here!\r\n")

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    try:
        readline.read_history_file("languages/.cli_history")
    except:
        pass

    try:
        while True:
            line = raw_input('>>> ')
            print(hook.dispatch(line))
    except KeyboardInterrupt:
        readline.write_history_file('languages/.cli_history')
        print("\r\nExiting program")
    except EOFError:
        readline.write_history_file('languages/.cli_history')
        print("\r\nExiting program")

def main():
    if len(sys.argv) < 2:
        shell()
    elif sys.argv[1] == "-":
      for line in sys.stdin.readlines():
        print(hook.dispatch(line))
    else:
        line = ' '.join(sys.argv[1:])
        print(hook.dispatch(line))

if __name__ == '__main__':
    main()
