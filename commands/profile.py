from utils import hook, HookFlags, JsonResponse
from libs import centarra

@hook.command('profile password', args_amt=1, doc=('Change your password in the panel. profile password <password>',))
def password(args, flags):
    reply = centarra('/profile/password', newpass=args[0])
    return JsonResponse(reply, "Your password has been successfully changed.")

@hook.command('profile webhook-uri', args_amt=1,
              doc=("Change your webhook URI for job updates. profile webhook-uri <uri>",))
def webhook_uri(args, flags):
    reply = centarra('/profile/webhook-uri', webhook_uri=args[0])
    return JsonResponse(reply, "Your webhook has been successfully changed.")

@hook.command('profile contact', args_amt=10,
              doc=("Change your contact information.",
                   "profile contact <email> <organization> <contact_name> <address1> " +
                   "<address2> <city> <state> <country> <phone> <zip>"))
def profile_contact(args, flags):
    args = {
        'new_email': args[0],
        'organization': args[1],
        'contact_name': args[2],
        'address1': args[3],
        'address2': args[4],
        'city': args[5],
        'state': args[6],
        'country': args[7],
        'phone': args[8],
        'zip': args[9]
    }
    reply = centarra('/profile/email', **args)
    rsp = ""
    for i in args:
        rsp += "%s=%s, " % (i, args[i])
    return JsonResponse(reply, "Your contact information has been updated (%s)" % rsp[:-2])


#@hook.command('profile new-api-key')
#def new_api_key