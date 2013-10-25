"""
Easy Diff Dynamic Menu

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import join, exists
from os import makedirs
from EasyDiff.easy_diff_global import load_settings, debug

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
    %(vc)s
    { "caption": "-"}
]
'''

VC_MENU = '''{
        "caption": "EasyDiff Version Control",
        "children":
        [
%(vc)s
        ]
    },
'''

SVN_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn"
            },
            {
                "caption": "SVN Diff Last Revision",
                "command": "easy_diff_svn",
                "args": {"last": true}
            },
            { "caption": "-"}'''

GIT_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git"
            },
            {
                "caption": "Git Diff (staged for commit)",
                "command": "easy_diff_git",
                "args": {"staged": true}
            },
            {
                "caption": "Git Diff Last Revision",
                "command": "easy_diff_git",
                "args": {"last": true}
            },
            { "caption": "-"}'''

HG_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg"
            },
            {
                "caption": "Mercurial Diff Last Revision",
                "command": "easy_diff_hg",
                "args": {"last": true}
            },
            { "caption": "-"}'''


def update_menu(name="..."):
    menu_path = join(sublime.packages_path(), "User", MENU_FOLDER)
    if not exists(menu_path):
        makedirs(menu_path)
    if exists(menu_path):
        settings = load_settings()
        svn_disabled = settings.get("svn_disabled", False) or settings.get("svn_hide_menu", False)
        git_disabled = settings.get("git_disabled", False) or settings.get("git_hide_menu", False)
        hg_disabled = settings.get("hg_disabled", False) or settings.get("hg_hide_menu", False)
        menu = join(menu_path, CONTEXT_MENU)
        vc = []
        if not svn_disabled:
            vc.append(SVN_MENU)
        if not git_disabled:
            vc.append(GIT_MENU)
        if not hg_disabled:
            vc.append(HG_MENU)
        vc_menu = None
        if len(vc):
            vc_menu = ",\n".join(vc)
        with open(menu, "w") as f:
            f.write(
                DIFF_MENU % {
                    "file_name": name,
                    "vc": ("" if vc_menu is None else VC_MENU % {"vc": vc_menu})
                }
            )


def refresh_menu():
    update_menu()
    debug("refresh menu")
    settings = load_settings()
    settings.clear_on_change('reload_menu')
    settings.add_on_change('reload_menu', refresh_menu)


def plugin_loaded():
    refresh_menu()
