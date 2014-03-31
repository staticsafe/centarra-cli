from utils import hook
from utils import HookFlags
from libs import substitutes, dump_subs

flags = HookFlags(m='multiword')

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
    substitutes[args[0]] = [' '.join(args[1:]), 'm' in flags]
    dump_subs()
    return ("{var} has been set to {x}{val}{x}".format(var=args[0], x="" if 'm' in flags else '"',
                                                     val=' '.join(args[1:])))

@hook.command('get', args_amt=1, return_json=False, doc=("Return the value of a variable, set automatically or by `set'",
                                                         "All vps nicknames and names are set automatically to their vps id.",
                                                         "\t`get <key>'"))
def get(args, flags):
    try:
        return ("The variable {var} is set to the value {x}{value}{x}. Set it with `set [-m] {var} <new_value>'"
                .format(var=args[0], value=substitutes[args[0]][0], x='' if substitutes[args[0]][1] else '"'))
    except KeyError:
        return "The variable {var} does not exist. Set it with `set [-m] {var} <new_value>'".format(var=args[0])
