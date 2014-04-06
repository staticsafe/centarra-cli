from utils import hook, HookFlags, JsonResponse
from libs import centarra


@hook.command('profile password', args_amt=1, doc=("Change your password in the panel.",
                                                   "Usage:",
                                                   "\t`profile password <password>'",))
def password(args, flags):
    reply = centarra('/profile/password', newpass=args[0])
    return JsonResponse(reply, "Your password has been successfully changed.")


@hook.command('profile webhook-uri', args_amt=1,
              doc=("Change your webhook URI for job updates.",
                                                   "Usage:", "\t`profile webhook-uri <uri>'"))
def webhook_uri(args, flags):
    reply = centarra('/profile/webhook-uri', webhook_uri=args[0])
    return JsonResponse(reply, "Your webhook has been successfully changed.")


@hook.command('profile contact', args_amt=10,
              doc=("Change your contact information.",
                   "Usage:",
                   "\t`profile contact <email> <organization> <contact_name> <address1> " +
                   "<address2> <city> <state> <country> <phone> <zip>'"))
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


@hook.command("profile new-api-key", doc=("Generate a new API key on your account.",
                                          "This will likely make this cli unusable, since we need the new key to continue.",
                                          "Centarra does not supply us with the new key after this command, " +
                                          "so you will have to log in to receive the new key.",
                                          "Usage:",
                                          "\t`profile new-api-key'"))
def new_api_key(args, flags):
    reply = centarra('/profile/new-apikey')
    return JsonResponse(reply, "A new API key has been generated in your account.")

# It's silly to include the totp stuff in here, so I'm leaving it out.

flags = HookFlags(s='success', f='fail')

@hook.command("profile login-preferences", doc=("Change your login preferences, so you don't receive e-mails for certain log-in events.",
                                                    "Providing a flag means you want to receive e-mails for that event.",
                                                    "Flags:",
                                                    "\t -s, --success: Allow the panel to send e-mails when a user successfully logs in",
                                                    "\t -f, --fail: Allow the panel to send e-mails when a user attempts to log in, but fails",
                                                    "Usage:",
                                                    "\t`profile set-login-preferences [-st]'"))
def login_preferences(args, flags):
    preferences = {
        'fail': 1 if 'f' in flags else 0,
        'success': 1 if 's' in flags else 0
    }
    reply = centarra('/profile/login-preferences', **preferences)
    return JsonResponse(reply, "Your login preferences have been updated: " +
                               ', '.join(["%s log-in events: %s" % (a, bool(preferences[a])) for a in preferences]))
