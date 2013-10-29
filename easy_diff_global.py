"""
Easy Diff Global

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import exists, normpath, abspath
from EasyDiff.lib.multiconf import get as multiget
import re

DEBUG = False
EXTERNAL_DIFF = None
SETTINGS = "easy_diff.sublime-settings"


def log(msg, status=False):
    string = str(msg)
    print("EasyDiff: %s" % string)
    if status:
        sublime.status_message(string)


def debug(msg, status=False):
    if DEBUG:
        log(msg, status)


def load_settings():
    return sublime.load_settings(SETTINGS)


def global_reload():
    set_debug_flag()
    set_external_diff()
    settings = load_settings()
    settings.clear_on_change('reload_global')
    settings.add_on_change('reload_global', global_reload)


def set_debug_flag():
    global DEBUG
    settings = load_settings()
    DEBUG = settings.get("debug", False)
    debug("debug logging enabled")


def set_external_diff():
    global EXTERNAL_DIFF
    global SHOW_EXTERNAL
    settings = load_settings()
    ext_diff = multiget(settings, "external_diff", None)
    if ext_diff is None or ext_diff == "" or not exists(abspath(normpath(ext_diff))):
        EXTERNAL_DIFF = None
    else:
        EXTERNAL_DIFF = abspath(normpath(ext_diff))

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
    return EXTERNAL_DIFF


def plugin_loaded():
    global_reload()
