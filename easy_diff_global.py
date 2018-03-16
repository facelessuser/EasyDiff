"""
Easy Diff Global.

Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import exists, normpath, abspath, isdir
from EasyDiff.lib.multiconf import get as multiget
import re
try:
    from SubNotify.sub_notify import SubNotifyIsReadyCommand as Notify
except Exception:
    class Notify(object):
        """Dummy fallback notify class."""

        @classmethod
        def is_ready(cls):
            """Disable notifications."""

            return False

DEBUG = False
SETTINGS = "easy_diff.sublime-settings"


def get_group_view(window, group, index):
    """Get the view at the given index in the given group."""

    sheets = window.sheets_in_group(int(group))
    sheet = sheets[index] if -1 < index < len(sheets) else None
    view = sheet.view() if sheet is not None else None
    return view


def log(msg, status=False):
    """Log messages."""

    string = str(msg)
    print("EasyDiff: %s" % string)
    if status:
        notify(string)


def debug(msg, status=False):
    """Debug message."""

    if DEBUG:
        log(msg, status)


def load_settings():
    """Load settings."""

    return sublime.load_settings(SETTINGS)


def global_reload():
    """Global reload."""

    set_debug_flag()
    settings = load_settings()
    settings.clear_on_change('reload_global')
    settings.add_on_change('reload_global', global_reload)


def set_debug_flag():
    """Set debug flag."""

    global DEBUG
    settings = load_settings()
    DEBUG = settings.get("debug", False)
    debug("debug logging enabled")


def get_encoding(view):
    """Get the file encoding."""

    encoding = view.encoding()
    mapping = [
        ("with BOM", ""),
        ("Windows", "cp"),
        ("-", "_"),
        (" ", "")
    ]
    encoding = view.encoding()
    m = re.match(r'.+\((.*)\)', encoding)
    if m is not None:
        encoding = m.group(1)

    for item in mapping:
        encoding = encoding.replace(item[0], item[1])

    return "utf_8" if encoding in ["Undefined", "Hexidecimal"] else encoding


def get_external_diff():
    """Get external diff path."""

    settings = load_settings()
    ext_diff = multiget(settings, "external_diff", None)
    if ext_diff is None or ext_diff == "" or not exists(abspath(normpath(ext_diff))):
        diff_path = None
    else:
        diff_path = abspath(normpath(ext_diff))
    debug("External diff was not found!" if diff_path is None else "External diff \"%s\" found." % diff_path)
    return diff_path


def get_target(paths=[], group=-1, index=-1):
    """Get the target."""

    target = None
    if index != -1:
        view = get_group_view(sublime.active_window(), group, index)
        if view is not None:
            target = view.file_name()
            if target is None:
                target = ""
    elif len(paths) and exists(paths[0]) and not isdir(paths[0]):
        target = paths[0]
    return target


def notify(msg):
    """Notify with SubNotify if possible and enabled."""

    if load_settings().get("use_sub_notify", False) and Notify.is_ready():
        sublime.run_command("sub_notify", {"title": "EasyDiff", "msg": msg})
    else:
        sublime.status_message(msg)


def plugin_loaded():
    """Setup plugin."""

    global_reload()
