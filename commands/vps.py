from utils import hook, HookFlags, JsonResponse
from libs import centarra

@hook.command('vps list', flags=HookFlags(), return_json=True, doc='')
def first_command(args, flags):
    reply = centarra('/vps/list')
    return JsonResponse(reply, "Your current vps' are: and then, you know, arguments.")
