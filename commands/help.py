from utils.config import language
from utils import hook, HookFlags

from re import compile

flags = HookFlags(r=('regex', True))
@hook.command('help', args_amt=lambda x: 0 <= len(x) <= 2, flags=flags, return_json=False, doc=("Fetch information regarding a certain command",
                                                                                                "`help' will, without any arguments, list all commands and a brief idea of what they do.",
                                                                                                "Once supplied with a command, `help' will return all documentation regarding that command. Any command listed in `help' will return documentation"
                                                                                                "Flags: (only when no command is supplied)",
                                                                                                "\t-r, --regex <regex>: filter results by a provided regular expression.",
                                                                                                "Usage:",
                                                                                                "\t`help [-r <regex>|<my command>]'"))
def help(args, flags):
    # this returns the string we want to print out as help.
    command = ' '.join(args)
    if not command or command == []:
        rply = ""
        rg = None
        if 'r' in flags:
            rg = compile(flags['r'])
        for cmd in sorted(hook.commands):
            if rg is None or rg.search(cmd):
                rply += "`%s': %s\r\n" % (cmd, hook.commands[cmd]['doc'][0])
        return rply
    if command in hook.commands:
        return '\r\n' + ('\r\n'.join(hook.commands[command]['doc'])) + '\r\n'
    return language['help']['command_not_found']
