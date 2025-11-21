"""
Easy Diff Basic Commands.

Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import sublime_plugin
from os.path import basename
from EasyDiff.easy_diff_global import load_settings, log, get_external_diff, get_target, get_group_view
from EasyDiff.easy_diff_dynamic_menu import update_menu
from EasyDiff.easy_diff import EasyDiffView, EasyDiffInput, EasyDiff

LEFT = None


###############################
# Helper Functions
###############################
def diff(left, right, external=False):
    """
    Initiate diff by getting left side and right side compare.

    Call the appropriate diff method and call internal or external diff.
    """

    lw = None
    rw = None
    lv = None
    rv = None

    for w in sublime.windows():
        if w.id() == left["win_id"]:
            lw = w
        if w.id() == right["win_id"]:
            rw = w
        if lw is not None and rw is not None:
            break

    if lw is not None:
        for v in lw.views():
            if v.id() == left["view_id"]:
                lv = v
                break
    else:
        if left["clip"]:
            lv = left["clip"]

    if rw is not None:
        for v in rw.views():
            if v.id() == right["view_id"]:
                rv = v
                break
    else:
        if right["clip"]:
            rv = right["clip"]

    if lv is not None and rv is not None:
        ext_diff = get_external_diff()
        if external:
            EasyDiff.extcompare(EasyDiffInput(lv, rv, external=True), ext_diff)
        else:
            EasyDiff.compare(EasyDiffInput(lv, rv))
    else:
        log("Can't compare")


def get_mru_window(win_id):
    """Get MRU window."""

    window = None
    for w in sublime.windows():
        if w.id() == win_id:
            window = w
            break
    return window


def get_mru_view(mru_obj):
    """Get MRU view."""

    view = None
    if mru_obj is not None:
        win_id, group, index, view_id = mru_obj
        window = get_mru_window(win_id)
        v = get_group_view(window, group, index)
        if v and v.id() == view_id:
            view = v
    return view


def panel_enable_check(method="view", external=False):
    """Check if panel command can be enabled."""

    allow = bool(load_settings().get("last_activated_commands", True))
    enabled = False
    if method == "left":
        enabled = bool(
            load_settings().get("quick_panel_left_right_commands", True)
        )
    elif method == "compare":
        enabled = (
            LEFT is not None and
            bool(load_settings().get("quick_panel_left_right_commands", True))
        )
    elif method == "mru":
        current = get_mru_view(EasyDiffListener.current)
        last = get_mru_view(EasyDiffListener.last)
        enabled = (
            allow and
            bool(current and last)
        )
    elif method == "clipboard":
        enabled = (
            bool(load_settings().get("use_clipboard", True)) and
            bool(get_mru_view(EasyDiffListener.current))
        )
    elif method == "svn":
        enabled = not bool(load_settings().get("svn_disabled", False))
    elif method == "git":
        enabled = not bool(load_settings().get("git_disabled", False))
    elif method == "hg":
        enabled = not bool(load_settings().get("hg_disabled", False))

    if external:
        enabled = (
            enabled and
            bool(load_settings().get("show_external", True)) and
            get_external_diff() is not None
        )
    else:
        enabled = (
            enabled and
            bool(load_settings().get("show_internal", True))
        )
    return enabled


###############################
# Helper Classes
###############################
class _EasyDiffSelection(object):
    """Handle selection diff."""

    def get_selections(self):
        """Get the selections."""

        bfr = ""
        length = len(self.view.sel())
        for s in self.view.sel():
            if s.size() == 0:
                continue
            bfr += self.view.substr(s)
            if length > 1:
                bfr += "\n"
            length -= 1
        return bfr

    def get_encoding(self):
        """Get view encoding."""

        return self.view.encoding()

    def has_selections(self, view=None):
        """Check if view has a valid selection."""

        if view is None:
            view = self.view
        selections = False
        if bool(load_settings().get("multi_select", False)):
            for s in view.sel():
                if s.size() > 0:
                    selections = True
                    break
        else:
            selections = len(view.sel()) == 1 and view.sel()[0].size() > 0
        return selections


###############################
# Compare Views
###############################
class EasyDiffSetLeftCommand(sublime_plugin.WindowCommand, _EasyDiffSelection):
    """Set left side command."""

    def run(self, external=False, paths=[], group=-1, index=-1):
        """Run command."""

        global LEFT
        self.external = external
        self.set_view(paths, group, index)
        if self.view is not None:
            if bool(load_settings().get("use_selections", True)) and self.has_selections():
                LEFT = {
                    "win_id": None, "view_id": None,
                    "clip": EasyDiffView("sel", self.get_selections(), self.get_encoding())
                }
            else:
                LEFT = {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}
                name = self.view.file_name()
                if name is None:
                    name = "Untitled"

    def set_view(self, paths, group=-1, index=-1, open_file=True):
        """Set view."""

        self.view = None
        if len(paths):
            file_path = get_target(paths)
            if file_path is None:
                return
            if open_file:
                self.view = self.window.open_file(file_path)
            else:
                self.view = self.window.find_open_file(file_path)
        elif index != -1:
            self.view = get_group_view(self.window, group, index)
        else:
            self.view = self.window.active_view()

    def is_enabled(self, external=False, paths=[], group=-1, index=-1):
        """Check if command is enabled."""

        return get_target(paths, group, index) is not None if len(paths) or index != -1 else True

    def description(self, external=False, paths=[], group=-1, index=-1):
        """Return menu description."""

        self.set_view(paths, group, index, False)
        if self.view is not None and bool(load_settings().get("use_selections", True)) and self.has_selections():
            description = "%sDiff Set Left Side [sel]" % ('' if external else 'Easy')
        else:
            description = "%sDiff Set Left Side" % ('' if external else 'Easy')
        return description


class EasyDiffCompareBothCommand(sublime_plugin.WindowCommand, _EasyDiffSelection):
    """Compare window command."""

    def run(self, external=False, clipboard=False, paths=[], group=-1, index=-1):
        """Run command."""

        self.external = external
        self.clipboard = clipboard
        self.set_view(paths, group, index)
        if self.view is not None:
            self.diff()

    def diff(self):
        """Diff."""

        diff(self.get_left(), self.get_right(), external=self.external)

    def get_left(self):
        """Get left."""

        if self.clipboard:
            left = {
                "win_id": None, "view_id": None,
                "clip": EasyDiffView("clip", sublime.get_clipboard(), "UTF-8")
            }
        else:
            left = LEFT
        return left

    def get_right(self):
        """Get right."""
        if self.has_selections():
            right = {
                "win_id": None, "view_id": None,
                "clip": EasyDiffView("sel", self.get_selections(), self.get_encoding())
            }
        else:
            right = {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}
        return right

    def set_view(self, paths, group=-1, index=-1, open_file=True):
        """Set view."""

        self.view = None
        if len(paths):
            file_path = get_target(paths)
            if file_path is None:
                return
            if open_file:
                self.view = self.window.open_file(file_path)
            else:
                self.view = self.window.find_open_file(file_path)
        elif index != -1:
            self.view = get_group_view(self.window, group, index)
        else:
            self.view = self.window.active_view()

    def is_enabled(self, clipboard=False, external=False, paths=[], group=-1, index=-1):
        """Check if command is enabled."""

        if clipboard:
            enabled = (
                bool(load_settings().get("use_clipboard", True)) and
                (get_target(paths, group, index) is not None if len(paths) or index != -1 else True)
            )
        else:
            enabled = (
                LEFT is not None and
                (get_target(paths, group, index) is not None if len(paths) or index != -1 else True)
            )
        return enabled

    def is_visible(self, clipboard=False, external=False, paths=[], group=-1, index=-1):
        """Check if visible in menu."""

        return bool(load_settings().get("use_clipboard", True)) if clipboard else True

    def get_left_name(self):
        """Get left name."""

        name = '"..."'
        if LEFT is not None:
            left = LEFT.get("clip")
            name = None
            if left is not None:
                name = "[%s]" % left.file_name()
            else:
                win_id = LEFT.get("win_id")
                view_id = LEFT.get("view_id")
                window = None
                view = None
                for w in sublime.windows():
                    if w.id() == win_id:
                        window = w
                if window is not None:
                    for v in window.views():
                        if v.id() == view_id:
                            view = v
                if view is not None:
                    name = view.file_name()
                    if name is None:
                        name = '"Untitled"'
                    else:
                        name = '"%s"' % basename(name)
        return name

    def description(self, external=False, clipboard=False, paths=[], group=-1, index=-1):
        """Return menu description."""

        self.set_view(paths, group, index, False)
        if clipboard:
            if self.view is not None and bool(load_settings().get("use_selections", True)) and self.has_selections():
                description = "%sDiff Compare [sel] with Clipboard" % ('' if external else 'Easy')
            else:
                description = "%sDiff Compare Tab with Clipboard" % ('' if external else 'Easy')
        elif self.view is not None and self.has_selections():
            description = "%sDiff Compare [sel] with %s" % (
                '' if external else 'Easy',
                self.get_left_name()
            )
        else:
            description = "%sDiff Compare with %s" % (
                '' if external else 'Easy',
                self.get_left_name()
            )
        return description


###############################
# MRU Tab Command
###############################
class EasyDiffMruCompareCommand(sublime_plugin.WindowCommand, _EasyDiffSelection):
    """Most recently used compare command."""

    def run(self, external=False, paths=[], group=-1, index=-1):
        """Run command."""

        window = get_mru_window(EasyDiffListener.last[0])
        view = get_mru_view(EasyDiffListener.last)
        if view:
            window.run_command(
                "easy_diff_set_left",
                {"group": EasyDiffListener.last[1], "index": EasyDiffListener.last[2]}
            )
            self.window.run_command(
                "easy_diff_compare_both",
                {"external": external}
            )

    def is_enabled(self, external=False):
        """Check if command is enabled."""

        return panel_enable_check("mru", external)

    def is_visible(self, external=False, paths=[], group=-1, index=-1):
        """Check if command is visible."""

        return bool(load_settings().get("last_activated_commands", True))

    def get_mru_sels(self):
        """Get MRU selections."""

        mru_last_sel = False
        mru_current_sel = False
        if bool(load_settings().get("use_selections", True)):
            view = get_mru_view(EasyDiffListener.last)
            if self.view is not None:
                mru_last_sel = self.has_selections(view)
                view = get_mru_view(EasyDiffListener.current)
                if self.view is not None:
                    mru_current_sel = self.has_selections(view)
        return mru_last_sel, mru_current_sel

    def description(self, external=False, paths=[], group=-1, index=-1):
        """Return menu description."""

        view_l = get_mru_view(EasyDiffListener.last)
        view_c = get_mru_view(EasyDiffListener.current)
        use_selections = bool(load_settings().get("use_selections", True))
        sel_l = "Tab"
        sel_c = "Tab"

        if view_l and use_selections:
            self.view = view_l
            if self.has_selections():
                sel_l = "[sel]"
        if view_c and use_selections:
            self.view = view_c
            if self.has_selections():
                sel_c = "[sel]"
        self.view = None

        description = "%sDiff Last %s with Current %s" % ('' if external else 'Easy', sel_l, sel_c)
        return description


###############################
# Quick Panel Diff
###############################
class EasyDiffPanelCommand(sublime_plugin.TextCommand, _EasyDiffSelection):
    """Diff panel command."""

    panel_entries = [
        {
            "caption": "Set Left Side%(selections)s",
            "cmd": "easy_diff_set_left",
            "type": "window",
            "condition": "left"
        },
        {
            "caption": "Compare%(selections)s with %(file)s",
            "cmd": "easy_diff_compare_both",
            "type": "window",
            "condition": "compare"
        },
        {
            "caption": "Quick Compare: Current %(selections)s with Clipboard",
            "cmd": "easy_diff_compare_both",
            "args": {"clipboard": True},
            "type": "window",
            "condition": "clipboard"
        },
        {
            "caption": "Quick Compare: Last %(mru_last_sel)s with Current %(mru_current_sel)s",
            "cmd": "easy_diff_mru_compare",
            "type": "window",
            "condition": "mru"
        },
        {
            "caption": "SVN Diff",
            "cmd": "easy_diff_svn",
            "type": "window",
            "condition": "svn"
        },
        {
            "caption": "SVN Diff with Previous Revision",
            "cmd": "easy_diff_svn",
            "args": {"last": True},
            "type": "window",
            "condition": "svn"
        },
        {
            "caption": "SVN Revert",
            "cmd": "easy_diff_svn",
            "args": {"revert": True},
            "type": "view",
            "condition": "svn"
        },
        {
            "caption": "GIT Diff",
            "cmd": "easy_diff_git",
            "type": "window",
            "condition": "git"
        },
        {
            "caption": "GIT Diff with Previous Revision",
            "cmd": "easy_diff_git",
            "args": {"last": True},
            "type": "window",
            "condition": "git"
        },
        {
            "caption": "GIT Revert",
            "cmd": "easy_diff_git",
            "args": {"revert": True},
            "type": "view",
            "condition": "git"
        },
        {
            "caption": "Mercurial Diff",
            "cmd": "easy_diff_hg",
            "type": "window",
            "condition": "hg"
        },
        {
            "caption": "Mercurial Diff with Previous Revision",
            "cmd": "easy_diff_hg",
            "args": {"last": True},
            "type": "window",
            "condition": "hg"
        },
        {
            "caption": "Mercurial Revert",
            "cmd": "easy_diff_hg",
            "args": {"revert": True},
            "type": "view",
            "condition": "hg"
        },
    ]

    def run(self, edit, external=False):
        """Run command."""

        self.external = external
        self.menu_options = []
        self.menu_callback = []
        if (
            (not external and bool(load_settings().get("show_internal", True))) or
            (external and bool(load_settings().get("show_external", True)))
        ):
            left_name = self.get_left_name()
            selections = bool(load_settings().get("use_selections", True)) and self.has_selections()
            mru_last_sel, mru_current_sel = self.get_mru_sels()
            mru_last = " [sel]" if mru_last_sel else "Tab"
            mru_current = " [sel]" if mru_current_sel else "Tab"
            for entry in self.panel_entries:
                if panel_enable_check(entry["condition"], external):
                    self.menu_options.append(
                        entry["caption"] % {
                            "file": left_name,
                            "selections": ' [sel]' if selections else 'Tab',
                            "mru_last_sel": mru_last,
                            "mru_current_sel": mru_current
                        }
                    )
                    target = self.view.window() if entry["type"] == "window" else self.view
                    args = entry.get("args", {}).copy()
                    args["external"] = external
                    self.menu_callback.append(
                        lambda t=target, e=entry, a=args: t.run_command(e["cmd"], a)
                    )
        if len(self.menu_options) > 1:
            self.view.window().show_quick_panel(self.menu_options, self.check_selection)
        elif len(self.menu_options) == 1:
            self.check_selection(0)

    def get_mru_sels(self):
        """Get MRU selections."""

        mru_last_sel = False
        mru_current_sel = False
        if bool(load_settings().get("use_selections", True)):
            view = get_mru_view(EasyDiffListener.last)
            if self.view is not None:
                mru_last_sel = self.has_selections(view)
                view = get_mru_view(EasyDiffListener.current)
                if self.view is not None:
                    mru_current_sel = self.has_selections(view)
        return mru_last_sel, mru_current_sel

    def get_left_name(self):
        """Get left name."""

        name = None
        if LEFT is not None:
            left = LEFT.get("clip")
            name = None
            if left is not None:
                name = left.file_name()
            else:
                win_id = LEFT.get("win_id")
                view_id = LEFT.get("view_id")
                window = None
                view = None
                for w in sublime.windows():
                    if w.id() == win_id:
                        window = w
                if window is not None:
                    for v in window.views():
                        if v.id() == view_id:
                            view = v
                if view is not None:
                    name = view.file_name()
                    if name is None:
                        name = "Untitled"
                    else:
                        name = basename(name)
        return name

    def check_selection(self, value):
        """Check user's selection."""

        if value != -1:
            callback = self.menu_callback[value]
            sublime.set_timeout(callback, 0)

    def is_enabled(self, external=False):
        """Check if command is enabled."""

        return (
            (not external and bool(load_settings().get("show_internal", True))) or
            (external and bool(load_settings().get("show_external", True)))
        ) and bool(load_settings().get("quick_panel_commands", True))


###############################
# View Close Listener
###############################
class EasyDiffListener(sublime_plugin.EventListener):
    """Listener for EasyDiff."""

    current = None
    last = None

    def on_close(self, view):
        """Update menu on view close."""

        global LEFT
        vid = view.id()
        if LEFT is not None and vid == LEFT["view_id"]:
            LEFT = None

    def on_activated(self, view):
        """Track last activated view."""
        if view.settings().get('is_widget'):
            return
        cls = EasyDiffListener
        window = view.window()
        if window is not None:
            sheet = window.active_sheet()
            win_id = window.id()
            view_id = view.id()
            group, index = window.get_sheet_index(sheet)
            if group != -1:
                if (win_id, group, index, view_id) != cls.current:
                    cls.last = cls.current
                    cls.current = (win_id, group, index, view_id)


###############################
# Loaders
###############################
def basic_reload():
    """Reload on settings change."""

    global LEFT
    LEFT = None
    update_menu()
    settings = load_settings()
    settings.clear_on_change('reload_basic')
    settings.add_on_change('reload_basic', basic_reload)


def plugin_loaded():
    """Plugin reload."""

    basic_reload()
