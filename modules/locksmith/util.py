class UnknownCommandError(Exception):
    pass

def discover_commands():
    """
    Inspect commands.py and find all available commands
    """
    import inspect
    from locksmith import commands

    command_table = {}
    fns = inspect.getmembers(commands, inspect.isfunction)

    for name, fn in fns:
        if name.startswith("cmd_"):
            command_table.update({
                name.split("cmd_")[1]:fn
            })

    return command_table


def exec_command(command, *args, **kwargs):
    """
    Execute given command
    """
    commands = discover_commands()
    try:
        cmd_fn = commands[command]
    except KeyError:
        raise UnknownCommandError
    cmd_fn(*args,**kwargs)

def to_bool(val):
    """
    Return True/False based on string
    """
    if (isinstance(val, basestring) and bool(val)):
        return not val in ('False', 'false', '0', '0.0')

    return bool(val)
