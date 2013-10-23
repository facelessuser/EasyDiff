"""
Easy Diff Dynamic Menu

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import join, exists
from os import makedirs

MENU_FOLDER = "EasyDiff"
CONTEXT_MENU = "Context.sublime-menu"
DIFF_MENU = '''[
    { "caption": "-" },
    {
        "caption": "EasyDiff Set Left Side",
        "children":
        [
            {
                "caption": "View",
                "command": "easy_diff_set_left"
            },
            {
                "caption": "Clipboard",
                "command": "easy_diff_set_left_clipboard"
            },
            {
                "caption": "Selection",
                "command": "easy_diff_set_left_selection"
            }
        ]
    },
    {
        "caption": "EasyDiff Compare with \\"%(file_name)s\\"",
        "children":
        [
            {
                "caption": "View",
                "command": "easy_diff_compare_both_view"
            },
            {
                "caption": "Clipboard",
                "command": "easy_diff_compare_both_clipboard"
            },
            {
                "caption": "Selection",
                "command": "easy_diff_compare_both_selection"
            }
        ]
    },
    {
        "caption": "EasyDiff SVN",
        "children":
        [
            {
                "caption": "Diff",
                "command": "easy_diff_svn"
            },
            {
                "caption": "Diff Last Revision",
                "command": "easy_diff_svn",
                "args": {"last": true}
            }
        ]
    },
    {
        "caption": "EasyDiff Git",
        "children":
        [
            {
                "caption": "Diff",
                "command": "easy_diff_git"
            },
            {
                "caption": "Diff (staged for commit)",
                "command": "easy_diff_git",
                "args": {"staged": true}
            },
            {
                "caption": "Diff Last Revision",
                "command": "easy_diff_git",
                "args": {"last": true}
            }
        ]
    },
    { "caption": "-"}
]
'''


def update_menu(name="..."):
    menu_path = join(sublime.packages_path(), "User", MENU_FOLDER)
    if not exists(menu_path):
        makedirs(menu_path)
    if exists(menu_path):
        menu = join(menu_path, CONTEXT_MENU)
        with open(menu, "w") as f:
            f.write(DIFF_MENU % {"file_name": name})
