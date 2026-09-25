import os
import sys
import posixpath


def is_windows() -> bool:
    return sys.platform == 'win32'


def is_linux() -> bool:
    return sys.platform == 'linux'


def to_tool_path(path: str, linux: bool = None) -> str:
    """Converts an absolute local path to the wine drive form on Linux; unchanged elsewhere."""
    if linux is None:
        linux = is_linux()

    if not linux:
        return path

    if not posixpath.isabs(path):
        raise ValueError("to_tool_path requires an absolute path: %s" % path)

    # wine maps Z:\ to host / by default
    return 'Z:' + path.replace('/', '\\')


def relative_from_folder(abspath: str, folder_name: str, sep: str = os.sep):
    """Returns abspath capped before the last occurrence of folder_name, or False if absent."""
    offset = abspath.rfind(sep + folder_name + sep)

    if offset == -1:
        if abspath.endswith(sep + folder_name):
            return abspath[abspath.rfind(sep + folder_name) + 1:]
        return False

    return abspath[offset + 1:]


def to_content_path(rel: str, sep: str = os.sep) -> str:
    """Converts an os-native relative path to SE content form (backslash-separated)."""
    return rel.replace(sep, '\\')
