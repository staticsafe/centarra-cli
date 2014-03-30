from utils import hook, HookFlags, JsonResponse
from libs import centarra



@hook.command('profile password', args_amt=1, flags=HookFlags(), return_json=True, doc='')
def first_command(args, flags):
    reply = centarra('/profile/password', newpass=args[0])
    return JsonResponse(reply, "Your password has been successfully changed.")
