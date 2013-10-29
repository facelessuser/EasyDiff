"""
Easy Diff Version Control

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import sublime_plugin
from os.path import basename
import EasyDiff.lib.svn as svn
import EasyDiff.lib.git as git
import EasyDiff.lib.hg as hg
from EasyDiff.lib.multiconf import get as multiget
from EasyDiff.easy_diff_global import load_settings, log, debug, get_encoding
import re
import traceback

SVN_ENABLED = False
GIT_ENABLED = False
HG_ENABLED = False


class _VersionControlDiff(sublime_plugin.TextCommand):
    control_type = ""
    control_enabled = False

    def get_diff(self, name, **kwargs):
        return None

    def is_versioned(self, name):
        return False

    def is_enabled(self):
        enabled = False
        name = self.view.file_name() if self.view is not None else None
        if name is not None:
            try:
                enabled = (
                    self.control_enabled and
                    (
                        load_settings().get("skip_version_check_on_is_enabled", False) or
                        self.is_versioned(name)
                    )
                )
            except:
                pass
        return enabled

    def decode(self, result):
        try:
            debug("decoding with %s" % self.encoding)
            return result.decode(self.encoding)
        except:
            debug("fallback to utf-8 decode")
            return result.decode('utf-8')

    def get_encoding(self):
        return get_encoding(self.view)

    def run(self, edit, **kwargs):
        name = self.view.file_name() if self.view is not None else None
        self.encoding = self.get_encoding()
        if name is not None:
            result = self.get_diff(name, **kwargs)

            if result == "":
                sublime.status_message("No Difference")
                result = None

            if result is not None:
                use_buffer = bool(load_settings().get("use_buffer", False))

                win = sublime.active_window()
                if use_buffer:
                    v = win.new_file()
                    v.set_name("EasyDiff: %s (%s)" % (self.control_type, basename(name)))
                    v.set_scratch(True)
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                else:
                    v = win.create_output_panel('easy_diff')
                    v.assign_syntax('Packages/Diff/Diff.tmLanguage')
                    v.run_command('append', {'characters': result})
                    win.run_command("show_panel", {"panel": "output.easy_diff"})


class EasyDiffSvnCommand(_VersionControlDiff):
    def __init__(self, edit):
        super().__init__(edit)
        self.control_type = "SVN"
        self.control_enabled = SVN_ENABLED

    def is_versioned(self, name):
        disabled = load_settings().get("svn_disabled", False)
        return not disabled and svn.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if self.is_versioned(name):
            result = self.decode(svn.diff(name, last=kwargs.get("last", False))).replace('\r', '')
        else:
            log("View not versioned under SVN!", status=True)
        return result


class EasyDiffGitCommand(_VersionControlDiff):
    def __init__(self, edit):
        super().__init__(edit)
        self.control_type = "GIT"
        self.control_enabled = GIT_ENABLED

    def is_versioned(self, name):
        disabled = load_settings().get("git_disabled", False)
        return not disabled and git.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if git.is_versioned(name):
            result = self.decode(
                git.diff(
                    name,
                    last=kwargs.get("last", False),
                    staged=kwargs.get("staged", False)
                )
            ).replace('\r', '')
        else:
            log("View not versioned under Git!", Status=True)
        return result


class EasyDiffHgCommand(_VersionControlDiff):
    def __init__(self, edit):
        super().__init__(edit)
        self.control_type = "HG"
        self.control_enabled = HG_ENABLED

    def is_versioned(self, name):
        disabled = load_settings().get("hg_disabled", False)
        return not disabled and hg.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if self.is_versioned(name):
            result = self.decode(hg.diff(name, last=kwargs.get("last", False))).replace('\r', '')
        else:
            log("View not versioned under Mercurial!", status=True)
        return result


def setup_vc_binaries():
    global SVN_ENABLED
    global GIT_ENABLED
    global HG_ENABLED

    settings = load_settings()
    svn_path = multiget(settings, "svn", None)
    git_path = multiget(settings, "git", None)
    hg_path = multiget(settings, "hg", None)
    if svn_path is not None and svn_path != "":
        svn.set_svn_path(svn_path)
    if git_path is not None and git_path != "":
        git.set_git_path(git_path)
    if hg_path is not None and hg_path != "":
        hg.set_hg_path(hg_path)

    try:
        log("svn %s" % svn.version())
        SVN_ENABLED = True
    except:
        log("svn not found or is not working!")
        pass
    try:
        log("git %s" % git.version())
        GIT_ENABLED = True
    except:
        log("git not found or is not working!")
        pass
    try:
        log("hg %s" % hg.version())
        HG_ENABLED = True
    except:
        log("hg not found or is not working!")
        pass

    settings.clear_on_change('reload_vc')
    settings.add_on_change('reload_vc', setup_vc_binaries)


def plugin_loaded():
    setup_vc_binaries()
