"""
Easy Diff Dynamic Menu

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import join, exists
from os import makedirs
from EasyDiff.easy_diff_global import load_settings, debug, get_external_diff
from EasyDiff.lib.multiconf import get as multiget

MENU_FOLDER = "EasyDiff"
CONTEXT_MENU = "Context.sublime-menu"
DIFF_MENU = '''[
    %(internal)s
    %(vc_internal)s
    %(external)s
    %(vc_external)s
    { "caption": "-"}
]
'''

INTERNAL_MENU = '''{ "caption": "-" },
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
'''

EXTERNAL_MENU = '''{ "caption": "-" },
    {
        "caption": "Diff Set Left Side",
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
        "caption": "Diff Compare with \\"%(file_name)s\\"",
        "children":
        [
            {
                "caption": "View",
                "command": "easy_diff_compare_both_view",
                "args": {"external": true}
            },
            {
                "caption": "Clipboard",
                "command": "easy_diff_compare_both_clipboard",
                "args": {"external": true}
            },
            {
                "caption": "Selection",
                "command": "easy_diff_compare_both_selection",
                "args": {"external": true}
            }
        ]
    },
'''

VC_INTERNAL_MENU = '''{
        "caption": "EasyDiff Version Control",
        "children":
        [
%(vc)s
        ]
    },
'''

VC_EXTERNAL_MENU = '''{
        "caption": "Diff Version Control",
        "children":
        [
%(vc)s
        ]
    },
'''

SVN_INTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn"
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"last": true}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true}
            },
            { "caption": "-"}'''

GIT_INTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git"
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"last": true}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true}
            },
            { "caption": "-"}'''

HG_INTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg"
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"last": true}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true}
            },
            { "caption": "-"}'''

SVN_EXTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn",
                "args": {"external": true}
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"external": true, "last": true}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true}
            },
            { "caption": "-"}'''

GIT_EXTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git",
                "args": {"external": true}
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"external": true, "last": true}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true}
            },
            { "caption": "-"}'''

HG_EXTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg",
                "args": {"external": true}
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"external": true, "last": true}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true}
            },
            { "caption": "-"}'''


def update_menu(name="..."):
    menu_path = join(sublime.packages_path(), "User", MENU_FOLDER)
    if not exists(menu_path):
        makedirs(menu_path)
    if exists(menu_path):
        settings = load_settings()
        svn_disabled = multiget(settings, "svn_disabled", False) or multiget(settings, "svn_hide_menu", False)
        git_disabled = multiget(settings, "git_disabled", False) or multiget(settings, "git_hide_menu", False)
        hg_disabled = multiget(settings, "hg_disabled", False) or multiget(settings, "hg_hide_menu", False)
        show_ext = multiget(settings, "show_external", False) and get_external_diff() is not None
        show_int = multiget(settings, "show_internal", True)
        menu = join(menu_path, CONTEXT_MENU)
        vc_internal = []
        vc_internal_menu = None
        if show_int:
            if not svn_disabled:
                vc_internal.append(SVN_INTERNAL_MENU)
            if not git_disabled:
                vc_internal.append(GIT_INTERNAL_MENU)
            if not hg_disabled:
                vc_internal.append(HG_INTERNAL_MENU)
            if len(vc_internal):
                vc_internal_menu = ",\n".join(vc_internal)
        vc_external = []
        vc_external_menu = None
        if show_ext:
            if not svn_disabled:
                vc_external.append(SVN_EXTERNAL_MENU)
            if not git_disabled:
                vc_external.append(GIT_EXTERNAL_MENU)
            if not hg_disabled:
                vc_external.append(HG_EXTERNAL_MENU)
            if len(vc_external):
                vc_external_menu = ",\n".join(vc_external)
        with open(menu, "w") as f:
            f.write(
                DIFF_MENU % {
                    "internal": ("" if not show_int else INTERNAL_MENU % {"file_name": name}),
                    "external": ("" if not show_ext else EXTERNAL_MENU % {"file_name": name}),
                    "vc_internal": ("" if vc_internal_menu is None or not show_int else VC_INTERNAL_MENU % {"vc": vc_internal_menu}),
                    "vc_external": ("" if vc_external_menu is None or not show_ext else VC_EXTERNAL_MENU % {"vc": vc_external_menu})
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
