import os
import subprocess
import threading

from ..seut_errors          import get_abs_path
from .seut_paths            import is_windows, is_linux

_UNSET = object()


def wine_prefix_cmd(native: bool = False) -> list:
    """Wine command prefix for running a Windows tool, empty off Linux/native."""
    if native or not is_linux():
        return []
    from ..seut_utils import get_preferences
    return [get_preferences().wine_path or 'wine']


def wrap_cmdline(cmdline: list, native: bool = False) -> list:
    """Prepends the wine command prefix on non-Windows for Windows-exe tools."""
    return wine_prefix_cmd(native) + cmdline


def wine_env(native: bool = False):
    """Env with WINEPREFIX for wine runs; None otherwise."""
    if native or not is_linux():
        return None
    from ..seut_utils import get_preferences
    return {**os.environ, 'WINEPREFIX': get_abs_path(get_preferences().wineprefix_path), 'WINEDEBUG': 'fixme-all'}


def call_tool(args: list, logfile=None, native: bool = False, prefix=None, env=_UNSET) -> list:

    if prefix is None:
        prefix = wine_prefix_cmd(native)
    if env is _UNSET:
        env = wine_env(native)

    try:
        out = subprocess.check_output(prefix + args, cwd=None, stderr=subprocess.STDOUT, shell=is_windows(), env=env)
        if logfile is not None:
            write_to_log(logfile, out, args=args)
        return [0, out, args]

    except subprocess.CalledProcessError as e:
        if logfile is not None:
            write_to_log(logfile, e.output, args=args)
        return [e.returncode, e.output, args]

    except Exception as e:
        print(e)


def call_tool_threaded(commands: list, thread_count: int, logfile=None, native: bool = False):

    # Resolve wine prefix + env once on the main thread; bpy is not thread-safe.
    prefix = wine_prefix_cmd(native)
    env = wine_env(native)

    threads = []
    results = []
    commands_left = commands

    while len(commands_left) > 0:
        if len(threads) < thread_count:
            c = commands_left[0]
            t = threading.Thread(target=threaded_call, args=(c, results, prefix, env))
            threads.append(t)
            commands_left.remove(c)
            t.start()
        else:
            t = threads[0]
            threads.remove(t)
            t.join()

    for i in threads:
        i.join()

    if logfile is not None:
        output = ""

        for r in results:
            output += r[1].decode("utf-8", "ignore") + '\n'

        write_to_log(logfile, output.encode())

    return results


def threaded_call(c: list, results: list, prefix: list, env):
    result = call_tool(c, prefix=prefix, env=env)
    results.append(result)


def write_to_log(logfile: str, content: str, args=None, cwd=None):

    with open(get_abs_path(logfile), 'wb') as log:

        if cwd:
            cwd_str = "Running from: " + cwd + '\n'
            log.write(cwd_str.encode('utf-8'))

        if args:
            args_str = "Command: " + str(args) + '\n'
            log.write(args_str.encode('utf-8'))

        log.write(content)


def get_tool_dir() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')