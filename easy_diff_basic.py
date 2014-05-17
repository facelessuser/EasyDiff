"""
Easy Diff Basic Commands

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import sublime_plugin
from os.path import basename
from EasyDiff.easy_diff_global import load_settings, log, get_external_diff, get_target
from EasyDiff.easy_diff_dynamic_menu import update_menu
from EasyDiff.easy_diff import EasyDiffView, EasyDiffInput, EasyDiff

LEFT = None


###############################
# Helper Functions
###############################
def diff(right, external=False):
    lw = None
    rw = None
    lv = None
    rv = None

    for w in sublime.windows():
        if w.id() == LEFT["win_id"]:
            lw = w
        if w.id() == right["win_id"]:
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


###############################
# Helper Classes
###############################
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

    def get_encoding(self):
        return self.view.encoding()

    def has_selections(self):
        selections = False
        if bool(load_settings().get("multi_select", False)):
            for s in self.view.sel():
                if s.size() > 0:
                    selections = True
                    break
        else:
            selections = len(self.view.sel()) == 1 and self.view.sel()[0].size() > 0
        return selections


class _EasyDiffCompareBothTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, external=False, group=-1, index=-1):
        if index != -1:
            # Ensure we have the correct view
            self.view = sublime.active_window().views_in_group(group)[index]
        diff(self.get_right(), external=external)

    def view_has_selections(self, group=-1, index=-1):
        has_selections = False
        if index != -1:
            view = sublime.active_window().views_in_group(group)[index]
            if bool(load_settings().get("multi_select", False)):
                for sel in view.sel():
                    if sel.size() > 0:
                        has_selections = True
                        break
            else:
                has_selections = len(view.sel()) == 1 and view.sel()[0].size() > 0
        else:
            has_selections = self.has_selections()
        return has_selections

    def get_right(self):
        return None

    def check_enabled(self, group=-1, index=-1):
        return True

    def is_enabled(self, external=False, group=-1, index=-1):
        return LEFT is not None and self.check_enabled(group, index)


class _EasyDiffCompareBothWindowCommand(sublime_plugin.WindowCommand):
    no_view = False

    def run(self, external=False, paths=[], group=-1, index=-1):
        self.external = external
        self.set_view(paths, group, index)
        if not self.no_view and self.view is None:
            return
        if not self.no_view:
            sublime.set_timeout(self.is_loaded, 100)
        else:
            self.diff()

    def is_loaded(self):
        if self.view.is_loading():
            sublime.set_timeout(self.is_loaded, 100)
        else:
            self.diff()

    def diff(self):
        diff(self.get_right(), external=self.external)

    def set_view(self, paths, group=-1, index=-1, open_file=True):
        if len(paths):
            file_path = get_target(paths)
            if file_path is None:
                return
            if open_file:
                self.view = self.window.open_file(file_path)
        elif index != -1:
            self.view = self.window.views_in_group(group)[index]
        else:
            self.view = self.window.active_view()

    def get_right(self):
        return None

    def check_enabled(self, paths=[], group=-1, index=-1):
        return True

    def is_enabled(self, external=False, paths=[], group=-1, index=-1):
        return LEFT is not None and self.check_enabled(paths)


###############################
# Set View
###############################
class EasyDiffSetLeftCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], group=-1, index=-1):
        global LEFT
        self.set_view(paths, group, index)
        if self.view is None:
            return
        LEFT = {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}
        name = self.view.file_name()
        if name is None:
            name = "Untitled"
        update_menu(basename(name))

    def set_view(self, paths, group=-1, index=-1, open_file=True):
        if len(paths):
            file_path = get_target(paths)
            if file_path is None:
                return
            if open_file:
                self.view = self.window.open_file(file_path)
        elif index != -1:
            self.view = self.window.views_in_group(group)[index]
        else:
            self.view = self.window.active_view()

    def is_enabled(self, paths=[], group=-1, index=-1):
        return get_target(paths, group, index) is not None if len(paths) or index != -1 else True


class EasyDiffCompareBothViewCommand(_EasyDiffCompareBothWindowCommand):
    def get_right(self):
        return {"win_id": self.view.window().id(), "view_id": self.view.id(), "clip": None}

    def check_enabled(self, paths=[], group=-1, index=-1):
        return True

    def is_enabled(self, external=False, paths=[], group=-1, index=-1):
        return LEFT is not None and (get_target(paths, group, index) is not None if len(paths) or index != -1 else True) and self.check_enabled()


###############################
# Set Clipboard
###############################
class EasyDiffSetLeftClipboardCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], group=-1, index=-1):
        global LEFT
        LEFT = {"win_id": None, "view_id": None, "clip": EasyDiffView("**clipboard**", sublime.get_clipboard(), "UTF-8")}
        update_menu("**clipboard**")

    def is_enabled(self, paths=[], group=-1, index=-1):
        valid_path = get_target(paths, group, index) is not None if len(paths) or index != -1 else True
        return bool(load_settings().get("use_clipboard", True)) and valid_path

    def is_visible(self, paths=[], group=-1, index=-1):
        return bool(load_settings().get("use_clipboard", True))


class EasyDiffCompareBothClipboardCommand(_EasyDiffCompareBothWindowCommand):
    no_view = True

    def get_right(self):
        return {"win_id": None, "view_id": None, "clip": EasyDiffView("**clipboard**", sublime.get_clipboard(), "UTF-8")}

    def check_enabled(self, paths=[], group=-1, index=-1):
        valid_path = get_target(paths, group, index) is not None if len(paths) or index != -1 else True
        return bool(load_settings().get("use_clipboard", True)) and valid_path

    def is_visible(self, external=False, paths=[], group=-1, index=-1):
        return bool(load_settings().get("use_clipboard", True))


###############################
# Set Selection
###############################
class EasyDiffSetLeftSelectionCommand(sublime_plugin.TextCommand, _EasyDiffSelection):
    def run(self, edit, group=-1, index=-1):
        global LEFT
        if index != -1:
            # Ensure we have the correct view
            self.view = sublime.active_window().views_in_group(group)[index]
        LEFT = {"win_id": None, "view_id": None, "clip": EasyDiffView("**selection**", self.get_selections(), self.get_encoding())}
        update_menu("**selection**")

    def view_has_selections(self, group=-1, index=-1):
        has_selections = False
        if index != -1:
            view = sublime.active_window().views_in_group(group)[index]
            if bool(load_settings().get("multi_select", False)):
                for sel in view.sel():
                    if sel.size() > 0:
                        has_selections = True
                        break
            else:
                has_selections = len(view.sel()) == 1 and view.sel()[0].size() > 0
        else:
            has_selections = self.has_selections()
        return has_selections

    def is_enabled(self, group=-1, index=-1):
        return bool(load_settings().get("use_selections", True)) and self.view_has_selections(group, index)

    def is_visible(self, group=-1, index=-1):
        return bool(load_settings().get("use_selections", True))


class EasyDiffCompareBothSelectionCommand(_EasyDiffCompareBothTextCommand, _EasyDiffSelection):
    def get_right(self):
        return {"win_id": None, "view_id": None, "clip": EasyDiffView("**selection**", self.get_selections(), self.get_encoding())}

    def check_enabled(self, group=-1, index=-1):
        return bool(load_settings().get("use_selections", True)) and self.view_has_selections(group, index)

    def is_visible(self, external=False, group=-1, index=-1):
        return bool(load_settings().get("use_selections", True))


###############################
# View Close Listener
###############################
class EasyDiffListener(sublime_plugin.EventListener):
    def on_close(self, view):
        global LEFT
        vid = view.id()
        if LEFT is not None and vid == LEFT["view_id"]:
            LEFT = None
            update_menu()


###############################
# Loaders
###############################
def basic_reload():
    global LEFT
    LEFT = None
    update_menu()
    settings = load_settings()
    settings.clear_on_change('reload_basic')
    settings.add_on_change('reload_basic', basic_reload)


def plugin_loaded():
    basic_reload()
