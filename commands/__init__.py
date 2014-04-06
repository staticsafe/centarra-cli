"""
Commands for centarra-cli

We register our commands as:

from util import hook, HookFlags, JsonResponse, CommandError

flags = HookFlags(a=('long-flag', True), b=('longer-flag', False)) # Passing True means it accepts a parameter.

# both parts of the tuple are optional - accepting a param is default false, and no long mode means there is none.
# it doesn't even have to be a list - a='my-flag' is fine if it doesn't accept a parameter.

@hook.command('first_command', flags=flags, return_json=True,
    doc='Stick your documentation in here. This is what will show up in your help command.')
        # flags is HookFlags object, return_json is if we receive data we can throw at the user.
def first_command(args, flags):  # flags is passed as a Flags object. args is a list as parameters, in order, sep by " "
    # you can access anything in the util section and access the api, but we do want to allow the option to return json
    # so, we have a choice of what we want to return
    return JsonResponse(raw_json="{}", reply="Your text you want to respond with - use the raw json as much as you can")
    # or
    return "Just a boring old string. Was your query successful?"  # --json will not work with this.

    # we'll make sure to handle authentication errors outside, but in case you hit your own error:
    return CommandError('color?', 'Your Error, how to fix it.')
"""

from commands.profile import *
from commands.vps import *
from commands.help import *
from commands.builtin import *
from commands.dns import *
