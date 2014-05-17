"""
Easy Diff Version Control

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import sublime_plugin
from os.path import basename, splitext, join
import EasyDiff.lib.svn as svn
import EasyDiff.lib.git as git
import EasyDiff.lib.hg as hg
from EasyDiff.lib.multiconf import get as multiget
from EasyDiff.easy_diff_global import load_settings, log, debug, get_encoding, get_external_diff, get_target, notify
import subprocess
import tempfile

SVN_ENABLED = False
GIT_ENABLED = False
HG_ENABLED = False


###############################
# Version Control Base
###############################
class _VersionControlDiff(object):
    control_type = ""
    control_enabled = False
    temp_folder = None

    def get_diff(self, name, **kwargs):
        return None

    def is_versioned(self, name):
        return False

    def vc_is_enabled(self, name):
        enabled = False
        if name is not None:
            try:
                enabled = (
                    self.control_enabled and
                    (
                        multiget(load_settings(), "skip_version_check_on_is_enabled", False) or
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

    def create_temp(self):
        if self.temp_folder is None:
            self.temp_folder = tempfile.mkdtemp(prefix="easydiff")

    def get_files(name, **kwargs):
        return None, None

    def revert_file(self, name):
        pass

    def revert(self, name):
        result = self.get_diff(name)

        if result == "":
            notify("Nothing to Revert")
            result = None

        if result is not None and sublime.ok_cancel_dialog("Are you sure you want to revert \"%s\"?" % basename(name)):
            try:
                self.revert_file(name)
            except Exception as e:
                debug(e)
                sublime.error_message("Could not revert \"%s\"!" % basename(name))

    def internal_diff(self, name, **kwargs):
        result = self.get_diff(name, **kwargs)

        if result == "":
            notify("No Difference")
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

    def external_diff(self, name, **kwargs):
        self.create_temp()
        f1, f2 = self.get_files(name, **kwargs)
        ext_diff = get_external_diff()
        if f1 is not None and f2 is not None:
            subprocess.Popen(
                [
                    ext_diff,
                    f1,
                    f2
                ]
            )

    def is_loaded(self):
        if self.view.is_loading():
            sublime.set_timeout(self.is_loaded, 100)
        else:
            self.diff()

    def vc_run(self, **kwargs):
        self.kwargs = kwargs
        sublime.set_timeout(self.is_loaded, 100)

    def diff(self):
        name = self.view.file_name() if self.view is not None else None
        self.encoding = self.get_encoding()
        if name is not None:
            if self.kwargs.get("revert"):
                self.revert(name)
            else:
                external = self.kwargs.get("external", False)
                if not external:
                    self.internal_diff(name, **self.kwargs)
                else:
                    self.external_diff(name, **self.kwargs)


class _VersionControlCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], group=-1, index=-1, **kwargs):
        if len(paths):
            name = get_target(paths)
        elif index != -1:
            self.view = sublime.active_window().views_in_group(group)[index]
            name = self.view.file_name()
        else:
            self.view = self.window.active_view()
            if self.view is None:
                return False
            name = self.view.file_name() if self.view is not None else None

        if name is None:
            return False

        if len(paths):
            self.view = self.window.open_file(name)

        self.vc_run(**kwargs)

    def is_enabled(self, paths=[], group=-1, index=-1, **kwargs):
        if len(paths) or index != -1:
            name = get_target(paths, group, index)
        else:
            self.view = self.window.active_view()
            if self.view is None:
                return False
            name = self.view.file_name() if self.view is not None else None

        if name is None:
            return False

        return self.vc_is_enabled(name)


###############################
# Version Control Specific Classes
###############################
class _EasyDiffSvn(_VersionControlDiff):
    def setup(self):
        self.control_type = "SVN"
        self.control_enabled = SVN_ENABLED

    def revert_file(self, name):
        svn.revert(name)

    def get_files(self, name, **kwargs):
        f1 = None
        f2 = None
        if self.is_versioned(name):
            f2 = name
            root, ext = splitext(basename(name))
            rev = None
            if kwargs.get("last", False):
                rev = "PREV"
                f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, rev, ext))
            else:
                rev = "BASE"
                f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, rev, ext))
            svn.export(f2, f1, rev=rev)
        else:
            log("View not versioned under SVN!", status=True)
        return f1, f2

    def is_versioned(self, name):
        disabled = multiget(load_settings(), "svn_disabled", False)
        return not disabled and svn.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if self.is_versioned(name):
            result = self.decode(svn.diff(name, last=kwargs.get("last", False))).replace('\r', '')
        else:
            log("View not versioned under SVN!", status=True)
        return result


class _EasyDiffGit(_VersionControlDiff):
    def setup(self):
        self.control_type = "GIT"
        self.control_enabled = GIT_ENABLED

    def revert_file(self, name):
        git.checkout(name)

    def get_files(self, name, **kwargs):
        f1 = None
        f2 = None
        if self.is_versioned(name):
            f2 = name
            root, ext = splitext(basename(name))
            rev = None
            if kwargs.get("last", False):
                revs = git.getrevision(f2, 2)
                if revs is not None and len(revs) == 2:
                    rev = revs[1]
                if rev is not None:
                    f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, rev, ext))
            else:
                rev = "HEAD"
                f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, rev, ext))
            if f1 is not None:
                with open(f1, "wb") as f:
                    bfr = git.show(f2, rev)
                    if bfr is not None:
                        f.write(bfr)
                    else:
                        f1 = None
        else:
            log("View not versioned under Git!", status=True)
        return f1, f2

    def is_versioned(self, name):
        disabled = multiget(load_settings(), "git_disabled", False)
        return not disabled and git.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if git.is_versioned(name):
            result = self.decode(
                git.diff(
                    name,
                    last=kwargs.get("last", False)
                )
            ).replace('\r', '')
        else:
            log("View not versioned under Git!", status=True)
        return result


class _EasyDiffHg(_VersionControlDiff):
    def setup(self):
        self.control_type = "HG"
        self.control_enabled = HG_ENABLED

    def revert_file(self, name):
        hg.revert(name)

    def get_files(self, name, **kwargs):
        f1 = None
        f2 = None
        if self.is_versioned(name):
            f2 = name
            root, ext = splitext(basename(name))
            rev = None
            if kwargs.get("last", False):
                revs = hg.getrevision(f2, 2)
                if revs is not None and len(revs) == 2:
                    rev = revs[1]
                if rev is not None:
                    f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, rev, ext))
            else:
                # Leave rev as None
                f1 = join(self.temp_folder, "%s-r%s-LEFT%s" % (root, "BASE", ext))
            if f1 is not None:
                with open(f1, "wb") as f:
                    bfr = hg.cat(f2, rev)
                    if bfr is not None:
                        f.write(bfr)
                    else:
                        f1 = None
        else:
            log("View not versioned under Mercurial!", status=True)
        return f1, f2

    def is_versioned(self, name):
        disabled = multiget(load_settings(), "hg_disabled", False)
        return not disabled and hg.is_versioned(name)

    def get_diff(self, name, **kwargs):
        result = None
        if self.is_versioned(name):
            result = self.decode(hg.diff(name, last=kwargs.get("last", False))).replace('\r', '')
        else:
            log("View not versioned under Mercurial!", status=True)
        return result


###############################
# Version Control Commands
###############################
class EasyDiffSvnCommand(_VersionControlCommand, _EasyDiffSvn):
    def __init__(self, window):
        super().__init__(window)
        self.setup()


class EasyDiffGitCommand(_VersionControlCommand, _EasyDiffGit):
    def __init__(self, window):
        super().__init__(window)
        self.setup()


class EasyDiffHgCommand(_VersionControlCommand, _EasyDiffHg):
    def __init__(self, window):
        super().__init__(window)
        self.setup()


###############################
# Loaders
###############################
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
