import commands
from utils import hook
import sys
from utils import config

print("Welcome to the Centarra-CLI, for managing your account via a clean command-line interface.\r\n")
print("See the `help' command for help on commands available here!\r\n")

if not config['centarra_username']:
    print('Please enter in your Centarra username and api-key before continuing')
    sys.exit(0)

while True:
    line = raw_input('>>>')
    print(hook.dispatch(line))
