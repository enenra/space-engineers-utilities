import bpy
import os
import subprocess

from ..seut_preferences     import get_addon
from ..seut_errors          import get_abs_path

def call_tool(args: list, logfile=None) -> list:

    try:
        out = subprocess.check_output(args, cwd=None, stderr=subprocess.STDOUT, shell=True)
        if logfile is not None:
            write_to_log(logfile, out, args=args)
        return [0, out]
    
    except subprocess.CalledProcessError as e:
        if logfile is not None:
            write_to_log(logfile, e.output, args=args)
        return [e.returncode, e.output]
    
    except Exception as e:
        print(e)


def write_to_log(logfile: str, content: str, args: list, cwd=None):

    with open(get_abs_path(logfile), 'wb') as log:

        if cwd:
            str = "Running from: %s \n" % (cwd)
            log.write(str.encode('utf-8'))

        if args:
            str = "Command: %s \n" % (" ".join(args))
            log.write(str.encode('utf-8'))

        log.write(content)


def get_tool_dir() -> str:
    return os.path.join(bpy.utils.user_resource("SCRIPTS"), 'addons', __package__[:__package__.find(".")], 'tools')