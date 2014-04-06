## Centarra-cli

As a new way to access your [Centarra](http://billing.centarra.com) account, *Centarra-cli* is a flexible and extensible new CLI made to gracefully combine user input with simply-defined commands.

### Installation

Currently, you can grab a clone of this repository as it goes, and run the cli.py file out-of-the box - however, you will need to have the `requests` module installed.

This can be done easily with the PIP Python package manager:

```bash
sudo pip install requests
```

We'll make this optional at some point.

You're also going to need to rename `config.sample.json` to `config.json` before running the program, in order to provide the CLI with the information it needs to work properly.

### Usage

The `help` command holds all the defined documentation in the program, and the flag system should be reminicent of your familiar shell.

For a refresher:

 - "quoted text" is counted as one argument
 - flags are specified using `-l` or `--long-version`, and multiple flags can be chained on a single-dashed 'short' flag: `-helo` is equivelent to `-h -e -l -o`
 - Parametered flags grab the next parameter they can find: `-h value` takes `value` to `-h`, while `-hi v1 v2` takes `v1` to `-h` and `v2` to `-i`

`help` on its own will display all available commands, and a brief idea of what they do. Also available: `help --regex billing` (or `-r`)

`help <command>` will display all help for the command you have specified. This is closest to a manual page - it should provide all information about flags accepted, parameters expected, and what the command will do.

Flags can be in any order, but their arguments can not, and all command arguments must be in order (unless specified otherwise)

### Contributing

A sample command and explanation can be found in `/commands/__init__.py`, for help in creating your own commands.

Documentation lies ahead:

#### Hook

The hook is a decorator you need to apply to every command to make it... "work".

```python
from utils import hook

@hook.command(...)
```

This hook takes five arguments:

 - command (**required**): A two-word command that is entered straight into the command line as the command. string, example: "billing list", "vps list", "hello world".
  - These must be two words unless they are specified as a builtin, which is now hardcoded in line 103 of `utils/handler.py`.
```python
@hook.command("my command", ...)
```
 - flags: (optional, empty `HookFlags()` object if unspecified) A HookFlags (in utils module, `from utils import HookFlag`) object that holds all the flags that this command can accept.
  - HookFlags takes a list of arguments in the form of `HookFlags(s=('longname', True|False), ...)`. `s` is the short flag name, 'longname' is the long flag name (`--longname` or `-s`), and the boolean value is if the command should accept an argument or not.
  - The tuple is not required if only one part is needed - so `s='longname'` is valid, as is `s=True`. By default, flags don't accept parameters.
```python
@hook.command("my command", flags=HookFlags(r=("reset", False))) # -r or --reset, doesn't take an argument
@hook.command("my command", flags=HookFlags(h=("hello", True)))  # -h or --hello, takes an argument
@hook.command("my command", flags=HookFlags(b="balloon", c=True, y=("yes", True)))
# ^ chain arguments. -b is --balloon, takes no args. -c, takes an arg. -y or --yes, takes an arg.
@hook.command("my command")  # accepts no flags
```
 - args_amt (optional, 0 if unspecified) args_amt dictates how many arguments can be passed to a function. This can either be an integer, or a lambda that accepts all the parameters of the function and returns True/False.
```python
@hook.command("my command", args_amt=2)  # accept two arguments
@hook.command("my command", args_amt=lambda x: 2 > len(x))  # less than two arguments
@hook.command("my command")  # accepts zero arguments, not counting flags.
```
 - return_json (optional, True if unspecified) boolean, if this function will return a JsonResponse as its response - to enable the `--json` flag
```python
@hook.command("my command", return_json=True) # must return a json object
@hook.command("my command")  # must return a json object
@hook.command("my command", return_json=False)  # doesn't have to return a json object
```
 - doc ('no_documentation' language value in a tuple if unspecified) - a tuple that holds all of the documentation for a command. The first line should be a short synopsis, and the rest should be a full man-page. Examples and flags should be preceeded by \t, and examples or references to other commands should be surrounded by \`cmd' - to keep consistant.
```python
@hook.command("my command", 
    doc=("short sum", "\t-h, --hello: throws you under a bus", "\t`my command [-h]'"))
```

#### Function definition

After the decorator, we define a function to handle the command logic.

```python
def myFunction(args, flags):
```

We accept two arguments: args and flags.

 - args holds a list of arguments, already split by space or quotes, without the flag arguments.
 - flags holds a dict of {'shortflag' => 'value'} - where 'value' is True if the flag didn't need an argument.


#### Function Logic and Return Value

The `centarra` function allows you to access the panel API:

```python

from libs import centarra
from utils import JsonResponse

json_response = centarra('/uri/for/request', a="arguments", f="for posting")

return JsonResponse(json_response, "My nicely formatted string with the json_response information.")
```

A JsonResponse will handle the json accordingly if the `--json` flag was used. Otherwise the string will be returned.

If we don't return a JsonResponse, we can return something else simply by returning a String - but this will override --json if it is provided.

#### Other cool stuff

We can set parameters by editing the dict `substitutes` in `libs`:

```python
from libs import substitutes, dump_subs
substitutes = {'key': ['value', False]} # boolean is if_multiline
dump_subs()  # update to file.
```

This allows us to set aliases, like vps names set to point to vps ids - so accessing them is easy with stuff like $nasonfish-0 or even nicknames, $n.

Make sure not to overwrite their preferences, though - those persist through reboot.
