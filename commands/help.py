from utils.config import language
from utils import hook, HookFlags

from re import compile

flags = HookFlags(r=('regex', True), l='long')
@hook.command('help', args_amt=lambda x: 0 <= len(x) <= 2, flags=flags, return_json=False, doc=("Fetch information regarding a certain command",
                                                                                                "`help' will, without any arguments, list all commands and a brief idea of what they do.",
                                                                                                "Once supplied with a command, `help' will return all documentation regarding that command. Any command listed in `help' will return documentation"
                                                                                                "Flags: (only when no command is supplied)",
                                                                                                "\t-r, --regex <regex>: filter results by a provided regular expression.",
                                                                                                "\t-l, --long: explicitly show the entire man-page for all matching commands.",
                                                                                                "Usage:",
                                                                                                "\t`help [-l] [-r <regex>|<my command>]'"))
def help(args, flags):
    # this returns the string we want to print out as help.
    command = ' '.join(args)
    reply = ""
    if not command:
        rg = None
        if 'r' in flags:
            rg = compile(flags['r'])
        for cmd in sorted(hook.commands):
            if rg is None or rg.search(cmd):
                reply += _help_append(cmd, hook.commands[cmd], 'l' in flags)
        return reply
    if hook.commands.get(command, False):
        return _help_append(command, hook.commands[command], True)
    for c in hook.commands:
        if command in c:
            reply += _help_append(c, hook.commands[c], 'l' in flags)
    return reply or language['help']['command_not_found']

def _help_append(name, command, long):
    if not long:
        return "`%s': %s\r\n" % (name, command['doc'][0])
    else:
        return name + ':\r\n' + ('\r\n'.join(command['doc'])) + '\r\n---\r\n'
