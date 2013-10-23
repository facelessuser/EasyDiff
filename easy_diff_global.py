"""
Easy Diff Global

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
DEBUG = False
SETTINGS = "easy_diff.sublime-settings"


def log(msg):
    print("EasyDiff: %s" % str(msg))


def debug(msg):
    if DEBUG:
        log(msg)


def load_settings():
    return sublime.load_settings(SETTINGS)


def set_debug_flag():
    global DEBUG
    settings = load_settings()
    DEBUG = settings.get("debug", False)
    debug("debug logging enabled")
    settings.clear_on_change('reload_global')
    settings.add_on_change('reload_global', set_debug_flag)


def plugin_loaded():
    set_debug_flag()
