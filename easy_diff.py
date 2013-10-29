"""
Easy Diff

Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>
License: MIT
"""
import sublime
import time
import difflib
from os.path import basename
from os import stat as osstat
import tempfile
from EasyDiff.easy_diff_global import load_settings, get_encoding
import subprocess


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


class EasyDiffExtInput(object):
    def __init__(self, v1, v2):
        untitled = False
        self.f1 = v1.file_name()
        if self.f1 is None:
            untitled = True
            self.f1 = self.create_temp(v1, "Untitled")
            self.t1 = time.ctime()
        elif isinstance(v1, EasyDiffView):
            self.t1 = v1.get_time()
            self.f1 = self.create_temp(v1, v1.file_name().replace("*", ""))
        else:
            self.t1 = time.ctime(osstat(self.f1).st_mtime)

        self.f2 = v2.file_name()
        if self.f2 is None:
            self.f2 = self.create_temp(v1, "Untitled2" if untitled else "Untitled")
            self.t2 = time.ctime()
        elif isinstance(v2, EasyDiffView):
            self.t2 = v2.get_time()
            self.f2 = self.create_temp(v2, v2.file_name().replace("*", ""))
        else:
            self.t2 = time.ctime(osstat(self.f2).st_mtime)

    def create_temp(self, v, name):
        with tempfile.NamedTemporaryFile(delete=False, prefix=name, suffix="") as f:
            encoding = get_encoding(v)
            try:
                bfr = v.substr(sublime.Region(0, v.size())).encode(encoding)
            except:
                bfr = v.substr(sublime.Region(0, v.size())).encode("utf-8")
            f.write(bfr)
        return f.name


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
            sublime.status_message("No Difference")
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
