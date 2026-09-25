import os
import importlib.util

_MODULE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'space-engineers-utilities', 'utils', 'seut_paths.py',
)
_spec = importlib.util.spec_from_file_location('seut_paths', _MODULE_PATH)
seut_paths = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seut_paths)

relative_from_folder = seut_paths.relative_from_folder
to_content_path = seut_paths.to_content_path
to_tool_path = seut_paths.to_tool_path
is_linux = seut_paths.is_linux


def test_relative_from_folder_midpath_unix():
    assert relative_from_folder('/home/u/MyMod/Models/Cubes/x.fbx', 'Models', '/') == 'Models/Cubes/x.fbx'


def test_relative_from_folder_midpath_windows():
    assert relative_from_folder('C:\\m\\Models\\Cubes\\x.fbx', 'Models', '\\') == 'Models\\Cubes\\x.fbx'


def test_relative_from_folder_at_end_unix():
    assert relative_from_folder('/home/u/Models', 'Models', '/') == 'Models'


def test_relative_from_folder_at_end_windows():
    assert relative_from_folder('C:\\a\\Models', 'Models', '\\') == 'Models'


def test_relative_from_folder_absent():
    assert relative_from_folder('/home/u/foo/bar', 'Models', '/') is False


def test_relative_from_folder_multiple_occurrence():
    assert relative_from_folder('/a/Models/b/Models/c.fbx', 'Models', '/') == 'Models/c.fbx'


def test_relative_from_folder_substring_no_false_match():
    assert relative_from_folder('/a/Models/x.fbx', 'Model', '/') is False


def test_to_content_path_from_unix():
    assert to_content_path('Models/Cubes/x.mwm', '/') == 'Models\\Cubes\\x.mwm'


def test_to_content_path_from_windows_noop():
    assert to_content_path('Models\\Cubes\\x.mwm', '\\') == 'Models\\Cubes\\x.mwm'


def test_to_content_path_default_sep():
    assert to_content_path(os.sep.join(['a', 'b', 'c'])) == 'a\\b\\c'


def test_to_tool_path_non_linux_identity():
    assert to_tool_path('C:\\mod\\x.fbx', linux=False) == 'C:\\mod\\x.fbx'


def test_to_tool_path_linux_z_drive():
    assert to_tool_path('/home/u/x.fbx', linux=True) == 'Z:\\home\\u\\x.fbx'


def test_to_tool_path_linux_nested():
    assert to_tool_path('/a/b/c/d.hkt', linux=True) == 'Z:\\a\\b\\c\\d.hkt'


def test_to_tool_path_linux_rejects_relative():
    try:
        to_tool_path('rel/path.fbx', linux=True)
    except ValueError:
        return
    raise AssertionError('expected ValueError for relative path on linux')


def test_to_tool_path_non_linux_allows_relative():
    assert to_tool_path('rel/path.fbx', linux=False) == 'rel/path.fbx'


def test_is_linux_returns_bool():
    assert isinstance(is_linux(), bool)
