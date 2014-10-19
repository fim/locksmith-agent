import os
import inspect
from datetime import datetime
from argparse import ArgumentParser

from locksmith.lock import *
from locksmith.log import logger

class CommandlineArgumentError(Exception):
    pass

class CommandError(Exception):
    pass

def cmd_list(conf, argv):
    """
    List all existing build environments
    """
    usage = "%(prog)s [options] list [list_options]"
    description = inspect.getdoc(cmd_list)
    parser = ArgumentParser(
        usage = usage,
        description = description)
    args = parser.parse_args(argv)

    try:
        try:
            lrpc = LockRPC(**conf)
        except TypeError:
            raise CommandError("Config file is missing or is invalid. Try re-registering your client")
        for l in lrpc.list():
            print l['stub']
    except ListException,e:
        raise CommandError("Couldn't list locks for user %s: %s" % (conf['username'], e))


def cmd_lock(conf, argv):
    """
    Acquire a lock from the server
    """
    usage = "%(prog)s [options] lock [lock_options] lock_name"
    description = inspect.getdoc(cmd_lock)
    parser = ArgumentParser(
        usage = usage,
        description = description)
    parser.add_argument("-s", "--silent", action="store_true",
            default=False, help="Fail silently on error",)
    parser.add_argument("-x", "--exclusive", action="store_true",
            default=False, help="Acquire exclusive lock",)
    parser.add_argument("lock", help="lock name",)
    args = parser.parse_args(argv)


    try:
        lrpc = LockRPC(**conf)
        lrpc.lock(args.lock, args.exclusive)
    except TypeError:
        raise CommandError("Config file is missing or is invalid. Try re-registering your client")
    except LockException,e:
        if args.silent:
            return

        raise CommandError("Couldn't acquire lock %s: %s" % (args.lock, e))

def cmd_unlock(conf, argv):
    """
    Create new build environments
    """
    description = inspect.getdoc(cmd_unlock)
    usage = "%(prog)s [options] unlock [unlock_options] lock_name"
    parser = ArgumentParser(
        usage = usage,
        description = description)
    parser.add_argument("-s", "--silent", action="store_true",
            default=False, help="Fail silently on error",)
    parser.add_argument("lock", help="lock name",)
    args = parser.parse_args(argv)


    try:
        lrpc = LockRPC(**conf)
        lrpc.unlock(args.lock)
    except TypeError:
        raise CommandError("Config file is missing or is invalid. Try re-registering your client")
    except UnlockException,e:
        if args.silent:
            return

        raise CommandError("Couldn't release lock %s: %s" % (args.lock, e))


def cmd_register(conf, argv):
    """
    Register with the lock server
    """
    usage = "%(prog)s [options] register [register_options]"
    description = inspect.getdoc(cmd_register)
    parser = ArgumentParser(
        usage=usage,
        description = "Automatically register with the lock server and " \
        "initialize the config file")
    parser.add_argument("server", help="server url for RPC service",)
    args = parser.parse_args(argv)

    if not args.server:
        raise CommandlineArgumentError("You need to define a server URL")

    if os.path.exists(os.path.expanduser(conf.filename)):
        raw_input("Config file already exists. If you want to abort press ^C otherwise press enter.")

    try:
        lrpc = LockRPC(server=args.server)
        u,p = lrpc.register()
    except TypeError:
        raise CommandError("Config file is missing or is invalid. Try re-registering your client")
    except RegisterException,e:
        raise CommandError("Couldn't register with server: %s" % e)

    try:
        conf['username'] = u
        conf['password'] = p
        conf['server'] = args.server
        conf.save()
    except Exception,e:
        logger.error("Couldn't config %s: %s" % (conf.filename, e))
        raise


def cmd_execute(conf, argv):
    """
    Execute command if lock can be acquired
    """
    usage = "%(prog)s [options] execute [execute_options] -l lock_name command"
    description = inspect.getdoc(cmd_execute)
    parser = ArgumentParser(
        usage = usage,
        description = description)
    parser.add_argument("-s", "--silent", action="store_true",
            default=False, help="Fail silently on error",)
    parser.add_argument("-l", "--lock", dest="lock",
            required=True, help="lock name",)
    parser.add_argument("-x", "--exclusive", action="store_true",
            default=False, help="Acquire exclusive lock",)
    parser.add_argument("command", help="command to execute",)
    args = parser.parse_args(argv)

    try:
        lrpc = LockRPC(**conf)
        lrpc.lock(args.lock, exclusive=args.exclusive)
        from subprocess import call
        call(args.command.split(" "))
        lrpc.unlock(args.lock)
    except LockException,e:
        if args.silent:
            return

        raise CommandError("Couldn't acquire lock %s: %s" % (args.lock, e))
    except (Exception, SystemExit):
        lrpc.unlock(args.lock)
        raise

def cmd_help(conf, argv):
    """
    List available commands
    """
    usage = "%(prog)s [options] help [help_options] [command_name]"
    description = inspect.getdoc(cmd_help)
    parser = ArgumentParser(usage=usage,description=description)
    parser.add_argument("command", nargs="?", default=None, help="command name")
    args = parser.parse_args(argv)

    import locksmith.util
    cmds = locksmith.util.discover_commands()
    if args.command:
        try:
            cmds[argv[0]]({}, ['--help'])
        except KeyError:
            raise Exception("Command not found")

    logger.info("Available commands:")

    for k in sorted(cmds.keys()):
        logger.info("  {:16}\t{}".format(k, inspect.getdoc(cmds[k])))
