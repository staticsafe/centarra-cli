from utils import hook, HookFlags, JsonResponse
from libs import user_substitutes
from libs.api import flashed

flags = HookFlags(m='multiword')

# TODO infinite loops... they can happen if you're just that commited to screwing everything up!

@hook.command('set', flags=flags, args_amt=lambda x: 2 >= len(x), return_json=False, doc=("Set a variable for substitution in commands",
                                                         "Setting a variable will replace all parameters prefixed with `$' with the variable previously set",
                                                         "These variables will persist through restarts, and can be edited in the `/libs/substitutes.json` file",
                                                         "Flags:",
                                                         "\t-m, --multiword: Allow set commands to cover more than one parameter/flag - it will be" +
                                                         "interpreted as if it were entered into the command raw, instead of in quotes.",
                                                         "-m Allows you to cover certain parameter flags with a set variable.",
                                                         "Also, VPS names and nicknames are set automatically to their id.",
                                                         "\t`set <key> <value ...>', with any length value."))
def set(args, flags):
    user_substitutes.sub(args[0], ' '.join(args[1:]), 'm' in flags)
    user_substitutes.dump_subs()
    return ("{var} has been set to {x}{val}{x}".format(var=args[0], x="" if 'm' in flags else '"',
                                                     val=' '.join(args[1:])))

@hook.command('get', args_amt=1, return_json=False, doc=("Return the value of a variable, set automatically or by `set'",
                                                         "All vps nicknames and names are set automatically to their vps id.",
                                                         "\t`get <key>'"))
def get(args, flags):
    arg = user_substitutes.fetch(args[0])
    if not arg:
        return "The variable {var} does not exist. Set it with `set [-m] {var} <new_value>'".format(var=args[0])
    return ("The variable {var} is set to the value {x}{value}{x}. Set it with `set [-m] {var} <new_value>'"
            .format(var=args[0], value=arg['value'], x='' if arg['multiword'] else '"'))



@hook.command("delete", args_amt=1, return_json=False, doc=("Delete a variable's link to its value.",
                                                            "These variables, set with `set', are removed from the program completely once you delete them.",
                                                            "However, keep in mind variables set by certain commands  will be re-set if the command is called again.",
                                                            "Usage:",
                                                            "\t`delete <variable>'"))
def delete_var(args, flags):
    if args[0] in user_substitutes.data:
        v = user_substitutes.data[args[0]]
        del(user_substitutes.data[args[0]])
        user_substitutes.dump_subs()
        return "The variable {var}, set to {value}, has been deleted and will no longer substitute into commands.\n" + \
               "Set the variable again with `set {var} <new value>'".format(var=args[0], value=v)
    return "No variable could be found with that name {name}.".format(name=args[0])

# TODO maybe a flag to make the command not substitute variables would be cool?

@hook.command("exit", doc=("Exit the CLI.",))
def exit(args, flags):
    import sys
    print("Exiting Centarra-CLI.")
    sys.exit(0)

@hook.command("flashed", return_json=False, doc=("Display 'flashed' messages sent with the last request",
                              "Flashed messages usually indicate the status of the last request, and are presented to the panel as notifications in the corner."))
def get_flashed(args, flags):
    return flashed()
