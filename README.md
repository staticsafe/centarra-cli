## Centarra-cli

As a new way to access your [Centarra](http://billing.centarra.com) account, *Centarra-cli* is a flexible and extensible new CLI made to gracefully combine user input with simply-defined commands.

### Installation

Currently, you can grab a clone of this repository as it goes, and run the cli.py file out-of-the box - however, you will need to have the `requests` module installed.

This can be done easily with the PIP Python package manager:

```bash
sudo pip install requests
```

We'll make this optional at some point

### Usage

The `help` command holds all the defined documentation in the program, and the flag system should be reminicent of your familiar shell.

For a refresher:

 - "quoted text" is counted as one argument
 - flags are specified using `-l` or `--long-version`, and multiple flags can be chained on a single-dashed 'short' flag: `-helo` is equivelent to `-h -e -l -o`
 - Parametered flags grab the next parameter they can find: `-h value` takes `value` to `-h`, while `-hi v1 v2` takes `v1` to `-h` and `v2` to `-i`

`help` on its own will display all available commands, and a brief idea of what they do. Coming soon: `help --regex billing.+` (or wildcards)

`help <command>` will display all help for the command you have specified. This is closest to a manual page - it should provide all information about flags accepted, parameters expected, and what the command will do.

Flags can be in any order, but their arguments can not, and all command arguments must be in order (unless specified otherwise)

### Contributing

A sample command and explanation can be found in `/commands/\_\_init\_\_.py`, for help in creating your own commands.

