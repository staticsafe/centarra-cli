from utils.config import language
from utils import hook, HookFlags

from re import compile

flags = HookFlags(r=('regex', True))
@hook.command('help', args_amt=lambda x: 0 <= len(x) <= 2, flags=flags, return_json=False)
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
        return '\r\n'.join(hook.commands[command]['doc'])
    return language['help']['command_not_found']
