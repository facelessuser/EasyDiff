"""
EasyDiff Dynamic Menu.

Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
from os.path import join, exists
from os import makedirs, remove
from EasyDiff.easy_diff_global import load_settings, debug, get_external_diff
from EasyDiff.lib.multiconf import get as multiget

MENU_FOLDER = "EasyDiff"
CONTEXT_MENU = "Context.sublime-menu"
SIDEBAR_MENU = "Side Bar.sublime-menu"
TAB_MENU = "Tab Context.sublime-menu"


###############################
# General Menus
###############################
DIFF_MENU = '''[
    %(internal)s
    %(vc_internal)s
    %(external)s
    %(vc_external)s
    { "caption": "-"}
]
'''

DIFF_SUBMENU = '''
[
    { "caption": "-"},
    {
    "caption": "EasyDiff",
    "children":
    [
    %(internal)s
    %(vc_internal)s
    %(external)s
    %(vc_external)s
    { "caption": "-"}
    ]
    }
]
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

###############################
# View Menus
###############################
INTERNAL_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left"
    },
    {
        "command": "easy_diff_compare_both"
    },
'''

EXTERNAL_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left",
        "args": {"external": true}
    },
    {
        "command": "easy_diff_compare_both",
        "args": {"external": true}
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


###############################
# Sidebar Menus
###############################
INTERNAL_SIDEBAR_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left",
        "args": {"paths": []}
    },
    {
        "command": "easy_diff_compare_both",
        "args": {"paths": []}
    },
'''

EXTERNAL_SIDEBAR_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left",
        "args": {"external": true, "paths": []}
    },
    {
        "command": "easy_diff_compare_both",
        "args": {"external": true, "paths": []}
    },
'''

SVN_SIDEBAR_INTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn",
                "args": {"paths": []}
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"last": true, "paths": []}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''

GIT_SIDEBAR_INTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git",
                "args": {"paths": []}
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"last": true, "paths": []}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''

HG_SIDEBAR_INTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg",
                "args": {"paths": []}
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"last": true, "paths": []}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''

SVN_SIDEBAR_EXTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn",
                "args": {"external": true, "paths": []}
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"external": true, "last": true, "paths": []}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''

GIT_SIDEBAR_EXTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git",
                "args": {"external": true, "paths": []}
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"external": true, "last": true, "paths": []}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''

HG_SIDEBAR_EXTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg",
                "args": {"external": true, "paths": []}
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"external": true, "last": true, "paths": []}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true, "paths": []}
            },
            { "caption": "-"}'''


###############################
# Tab Menus
###############################
INTERNAL_TAB_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left",
        "args": {"group": -1, "index": -1}
    },
    {
        "command": "easy_diff_compare_both",
        "args": {"group": -1, "index": -1}
    },
'''

EXTERNAL_TAB_MENU = '''{ "caption": "-" },
    {
        "command": "easy_diff_set_left",
        "args": {"external": true, "group": -1, "index": -1}
    },
    {
        "command": "easy_diff_compare_both",
        "args": {"external": true, "group": -1, "index": -1}
    },
'''

SVN_TAB_INTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn",
                "args": {"group": -1, "index": -1}
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"last": true, "group": -1, "index": -1}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''

GIT_TAB_INTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git",
                "args": {"group": -1, "index": -1}
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"last": true, "group": -1, "index": -1}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''

HG_TAB_INTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg",
                "args": {"group": -1, "index": -1}
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"last": true, "group": -1, "index": -1}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''

SVN_TAB_EXTERNAL_MENU = '''
            {
                "caption": "SVN Diff",
                "command": "easy_diff_svn",
                "args": {"external": true, "group": -1, "index": -1}
            },
            {
                "caption": "SVN Diff with Previous Revision",
                "command": "easy_diff_svn",
                "args": {"external": true, "last": true, "group": -1, "index": -1}
            },
            {
                "caption": "SVN Revert",
                "command": "easy_diff_svn",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''

GIT_TAB_EXTERNAL_MENU = '''
            {
                "caption": "Git Diff",
                "command": "easy_diff_git",
                "args": {"external": true, "group": -1, "index": -1}
            },
            {
                "caption": "Git Diff with Previous Revision",
                "command": "easy_diff_git",
                "args": {"external": true, "last": true, "group": -1, "index": -1}
            },
            {
                "caption": "Git Revert",
                "command": "easy_diff_git",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''

HG_TAB_EXTERNAL_MENU = '''
            {
                "caption": "Mercurial Diff",
                "command": "easy_diff_hg",
                "args": {"external": true, "group": -1, "index": -1}
            },
            {
                "caption": "Mercurial Diff with Previous Revision",
                "command": "easy_diff_hg",
                "args": {"external": true, "last": true, "group": -1, "index": -1}
            },
            {
                "caption": "Mercurial Revert",
                "command": "easy_diff_hg",
                "args": {"revert": true, "group": -1, "index": -1}
            },
            { "caption": "-"}'''


###############################
# Menu Updater
###############################
class MenuUpdater(object):
    """Update menu."""

    def __init__(self, name):
        """Initialize."""

        self.name = name
        self.menu_path = join(sublime.packages_path(), "User", MENU_FOLDER)
        if not exists(self.menu_path):
            makedirs(self.menu_path)
        settings = load_settings()
        self.menu_types = multiget(settings, "menu_types", [])
        self.svn_disabled = multiget(settings, "svn_disabled", False) or multiget(settings, "svn_hide_menu", False)
        self.git_disabled = multiget(settings, "git_disabled", False) or multiget(settings, "git_hide_menu", False)
        self.hg_disabled = multiget(settings, "hg_disabled", False) or multiget(settings, "hg_hide_menu", False)
        self.show_ext = multiget(settings, "show_external", False) and get_external_diff() is not None
        self.show_int = multiget(settings, "show_internal", True)

    def update_menu(self, menu_name, menus, submenu):
        """Update the menu."""

        if exists(self.menu_path):
            menu = join(self.menu_path, menu_name)
            vc_internal = []
            vc_internal_menu = None
            if self.show_int:
                if not self.svn_disabled:
                    vc_internal.append(menus["svn"]["internal"])
                if not self.git_disabled:
                    vc_internal.append(menus["git"]["internal"])
                if not self.hg_disabled:
                    vc_internal.append(menus["hg"]["internal"])
                if len(vc_internal):
                    vc_internal_menu = ",\n".join(vc_internal)

            vc_external = []
            vc_external_menu = None
            if self.show_ext:
                if not self.svn_disabled:
                    vc_external.append(menus["svn"]["external"])
                if not self.git_disabled:
                    vc_external.append(menus["git"]["external"])
                if not self.hg_disabled:
                    vc_external.append(menus["hg"]["external"])
                if len(vc_external):
                    vc_external_menu = ",\n".join(vc_external)
            with open(menu, "w") as f:
                f.write(
                    (DIFF_SUBMENU if submenu else DIFF_MENU) % {
                        "internal": ("" if not self.show_int else menus["internal"]),
                        "external": ("" if not self.show_ext else menus["external"]),
                        "vc_internal": (
                            "" if vc_internal_menu is None or not self.show_int else VC_INTERNAL_MENU % {
                                "vc": vc_internal_menu
                            }
                        ),
                        "vc_external": (
                            "" if vc_external_menu is None or not self.show_ext else VC_EXTERNAL_MENU % {
                                "vc": vc_external_menu
                            }
                        )
                    }
                )

    def remove_menu(self, menu_name):
        """Remove the menu."""

        if exists(self.menu_path):
            menu = join(self.menu_path, menu_name)
            if exists(menu):
                remove(menu)

    def update_context_menu(self):
        """Update the context menu."""

        menus = {
            "internal": INTERNAL_MENU,
            "external": EXTERNAL_MENU,
            "svn": {
                "internal": SVN_INTERNAL_MENU,
                "external": SVN_EXTERNAL_MENU
            },
            "git": {
                "internal": GIT_INTERNAL_MENU,
                "external": GIT_EXTERNAL_MENU
            },
            "hg": {
                "internal": HG_INTERNAL_MENU,
                "external": HG_EXTERNAL_MENU
            }
        }
        if "view" in self.menu_types:
            submenu = load_settings().get("submenu", [])
            self.update_menu(CONTEXT_MENU, menus, "view" in submenu)
        else:
            self.remove_menu(CONTEXT_MENU)

    def update_sidebar_menu(self):
        """Update the sidebar menu."""

        menus = {
            "internal": INTERNAL_SIDEBAR_MENU,
            "external": EXTERNAL_SIDEBAR_MENU,
            "svn": {
                "internal": SVN_SIDEBAR_INTERNAL_MENU,
                "external": SVN_SIDEBAR_EXTERNAL_MENU
            },
            "git": {
                "internal": GIT_SIDEBAR_INTERNAL_MENU,
                "external": GIT_SIDEBAR_EXTERNAL_MENU
            },
            "hg": {
                "internal": HG_SIDEBAR_INTERNAL_MENU,
                "external": HG_SIDEBAR_EXTERNAL_MENU
            }
        }
        if "sidebar" in self.menu_types:
            submenu = load_settings().get("submenu", [])
            self.update_menu(SIDEBAR_MENU, menus, "sidebar" in submenu)
        else:
            self.remove_menu(SIDEBAR_MENU)

    def update_tab_menu(self):
        """Update tab menu."""

        menus = {
            "internal": INTERNAL_TAB_MENU,
            "external": EXTERNAL_TAB_MENU,
            "svn": {
                "internal": SVN_TAB_INTERNAL_MENU,
                "external": SVN_TAB_EXTERNAL_MENU
            },
            "git": {
                "internal": GIT_TAB_INTERNAL_MENU,
                "external": GIT_TAB_EXTERNAL_MENU
            },
            "hg": {
                "internal": HG_TAB_INTERNAL_MENU,
                "external": HG_TAB_EXTERNAL_MENU
            }
        }
        if "tab" in self.menu_types:
            submenu = load_settings().get("submenu", [])
            self.update_menu(TAB_MENU, menus, "tab" in submenu)
        else:
            self.remove_menu(TAB_MENU)


def update_menu(name="..."):
    """Update all menus."""

    menu_updater = MenuUpdater(name)
    menu_updater.update_context_menu()
    menu_updater.update_sidebar_menu()
    menu_updater.update_tab_menu()


###############################
# Loaders
###############################
def refresh_menu():
    """Refresh teh menus."""

    update_menu()
    debug("refresh menu")
    settings = load_settings()
    settings.clear_on_change('reload_menu')
    settings.add_on_change('reload_menu', refresh_menu)


def plugin_loaded():
    """Setup plugin."""

    refresh_menu()
