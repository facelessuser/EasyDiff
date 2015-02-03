"""
Easy Diff Global

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import exists, normpath, abspath, isdir
from EasyDiff.lib.multiconf import get as multiget
import re
try:
    from SubNotify.sub_notify import SubNotifyIsReadyCommand as Notify
except:
    class Notify:
        @classmethod
        def is_ready(cls):
            return False


DEBUG = False
SETTINGS = "easy_diff.sublime-settings"
SHEET_WORKAROUND = int(sublime.version()) < 3068

try:
    # If TabsExtra is installed, we want to use its "get_group_view"
    # This will keep from messing up our TabsExtra activation tracker by disabling
    # timestamps when refocusing our view when we try to resolve sheet index
    # with view index.
    from TabsExtra.tabs_extra import get_group_view
except:
    # TabsExtra is not available.  Do not worry about activation trackers.
    def get_group_view(window, group, index):
        """
        Get the view at the given index in the given group.
        """

        if SHEET_WORKAROUND:
            active_sheet = window.active_sheet()
        sheets = window.sheets_in_group(int(group))
        if index < len(sheets):
            sheet = sheets[index]
        else:
            sheet = None
        if sheet is not None:
            if SHEET_WORKAROUND:
                window.focus_sheet(sheet)
                view = window.active_view()
            else:
                view = sheet.view()

        if SHEET_WORKAROUND:
            window.focus_sheet(active_sheet)

        return view


def log(msg, status=False):
    string = str(msg)
    print("EasyDiff: %s" % string)
    if status:
        notify(string)


def debug(msg, status=False):
    if DEBUG:
        log(msg, status)


def load_settings():
    return sublime.load_settings(SETTINGS)


def global_reload():
    set_debug_flag()
    settings = load_settings()
    settings.clear_on_change('reload_global')
    settings.add_on_change('reload_global', global_reload)


def set_debug_flag():
    global DEBUG
    settings = load_settings()
    DEBUG = settings.get("debug", False)
    debug("debug logging enabled")


def get_encoding(view):
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
    settings = load_settings()
    ext_diff = multiget(settings, "external_diff", None)
    diff_path = None if ext_diff is None or ext_diff == "" or not exists(abspath(normpath(ext_diff))) else abspath(normpath(ext_diff))
    debug("External diff was not found!" if diff_path is None else "External diff \"%s\" found." % diff_path)
    return diff_path


def get_target(paths=[], group=-1, index=-1):
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
    if load_settings().get("use_sub_notify", False) and Notify.is_ready():
        sublime.run_command("sub_notify", {"title": "EasyDiff", "msg": msg})
    else:
        sublime.status_message(msg)


def plugin_loaded():
    global_reload()
