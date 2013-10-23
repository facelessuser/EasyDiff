"""
Easy Diff

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import sublime_plugin
import time
from os import stat as osstat
from os import makedirs
from os.path import basename, join, exists
import difflib
import EasyDiff.lib.svn as svn
import EasyDiff.lib.git as git
from EasyDiff.lib.multiconf import get as multiget

SVN_ENABLED = False
GIT_ENABLED = False

MENU_FOLDER = "EasyDiff"
CONTEXT_MENU = "Context.sublime-menu"
SETTINGS = "easy_diff.sublime-settings"
LEFT = None
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
        "command": "easy_diff_svn_last_rev"
    },
    {
        "caption": "EasyDiff Git",
        "command": "easy_diff_git_last_rev"
    },
    { "caption": "-"}
]
'''

DEBUG = False


def log(msg):
    print("EasyDiff: %s" % str(msg))


def debug(msg):
    if DEBUG:
        log(msg)


def update_menu(name="..."):
    menu_path = join(sublime.packages_path(), "User", MENU_FOLDER)
    if not exists(menu_path):
        makedirs(menu_path)
    if exists(menu_path):
        menu = join(menu_path, CONTEXT_MENU)
        with open(menu, "w") as f:
            f.write(DIFF_MENU % {"file_name": name})


class EasyDiffView(object):
    def __init__(self, name, content):
        self.filename = name
        self.content = content
        self.time = time.ctime()

    def get_time(self):
        return self.time

    def file_name(self):
        return self.filename

    def substr(self, region):
        return self.content[region.begin():region.end() + 1]

    def size(self):
        return len(self.content)


class EasyDiffInput(object):
    def __init__(self, v1, v2):
        untitled = False
        self.f1 = v1.file_name()
        if self.f1 is None:
            self.f1 = "Untitled"
            untitled = True
            self.t1 = time.ctime()
        elif isinstance(v1, EasyDiffView):
            self.t1 = v1.get_time()
        else:
            self.t1 = time.ctime(osstat(self.f1).st_mtime)
        self.b1 = v1.substr(sublime.Region(0, v1.size())).splitlines()

        self.f2 = v2.file_name()
        if self.f2 is None:
            self.f2 = "Untitled2" if untitled else "Untitled"
            self.t2 = time.ctime()
        elif isinstance(v2, EasyDiffView):
            self.t2 = v2.get_time()
        else:
            self.t2 = time.ctime(osstat(self.f2).st_mtime)
        self.b2 = v2.substr(sublime.Region(0, v2.size())).splitlines()


class EasyDiff(object):
    @classmethod
    def compare(cls, inputs):
        diff = difflib.unified_diff(
            inputs.b1, inputs.b2,
            inputs.f1, inputs.f2,
            inputs.t1, inputs.t2,
            lineterm=''
        )
        result = u"\n".join(line for line in diff)

        if result == "":
            sublime.status_message("No Difference")
            return

        use_buffer = bool(sublime.load_settings(SETTINGS).get("use_buffer", False))

        win = sublime.active_window()
        if use_buffer:
            v = win.new_file()
            v.set_name("EasyDiff: %s -> %s (%s)" % (basename(inputs.f1), basename(inputs.f2), time.ctime()))
            v.set_scratch(True)
            v.assign_syntax('Packages/Diff/Diff.tmLanguage')
            v.run_command('append', {'characters': result})
        else:
            v = win.create_output_panel('easy_diff')
            v.assign_syntax('Packages/Diff/Diff.tmLanguage')
            v.run_command('append', {'characters': result})
            win.run_command("show_panel", {"panel": "output.easy_diff"})


class EasyDiffSetLeftCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global LEFT
        LEFT = {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}
        name = self.view.file_name()
        if name is None:
            name = "Untitled"
        update_menu(basename(name))


class EasyDiffSetLeftClipboardCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global LEFT
        LEFT = {"win_id": None, "view_id": None, "clip": EasyDiffView("**clipboard**", sublime.get_clipboard())}
        update_menu("**clipboard**")

    def is_enabled(self):
        return bool(sublime.load_settings(SETTINGS).get("use_clipboard", True))

    is_visible = is_enabled


class _EasyDiffSelection(object):
    def get_selections(self):
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

    def has_selections(self):
        selections = False
        if bool(sublime.load_settings(SETTINGS).get("multi_select", False)):
            for s in self.view.sel():
                if s.size() > 0:
                    selections = True
                    break
        else:
            selections = len(self.view.sel()) == 1 and self.view.sel()[0].size() > 0
        return selections


class EasyDiffSetLeftSelectionCommand(sublime_plugin.TextCommand, _EasyDiffSelection):
    def run(self, edit):
        global LEFT
        LEFT = {"win_id": None, "view_id": None, "clip": EasyDiffView("**selection**", self.get_selections())}
        update_menu("**selection**")

    def is_enabled(self):
        return bool(sublime.load_settings(SETTINGS).get("use_selections", True)) and self.has_selections()

    is_visible = is_enabled


class _EasyDiffCompareBothCommand(sublime_plugin.TextCommand):
    def set_right(self):
        pass

    def run(self, edit):
        self.set_right()

        lw = None
        rw = None
        lv = None
        rv = None

        for w in sublime.windows():
            if w.id() == LEFT["win_id"]:
                lw = w
            if w.id() == self.right["win_id"]:
                rw = w
            if lw is not None and rw is not None:
                break

        if lw is not None:
            for v in lw.views():
                if v.id() == LEFT["view_id"]:
                    lv = v
                    break
        else:
            if LEFT["clip"]:
                lv = LEFT["clip"]

        if rw is not None:
            for v in rw.views():
                if v.id() == self.right["view_id"]:
                    rv = v
                    break
        else:
            if self.right["clip"]:
                rv = self.right["clip"]

        if lv is not None and rv is not None:
            EasyDiff.compare(EasyDiffInput(lv, rv))
        else:
            log("Can't compare")

    def is_enabled(self):
        return LEFT is not None and self.is_visible()


class EasyDiffCompareBothViewCommand(_EasyDiffCompareBothCommand):
    def set_right(self):
        self.right = {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}

    def is_visible(self):
        return not (LEFT is not None and self.view.window().id() == LEFT["win_id"] and self.view.id() == LEFT["view_id"])


class EasyDiffCompareBothClipboardCommand(_EasyDiffCompareBothCommand):
    def set_right(self):
        self.right = {"win_id": None, "view_id": None, "clip": EasyDiffView("**clipboard**", sublime.get_clipboard())}

    def is_visible(self):
        return bool(sublime.load_settings(SETTINGS).get("use_clipboard", True))


class EasyDiffCompareBothSelectionCommand(_EasyDiffCompareBothCommand, _EasyDiffSelection):
    def set_right(self):
        self.right = {"win_id": None, "view_id": None, "clip": EasyDiffView("**selection**", self.get_selections())}

    def is_visible(self):
        return bool(sublime.load_settings(SETTINGS).get("use_selections", True)) and self.has_selections()


class EasyDiffSvnLastRevCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        name = self.view.file_name() if self.view is not None else None
        if name is not None:
            if svn.is_versioned(name):
                result = svn.diff_current(name).decode("utf-8").replace('\r', '')
                if result == "":
                    sublime.status_message("No Difference")
                    return

                use_buffer = bool(sublime.load_settings(SETTINGS).get("use_buffer", False))

                win = sublime.active_window()
                if use_buffer:
                    v = win.new_file()
                    v.set_name("EasyDiff: SVN (%s)" % basename(name))
                    v.set_scratch(True)
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                else:
                    v = win.create_output_panel('easy_diff')
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                    win.run_command("show_panel", {"panel": "output.easy_diff"})

    def is_visible(self):
        return SVN_ENABLED

    def is_enabled(self):
        name = self.view.file_name() if self.view != None else None
        if name is not None:
            try:
                versioned = svn.is_versioned(name)
                return SVN_ENABLED and versioned
            except Exception as e:
                pass
        return False


class EasyDiffGitLastRevCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        name = self.view.file_name() if self.view is not None else None
        if name is not None:
            if git.is_versioned(name):
                result = git.diff_current(name).decode("utf-8").replace('\r', '')
                if result == "":
                    sublime.status_message("No Difference")
                    return

                use_buffer = bool(sublime.load_settings(SETTINGS).get("use_buffer", False))

                win = sublime.active_window()
                if use_buffer:
                    v = win.new_file()
                    v.set_name("EasyDiff: Git (%s)" % basename(name))
                    v.set_scratch(True)
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                else:
                    v = win.create_output_panel('easy_diff')
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                    win.run_command("show_panel", {"panel": "output.easy_diff"})

    def is_visible(self):
        return GIT_ENABLED

    def is_enabled(self):
        name = self.view.file_name() if self.view != None else None
        if name is not None:
            try:
                versioned = git.is_versioned(name)
                return GIT_ENABLED and versioned
            except:
                pass
        return False


class EasyDiffListener(sublime_plugin.EventListener):
    def on_close(self, view):
        global LEFT
        vid = view.id()
        if LEFT is not None and vid == LEFT["view_id"]:
            LEFT = None
            update_menu()


def plugin_loaded():
    global SVN_ENABLED
    global GIT_ENABLED

    update_menu()
    settings = sublime.load_settings(SETTINGS)
    svn_path = multiget(settings, "svn", None)
    git_path = multiget(settings, "git", None)
    if svn_path is not None and svn_path != "":
        svn.set_svn_path(svn_path)
    if git_path is not None and git_path != "":
        git.set_git_path(git_path)

    try:
        log("svn %s" % svn.version())
        SVN_ENABLED = True
    except:
        pass
    try:
        log("git %s" % git.version())
        GIT_ENABLED = True
    except:
        pass
