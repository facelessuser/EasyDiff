"""
Easy Diff

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import time
import difflib
from os.path import basename, join, splitext, exists
from os import stat as osstat
import tempfile
from EasyDiff.easy_diff_global import load_settings, get_encoding, notify
import subprocess

LEFT = 1
RIGHT = 2


class EasyDiffView(object):
    def __init__(self, name, content, encoding):
        self.filename = name
        self.content = content
        self.time = time.ctime()
        self.encode = encoding

    def encoding(self):
        return self.encode

    def get_time(self):
        return self.time

    def file_name(self):
        return self.filename

    def substr(self, region):
        return self.content[region.begin():region.end() + 1]

    def size(self):
        return len(self.content)


class EasyDiffInput(object):
    def __init__(self, v1, v2, external=False):
        self.untitled = False
        self.temp_folder = None
        self.process_view(v1, LEFT, external)
        self.process_view(v2, RIGHT, external)

    def process_view(self, view, side, external):
        self.side = side
        name = view.file_name()
        if name is None or not exists(name):
            self.set_view_buffer(view, self.untitled, external)
        elif isinstance(view, EasyDiffView):
            self.set_special(view, external)
        else:
            self.set_view(view)

        self.set_buffer(view, external)

    def set_buffer(self, view, external):
        setattr(
            self,
            "b%d" % self.side,
            view.substr(sublime.Region(0, view.size())).splitlines() if not external else []
        )

    def set_view(self, view):
        setattr(self, "f%d" % self.side, view.file_name())
        setattr(self, "t%d" % self.side, time.ctime(osstat(view.file_name()).st_mtime))

    def set_special(self, view, external):
        setattr(self, "f%d" % self.side, view.file_name())
        if external:
            setattr(self, "f%d" % self.side, self.create_temp(view, view.file_name().replace("*", "")))
        setattr(self, "t%d" % self.side, view.get_time())

    def set_view_buffer(self, view, untitled, external):
        setattr(
            self,
            "f%d" % self.side,
            self.create_temp(view, "Untitled2" if self.untitled else "Untitled") if external else "Untitled2" if self.untitled else "Untitled"
        )
        setattr(self, "t%d" % self.side, time.ctime())
        self.untitled = True

    def create_temp(self, v, name):
        file_name = None
        if self.temp_folder is None:
            self.temp_folder = tempfile.mkdtemp(prefix="easydiff")
            file_name = self.create_file(v, name)
        else:
            file_name = self.create_file(v, name)
        return file_name

    def create_file(self, v, name):
        root, ext = splitext(name)
        with open(join(self.temp_folder, "%s-%s%s" % (root, "LEFT" if self.side == LEFT else "RIGHT", ext)), "wb") as f:
            encoding = get_encoding(v)
            try:
                bfr = v.substr(sublime.Region(0, v.size())).encode(encoding)
            except:
                bfr = v.substr(sublime.Region(0, v.size())).encode("utf-8")
            f.write(bfr)
        return f.name


class EasyDiff(object):
    @classmethod
    def extcompare(cls, inputs, ext_diff):
        subprocess.Popen(
            [
                ext_diff,
                inputs.f1,
                inputs.f2
            ]
        )

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
            notify("No Difference")
            return

        use_buffer = bool(load_settings().get("use_buffer", False))

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
